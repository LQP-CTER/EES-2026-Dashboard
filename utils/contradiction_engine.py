"""
Contradiction Engine — EES 2026
Tự động phát hiện các mâu thuẫn dữ liệu (contradictions) trong khảo sát.
Mỗi contradiction = một "câu chuyện" đáng kể cho lãnh đạo.

Ví dụ mâu thuẫn:
- Lương cao nhưng vẫn muốn nghỉ
- Tự hào về công ty nhưng burnout cao
- Tin BLĐ nhưng không được thông báo kịp thời
- Quản lý tốt nhưng tổ chức yếu
"""

import pandas as pd
import numpy as np
from shared.codebook import PILLAR_META, PILLAR_ORDER, get_pillar_questions, get_question_label


def detect_contradictions(df, group_id, cfg):
    """
    Phát hiện tất cả mâu thuẫn trong dữ liệu của một nhóm.
    Returns: list[dict] sorted by impact_score descending.
    Mỗi dict: {
        'id': str,
        'title': str,
        'narrative': str,
        'type': str (paradox|gap|cliff|blind_spot),
        'severity': str (critical|warning|info),
        'impact_score': float (0-100),
        'metrics': dict,
        'pillar': str or 'CROSS',
        'deep_dive_fn': callable or None,
    }
    """
    contradictions = []
    group_name = cfg.get('short', group_id)

    ei = df['EI'].mean() if 'EI' in df.columns else None
    enps = df['eNPS'].mean() if 'eNPS' in df.columns else None
    intent_low = (df['intent'] <= 2).mean() * 100 if 'intent' in df.columns else None
    mei = df['MEI'].mean() if 'MEI' in df.columns else None
    burnout = (df['burnout_risk'] > 0).mean() * 100 if 'burnout_risk' in df.columns else None

    def _qmean(q):
        return df[q].mean() if q in df.columns else None

    # ── CROSS-PILLAR CONTRADICTIONS ──

    # 1. Pride Paradox: Tự hào nhưng muốn nghỉ
    q28 = _qmean('Q28')
    if q28 and intent_low and q28 > 3.8 and intent_low > 15:
        contradictions.append({
            'id': 'PRIDE_PARADOX',
            'title': f'Nghịch lý Tự hào: Yêu công ty nhưng {intent_low:.0f}% muốn nghỉ',
            'narrative': (
                f"Nhân viên {group_name} tự hào về GHN (Q28={q28:.2f}/5) "
                f"nhưng {intent_low:.1f}% vẫn muốn rời đi. "
                f"Đây là dạng 'nghỉ trong tiếc nuối' — họ yêu tổ chức "
                f"nhưng điều kiện làm việc đang buộc họ ra đi."
            ),
            'type': 'paradox',
            'severity': 'critical' if intent_low > 25 else 'warning',
            'impact_score': min(100, intent_low * 2.5 + (q28 - 3.5) * 20),
            'metrics': {'Q28_tu_hao': q28, 'intent_low_pct': intent_low},
            'pillar': 'CROSS',
        })

    # 2. Silent Disengaged: EI thấp nhưng không muốn nghỉ
    if ei and intent_low and ei < 60 and intent_low < 8:
        contradictions.append({
            'id': 'SILENT_DISENGAGED',
            'title': f'Buông xuôi thầm lặng: EI chỉ {ei:.0f}% nhưng ít người muốn nghỉ',
            'narrative': (
                f"Chỉ số gắn kết chỉ {ei:.1f}% nhưng chỉ {intent_low:.1f}% muốn nghỉ. "
                f"Nhân viên đã 'check out' — vẫn đi làm nhưng không còn nỗ lực. "
                f"Đây là dạng nguy hiểm nhất vì không nhìn thấy trong chỉ số turnover."
            ),
            'type': 'paradox',
            'severity': 'critical',
            'impact_score': min(100, (100 - ei) * 1.5),
            'metrics': {'EI': ei, 'intent_low_pct': intent_low},
            'pillar': 'CROSS',
        })

    # 3. Manager Island: QL tốt nhưng tổ chức yếu
    if mei and ei and mei > 72 and ei < 62:
        contradictions.append({
            'id': 'MANAGER_ISLAND',
            'title': f'Đảo Quản lý: MEI {mei:.0f}% nhưng EI chỉ {ei:.0f}%',
            'narrative': (
                f"Quản lý trực tiếp được đánh giá tốt (MEI={mei:.1f}%) "
                f"nhưng gắn kết tổng thể chỉ {ei:.1f}%. "
                f"Nhân viên hài lòng với sếp nhưng bất mãn với tổ chức. "
                f"Khi quản lý nghỉ, nhân viên sẽ theo."
            ),
            'type': 'paradox',
            'severity': 'warning',
            'impact_score': min(100, (mei - ei) * 2.5),
            'metrics': {'MEI': mei, 'EI': ei},
            'pillar': 'CROSS',
        })

    # 4. Burnout Blind: Nói ổn nhưng burnout cao
    q29 = _qmean('Q29')
    if q29 and burnout and q29 > 3.7 and burnout > 25:
        contradictions.append({
            'id': 'BURNOUT_BLIND',
            'title': f'Kiệt sức vô hình: Nói ổn (Q29={q29:.1f}) nhưng {burnout:.0f}% burnout',
            'narrative': (
                f"Nhân viên nói áp lực không ảnh hưởng (Q29={q29:.2f}/5) "
                f"nhưng {burnout:.1f}% thực tế đang burnout. "
                f"Họ đã 'normalize' sự kiệt sức. Khi nhận ra thì đã quá muộn."
            ),
            'type': 'blind_spot',
            'severity': 'critical' if burnout > 35 else 'warning',
            'impact_score': min(100, burnout * 2),
            'metrics': {'Q29_ap_luc': q29, 'burnout_pct': burnout},
            'pillar': 'TC5',
        })

    # 4b. Burnout Trap: Burnout rất cao nhưng không muốn nghỉ
    if burnout and intent_low and burnout > 18 and intent_low < 5:
        contradictions.append({
            'id': 'BURNOUT_TRAP',
            'title': f'Cạm bẫy trung thành: Kiệt sức ({burnout:.0f}%) nhưng tỷ lệ muốn nghỉ cực thấp ({intent_low:.1f}%)',
            'narrative': (
                f"Tỷ lệ Burnout lên tới {burnout:.1f}% nhưng chỉ {intent_low:.1f}% nhân viên có ý định rời đi. "
                f"Nhân viên kiệt sức nhưng vẫn bám trụ (có thể do thị trường việc làm khó khăn hoặc do thu nhập). "
                f"Điều này rất nguy hiểm vì dẫn đến năng suất kém, sai sót vận hành, làm hỏng văn hóa tổ chức "
                f"từ bên trong thay vì chảy máu chất xám."
            ),
            'type': 'paradox',
            'severity': 'critical',
            'impact_score': min(100, burnout * 2.5 + (5 - intent_low) * 10),
            'metrics': {'burnout_pct': burnout, 'intent_low_pct': intent_low},
            'pillar': 'CROSS',
        })

    # 4c. Leadership Halo: Tin lãnh đạo cao nhưng eNPS thấp
    q9 = _qmean('Q9')
    if q9 and enps is not None and q9 > 3.4 and enps < 20:
        contradictions.append({
            'id': 'LEADERSHIP_HALO',
            'title': f'Hào quang lãnh đạo: Niềm tin cao (Q9={q9:.2f}) nhưng eNPS thấp ({enps:+.0f})',
            'narrative': (
                f"Nhân viên tin tưởng vào tầm nhìn và định hướng của Ban lãnh đạo cấp cao (Q9={q9:.2f}/5) "
                f"nhưng lại không sẵn lòng giới thiệu công ty làm nơi làm việc (eNPS chỉ {enps:+.0f}). "
                f"Lỗ hổng không nằm ở chiến lược cấp cao, mà nằm ở trải nghiệm thực tế hàng ngày, "
                f"cách thực thi ở cấp cơ sở hoặc thu nhập/môi trường."
            ),
            'type': 'paradox',
            'severity': 'warning',
            'impact_score': min(100, (q9 - 3.0) * 20 + max(0, 30 - enps)),
            'metrics': {'Q9_tin_BLD': q9, 'eNPS': enps},
            'pillar': 'CROSS',
        })

    # ── PER-PILLAR CONTRADICTIONS ──

    # 5. Info Gap (TC1): Tin BLĐ nhưng không được thông báo
    q9 = _qmean('Q9')
    q10 = _qmean('Q10')
    if q9 and q10 and (q9 - q10) > 0.5:
        contradictions.append({
            'id': 'INFO_GAP',
            'title': f'Đứt gãy thông tin: Tin BLĐ ({q9:.1f}) nhưng thông báo kém ({q10:.1f})',
            'narrative': (
                f"Nhân viên tin BLĐ đúng hướng (Q9={q9:.2f}) "
                f"nhưng không được thông báo kịp thời (Q10={q10:.2f}). "
                f"Khoảng cách {q9-q10:.2f} điểm — kênh truyền thông nội bộ đang hỏng."
            ),
            'type': 'gap',
            'severity': 'warning' if (q9 - q10) < 0.8 else 'critical',
            'impact_score': min(100, (q9 - q10) * 50),
            'metrics': {'Q9_tin_BLD': q9, 'Q10_thong_bao': q10, 'gap': q9 - q10},
            'pillar': 'TC1',
        })

    # 6. Fairness Gap (TC2): Hỗ trợ tốt nhưng phân bổ không công bằng
    q11 = _qmean('Q11')
    q12 = _qmean('Q12')
    if q11 and q12 and (q11 - q12) > 0.5:
        contradictions.append({
            'id': 'FAIRNESS_GAP',
            'title': f'Tử huyệt Công bằng: Hỗ trợ {q11:.1f} nhưng Công bằng chỉ {q12:.1f}',
            'narrative': (
                f"Quản lý hỗ trợ tốt (Q11={q11:.2f}) nhưng phân bổ không công bằng (Q12={q12:.2f}). "
                f"Khoảng cách {q11-q12:.2f} điểm — đây là 'tử huyệt cảm xúc' "
                f"kích hoạt ý định nghỉ việc mạnh nhất."
            ),
            'type': 'gap',
            'severity': 'warning' if (q11 - q12) < 0.8 else 'critical',
            'impact_score': min(100, (q11 - q12) * 55),
            'metrics': {'Q11_ho_tro': q11, 'Q12_cong_bang': q12, 'gap': q11 - q12},
            'pillar': 'TC2',
        })

    # 7. Tenure Cliff: Điểm giảm đột ngột theo thâm niên
    if 'Q5' in df.columns and 'EI' in df.columns:
        tenure_order = [
            'Dưới 1 tháng', 'Trên 1 đến 3 tháng', 'Trên 3 đến 6 tháng',
            'Trên 6 đến 9 tháng', 'Trên 9 đến 12 tháng', 'Trên 1 đến 2 năm',
            'Trên 2 đến 3 năm', 'Trên 3 đến 5 năm', 'Trên 5 năm',
        ]
        tenure_ei = []
        for t in tenure_order:
            subset = df[df['Q5'] == t]['EI']
            if len(subset) >= 10:
                tenure_ei.append({'tenure': t, 'ei': subset.mean(), 'n': len(subset)})

        if len(tenure_ei) >= 4:
            tdf = pd.DataFrame(tenure_ei)
            diffs = tdf['ei'].diff()
            max_drop_idx = diffs.idxmin()
            if pd.notna(max_drop_idx) and diffs.loc[max_drop_idx] < -5:
                cliff_tenure = tdf.loc[max_drop_idx, 'tenure']
                cliff_drop = abs(diffs.loc[max_drop_idx])
                contradictions.append({
                    'id': 'TENURE_CLIFF',
                    'title': f'Vực thẳm Thâm niên: EI giảm {cliff_drop:.0f} điểm tại "{cliff_tenure}"',
                    'narrative': (
                        f"Phát hiện 'vực thẳm' tại mốc thâm niên '{cliff_tenure}': "
                        f"EI giảm đột ngột {cliff_drop:.1f} điểm. "
                        f"Đây là thời điểm kỳ vọng ban đầu va chạm thực tế — "
                        f"cần can thiệp ngay tại mốc này."
                    ),
                    'type': 'cliff',
                    'severity': 'warning',
                    'impact_score': min(100, cliff_drop * 3),
                    'metrics': {'cliff_tenure': cliff_tenure, 'ei_drop': cliff_drop},
                    'pillar': 'CROSS',
                })

    # 8. Income Paradox (TC4): Thu nhập OK nhưng vẫn bất mãn
    q21 = _qmean('Q21')
    if q21 and intent_low and q21 > 3.5 and intent_low > 18:
        contradictions.append({
            'id': 'INCOME_PARADOX',
            'title': f'Nghịch lý Thu nhập: Q21={q21:.1f} nhưng {intent_low:.0f}% muốn nghỉ',
            'narrative': (
                f"Thu nhập được đánh giá OK (Q21={q21:.2f}) "
                f"nhưng {intent_low:.1f}% vẫn muốn nghỉ. "
                f"Vấn đề KHÔNG phải tiền — nguyên nhân nằm ở quản lý (TC2) "
                f"hoặc môi trường (TC5)."
            ),
            'type': 'paradox',
            'severity': 'warning',
            'impact_score': min(100, intent_low * 2 + (q21 - 3.0) * 15),
            'metrics': {'Q21_thu_nhap': q21, 'intent_low_pct': intent_low},
            'pillar': 'TC4',
        })

    # 9. Glass Ceiling (TC3): Nhân viên cũ không thấy thăng tiến
    q19 = _qmean('Q19')
    if q19 and 'Q5' in df.columns:
        senior_mask = df['Q5'].isin(['Trên 2 đến 3 năm', 'Trên 3 đến 5 năm', 'Trên 5 năm'])
        junior_mask = df['Q5'].isin(['Dưới 1 tháng', 'Trên 1 đến 3 tháng', 'Trên 3 đến 6 tháng'])
        senior_q19 = df.loc[senior_mask, 'Q19'].mean() if senior_mask.any() else None
        junior_q19 = df.loc[junior_mask, 'Q19'].mean() if junior_mask.any() else None
        if senior_q19 and junior_q19 and senior_q19 < 3.2 and (junior_q19 - senior_q19) > 0.3:
            contradictions.append({
                'id': 'GLASS_CEILING',
                'title': f'Trần Thủy tinh: NV cũ {senior_q19:.1f} vs NV mới {junior_q19:.1f} về thăng tiến',
                'narrative': (
                    f"Nhân viên thâm niên đánh giá lộ trình thăng tiến chỉ {senior_q19:.2f}/5 "
                    f"so với {junior_q19:.2f} của nhân viên mới. "
                    f"Khoảng cách {junior_q19-senior_q19:.2f} — họ ở lại vì quán tính, "
                    f"không vì kỳ vọng. Khi có cơ hội bên ngoài, họ sẽ đi ngay."
                ),
                'type': 'gap',
                'severity': 'warning',
                'impact_score': min(100, (junior_q19 - senior_q19) * 60),
                'metrics': {'senior_Q19': senior_q19, 'junior_Q19': junior_q19},
                'pillar': 'TC3',
            })

    # 10. MEI Shield Failure: QL tốt nhưng vẫn muốn nghỉ
    if mei and intent_low and mei > 70 and intent_low > 15:
        contradictions.append({
            'id': 'MEI_SHIELD_FAIL',
            'title': f'Tấm khiên MEI thất bại: QL tốt ({mei:.0f}%) nhưng {intent_low:.0f}% muốn nghỉ',
            'narrative': (
                f"Quản lý tốt (MEI={mei:.1f}%) đáng lẽ phải giữ được nhân viên, "
                f"nhưng {intent_low:.1f}% vẫn muốn nghỉ. "
                f"Thu nhập (TC4) hoặc điều kiện (TC3) đang 'override' vai trò quản lý."
            ),
            'type': 'paradox',
            'severity': 'warning',
            'impact_score': min(100, intent_low * 2.2),
            'metrics': {'MEI': mei, 'intent_low_pct': intent_low},
            'pillar': 'TC2',
        })

    # Sort by impact_score
    contradictions.sort(key=lambda x: x['impact_score'], reverse=True)
    return contradictions


def get_top_contradictions(contradictions, n=3):
    """Trả về top N contradictions có impact_score cao nhất."""
    return contradictions[:n]


def get_contradictions_by_type(contradictions, type_filter):
    """Lọc contradictions theo type: paradox, gap, cliff, blind_spot."""
    return [c for c in contradictions if c['type'] == type_filter]


def get_contradictions_by_pillar(contradictions, pillar_id):
    """Lọc contradictions theo pillar hoặc CROSS."""
    return [c for c in contradictions if c['pillar'] in (pillar_id, 'CROSS')]


def format_contradiction_summary(contradictions):
    """Tạo summary text cho tất cả contradictions."""
    if not contradictions:
        return "Không phát hiện mâu thuẫn dữ liệu đáng kể."

    critical = [c for c in contradictions if c['severity'] == 'critical']
    warning = [c for c in contradictions if c['severity'] == 'warning']

    lines = []
    if critical:
        lines.append(f"Phát hiện **{len(critical)} nghịch lý nghiêm trọng** cần hành động ngay:")
        for c in critical:
            lines.append(f"  - **{c['title']}** (impact: {c['impact_score']:.0f}/100)")
    if warning:
        lines.append(f"Và **{len(warning)} cảnh báo** cần theo dõi:")
        for c in warning[:3]:
            lines.append(f"  - **{c['title']}** (impact: {c['impact_score']:.0f}/100)")

    return '\n'.join(lines)
