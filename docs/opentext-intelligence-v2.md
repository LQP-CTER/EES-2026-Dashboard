# OPEN-TEXT INTELLIGENCE ENGINE — EES 2026
## Phân tích Câu hỏi Mở: Tiếng nói Thực sự của Nhân viên GHN
### Version 2.1 — Tháng 6/2026 | Chuẩn McKinsey/Qualtrics Text iQ

---

## TRIẾT LÝ NỀN TẢNG

> **"Câu hỏi đóng đo lường mức độ hài lòng. Câu hỏi mở tiết lộ sự thật tổ chức."**

Dữ liệu Likert cho bạn biết nhân viên cảm thấy *như thế nào*. Câu hỏi mở cho bạn biết *tại sao* — và tại sao đó mới là căn cứ để ra quyết định chiến lược.

Tại GHN EES 2026, 3 câu hỏi mở cuối (Q32/Q33/Q34) là **nguồn dữ liệu chẩn đoán tổ chức quan trọng nhất** — không phải vì số lượng (hơn 32.000 phản hồi), mà vì chất lượng tín hiệu ẩn bên trong. Mỗi câu trả lời — dù ngắn hay dài — đều mang một tín hiệu cần giải mã, không chỉ đếm.

**Nguyên tắc tuyệt đối:**
- Khi open-text **mâu thuẫn** với Likert score → ưu tiên open-text
- Silence (im lặng) **cũng là dữ liệu** — đôi khi quan trọng hơn những gì được viết
- Tần suất không phải tất cả — **cường độ cảm xúc** và **độ sâu hệ thống** mới quyết định mức độ nguy hiểm
- Đừng bao giờ phân tích câu hỏi mở một mình — luôn đặt trong tương quan với Burnout Index, Attrition Risk, và Pillar scores

---

## CẤU TRÚC 3 CÂU HỎI MỞ EES 2026

| Mã | Nội dung câu hỏi | Mục đích phân tích |
|---|---|---|
| **Q32** | "Điều gì ở GHN khiến bạn hài lòng / gắn bó nhất?" | **Retention anchor** — động lực ở lại, điểm mạnh cần bảo vệ |
| **Q33** | "Điều gì bạn tự hào / điều gì giúp bạn duy trì hiệu quả?" | **Engagement driver** — nguồn nội lực, mạng lưới hỗ trợ |
| **Q34** | "Bạn muốn GHN cải thiện điều gì để bạn gắn bó lâu hơn?" | **Pain point & Intent signal** — rào cản ở lại, rủi ro nghỉ việc |

**Lưu ý thiết kế:** Q34 là câu hỏi có giá trị chẩn đoán cao nhất vì nó gắn trực tiếp với **Intent to Stay**. Mọi nội dung Q34 đều cần được đọc qua lens "Nếu điều này không được giải quyết, người này sẽ nghỉ việc trong bao lâu?"

---

## PHASE 1 — DATA TRUST & SILENCE ANALYSIS

### 1.1 Silence Rate — Đọc Cái Không Được Viết

Trước khi phân tích bất kỳ nội dung nào, tính Silence Rate theo group:

```
Silence Rate (%) = (Số phản hồi trống hoặc vô nghĩa / Tổng số người tham gia) × 100
```

**Baseline thực tế EES 2026 để so sánh:**

| Group | Q32 Silence | Q33 Silence | Q34 Silence | Tín hiệu |
|---|---|---|---|---|
| 1A (Shipper) | ~28% | ~31% | ~30% | Vừa phải — nhiều người viết ngắn |
| 1B (Driver) | ~34% | ~42% | ~38% | Trung bình — nhóm nhỏ, cẩn thận về mẫu |
| 2A (Warehouse) | **88.9%** | **86.9%** | **80.7%** | 🔴 Khủng hoảng tâm lý tự kiểm duyệt |
| 2B (Frontline Mgr) | **93.9%** | **92.9%** | **85.2%** | 🔴 Bẫy quản lý — không thể nói thật |
| 3A (Office/HO) | **92.1%** | **89.2%** | **76.8%** | 🟡 Mệt mỏi khảo sát + sợ lộ danh tính |
| 3B (Senior Mgr) | **94.5%** | **75.2%** | **69.7%** | ⚠️ Nghịch lý: càng cao cấp càng im lặng |

**Phân tích tín hiệu từ im lặng:**

- **Silence Rate > 80% (2A/2B):** Đây không phải lười viết. Đây là **rút lui tâm lý có hệ thống** (Systemic Psychological Withdrawal). Nhân viên warehouse và frontline manager đã học rằng lên tiếng không mang lại kết quả — hoặc tệ hơn, có hại cho bản thân. Số người trả lời ít ỏi (10-20%) là phần nổi tảng băng chìm đại diện cho cả nhóm.

- **3B Silence Rate Q32 = 94.5% (cao nhất toàn công ty):** Cấp Director/Manager cấp cao nhất *không viết gì về điều họ hài lòng*. Đây là tín hiệu **chiến lược nguy hiểm**: người dẫn dắt tổ chức đang thiếu kết nối cảm xúc với nơi họ làm việc.

- **Khi Silence Rate cao + Likert Score trung bình/cao:** Đây là dấu hiệu **"Compliance through Fear"** — nhân viên chọn điểm an toàn trong trắc nghiệm nhưng không đủ tin tưởng để viết thêm. KHÔNG được báo cáo đây là "nhân viên hài lòng".

### 1.2 Noise Filtering — Lọc Phản Hồi Rác

Loại bỏ khỏi phân tích (đánh dấu riêng, KHÔNG xóa):

| Loại | Ví dụ thực tế | Tỷ lệ ước tính |
|---|---|---|
| Vô nghĩa / ngẫu nhiên | "ok", "tốt", "không", "hshshd", "123" | ~8–15% |
| Lặp lại mẫu giống hệt | 15 người cùng bưu cục viết "môi trường làm việc rất tốt quản lý gương mẫu" | Kiểm tra từng cụm |
| Xác nhận không nội dung | "không có ý kiến", "chưa nghĩ ra", "ko biết nữa" | ~15–25% |
| Câu quá ngắn không có thông tin | "thu nhập", "đồng nghiệp", "môi trường" (1-2 từ) | ~20–30% |

**Quy tắc tối thiểu:** Chỉ đưa vào phân tích sâu các phản hồi có **≥ 8 từ và mang thông tin có thể giải mã**.

### 1.3 Manipulation Detection — Phát Hiện Thao Túng

Quét pattern bất thường trong cùng bưu cục/phòng ban:
- Nếu **≥ 5 phản hồi** trong cùng đơn vị có text **cosine similarity > 0.85** → gắn flag **[COORDINATED_RESPONSE]**
- Báo cáo riêng lên HRBP Vùng để điều tra — không đưa vào phân tích đại diện
- Đây là dấu hiệu Quản lý tuyến đầu **ép hoặc mớm lời** để đạt KPI thi đua khảo sát

---

## PHASE 2 — TAXONOMY 9 CHỦ ĐỀ (thực tế EES 2026)

### Hệ thống Phân loại Chuẩn — Bắt Buộc Áp Dụng Nhất Quán

Mỗi phản hồi có thể nhận **nhiều label** (multi-label). Đây là hệ thống 9 chủ đề được xây dựng từ dữ liệu thực tế EES 2026 và GHN operational reality:

---

### CHỦ ĐỀ 1: Thu nhập Sinh tồn & Tính Minh bạch Đãi ngộ
**[LABEL: INCOME]**

**Scope:** Lương cơ bản, đơn giá, phúc lợi, thưởng, truy thu, phạt tiền, độ minh bạch của công thức thu nhập, COD giam ví, biến động thu nhập không đoán được.

**Keywords thực tế (Group 1A/1B/2A):**
> "thu nhập", "tăng lương", "đơn giá", "phúc lợi", "truy thu", "phạt oan", "giam COD", "tiền chuyến", "thu nhập đang giảm", "bị bom", "trừ tiền", "chốt phạt"

**Keywords thực tế (Group 3A/3B):**
> "thu nhập cạnh tranh", "chính sách đãi ngộ rõ ràng", "tăng thu nhập hàng năm", "cơ chế thu nhập phúc lợi", "đại ngộ ổn"

**Cường độ cảm xúc:**
- **Low:** "Mong tăng thêm thu nhập" — góp ý xây dựng
- **Medium:** "Thu nhập đơn hàng công ty đang giảm mà không rõ lý do" — hoang mang, mất định hướng
- **High/Critical:** "Phạt oan ức vô lý, kêu cứu thì HR đùn đẩy, làm việc như nô lệ" — phẫn nộ hệ thống, nguy cơ nghỉ việc ngay

**Tín hiệu nguy hiểm đặc thù GHN:**
- Đề cập "trả thu nhập 2 lần/tháng" = thanh khoản gia đình bị áp lực
- "App giật lag không giao được đơn" trong ngữ cảnh thu nhập = thu nhập bị tước đoạt gián tiếp bởi hạ tầng
- "Phạt 100% thu nhập 1 kỳ" (từ Group 2B) = vi phạm Luật Lao động — [URGENT_ESCALATION]

---

### CHỦ ĐỀ 2: Khối lượng Công việc & Kiệt sức Vận hành
**[LABEL: BURNOUT]**

**Scope:** Giờ làm thực tế, ca kíp, áp lực KPI/sản lượng, không có ngày nghỉ phục hồi, ép OT, peak season burnout, tốc độ băng tải vượt ngưỡng con người.

**Keywords thực tế:**
> "nghỉ chủ nhật", "giảm giờ làm", "làm việc nhiều quá", "không có ngày nghỉ", "365 ngày", "ép ca", "ca thứ 8", "đuối theo line", "giảm tải", "cân bằng", "chưa có ngày nghỉ lễ"

**Tín hiệu gián tiếp — KHÔNG được bỏ qua:**
> "vì miếng cơm manh áo" — cụm này KHÔNG phải than vãn về lương. Đây là tín hiệu **kiệt sức hiện sinh** (existential burnout): nhân viên đang làm việc trong trạng thái tồn tại, không phải phát triển. Mức độ nghỉ việc tiếp theo: cao.
>
> "bình thường, vì đồng thu nhập em quên mọi thứ, cố gắng bỏ qua" — đây là **Learned Helplessness** giai đoạn 3. Người này đã tắt hệ thống cảnh báo nội tâm. Rủi ro nghỉ việc đột ngột không báo trước.

**Burnout phân tầng (áp dụng cho Group 2A/2B):**
- **Stage 1-2 (Stress tích lũy):** "Áp lực nhưng vẫn chịu được" — giám sát
- **Stage 3-4 (Kiệt sức thực sự):** "Mệt mỏi, không còn hứng khởi" — can thiệp sớm
- **Stage 5-6 (Sụp đổ/Rút lui):** "Làm đối phó", "nghỉ để khỏe" — nguy cơ nghỉ việc ngay

---

### CHỦ ĐỀ 3: Công cụ, Hạ tầng & Hệ thống Vận hành
**[LABEL: TOOLS]**

**Scope:** App Driver, App PDA, hệ thống chấm công, phần mềm quản lý, thiết bị hư hỏng, hạ tầng kho bãi, wifi/mạng, xe chở hàng.

**Keywords thực tế:**
> "app giật lag", "ứng dụng bắn đơn", "PDA bắn hàng", "app lỗi", "cập nhật đơn chậm", "hệ thống", "tối ưu công nghệ", "giảm thao tác thủ công", "tăng tự động hóa", "công cụ quản lý realtime"

**Chuỗi nhân quả bắt buộc phân tích (KHÔNG chỉ đếm mentions):**

```
App lỗi/giật lag
    ↓
Đơn không cập nhật được / bị coi là chậm giao
    ↓
Hệ thống tự động trừ tiền / phạt shipper
    ↓
Thu nhập giảm oan + mất niềm tin vào tính công bằng
    ↓
Attrition Risk tăng + Distrust hệ thống
```

Khi phát hiện pattern này trong data: không báo cáo là "nhân viên không hài lòng về app". Báo cáo là **"Lỗi hạ tầng đang chuyển hóa thành rủi ro mất nhân sự thông qua cơ chế phạt tự động bất công"**.

**Cho Group 3B/3A:**
- "Cần công cụ quản trị chuyên biệt theo đặc thù phòng ban" = productivity gap do thiếu tooling
- "Dữ liệu realtime để theo dõi" = nhu cầu visibility trong ra quyết định
- "Ứng dụng AI" = kỳ vọng transformational, không chỉ operational

---

### CHỦ ĐỀ 4: Thái độ & Năng lực Quản lý
**[LABEL: MANAGER]**

**Scope:** Thái độ quản lý trực tiếp, hành vi lãnh đạo, hỗ trợ vs. áp đặt, thiên vị, bạo lực ngôn ngữ, quản trị bằng sợ hãi.

**Keywords thực tế:**
> "quản lý nhiệt tình", "cấp trên hỗ trợ", "quản lý hòa đồng", "quản lý tôi luôn là tấm gương", "cần lắng nghe hơn", "QLtt xin hãy lắng nghe ý kiến", "quy chụp đánh giá mang tính cá nhân", "đùn đẩy", "thiên vị"

**Đặc biệt quan trọng — Cross-Group Perception Gap:**
Khi phân tích Manager theme, LUÔN đặt 2A và 2B cạnh nhau:

| 2A (Nhân viên warehouse) nói | 2B (Quản lý tuyến đầu) nói |
|---|---|
| "Quản lý áp đặt chỉ tiêu, không lắng nghe" | "Nhân viên vô kỷ luật, bỏ ca, ý thức kém" |
| "Bị chửi bới khi không đạt KPI" | "Không còn cách nào khác vì HO ép KPI quá cao" |

**Phân tích hệ thống bắt buộc:** Đây không phải conflict cá nhân. Đây là **Pressure Absorber Syndrome**: HO tạo ra áp lực KPI sản lượng cao → 2B không có công cụ hay quyền hạn để đạt → 2B dùng áp lực hành vi với 2A → 2A phản kháng thụ động (bùng ca) → 2B bị đánh giá kém → vòng lặp độc hại.

**Gắn cờ [URGENT_ESCALATION] khi phát hiện:**
- Ngôn ngữ bạo lực, xúc phạm nhân phẩm từ quản lý
- Ép buộc điền khảo sát (coordinated response + manager context)
- Đe dọa trả đũa khi nhân viên phản ánh

---

### CHỦ ĐỀ 5: Đồng nghiệp, Đoàn kết & Văn hóa Làm việc
**[LABEL: CULTURE]**

**Scope:** Mối quan hệ với đồng nghiệp, tinh thần đoàn kết, văn hóa tổ chức, bầu không khí làm việc, sự hòa đồng, hỗ trợ lẫn nhau.

**Keywords thực tế:**
> "đồng nghiệp hòa đồng", "anh em đoàn kết", "hỗ trợ lẫn nhau", "văn hóa cởi mở", "môi trường trẻ trung năng động", "thoải mái", "thân thiện", "gắn bó", "tập thể"

**Giá trị phân tích đặc biệt:**
- **Ở Group 1A/2A:** Đồng nghiệp thường là **Retention Anchor chủ lực** khi thu nhập thấp và điều kiện làm việc khó khăn. Mất đoàn kết nhóm = mất lý do duy nhất còn ở lại.
- **Ở Group 3B:** Văn hóa cởi mở + trao quyền = driver gắn kết hàng đầu. Nhưng "cởi mở" cần phân biệt với "lý tưởng hóa" — đối chiếu với Likert TC1 score.

**Tín hiệu âm tính ẩn:**
> "vui vẻ hòa đồng" khi Burnout Index > 3.5 = **"Proud but Exhausted"** — nhân viên dùng tinh thần tập thể để che lấp kiệt sức cá nhân. Đây là nhóm rủi ro nghỉ việc cao nhất vì họ sẽ ra đi đột ngột, không báo trước.

---

### CHỦ ĐỀ 6: Phát triển Nghề nghiệp & Lộ trình Thăng tiến
**[LABEL: CAREER]**

**Scope:** Cơ hội thăng tiến, lộ trình rõ ràng, đào tạo, mentoring, phát triển năng lực, học hỏi từ công việc.

**Keywords thực tế:**
> "lộ trình thăng tiến rõ ràng", "cơ hội thể hiện bản thân", "đào tạo", "mentoring coaching", "phát triển năng lực", "học hỏi", "năng lực lãnh đạo", "framework đào tạo", "cơ hội thăng tiến thật", "chuẩn hóa năng lực"

**Phân tích theo group:**

| Group | Kỳ vọng Career | Rủi ro nếu không đáp ứng |
|---|---|---|
| 1A/1B | Ổn định, thu nhập đủ sống, ít đòi hỏi career path | Thấp — nhưng khi có offer tốt hơn ở SPX/Grab: rời ngay |
| 2A | Thăng cấp, học nhiều vị trí | Trung bình — 3A/3B mới là đích đến mong muốn |
| 2B | Lộ trình từ AM → OM → BC trưởng rõ ràng | **Cao** — không thấy đường tiến = nghỉ trong 6 tháng |
| 3A | Career ceiling frustration là vấn đề số 1 | **Rất cao** — nhiều nhất trong cohort attrition risk |
| 3B | Trao quyền thật, strategic impact | **Cao** — nếu không được làm gì có nghĩa, talent cấp cao rời đi |

**Insight đặc biệt từ data 3B:**
> "1 cơ hội thăng tiến thật, 2 quyền vận hành thật, 3 khả năng kiếm thu nhập cao nếu build được team mạnh"
Đây là **Career Value Proposition hoàn chỉnh** của cấp quản lý — GHN cần đảm bảo cả 3. Nếu chỉ có 1/3 → attrition risk trong 12 tháng.

---

### CHỦ ĐỀ 7: Quy trình, Phối hợp Liên Phòng ban & Hiệu quả Vận hành
**[LABEL: PROCESS]**

**Scope:** Quy trình nội bộ, phối hợp liên bộ phận, SLA nội bộ, chồng chéo công việc, thủ tục hành chính, tốc độ phản hồi, đùn đẩy trách nhiệm.

**Keywords thực tế:**
> "quy trình liên phòng ban", "phối hợp hỗ trợ nhiệt tình hơn", "chồng chéo công việc", "lơ tin nhắn", "đơn giản hóa quy trình", "rõ trách nhiệm", "xử lý chồng chéo", "internal SLA", "quy trình chuẩn hóa"

**Đây là chủ đề chính của Group 3A/3B (Office/HO):**
Các phản hồi về Process không phải nêu "muốn làm ít hơn" — mà là **muốn làm việc có hiệu quả hơn**. Đây là tín hiệu **High Engagement + Operational Frustration**: những người cẩn thận nhất, muốn đóng góp nhất mới bực bội vì quy trình kém.

**Chuỗi nhân quả:**
```
Quy trình liên phòng ban không rõ ràng
    ↓
Chờ đợi, đùn đẩy, lặp lại công việc
    ↓
"Thuế vận hành ẩn" (Operational Tax) — mất 20-30% năng suất thực tế
    ↓
Burnout nhóm 3A mà không ai gọi là burnout (vì không phải physical)
    ↓
Attrition risk trong 6-9 tháng, đặc biệt các nhân tài không chịu được inefficiency
```

---

### CHỦ ĐỀ 8: Môi trường Vật lý & Điều kiện Làm việc
**[LABEL: ENVIRONMENT]**

**Scope:** Cơ sở vật chất kho/bưu cục, an toàn lao động, thiết bị bảo hộ, nhiệt độ, vệ sinh, không gian làm việc văn phòng, suất ăn.

**Keywords thực tế:**
> "thêm quạt mát", "dựng xe còn lộn xộn", "cơ sở vật chất", "an toàn", "suất ăn nhân viên", "chỗ ăn ở khi chạy xa", "áo đồng phục cũ rồi", "mặt bằng", "ổn định chỗ ngồi"

**Đặc điểm nhóm:**
- 1A/1B: Điều kiện thực địa (nhiệt độ, thiết bị, đồng phục) — ảnh hưởng trực tiếp đến dignity và sức khỏe
- 2A: Điều kiện kho (băng tải, nhiệt độ, an toàn lao động) — liên quan đến physical burnout
- 3A/3B: Suất ăn, không gian làm việc, linh hoạt thứ 7 — work-life balance signal

**Dignity Marker:** Đề cập đến đồng phục, thiết bị cá nhân — dù nhỏ — là tín hiệu **nhân viên cảm thấy bị xem là công cụ, không phải con người**. Đặc biệt quan trọng với 1A vì dignity là top-3 retention driver cho gig/semi-gig workforce.

---

### CHỦ ĐỀ 9: Niềm tin Tổ chức, Giao tiếp & Ý định Gắn bó
**[LABEL: TRUST]**

**Scope:** Niềm tin vào lãnh đạo cấp cao, giao tiếp chính sách, minh bạch định hướng, cam kết follow-up sau khảo sát, ý định nghỉ việc, learned helplessness.

**Keywords thực tế:**
> "minh bạch", "định hướng rõ ràng", "tầm nhìn", "lắng nghe", "có tiếng nói", "trao quyền", "chia sẻ tầm nhìn GHN", "thay đổi chính sách đột ngột", "ổn định công việc", "gắn bó lâu dài", "bỏ qua", "cố gắng bỏ qua"

**Đây là chủ đề quan trọng nhất để đo lường Organizational Health:**

| Signal | Nghĩa thực | Action |
|---|---|---|
| "Có tiếng nói" (Group 3B) | Psychological Safety thấp ở cấp senior | Structural problem, không phải cá nhân |
| "Chia sẻ tầm nhìn GHN" | Nhân viên cấp cao thiếu strategic alignment | BOD phải communicate trực tiếp, không qua tầng trung gian |
| "cố gắng bỏ qua" (Group 2A) | Learned helplessness — đã từ bỏ kỳ vọng thay đổi | Attrition risk cao, exit sẽ đột ngột |
| "không có ý kiến" lặp lại nhiều lần | Survey cynicism — không tin khảo sát có giá trị | Gốc rễ: các khảo sát trước không được follow-up |
| Không viết gì (silence 3B) | Disengagement ở tầng lãnh đạo | Tín hiệu nguy hiểm nhất toàn công ty |

**Post-Survey Credibility:** Nếu EES 2025 không có visible follow-up action → EES 2026 silence rate tăng là hoàn toàn hợp lý. Phần lớn "không có ý kiến" là **"tôi đã ý kiến rồi mà không ai nghe"** — không phải thiếu ý kiến.

---

## PHASE 2.5 — PRIORITY WEIGHT MATRIX THEO GROUP

### Tại sao cần trọng số?

9 chủ đề không nặng bằng nhau trong mọi group. Nếu báo cáo tất cả 9 theme ngang hàng, BOD sẽ bị overwhelm và không biết ưu tiên gì. Ma trận dưới đây — derive từ KDA expected drivers trong master analytics — xác định theme nào cần phân tích sâu nhất và xuất hiện đầu tiên trong báo cáo.

### Priority Weight Matrix

| Theme | 1A Shipper | 1B Driver | 2A Warehouse | 2B Frontline Mgr | 3A Office | 3B Senior Mgr |
|---|---|---|---|---|---|---|
| **INCOME** | ⭐⭐⭐⭐⭐ 35% | ⭐⭐⭐⭐⭐ 35% | ⭐⭐⭐⭐⭐ 30% | ⭐⭐⭐ 15% | ⭐⭐ 10% | ⭐⭐ 10% |
| **BURNOUT** | ⭐⭐⭐ 20% | ⭐⭐⭐ 20% | ⭐⭐⭐⭐ 25% | ⭐⭐⭐⭐ 20% | ⭐⭐⭐ 15% | ⭐⭐ 10% |
| **TOOLS** | ⭐⭐⭐ 15% | ⭐⭐ 10% | ⭐⭐⭐ 20% | ⭐⭐⭐ 15% | ⭐⭐ 10% | ⭐⭐ 10% |
| **MANAGER** | ⭐⭐⭐⭐ 25% | ⭐⭐⭐ 15% | ⭐⭐⭐ 15% | ⭐⭐ 10% | ⭐⭐⭐ 15% | ⭐⭐ 10% |
| **CULTURE** | ⭐ 5% | ⭐⭐ 10% | ⭐ 5% | ⭐⭐ 10% | ⭐⭐ 10% | ⭐ 5% |
| **CAREER** | — | — | ⭐ 5% | ⭐⭐⭐⭐ 20% | ⭐⭐⭐⭐⭐ 35% | ⭐⭐⭐⭐ 25% |
| **PROCESS** | — | ⭐ 5% | — | ⭐⭐ 10% | ⭐⭐⭐ 15% | ⭐⭐⭐⭐ 25% |
| **ENVIRONMENT** | — | ⭐ 5% | — | — | ⭐ 5% | — |
| **TRUST** | — | — | — | — | ⭐⭐ 10% | ⭐⭐⭐⭐ 25% |

**Cách đọc:** Theme có trọng số cao nhất của group = phân tích đầu tiên + sâu nhất + quote nhiều nhất + business impact được quantify.

**Luật ưu tiên báo cáo:**
- Top 3 themes theo trọng số = chiếm 70% nội dung phân tích của mỗi group
- Theme trọng số < 5% = đề cập nếu có signal bất thường, không phân tích sâu
- Nếu một theme có trọng số thấp nhưng xuất hiện [URGENT_ESCALATION] → override priority, phân tích ngay

**Lưu ý:** Trọng số trên là baseline từ nghiên cứu VN logistics. Nếu actual KDA trên data thực cho kết quả khác → **dùng KDA thực tế, không dùng baseline này.**

---

## PHASE 3 — ASPECT-BASED SENTIMENT ANALYSIS (ABSA)

### Quy tắc Vàng: Không Label Tổng, Chỉ Label Khía Cạnh

**Sai:**
> Phản hồi: *"Bưu cục trưởng nhiệt tình hỗ trợ, nhưng app cứ lỗi làm mất đơn, thu nhập bị trừ oan"*
> ❌ Label: Negative (tổng thể)

**Đúng:**
> - [MANAGER] → Positive (bưu cục trưởng nhiệt tình)
> - [TOOLS] → Negative (app lỗi mất đơn)
> - [INCOME] → High Negative/Critical (trừ thu nhập oan)

### Ngưỡng Kích hoạt ABSA — Không Áp dụng Toàn bộ

ABSA tốn thời gian. Với 32,000+ phản hồi, áp dụng cho tất cả là không thực tế. Chỉ chạy ABSA cho phản hồi đáp ứng ít nhất 1 trong các điều kiện:

1. **Độ dài** ≥ 50 từ (phản hồi có đủ context để bóc tách aspect)
2. **contradiction_flag = True** trong data đã processed (Likert và behavior đã mâu thuẫn)
3. **EWS_flag = True** (Early Warning Signal đã được đánh dấu)
4. **Intensity = 3 hoặc 4** (Frustration/Crisis — đã pass qua noise filter)
5. Thuộc group có **Burnout Index > 3.0** và response có ≥ 2 chủ đề khác nhau trong cùng câu

Với phần còn lại: gán single-label theo theme dominant (không bóc tách). Đánh dấu `[SINGLE_LABEL]` để phân biệt.

### Thang đo Cường độ Cảm xúc (4 cấp)

| Cấp | Label | Dấu hiệu | Hành động |
|---|---|---|---|
| 1 | **Constructive** | Góp ý cụ thể, mang tính xây dựng, không cảm xúc tiêu cực | Ghi nhận, tổng hợp vào improvement backlog |
| 2 | **Discontent** | Chán nản, mệt mỏi, phiền toái lặp lại nhưng chưa phản kháng | Monitor, kiểm tra trong 30 ngày |
| 3 | **Frustration** | Phẫn nộ rõ ràng, cảm giác bị đối xử bất công, đang tích lũy | HRBP review trong 7 ngày |
| 4 | **Crisis/Toxic** | Tổn thương lòng tự trọng, đe dọa vận hành, ngôn ngữ cực đoan | **[URGENT_ESCALATION]** trong 24-48h |

---

## PHASE 4 — CROSS-VALIDATION: OPEN-TEXT vs. LIKERT

### Contradiction Matrix — Phát hiện Sự thật Bị che giấu

Chạy bắt buộc cho mỗi segment phân tích:

| Likert Score | Open-Text Signal | Diagnosis | Độ ưu tiên |
|---|---|---|---|
| TC4 ≥ 3.5 | Nhiều đề cập INCOME/Frustration | **"Satisfied on paper, struggling in reality"** — Score bị inflate bởi social desirability | 🔴 Cao |
| TC2 ≥ 4.0 | Nhiều đề cập MANAGER/Frustration | **"Fear-based positive score"** — Nhân viên cho điểm cao vì sợ | 🔴 Cao |
| TC5 ≥ 4.0 | BURNOUT signals cao + "cố gắng bỏ qua" | **"Proud but Exhausted"** — Sắp nghỉ mà không ai biết | 🔴 Cao |
| Q22 ≥ 4.0 | TRUST/Cynicism + "không có ý kiến" | **"Stating intention, hiding reality"** — Intent to Stay là surface answer | 🟡 Trung bình |
| Burnout Index < 2.0 | WORKLOAD signals mạnh trong text | **Burnout bị normalize** — Họ không nhận ra mình đang kiệt sức | 🟡 Trung bình |

### Khi Open-Text Mâu thuẫn với Likert → Ưu tiên Open-text

**Lý do:** Likert là public commitment. Open-text là private truth. Người Việt, đặc biệt frontline, sẽ chọn điểm "an toàn" trong trắc nghiệm nhưng viết thật hơn trong tự luận (dù vẫn không hoàn toàn thật).

---

## PHASE 4.5 — VIETNAMESE TEXT NORMALIZATION (Frontline-specific)

### Tại sao cần bước này?

Hơn 60% phản hồi từ 1A/2A viết không dấu, viết tắt, hoặc sai chính tả. Nếu skip bước này, keyword matching sẽ miss 30–40% tín hiệu từ đúng nhóm quan trọng nhất. Không có normalization = phân tích INCOME/BURNOUT bị undercount nghiêm trọng.

### Bảng Normalization Thực tế EES 2026

**Không dấu → Có dấu (các cụm từ quan trọng nhất):**

| Viết thực tế trong data | Chuẩn hóa về | Theme |
|---|---|---|
| `thu nhap`, `thu nhâpj`, `luong`, `luơng` | thu nhập, lương | INCOME |
| `dong nghiep`, `anh em` | đồng nghiệp | CULTURE |
| `quan ly`, `ql`, `qltt` | quản lý, quản lý trực tiếp | MANAGER |
| `phuc loi`, `phuc_loi` | phúc lợi | INCOME |
| `nghi viec`, `bo viec` | nghỉ việc | TRUST/ATTRITION |
| `tang luong`, `tang thu nhap` | tăng lương/thu nhập | INCOME |
| `lam them`, `lam them gio` | làm thêm giờ, OT | BURNOUT |
| `ung dung`, `app`, `pda` | ứng dụng, app, thiết bị | TOOLS |
| `ki luat`, `ky luat` | kỷ luật | MANAGER |
| `lo trinh`, `thang tien` | lộ trình thăng tiến | CAREER |
| `phoi hop`, `lien phong ban` | phối hợp, liên phòng ban | PROCESS |
| `minh bach`, `ro rang` | minh bạch, rõ ràng | TRUST |

**Viết tắt phổ biến:**

| Viết tắt | Nghĩa đầy đủ |
|---|---|
| `nv`, `nvxl`, `nvpttt` | nhân viên, nhân viên xử lý, nhân viên phát tuyến trực tiếp |
| `ql`, `qltt`, `bctp`, `bc` | quản lý, quản lý trực tiếp, bưu cục trưởng phó, bưu cục |
| `kt`, `kpi`, `otc`, `sla` | kiểm tra, KPI, OTC, SLA |
| `ko`, `k`, `kh` | không, không, khách hàng |
| `đc`, `dc` | được |
| `vs` | với |
| `mk`, `mik` | mình |

**Typo tolerance — không reject, map về gốc:**

| Typo thực tế | Map về |
|---|---|
| `hoà đồng vui vẽ`, `vui ve` | hòa đồng vui vẻ |
| `thân thiên` | thân thiện |
| `da co gắn hơn nữa` | đã cố gắng hơn nữa |
| `thu nhâpj` | thu nhập |
| `rế quản lý` | dễ quản lý |

### Nguyên tắc Xử lý:

1. **Normalize trước khi label** — không label raw text
2. **Không xóa phản hồi vì lỗi chính tả** — chỉ loại bỏ nếu sau normalize vẫn không có thông tin
3. **Giữ nguyên văn gốc** bên cạnh version đã normalize — để quote verbatim trong báo cáo vẫn dùng bản gốc (authentic voice)
4. **Flag `[NORMALIZED]`** cho các phản hồi đã qua xử lý để traceability

---

## PHASE 5 — FRONTLINE SLANG DICTIONARY (GHN-specific)

| Slang thực địa | Khái niệm HR/Vận hành | Tầng thực tế ẩn |
|---|---|---|
| **Bị bom / Boom đơn** | Return Rate / Compensation Risk | Công sức + nhiên liệu mất trắng, không có thu nhập bù đắp — nguồn gốc ức chế đãi ngộ sâu nhất |
| **Ôm súp / Súp hành** | Supervisor Favoritism | Tuyến đường ngon bị phân cho người thân quen, người mới/ngoài nhóm nhận tuyến khó — bất công cơ cấu |
| **Bắn app / Bắn đơn** | Algorithmic Dispatch Perception | Khi nói "app không bắn đơn" = không tin vào sự công bằng của thuật toán |
| **Chạy line / Line hàng** | Sorting Physical Pressure | Tốc độ băng tải vượt ngưỡng con người — burnout vật lý thực sự |
| **Bùng ca / Cúp ca** | Absenteeism / Passive Strike | Không phải lười biếng — là phản kháng thụ động hoặc kiệt sức cảm xúc cực hạn |
| **Giam COD / Giam ví** | Liquidity Retaliation | Khóa ký quỹ = cắt đứt dòng tiền sinh tồn của gia đình → trigger nghỉ việc tức thì |
| **Chốt phạt / Harawork log** | Algorithmic Penalty | Phạt tự động → khi shipper nói "phạt oan" = phản kháng lại sự bất công trong đối soát tự động |
| **Đuối theo line** | Physical Burnout Signal | Vượt ngưỡng thể chất — cần giảm tốc độ hoặc tăng nhân sự |
| **Sắp xếp ca thứ 8** | Excess OT / No Recovery | Ca thứ 8 trong tuần = không có ngày phục hồi — vi phạm tiêu chuẩn lao động |

---

## PHASE 6 — ICEBERG ESTIMATION MODEL

### Nguyên tắc Tảng Băng Chìm

Số lượng người viết phản hồi tiêu cực chỉ là phần nổi. Phần chìm lớn hơn rất nhiều do:
1. **Fear of Retaliation** — đặc biệt tại các bưu cục có quản lý kiểm soát chặt
2. **Survey Fatigue** — không tin vào giá trị của việc viết
3. **Normalization** — đã quen với điều kiện xấu, không còn thấy cần phàn nàn

**Công thức ước tính:**

```
Số người thực sự bị ảnh hưởng ≈ Số người viết tiêu cực × (1 / (1 - Silence Rate))
```

Ví dụ Group 2A: 300 người viết về INCOME/Critical + Silence Rate 80.7%
→ Ước tính thực tế: 300 / (1 - 0.807) ≈ **1,554 người** thực sự có vấn đề thu nhập nghiêm trọng

**Luôn kèm confidence range:** "Ước tính 1,400–1,700 người (80% CI) đang gặp vấn đề tương tự, trong khi chỉ 300 người lên tiếng."

### ⚠️ Điều kiện Áp dụng Iceberg Model — Bắt buộc Kiểm tra Trước

Iceberg estimation **chỉ defensible** khi có ít nhất 2 trong 3 điều kiện sau. Nếu không đủ điều kiện → ghi chú "Insufficient corroborating evidence" và báo cáo số liệu thô.

| Điều kiện | Ngưỡng | Lý do |
|---|---|---|
| Burnout Index của group | > 3.0 | Xác nhận nhóm đang chịu stress thực sự, không phải silence do "không có gì để nói" |
| Attrition Risk Score | > 60% high-risk | Silence gắn với sợ trả đũa, không phải thỏa mãn |
| Contradiction Flag Rate | > 15% trong group | Likert vs behavior gap — xác nhận self-censorship |

**Lý do cần điều kiện này:** Người im lặng không đồng nhất — ước tính 30–50% im lặng vì thực sự không có vấn đề đặc biệt. Áp dụng iceberg không có điều kiện sẽ phóng đại con số, mất credibility trước CFO/BOD khi bị cross-check.

**Khi đủ điều kiện, luôn trình bày theo format:**
> "Trong số N người viết phản hồi tiêu cực về [theme], ước tính **X–Y người** (khoảng tin cậy 80%) trong group có trải nghiệm tương tự nhưng không lên tiếng. Ước tính này có giá trị vì Burnout Index group = [Z] và Attrition Risk = [W%]."

---

## PHASE 7 — ROOT-CAUSE HYPOTHESIS FRAMEWORK

### Dialectical Analysis — Phân tích Biện chứng 3 lớp

Mỗi insight từ open-text phải được trình bày theo cấu trúc:

```
[Bằng chứng thực địa — verbatim quote]
    ↓
[Cơ chế vận hành/hệ thống tạo ra vấn đề — Layer 2]
    ↓
[Trải nghiệm con người bị tổn thương — Layer 3]
    ↓
[Hậu quả kinh doanh đo lường được — ROI/Cost]
```

**Ví dụ chuẩn:**
> *"Thu nhập đơn hàng đang giảm mà không rõ lý do"* (Group 1A, nhiều phản hồi tương tự)
>
> ↓ **Cơ chế:** Công thức đơn giá GHN thay đổi theo mùa/chính sách nhưng không được communicate rõ ràng xuống tuyến đầu. Shipper không biết tại sao thu nhập giảm → không thể lập kế hoạch tài chính.
>
> ↓ **Trải nghiệm:** Mất kiểm soát tài chính cá nhân = nguồn căng thẳng lớn nhất trong mô hình tâm lý frontline (Income Unpredictability > Income Level).
>
> ↓ **Hậu quả:** Dự báo tăng 15–20% attrition trong nhóm này trong quý tiếp theo nếu không có can thiệp giao tiếp chính sách. Chi phí thay thế 1 shipper = ~8–12 triệu VND (recruitment + training + ramp-up).

---

## PHASE 8 — OUTPUT STANDARDS CHO BÁO CÁO OPEN-TEXT

### Cấu trúc Báo cáo Phân tích Open-Text chuẩn

**A. Executive Summary (1 trang)**
- 3 phát hiện quan trọng nhất (không phải top 3 phổ biến nhất — mà top 3 nguy hiểm nhất)
- 1 contradiction pattern bắt buộc
- 1 signal nguy hiểm tiềm ẩn không lộ ra trong Likert data

**B. Silence Analysis (trước thematic analysis)**
- Bảng Silence Rate theo group và theo câu hỏi
- Diễn giải: im lặng này nói lên điều gì?
- So sánh với EES 2025 nếu có

**C. Thematic Distribution (cho mỗi group)**
- Bảng phân phối 9 chủ đề (% trong số phản hồi hữu ích)
- Heatmap Q32/Q33/Q34 × 9 themes
- Tín hiệu khác biệt giữa các câu hỏi trong cùng group

**D. Deep-Dive Per Theme**
Mỗi chủ đề quan trọng: Tần suất + Cường độ + Chuỗi nhân quả + Verbatim quote + Business impact

**E. Cross-Group Contradiction Analysis**
- Ít nhất 2 contradiction patterns giữa Likert và open-text
- Perception gap giữa 2A và 2B

**F. Urgent Signals**
- Mọi phản hồi được gắn [URGENT_ESCALATION] hoặc [COORDINATED_RESPONSE]
- Bưu cục/phòng ban cụ thể cần HRBP can thiệp ngay

**G. Action Triggers**
Mỗi theme quan trọng → 1 action cụ thể với: owner + timeline + success metric

### Nghiêm Cấm trong Báo cáo Open-Text

❌ "Nhân viên phàn nàn về thu nhập" (không có cơ chế, không có data)
❌ Liệt kê quote rời rạc như minh chứng — quote phải trong chuỗi phân tích
❌ "Một số nhân viên cho rằng..." khi không có số liệu
❌ Kết luận từ % khi N < 20
❌ Bỏ qua silence để chỉ phân tích những người lên tiếng
❌ Dừng ở Layer 1 (chính sách) mà không đào Layer 2 (vận hành) và Layer 3 (con người)

---

## PHASE 9 — CLOSED-LOOP ACTION SOP

### Từ Open-Text đến Can thiệp Thực địa

**4 bước bắt buộc cho mọi signal Critical/URGENT_ESCALATION:**

**Bước 1 — Triage (trong 24h):**
HRBP Vùng nhận alert với: location, group, quote nguyên văn, intensity label, business risk ước tính

**Bước 2 — Root-Cause Investigation (trong 7 ngày):**
- Phỏng vấn độc lập cả quản lý và nhân viên tại điểm nóng
- Xác định "Perception Gap" — ai đang đúng về thực tế vận hành?
- Không phán xét, chỉ thu thập bằng chứng

**Bước 3 — Targeted Intervention (theo severity):**
- Quick fix: thay thiết bị hỏng, điều chỉnh KPI tạm thời, giao tiếp lại chính sách
- Structural fix: luân chuyển quản lý độc hại, sửa quy trình phạt, tăng SLA nội bộ
- Strategic fix: redesign compensation formula, rebuild career path

**Bước 4 — Pulse Validation (30 ngày sau):**
3 câu hỏi: (1) Vấn đề đã được giải quyết chưa? (2) Hành động của GHN có thay đổi gì? (3) Bạn có sẵn sàng giới thiệu GHN cho người khác không?
Ca chỉ đóng khi **Perceived Resolution Rate ≥ 70%** từ pulse survey (xem định nghĩa dưới).

**Tại sao không dùng eNPS để đo kết quả?** eNPS bị ảnh hưởng bởi hàng chục yếu tố ngoài intervention — thưởng Tết, tin tức ngành, thay đổi nhân sự. Sau 30 ngày, eNPS tăng không có nghĩa intervention hiệu quả; eNPS không tăng không có nghĩa intervention thất bại. Đây là metric quá noisy cho mục đích đo point-in-time intervention.

**Thay bằng Pulse 3-câu có mục tiêu:**
1. *"Vấn đề [X cụ thể] mà bạn đã phản hồi — bạn thấy đã được giải quyết chưa?"* (1–5)
2. *"Kể từ khảo sát, bạn có thấy thay đổi cụ thể nào trong công việc hàng ngày không?"* (Có / Không + mô tả)
3. *"Mức độ tin tưởng của bạn vào việc GHN sẽ tiếp tục cải thiện đã thay đổi như thế nào?"* (Tăng / Không đổi / Giảm)

**Perceived Resolution Rate** = % người trả lời câu 1 ≥ 3/5.
**Ca đóng khi:** PRR ≥ 70% VÀ câu 3 "Tăng" ≥ 50%. Nếu không đạt → quay lại Bước 2.

---

## SELF-REVIEW CHECKLIST TRƯỚC KHI OUTPUT

Chạy checklist này. Nếu bất kỳ item nào "No" → rework:

**Data Quality:**
- [ ] Silence Rate đã được tính và diễn giải trước khi phân tích nội dung?
- [ ] Noise đã được filter — chỉ phân tích phản hồi ≥ 8 từ có thông tin?
- [ ] Coordinated response đã được kiểm tra và flag?

**Analytical Depth:**
- [ ] Mọi quote đều nằm trong chuỗi [Quote → Mechanism → Business Impact]?
- [ ] Ít nhất 1 contradiction giữa Likert và open-text được chỉ ra?
- [ ] Tín hiệu gián tiếp (e.g., "vì miếng cơm manh áo") đã được giải mã?
- [ ] Cross-group perception gap (2A vs 2B) đã được phân tích?
- [ ] Iceberg estimation đã áp dụng cho các vấn đề Critical?

**Frontline Intelligence:**
- [ ] Slang thực địa đã được giải mã đúng ngữ cảnh?
- [ ] Survival psychology được áp dụng khi đọc phản hồi 1A/2A (positive score ≠ positive experience)?
- [ ] Dignity signals (đồng phục, thiết bị) không bị bỏ qua?

**Business Relevance:**
- [ ] Mọi finding có gắn với chi phí attrition hoặc SLA impact cụ thể?
- [ ] Action items có owner + timeline + success metric?
- [ ] URGENT_ESCALATION signals đã được tách riêng để gửi HRBP ngay?
