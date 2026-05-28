"""
Pillar Anomaly Detector — EES 2026
Phát hiện bất thường trong từng trụ cột (TC1-TC5) cho mỗi nhóm khảo sát.

Logic: DETECT → DEEP DIVE → AI INSIGHT
- Detect: Chạy rules per pillar per group
- Deep Dive: Khi phát hiện anomaly → drill down chi tiết
- AI Insight: Giải thích "tại sao vô lý" + đề xuất hành động
"""
import pandas as pd
import numpy as np
from shared.codebook import get_pillar_questions, get_question_label, PILLAR_META


# ═══════════════════════════════════════════════════════════════
# ANOMALY PATTERNS DEFINITION
# ═══════════════════════════════════════════════════════════════

PILLAR_PATTERNS = {
    # TC1 - Niềm tin & Định hướng
    'TC1_info_gap': {
        'label': 'Đứt gãy thông tin',
        'icon': '📢',
        'color': '#F59E0B',
        'desc': 'Nhân viên TIN lãnh đạo nhưng KHÔNG được thông báo kịp thời về thay đổi',
    },
    'TC1_trust_paradox': {
        'label': 'Nghịch lý niềm tin',
        'icon': '🤔',
        'color': '#8B5CF6',
        'desc': 'Tin BLĐ nhưng vẫn muốn nghỉ → vấn đề nằm ở trụ cột khác',
    },
    
    # TC2 - Quản lý Trực tiếp
    'TC2_fairness_gap': {
        'label': 'Hỗ trợ tốt nhưng phân bổ không công bằng',
        'icon': '⚖️',
        'color': '#EF4444',
        'desc': 'QL hỗ trợ tốt nhưng phân đơn/lịch chạy thiên vị → tử huyệt cảm xúc',
    },
    'TC2_manager_island': {
        'label': 'Quản lý tốt — Tổ chức yếu',
        'icon': '🏝️',
        'color': '#B45309',
        'desc': 'Nhân viên thích QL trực tiếp nhưng ghét công ty → rủi ro khi QL rời đi',
    },
    
    # TC3 - Công việc & Điều kiện
    'TC3_glass_ceiling': {
        'label': 'Trần thủy tinh',
        'icon': '🔝',
        'color': '#7C3AED',
        'desc': 'Nhân viên thâm niên KHÔNG thấy lộ trình thăng tiến → Quiet Quitting',
    },
    'TC3_tool_barrier': {
        'label': 'Công cụ cản trở',
        'icon': '🔧',
        'color': '#DC2626',
        'desc': 'App/thiết bị kém → năng suất thấp → thu nhập thấp → vòng lặp tiêu cực',
    },
    
    # TC4 - Thu nhập & Minh bạch
    'TC4_transparency_issue': {
        'label': 'Thu nhập tốt nhưng CẢM THẤY bất công',
        'icon': '💰',
        'color': '#EA580C',
        'desc': 'Lương thực tế OK nhưng nhân viên không hiểu cách tính → vấn đề MINH BẠCH',
    },
    'TC4_income_paradox': {
        'label': 'Lương cao nhưng vẫn muốn nghỉ',
        'icon': '💸',
        'color': '#0891B2',
        'desc': 'TC4 cao nhưng % Muốn nghỉ vẫn cao → vấn đề ở TC2 hoặc TC5',
    },
    
    # TC5 - Môi trường & Gắn kết
    'TC5_pride_paradox': {
        'label': 'Tự hào nhưng vẫn muốn nghỉ',
        'icon': '💔',
        'color': '#BE185D',
        'desc': 'Yêu công ty nhưng không chịu nổi điều kiện → nghỉ trong tiếc nuối',
    },
    'TC5_burnout_blind': {
        'label': 'Kiệt sức không nhận ra',
        'icon': '😵',
        'color': '#9333EA',
        'desc': 'Burnout cao nhưng nhân viên nói "không áp lực" → dangerous blind spot',
    },
    'TC5_social_glue': {
        'label': 'Gắn bó vì đồng nghiệp, không vì tổ chức',
        'icon': '👥',
        'color': '#0D9488',
        'desc': 'Ở lại vì bạn bè → khi bạn thân nghỉ sẽ có domino effect',
    },
    
    # Cross-pillar
    'XP_silent_disengaged': {
        'label': 'Buông xuôi thầm lặng (Quiet Quitting)',
        'icon': '👻',
        'color': '#64748B',
        'desc': 'EI thấp nhưng không muốn nghỉ → đã buông xuôi, không còn nỗ lực',
    },
    'XP_onboarding_shock': {
        'label': 'Sốc Onboarding',
        'icon': '🆘',
        'color': '#DC2626',
        'desc': 'Nhân viên mới (<3 tháng) có điểm thấp ở nhiều trụ cột → cần can thiệp gấp',
    },
}


# ═══════════════════════════════════════════════════════════════
# DETECT FUNCTIONS
# ═══════════════════════════════════════════════════════════════

def detect_pillar_anomalies(df, group_id, pillar_id, min_n=15):
    """
    Phát hiện bất thường cho 1 trụ cột của 1 nhóm.
    Returns: list of detected anomalies với data để deep dive.
    """
    if len(df) < min_n:
        return []
    
    anomalies = []
    qs = get_pillar_questions(group_id, pillar_id)
    q_cols = [q for q in qs if q in df.columns]
    
    if not q_cols:
        return []
    
    # Calculate pillar score
    pillar_mean = df[q_cols].mean().mean()
    pillar_pct = ((df[q_cols] >= 4).sum().sum() / (df[q_cols].notna().sum().sum())) * 100
    
    # Get other metrics
    ei = df['EI'].mean() if 'EI' in df.columns else None
    intent_low_pct = (df['intent'] <= 2).mean() * 100 if 'intent' in df.columns else None
    burnout_pct = (df['burnout_risk'] > 0).mean() * 100 if 'burnout_risk' in df.columns else None
    
    # ═══ TC1: Niềm tin & Định hướng ═══
    if pillar_id == 'TC1' and len(q_cols) >= 2:
        # Info gap: Q10 (thông báo) thấp hơn Q9 (tin BLĐ)
        if 'Q9' in df.columns and 'Q10' in df.columns:
            q9_mean = df['Q9'].mean()
            q10_mean = df['Q10'].mean()
            gap = q9_mean - q10_mean
            if gap > 0.5:
                anomalies.append({
                    'id': 'TC1_info_gap',
                    'data': {'Q9': q9_mean, 'Q10': q10_mean, 'gap': gap},
                    'severity': 'high' if gap > 0.8 else 'medium',
                })
        
        # Trust paradox: TC1 cao nhưng muốn nghỉ cao
        if pillar_pct > 70 and intent_low_pct and intent_low_pct > 20:
            anomalies.append({
                'id': 'TC1_trust_paradox',
                'data': {'TC1_pct': pillar_pct, 'intent_low_pct': intent_low_pct},
                'severity': 'high',
            })
    
    # ═══ TC2: Quản lý Trực tiếp ═══
    elif pillar_id == 'TC2':
        # Fairness gap: Q hỗ trợ cao nhưng Q công bằng thấp
        fairness_q = 'Q12' if group_id in ('1A', '1B') else 'Q14'
        support_q = 'Q11' if group_id in ('1A', '1B') else 'Q13'
        
        if fairness_q in df.columns and support_q in df.columns:
            support_mean = df[support_q].mean()
            fairness_mean = df[fairness_q].mean()
            gap = support_mean - fairness_mean
            if gap > 0.5:
                anomalies.append({
                    'id': 'TC2_fairness_gap',
                    'data': {
                        'support_q': support_q, 'support_mean': support_mean,
                        'fairness_q': fairness_q, 'fairness_mean': fairness_mean,
                        'gap': gap
                    },
                    'severity': 'high' if gap > 0.8 else 'medium',
                })
        
        # Manager island: TC2 cao nhưng EI thấp
        mei = df['MEI'].mean() if 'MEI' in df.columns else None
        if mei and mei > 75 and ei and ei < 60:
            anomalies.append({
                'id': 'TC2_manager_island',
                'data': {'MEI': mei, 'EI': ei},
                'severity': 'high',
            })
    
    # ═══ TC3: Công việc & Điều kiện ═══
    elif pillar_id == 'TC3':
        # Glass ceiling: Q19 (thăng tiến) thấp ở nhóm thâm niên cao
        if 'Q19' in df.columns and 'Q5' in df.columns:
            senior_mask = df['Q5'].isin(['Trên 2 đến 3 năm', 'Trên 3 đến 5 năm', 'Trên 5 năm',
                                          'Trên 2 năm', 'Trên 3 năm'])
            junior_mask = ~senior_mask & df['Q5'].notna()
            
            senior_career = df.loc[senior_mask, 'Q19'].mean() if senior_mask.any() else None
            junior_career = df.loc[junior_mask, 'Q19'].mean() if junior_mask.any() else None
            
            if senior_career and junior_career and senior_career < 3.2 and junior_career - senior_career > 0.3:
                anomalies.append({
                    'id': 'TC3_glass_ceiling',
                    'data': {
                        'senior_score': senior_career,
                        'junior_score': junior_career,
                        'gap': junior_career - senior_career,
                        'n_senior': senior_mask.sum()
                    },
                    'severity': 'high' if senior_career < 2.8 else 'medium',
                })
        
        # Tool barrier: Q16 (App/thiết bị) < 3.5
        tool_q = 'Q16' if group_id in ('1A', '1B') else 'Q18'
        if tool_q in df.columns:
            tool_mean = df[tool_q].mean()
            if tool_mean < 3.5:
                anomalies.append({
                    'id': 'TC3_tool_barrier',
                    'data': {'question': tool_q, 'score': tool_mean},
                    'severity': 'high' if tool_mean < 3.0 else 'medium',
                })
    
    # ═══ TC4: Thu nhập & Minh bạch ═══
    elif pillar_id == 'TC4':
        # Transparency issue: Q21 (công bằng) thấp
        if 'Q21' in df.columns:
            q21_mean = df['Q21'].mean()
            if q21_mean < 3.5:
                anomalies.append({
                    'id': 'TC4_transparency_issue',
                    'data': {'Q21_mean': q21_mean},
                    'severity': 'high' if q21_mean < 3.0 else 'medium',
                })
        
        # Income paradox: TC4 cao nhưng muốn nghỉ cao
        if pillar_pct > 65 and intent_low_pct and intent_low_pct > 20:
            anomalies.append({
                'id': 'TC4_income_paradox',
                'data': {'TC4_pct': pillar_pct, 'intent_low_pct': intent_low_pct},
                'severity': 'high',
            })
    
    # ═══ TC5: Môi trường & Gắn kết ═══
    elif pillar_id == 'TC5':
        # Pride paradox: Q28 (tự hào) cao nhưng muốn nghỉ cao
        if 'Q28' in df.columns and 'intent' in df.columns:
            q28_mean = df['Q28'].mean()
            if q28_mean > 3.8 and intent_low_pct and intent_low_pct > 15:
                anomalies.append({
                    'id': 'TC5_pride_paradox',
                    'data': {'Q28_mean': q28_mean, 'intent_low_pct': intent_low_pct},
                    'severity': 'high' if intent_low_pct > 25 else 'medium',
                })
        
        # Burnout blind spot: Q29 (áp lực OK) nhưng burnout cao
        if 'Q29' in df.columns and burnout_pct:
            q29_mean = df['Q29'].mean()
            if q29_mean > 3.8 and burnout_pct > 25:
                anomalies.append({
                    'id': 'TC5_burnout_blind',
                    'data': {'Q29_mean': q29_mean, 'burnout_pct': burnout_pct},
                    'severity': 'high' if burnout_pct > 35 else 'medium',
                })
        
        # Social glue: Q27 (đồng nghiệp) cao nhưng EI thấp
        if 'Q27' in df.columns and ei:
            q27_mean = df['Q27'].mean()
            if q27_mean > 4.0 and ei < 55:
                anomalies.append({
                    'id': 'TC5_social_glue',
                    'data': {'Q27_mean': q27_mean, 'EI': ei},
                    'severity': 'medium',
                })
    
    # ═══ Cross-pillar patterns ═══
    # Silent disengaged: EI thấp nhưng không muốn nghỉ
    if ei and ei < 55 and intent_low_pct and intent_low_pct < 8:
        anomalies.append({
            'id': 'XP_silent_disengaged',
            'data': {'EI': ei, 'intent_low_pct': intent_low_pct},
            'severity': 'high',
            'cross_pillar': True,
        })
    
    # Onboarding shock: nhân viên mới có điểm thấp
    if 'Q5' in df.columns:
        new_mask = df['Q5'].isin(['Dưới 1 tháng', 'Trên 1 đến 3 tháng', '< 1 tháng', '1-3 tháng'])
        if new_mask.any():
            new_df = df[new_mask]
            new_ei = new_df['EI'].mean() if 'EI' in new_df.columns else None
            if new_ei and new_ei < 50:
                anomalies.append({
                    'id': 'XP_onboarding_shock',
                    'data': {'new_ei': new_ei, 'n_new': new_mask.sum()},
                    'severity': 'high',
                    'cross_pillar': True,
                })
    
    return anomalies


# ═══════════════════════════════════════════════════════════════
# DEEP DIVE FUNCTIONS
# ═══════════════════════════════════════════════════════════════

def deep_dive_anomaly(df, group_id, pillar_id, anomaly):
    """
    Deep dive vào 1 anomaly cụ thể.
    Returns: dict với data chi tiết để hiển thị + AI prompt.
    """
    anomaly_id = anomaly['id']
    data = anomaly['data']
    
    result = {
        'anomaly_id': anomaly_id,
        'pattern': PILLAR_PATTERNS.get(anomaly_id, {}),
        'data': data,
        'breakdown': {},
        'ai_prompt': '',
    }
    
    # ═══ TC1 Deep Dive ═══
    if anomaly_id == 'TC1_info_gap':
        # Breakdown theo thâm niên
        if 'Q5' in df.columns:
            tenure_gap = df.groupby('Q5').agg({
                'Q9': 'mean', 'Q10': 'mean'
            }).round(2)
            tenure_gap['gap'] = tenure_gap['Q9'] - tenure_gap['Q10']
            result['breakdown']['by_tenure'] = tenure_gap
        
        result['ai_prompt'] = f"""
Dữ liệu TC1 của nhóm {group_id}:
- Q9 (Tin BLĐ): {data['Q9']:.2f} điểm
- Q10 (Thông báo kịp thời): {data['Q10']:.2f} điểm
- Khoảng cách: {data['gap']:.2f} điểm

BẤT THƯỜNG: Nhân viên TIN lãnh đạo nhưng KHÔNG được thông báo kịp thời.

Phân tích:
1. Kênh truyền thông nội bộ đang có vấn đề gì? (Họp, email, app, TBC?)
2. Nhóm thâm niên nào bị ảnh hưởng nhiều nhất?
3. Đề xuất 1 hành động cụ thể trong 30 ngày.
"""
    
    # ═══ TC2 Deep Dive ═══
    elif anomaly_id == 'TC2_fairness_gap':
        # So sánh câu hỗ trợ vs câu công bằng
        result['breakdown']['comparison'] = {
            'Hỗ trợ': data['support_mean'],
            'Công bằng': data['fairness_mean'],
            'Chênh lệch': data['gap'],
        }
        
        # Breakdown theo vùng nếu có
        if 'region' in df.columns:
            region_scores = df.groupby('region')[[data['support_q'], data['fairness_q']]].mean().round(2)
            region_scores['gap'] = region_scores[data['support_q']] - region_scores[data['fairness_q']]
            result['breakdown']['by_region'] = region_scores
        
        result['ai_prompt'] = f"""
Dữ liệu TC2 của nhóm {group_id}:
- {data['support_q']} (Hỗ trợ): {data['support_mean']:.2f} điểm
- {data['fairness_q']} (Công bằng): {data['fairness_mean']:.2f} điểm
- Khoảng cách: {data['gap']:.2f} điểm

BẤT THƯỜNG: Quản lý HỖ TRỢ tốt nhưng phân bổ KHÔNG CÔNG BẰNG.

Đây là "tử huyệt cảm xúc" — nhân viên chấp nhận QL khó tính nhưng KHÔNG chấp nhận thiên vị.

Phân tích:
1. Vấn đề công bằng nằm ở đâu? (Phân đơn? Lịch chạy? Tuyến đường?)
2. Có pattern nào theo vùng/bưu cục không?
3. Đề xuất cơ chế minh bạch hóa quy trình phân bổ.
"""
    
    # ═══ TC3 Deep Dive ═══
    elif anomaly_id == 'TC3_glass_ceiling':
        result['breakdown']['career_path'] = {
            'Nhân viên mới (<2 năm)': data['junior_score'],
            'Nhân viên cũ (>2 năm)': data['senior_score'],
            'Khoảng cách': data['gap'],
            'Số NV thâm niên': data['n_senior'],
        }
        
        result['ai_prompt'] = f"""
Dữ liệu TC3 - Câu Q19 (Lộ trình thăng tiến) của nhóm {group_id}:
- Nhân viên mới (<2 năm): {data['junior_score']:.2f} điểm
- Nhân viên thâm niên (>2 năm): {data['senior_score']:.2f} điểm
- Khoảng cách: {data['gap']:.2f} điểm
- Số NV thâm niên bị ảnh hưởng: {data['n_senior']} người

BẤT THƯỜNG: "TRẦN THỦY TINH" — Nhân viên lâu năm KHÔNG thấy tương lai.

Sau 12-18 tháng, họ chuyển từ "gắn bó tích cực" sang "Quiet Quitting" — vẫn làm nhưng không còn nỗ lực.
Khi có cơ hội bên ngoài tốt hơn, họ sẽ nghỉ ngay.

Phân tích:
1. Tại sao nhân viên mới vẫn kỳ vọng nhưng nhân viên cũ đã mất hy vọng?
2. Lộ trình thăng tiến hiện tại có rõ ràng không? Có ví dụ thực tế không?
3. Đề xuất giải pháp: Career Conversation, Skill Matrix, hay Internal Mobility?
"""
    
    elif anomaly_id == 'TC3_tool_barrier':
        tool_q = data['question']
        tool_label = get_question_label(group_id, tool_q)
        result['breakdown']['tool_score'] = {
            'Câu hỏi': f'{tool_q}: {tool_label}',
            'Điểm TB': data['score'],
            '% Đánh giá 1-2': (df[tool_q] <= 2).mean() * 100 if tool_q in df.columns else 0,
        }
        
        result['ai_prompt'] = f"""
Dữ liệu TC3 của nhóm {group_id}:
- {tool_q} ({tool_label}): {data['score']:.2f} điểm
- Tỷ lệ đánh giá kém (1-2 điểm): {result['breakdown']['tool_score']['% Đánh giá 1-2']:.1f}%

BẤT THƯỜNG: Công cụ/thiết bị đang CẢN TRỞ công việc hàng ngày.

Vòng lặp tiêu cực: App/Thiết bị kém → Năng suất thấp → Thu nhập thấp → Bức xúc → Nghỉ việc.

Phân tích:
1. Vấn đề cụ thể là gì? (App crash? Máy quét hỏng? Xe cũ?)
2. Ảnh hưởng đến năng suất/thu nhập như thế nào?
3. Đề xuất giải pháp ngắn hạn (workaround) và dài hạn (upgrade).
"""
    
    # ═══ TC4 Deep Dive ═══
    elif anomaly_id == 'TC4_transparency_issue':
        result['breakdown']['fairness'] = {
            'Q21 (Thu nhập phản ánh công sức)': data['Q21_mean'],
            '% Đánh giá thấp (1-2)': (df['Q21'] <= 2).mean() * 100 if 'Q21' in df.columns else 0,
        }
        
        # Thêm Q22, Q23 nếu có
        for q in ['Q22', 'Q23']:
            if q in df.columns:
                result['breakdown']['fairness'][f'{q}'] = df[q].mean()
        
        result['ai_prompt'] = f"""
Dữ liệu TC4 của nhóm {group_id}:
- Q21 (Thu nhập phản ánh công sức): {data['Q21_mean']:.2f} điểm

BẤT THƯỜNG: Nhân viên CẢM THẤY thu nhập không công bằng.

Vấn đề có thể KHÔNG phải ở MỨC LƯƠNG mà ở sự MINH BẠCH:
- Không hiểu cách tính lương
- Không biết tại sao bị phạt
- Không thấy mối liên hệ giữa nỗ lực và thu nhập

Phân tích:
1. Nhân viên đang hiểu sai về cơ chế lương, hay cơ chế thực sự có vấn đề?
2. Kênh nào để nhân viên tra cứu thu nhập? (App? Bảng lương? Hỏi TBC?)
3. Đề xuất cách tăng tính minh bạch: Real-time earnings dashboard? Monthly statement?
"""
    
    elif anomaly_id == 'TC4_income_paradox':
        result['ai_prompt'] = f"""
Dữ liệu TC4 của nhóm {group_id}:
- Điểm TC4: {data['TC4_pct']:.1f}% (tích cực)
- % Muốn nghỉ: {data['intent_low_pct']:.1f}%

NGHỊCH LÝ: Thu nhập được đánh giá TỐT nhưng vẫn muốn nghỉ.

Điều này cho thấy vấn đề KHÔNG nằm ở TIỀN mà ở yếu tố khác:
- Quản lý trực tiếp (TC2)?
- Môi trường làm việc (TC5)?
- Cơ hội phát triển (TC3)?

Phân tích:
1. Trụ cột nào có điểm thấp nhất? Đó có thể là nguyên nhân thực sự.
2. Phỏng vấn sâu 5-10 nhân viên muốn nghỉ để tìm hiểu lý do thực sự.
3. Đừng tăng lương vội — hãy fix vấn đề gốc rễ trước.
"""
    
    # ═══ TC5 Deep Dive ═══
    elif anomaly_id == 'TC5_pride_paradox':
        result['breakdown']['pride_vs_intent'] = {
            'Q28 (Tự hào)': data['Q28_mean'],
            '% Muốn nghỉ': data['intent_low_pct'],
        }
        
        # Kiểm tra các câu khác trong TC5
        for q in ['Q26', 'Q27', 'Q29']:
            if q in df.columns:
                result['breakdown']['pride_vs_intent'][f'{q}'] = df[q].mean()
        
        result['ai_prompt'] = f"""
Dữ liệu TC5 của nhóm {group_id}:
- Q28 (Tự hào là NV GHN): {data['Q28_mean']:.2f} điểm
- % Muốn nghỉ: {data['intent_low_pct']:.1f}%

NGHỊCH LÝ: YÊU công ty nhưng VẪN muốn nghỉ.

Đây là dạng "nghỉ trong tiếc nuối" — nhân viên có tình cảm với tổ chức
nhưng không chịu nổi điều kiện làm việc hàng ngày.

Nguyên nhân có thể:
- Áp lực quá tải (Q29 thấp?)
- Thu nhập không đủ sống (TC4 thấp?)
- Quản lý trực tiếp toxic (TC2 thấp?)

Phân tích:
1. Câu hỏi nào trong TC5 có điểm thấp nhất? Đó là "giọt nước tràn ly".
2. Những nhân viên tự hào nhưng muốn nghỉ — họ là ai? (Thâm niên? Vùng?)
3. Giữ chân họ bằng cách nào khi tình cảm vẫn còn?
"""
    
    elif anomaly_id == 'TC5_burnout_blind':
        result['breakdown']['burnout_gap'] = {
            'Q29 (Cảm nhận áp lực)': data['Q29_mean'],
            'Burnout thực tế': f"{data['burnout_pct']:.1f}%",
            'Nhận định': 'Nhân viên KHÔNG NHẬN RA mình đang kiệt sức',
        }
        
        result['ai_prompt'] = f"""
Dữ liệu TC5 của nhóm {group_id}:
- Q29 (Áp lực không ảnh hưởng cuộc sống): {data['Q29_mean']:.2f} điểm (CAO = cảm thấy OK)
- Burnout Score thực tế: {data['burnout_pct']:.1f}% (CAO = nguy hiểm)

BẤT THƯỜNG: "KIỆT SỨC KHÔNG NHẬN RA"

Nhân viên NÓI rằng áp lực không ảnh hưởng, nhưng DỮ LIỆU cho thấy họ đang burnout.
Đây là dangerous blind spot — họ đã "normalize" sự kiệt sức.

Khi nhận ra thì đã quá muộn — họ sẽ nghỉ đột ngột, không báo trước.

Phân tích:
1. Tại sao họ không nhận ra? (Văn hóa "cày cuốc"? Sợ bị đánh giá yếu?)
2. Dấu hiệu burnout nào đang bị bỏ qua? (Mất ngủ? Cáu gắt? Hay ốm?)
3. Can thiệp nào giúp họ NHẬN RA trước khi quá muộn?
"""
    
    elif anomaly_id == 'TC5_social_glue':
        result['ai_prompt'] = f"""
Dữ liệu TC5 của nhóm {group_id}:
- Q27 (Đồng nghiệp hỗ trợ): {data['Q27_mean']:.2f} điểm (CAO)
- EI tổng: {data['EI']:.1f}% (THẤP)

BẤT THƯỜNG: Nhân viên GẮN BÓ VÌ ĐỒNG NGHIỆP, không vì tổ chức.

Đây là "social glue" — chất kết dính xã hội. Họ ở lại vì bạn bè, không vì công ty.

RỦI RO: Khi 1 người có ảnh hưởng nghỉ → domino effect → cả nhóm nghỉ theo.

Phân tích:
1. Ai là "influencer" trong nhóm? (Người được nhiều người quý mến?)
2. Nếu người đó nghỉ, bao nhiêu người sẽ nghỉ theo?
3. Làm sao để chuyển "gắn bó vì bạn" thành "gắn bó vì tổ chức"?
"""
    
    # ═══ Cross-pillar Deep Dive ═══
    elif anomaly_id == 'XP_silent_disengaged':
        result['ai_prompt'] = f"""
Dữ liệu tổng hợp của nhóm {group_id}:
- EI (Engagement Index): {data['EI']:.1f}% (THẤP)
- % Muốn nghỉ: {data['intent_low_pct']:.1f}% (CŨNG THẤP)

NGHỊCH LÝ: "BUÔNG XUÔI THẦM LẶNG" (Quiet Quitting)

Nhân viên KHÔNG gắn kết nhưng CŨNG KHÔNG muốn nghỉ.
Họ đã "check out" — vẫn đi làm nhưng không còn nỗ lực, không đóng góp ý tưởng.

Đây là dạng nguy hiểm nhất vì:
- Không nhìn thấy trong chỉ số nghỉ việc
- Ảnh hưởng đến năng suất và văn hóa team
- Khi có cơ hội tốt hơn, họ sẽ nghỉ ngay

Phân tích:
1. Trụ cột nào có điểm thấp nhất? Đó là nguyên nhân khiến họ buông xuôi.
2. Họ có biết mình đang quiet quitting không?
3. Làm sao để "đánh thức" họ trước khi họ rời đi?
"""
    
    elif anomaly_id == 'XP_onboarding_shock':
        result['ai_prompt'] = f"""
Dữ liệu nhân viên mới (<3 tháng) của nhóm {group_id}:
- EI: {data['new_ei']:.1f}% (RẤT THẤP)
- Số lượng: {data['n_new']} người

BẤT THƯỜNG: "SỐC ONBOARDING"

Nhân viên mới đang trải qua giai đoạn khó khăn nhất:
- Chưa quen việc → năng suất thấp → thu nhập thấp
- Chưa có mối quan hệ → cô đơn
- Chưa hiểu văn hóa → lạc lõng

Nếu không can thiệp trong 30 ngày đầu, 60-70% sẽ nghỉ trong 3 tháng đầu.

Phân tích:
1. Giai đoạn nào trong onboarding gây sốc nhất? (Tuần 1? Tháng 1?)
2. Buddy/Mentor program có hoạt động không?
3. Đề xuất "30-Day Survival Kit" cho nhân viên mới.
"""
    
    return result


# ═══════════════════════════════════════════════════════════════
# RENDER FUNCTIONS
# ═══════════════════════════════════════════════════════════════

def render_anomaly_alert(anomaly, deep_dive_data, group_id):
    """
    Render alert banner cho 1 anomaly.
    Gọn gàng, không chiếm nhiều space.
    """
    import streamlit as st
    
    pattern = deep_dive_data['pattern']
    if not pattern:
        return
    
    severity = anomaly.get('severity', 'medium')
    border_color = '#DC2626' if severity == 'high' else pattern.get('color', '#F59E0B')
    bg_color = '#FEF2F2' if severity == 'high' else '#FFFBEB'
    
    # Alert banner
    st.markdown(f"""
    <div style="background: {bg_color}; border: 1px solid {border_color}40; border-left: 4px solid {border_color}; 
                border-radius: 8px; padding: 12px 16px; margin-bottom: 12px;">
        <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 6px;">
            <span style="font-size: 1.1rem;">{pattern.get('icon', '⚠️')}</span>
            <strong style="color: {border_color}; font-size: 0.88rem;">{pattern.get('label', 'Cảnh báo')}</strong>
            <span style="background: {border_color}20; color: {border_color}; font-size: 0.68rem; 
                         padding: 2px 8px; border-radius: 10px; margin-left: auto;">
                {'Ưu tiên cao' if severity == 'high' else 'Cần theo dõi'}
            </span>
        </div>
        <div style="font-size: 0.82rem; color: #475569; line-height: 1.5;">
            {pattern.get('desc', '')}
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Deep dive data (compact)
    if deep_dive_data.get('breakdown'):
        with st.expander(f"📊 Chi tiết phân tích", expanded=False):
            for key, value in deep_dive_data['breakdown'].items():
                if isinstance(value, pd.DataFrame):
                    st.markdown(f"**{key.replace('_', ' ').title()}:**")
                    st.dataframe(value, width='stretch', hide_index=True)
                elif isinstance(value, dict):
                    st.markdown(f"**{key.replace('_', ' ').title()}:**")
                    for k, v in value.items():
                        if isinstance(v, float):
                            st.markdown(f"- {k}: **{v:.2f}**")
                        else:
                            st.markdown(f"- {k}: **{v}**")
    
    # AI Insight
    if deep_dive_data.get('ai_prompt'):
        from utils.ai_generator import render_ai_insight_card
        ai_data = {
            'group_id': group_id,
            'anomaly_id': anomaly['id'],
            'metrics': anomaly['data'],
        }
        render_ai_insight_card(
            "AI Deep Dive Insight",
            ai_data,
            deep_dive_data['ai_prompt'],
            badge="Anomaly Analyzer",
            custom_style="margin-top: 8px; margin-bottom: 16px;"
        )


def render_pillar_anomalies(df, group_id, pillar_id):
    """
    Render tất cả anomalies cho 1 trụ cột.
    Returns: True nếu có anomaly, False nếu không.
    """
    import streamlit as st
    
    anomalies = detect_pillar_anomalies(df, group_id, pillar_id)
    
    if not anomalies:
        return False
    
    # Filter out cross-pillar if not relevant to this pillar
    pillar_anomalies = [a for a in anomalies if not a.get('cross_pillar', False)]
    cross_anomalies = [a for a in anomalies if a.get('cross_pillar', False)]
    
    # Render pillar-specific anomalies
    for anomaly in pillar_anomalies[:2]:  # Max 2 per pillar to keep it clean
        deep_dive = deep_dive_anomaly(df, group_id, pillar_id, anomaly)
        render_anomaly_alert(anomaly, deep_dive, group_id)
    
    # Render cross-pillar anomalies (only once, in TC1 tab)
    if pillar_id == 'TC1' and cross_anomalies:
        st.markdown("---")
        st.markdown("**🔍 Phát hiện liên trụ cột:**")
        for anomaly in cross_anomalies[:1]:  # Max 1 cross-pillar
            deep_dive = deep_dive_anomaly(df, group_id, pillar_id, anomaly)
            render_anomaly_alert(anomaly, deep_dive, group_id)
    
    return True
