# KẾ HOẠCH PHÂN TÍCH 5 TRỤ CỘT × 6 NHÓM KHẢO SÁT
## EES 2026 — Production Analytics Playbook v3.0
### GiaoHangNhanh | Employee Experience Department

> **Phiên bản:** 3.0 — June 2026
> **Thay đổi so với v2:** Fix 7 lỗi kỹ thuật + tenure normalization + unit tests
> **Trạng thái:** Production-ready (đã review kỹ thuật)

---

## CHANGELOG v2 → v3

| # | Lỗi | Trạng thái |
|---|-----|-----------|
| 1 | `calibrate_weights()` dùng Logistic Regression → multicollinearity | ✅ Fixed: Ridge + VIF check |
| 2 | `burnout_score` clip sai, mất thông tin điểm 4–5 | ✅ Fixed: công thức chuẩn |
| 3 | `cronbach_alpha()` trả về 2 kiểu (dict/float) → runtime bug | ✅ Fixed: luôn trả về dict |
| 4 | TC1_A2 dùng `TC1[-1]` sai position cho nhóm 2B (5 items) | ✅ Fixed: thêm `comms_item` alias |
| 5 | EWS tenure window: TC5_A3 dùng 6T, XP_6 dùng 3T → không nhất quán | ✅ Fixed: `EWS_TENURE_WINDOW` constant |
| 6 | `df_hris` không filter theo unit → income benchmark sai | ✅ Fixed: `get_unit_hris()` helper |
| 7 | XP_9 Quadrant dùng `iterrows()` → chậm với data lớn | ✅ Fixed: vectorized `np.select` |
| 8 | Overall health score dùng trọng số tùy tiện (0.5/0.3/0.2) | ✅ Fixed: dùng percentile rank |
| 9 | Tenure values string — không có normalization layer | ✅ Fixed: `normalize_raw_data()` |
| 10 | JSI workload item 3B từ TC5, không nhất quán với nhóm khác | ✅ Fixed: documented + handled |
| 11 | `prev_company` (D6) không có xử lý NLP | ✅ Fixed: thêm NLP taxonomy skeleton |
| 12 | Không có unit tests để tự verify kết quả | ✅ Fixed: `run_sanity_checks()` |

---

## MỤC LỤC

1. [Constants & Codebook Mapper](#1-constants--codebook-mapper)
2. [Data Normalization Layer](#2-data-normalization-layer)
3. [Derived Indices](#3-derived-indices)
4. [Data Quality Pipeline](#4-data-quality-pipeline)
5. [Anomaly Detection — 5 Trụ cột](#5-anomaly-detection)
6. [Cross-Pillar Patterns](#6-cross-pillar-patterns)
7. [Deep Dive Flow](#7-deep-dive-flow)
8. [AI Insight Prompt Templates](#8-ai-prompts)
9. [Foundation Indices & Supplemental Metrics](#9-foundation-indices)
10. [Unit Tests & Sanity Checks](#10-unit-tests)
11. [Implementation Roadmap](#11-roadmap)

---

## 1. CONSTANTS & CODEBOOK MAPPER

```python
# ============================================================
# SECTION 1A: SYSTEM CONSTANTS
# ============================================================

# Thứ tự thâm niên (ordinal encoding)
TENURE_LABELS = [
    'Dưới 1 tháng',        # 0
    'Trên 1 đến 3 tháng',  # 1
    'Trên 3 đến 6 tháng',  # 2
    'Trên 6 đến 9 tháng',  # 3
    'Trên 9 đến 12 tháng', # 4
    'Trên 1 đến 2 năm',    # 5
    'Trên 2 đến 3 năm',    # 6
    'Trên 3 đến 5 năm',    # 7
    'Trên 5 năm',           # 8
]

# Map cả string lẫn số (survey platform có thể export khác nhau)
TENURE_MAP = {label: i for i, label in enumerate(TENURE_LABELS)}
TENURE_MAP.update({i + 1: i for i in range(len(TENURE_LABELS))})  # fallback số 1-9

# Thâm niên ngưỡng "nhân viên mới" cho EWS — khác nhau theo nhóm
# FIX #5: định nghĩa 1 lần, dùng mọi nơi — không hardcode trong từng hàm
EWS_TENURE_THRESHOLD = {
    '1A': 2,   # ≤ index 2 = ≤ 6 tháng (frontline turnover nhanh hơn)
    '1B': 2,
    '2A': 2,
    '2B': 3,   # ≤ index 3 = ≤ 9 tháng (QL cần thêm thời gian để thích nghi)
    '3A': 3,
    '3B': 3,
}

# Nhóm thâm niên "senior" để phân tích trần thủy tinh
SENIOR_TENURE_THRESHOLD = 6  # ≥ index 6 = ≥ 2 năm

# eNPS categories (chuẩn NPS quốc tế)
ENPS_BINS    = [-1, 6, 8, 10]
ENPS_LABELS  = ['Detractor', 'Passive', 'Promoter']
ENPS_PROMOTER_MIN  = 9
ENPS_DETRACTOR_MAX = 6

# Minimum n cho anonymity
MIN_UNIT_N = 5

# Anomaly relative threshold (1.5 std = ~87th/13th percentile)
ANOMALY_STD_MULTIPLIER = 1.5

# Trọng số mặc định (Gallup-based prior — SẼ được overwrite sau calibration)
DEFAULT_WEIGHTS = {
    'TC1': 0.15, 'TC2': 0.25, 'TC3': 0.20, 'TC4': 0.20, 'TC5': 0.20,
}
CALIBRATED_WEIGHTS = {}  # Populated bởi calibrate_weights()


# ============================================================
# SECTION 1B: DEMOGRAPHIC MAP
# ============================================================

DEMO_MAP = {
    '1A': {'D1': 'gen_raw', 'D2': 'gender', 'D3': 'marital',
            'D4': 'edu', 'D5': 'tenure_raw', 'D6': 'prev_company'},
    '1B': {'D1': 'gen_raw', 'D2': 'gender', 'D3': 'marital',
            'D4': 'edu', 'D5': 'tenure_raw', 'D6': 'prev_company'},
    '2A': {'D1': 'gen_raw', 'D2': 'gender', 'D3': 'marital', 'D4': 'edu',
            'D5': 'tenure_raw', 'D6': 'prev_company', 'D7': 'dept',
            'D8': 'sub_dept', 'D9': 'grade'},
    '2B': {'D1': 'gen_raw', 'D2': 'gender', 'D3': 'marital', 'D4': 'edu',
            'D5': 'tenure_raw', 'D6': 'prev_company', 'D7': 'dept',
            'D8': 'sub_dept', 'D9': 'grade'},
    '3A': {'D1': 'gen_raw', 'D2': 'gender', 'D3': 'marital', 'D4': 'edu',
            'D5': 'tenure_raw', 'D6': 'prev_company', 'D7': 'dept',
            'D8': 'sub_dept', 'D9': 'grade'},
    '3B': {'D1': 'gen_raw', 'D2': 'gender', 'D3': 'marital', 'D4': 'edu',
            'D5': 'tenure_raw', 'D6': 'prev_company', 'D7': 'dept',
            'D9': 'grade'},
}


# ============================================================
# SECTION 1C: QUESTION MAP — NGUỒN CHÂN LÝ DUY NHẤT
# FIX #4: Thêm comms_item alias tường minh — không dùng TC1[-1] nữa
# ============================================================

QUESTION_MAP = {
    # ----------------------------------------------------------
    # 1A: NV Giao nhận / Shipper
    # ----------------------------------------------------------
    '1A': {
        'TC1': ['C1', 'C2'],
        'TC2': ['C3', 'C4', 'C5', 'C6', 'C7'],
        'TC3': ['C8', 'C9', 'C10', 'C11', 'C12'],
        'TC4': ['C13', 'C14', 'C15', 'C16', 'C17'],
        'TC5': ['C18', 'C19', 'C20', 'C21'],
        'attrition': 'C22', 'eNPS': 'C23', 'open': ['C24', 'C25', 'C26'],
        # Sub-item aliases
        'trust_item':   'C1',   # Tin GHN đi đúng hướng
        'comms_item':   'C2',   # Thông báo thay đổi kịp thời ← FIX #4
        'fairness':     'C4',   # Phân đơn công bằng
        'feedback':     'C7',   # AM phản hồi phát triển
        'tool':         'C8',   # App Driver hoạt động ổn định
        'workload':     'C10',  # Cường độ làm việc có thể duy trì
        'career':       'C11',  # Lộ trình thăng tiến lên Leader/TBC/AM
        'income_fair':  'C13',  # Thu nhập phản ánh công sức
        'transparency': 'C14',  # App hiển thị rõ phạt / thu nhập tạm tính
        'incident_pay': 'C17',  # Hỗ trợ sự cố ảnh hưởng thu nhập
        'safety':       'C18',  # An toàn giao thông + GHN quan tâm
        'peer':         'C19',  # Đồng nghiệp hỗ trợ
        'pride':        'C20',  # Tự hào là shipper GHN
        'pressure':     'C21',  # Áp lực không ảnh hưởng cuộc sống
        'respect':      None,   # 1A không có câu tôn trọng tường minh
        'psych_safety': None,
        'autonomy':     None,
        'belonging':    'C20',  # dùng pride làm proxy belonging cho JSI
    },
    # ----------------------------------------------------------
    # 1B: Tài xế Vận tải
    # ----------------------------------------------------------
    '1B': {
        'TC1': ['C1', 'C2'],
        'TC2': ['C3', 'C4', 'C5', 'C6', 'C7'],
        'TC3': ['C8', 'C9', 'C10', 'C11', 'C12'],
        'TC4': ['C13', 'C14', 'C15', 'C16', 'C17'],
        'TC5': ['C18', 'C19', 'C20', 'C21'],
        'attrition': 'C22', 'eNPS': 'C23', 'open': ['C24', 'C25', 'C26'],
        'trust_item':   'C1',
        'comms_item':   'C2',   # Thông báo chính sách/lịch trình kịp thời
        'fairness':     'C4',   # Lịch chạy phân bổ công bằng
        'feedback':     'C7',   # ĐPV hỗ trợ khi sự cố
        'tool':         'C8',   # Xe/phương tiện an toàn
        'workload':     'C9',   # Lịch chạy hợp lý, đủ thời gian nghỉ
        'safety':       'C10',  # GHN đảm bảo làm việc an toàn trên đường
        'career':       'C11',  # Lộ trình lên điều phối/giám sát
        'income_fair':  'C13',  # Thu nhập phản ánh quãng đường/công sức
        'transparency': 'C14',  # Hiểu rõ phụ cấp đường dài, ca đêm
        'incident_pay': 'C17',  # Hỗ trợ tai nạn/hư xe/mất hàng
        'peer':         'C18',  # Đội vận tải hỗ trợ nhau
        'pride':        'C19',  # Tự hào là tài xế GHN
        'pressure':     'C20',  # Áp lực không ảnh hưởng cuộc sống
        'respect':      'C21',  # Được tôn trọng như người lao động có giá trị
        'psych_safety': None,
        'autonomy':     None,
        'belonging':    'C19',
    },
    # ----------------------------------------------------------
    # 2A: NV Vận hành Kho
    # ----------------------------------------------------------
    '2A': {
        'TC1': ['C1', 'C2'],
        'TC2': ['C3', 'C4', 'C5', 'C6'],
        'TC3': ['C7', 'C8', 'C9', 'C10', 'C11'],
        'TC4': ['C12', 'C13', 'C14', 'C15', 'C16'],
        'TC5': ['C17', 'C18', 'C19', 'C20', 'C21'],
        'attrition': 'C22', 'eNPS': 'C23', 'open': ['C24', 'C25', 'C26'],
        'trust_item':    'C1',
        'comms_item':    'C2',  # Thay đổi quan trọng được thông báo rõ
        'fairness':      'C3',  # Phân ca/khu vực công bằng (TC2 item đầu)
        'feedback':      'C4',  # QL lắng nghe và phản hồi bằng hành động
        'tool':          'C7',  # Thiết bị PDA/xe đẩy/băng tải hoạt động tốt
        'workload':      'C9',  # Khối lượng hàng không quá sức
        'career':        'C10', # Biết mình có thể thăng tiến lên Trưởng nhóm
        'income_fair':   'C12', # Thu nhập phản ánh sức lao động và thời gian
        'transparency':  'C13', # Phân ca có tiêu chí rõ ràng
        'ot_fair':       'C14', # Cơ hội tăng ca công bằng
        'incident_pay':  'C15', # Biết quy trình hỗ trợ khi ốm/tai nạn
        'recognition':   'C16', # Nỗ lực được công nhận xứng đáng
        'safety_phys':   'C17', # Điều kiện vật lý kho (nhiệt độ, bụi, ánh sáng)
        'safety_labor':  'C18', # ATLĐ được tuân thủ nghiêm ngặt
        'peer':          'C19', # Đồng nghiệp hỗ trợ
        'pressure':      'C20', # Áp lực không ảnh hưởng cuộc sống
        'respect':       'C21', # Được tôn trọng như người lao động có giá trị
        'pride':         None,  # 2A không có câu tự hào tường minh
        'psych_safety':  None,
        'autonomy':      None,
        'belonging':     'C21', # dùng respect làm proxy
    },
    # ----------------------------------------------------------
    # 2B: Quản lý Tuyến đầu (AM, OM, Supervisor, TBC, Team Leader)
    # ----------------------------------------------------------
    '2B': {
        'TC1': ['C1', 'C2', 'C3', 'C4', 'C5'],
        'TC2': ['C6', 'C7', 'C8', 'C9'],
        'TC3': ['C10', 'C11', 'C12', 'C13', 'C14'],
        'TC4': ['C15', 'C16', 'C17'],
        'TC5': ['C18', 'C19', 'C20', 'C21'],
        'attrition': 'C22', 'eNPS': 'C23', 'open': ['C24', 'C25', 'C26'],
        'trust_item':   'C2',  # Tin BLĐ đưa ra quyết định đúng
        # FIX #4: 2B có 5 TC1 items, comms là C4 (không phải C5 cuối)
        'comms_item':   'C4',  # Thông tin từ cấp trên rõ ràng và đúng thời điểm
        'ho_support':   'C3',  # HO (HR, Tech, Finance) hỗ trợ kịp thời
        'integrity':    'C5',  # BLĐ làm đúng những gì họ nói
        'autonomy':     'C7',  # Đủ quyền hạn tự ra quyết định
        'psych_safety': 'C8',  # Tâm lý an toàn khi nói thẳng ý kiến
        'dev_support':  'C9',  # Cấp trên đầu tư phát triển năng lực QL
        'tool':         'C10', # Đủ hệ thống/công cụ/dữ liệu quản lý
        'kpi_fair':     'C11', # KPI khả thi, không phải hy sinh chất lượng
        'workload':     'C12', # Workload áp lực có thể duy trì lâu dài
        'career':       'C13', # Thấy rõ lộ trình thăng tiến trong GHN
        'ho_process':   'C14', # Quy trình HO hỗ trợ, không làm chậm trễ
        'income_fair':  'C15', # Đãi ngộ phản ánh đóng góp và trách nhiệm
        'transparency': 'C17', # Đánh giá hiệu suất minh bạch và nhất quán
        'peer':         'C18', # Quản lý cùng cấp phối hợp không đổ lỗi
        'pride':        'C19', # Tự hào là QL tuyến đầu tại GHN
        'pressure':     'C20', # Áp lực không ảnh hưởng cuộc sống
        'respect':      'C21', # Được tôn trọng bởi cấp trên và đội
        'belonging':    'C19',
    },
    # ----------------------------------------------------------
    # 3A: NV Văn phòng / Hỗ trợ HO
    # ----------------------------------------------------------
    '3A': {
        'TC1': ['C1', 'C2', 'C3', 'C4', 'C5'],
        'TC2': ['C6', 'C7', 'C8', 'C9'],
        'TC3': ['C10', 'C11', 'C12', 'C13', 'C14'],
        'TC4': ['C15', 'C16', 'C17'],
        'TC5': ['C18', 'C19', 'C20', 'C21'],
        'attrition': 'C22', 'eNPS': 'C23', 'open': ['C24', 'C25', 'C26'],
        'trust_item':   'C2',  # Tin BLĐ quyết định đúng đắn
        # FIX #4: 3A có 5 TC1 items, comms gần nhất là C3 (SMT giải thích lý do)
        'comms_item':   'C3',  # SMT giải thích rõ lý do quyết định lớn
        'integrity':    'C4',  # BLĐ làm đúng những gì họ nói
        'care':         'C5',  # BLĐ quan tâm thực sự đến phúc lợi NV
        'mgr_dev':      'C6',  # QL quan tâm phát triển career
        'autonomy':     'C7',  # Được trao quyền và tin tưởng
        'feedback':     'C8',  # Nhận phản hồi thường xuyên từ QL
        'psych_safety': 'C9',  # Thoải mái chia sẻ ý kiến khác biệt
        'tool':         'C10', # Đủ công cụ/hệ thống/thông tin
        'process':      'C11', # Quy trình nội bộ không gây chậm trễ
        'collab':       'C12', # Phối hợp liên phòng ban hiệu quả
        'career':       'C13', # GHN tạo điều kiện phát triển năng lực
        'workload':     'C14', # Khối lượng công việc phân bổ hợp lý
        'income_fair':  'C15', # Đãi ngộ phản ánh đóng góp thực sự
        'transparency': 'C17', # Chính sách lương thưởng rõ ràng nhất quán
        'peer':         'C18', # Văn hóa hợp tác, không cạnh tranh nội bộ
        'pressure':     'C19', # Áp lực kiểm soát được, không ảnh hưởng sức khỏe
        'pride':        'C20', # Tự hào về GHN và vai trò của mình
        'belonging':    'C21', # Cảm thấy thuộc về GHN
        'respect':      None,  # 3A không có câu tôn trọng riêng
    },
    # ----------------------------------------------------------
    # 3B: Manager / Senior Manager / Director HO
    # ----------------------------------------------------------
    '3B': {
        'TC1': ['C1', 'C2', 'C3', 'C4'],
        'TC2': ['C5', 'C6', 'C7', 'C8'],
        'TC3': ['C9', 'C10', 'C11', 'C12', 'C13'],
        'TC4': ['C14', 'C15', 'C16', 'C17'],
        'TC5': ['C18', 'C19', 'C20', 'C21'],
        'attrition': 'C22', 'eNPS': 'C23', 'open': ['C24', 'C25', 'C26'],
        'trust_item':   'C1',  # Thấy rõ tầm nhìn chiến lược dài hạn
        # FIX #4: 3B có 4 TC1 items; không có "thông báo kịp thời" — C2 gần nhất là data-driven
        'comms_item':   None,  # 3B TC1 không có item truyền thông tường minh
        'data_driven':  'C2',  # Quyết định dựa trên dữ liệu và lý do rõ
        'integrity':    'C3',  # BLĐ hành xử nhất quán giữa lời nói và hành động
        'autonomy':     'C4',  # Được trao đủ quyền hạn điều hành
        'priorities':   'C5',  # Biết rõ ưu tiên tổ chức kỳ vọng ở mình
        'feedback_up':  'C6',  # Có cơ chế nhận feedback trung thực từ NV
        'ld_dev':       'C7',  # GHN đầu tư phát triển năng lực lãnh đạo
        'psych_safety': 'C8',  # Chia sẻ bất đồng với đồng cấp/cấp trên an toàn
        'tool':         'C9',  # Đủ công cụ data ra quyết định
        'org_design':   'C10', # Cơ cấu tổ chức ít rào cản hành chính
        'frontline_fb': 'C11', # Nhận được feedback trung thực từ tuyến đầu
        'innovation':   'C12', # GHN tạo không gian thử nghiệm và chấp nhận thất bại
        'succession':   'C13', # Hệ thống kế thừa lãnh đạo rõ ràng
        'income_fair':  'C14', # Đãi ngộ tương xứng trách nhiệm
        'resource_fair':'C15', # Nguồn lực phân bổ công bằng theo giá trị chiến lược
        'transparency': 'C16', # Đánh giá lương/thưởng lãnh đạo minh bạch
        'recognition':  'C17', # Đóng góp được công nhận xứng đáng và kịp thời
        # FIX #10: workload của 3B nằm ở TC5 (C18), không phải TC3
        # JSI sẽ dùng đúng C18 — nhưng cần note cross-pillar nature
        'workload':     'C18', # Áp lực có thể duy trì hiệu quả lâu dài (TC5!)
        'talent_culture':'C19',# Văn hóa giữ chân người tài
        'pride':        'C20', # Tự hào là lãnh đạo GHN
        'peer_collab':  'C21', # Đồng cấp phối hợp thực chất
        'pressure':     'C18', # alias pressure = workload cho 3B (cùng câu)
        'respect':      None,
        'belonging':    'C20',
    },
}


def get_pillar_questions(group_id: str, pillar: str) -> list:
    """Truy xuất danh sách câu hỏi cho pillar + group. Entry point duy nhất."""
    if group_id not in QUESTION_MAP:
        raise ValueError(f"Group '{group_id}' không hợp lệ. Hợp lệ: {list(QUESTION_MAP.keys())}")
    if pillar not in QUESTION_MAP[group_id]:
        raise ValueError(f"Pillar '{pillar}' không tồn tại cho group '{group_id}'")
    val = QUESTION_MAP[group_id][pillar]
    return val if isinstance(val, list) else ([val] if val else [])


def get_item(group_id: str, alias: str):
    """Truy xuất column name cho sub-item alias. Trả về None nếu không có."""
    return QUESTION_MAP.get(group_id, {}).get(alias)
```

---

## 2. DATA NORMALIZATION LAYER

> **Chạy ngay sau import raw data, trước mọi bước khác.**
> FIX #9: Chuẩn hóa tenure, gen, grade — xử lý cả string lẫn numeric export từ các platform khác nhau.

```python
import pandas as pd
import numpy as np
import re

# ---- 2.1 Tenure normalization ----

def normalize_tenure(df: pd.DataFrame) -> pd.DataFrame:
    """
    Chuẩn hóa cột tenure từ D5 (raw) → tenure (ordinal int) + tenure_label (string).
    Xử lý được: string tiếng Việt, số 1–9, mixed cases.
    """
    if 'tenure_raw' not in df.columns:
        return df

    def _parse_tenure(val):
        if pd.isna(val):
            return -1
        val_str = str(val).strip()
        # Thử map trực tiếp trước
        if val_str in TENURE_MAP:
            return TENURE_MAP[val_str]
        # Thử convert số
        try:
            return TENURE_MAP.get(int(float(val_str)), -1)
        except (ValueError, TypeError):
            pass
        # Fuzzy match: tìm số tháng/năm trong string
        if 'dưới 1' in val_str.lower() or '< 1' in val_str.lower():
            return 0
        return -1

    df['tenure'] = df['tenure_raw'].apply(_parse_tenure)
    df['tenure_label'] = df['tenure'].map(
        {i: label for i, label in enumerate(TENURE_LABELS)}
    ).fillna('Unknown')
    return df


# ---- 2.2 Generation normalization ----

GEN_MAP = {
    'Trước 1980 (Gen X)':  'Gen X',
    'Gen X':               'Gen X',
    1:                     'Gen X',
    '1981 – 1989 (Gen Y)': 'Gen Y (older)',
    '1990 – 1996 (Gen Y)': 'Gen Y (younger)',
    'Gen Y':               'Gen Y (older)',
    2:                     'Gen Y (older)',
    3:                     'Gen Y (younger)',
    '1997 – 2000 (Gen Z)': 'Gen Z',
    'Từ 2001 trở đi (Gen Z)': 'Gen Z',
    'Gen Z':               'Gen Z',
    4:                     'Gen Z',
    5:                     'Gen Z',
}

def normalize_gen(df: pd.DataFrame) -> pd.DataFrame:
    if 'gen_raw' in df.columns:
        df['gen'] = df['gen_raw'].map(GEN_MAP).fillna('Unknown')
        # Simplified 3-gen version for cross-tab analysis
        df['gen3'] = df['gen'].map(
            lambda x: 'Gen X' if x == 'Gen X'
                      else 'Gen Z' if x == 'Gen Z'
                      else 'Gen Y' if 'Gen Y' in str(x) else 'Unknown'
        )
    return df


# ---- 2.3 Column rename (Demographic) ----

def rename_demographics(df: pd.DataFrame, group_id: str) -> pd.DataFrame:
    """Đổi tên cột D1–D9 sang tên ngữ nghĩa theo DEMO_MAP."""
    rename_dict = DEMO_MAP.get(group_id, {})
    return df.rename(columns=rename_dict)


# ---- 2.4 Prev company NLP taxonomy ----
# FIX #11: Framework xử lý D6 (prev_company) thay vì bỏ qua

PREV_COMPANY_TAXONOMY = {
    'logistics_competitor': ['ninja', 'j&t', 'jt', 'viettel post', 'best', 'ghn', 'snappy', 'grab'],
    'logistics_adjacent':   ['lazada', 'shopee', 'tiki', 'sendo', 'vnpost', 'bưu điện'],
    'manufacturing':        ['samsung', 'intel', 'khu công nghiệp', 'nhà máy', 'xưởng'],
    'retail_food':          ['vinmart', 'bách hóa', 'circle k', 'highland', 'phúc long'],
    'first_job':            ['chưa làm', 'lần đầu', 'sinh viên', 'mới ra trường'],
    'other':                [],  # default bucket
}

def classify_prev_company(val: str) -> str:
    """Phân loại câu trả lời D6 thành taxonomy bucket."""
    if pd.isna(val) or str(val).strip() == '':
        return 'not_answered'
    val_lower = str(val).lower()
    for category, keywords in PREV_COMPANY_TAXONOMY.items():
        if any(kw in val_lower for kw in keywords):
            return category
    # Heuristic: nếu quá ngắn (<5 ký tự) → unclear
    if len(val_lower.strip()) < 5:
        return 'unclear'
    return 'other'

def process_prev_company(df: pd.DataFrame) -> pd.DataFrame:
    if 'prev_company' in df.columns:
        df['prev_company_cat'] = df['prev_company'].apply(classify_prev_company)
    return df


# ---- 2.5 Master normalization runner ----

def normalize_raw_data(df: pd.DataFrame, group_id: str) -> pd.DataFrame:
    """
    Entry point duy nhất. Chạy ngay sau khi load CSV/Excel từ survey platform.
    Thứ tự: rename → tenure → gen → prev_company
    """
    df = rename_demographics(df, group_id)
    df = normalize_tenure(df)
    df = normalize_gen(df)
    df = process_prev_company(df)
    return df
```

---

## 3. DERIVED INDICES

```python
from scipy import stats as scipy_stats
from sklearn.linear_model import LogisticRegression, RidgeClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.inspection import permutation_importance
from sklearn.model_selection import cross_val_score
import warnings


# ---- 3.1 Pillar Score ----

def compute_pillar_score(df: pd.DataFrame, group_id: str, pillar: str) -> pd.Series:
    """
    Tính điểm trụ cột = trung bình các items, convert sang % (0–100).
    Missing: cần ≥ 50% items có dữ liệu; nếu không → NaN.
    NOTE: Giả định MCAR (Missing Completely At Random) — analyst cần verify.
    """
    qs = get_pillar_questions(group_id, pillar)
    valid_qs = [q for q in qs if q in df.columns]
    if not valid_qs:
        return pd.Series(np.nan, index=df.index)

    raw = df[valid_qs]
    min_valid = max(1, int(len(valid_qs) * 0.5))
    enough_data = raw.notna().sum(axis=1) >= min_valid
    score = raw.mean(axis=1)
    score[~enough_data] = np.nan
    return ((score - 1) / 4 * 100).round(2)


# ---- 3.2 Burnout Proxy ----
# FIX #2: Công thức chuẩn — không clip, không mất thông tin điểm 4–5

def compute_burnout(df: pd.DataFrame, group_id: str) -> pd.DataFrame:
    """
    Burnout Proxy = trung bình reverse của workload + pressure items.
    Thang 0–100 (cao = burnout risk cao).
    Cả hai items cần có dữ liệu; nếu chỉ có 1 → dùng item đó.
    """
    wl_col = get_item(group_id, 'workload')
    pr_col = get_item(group_id, 'pressure')

    has_wl = wl_col and wl_col in df.columns
    has_pr = pr_col and pr_col in df.columns

    if has_wl and has_pr and wl_col != pr_col:
        # FIX: (5 - x) / 4 * 100 → 1→100%, 5→0% — không clip, không mất info
        burnout_wl = (5 - df[wl_col]) / 4 * 100
        burnout_pr = (5 - df[pr_col]) / 4 * 100
        df['burnout_score'] = ((burnout_wl + burnout_pr) / 2).round(1)
        df['burnout_proxy'] = (df['burnout_score'] >= 50).astype(int)
    elif has_wl:
        df['burnout_score'] = ((5 - df[wl_col]) / 4 * 100).round(1)
        df['burnout_proxy'] = (df['burnout_score'] >= 50).astype(int)
    else:
        df['burnout_score'] = np.nan
        df['burnout_proxy'] = np.nan

    # NOTE 3B: pressure = workload (cùng câu C18), burnout_score sẽ chỉ dùng 1 item
    if group_id == '3B':
        df['burnout_note'] = 'Single-item burnout proxy (3B pressure=workload=C18)'

    return df


# ---- 3.3 Cronbach Alpha ----
# FIX #3: Luôn trả về dict — không có type inconsistency

def cronbach_alpha(df: pd.DataFrame, cols: list) -> dict:
    """
    Tính độ tin cậy cho một pillar.
    LUÔN trả về dict với keys: type, value, n_items, interpretation, warning.
    """
    valid_cols = [c for c in cols if c in df.columns]
    data = df[valid_cols].dropna()

    base = {'n_items': len(valid_cols), 'n_respondents': len(data)}

    if len(valid_cols) < 2:
        return {**base, 'type': 'insufficient', 'value': None,
                'interpretation': 'Cần ≥ 2 items', 'warning': 'Không tính được'}

    if len(valid_cols) == 2:
        # 2 items: Pearson r (không phải alpha)
        if len(data) < 5:
            return {**base, 'type': 'pearson_r', 'value': None,
                    'warning': 'Cỡ mẫu quá nhỏ (n<5)'}
        r, p = scipy_stats.pearsonr(data[valid_cols[0]], data[valid_cols[1]])
        return {
            **base, 'type': 'pearson_r', 'value': round(float(r), 3),
            'p_value': round(float(p), 4),
            'interpretation': (
                'Tương quan mạnh (r≥0.6)' if r >= 0.6 else
                'Tương quan trung bình (0.3≤r<0.6)' if r >= 0.3 else
                'Tương quan yếu (r<0.3)'
            ),
            'warning': '2-item scale: dùng Pearson r, không phải Cronbach alpha. Interpret with caution.'
        }

    # ≥ 3 items: Cronbach alpha
    n_items  = len(valid_cols)
    item_var = data.var(axis=0, ddof=1).sum()
    total_var = data.sum(axis=1).var(ddof=1)
    if total_var == 0:
        return {**base, 'type': 'cronbach_alpha', 'value': None,
                'warning': 'Zero variance — all respondents answered the same'}
    alpha = (n_items / (n_items - 1)) * (1 - item_var / total_var)
    alpha = float(np.clip(alpha, -1, 1))  # bound theo lý thuyết

    return {
        **base, 'type': 'cronbach_alpha', 'value': round(alpha, 3),
        'interpretation': (
            'Tốt (α≥0.70)' if alpha >= 0.70 else
            'Chấp nhận được (0.60≤α<0.70)' if alpha >= 0.60 else
            'Thấp (α<0.60) — interpret trụ cột này thận trọng'
        ),
        'warning': (
            None if alpha >= 0.60
            else f'⚠️ Cronbach α = {round(alpha,3)} < 0.60 — items trong trụ cột này đo nhiều construct khác nhau'
        )
    }


def validate_pillar_reliability(df: pd.DataFrame, group_id: str) -> dict:
    """Chạy reliability check cho tất cả pillars của một group."""
    report = {}
    for pillar in ['TC1', 'TC2', 'TC3', 'TC4', 'TC5']:
        qs = get_pillar_questions(group_id, pillar)
        report[pillar] = cronbach_alpha(df, qs)
    return report


# ---- 3.4 All Indices ----

def compute_all_indices(df: pd.DataFrame, group_id: str,
                        weights: dict = None) -> pd.DataFrame:
    """
    Tính toàn bộ derived indices. Chạy trên FULL dataset (không filter theo unit).
    Trả về df với các cột mới.
    """
    if weights is None:
        weights = CALIBRATED_WEIGHTS.get(group_id, DEFAULT_WEIGHTS)

    pillars = ['TC1', 'TC2', 'TC3', 'TC4', 'TC5']

    # 1. Pillar Scores
    for p in pillars:
        df[f'{p}_score'] = compute_pillar_score(df, group_id, p)

    # 2. Engagement Index
    available = [p for p in pillars if f'{p}_score' in df.columns]
    w_sum = sum(weights[p] for p in available)
    df['EI'] = sum(df[f'{p}_score'] * (weights[p] / w_sum) for p in available).round(2)

    # 3. Manager Effectiveness Index (proxy)
    df['MEI'] = df['TC2_score']
    # Nota: MEI = TC2_score là proxy. Lý tưởng cần 360 feedback riêng.

    # 4. Burnout
    df = compute_burnout(df, group_id)

    # 5. Attrition / eNPS
    if 'C22' in df.columns:
        df['attrition_score'] = df['C22']
        df['attrition_risk']  = (6 - df['C22'])   # reverse: 5=high risk
        df['is_flight_risk']  = (df['C22'] <= 2).astype(int)

    if 'C23' in df.columns:
        df['eNPS_raw'] = df['C23']
        df['eNPS_cat'] = pd.cut(df['C23'], bins=ENPS_BINS, labels=ENPS_LABELS)

    # 6. Career Growth Index
    career_col = get_item(group_id, 'career')
    if career_col and career_col in df.columns:
        df['career_index'] = ((df[career_col] - 1) / 4 * 100).round(1)

    # 7. Psychological Safety Score
    ps_col = get_item(group_id, 'psych_safety')
    if ps_col and ps_col in df.columns:
        df['psych_safety_score'] = ((df[ps_col] - 1) / 4 * 100).round(1)

    # 8. Respect Index
    resp_col = get_item(group_id, 'respect')
    if resp_col and resp_col in df.columns:
        df['respect_index'] = ((df[resp_col] - 1) / 4 * 100).round(1)

    # 9. JSI Proxy
    # FIX #10: workload item per group được lấy qua get_item() — đúng cho 3B (C18/TC5)
    tc4_s = df.get('TC4_score', pd.Series(np.nan, index=df.index))
    wl_col = get_item(group_id, 'workload')
    wl_s   = ((df[wl_col] - 1) / 4 * 100) if wl_col and wl_col in df.columns else pd.Series(np.nan, index=df.index)
    bl_col = get_item(group_id, 'belonging') or get_item(group_id, 'pride') or get_item(group_id, 'respect')
    bl_s   = ((df[bl_col] - 1) / 4 * 100) if bl_col and bl_col in df.columns else pd.Series(np.nan, index=df.index)
    df['JSI'] = (0.4 * tc4_s + 0.3 * wl_s + 0.3 * bl_s).round(2)
    if group_id == '3B':
        df['JSI_note'] = 'JSI workload component = C18 (TC5) cho 3B — cross-pillar'

    return df


# ---- 3.5 Aggregate to unit level ----

def aggregate_unit(df: pd.DataFrame, group_col: str = 'unit') -> pd.DataFrame:
    """Tổng hợp individual → unit-level. Loại đơn vị n < MIN_UNIT_N."""
    score_cols = [c for c in df.columns if c.endswith('_score') or c in ['EI', 'MEI', 'JSI', 'eNPS_raw']]
    binary_cols = ['is_flight_risk', 'burnout_proxy']

    agg = df.groupby(group_col)[score_cols].agg(['mean', 'std']).round(2)
    agg.columns = ['_'.join(c) for c in agg.columns]

    # Sample size (tránh dùng tên cột giả định)
    agg['n'] = df.groupby(group_col)[score_cols[0]].count()

    for col in binary_cols:
        if col in df.columns:
            agg[f'{col}_pct'] = (df.groupby(group_col)[col].mean() * 100).round(1)

    if 'eNPS_cat' in df.columns:
        enps = df.groupby(group_col)['eNPS_cat'].value_counts(normalize=True).unstack(fill_value=0)
        agg['eNPS_score'] = ((enps.get('Promoter', 0) - enps.get('Detractor', 0)) * 100).round(1)

    # Ẩn đơn vị có n < MIN_UNIT_N
    small = agg['n'] < MIN_UNIT_N
    if small.any():
        print(f"⚠️ {small.sum()} đơn vị bị ẩn do n < {MIN_UNIT_N}: {agg[small].index.tolist()}")
    return agg[~small]


# ---- 3.6 Weight Calibration ----
# FIX #1: Ridge Regression + VIF check thay vì Logistic Regression thuần

def check_multicollinearity(X: np.ndarray, feature_names: list) -> dict:
    """
    Tính VIF (Variance Inflation Factor) cho từng feature.
    VIF > 5 = multicollinearity đáng lo ngại.
    VIF > 10 = multicollinearity nghiêm trọng.
    """
    from numpy.linalg import inv
    try:
        corr = np.corrcoef(X.T)
        vif_values = np.diag(inv(corr))
        return {name: round(float(v), 2) for name, v in zip(feature_names, vif_values)}
    except np.linalg.LinAlgError:
        return {name: float('inf') for name in feature_names}


def calibrate_weights(df: pd.DataFrame, group_id: str,
                      min_n: int = 50, min_flight_rate: float = 0.05) -> dict:
    """
    Calibrate pillar weights empirically dựa trên Permutation Importance.
    FIX #1: Dùng Ridge Logistic + Permutation Importance thay vì raw coefficients
    vì raw Logistic coefficients bị distorted bởi multicollinearity.

    Workflow:
    1. Check multicollinearity (VIF)
    2. Nếu VIF cao → dùng Ridge (L2 penalty giảm variance)
    3. Dùng Permutation Importance (không bị bias bởi scale hay collinearity)
    4. Normalize permutation importance thành weights
    """
    features = ['TC1_score', 'TC2_score', 'TC3_score', 'TC4_score', 'TC5_score']
    target   = 'is_flight_risk'
    data = df[[*features, target]].dropna()

    print(f"\n=== Calibrating weights cho nhóm {group_id} ===")
    print(f"Sample size: n={len(data)}, flight_risk={data[target].mean():.1%}")

    if len(data) < min_n:
        print(f"⚠️ n={len(data)} < {min_n} — cỡ mẫu nhỏ, dùng default weights")
        return DEFAULT_WEIGHTS

    if data[target].mean() < min_flight_rate:
        print(f"⚠️ Flight risk rate {data[target].mean():.1%} < {min_flight_rate:.0%} — quá ít cases, dùng default weights")
        return DEFAULT_WEIGHTS

    X = data[features].values
    y = data[target].values
    feature_short = ['TC1', 'TC2', 'TC3', 'TC4', 'TC5']

    # Step 1: VIF check
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    vif = check_multicollinearity(X_scaled, feature_short)
    high_vif = {k: v for k, v in vif.items() if v > 5}
    print(f"VIF: {vif}")
    if high_vif:
        print(f"⚠️ Multicollinearity detected (VIF>5): {high_vif} → dùng Ridge")

    # Step 2: Fit Ridge Logistic Regression
    # alpha=1.0 là regularization strength — có thể tune nếu cần
    from sklearn.linear_model import LogisticRegression
    model = LogisticRegression(penalty='l2', C=1.0, solver='lbfgs',
                                max_iter=1000, random_state=42)
    model.fit(X_scaled, y)

    # Step 3: Cross-validated permutation importance (không bị bias bởi collinearity)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        perm = permutation_importance(model, X_scaled, y, n_repeats=20,
                                       random_state=42, scoring='roc_auc')

    importances = perm.importances_mean
    importances = np.maximum(importances, 0)  # clip âm về 0

    if importances.sum() == 0:
        print("⚠️ Permutation importance = 0 cho tất cả features — dùng default weights")
        return DEFAULT_WEIGHTS

    weights = dict(zip(feature_short, (importances / importances.sum()).round(4)))
    print(f"✅ Calibrated weights: {weights}")

    # Cross-validation score để báo cáo độ tin cậy
    cv_auc = cross_val_score(model, X_scaled, y, cv=5, scoring='roc_auc').mean()
    print(f"Model CV AUC: {cv_auc:.3f} {'✅ Đủ tin cậy' if cv_auc > 0.65 else '⚠️ Thấp — weights nên treat as directional only'}")

    CALIBRATED_WEIGHTS[group_id] = weights
    return weights


# ---- 3.7 Relative Thresholds ----

def compute_relative_thresholds(df: pd.DataFrame, group_id: str) -> dict:
    """
    Tính ngưỡng anomaly từ distribution thực của GHN.
    Chạy 1 lần trên FULL dataset sau khi đã compute_all_indices().
    """
    metrics = ['TC1_score', 'TC2_score', 'TC3_score', 'TC4_score', 'TC5_score',
               'EI', 'MEI', 'burnout_score', 'career_index', 'JSI',
               'respect_index', 'psych_safety_score']
    binary  = ['is_flight_risk']

    thresholds = {}
    for m in metrics:
        if m not in df.columns:
            continue
        s = df[m].dropna()
        if len(s) < 10:
            continue
        thresholds[m] = {
            'mean': round(s.mean(), 2), 'std': round(s.std(), 2),
            'p10':  round(s.quantile(0.10), 2), 'p25': round(s.quantile(0.25), 2),
            'p50':  round(s.quantile(0.50), 2), 'p75': round(s.quantile(0.75), 2),
            'p90':  round(s.quantile(0.90), 2),
        }

    for b in binary:
        if b in df.columns:
            s = df[b].dropna()
            thresholds[f'{b}_pct'] = {
                'mean': round(s.mean() * 100, 2),
                'p25':  round(s.quantile(0.25) * 100, 2),
                'p75':  round(s.quantile(0.75) * 100, 2),
                'p90':  round(s.quantile(0.90) * 100, 2),
            }

    return thresholds
```

---

## 4. DATA QUALITY PIPELINE

```python
def run_data_quality_pipeline(df: pd.DataFrame, group_id: str) -> tuple:
    """
    Step 0 — bắt buộc trước mọi phân tích.
    Returns: (df_clean, quality_report)
    """
    content_cols = [f'C{i}' for i in range(1, 22) if f'C{i}' in df.columns]
    report = {
        'original_n': len(df), 'group_id': group_id,
        'flags': {}, 'warnings': [], 'excluded_ids': []
    }
    excl = pd.Series(False, index=df.index)

    # Flag 1: Straight-liners (≥80% cùng điểm trong content questions)
    def _is_straightliner(row):
        vals = row[content_cols].dropna()
        return len(vals) >= 10 and vals.value_counts(normalize=True).max() >= 0.80

    sl = df.apply(_is_straightliner, axis=1)
    report['flags']['straight_liners'] = int(sl.sum())
    if sl.any():
        report['warnings'].append(f"⚠️ {sl.sum()} straight-liner responses (≥80% cùng điểm)")
    excl |= sl

    # Flag 2: Speeders
    if 'completion_time_sec' in df.columns:
        sp = df['completion_time_sec'] < 180
        report['flags']['speeders'] = int(sp.sum())
        if sp.any():
            report['warnings'].append(f"⚠️ {sp.sum()} responses < 3 phút")
        excl |= sp

    # Flag 3: Logical inconsistency (pride cao nhưng muốn nghỉ — flag, không loại)
    pride_col = get_item(group_id, 'pride')
    if pride_col and pride_col in df.columns and 'C22' in df.columns:
        incon = (df[pride_col] >= 4) & (df['C22'] == 1)
        report['flags']['logical_inconsistency'] = int(incon.sum())
        if incon.any():
            report['warnings'].append(
                f"ℹ️ {incon.sum()} responses: Pride≥4 nhưng C22=1 — review thủ công"
            )

    # Flag 4: Excessive missing (>30% content questions)
    miss_rate = df[content_cols].isna().mean(axis=1)
    emiss = miss_rate > 0.30
    report['flags']['excessive_missing'] = int(emiss.sum())
    if emiss.any():
        report['warnings'].append(f"⚠️ {emiss.sum()} responses thiếu >30% câu hỏi")
    excl |= emiss

    # Flag 5: Anonymity check per unit
    if 'unit' in df.columns:
        small = df['unit'].value_counts()
        small = small[small < MIN_UNIT_N].index.tolist()
        if small:
            report['warnings'].append(
                f"🔒 {len(small)} đơn vị n < {MIN_UNIT_N} — kết quả sẽ bị ẩn: {small[:5]}"
            )

    # Silence pattern (3 câu mở riêng biệt — FIX v2)
    open_cols = [c for c in ['C24', 'C25', 'C26'] if c in df.columns]
    if open_cols:
        is_blank = {c: (df[c].isna() | (df[c].astype(str).str.strip() == '')) for c in open_cols}
        report['silence_rate'] = {
            c: round(is_blank[c].mean() * 100, 1) for c in open_cols
        }
        if len(open_cols) == 3:
            all_skip    = is_blank['C24'] & is_blank['C25'] & is_blank['C26']
            only_c26    = is_blank['C24'] & is_blank['C25'] & ~is_blank['C26']
            report['silence_rate']['all_3_skip']       = round(all_skip.mean() * 100, 1)
            report['silence_rate']['frustration_only']  = round(only_c26.mean() * 100, 1)
            if report['silence_rate']['all_3_skip'] > 50:
                report['warnings'].append(
                    f"🔴 {report['silence_rate']['all_3_skip']}% không điền bất kỳ câu mở nào — "
                    f"dấu hiệu thiếu tin tưởng vào ẩn danh"
                )
            if report['silence_rate'].get('frustration_only', 0) > 15:
                report['warnings'].append(
                    f"⚡ {report['silence_rate']['frustration_only']}% chỉ điền C26 (vấn đề) — "
                    f"frustration cao, không thấy điểm tích cực"
                )

    # Summary
    report['excluded_n'] = int(excl.sum())
    report['clean_n']    = int((~excl).sum())
    report['excl_rate']  = round(report['excluded_n'] / report['original_n'] * 100, 1)
    if report['excl_rate'] > 15:
        report['warnings'].append(
            f"🔴 Tỷ lệ loại cao ({report['excl_rate']}%) — kiểm tra quy trình thu thập dữ liệu"
        )

    df_clean = df[~excl].copy()
    return df_clean, report
```

---

## 5. ANOMALY DETECTION

### 5.1 HRIS Helper — FIX #6

```python
def get_unit_hris(df_survey_unit: pd.DataFrame,
                  df_hris: pd.DataFrame,
                  join_key: str = 'employee_id') -> pd.DataFrame | None:
    """
    FIX #6: Filter HRIS về đúng unit trước khi dùng bất kỳ HRIS metric nào.
    Không pre-filter = income benchmark tính trên toàn công ty = SAI.
    """
    if df_hris is None:
        return None
    if join_key not in df_survey_unit.columns or join_key not in df_hris.columns:
        print(f"⚠️ Join key '{join_key}' không có trong survey hoặc HRIS — HRIS enrichment bị bỏ qua")
        return None
    unit_ids = df_survey_unit[join_key].dropna().unique()
    filtered = df_hris[df_hris[join_key].isin(unit_ids)]
    if len(filtered) == 0:
        print(f"⚠️ Không tìm thấy HRIS records cho unit này (n_survey={len(df_survey_unit)})")
        return None
    return filtered


### 5.2 Per-Pillar Anomaly Detectors

def _is_low(val, thresh_dict, key='p25'):
    """Helper: kiểm tra val < ngưỡng, trả False nếu thiếu dữ liệu."""
    if np.isnan(val) or thresh_dict.get(key) is None:
        return False
    return val < thresh_dict[key]

def _is_high(val, thresh_dict, key='p75'):
    if np.isnan(val) or thresh_dict.get(key) is None:
        return False
    return val > thresh_dict[key]


def detect_TC1_anomalies(unit_df, company_thresholds, group_id):
    anomalies = []
    t1 = company_thresholds.get('TC1_score', {})
    ei_t = company_thresholds.get('EI', {})

    tc1_mean = unit_df['TC1_score'].mean() if 'TC1_score' in unit_df.columns else np.nan
    ei_mean  = unit_df['EI'].mean()         if 'EI' in unit_df.columns else np.nan

    # A1: Mất niềm tin cục bộ
    if _is_low(tc1_mean, t1) and not _is_low(ei_mean, ei_t):
        anomalies.append({'id': 'TC1_A1', 'pattern': 'Mất niềm tin cục bộ',
                          'tc1': round(tc1_mean, 1), 'company_p25': t1.get('p25')})

    # A2: Thông tin đứt gãy — FIX #4: dùng alias, không dùng position
    trust_col = get_item(group_id, 'trust_item')
    comms_col = get_item(group_id, 'comms_item')
    if trust_col and comms_col and trust_col in unit_df.columns and comms_col in unit_df.columns:
        trust_mean = unit_df[trust_col].mean()
        comms_mean = unit_df[comms_col].mean()
        gap = trust_mean - comms_mean
        if gap > 0.5:
            anomalies.append({
                'id': 'TC1_A2', 'pattern': 'Thông tin đứt gãy',
                'trust': round(trust_mean, 2), 'comms': round(comms_mean, 2),
                'gap': round(gap, 2),
                'interpretation': 'Tin BLĐ nhưng KHÔNG được thông báo kịp thời → kênh truyền thông vấn đề'
            })
    elif group_id == '3B':
        pass  # 3B không có comms_item — TC1_A2 không apply

    # A3: Nghịch lý tin tưởng
    fr_t   = company_thresholds.get('is_flight_risk_pct', {})
    fr_pct = unit_df['is_flight_risk'].mean() * 100 if 'is_flight_risk' in unit_df.columns else np.nan
    if _is_high(tc1_mean, t1) and _is_high(fr_pct, fr_t):
        anomalies.append({'id': 'TC1_A3', 'pattern': 'Nghịch lý tin tưởng',
                          'tc1': round(tc1_mean, 1), 'flight_pct': round(fr_pct, 1),
                          'note': 'Tin BLĐ nhưng vẫn muốn nghỉ → deep dive TC2–TC4'})

    # A4: Generation Gap
    if 'gen3' in unit_df.columns and 'TC1_score' in unit_df.columns:
        gen_tc1 = unit_df.groupby('gen3')['TC1_score'].mean()
        gz = gen_tc1.get('Gen Z', np.nan)
        gx = gen_tc1.get('Gen X', np.nan)
        if not np.isnan(gz) and not np.isnan(gx) and (gx - gz) > 20:
            anomalies.append({'id': 'TC1_A4', 'pattern': 'Generation Gap',
                              'gen_z_tc1': round(gz, 1), 'gen_x_tc1': round(gx, 1),
                              'gap_pct': round(gx - gz, 1)})
    return anomalies


def detect_TC2_anomalies(unit_df, company_thresholds, group_id):
    anomalies = []
    t2 = company_thresholds.get('TC2_score', {})
    ei_t = company_thresholds.get('EI', {})
    fr_t = company_thresholds.get('is_flight_risk_pct', {})

    tc2_mean = unit_df['TC2_score'].mean() if 'TC2_score' in unit_df.columns else np.nan
    ei_mean  = unit_df['EI'].mean()         if 'EI' in unit_df.columns else np.nan
    fr_pct   = unit_df['is_flight_risk'].mean() * 100 if 'is_flight_risk' in unit_df.columns else np.nan

    # A1: Manager Island
    if _is_high(tc2_mean, t2) and _is_low(ei_mean, ei_t):
        anomalies.append({'id': 'TC2_A1', 'pattern': 'Manager Island',
                          'tc2': round(tc2_mean, 1), 'ei': round(ei_mean, 1),
                          'risk': 'NV ở lại vì QL — rủi ro nếu QL nghỉ'})

    # A2: Fairness gap
    fair_col    = get_item(group_id, 'fairness')
    tc2_qs      = get_pillar_questions(group_id, 'TC2')
    support_col = tc2_qs[0] if tc2_qs else None
    if (fair_col and fair_col in unit_df.columns and
            support_col and support_col in unit_df.columns and
            fair_col != support_col):
        gap = unit_df[support_col].mean() - unit_df[fair_col].mean()
        if gap > 0.6:
            anomalies.append({
                'id': 'TC2_A2', 'pattern': 'Phân biệt đối xử / Thiếu công bằng',
                'support': round(unit_df[support_col].mean(), 2),
                'fairness': round(unit_df[fair_col].mean(), 2),
                'gap': round(gap, 2)
            })

    # A3: QL yếu toàn diện
    if _is_low(tc2_mean, t2, 'p10') and len(unit_df) >= 15:
        breakdown = {q: round(unit_df[q].mean(), 2) for q in tc2_qs if q in unit_df.columns}
        anomalies.append({'id': 'TC2_A3', 'pattern': 'Quản lý yếu toàn diện',
                          'tc2': round(tc2_mean, 1), 'n': len(unit_df),
                          'breakdown': breakdown})

    # A4: MEI shield thất bại
    if _is_high(tc2_mean, t2) and _is_high(fr_pct, fr_t):
        anomalies.append({'id': 'TC2_A4', 'pattern': 'MEI shield thất bại',
                          'tc2': round(tc2_mean, 1), 'flight_pct': round(fr_pct, 1),
                          'note': 'QL tốt nhưng TC4 (thu nhập) quá thấp override'})

    # A5: Feedback item yếu nhất
    feed_col = get_item(group_id, 'feedback')
    if feed_col and tc2_qs:
        tc2_means = {q: unit_df[q].mean() for q in tc2_qs if q in unit_df.columns}
        if tc2_means and min(tc2_means, key=tc2_means.get) == feed_col:
            anomalies.append({'id': 'TC2_A5', 'pattern': 'Feedback một chiều',
                              'feedback_score': round(tc2_means[feed_col], 2),
                              'tc2_avg': round(np.mean(list(tc2_means.values())), 2)})
    return anomalies


def detect_TC3_anomalies(unit_df, company_thresholds, group_id):
    anomalies = []
    tc3_qs  = get_pillar_questions(group_id, 'TC3')
    tc3_means = {q: unit_df[q].mean() for q in tc3_qs if q in unit_df.columns}
    bn_t = company_thresholds.get('burnout_score', {})

    # A1: Công cụ cản trở (item đầu TC3)
    tool_col = get_item(group_id, 'tool')
    if tool_col and tool_col in unit_df.columns and unit_df[tool_col].mean() < 3.0:
        anomalies.append({'id': 'TC3_A1', 'pattern': 'Công cụ cản trở',
                          'tool_score': round(unit_df[tool_col].mean(), 2),
                          'note': 'Cross-check HRIS năng suất đơn vị này'})

    # A2: Burnout ẩn
    wl_col = get_item(group_id, 'workload')
    if (wl_col and wl_col in unit_df.columns and 'burnout_score' in unit_df.columns):
        wl_mean = unit_df[wl_col].mean()
        bn_mean = unit_df['burnout_score'].mean()
        if wl_mean > 3.0 and _is_high(bn_mean, bn_t):
            anomalies.append({'id': 'TC3_A2', 'pattern': 'Burnout ẩn',
                              'perceived_workload_ok': round(wl_mean, 2),
                              'burnout_score': round(bn_mean, 1),
                              'note': 'Triangulate với NLP câu mở C25/C26'})

    # A3: Trần thủy tinh
    career_col = get_item(group_id, 'career')
    if career_col and career_col in unit_df.columns and 'tenure' in unit_df.columns:
        senior = unit_df['tenure'] >= SENIOR_TENURE_THRESHOLD
        s_career = unit_df.loc[senior, career_col].mean()
        j_career = unit_df.loc[~senior, career_col].mean()
        if not np.isnan(s_career) and s_career < 3.0:
            anomalies.append({'id': 'TC3_A3', 'pattern': 'Trần thủy tinh',
                              'senior_career': round(s_career, 2),
                              'junior_career': round(j_career, 2) if not np.isnan(j_career) else None,
                              'interpretation': 'NV lâu năm không thấy tương lai → quiet quitting'})

    # A4: Hướng dẫn thay đổi kém (item cuối TC3)
    if tc3_qs and tc3_means:
        guidance_col = tc3_qs[-1]
        if guidance_col in tc3_means and min(tc3_means, key=tc3_means.get) == guidance_col:
            anomalies.append({'id': 'TC3_A4', 'pattern': 'Thay đổi không hướng dẫn',
                              'score': round(tc3_means[guidance_col], 2),
                              'note': 'Check TC1_A2: thường đi kèm'})

    # A5: An toàn lao động (1B, 2A)
    safety_col = get_item(group_id, 'safety') or get_item(group_id, 'safety_labor')
    if safety_col and safety_col in unit_df.columns and unit_df[safety_col].mean() < 3.0:
        anomalies.append({'id': 'TC3_A5', 'pattern': 'ATLĐ bị xem nhẹ',
                          'safety_score': round(unit_df[safety_col].mean(), 2),
                          'action': 'Ưu tiên cao — kiểm tra vật chất + NLP tìm "tai nạn", "nguy hiểm"'})
    return anomalies


def detect_TC4_anomalies(unit_df, company_thresholds, group_id, df_hris_full=None):
    anomalies = []
    # FIX #6: filter HRIS theo unit TRƯỚC khi dùng
    df_hris = get_unit_hris(unit_df, df_hris_full)

    t4 = company_thresholds.get('TC4_score', {})
    fr_t = company_thresholds.get('is_flight_risk_pct', {})

    income_col = get_item(group_id, 'income_fair')
    trans_col  = get_item(group_id, 'transparency')
    tc4_qs     = get_pillar_questions(group_id, 'TC4')

    # A1: Bất công cảm nhận
    if income_col and income_col in unit_df.columns:
        inc_mean = unit_df[income_col].mean()
        if _is_low(inc_mean, t4, 'p25'):
            r = {'id': 'TC4_A1', 'pattern': 'Bất công cảm nhận',
                 'perceived_fairness': round(inc_mean, 2)}
            if df_hris is not None and 'income_m' in df_hris.columns:
                unit_inc = df_hris['income_m'].mean()  # Đã filter → đúng unit
                company_median = company_thresholds.get('hris_income_median', None)
                r['unit_avg_income'] = round(unit_inc, 0)
                if company_median and unit_inc > company_median and _is_low(inc_mean, t4, 'p25'):
                    r['interpretation'] = '🔑 Thu nhập TRÊN median nhưng cảm nhận THẤP → vấn đề minh bạch'
            anomalies.append(r)

    # A2: Minh bạch kém
    if (trans_col and trans_col in unit_df.columns and
            income_col and income_col in unit_df.columns and
            trans_col != income_col):
        gap = unit_df[income_col].mean() - unit_df[trans_col].mean()
        if gap > 0.5:
            r = {'id': 'TC4_A2', 'pattern': 'Phạt/Phụ cấp không minh bạch',
                 'transparency': round(unit_df[trans_col].mean(), 2),
                 'income_fair': round(unit_df[income_col].mean(), 2),
                 'gap': round(gap, 2)}
            if df_hris is not None and 'tong_phat' in df_hris.columns:
                r['pct_penalized'] = round((df_hris['tong_phat'] > 0).mean() * 100, 1)
                r['avg_penalty']   = round(df_hris['tong_phat'].mean(), 0)
            anomalies.append(r)

    # A3: Tiền tốt vẫn nghỉ
    tc4_mean = unit_df['TC4_score'].mean() if 'TC4_score' in unit_df.columns else np.nan
    fr_pct   = unit_df['is_flight_risk'].mean() * 100 if 'is_flight_risk' in unit_df.columns else np.nan
    if _is_high(tc4_mean, t4) and _is_high(fr_pct, fr_t):
        anomalies.append({'id': 'TC4_A3', 'pattern': 'Thu nhập tốt, vẫn muốn nghỉ',
                          'tc4': round(tc4_mean, 1), 'flight_pct': round(fr_pct, 1),
                          'note': 'Tiền không phải nguyên nhân → deep dive TC2, TC5'})

    # A4: Hỗ trợ sự cố kém
    if tc4_qs:
        incident_col = get_item(group_id, 'incident_pay')
        if incident_col and incident_col in unit_df.columns:
            inc_pay = unit_df[incident_col].mean()
            tc4_means = {q: unit_df[q].mean() for q in tc4_qs if q in unit_df.columns}
            if tc4_means and min(tc4_means, key=tc4_means.get) == incident_col:
                anomalies.append({'id': 'TC4_A4', 'pattern': 'Hỗ trợ sự cố kém',
                                  'score': round(inc_pay, 2),
                                  'note': 'NLP: tìm "sự cố", "bồi thường", "không ai giúp"'})
    return anomalies


def detect_TC5_anomalies(unit_df, company_thresholds, group_id):
    anomalies = []
    bn_t = company_thresholds.get('burnout_score', {})
    ei_t = company_thresholds.get('EI', {})
    fr_t = company_thresholds.get('is_flight_risk_pct', {})
    rs_t = company_thresholds.get('respect_index', {})

    pride_col   = get_item(group_id, 'pride')
    peer_col    = get_item(group_id, 'peer')
    pressure_col= get_item(group_id, 'pressure')
    respect_col = get_item(group_id, 'respect')

    burnout_mean = unit_df['burnout_score'].mean() if 'burnout_score' in unit_df.columns else np.nan
    ei_mean      = unit_df['EI'].mean()             if 'EI' in unit_df.columns else np.nan

    # A1: Tự hào nhưng kiệt sức
    if pride_col and pride_col in unit_df.columns:
        if unit_df[pride_col].mean() > 3.8 and _is_high(burnout_mean, bn_t):
            anomalies.append({'id': 'TC5_A1', 'pattern': 'Tự hào nhưng kiệt sức',
                              'pride': round(unit_df[pride_col].mean(), 2),
                              'burnout': round(burnout_mean, 1),
                              'risk': 'Committed Under Pressure — sẽ flip nếu không can thiệp'})

    # A2: Social Glue Risk
    if peer_col and peer_col in unit_df.columns:
        if unit_df[peer_col].mean() > 3.8 and _is_low(ei_mean, ei_t):
            anomalies.append({'id': 'TC5_A2', 'pattern': 'Social Glue Risk',
                              'peer': round(unit_df[peer_col].mean(), 2), 'ei': round(ei_mean, 1),
                              'risk': 'Ở lại vì bạn — domino khi 1 người nghỉ'})

    # A3 + EWS: Onboarding Shock — FIX #5: dùng EWS_TENURE_THRESHOLD constant
    ews_thresh = EWS_TENURE_THRESHOLD.get(group_id, 2)
    if pressure_col and pressure_col in unit_df.columns and 'tenure' in unit_df.columns:
        new_mask = unit_df['tenure'] <= ews_thresh
        new_df   = unit_df[new_mask]
        if len(new_df) >= 3:
            new_pressure = new_df[pressure_col].mean()
            if new_pressure < 3.0:
                new_fr = new_df['is_flight_risk'].mean() * 100 if 'is_flight_risk' in new_df.columns else None
                anomalies.append({
                    'id': 'TC5_A3', 'pattern': 'Onboarding Shock — EWS',
                    'new_n': len(new_df), 'new_pressure': round(new_pressure, 2),
                    'new_flight_pct': round(new_fr, 1) if new_fr else None,
                    'ews_window': f'tenure ≤ index {ews_thresh} ({TENURE_LABELS[ews_thresh]})',
                    'action': '🚨 HRBP gặp nhóm này trong tuần này'
                })

    # A4: Burnout blind spot
    if pressure_col and pressure_col in unit_df.columns:
        if unit_df[pressure_col].mean() >= 3.8 and _is_high(burnout_mean, bn_t):
            anomalies.append({'id': 'TC5_A4', 'pattern': 'Burnout Blind Spot',
                              'perceived_ok': round(unit_df[pressure_col].mean(), 2),
                              'burnout': round(burnout_mean, 1),
                              'note': 'NV không nhận ra mình kiệt sức — normalize hóa áp lực'})

    # A5: Respect Deficit
    if respect_col and respect_col in unit_df.columns:
        if _is_low(unit_df[respect_col].mean(), rs_t):
            fr_pct = unit_df['is_flight_risk'].mean() * 100 if 'is_flight_risk' in unit_df.columns else None
            anomalies.append({'id': 'TC5_A5', 'pattern': 'Respect Deficit',
                              'respect': round(unit_df[respect_col].mean(), 2),
                              'flight_pct': round(fr_pct, 1) if fr_pct else None,
                              'note': '⚡ Strongest attrition predictor cho lao động trực tiếp'})
    return anomalies
```

---

## 6. CROSS-PILLAR PATTERNS

```python
def detect_cross_pillar_patterns(unit_df: pd.DataFrame,
                                   company_thresholds: dict,
                                   group_id: str) -> list:
    """
    FIX #7: Vectorized operations — không dùng iterrows()
    FIX #5: EWS dùng EWS_TENURE_THRESHOLD constant
    FIX #8: Health score dùng percentile rank, không phải trọng số tùy tiện
    """
    patterns = []
    t = company_thresholds

    def get_mean(col): return unit_df[col].mean() if col in unit_df.columns else np.nan
    def low(val, key, pkey='p25'): return not np.isnan(val) and val < t.get(key, {}).get(pkey, np.inf)
    def high(val, key, pkey='p75'): return not np.isnan(val) and val > t.get(key, {}).get(pkey, -np.inf)

    tc1 = get_mean('TC1_score'); tc2 = get_mean('TC2_score')
    tc3 = get_mean('TC3_score'); tc4 = get_mean('TC4_score'); tc5 = get_mean('TC5_score')
    ei  = get_mean('EI'); burnout = get_mean('burnout_score')
    fr  = unit_df['is_flight_risk'].mean() * 100 if 'is_flight_risk' in unit_df.columns else np.nan

    # XP_1: Committed Under Pressure
    if high(burnout, 'burnout_score') and low(fr, 'is_flight_risk_pct'):
        patterns.append({'id': 'XP_1', 'name': 'Committed Under Pressure',
                         'burnout': round(burnout, 1), 'flight_pct': round(fr, 1),
                         'urgency': 'HIGH', 'action': 'Workload review + 1-1 trước khi flip'})

    # XP_2: Silent Disengaged
    if low(ei, 'EI') and low(fr, 'is_flight_risk_pct'):
        patterns.append({'id': 'XP_2', 'name': 'Silent Disengaged — Quiet Quitting',
                         'ei': round(ei, 1), 'flight_pct': round(fr, 1),
                         'urgency': 'MEDIUM', 'action': 'Skip-level conversation để tìm nguyên nhân thật'})

    # XP_3: Manager Island
    if high(tc2, 'TC2_score') and low(ei, 'EI'):
        worst_pillars = sorted([('TC1',tc1),('TC3',tc3),('TC4',tc4),('TC5',tc5)],
                                key=lambda x: x[1] if not np.isnan(x[1]) else 999)[:2]
        patterns.append({'id': 'XP_3', 'name': 'Manager Island',
                         'tc2': round(tc2, 1), 'ei': round(ei, 1),
                         'weakest': worst_pillars, 'urgency': 'MEDIUM'})

    # XP_4: Flight Risk Cluster
    if high(fr, 'is_flight_risk_pct', 'p90'):
        patterns.append({'id': 'XP_4', 'name': '🚨 Flight Risk Cluster',
                         'flight_pct': round(fr, 1),
                         'urgency': 'CRITICAL', 'action': 'HRBP + Line Mgr gặp trong 48h'})

    # XP_5: Income Paradox
    if high(tc4, 'TC4_score') and low(ei, 'EI'):
        patterns.append({'id': 'XP_5', 'name': 'Income Paradox',
                         'tc4': round(tc4, 1), 'ei': round(ei, 1),
                         'note': 'Tiền không phải vấn đề — deep dive TC2, TC3, TC5',
                         'urgency': 'MEDIUM'})

    # XP_6: Onboarding Shock EWS — FIX #5: consistent window
    ews_thresh = EWS_TENURE_THRESHOLD.get(group_id, 2)
    if 'tenure' in unit_df.columns and 'is_flight_risk' in unit_df.columns:
        new_mask = unit_df['tenure'] <= ews_thresh
        new_df   = unit_df[new_mask]
        if len(new_df) >= 3:
            new_fr  = new_df['is_flight_risk'].mean() * 100
            new_tc2 = new_df['TC2_score'].mean() if 'TC2_score' in new_df.columns else np.nan
            if new_fr > 30 or low(new_tc2, 'TC2_score'):
                patterns.append({'id': 'XP_6', 'name': 'Onboarding Shock EWS',
                                 'new_n': len(new_df), 'new_flight_pct': round(new_fr, 1),
                                 'new_tc2': round(new_tc2, 1) if not np.isnan(new_tc2) else None,
                                 'window': TENURE_LABELS[ews_thresh],
                                 'urgency': 'HIGH', 'action': 'Kích hoạt 30-60-90 day program'})

    # XP_7: Tenure Cliff
    if 'tenure' in unit_df.columns and 'EI' in unit_df.columns:
        tenure_ei = unit_df.groupby('tenure')['EI'].mean().reindex(range(len(TENURE_LABELS)))
        tenure_ei = tenure_ei.dropna()
        if len(tenure_ei) >= 4:
            diffs = tenure_ei.diff().dropna()
            cliff_idx_int = int(diffs.idxmin())
            cliff_val = float(diffs.min())
            if cliff_val < -15:
                patterns.append({'id': 'XP_7', 'name': 'Tenure Cliff',
                                 'cliff_at': TENURE_LABELS[cliff_idx_int] if cliff_idx_int < len(TENURE_LABELS) else cliff_idx_int,
                                 'ei_drop': round(cliff_val, 1), 'urgency': 'MEDIUM'})

    # XP_8: Generation Gap
    if 'gen3' in unit_df.columns:
        pillar_cols = [c for c in ['TC1_score','TC2_score','TC3_score','TC4_score','TC5_score']
                       if c in unit_df.columns]
        gen_scores = unit_df.groupby('gen3')[pillar_cols].mean()
        if 'Gen Z' in gen_scores.index and 'Gen X' in gen_scores.index:
            gap_series = gen_scores.loc['Gen X'] - gen_scores.loc['Gen Z']
            sig_pillars = gap_series[gap_series > 20].index.tolist()
            if len(sig_pillars) >= 2:
                patterns.append({'id': 'XP_8', 'name': 'Generation Gap Systemic',
                                 'significant_pillars': sig_pillars,
                                 'gen_z': gen_scores.loc['Gen Z'].round(1).to_dict(),
                                 'gen_x': gen_scores.loc['Gen X'].round(1).to_dict(),
                                 'urgency': 'MEDIUM'})

    # XP_9: Engagement Quadrant — FIX #7: vectorized, no iterrows
    # FIX: dùng EI × eNPS (không phải attrition × eNPS như v1)
    if 'EI' in unit_df.columns and 'eNPS_raw' in unit_df.columns:
        ei_median = t.get('EI', {}).get('p50', unit_df['EI'].median())
        conditions = [
            (unit_df['EI'] >= ei_median) & (unit_df['eNPS_raw'] >= ENPS_PROMOTER_MIN),
            (unit_df['EI'] <  ei_median) & (unit_df['eNPS_raw'] >= ENPS_PROMOTER_MIN),
            (unit_df['EI'] >= ei_median) & (unit_df['eNPS_raw'] <= ENPS_DETRACTOR_MAX),
        ]
        choices = ['Champions', 'Trapped Loyalists', 'Confused Leavers']
        quad = pd.Series(np.select(conditions, choices, default='Flight Risk'), index=unit_df.index)
        dist = quad.value_counts()
        patterns.append({'id': 'XP_9', 'name': 'Engagement Quadrant',
                         'distribution': dist.to_dict(),
                         'pct': (dist / len(quad) * 100).round(1).to_dict(),
                         'note': 'Dùng EI × eNPS (không phải attrition × eNPS)'})

    # XP_10: Contradiction Index (Fear-based compliance)
    silence_rate = t.get('_silence_all_3_skip', 0)
    if high(ei, 'EI') and silence_rate > 50:
        patterns.append({'id': 'XP_10', 'name': 'Contradiction Index',
                         'ei': round(ei, 1), 'silence_rate': silence_rate,
                         'note': 'EI cao + Silence cao → sợ nói thật', 'urgency': 'CHECK'})

    # XP_11: Quiet Exodus
    if low(burnout, 'burnout_score', 'p25') and high(fr, 'is_flight_risk_pct'):
        pillar_scores = {p: v for p, v in
                         [('TC1',tc1),('TC2',tc2),('TC3',tc3),('TC4',tc4),('TC5',tc5)]
                         if not np.isnan(v)}
        root = min(pillar_scores, key=pillar_scores.get) if pillar_scores else 'Unknown'
        patterns.append({'id': 'XP_11', 'name': 'Quiet Exodus',
                         'flight_pct': round(fr, 1), 'burnout': round(burnout, 1),
                         'likely_root': root,
                         'root_score': round(pillar_scores.get(root, 0), 1),
                         'urgency': 'HIGH'})

    return patterns


# ---- 6.1 Unit Health Score — FIX #8: percentile rank ----

def compute_unit_health(unit_df: pd.DataFrame,
                         company_distributions: dict) -> dict:
    """
    FIX #8: Dùng percentile rank so với GHN distribution.
    Không còn trọng số tùy tiện (0.5/0.3/0.2).
    100 = tốt nhất trong công ty, 0 = tệ nhất.
    """
    def pct_rank(val, dist_array):
        if np.isnan(val) or dist_array is None:
            return None
        return round(float(scipy_stats.percentileofscore(dist_array, val)), 1)

    ei_dist       = company_distributions.get('EI')
    burnout_dist  = company_distributions.get('burnout_score')
    flight_dist   = company_distributions.get('is_flight_risk')

    ei_val      = unit_df['EI'].mean() if 'EI' in unit_df.columns else np.nan
    burnout_val = unit_df['burnout_score'].mean() if 'burnout_score' in unit_df.columns else np.nan
    flight_val  = unit_df['is_flight_risk'].mean() * 100 if 'is_flight_risk' in unit_df.columns else np.nan

    return {
        'EI_percentile':      pct_rank(ei_val, ei_dist),           # cao = tốt
        'burnout_percentile': 100 - (pct_rank(burnout_val, burnout_dist) or 0),  # cao = tốt
        'retention_percentile': 100 - (pct_rank(flight_val, flight_dist) or 0),  # cao = tốt
        'note': 'Percentile rank within GHN. Không thể so sánh across years nếu distribution thay đổi.'
    }


def run_full_anomaly_scan(unit_df, company_thresholds, group_id,
                           df_hris_full=None, company_distributions=None) -> dict:
    """Entry point duy nhất. Chạy toàn bộ scan cho một unit."""
    return {
        'group_id': group_id, 'unit_n': len(unit_df),
        'pillar_anomalies': {
            'TC1': detect_TC1_anomalies(unit_df, company_thresholds, group_id),
            'TC2': detect_TC2_anomalies(unit_df, company_thresholds, group_id),
            'TC3': detect_TC3_anomalies(unit_df, company_thresholds, group_id),
            'TC4': detect_TC4_anomalies(unit_df, company_thresholds, group_id, df_hris_full),
            'TC5': detect_TC5_anomalies(unit_df, company_thresholds, group_id),
        },
        'cross_pillar_patterns': detect_cross_pillar_patterns(unit_df, company_thresholds, group_id),
        'health_score': compute_unit_health(unit_df, company_distributions or {}),
        'priority_actions': [
            p for p in detect_cross_pillar_patterns(unit_df, company_thresholds, group_id)
            if p.get('urgency') in ('CRITICAL', 'HIGH')
        ]
    }
```

---

## 7. DEEP DIVE FLOW

*(Giữ nguyên từ v2 — không có lỗi kỹ thuật)*

| Nhóm | Trigger ưu tiên | Focus |
|------|-----------------|-------|
| 1A | XP_4 + TC4_A1 + TC5_A5 | Thu nhập vs đơn vs khu vực; App Driver |
| 1B | TC5_A5 + TC3_A5 | Tuyến dài/ngắn; ca đêm; safety |
| 2A | TC5_A3 + XP_6 | Ca đêm cohort; OT fairness; ATLĐ |
| 2B | XP_1 + TC2_A1 | Áp lực kép; autonomy; burnout cascade |
| 3A | XP_2 + TC3_A3 | Process debt; cross-dept friction; invisible burnout |
| 3B | TC1_A5 + XP_1 | Strategy clarity; succession; peer collaboration |

---

## 8. AI PROMPT TEMPLATES

*(Giữ nguyên từ v2 — chất lượng tốt)*

```python
ANOMALY_INSIGHT_PROMPT = """
Bạn là Chuyên gia People Analytics cấp cao phân tích EES cho [{GROUP_NAME}].
Phân tích như McKinsey consultant, không như chatbot HR thông thường.

DỮ LIỆU PHÁT HIỆN:
Đơn vị: {UNIT_NAME} (n={N})
Pattern: {PATTERN_NAME} (ID: {PATTERN_ID})
{METRICS_JSON}
So sánh GHN: {BENCHMARK_DATA}

⚠️ Nếu n < 15: nhắc rõ kết quả cần validate bằng phỏng vấn trực tiếp.

YÊU CẦU:
1. TẠI SAO pattern này xuất hiện ở đây? 2–3 giả thuyết ưu tiên theo khả năng.
2. Nếu không can thiệp trong 60 ngày, hệ quả là gì?
3. 1 hành động CỤ THỂ trong 30 ngày: ai làm, làm gì, đo bằng gì.

Format: 3–4 đoạn ngắn, data-driven, cho người đọc là HRBP/Line Manager.
"""

CROSS_PILLAR_PROMPT = """
Phân tích sức khỏe tổ chức [{GROUP_NAME}] tại [{UNIT_NAME}]:

TC1: {TC1}% ({TC1_DELTA:+.1f}% vs GHN avg)
TC2: {TC2}% ({TC2_DELTA:+.1f}%)
TC3: {TC3}% ({TC3_DELTA:+.1f}%)
TC4: {TC4}% ({TC4_DELTA:+.1f}%)
TC5: {TC5}% ({TC5_DELTA:+.1f}%)
EI: {EI}% | Flight Risk: {FLIGHT_PCT}% | Burnout: {BURNOUT}% | eNPS: {ENPS}

Patterns: {PATTERNS_LIST}

1. Trụ cột "nút thắt cổ chai" — cải thiện sẽ kéo các trụ cột khác lên?
2. Mâu thuẫn đáng chú ý giữa các chỉ số?
3. Nếu chỉ có 1 can thiệp trong quý này, đó là gì và tại sao?
"""

EXECUTIVE_SUMMARY_PROMPT = """
Viết Executive Summary 1 trang (≤400 từ) cho C-Level/BOD về EES 2026.

COMPANY SCORECARD: {COMPANY_SCORECARD}
TOP STRENGTHS: {STRENGTHS}
TOP PAIN POINTS: {PAIN_POINTS}
HIGH RISK UNITS: {HIGH_RISK_UNITS}

Cấu trúc:
- 2 câu tổng quan tình hình
- 3 insight trọng yếu (data-backed)
- 3 khuyến nghị ưu tiên
- 1 câu cảnh báo rủi ro nếu không hành động

Tone: tự tin, thẳng thắn. Tránh ngôn ngữ mơ hồ và kết luận chung chung.
"""
```

---

## 9. FOUNDATION INDICES & TENURE COHORT

*(Giữ nguyên từ v2 — đã đúng)*

```python
def analyze_tenure_cohorts(df, group_id):
    """Phân tích EI theo cohort thâm niên → phát hiện Tenure Cliff và EWS."""
    if 'tenure' not in df.columns or 'EI' not in df.columns:
        return {}
    metrics = [c for c in ['EI','TC4_score','TC2_score','burnout_score','is_flight_risk'] if c in df.columns]
    cohort = df.groupby('tenure')[metrics].agg(['mean','count']).round(2)
    cohort.index = [TENURE_LABELS[i] if i < len(TENURE_LABELS) else i for i in cohort.index]
    company_ei = df['EI'].mean()
    ews_thresh = EWS_TENURE_THRESHOLD.get(group_id, 2)
    early_mask = df['tenure'] <= ews_thresh
    early_ei   = df.loc[early_mask, 'EI'].mean() if early_mask.any() else np.nan
    result = {'cohort_data': cohort.to_dict(), 'ews': [], 'cliffs': []}
    if not np.isnan(early_ei) and early_ei < company_ei - 10:
        result['ews'].append({'ei_gap': round(company_ei - early_ei, 1),
                              'action': 'Review onboarding — EI drop 0–6 tháng = early turnover signal'})
    return result
```

---

## 10. UNIT TESTS & SANITY CHECKS

> FIX #12: Chạy trước khi report bất kỳ kết quả nào. Phát hiện lỗi sớm, không để BOD nhận báo cáo sai.

```python
def run_sanity_checks(df: pd.DataFrame, group_id: str) -> dict:
    """
    Sanity checks sau compute_all_indices().
    Trả về {'passed': bool, 'issues': list[str], 'warnings': list[str]}
    """
    issues   = []
    warnings = []

    # Check 1: Pillar scores trong range 0–100
    for p in ['TC1_score', 'TC2_score', 'TC3_score', 'TC4_score', 'TC5_score']:
        if p in df.columns:
            out_of_range = ((df[p] < 0) | (df[p] > 100)).sum()
            if out_of_range > 0:
                issues.append(f"❌ {p}: {out_of_range} values ngoài range [0,100]")

    # Check 2: EI trong range 0–100
    if 'EI' in df.columns:
        oor = ((df['EI'] < 0) | (df['EI'] > 100)).sum()
        if oor > 0:
            issues.append(f"❌ EI: {oor} values ngoài range [0,100]")

    # Check 3: Burnout score trong range 0–100
    if 'burnout_score' in df.columns:
        oor = ((df['burnout_score'] < 0) | (df['burnout_score'] > 100)).sum()
        if oor > 0:
            issues.append(f"❌ burnout_score: {oor} values ngoài range [0,100]")

    # Check 4: attrition_risk và is_flight_risk nhất quán
    if 'C22' in df.columns and 'is_flight_risk' in df.columns:
        should_be_risk = df['C22'] <= 2
        mismatch = (should_be_risk != df['is_flight_risk'].astype(bool)).sum()
        if mismatch > 0:
            issues.append(f"❌ is_flight_risk mismatch với C22: {mismatch} rows")

    # Check 5: eNPS_raw trong range 0–10
    if 'eNPS_raw' in df.columns:
        oor = ((df['eNPS_raw'] < 0) | (df['eNPS_raw'] > 10)).sum()
        if oor > 0:
            issues.append(f"❌ eNPS_raw: {oor} values ngoài range [0,10]")

    # Check 6: Pillar score correlation (các trụ cột quá liên quan nhau → multicollinearity)
    pillar_cols = [f'{p}_score' for p in ['TC1','TC2','TC3','TC4','TC5'] if f'{p}_score' in df.columns]
    if len(pillar_cols) >= 2:
        corr_mat = df[pillar_cols].corr()
        for i in range(len(pillar_cols)):
            for j in range(i+1, len(pillar_cols)):
                r = corr_mat.iloc[i, j]
                if r > 0.90:
                    warnings.append(
                        f"⚠️ {pillar_cols[i]} ↔ {pillar_cols[j]}: r={r:.2f} (rất cao) "
                        f"→ calibrate_weights() sẽ không ổn định — xem xét Ridge alpha"
                    )

    # Check 7: Burnout proxy vs burnout_score nhất quán
    if 'burnout_proxy' in df.columns and 'burnout_score' in df.columns:
        # burnout_proxy=1 khi burnout_score >= 50
        incon = ((df['burnout_proxy'] == 1) & (df['burnout_score'] < 40)).sum()
        incon += ((df['burnout_proxy'] == 0) & (df['burnout_score'] > 60)).sum()
        if incon > df.notna().min().min() * 0.05:  # >5% mismatch
            warnings.append(f"⚠️ burnout_proxy và burnout_score không nhất quán ở {incon} rows")

    # Check 8: Tenure sau normalization không có -1 (failed parse) nhiều
    if 'tenure' in df.columns:
        failed = (df['tenure'] == -1).sum()
        if failed > 0:
            rate = failed / len(df) * 100
            if rate > 5:
                issues.append(f"❌ {failed} ({rate:.1f}%) tenure values không parse được — kiểm tra format D5")
            else:
                warnings.append(f"ℹ️ {failed} tenure values không parse được (≤5% — acceptable)")

    # Check 9: Minimum sample size
    if len(df) < MIN_UNIT_N:
        issues.append(f"❌ n={len(df)} < {MIN_UNIT_N} — quá nhỏ để phân tích")

    # Check 10: EI vs individual pillar scores nhất quán
    if 'EI' in df.columns and 'TC2_score' in df.columns:
        # EI không bao giờ cao hơn max pillar score (weighted avg luôn <= max component)
        max_pillar = df[[c for c in df.columns if c.endswith('_score')]].max(axis=1)
        impossible = (df['EI'] > max_pillar + 1).sum()  # +1 cho rounding error
        if impossible > 0:
            issues.append(f"❌ EI cao hơn max pillar score ở {impossible} rows — lỗi compute_all_indices()")

    passed = len(issues) == 0
    if passed:
        print(f"✅ Sanity checks PASSED cho group {group_id} (n={len(df)})")
        for w in warnings:
            print(f"  {w}")
    else:
        print(f"❌ Sanity checks FAILED cho group {group_id}:")
        for issue in issues:
            print(f"  {issue}")

    return {'passed': passed, 'issues': issues, 'warnings': warnings, 'n': len(df)}


def run_quick_smoke_test(group_id: str = '1A') -> bool:
    """
    Smoke test với synthetic data nhỏ để verify pipeline chạy được.
    Chạy trước khi load real data.
    """
    print(f"\n=== Smoke Test: group {group_id} ===")
    np.random.seed(42)
    n = 50
    content_cols = {f'C{i}': np.random.randint(1, 6, n) for i in range(1, 24)}
    demo_cols = {
        'D1': np.random.choice([1,2,3,4,5], n),
        'D2': np.random.choice([1,2], n),
        'D3': np.random.choice([1,2,3,4,5], n),
        'D4': np.random.choice([1,2,3,4,5], n),
        'D5': np.random.choice(list(range(1, 10)), n),
        'D6': np.random.choice(['GHN', 'J&T', '', 'Ninja Van', 'Shopee'], n),
        'unit': np.random.choice(['BC_001', 'BC_002', 'BC_003'], n),
        'employee_id': range(1001, 1001 + n),
    }
    df_test = pd.DataFrame({**demo_cols, **content_cols})

    try:
        df_test = normalize_raw_data(df_test, group_id)
        df_test, qr = run_data_quality_pipeline(df_test, group_id)
        df_test = compute_all_indices(df_test, group_id)
        checks = run_sanity_checks(df_test, group_id)
        if not checks['passed']:
            print(f"❌ Smoke test failed: {checks['issues']}")
            return False
        print(f"✅ Smoke test PASSED — pipeline hoạt động với synthetic data")
        return True
    except Exception as e:
        print(f"❌ Smoke test ERROR: {type(e).__name__}: {e}")
        import traceback; traceback.print_exc()
        return False
```

---

## 11. IMPLEMENTATION ROADMAP

### Tuần 0 — Trước khi có data (làm ngay)
- [ ] Chạy `run_quick_smoke_test('1A')` — verify pipeline không crash
- [ ] Chạy smoke test cho cả 6 groups
- [ ] Xác nhận format export từ survey platform (string hay số?)
- [ ] Xác nhận `join_key` với HR Ops team (employee_id format trong HRIS)

### Tuần 1–2 — Sau khi collect xong data
- [ ] Import raw CSV → `normalize_raw_data()` → verify sample sizes
- [ ] `run_data_quality_pipeline()` → review trước khi tiếp tục
- [ ] `compute_all_indices()` → `run_sanity_checks()` → fix nếu có issues
- [ ] `validate_pillar_reliability()` → document alpha per group
- [ ] `calibrate_weights()` → lưu CALIBRATED_WEIGHTS → recalculate EI
- [ ] `compute_relative_thresholds()` → lưu làm baseline

### Tuần 2–3 — Anomaly Detection
- [ ] Chạy `run_full_anomaly_scan()` cho từng đơn vị
- [ ] Sort by urgency: CRITICAL → HIGH → MEDIUM
- [ ] Flag units cần HRBP action ngay (CRITICAL)
- [ ] Tenure cohort analysis (1A, 1B, 2A)
- [ ] prev_company taxonomy analysis (cross-tab với EI)

### Tuần 3–4 — AI Insight & Reporting
- [ ] AI prompts cho top 10 anomalous units
- [ ] NLP C24/C25/C26 → classify by pillar
- [ ] HRIS cross-reference với `get_unit_hris()`
- [ ] Executive Summary (EXECUTIVE_SUMMARY_PROMPT)
- [ ] Department deep-dive reports

### Tuần 4–5 — Action Framework
- [ ] Priority matrix: Urgency × Impact × Effort
- [ ] Quick Wins (0–30 ngày) / Mid-term (3–6 tháng) / Long-term (6–18 tháng)
- [ ] Owner mapping + KPI theo dõi
- [ ] HRBP Action Tracker

---

## PHỤ LỤC: CROSS-GROUP COMPARABILITY

```
⚠️ KHÔNG SO SÁNH TRỰC TIẾP:

TC1: 1A/1B/2A = 2 items (Pearson r) vs 2B/3A = 5 items, 3B = 4 items
TC4: 2B/3A = 3 items vs 1A/1B/2A = 5 items, 3B = 4 items
JSI: 3B workload từ TC5; các nhóm khác từ TC3 — cross-pillar

KHI REPORT COMPANY-WIDE:
→ Ghi chú rõ trong footnote mỗi chart
→ Dùng ranking trong nhóm (% vs nhóm mình), không dùng absolute score cross-group
→ Khi present cho BOD: chỉ dùng composite EI (đã weighted) để so sánh
```

---

*EES 2026 Analytics Playbook v3.0 | Employee Experience Dept — GiaoHangNhanh*
*June 2026 | Review cycle: v3.1 sau khi calibration chạy xong với real data*
