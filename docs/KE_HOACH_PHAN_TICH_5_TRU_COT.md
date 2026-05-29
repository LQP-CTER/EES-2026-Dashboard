# KẾ HOẠCH PHÂN TÍCH 5 TRỤ CỘT × 6 NHÓM KHẢO SÁT
## EES 2026 Dashboard — Anomaly Detection + Deep Dive + AI Insight

---

## 1. TỔNG QUAN CẤU TRÚC

### 5 Trụ cột (Pillars)

| Mã | Tên | Trọng số | Ý nghĩa |
|----|-----|----------|---------|
| TC1 | Niềm tin & Định hướng | 15% | Niềm tin vào BLĐ và chiến lược |
| TC2 | Năng lực Quản lý Trực tiếp | 25% | Hỗ trợ, công bằng, phản hồi từ QL |
| TC3 | Công việc & Điều kiện VH | 20% | Công cụ, quy trình, thăng tiến |
| TC4 | Thu nhập & Tính Minh bạch | 20% | Lương, cách tính, minh bạch phạt |
| TC5 | Môi trường & Sự Gắn kết | 20% | An toàn, đồng nghiệp, tự hào |

### 6 Nhóm khảo sát

| Mã | Tên | Đặc thù |
|----|-----|---------|
| 1A | Nhân viên Giao nhận (Shipper) | Frontline, thu nhập theo đơn |
| 1B | Tài xế xe tải | Frontline, tuyến đường dài |
| 2A | Nhân viên Vận hành Kho | Ca kíp, thiết bị, năng suất |
| 2B | Quản lý Vận hành Tuyến đầu | QL cấp trung, bưu cục |
| 3A | Nhân viên Văn phòng | Back office, quy trình |
| 3B | Quản lý HQ | Lãnh đạo, chiến lược |

### Ma trận câu hỏi theo trụ cột

| Trụ cột | 1A (Shipper) | 1B (Tài xế) | 2A/2B/3A/3B |
|---------|-------------|-------------|-------------|
| TC1 | Q9, Q10 (2 câu) | Q9, Q10 (2 câu) | Q9-Q12 (4 câu) |
| TC2 | Q11-Q15 (5 câu) | Q11-Q15 (5 câu) | Q13-Q17 (5 câu) |
| TC3 | Q16-Q20 (5 câu) | Q16-Q20 (5 câu) | Q18-Q21 (4 câu) |
| TC4 | Q21-Q25 (5 câu) | Q21-Q25 (5 câu) | Q22-Q25 (4 câu) |
| TC5 | Q26-Q29 (4 câu) | Q26-Q29 (4 câu) | Q26-Q29 (4 câu) |

---

## 2. FRAMEWORK PHÂN TÍCH: DETECT → DEEP DIVE → INSIGHT

```
┌─────────────────────────────────────────────────────────────┐
│                    LUỒNG PHÂN TÍCH                          │
│                                                             │
│  [DATA] → [DETECT] → [DEEP DIVE] → [AI INSIGHT] → [ACTION] │
│                                                             │
│  1. DETECT:   Chạy anomaly rules trên từng đơn vị           │
│               (Division/Department/Section)                  │
│                                                             │
│  2. DEEP DIVE: Khi phát hiện bất thường → tự động           │
│               drill-down vào dữ liệu chi tiết               │
│                                                             │
│  3. AI INSIGHT: Gửi context + data cho AI tạo              │
│                insight giải thích + khuyến nghị              │
│                                                             │
│  4. ACTION:   Hiển thị action priority matrix               │
│               + đề xuất hành động cụ thể                    │
└─────────────────────────────────────────────────────────────┘
```

---

## 3. CHI TIẾT PHÂN TÍCH THEO TỪNG TRỤ CỘT

---

### 3.1 TC1 — NIỀM TIN & ĐỊNH HƯỚNG (15%)

#### Câu hỏi theo nhóm

| Nhóm | Câu hỏi | Nội dung |
|------|---------|----------|
| 1A | Q9 | Tin GHN đúng hướng |
| 1A | Q10 | Thông báo thay đổi kịp thời |
| 1B | Q9 | Tin GHN phát triển bền vững |
| 1B | Q10 | Thông báo thay đổi kịp thời |
| 2A/2B/3A/3B | Q9-Q12 | 4 câu về niềm tin, định hướng, thay đổi, minh bạch |

#### Anomaly Rules cho TC1

| ID | Pattern | Điều kiện | Deep Dive |
|----|---------|-----------|-----------|
| TC1_A1 | **Mất niềm tin cục bộ** | TC1 < 55% ở 1 đơn vị nhưng EI toàn công ty > 65% | So sánh đơn vị đó vs trung bình; xem Q9 vs Q10 riêng biệt |
| TC1_A2 | **Thông tin đứt gãy** | Q10 thấp hơn Q9 > 0.5 điểm | Phân tích theo thâm niên: nhóm mới vs cũ có khác nhau không? |
| TC1_A3 | **Nghịch lý tin tưởng** | TC1 cao (>75%) nhưng % Muốn nghỉ vẫn cao (>20%) | Kiểm tra TC2-TC5: có phải vấn đề nằm ở trụ cột khác? |
| TC1_A4 | **Khoảng cách thế hệ** | Gen Z < Gen X > 0.8 điểm ở TC1 | Deep dive: Gen Z trả lời Q9 hay Q10 thấp hơn? |

#### Deep Dive Logic

```python
def deep_dive_TC1(df_unit, group_id):
    """
    Khi phát hiện TC1 bất thường:
    1. So sánh Q9 vs Q10 → xác định "tin BLĐ" hay "thông tin kém"
    2. Breakdown theo: thâm niên, thế hệ, vùng
    3. Cross-reference với TC2 (quản lý có giải thích thay đổi không?)
    4. NLP: tìm phản hồi mở liên quan đến "thay đổi", "chiến lược", "không biết"
    """
    insights = {}
    
    # Q9 vs Q10 gap
    q9_mean = df_unit['Q9'].mean()
    q10_mean = df_unit['Q10'].mean()
    gap = q9_mean - q10_mean
    if abs(gap) > 0.5:
        insights['info_gap'] = {
            'Q9': q9_mean, 'Q10': q10_mean, 'gap': gap,
            'interpretation': 'Tin BLĐ nhưng KHÔNG được thông báo kịp thời' if gap > 0 
                             else 'Thông báo tốt nhưng không tin BLĐ'
        }
    
    # Tenure breakdown
    if 'Q5' in df_unit.columns:
        tenure_scores = df_unit.groupby('Q5')[['Q9','Q10']].mean()
        insights['by_tenure'] = tenure_scores
    
    # Cross-pillar check
    if 'TC2_pct' in df_unit.columns:
        tc1 = df_unit['TC1_pct'].mean()
        tc2 = df_unit['TC2_pct'].mean()
        if tc1 < 60 and tc2 > 75:
            insights['manager_island'] = True  # QL tốt nhưng tổ chức yếu
    
    return insights
```

#### AI Insight Prompt Template

```
Dữ liệu TC1 của [NHÓM] tại [ĐƠN VỊ]:
- Điểm TC1: [X]% (trung bình toàn công ty: [Y]%)
- Q9 (Tin BLĐ): [A] điểm | Q10 (Thông báo kịp thời): [B] điểm
- Phân bố theo thâm niên: [DATA]
- Cross-reference TC2: [Z]%

[BẤT THƯỜNG PHÁT HIỆN]

Hãy phân tích:
1. Tại sao đơn vị này có điểm TC1 [cao/thấp] bất thường so với mặt bằng?
2. Nếu Q10 thấp hơn Q9: kênh truyền thông nội bộ đang có vấn đề gì?
3. Đề xuất 1 hành động cụ thể trong 30 ngày để cải thiện.
```

---

### 3.2 TC2 — NĂNG LỰC QUẢN LÝ TRỰC TIẾP (25%)

#### Câu hỏi theo nhóm

| Nhóm | Câu hỏi | Nội dung chính |
|------|---------|----------------|
| 1A | Q11-Q15 | AM/TBC hỗ trợ, phân đơn công bằng, xử lý sự cố, phản hồi |
| 1B | Q11-Q15 | ĐPV giải quyết, lịch chạy công bằng, thông tin chuyến, hỗ trợ sự cố |
| 2A/2B/3A/3B | Q13-Q17 | 5 câu về quản lý trực tiếp |

#### Anomaly Rules cho TC2

| ID | Pattern | Điều kiện | Deep Dive |
|----|---------|-----------|-----------|
| TC2_A1 | **Quản lý "ốc đảo"** | TC2 > 80% nhưng EI < 60% | Nhân viên thích QL nhưng ghét công ty → xem TC1, TC4 |
| TC2_A2 | **Phân biệt đối xử** | Q12 (công bằng) < Q11 (hỗ trợ) > 0.6 điểm | Deep dive: phân đơn/lịch chạy là vấn đề, không phải hỗ trợ |
| TC2_A3 | **Quản lý yếu toàn diện** | TC2 < 50% ở đơn vị có N > 30 | Breakdown từng câu: hỗ trợ, công bằng, phản hồi, xử lý sự cố |
| TC2_A4 | **MEI shield thất bại** | MEI > 4.2 nhưng % Muốn nghỉ vẫn > 15% | Kiểm tra: có phải thu nhập (TC4) quá thấp override MEI shield? |
| TC2_A5 | **Phản hồi một chiều** | Q15 (phản hồi) thấp nhất trong TC2 | So sánh nhóm thâm niên: mới vs cũ |

#### Deep Dive Logic

```python
def deep_dive_TC2(df_unit, group_id):
    """
    TC2 là trụ cột quan trọng nhất (25% trọng số).
    Deep dive tập trung:
    1. Câu nào thấp nhất trong TC2? → xác định vấn đề cụ thể
    2. MEI (Manager Effectiveness Index) so với EI
    3. Tương quan TC2 vs Ý định nghỉ (Q30)
    4. So sánh giữa các quản lý (nếu có tên_am/tên_tbc)
    """
    insights = {}
    
    # Find weakest question
    tc2_qs = get_pillar_questions(group_id, 'TC2')
    q_means = {q: df_unit[q].mean() for q in tc2_qs if q in df_unit.columns}
    weakest_q = min(q_means, key=q_means.get)
    insights['weakest'] = {
        'question': weakest_q,
        'score': q_means[weakest_q],
        'label': get_question_label(group_id, weakest_q)
    }
    
    # MEI vs EI comparison
    mei = df_unit['MEI'].mean() if 'MEI' in df_unit.columns else None
    ei = df_unit['EI'].mean() if 'EI' in df_unit.columns else None
    if mei and ei:
        if mei > 75 and ei < 60:
            insights['pattern'] = 'manager_island'
        elif mei < 50 and ei > 70:
            insights['pattern'] = 'resilient_culture'  # Văn hóa mạnh bù QL yếu
    
    # Manager-level comparison (if available)
    if 'tên_tbc' in df_unit.columns:
        mgr_scores = df_unit.groupby('tên_tbc')[tc2_qs].mean().mean(axis=1)
        insights['manager_variance'] = {
            'best': mgr_scores.idxmax(),
            'worst': mgr_scores.idxmin(),
            'spread': mgr_scores.max() - mgr_scores.min()
        }
    
    return insights
```

---

### 3.3 TC3 — CÔNG VIỆC & ĐIỀU KIỆN VẬN HÀNH (20%)

#### Câu hỏi theo nhóm

| Nhóm | Câu hỏi | Nội dung chính |
|------|---------|----------------|
| 1A | Q16-Q20 | App Driver, công cụ, cường độ, thăng tiến, hướng dẫn thay đổi |
| 1B | Q16-Q20 | Xe an toàn, lịch chạy, ATLĐ, thăng tiến, hướng dẫn |
| 2A/2B/3A/3B | Q18-Q21 | 4 câu về điều kiện làm việc |

#### Anomaly Rules cho TC3

| ID | Pattern | Điều kiện | Deep Dive |
|----|---------|-----------|-----------|
| TC3_A1 | **Công cụ cản trở** | Q16 (App/thiết bị) < 3.5 | Cross-ref năng suất (HRIS): app kém → năng suất thấp → thu nhập thấp? |
| TC3_A2 | **Burnout ẩn** | Q18 (cường độ) thấp nhưng Burnout Score cao (>30%) | Phân tích: cường độ cảm nhận vs burnout thực tế |
| TC3_A3 | **Trần thủy tinh** | Q19 (thăng tiến) < 3.0 ở nhóm thâm niên > 2 năm | So sánh nhóm < 1 năm vs > 2 năm: kỳ vọng vs thực tế |
| TC3_A4 | **Thay đổi không hướng dẫn** | Q20 thấp nhất trong TC3 | Correlate với Q10 (TC1): thông báo kém + không hướng dẫn = double gap |
| TC3_A5 | **An toàn bị xem nhẹ** | Q18 (ATLĐ, 1B) < 3.5 | Cross-ref NLP: tìm phản hồi về "tai nạn", "nguy hiểm", "sợ" |

#### Deep Dive Logic

```python
def deep_dive_TC3(df_unit, group_id, df_hris=None):
    """
    TC3 liên quan trực tiếp đến HRIS (năng suất, thiết bị).
    Deep dive:
    1. Câu nào thấp nhất? → công cụ, cường độ, hay thăng tiến?
    2. Nếu có HRIS: tương quan điểm TC3 vs năng suất thực tế
    3. Breakdown theo ca làm việc (nếu có)
    4. So sánh thâm niên: nhóm mới thấy TC3 khác nhóm cũ không?
    """
    insights = {}
    
    tc3_qs = get_pillar_questions(group_id, 'TC3')
    q_means = {q: df_unit[q].mean() for q in tc3_qs if q in df_unit.columns}
    
    # Career path analysis (Q19)
    if 'Q19' in df_unit.columns and 'Q5' in df_unit.columns:
        career_by_tenure = df_unit.groupby('Q5')['Q19'].mean()
        # Nhóm > 2 năm đánh giá thăng tiến thấp = trần thủy tinh
        senior_mask = df_unit['Q5'].isin(['Trên 2 đến 3 năm', 'Trên 3 đến 5 năm', 'Trên 5 năm'])
        senior_career = df_unit.loc[senior_mask, 'Q19'].mean()
        junior_career = df_unit.loc[~senior_mask, 'Q19'].mean()
        if senior_career < junior_career - 0.3:
            insights['glass_ceiling'] = {
                'senior_score': senior_career,
                'junior_score': junior_career,
                'gap': junior_career - senior_career
            }
    
    # HRIS linkage (if available)
    if df_hris is not None and 'income_m' in df_hris.columns:
        # Correlate TC3 score with actual income
        tc3_score = df_unit[tc3_qs].mean(axis=1)
        corr = tc3_score.corr(df_hris['income_m'])
        insights['tc3_income_corr'] = corr
    
    return insights
```

---

### 3.4 TC4 — THU NHẬP & TÍNH MINH BẠCH (20%)

#### Câu hỏi theo nhóm

| Nhóm | Câu hỏi | Nội dung chính |
|------|---------|----------------|
| 1A | Q21-Q25 | Thu nhập phản ánh công sức, App rõ phạt, hiểu cách tính, phân đơn hợp lý, hỗ trợ sự cố |
| 1B | Q21-Q25 | Thu nhập, phụ cấp, tuyến công bằng, bảo hộ, hỗ trợ sự cố |
| 2A/2B/3A/3B | Q22-Q25 | 4 câu về đãi ngộ |

#### Anomaly Rules cho TC4

| ID | Pattern | Điều kiện | Deep Dive |
|----|---------|-----------|-----------|
| TC4_A1 | **Thu nhập bất công cảm nhận** | Q21 < 3.5 nhưng thu nhập thực tế > trung bình | Vấn đề là MINH BẠCH, không phải mức lương |
| TC4_A2 | **Phạt không minh bạch** | Q22 (hiển thị rõ phạt) < Q21 (thu nhập) > 0.5 | Deep dive: bao nhiêu % bị phạt? Mức phạt TB? |
| TC4_A3 | **Thu nhập đủ nhưng vẫn muốn nghỉ** | TC4 > 70% nhưng % Muốn nghỉ > 20% | Vấn đề nằm ở TC2 hoặc TC5, không phải tiền |
| TC4_A4 | **Chênh lệch thu nhập cực đoan** | HRIS: top 10% thu nhập > 3× bottom 10% | Phân tích: công bằng hay bất công? Do năng suất hay do tuyến? |
| TC4_A5 | **Hỗ trợ sự cố kém** | Q25 thấp nhất trong TC4 | Cross-ref NLP: tìm phản hồi về "sự cố", "bồi thường", "không ai giúp" |

#### Deep Dive Logic

```python
def deep_dive_TC4(df_unit, group_id, df_hris=None):
    """
    TC4 là trụ cột nhạy cảm nhất — liên quan trực tiếp đến tiền.
    Deep dive:
    1. Q21 (thu nhập phản ánh công sức) vs thu nhập thực tế → công bằng hay không?
    2. Q22 (minh bạch phạt) → bao nhiêu người bị phạt? Trung bình bao nhiêu?
    3. HRIS: phân bố thu nhập — có bất công cực đoan không?
    4. Tương quan TC4 vs Ý định nghỉ
    """
    insights = {}
    
    # Income fairness check
    if 'Q21' in df_unit.columns:
        q21_mean = df_unit['Q21'].mean()
        if df_hris is not None and 'income_m' in df_hris.columns:
            actual_income = df_hris['income_m'].mean()
            # Nếu lương thực tế cao nhưng Q21 thấp → vấn đề minh bạch
            if actual_income > 8.0 and q21_mean < 3.5:
                insights['transparency_issue'] = {
                    'actual_income': actual_income,
                    'perceived_fairness': q21_mean,
                    'interpretation': 'Thu nhập tốt nhưng nhân viên CẢM THẤY bất công'
                }
    
    # Penalty analysis
    if df_hris is not None and 'tong_phat' in df_hris.columns:
        pct_penalized = (df_hris['tong_phat'] > 0).mean() * 100
        avg_penalty = df_hris['tong_phat'].mean()
        insights['penalty'] = {
            'pct_penalized': pct_penalized,
            'avg_penalty': avg_penalty,
            'max_penalty': df_hris['tong_phat'].max()
        }
    
    # TC4 vs Intent correlation
    if 'intent' in df_unit.columns:
        tc4_qs = get_pillar_questions(group_id, 'TC4')
        tc4_score = df_unit[tc4_qs].mean(axis=1)
        intent_corr = tc4_score.corr(df_unit['intent'])
        insights['tc4_intent_corr'] = intent_corr
    
    return insights
```

---

### 3.5 TC5 — MÔI TRƯỜNG & SỰ GẮN KẾT (20%)

#### Câu hỏi theo nhóm

| Nhóm | Câu hỏi | Nội dung chính |
|------|---------|----------------|
| 1A | Q26-Q29 | ATGT, đồng nghiệp hỗ trợ, tự hào, áp lực không ảnh hưởng cuộc sống |
| 1B | Q26-Q29 | Đội vận tải hỗ trợ, tự hào, áp lực, được tôn trọng |
| 2A/2B/3A/3B | Q26-Q29 | 4 câu về môi trường, gắn kết |

#### Anomaly Rules cho TC5

| ID | Pattern | Điều kiện | Deep Dive |
|----|---------|-----------|-----------|
| TC5_A1 | **Tự hào nhưng kiệt sức** | Q28 (tự hào) > 4.0 nhưng Q29 (áp lực) < 3.0 | Yêu công ty nhưng không chịu nổi → burnout sắp xảy ra |
| TC5_A2 | **Đồng nghiệp tốt, công ty tệ** | Q27 (đồng nghiệp) > 4.0 nhưng EI < 55% | Gắn bó vì bạn bè, không vì tổ chức → rủi ro khi bạn nghỉ |
| TC5_A3 | **Áp lực xâm lấn cuộc sống** | Q29 < 3.0 ở nhóm thâm niên < 6 tháng | Onboarding quá khắc nghiệt → sốc văn hóa |
| TC5_A4 | **Thiếu an toàn tâm lý** | Q29 thấp + NLP phát hiện "sợ", "áp lực", "stress" | Deep dive NLP: tìm pattern cụ thể |
| TC5_A5 | **Burnout nghịch lý** | Burnout > 30% nhưng Q29 (áp lực) > 4.0 | Nhân viên KHÔNG NHẬN RA mình đang burnout |

#### Deep Dive Logic

```python
def deep_dive_TC5(df_unit, group_id):
    """
    TC5 phản ánh sức khỏe tinh thần và văn hóa.
    Deep dive:
    1. Q29 (áp lực) vs Burnout Score → có mismatch không?
    2. Q28 (tự hào) vs Ý định nghỉ → tự hào nhưng vẫn muốn nghỉ = vấn đề cấu trúc
    3. NLP: phân tích phản hồi mở về áp lực, đồng nghiệp, văn hóa
    4. So sánh thế hệ: Gen Z nhạy cảm hơn với áp lực?
    """
    insights = {}
    
    # Pride vs Intent paradox
    if 'Q28' in df_unit.columns and 'intent' in df_unit.columns:
        q28_mean = df_unit['Q28'].mean()
        quit_pct = (df_unit['intent'] <= 2).mean() * 100
        if q28_mean > 4.0 and quit_pct > 15:
            insights['pride_paradox'] = {
                'pride': q28_mean,
                'quit_intent': quit_pct,
                'interpretation': 'Tự hào về công ty nhưng VẪN muốn nghỉ → vấn đề ở điều kiện, không phải tình cảm'
            }
    
    # Burnout awareness gap
    if 'Q29' in df_unit.columns and 'burnout_risk' in df_unit.columns:
        q29_mean = df_unit['Q29'].mean()
        burnout_pct = (df_unit['burnout_risk'] > 0).mean() * 100
        if q29_mean > 3.8 and burnout_pct > 25:
            insights['burnout_blind_spot'] = {
                'perceived_pressure': q29_mean,
                'actual_burnout': burnout_pct,
                'interpretation': 'Nhân viên KHÔNG NHẬN RA mình đang kiệt sức'
            }
    
    # Peer bond vs org bond
    if 'Q27' in df_unit.columns:
        q27_mean = df_unit['Q27'].mean()
        ei = df_unit['EI'].mean() if 'EI' in df_unit.columns else None
        if ei and q27_mean > 4.0 and ei < 55:
            insights['social_glue'] = {
                'peer_bond': q27_mean,
                'org_engagement': ei,
                'risk': 'Nhân viên ở lại vì đồng nghiệp, không vì tổ chức. Khi bạn thân nghỉ → domino effect.'
            }
    
    return insights
```

---

## 4. CROSS-PILLAR ANOMALY PATTERNS (Liên trụ cột)

Đây là những pattern chỉ phát hiện được khi phân tích NHIỀU trụ cột cùng lúc:

| ID | Pattern | Điều kiện | Ý nghĩa |
|----|---------|-----------|---------|
| XP_1 | **Committed Under Pressure** | Burnout > 12% + Muốn nghỉ < 5% | Áp lực cao nhưng gắn bó vì lý do khác → sẽ "flip" đột ngột |
| XP_2 | **Silent Disengaged** | EI < 55% + Muốn nghỉ < 5% | Quiet Quitting — buông xuôi nhưng không nghỉ |
| XP_3 | **Manager Island** | TC2 > 80% + EI < 60% | QL tốt nhưng tổ chức yếu |
| XP_4 | **Flight Risk Cluster** | Muốn nghỉ > 20% ở 1 đơn vị | Nghỉ hàng loạt — cần can thiệp khẩn |
| XP_5 | **Income Paradox** | TC4 cao + EI thấp | Tiền tốt nhưng vẫn không gắn kết |
| XP_6 | **Onboarding Shock (EWS)** | Tenure ≤ 3 tháng + Q22 thấp + TC2/TC3 thấp | Sốc onboarding, cảnh báo nghỉ việc sớm (Early Warning Score) |
| XP_7 | **Tenure Cliff** | Điểm giảm đột ngột ở mốc 12-18 tháng | "Cliff" — khi kỳ vọng gặp thực tế |
| XP_8 | **Generation Gap** | Gen Z < Gen X > 1.0 điểm ở > 2 trụ cột | Khác biệt thế hệ hệ thống |
| XP_9 | **Engagement Quadrant** | Phân loại 4 nhóm dựa trên eNPS và Q22 | Tách bạch Champions, Trapped Loyalists, Confused Leavers, Flight Risk |
| XP_10 | **Contradiction Index** | EI > 75% nhưng Open-text Sentiment tiêu cực > 40% | Sức khỏe giả, "sợ nói thật" (Fear-based compliance) |
| XP_11 | **Satisfaction Gap (JSI)** | Phân tích JSI Proxy (0.4*TC4 + 0.3*TC3_workload + 0.3*TC5_respect) vs EI | Hài lòng công việc hiện tại nhưng không gắn kết, hay ngược lại |

---

## 4.1 CÁC CHỈ SỐ NỀN TẢNG (FOUNDATION INDICES) BỔ SUNG

Ngoài 5 trụ cột, mô hình phân tích cần đo lường:
1. **Silence Rate**: Tỷ lệ không điền câu hỏi mở (Q26). Silence rate càng cao = nhân viên càng thiếu niềm tin vào việc phản hồi có tác dụng.
2. **Engagement Quadrant Matrix**:
   - *Champions*: eNPS cao + Q22 cao (gắn kết & ở lại).
   - *Trapped Loyalists*: eNPS thấp + Q22 cao (disengaged nhưng chưa nghỉ).
   - *Confused Leavers*: eNPS cao + Q22 thấp (thích công ty nhưng sắp đi).
   - *Flight Risk*: eNPS thấp + Q22 thấp (đang lên kế hoạch rời đi).
3. **JSI (Overall Job Satisfaction Index) Proxy**: Ước tính mức độ hài lòng chung bằng công thức `JSI ≈ 0.4*TC4 + 0.3*TC3_workload + 0.3*TC5_respect`. Dùng để phân tích chéo "Hài lòng" vs "Gắn kết".
4. **Early Warning Score (EWS)**: Cảnh báo nghỉ việc sớm ở nhóm thâm niên ≤ 3 tháng thông qua Q22, TC2, TC3.

---

## 5. DEEP DIVE FLOW THEO TỪNG NHÓM

### 5.1 Nhóm 1A — Shipper / NVPTTT

```
DETECT: Chạy anomaly rules trên từng Bưu cục (section)
    │
    ├── TC1 bất thường → So sánh Q9 vs Q10, breakdown theo tuyến
    ├── TC2 bất thường → So sánh giữa các TBC/AM, xem Q12 (phân đơn)
    ├── TC3 bất thường → Cross-ref HRIS: năng suất giao, App Driver
    ├── TC4 bất thường → Phân tích phạt COD, thu nhập thực tế vs cảm nhận
    └── TC5 bất thường → NLP phản hồi về ATGT, áp lực, đồng nghiệp
    
DEEP DIVE TRIGGER:
    - Bưu cục có % Muốn nghỉ > 20% → drill down vào từng trụ cột
    - Bưu cục có MEI > 4.2 nhưng vẫn muốn nghỉ > 15% → kiểm tra TC4
    - Shipper mới (<2 tháng) có TC4 < 3.0 → onboarding shock
```

### 5.2 Nhóm 1B — Tài xế xe tải

```
DETECT: Chạy anomaly rules trên từng Đội xe (section)
    │
    ├── TC1 bất thường → Thông tin thay đổi có đến được tài xế không?
    ├── TC2 bất thường → ĐPV phân tuyến công bằng? (Q12)
    ├── TC3 bất thường → Xe an toàn? Lịch chạy hợp lý?
    ├── TC4 bất thường → Phụ cấp minh bạch? Tuyến công bằng?
    └── TC5 bất thường → Đội vận tải hỗ trợ nhau?
    
DEEP DIVE TRIGGER:
    - Đội xe có Q17 (lịch chạy) < 3.5 → burnout risk cao
    - Tài xế > 2 năm có Q19 (thăng tiến) < 3.0 → trần thủy tinh
    - Tuyến đường dài vs ngắn: chênh lệch thu nhập
```

### 5.3 Nhóm 2A — Nhân viên Kho

```
DETECT: Chạy anomaly rules trên từng Kho/TTTC (section)
    │
    ├── TC1 bất thường → NV kho có hiểu chiến lược không?
    ├── TC2 bất thường → Quản lý kho hỗ trợ? Phân công công bằng?
    ├── TC3 bất thường → Thiết bị hỏng? Ca đêm liên tục?
    ├── TC4 bất thường → KPI năng suất công bằng?
    └── TC5 bất thường → An toàn lao động? Đồng nghiệp?
    
DEEP DIVE TRIGGER:
    - Kho có ca đêm > 50% → so sánh EI ca đêm vs ca ngày
    - Thiết bị (Q18) < 3.5 → cross-ref KPI năng suất
    - Thăng tiến (Q19) < 3.0 ở nhóm > 12 tháng → quiet quitting
```

### 5.4 Nhóm 2B — Quản lý Vận hành Tuyến đầu

```
DETECT: Chạy anomaly rules trên từng Phòng ban/Bưu cục (section)
    │
    ├── TC1 bất thường → QL có hiểu và tin chiến lược không?
    ├── TC2 bất thường → QL cấp trên có hỗ trợ QL cấp trung?
    ├── TC3 bất thường → Công cụ quản lý? Quy trình?
    ├── TC4 bất thường → Đãi ngộ quản lý tương xứng?
    └── TC5 bất thường → Áp lực kép? Cô đơn ở tầng giữa?
    
DEEP DIVE TRIGGER:
    - QL có TC2 thấp → nhân viên của họ cũng sẽ có TC2 thấp (domino)
    - Burnout > 30% ở QL → rủi ro domino cho toàn đội
    - MEI cao nhưng EI thấp → manager island pattern
```

### 5.5 Nhóm 3A — Nhân viên Văn phòng

```
DETECT: Chạy anomaly rules trên từng Phòng ban (department)
    │
    ├── TC1 bất thường → Strategy-Execution Gap
    ├── TC2 bất thường → QL có ghi nhận đóng góp?
    ├── TC3 bất thường → Process Debt? Hệ thống hiệu quả?
    ├── TC4 bất thường → Lương BO công bằng so với frontline?
    └── TC5 bất thường → Vô hình nội bộ? Thiếu ghi nhận?
    
DEEP DIVE TRIGGER:
    - TC1 thấp + TC3 thấp → "Nợ quy trình" + mất niềm tin
    - Q29 (áp lực) thấp + Burnout cao → invisible burnout
    - Phòng ban có EI < 50% nhưng Muốn nghỉ < 5% → silent disengaged
```

### 5.6 Nhóm 3B — Quản lý HQ

```
DETECT: Chạy anomaly rules trên từng Khối (division)
    │
    ├── TC1 bất thường → Mơ hồ chiến lược ở chính người hoạch định?
    ├── TC2 bất thường → QL cấp cao có hỗ trợ QL cấp trung?
    ├── TC3 bất thường → Công cụ ra quyết định? Dữ liệu?
    ├── TC4 bất thường → Đãi ngộ QL tương xứng trách nhiệm?
    └── TC5 bất thường → Cô đơn ở tầng cao? Thiếu peer forum?
    
DEEP DIVE TRIGGER:
    - TC1 thấp ở 3B → toàn bộ tổ chức sẽ có TC1 thấp (cascade)
    - Burnout cao + Q29 (áp lực) cao → "mạnh mẽ giả tạo"
    - 3B có EI thấp → báo động đỏ cho sức khỏe tổ chức dài hạn
```

---

## 6. AI INSIGHT PROMPT TEMPLATES

### 6.1 Prompt cho Anomaly Detection

```python
ANOMALY_INSIGHT_PROMPT = """
Bạn là Chuyên gia People Analytics cấp cao, đang phân tích khảo sát EES cho [NHÓM].

DỮ LIỆU PHÁT HIỆN BẤT THƯỜNG:
- Đơn vị: [TÊN ĐƠN VỊ]
- Pattern: [TÊN PATTERN]
- Chỉ số liên quan:
  {metrics_json}

BỐI CẢNH:
- Trung bình toàn công ty: [EI/MEI/TCx]
- Đặc thù nhóm: [MÔ TẢ NGẮN]

YÊU CẦU:
1. Giải thích TẠI SAO pattern này xuất hiện ở đơn vị này mà không phải đơn vị khác?
2. Nếu không can thiệp, điều gì sẽ xảy ra trong 3-6 tháng tới?
3. Đề xuất 1 hành động CỤ THỂ, KHẢ THI trong 30 ngày.

Viết dưới dạng báo cáo ngắn cho Giám đốc HR, không dùng thuật ngữ kỹ thuật.
"""
```

### 6.2 Prompt cho Cross-Pillar Analysis

```python
CROSS_PILLAR_PROMPT = """
Bạn đang phân tích sức khỏe tổ chức của [NHÓM] tại [ĐƠN VỊ].

DỮ LIỆU 5 TRỤ CỘT:
- TC1 (Niềm tin & Định hướng): [X]%
- TC2 (Quản lý Trực tiếp): [Y]%
- TC3 (Công việc & Điều kiện): [Z]%
- TC4 (Thu nhập & Minh bạch): [W]%
- TC5 (Môi trường & Gắn kết): [V]%
- EI tổng: [EI]%
- % Muốn nghỉ: [R]%
- Burnout: [B]%

BẤT THƯỜNG LIÊN TRỤ CỘT:
[PATTERN DESCRIPTION]

PHÂN TÍCH:
1. Trụ cột nào là "nút thắt cổ chai" — cải thiện nó sẽ kéo các trụ cột khác lên?
2. Có mâu thuẫn nào giữa các chỉ số không? (VD: lương tốt nhưng vẫn muốn nghỉ)
3. Nếu chỉ có ngân sách cho 1 can thiệp, nên đầu tư vào đâu?
"""
```

### 6.3 Prompt cho Deep Dive Report

```python
DEEP_DIVE_PROMPT = """
BÁO CÁO DEEP DIVE — [TÊN ĐƠN VỊ] thuộc [NHÓM]

DỮ LIỆU CHI TIẾT:
{detailed_data_json}

SO SÁNH VỚI TRUNG BÌNH:
- Đơn vị này: [DATA]
- Trung bình nhóm: [DATA]
- Trung bình toàn công ty: [DATA]

CÂU HỎI CẦN TRẢ LỜI:
1. Vấn đề cốt lõi là gì? (Không phải triệu chứng, mà là NGUYÊN NHÂN)
2. Ai bị ảnh hưởng nhiều nhất? (Nhóm thâm niên nào? Thế hệ nào?)
3. Có pattern nào lặp lại không? (Theo mùa? Theo ca? Theo quản lý?)
4. Nếu bạn là HRBP phụ trách đơn vị này, bạn sẽ làm gì trong tuần đầu tiên?

Format: 2-3 đoạn văn, data-driven, actionable.
"""
```

---

## 7. IMPLEMENTATION ROADMAP

### Phase 1: Foundation (Hiện tại)
- [x] Codebook 6 nhóm
- [x] Pillar renderer với 4-5 tabs
- [x] Anomaly detector cơ bản (6 patterns)
- [x] AI insight generation (Groq)
- [x] View_a: KPI + breakdown
- [x] View_b: Division/Department/Section drill-down
- [x] View_d: Root cause (Muốn nghỉ vs Gắn bó)
- [x] View_f: Action priority matrix
- [x] View_e: Risk simulation + NLP

### Phase 2: Pillar-Level Anomaly Detection (Cần làm)
- [ ] Tích hợp anomaly rules per pillar vào `pillar_renderer.py`
- [ ] Thêm Tab 6: "Phát hiện Bất thường" cho mỗi trụ cột
- [ ] Deep dive logic per pillar per group
- [ ] Cross-pillar anomaly detection
- [ ] AI insight per anomaly type

### Phase 3: Automated Deep Dive (Cần làm)
- [ ] Khi phát hiện anomaly → tự động drill-down
- [ ] So sánh đơn vị bất thường vs trung bình
- [ ] Breakdown theo nhân khẩu học (thâm niên, thế hệ, vùng)
- [ ] Cross-reference HRIS data
- [ ] NLP analysis trên phản hồi mở per pillar

### Phase 4: AI-Powered Insights (Cần làm)
- [ ] AI insight cho mỗi anomaly detected
- [ ] AI so sánh cross-pillar
- [ ] AI đề xuất hành động cụ thể per group
- [ ] AI giải thích "tại sao vô lý" cho nghịch lý
- [ ] AI tạo executive summary per đơn vị

---

## 8. VÍ DỤ MINH HỌA: FLOW PHÁT HIỆN + DEEP DIVE

### Kịch bản: Phòng ban X có "Dự báo nghỉ việc cao nhưng không ai burnout"

```
STEP 1: DETECT
├── Chạy anomaly rules trên Phòng ban X
├── Phát hiện: % Muốn nghỉ = 25% (cao) nhưng Burnout = 8% (thấp)
├── Pattern matched: "Flight Risk without Burnout" (XP_NEW)
└── Trigger deep dive

STEP 2: DEEP DIVE
├── TC1 = 72% (bình thường) → Không phải mất niềm tin
├── TC2 = 68% (bình thường) → Quản lý OK
├── TC3 = 45% (THẤP) → Điều kiện làm việc kém
│   ├── Q18 (thiết bị) = 3.2 → công cụ kém
│   ├── Q19 (thăng tiến) = 2.8 → TRẦN THỦY TINH
│   └── Q20 (hướng dẫn) = 3.0 → thay đổi không giải thích
├── TC4 = 52% (THẤP) → Thu nhập không tương xứng
│   ├── Q21 (công bằng) = 3.1 → cảm thấy bất công
│   └── Q22 (minh bạch) = 3.4 → không hiểu cách tính
├── TC5 = 70% (bình thường) → Đồng nghiệp tốt, tự hào
└── Kết luận: Không burnout vì ĐỒNG NGHIỆP TỐT (TC5),
    nhưng muốn nghỉ vì THĂNG TIẾN MỜ NHẠT (TC3) + LƯƠNG THẤP (TC4)

STEP 3: AI INSIGHT
├── Input: Toàn bộ data từ Step 2
├── AI phân tích: "Phòng ban X đang trải qua 'Quiet Exodus' — nhân viên
│   không kiệt sức nhưng không thấy tương lai. Họ ở lại vì tình bạn (TC5=70%)
│   nhưng đang âm thầm tìm cơ hội khác vì thăng tiến mờ nhạt (Q19=2.8)
│   và thu nhập không tương xứng (Q21=3.1). Đây là dạng nghỉ việc
│   'có kế hoạch' — không bùng nổ như burnout mà âm thầm rút lui."
└── AI đề xuất: "Trong 30 ngày: (1) Tổ chức Career Conversation 1-1 cho
    nhóm thâm niên >12 tháng, (2) Công bố lộ trình thăng tiến rõ ràng
    với milestones cụ thể, (3) Rà soát benchmark lương so với thị trường."

STEP 4: ACTION
├── Hiển thị Action Priority Matrix cho Phòng ban X
├── Highlight: Q19 (thăng tiến) và Q21 (thu nhập) ở góc "Ưu tiên cao"
└── Đề xuất: Career Path Workshop + Salary Benchmark Review
```

---

## 9. TỔNG KẾT

### Số lượng analysis blocks: 5 trụ cột × 6 nhóm = 30 blocks

### Mỗi block cần:
1. **Anomaly rules** (4-5 rules per pillar) = ~25 rules
2. **Deep dive logic** (custom per group) = 30 functions
3. **AI insight prompts** (per anomaly type) = ~25 templates
4. **Cross-pillar patterns** = 8 patterns

### Tổng cộng:
- 25 pillar-level anomaly rules + 8 cross-pillar patterns = **33 rules**
- 30 deep dive functions (có thể reuse logic)
- 25+ AI prompt templates
- 6 group-specific analysis flows
