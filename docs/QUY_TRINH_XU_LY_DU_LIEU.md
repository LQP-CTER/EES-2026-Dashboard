# EES 2026 — Quy trình Xử lý Dữ liệu Khảo sát

> **Ngày cập nhật:** 29/05/2026 — Dựa trên dữ liệu thực tế từ 6 file khảo sát
> **Tổng mẫu raw toàn công ty:** 20,098 phản hồi / 21,340 headcount (**94.2% tỷ lệ phản hồi**)

---

## 1. Tổng quan 6 Nhóm Khảo sát

| Nhóm | Đối tượng | Platform | Headcount | Raw Form | Tỷ lệ PH | Giữ lại | Loại bỏ | % Giữ |
|------|-----------|----------|-----------|----------|----------|---------|---------|-------|
| **1A** | Shipper / NVPTTT | Quiz Platform | 13,867 | 12,955 | 93.4% | **10,359** | 2,596 | 80.0% |
| **1B** | Tài xế GXT/TXXT | Quiz Platform | 977 | 800 | 81.9% | **676** | 124 | 84.5% |
| **2A** | NV Kho & Vận hành | Google Form | 5,062 | 4,892 | 96.6% | **4,808** | 84 | 98.3% |
| **2B** | QL Tuyến đầu (Kho) | Google Form | 440 | 425 | 96.6% | **423** | 2 | 99.5% |
| **3A** | NV Văn phòng / HO | Google Form | 869 | 917 | 105.5% (1) | **913** | 4 | 99.6% |
| **3B** | QL & GĐ HO | Google Form | 125 | 109 | 87.2% | **108** | 1 | 99.1% |
| **TỔNG** | — | — | **21,340** | **20,098** | **94.2%** | **17,287** | 2,811 | **86.0%** |

(1) 3A vượt 100% do một số nhân viên thuộc hai bộ phận hoặc chuyển phòng trong kỳ khảo sát.

---

## 2. Cấu trúc Bộ câu hỏi

Tất cả 6 nhóm đều có **24 câu hỏi chính** theo cùng một sườn:

| Loại câu hỏi | Số lượng | Mô tả |
|--------------|----------|-------|
| Nhân khẩu học (Q1–Q8) | 8 câu | Năm sinh, giới tính, thâm niên, trình độ, v.v. |
| Likert 1–5 (Q9–Q29) | 21 câu | Đo lường 5 trụ cột + ý định ở lại |
| Câu hỏi mở (Q32–Q34) | 3 câu | Thích nhất / Điều giúp gắn bó / Cần cải thiện |
| eNPS (Q31) | 1 câu | Thang 0–10 |

**5 trụ cột đo lường (Engagement Index):**

| Mã | Tên | Câu hỏi | Trọng số |
|----|-----|---------|---------|
| TC1 | Niềm tin & Định hướng | Q9, Q10 | 15% |
| TC2 | Quản lý Trực tiếp | Q11–Q15 | 25% |
| TC3 | Môi trường & Công cụ | Q16–Q20 | 20% |
| TC4 | Đãi ngộ & Công bằng | Q21–Q25 | 20% |
| TC5 | Văn hóa & Sự Gắn kết | Q26–Q29 | 20% |

---

## 3. Sự khác biệt giữa hai Platform

### 3.1 Quiz Platform — Nhóm 1A, 1B

- **Cơ chế:** Nhân viên hoàn thành bài quiz nội bộ — dữ liệu giao về server GHN
- **Timestamp:** Là thời điểm giao bài (cửa sổ mở hàng chục giờ), **không phản ánh thời gian làm thực tế**
- **Câu mở:** Bắt buộc → không thể bỏ trống hợp lệ
- **Straight-line:** Khả năng cao xuất hiện do quiz có thể được hoàn thành nhanh bằng cách nhấn cùng một phím

### 3.2 Google Form — Nhóm 2A, 2B, 3A, 3B

- **Cơ chế:** Nhân viên điền Google Form qua link QR/URL
- **Email:** **Không thu thập** → không thể dedup theo email
- **Câu Likert:** **Bắt buộc** → mọi form gửi thành công đều có đầy đủ 21 câu Likert → `flag_too_missing` luôn = False
- **Câu mở:** Bắt buộc nhập (có validate) → tỷ lệ bỏ trống rất thấp
- **Hàm ý:** Tiêu chí "thiếu dữ liệu" không áp dụng được cho Google Form

---

## 4. Tiêu chí Loại bỏ (QC Filter)

### Nguyên tắc chung

> **Chỉ loại bỏ khi có đồng thời hai bằng chứng:** dữ liệu Likert không biến thiên (straight-line) **VÀ** không có ý kiến nào trong câu hỏi mở.

Một mình "đánh đồng đều" (straight-line) không đủ cơ sở để loại — nhân viên có thể thực sự hài lòng hoặc bất mãn toàn diện ở mọi khía cạnh, và điều này sẽ thể hiện qua câu mở.

### Rule áp dụng thống nhất cho TẤT CẢ 6 nhóm

```
Điều kiện loại bỏ = flag_straightline AND flag_empty_open
```

| Flag | Định nghĩa | Ngưỡng kỹ thuật |
|------|-----------|----------------|
| `flag_straightline` | Độ lệch chuẩn (std) của 21 câu Likert = 0 và có ít nhất 10 câu hợp lệ | `std == 0 & n_valid >= 10` |
| `flag_empty_open` | Tất cả 3 câu mở đều không có nội dung ý nghĩa | Bỏ trống / "không" / "k" / "na" / ký tự < 2 ký tự |
| **`flag_sl_and_empty`** | **Cả hai flag trên đều True** | **= flag_straightline AND flag_empty_open** |

### Các trường hợp xử lý cụ thể

| Trường hợp | Xử lý | Lý do |
|-----------|-------|-------|
| Straight-line **có** open-text ý nghĩa | **GIỮ** | Open-text là bằng chứng có phản hồi thực |
| Straight-line **không có** open-text | **LOẠI** | Không có bất kỳ bằng chứng về phản hồi thực |
| Không straight-line + có open-text | **GIỮ** | Phản hồi hoàn toàn bình thường |
| Không straight-line + không open-text | **GIỮ** | Likert biến thiên là bằng chứng đủ |

---

## 5. Kết quả Chi tiết Từng Nhóm

---

### Nhóm 1A — Shipper / NVPTTT

| Chỉ số | Giá trị |
|--------|---------|
| Platform | Quiz Platform (internal) |
| Headcount | 13,867 |
| Raw form | 12,955 |
| Tỷ lệ phản hồi | 93.4% |
| Câu Likert | 21 câu (Q9–Q29), không bắt buộc toàn bộ |
| Câu mở | 3 câu (Q32, Q33, Q34), không bắt buộc |

**Phân tích Straight-line:**

| Phân loại | Số lượng | % raw |
|-----------|---------|-------|
| Straight-line tổng | 7,110 | 54.9% |
| Thẳng hàng + **Không** có open-text → **LOẠI** | **2,596** | **20.0%** |
| Thẳng hàng + **Có** open-text → **GIỮ** | 4,514 | 34.8% |
| Không straight-line → GIỮ | 5,845 | 45.1% |

```
Raw: 12,955  →  Loại: 2,596  →  GIỮ LẠI: 10,359  (80.0%)
```

> **Ghi chú 1A:** Tỷ lệ straight-line cao (54.9%) phản ánh đặc thù Quiz Platform — nhân viên giao hàng có thể nhấn cùng ký tự để hoàn thành nhanh. Tuy nhiên **4,514 trong số này vẫn viết ý kiến mở** — đây là nhóm "im lặng nội tâm" cần phân tích NLP riêng.

---

### Nhóm 1B — Tài xế GXT/TXXT

| Chỉ số | Giá trị |
|--------|---------|
| Platform | Quiz Platform (internal) |
| Headcount | 977 |
| Raw form | 800 |
| Tỷ lệ phản hồi | 81.9% |

**Phân tích Straight-line:**

| Phân loại | Số lượng | % raw |
|-----------|---------|-------|
| Straight-line tổng | 276 | 34.5% |
| Thẳng hàng + **Không** có open-text → **LOẠI** | **124** | **15.5%** |
| Thẳng hàng + **Có** open-text → **GIỮ** | 152 | 19.0% |
| Không straight-line → GIỮ | 524 | 65.5% |

```
Raw: 800  →  Loại: 124  →  GIỮ LẠI: 676  (84.5%)
```

---

### Nhóm 2A — NV Kho & Vận hành

| Chỉ số | Giá trị |
|--------|---------|
| Platform | Google Form |
| Headcount | 5,062 |
| Raw form | 4,892 |
| Tỷ lệ phản hồi | 96.6% |
| Câu Likert | Bắt buộc — không thể missing |
| Câu mở | Bắt buộc nhập |

**Phân tích Straight-line:**

| Phân loại | Số lượng | % raw |
|-----------|---------|-------|
| Straight-line tổng | 1,878 | 38.4% |
| Thẳng hàng + **Không** có open-text → **LOẠI** | **84** | **1.7%** |
| Thẳng hàng + **Có** open-text → **GIỮ** | 1,794 | 36.7% |
| Không straight-line → GIỮ | 3,014 | 61.6% |

```
Raw: 4,892  →  Loại: 84  →  GIỮ LẠI: 4,808  (98.3%)
```

> **Ghi chú 2A:** 1,794 phản hồi straight-line nhưng **có viết ý kiến mở** — nhóm này phản ánh quan điểm qua open-text nhiều hơn là phân biệt điểm Likert. Nên phân tích NLP riêng để kiểm tra tính nhất quán.

---

### Nhóm 2B — Quản lý Tuyến đầu (Kho)

| Chỉ số | Giá trị |
|--------|---------|
| Platform | Google Form |
| Headcount | 440 |
| Raw form | 425 |
| Tỷ lệ phản hồi | 96.6% |

**Phân tích Straight-line:**

| Phân loại | Số lượng | % raw |
|-----------|---------|-------|
| Straight-line tổng | 104 | 24.5% |
| Thẳng hàng + **Không** có open-text → **LOẠI** | **2** | **0.5%** |
| Thẳng hàng + **Có** open-text → **GIỮ** | 102 | 24.0% |
| Không straight-line → GIỮ | 321 | 75.5% |

```
Raw: 425  →  Loại: 2  →  GIỮ LẠI: 423  (99.5%)
```

---

### Nhóm 3A — NV Văn phòng / HO

| Chỉ số | Giá trị |
|--------|---------|
| Platform | Google Form |
| Headcount | 869 |
| Raw form | 917 |
| Tỷ lệ phản hồi | 105.5% (1) |

**Phân tích Straight-line:**

| Phân loại | Số lượng | % raw |
|-----------|---------|-------|
| Straight-line tổng | 178 | 19.4% |
| Thẳng hàng + **Không** có open-text → **LOẠI** | **4** | **0.4%** |
| Thẳng hàng + **Có** open-text → **GIỮ** | 174 | 19.0% |
| Không straight-line → GIỮ | 739 | 80.6% |

```
Raw: 917  →  Loại: 4  →  GIỮ LẠI: 913  (99.6%)
```

(1) Vượt 100%: có thể do nhân viên chuyển bộ phận hoặc thay đổi headcount trong kỳ. Không downsampling — giữ nguyên 913 phản hồi hợp lệ.

---

### Nhóm 3B — Quản lý & Giám đốc HO

| Chỉ số | Giá trị |
|--------|---------|
| Platform | Google Form |
| Headcount | 125 |
| Raw form | 109 |
| Tỷ lệ phản hồi | 87.2% |

**Phân tích Straight-line:**

| Phân loại | Số lượng | % raw |
|-----------|---------|-------|
| Straight-line tổng | 11 | 10.1% |
| Thẳng hàng + **Không** có open-text → **LOẠI** | **1** | **0.9%** |
| Thẳng hàng + **Có** open-text → **GIỮ** | 10 | 9.2% |
| Không straight-line → GIỮ | 98 | 89.9% |

```
Raw: 109  →  Loại: 1  →  GIỮ LẠI: 108  (99.1%)
```

> **Lưu ý 3B:** n=108, Margin of Error ≈ ±9.4% (95% CI). Chỉ nên phân tích cấp tổ chức, không drill-down cấp phòng ban.

---

## 6. Tổng kết Toàn Công ty

### 6.1 Bảng tổng hợp theo Platform

| | Raw | Loại | Giữ lại | % Giữ |
|-|-----|------|---------|-------|
| Quiz Platform (1A + 1B) | 13,755 | 2,720 | 11,035 | **80.2%** |
| Google Form (2A + 2B + 3A + 3B) | 6,343 | 91 | 6,252 | **98.6%** |
| **TỔNG** | **20,098** | **2,811** | **17,287** | **86.0%** |

### 6.2 Lý do Loại bỏ

Toàn bộ **2,811 phản hồi bị loại** đều cùng một nguyên nhân:

```
Straight-line (std = 0 trên 21 câu Likert)  VÀ  Không có câu trả lời mở ý nghĩa
```

Không có phản hồi nào bị loại vì:
- Thiếu câu trả lời (missing) — do câu bắt buộc hoặc lọc từ platform
- Giá trị ngoài thang — do form có validate sẵn (1–5 Likert, 0–10 eNPS)
- Trùng lặp theo email — không thu thập email ở Google Form
- Thời gian hoàn thành quá nhanh — timestamp không phản ánh thời gian thực tế

### 6.3 Cơ sở Phân tích Chính thức (Analytic Base)

| Nhóm | Analytic Base | SL có open-text (GIỮ) | Không SL (GIỮ) |
|------|--------------|----------------------|----------------|
| 1A | 10,359 | 4,514 (43.6%) | 5,845 (56.4%) |
| 1B | 676 | 152 (22.5%) | 524 (77.5%) |
| 2A | 4,808 | 1,794 (37.3%) | 3,014 (62.7%) |
| 2B | 423 | 102 (24.1%) | 321 (75.9%) |
| 3A | 913 | 174 (19.1%) | 739 (80.9%) |
| 3B | 108 | 10 (9.3%) | 98 (90.7%) |
| **TỔNG** | **17,287** | **6,746 (39.0%)** | **10,541 (61.0%)** |

> **Hàm ý:** 39% mẫu final là "straight-line có ý kiến mở". Nhóm này có Likert biến thiên thấp, có thể kéo điểm trung bình về phía trung tâm. Cần phân tích NLP riêng cho nhóm này để khai thác giá trị từ open-text.

---

## 7. Luồng Xử lý Kỹ thuật

### Files xử lý chính

| File | Chức năng |
|------|----------|
| `utils/data_loader.py` | Pipeline xử lý chính: load, decode, QC, compute KPI |
| `shared/codebook.py` | Mapping câu hỏi, decode Likert/eNPS, tính Engagement Index |
| `shared/workforce_mapper.py` | Map survey → cơ cấu tổ chức (division / dept / section) |

### Luồng xử lý trong `load_group()`

```
1.  Load raw CSV (Supabase → fallback Google Sheets)
2.  Rename columns theo codebook (col_idx → Q9, Q10, ..., Q34)
3.  Decode Likert: A→1, B→2, C→3, D→4, E→5
4.  Decode eNPS: A→1 ... J→10
5.  Decode Q5 (thâm niên): A→"Dưới 1 tháng" ... I→"Trên 5 năm"
6.  Tính QC flags:
    ├─ flag_straightline    : std(Likert) == 0 & n_valid >= 10
    ├─ flag_too_missing     : missing > 80% (không áp dụng Google Form)
    ├─ flag_empty_open      : tất cả open-text vô nghĩa
    └─ flag_sl_and_empty    : flag_straightline AND flag_empty_open
7.  FILTER: Loại các hàng có flag_sl_and_empty == True
8.  Map org structure (division / department / section / region)
9.  Tính Pillar scores: TC1_pct ... TC5_pct (top-2-box %)
10. Tính Engagement Index (EI) = weighted average 5 pillars
11. Tính MEI, burnout_risk, stay_intention, eNPS_group
12. Preprocess open-text (NLP pipeline)
13. Return (df_clean, n_before)
```

### Pattern Straight-line theo Nhóm

| Nhóm | % SL tổng | Nhận xét |
|------|-----------|---------|
| 1A | 54.9% | Cao nhất — Quiz Platform, nhân viên giao hàng ít thời gian |
| 2A | 38.4% | Cao thứ 2 — nhóm đông nhất, áp lực ca làm |
| 1B | 34.5% | Tài xế — tương tự 1A nhưng nhóm nhỏ hơn |
| 2B | 24.5% | QL tuyến đầu — nhận thức cao hơn NV |
| 3A | 19.4% | NV VP — điều kiện điền form tốt hơn |
| 3B | 10.1% | Thấp nhất — QL & GĐ, cẩn thận nhất |

---

*Tài liệu tạo từ dữ liệu thực tế ngày 29/05/2026. Cập nhật khi thay đổi logic hoặc refresh dữ liệu.*
