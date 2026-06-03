"""
CODEBOOK – EES 2026
Bảng mã chuẩn cho toàn bộ 06 nhóm nhân sự.
Hiện tại triển khai cho Nhóm 1A (Shipper/NVPTTT) và Nhóm 1B (Tài xế GXT/TXXT).
"""

# ============================================================
# 1. MAPPING MÃ HÓA TỪ APP QUIZ → GIÁ TRỊ SỐ
# ============================================================

# Likert 1-5 (Câu 9-30): A=1, B=2, C=3, D=4, E=5, F=missing
LIKERT_CODE_MAP = {
    'A': 1, 'B': 2, 'C': 3, 'D': 4, 'E': 5,
    '1 - Rất không đồng ý': 1,
    '2 - Không đồng ý': 2,
    '3 - Trung lập': 3,
    '4 - Đồng ý': 4,
    '5 - Rất đồng ý': 5,
    'F': None,  # Bỏ trống / Không chọn
}

# eNPS 1-10 (Câu 31): A=1, B=2, ..., I=9, J=10 (theo sheet mapping chính thức)
ENPS_CODE_MAP = {
    'A': 1, 'B': 2, 'C': 3, 'D': 4, 'E': 5,
    'F': 6, 'G': 7, 'H': 8, 'I': 9, 'J': 10,
}
# eNPS cũng có dạng numeric (float) → giữ nguyên

# ============================================================
# 2. TRỌNG SỐ TRỤ CỘT
# ============================================================

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



PILLAR_WEIGHTS = {
    'TC1': 0.15,  # Niềm tin & Định hướng
    'TC2': 0.25,  # Quản lý Trực tiếp
    'TC3': 0.20,  # Môi trường & Công cụ Làm việc
    'TC4': 0.20,  # Đãi ngộ & Công bằng
    'TC5': 0.20,  # Văn hóa & Tự hào
}

# Phân loại Chỉ số Gắn kết
EI_CLASSIFICATION = {
    'Xuất sắc': (80, 100),
    'Khỏe mạnh': (65, 79.99),
    'Cần theo dõi': (50, 64.99),
    'Nghiêm trọng': (0, 49.99),
}

# ============================================================
# 3. CODEBOOK NHÓM 1A – 34 câu hỏi
# ============================================================

CODEBOOK_1A = {
    # --- Nhân khẩu học (Câu 1-8) ---
    'Q1':  {'col_idx': 15, 'tên': 'Năm sinh', 'loại': 'nhân_khẩu', 'trụ_cột': None},
    'Q2':  {'col_idx': 16, 'tên': 'Giới tính', 'loại': 'nhân_khẩu', 'trụ_cột': None},
    'Q3':  {'col_idx': 17, 'tên': 'Tình trạng hôn nhân', 'loại': 'nhân_khẩu', 'trụ_cột': None},
    'Q4':  {'col_idx': 18, 'tên': 'Trình độ học vấn', 'loại': 'nhân_khẩu', 'trụ_cột': None},
    'Q5':  {'col_idx': 19, 'tên': 'Thâm niên tự khai', 'loại': 'nhân_khẩu', 'trụ_cột': None},
    'Q6':  {'col_idx': 20, 'tên': 'Công việc trước GHN', 'loại': 'nhân_khẩu', 'trụ_cột': None},
    'Q7':  {'col_idx': 21, 'tên': 'Quà BTC', 'loại': 'nhân_khẩu', 'trụ_cột': None},
    'Q8':  {'col_idx': 22, 'tên': 'Size áo', 'loại': 'nhân_khẩu', 'trụ_cột': None},

    # --- TC1: Niềm tin & Định hướng ---
    'Q9':  {'col_idx': 23, 'tên': 'Tin GHN đúng hướng', 'loại': 'likert', 'trụ_cột': 'TC1'},
    'Q10': {'col_idx': 24, 'tên': 'Thông báo thay đổi kịp thời', 'loại': 'likert', 'trụ_cột': 'TC1'},

    # --- TC2: Quản lý Trực tiếp ---
    'Q11': {'col_idx': 25, 'tên': 'AM/TBC hỗ trợ kịp thời', 'loại': 'likert', 'trụ_cột': 'TC2'},
    'Q12': {'col_idx': 26, 'tên': 'Phân đơn công bằng', 'loại': 'likert', 'trụ_cột': 'TC2'},
    'Q13': {'col_idx': 27, 'tên': 'Biết quy trình xử lý sự cố', 'loại': 'likert', 'trụ_cột': 'TC2'},
    'Q14': {'col_idx': 28, 'tên': 'QL xử lý công bằng', 'loại': 'likert', 'trụ_cột': 'TC2'},
    'Q15': {'col_idx': 29, 'tên': 'Phản hồi làm tốt/cần cải thiện', 'loại': 'likert', 'trụ_cột': 'TC2'},

    # --- TC3: Môi trường & Công cụ ---
    'Q16': {'col_idx': 30, 'tên': 'App Driver ổn định', 'loại': 'likert', 'trụ_cột': 'TC3'},
    'Q17': {'col_idx': 31, 'tên': 'Đủ công cụ/phương tiện', 'loại': 'likert', 'trụ_cột': 'TC3'},
    'Q18': {'col_idx': 32, 'tên': 'Cường độ duy trì được', 'loại': 'likert', 'trụ_cột': 'TC3'},
    'Q19': {'col_idx': 33, 'tên': 'Lộ trình thăng tiến', 'loại': 'likert', 'trụ_cột': 'TC3'},
    'Q20': {'col_idx': 34, 'tên': 'Hướng dẫn khi thay đổi quy trình', 'loại': 'likert', 'trụ_cột': 'TC3'},

    # --- TC4: Đãi ngộ & Công bằng ---
    'Q21': {'col_idx': 35, 'tên': 'Thu nhập phản ánh công sức', 'loại': 'likert', 'trụ_cột': 'TC4'},
    'Q22': {'col_idx': 36, 'tên': 'App hiển thị rõ phạt/thu nhập', 'loại': 'likert', 'trụ_cột': 'TC4'},
    'Q23': {'col_idx': 37, 'tên': 'Hiểu cách tính thu nhập', 'loại': 'likert', 'trụ_cột': 'TC4'},
    'Q24': {'col_idx': 38, 'tên': 'Phân đơn khu vực hợp lý', 'loại': 'likert', 'trụ_cột': 'TC4'},
    'Q25': {'col_idx': 39, 'tên': 'Hỗ trợ sự cố ảnh hưởng thu nhập', 'loại': 'likert', 'trụ_cột': 'TC4'},

    # --- TC5: Văn hóa & Tự hào ---
    'Q26': {'col_idx': 40, 'tên': 'An toàn giao thông', 'loại': 'likert', 'trụ_cột': 'TC5'},
    'Q27': {'col_idx': 41, 'tên': 'Đồng nghiệp hỗ trợ', 'loại': 'likert', 'trụ_cột': 'TC5'},
    'Q28': {'col_idx': 42, 'tên': 'Tự hào là shipper GHN', 'loại': 'likert', 'trụ_cột': 'TC5'},
    'Q29': {'col_idx': 43, 'tên': 'Áp lực không ảnh hưởng cuộc sống', 'loại': 'likert', 'trụ_cột': 'TC5'},

    # --- Chỉ số đặc biệt ---
    'Q30': {'col_idx': 44, 'tên': 'Ý định ở lại 3 tháng', 'loại': 'intent', 'trụ_cột': None},
    'Q31': {'col_idx': 45, 'tên': 'eNPS (1-10)', 'loại': 'enps', 'trụ_cột': None},

    # --- Câu hỏi mở ---
    'Q32': {'col_idx': 46, 'tên': 'Thích nhất khi làm shipper', 'loại': 'open', 'trụ_cột': None},
    'Q33': {'col_idx': 47, 'tên': 'Điều giúp gắn bó', 'loại': 'open', 'trụ_cột': None},
    'Q34': {'col_idx': 48, 'tên': 'Cần thay đổi/cải thiện', 'loại': 'open', 'trụ_cột': None},
}

# ============================================================
# 4. CODEBOOK NHÓM 1B – 34 câu hỏi
# ============================================================

CODEBOOK_1B = {
    # --- Nhân khẩu học ---
    'Q1':  {'col_idx': 15, 'tên': 'Năm sinh', 'loại': 'nhân_khẩu', 'trụ_cột': None},
    'Q2':  {'col_idx': 16, 'tên': 'Giới tính', 'loại': 'nhân_khẩu', 'trụ_cột': None},
    'Q3':  {'col_idx': 17, 'tên': 'Tình trạng hôn nhân', 'loại': 'nhân_khẩu', 'trụ_cột': None},
    'Q4':  {'col_idx': 18, 'tên': 'Trình độ học vấn', 'loại': 'nhân_khẩu', 'trụ_cột': None},
    'Q5':  {'col_idx': 19, 'tên': 'Thâm niên tự khai', 'loại': 'nhân_khẩu', 'trụ_cột': None},
    'Q6':  {'col_idx': 20, 'tên': 'Công việc trước GHN', 'loại': 'nhân_khẩu', 'trụ_cột': None},
    'Q7':  {'col_idx': 21, 'tên': 'Quà BTC', 'loại': 'nhân_khẩu', 'trụ_cột': None},
    'Q8':  {'col_idx': 22, 'tên': 'Size áo', 'loại': 'nhân_khẩu', 'trụ_cột': None},

    # --- TC1: Niềm tin & Định hướng ---
    'Q9':  {'col_idx': 23, 'tên': 'Tin GHN phát triển bền vững', 'loại': 'likert', 'trụ_cột': 'TC1'},
    'Q10': {'col_idx': 24, 'tên': 'Thông báo thay đổi kịp thời', 'loại': 'likert', 'trụ_cột': 'TC1'},

    # --- TC2: Quản lý Trực tiếp (Điều phối viên) ---
    'Q11': {'col_idx': 25, 'tên': 'ĐPV giải quyết nhanh', 'loại': 'likert', 'trụ_cột': 'TC2'},
    'Q12': {'col_idx': 26, 'tên': 'Lịch chạy phân bổ công bằng', 'loại': 'likert', 'trụ_cột': 'TC2'},
    'Q13': {'col_idx': 27, 'tên': 'Nhận đủ thông tin trước chuyến', 'loại': 'likert', 'trụ_cột': 'TC2'},
    'Q14': {'col_idx': 28, 'tên': 'ĐPV xử lý công bằng', 'loại': 'likert', 'trụ_cột': 'TC2'},
    'Q15': {'col_idx': 29, 'tên': 'Hỗ trợ sự cố trên đường', 'loại': 'likert', 'trụ_cột': 'TC2'},

    # --- TC3: Môi trường & Công cụ ---
    'Q16': {'col_idx': 30, 'tên': 'Xe đảm bảo an toàn', 'loại': 'likert', 'trụ_cột': 'TC3'},
    'Q17': {'col_idx': 31, 'tên': 'Lịch chạy hợp lý, đủ nghỉ', 'loại': 'likert', 'trụ_cột': 'TC3'},
    'Q18': {'col_idx': 32, 'tên': 'An toàn lao động', 'loại': 'likert', 'trụ_cột': 'TC3'},
    'Q19': {'col_idx': 33, 'tên': 'Lộ trình thăng tiến', 'loại': 'likert', 'trụ_cột': 'TC3'},
    'Q20': {'col_idx': 34, 'tên': 'Hướng dẫn khi thay đổi', 'loại': 'likert', 'trụ_cột': 'TC3'},

    # --- TC4: Đãi ngộ & Công bằng ---
    'Q21': {'col_idx': 35, 'tên': 'Thu nhập phản ánh công sức', 'loại': 'likert', 'trụ_cột': 'TC4'},
    'Q22': {'col_idx': 36, 'tên': 'Hiểu rõ phụ cấp', 'loại': 'likert', 'trụ_cột': 'TC4'},
    'Q23': {'col_idx': 37, 'tên': 'Tuyến phân bổ công bằng', 'loại': 'likert', 'trụ_cột': 'TC4'},
    'Q24': {'col_idx': 38, 'tên': 'Đủ bảo hộ lao động', 'loại': 'likert', 'trụ_cột': 'TC4'},
    'Q25': {'col_idx': 39, 'tên': 'Hỗ trợ sự cố kịp thời', 'loại': 'likert', 'trụ_cột': 'TC4'},

    # --- TC5: Văn hóa & Tự hào ---
    'Q26': {'col_idx': 40, 'tên': 'Đội vận tải hỗ trợ nhau', 'loại': 'likert', 'trụ_cột': 'TC5'},
    'Q27': {'col_idx': 41, 'tên': 'Tự hào là tài xế GHN', 'loại': 'likert', 'trụ_cột': 'TC5'},
    'Q28': {'col_idx': 42, 'tên': 'Áp lực không ảnh hưởng', 'loại': 'likert', 'trụ_cột': 'TC5'},
    'Q29': {'col_idx': 43, 'tên': 'Được tôn trọng', 'loại': 'likert', 'trụ_cột': 'TC5'},

    # --- Chỉ số đặc biệt ---
    'Q30': {'col_idx': 44, 'tên': 'Ý định ở lại 3 tháng', 'loại': 'intent', 'trụ_cột': None},
    'Q31': {'col_idx': 45, 'tên': 'eNPS (1-10)', 'loại': 'enps', 'trụ_cột': None},

    # --- Câu hỏi mở ---
    'Q32': {'col_idx': 46, 'tên': 'Thích nhất khi làm tài xế', 'loại': 'open', 'trụ_cột': None},
    'Q33': {'col_idx': 47, 'tên': 'Điều giúp gắn bó', 'loại': 'open', 'trụ_cột': None},
    'Q34': {'col_idx': 48, 'tên': 'Cần thay đổi/cải thiện', 'loại': 'open', 'trụ_cột': None},
}

# ============================================================
# 5. CỘT METADATA (giống nhau 1A/1B)
# ============================================================

META_COLUMNS = {
    'tên_bài': 0,
    'id_nv': 1,
    'họ_tên': 2,
    'chức_danh': 3,
    'ngày_bắt_đầu': 4,
    'điểm_đạt': 5,
    'id_bưu_cục': 6,
    'tên_bc': 7,
    'tên_tbc': 8,
    'tên_am': 9,
    'vùng': 10,
    'lần_làm_bài': 11,
    'kết_quả': 12,
    'thời_gian_gửi': 13,
    'thời_gian_nộp': 14,
}

# ============================================================
# 6. MAPPING NHÂN KHẨU HỌC
# ============================================================

# ============================================================
# 7. HÀM CHUYỂN ĐỔI
# ============================================================

def decode_likert(value):
    """Chuyển đổi giá trị Likert (code hoặc text) → số 1-5 hoặc None."""
    if value is None:
        return None
    import math
    if isinstance(value, float) and math.isnan(value):
        return None
    if isinstance(value, (int, float)):
        return int(value) if 1 <= value <= 5 else None
    val = str(value).strip()
    return LIKERT_CODE_MAP.get(val, None)


def decode_enps(value):
    """Chuyển đổi giá trị eNPS (code hoặc number) → số 1-10 hoặc None."""
    if value is None:
        return None
    import math
    if isinstance(value, float) and math.isnan(value):
        return None
    if isinstance(value, (int, float)):
        v = int(value)
        return v if 1 <= v <= 10 else None
    val = str(value).strip()
    return ENPS_CODE_MAP.get(val, None)


def decode_intent(value):
    """Chuyển đổi Ý định ở lại (Likert 1-5 hoặc eNPS code lẫn)."""
    if value is None:
        return None
    import math
    if isinstance(value, float) and math.isnan(value):
        return None
    if isinstance(value, (int, float)):
        return int(value) if 1 <= value <= 5 else None
    val = str(value).strip()
    # Intent dùng cùng mapping Likert A-E
    result = LIKERT_CODE_MAP.get(val, None)
    if result is not None:
        return result
    # Nếu là code F-K → đây là eNPS bị lẫn, không phải Intent
    if val in ENPS_CODE_MAP and val not in ('A', 'B', 'C', 'D', 'E'):
        return None  # Đánh dấu missing cho Intent
    return None


def classify_enps(score):
    """Phân loại eNPS: Promoter (9-10), Passive (7-8), Detractor (1-6). Scale 1-10."""
    if score is None:
        return None
    if score >= 9:
        return 'Promoter'
    elif score >= 7:
        return 'Passive'
    else:
        return 'Detractor'


def calc_engagement_pct(mean_likert):
    """Chuẩn hóa điểm Likert trung bình thành phần trăm 0-100."""
    if mean_likert is None:
        return None
    return (mean_likert - 1) / 4 * 100


def classify_ei(ei_score):
    """Phân loại Chỉ số Gắn kết."""
    if ei_score is None:
        return None
    if ei_score >= 80:
        return 'Xuất sắc'
    elif ei_score >= 65:
        return 'Khỏe mạnh'
    elif ei_score >= 50:
        return 'Cần theo dõi'
    else:
        return 'Nghiêm trọng'


# ============================================================
# 7. DEMOGRAPHICS HELPERS
# ============================================================

def classify_generation(birth_year_or_code):
    """Phân loại thế hệ từ năm sinh hoặc code Quiz App."""
    if birth_year_or_code is None:
        return None
    import math
    if isinstance(birth_year_or_code, float) and math.isnan(birth_year_or_code):
        return None

    # Nếu là code A-E → map theo thứ tự
    val = str(birth_year_or_code).strip()
    gen_code_map = {
        'A': 'Trước 1980',  # Trước 1980
        'B': 'Gen X (1980-1989)',
        'C': 'Gen Y (1990-1994)',
        'D': 'Gen Z đời đầu (1995-1999)',
        'E': 'Gen Z (2000+)',
    }
    if val in gen_code_map:
        return gen_code_map[val]

    # Nếu là năm sinh
    try:
        year = int(float(val))
        if year < 1980: return 'Trước 1980'
        elif year < 1990: return 'Gen X (1980-1989)'
        elif year < 1995: return 'Gen Y (1990-1994)'
        elif year < 2000: return 'Gen Z đời đầu (1995-1999)'
        else: return 'Gen Z (2000+)'
    except (ValueError, TypeError):
        return None


def classify_tenure(months):
    """Phân loại thâm niên từ số tháng."""
    if months is None:
        return None
    import math
    if isinstance(months, float) and math.isnan(months):
        return None
    try:
        m = float(months)
    except (ValueError, TypeError):
        return None

    if m < 1: return '< 1 tháng'
    elif m < 3: return '1-3 tháng'
    elif m < 6: return '3-6 tháng'
    elif m < 9: return '6-9 tháng'
    elif m < 12: return '9-12 tháng'
    elif m < 24: return '1-2 năm'
    elif m < 36: return '2-3 năm'
    elif m < 60: return '3-5 năm'
    else: return '> 5 năm'


# ============================================================
# 8. VÙNG MAPPING (cho ees-tracking compatibility)
# ============================================================

VUNG_MAPPING = {
    'HNO': 'Vùng HNO', 'HNO Region': 'Vùng HNO',
    'DSH': 'Vùng DSH', 'DSH Region': 'Vùng DSH',
    'XBG': 'Vùng XBG', 'XBG Region': 'Vùng XBG',
    'DBB': 'Vùng DBB', 'DBB Region': 'Vùng DBB',
    'TBB': 'Vùng TBB', 'TBB Region': 'Vùng TBB',
    'TNT': 'Vùng TNT', 'TNT Region': 'Vùng TNT',
    'BTB': 'Vùng BTB', 'BTB Region': 'Vùng BTB',
    'TTB': 'Vùng TTB', 'TTB Region': 'Vùng TTB',
    'NTB': 'Vùng NTB', 'NTB Region': 'Vùng NTB',
    'TNG': 'Vùng TNG', 'TNG Region': 'Vùng TNG',
    'HCM': 'Vùng HCM', 'HCM Region': 'Vùng HCM',
    'DNB': 'Vùng DNB', 'DNB Region': 'Vùng DNB',
    'TNB': 'Vùng TNB', 'TNB Region': 'Vùng TNB',
    'ĐCL': 'Vùng ĐCL', 'ĐCL Region': 'Vùng ĐCL',
}


# ============================================================
# CODEBOOK NHÓM 2A, 2B, 3A, 3B (Auto-generated mapping)
# ============================================================

CODEBOOK_2A = {
    'Q1': {'col_idx': 1, 'tên': 'Năm sinh', 'loại': 'nhân_khẩu', 'trụ_cột': None},
    'Q2': {'col_idx': 2, 'tên': 'Giới tính', 'loại': 'nhân_khẩu', 'trụ_cột': None},
    'Q5': {'col_idx': 5, 'tên': 'Thâm niên', 'loại': 'nhân_khẩu', 'trụ_cột': None},
    'Q9': {'col_idx': 13, 'tên': 'Câu hỏi 1', 'loại': 'likert', 'trụ_cột': 'TC1'},
    'Q10': {'col_idx': 14, 'tên': 'Câu hỏi 2', 'loại': 'likert', 'trụ_cột': 'TC1'},
    'Q11': {'col_idx': 15, 'tên': 'Câu hỏi 3', 'loại': 'likert', 'trụ_cột': 'TC1'},
    'Q12': {'col_idx': 16, 'tên': 'Câu hỏi 4', 'loại': 'likert', 'trụ_cột': 'TC1'},
    'Q13': {'col_idx': 17, 'tên': 'Câu hỏi 5', 'loại': 'likert', 'trụ_cột': 'TC2'},
    'Q14': {'col_idx': 18, 'tên': 'Câu hỏi 6', 'loại': 'likert', 'trụ_cột': 'TC2'},
    'Q15': {'col_idx': 19, 'tên': 'Câu hỏi 7', 'loại': 'likert', 'trụ_cột': 'TC2'},
    'Q16': {'col_idx': 20, 'tên': 'Câu hỏi 8', 'loại': 'likert', 'trụ_cột': 'TC2'},
    'Q17': {'col_idx': 21, 'tên': 'Câu hỏi 9', 'loại': 'likert', 'trụ_cột': 'TC2'},
    'Q18': {'col_idx': 22, 'tên': 'Câu hỏi 10', 'loại': 'likert', 'trụ_cột': 'TC3'},
    'Q19': {'col_idx': 23, 'tên': 'Câu hỏi 11', 'loại': 'likert', 'trụ_cột': 'TC3'},
    'Q20': {'col_idx': 24, 'tên': 'Câu hỏi 12', 'loại': 'likert', 'trụ_cột': 'TC3'},
    'Q21': {'col_idx': 25, 'tên': 'Câu hỏi 13', 'loại': 'likert', 'trụ_cột': 'TC3'},
    'Q22': {'col_idx': 26, 'tên': 'Câu hỏi 14', 'loại': 'likert', 'trụ_cột': 'TC4'},
    'Q23': {'col_idx': 27, 'tên': 'Câu hỏi 15', 'loại': 'likert', 'trụ_cột': 'TC4'},
    'Q24': {'col_idx': 28, 'tên': 'Câu hỏi 16', 'loại': 'likert', 'trụ_cột': 'TC4'},
    'Q25': {'col_idx': 29, 'tên': 'Câu hỏi 17', 'loại': 'likert', 'trụ_cột': 'TC4'},
    'Q26': {'col_idx': 30, 'tên': 'Câu hỏi 18', 'loại': 'likert', 'trụ_cột': 'TC5'},
    'Q27': {'col_idx': 31, 'tên': 'Câu hỏi 19', 'loại': 'likert', 'trụ_cột': 'TC5'},
    'Q28': {'col_idx': 32, 'tên': 'Câu hỏi 20', 'loại': 'likert', 'trụ_cột': 'TC5'},
    'Q29': {'col_idx': 33, 'tên': 'Câu hỏi 21', 'loại': 'likert', 'trụ_cột': 'TC5'},
    'Q30': {'col_idx': 34, 'tên': 'Ý định ở lại', 'loại': 'intent', 'trụ_cột': None},
    'Q31': {'col_idx': 35, 'tên': 'eNPS', 'loại': 'enps', 'trụ_cột': None},
    'Q32': {'col_idx': 36, 'tên': 'Thích nhất', 'loại': 'open', 'trụ_cột': None},
    'Q33': {'col_idx': 37, 'tên': 'Giúp gắn bó', 'loại': 'open', 'trụ_cột': None},
    'Q34': {'col_idx': 38, 'tên': 'Cần cải thiện', 'loại': 'open', 'trụ_cột': None},
}

CODEBOOK_2B = {
    'Q1': {'col_idx': 1, 'tên': 'Năm sinh', 'loại': 'nhân_khẩu', 'trụ_cột': None},
    'Q2': {'col_idx': 2, 'tên': 'Giới tính', 'loại': 'nhân_khẩu', 'trụ_cột': None},
    'Q5': {'col_idx': 5, 'tên': 'Thâm niên', 'loại': 'nhân_khẩu', 'trụ_cột': None},
    'Q9': {'col_idx': 13, 'tên': 'Câu hỏi 1', 'loại': 'likert', 'trụ_cột': 'TC1'},
    'Q10': {'col_idx': 14, 'tên': 'Câu hỏi 2', 'loại': 'likert', 'trụ_cột': 'TC1'},
    'Q11': {'col_idx': 15, 'tên': 'Câu hỏi 3', 'loại': 'likert', 'trụ_cột': 'TC1'},
    'Q12': {'col_idx': 16, 'tên': 'Câu hỏi 4', 'loại': 'likert', 'trụ_cột': 'TC1'},
    'Q13': {'col_idx': 17, 'tên': 'Câu hỏi 5', 'loại': 'likert', 'trụ_cột': 'TC2'},
    'Q14': {'col_idx': 18, 'tên': 'Câu hỏi 6', 'loại': 'likert', 'trụ_cột': 'TC2'},
    'Q15': {'col_idx': 19, 'tên': 'Câu hỏi 7', 'loại': 'likert', 'trụ_cột': 'TC2'},
    'Q16': {'col_idx': 20, 'tên': 'Câu hỏi 8', 'loại': 'likert', 'trụ_cột': 'TC2'},
    'Q17': {'col_idx': 21, 'tên': 'Câu hỏi 9', 'loại': 'likert', 'trụ_cột': 'TC2'},
    'Q18': {'col_idx': 22, 'tên': 'Câu hỏi 10', 'loại': 'likert', 'trụ_cột': 'TC3'},
    'Q19': {'col_idx': 23, 'tên': 'Câu hỏi 11', 'loại': 'likert', 'trụ_cột': 'TC3'},
    'Q20': {'col_idx': 24, 'tên': 'Câu hỏi 12', 'loại': 'likert', 'trụ_cột': 'TC3'},
    'Q21': {'col_idx': 25, 'tên': 'Câu hỏi 13', 'loại': 'likert', 'trụ_cột': 'TC3'},
    'Q22': {'col_idx': 26, 'tên': 'Câu hỏi 14', 'loại': 'likert', 'trụ_cột': 'TC4'},
    'Q23': {'col_idx': 27, 'tên': 'Câu hỏi 15', 'loại': 'likert', 'trụ_cột': 'TC4'},
    'Q24': {'col_idx': 28, 'tên': 'Câu hỏi 16', 'loại': 'likert', 'trụ_cột': 'TC4'},
    'Q25': {'col_idx': 29, 'tên': 'Câu hỏi 17', 'loại': 'likert', 'trụ_cột': 'TC4'},
    'Q26': {'col_idx': 30, 'tên': 'Câu hỏi 18', 'loại': 'likert', 'trụ_cột': 'TC5'},
    'Q27': {'col_idx': 31, 'tên': 'Câu hỏi 19', 'loại': 'likert', 'trụ_cột': 'TC5'},
    'Q28': {'col_idx': 32, 'tên': 'Câu hỏi 20', 'loại': 'likert', 'trụ_cột': 'TC5'},
    'Q29': {'col_idx': 33, 'tên': 'Câu hỏi 21', 'loại': 'likert', 'trụ_cột': 'TC5'},
    'Q30': {'col_idx': 34, 'tên': 'Ý định ở lại', 'loại': 'intent', 'trụ_cột': None},
    'Q31': {'col_idx': 35, 'tên': 'eNPS', 'loại': 'enps', 'trụ_cột': None},
    'Q32': {'col_idx': 36, 'tên': 'Thích nhất', 'loại': 'open', 'trụ_cột': None},
    'Q33': {'col_idx': 37, 'tên': 'Giúp gắn bó', 'loại': 'open', 'trụ_cột': None},
    'Q34': {'col_idx': 38, 'tên': 'Cần cải thiện', 'loại': 'open', 'trụ_cột': None},
}

CODEBOOK_3A = {
    'Q1': {'col_idx': 1, 'tên': 'Năm sinh', 'loại': 'nhân_khẩu', 'trụ_cột': None},
    'Q2': {'col_idx': 2, 'tên': 'Giới tính', 'loại': 'nhân_khẩu', 'trụ_cột': None},
    'Q5': {'col_idx': 5, 'tên': 'Thâm niên', 'loại': 'nhân_khẩu', 'trụ_cột': None},
    'Q9': {'col_idx': 15, 'tên': 'Câu hỏi 1', 'loại': 'likert', 'trụ_cột': 'TC1'},
    'Q10': {'col_idx': 16, 'tên': 'Câu hỏi 2', 'loại': 'likert', 'trụ_cột': 'TC1'},
    'Q11': {'col_idx': 17, 'tên': 'Câu hỏi 3', 'loại': 'likert', 'trụ_cột': 'TC1'},
    'Q12': {'col_idx': 18, 'tên': 'Câu hỏi 4', 'loại': 'likert', 'trụ_cột': 'TC1'},
    'Q13': {'col_idx': 19, 'tên': 'Câu hỏi 5', 'loại': 'likert', 'trụ_cột': 'TC2'},
    'Q14': {'col_idx': 20, 'tên': 'Câu hỏi 6', 'loại': 'likert', 'trụ_cột': 'TC2'},
    'Q15': {'col_idx': 21, 'tên': 'Câu hỏi 7', 'loại': 'likert', 'trụ_cột': 'TC2'},
    'Q16': {'col_idx': 22, 'tên': 'Câu hỏi 8', 'loại': 'likert', 'trụ_cột': 'TC2'},
    'Q17': {'col_idx': 23, 'tên': 'Câu hỏi 9', 'loại': 'likert', 'trụ_cột': 'TC2'},
    'Q18': {'col_idx': 24, 'tên': 'Câu hỏi 10', 'loại': 'likert', 'trụ_cột': 'TC3'},
    'Q19': {'col_idx': 25, 'tên': 'Câu hỏi 11', 'loại': 'likert', 'trụ_cột': 'TC3'},
    'Q20': {'col_idx': 26, 'tên': 'Câu hỏi 12', 'loại': 'likert', 'trụ_cột': 'TC3'},
    'Q21': {'col_idx': 27, 'tên': 'Câu hỏi 13', 'loại': 'likert', 'trụ_cột': 'TC3'},
    'Q22': {'col_idx': 28, 'tên': 'Câu hỏi 14', 'loại': 'likert', 'trụ_cột': 'TC4'},
    'Q23': {'col_idx': 29, 'tên': 'Câu hỏi 15', 'loại': 'likert', 'trụ_cột': 'TC4'},
    'Q24': {'col_idx': 30, 'tên': 'Câu hỏi 16', 'loại': 'likert', 'trụ_cột': 'TC4'},
    'Q25': {'col_idx': 31, 'tên': 'Câu hỏi 17', 'loại': 'likert', 'trụ_cột': 'TC4'},
    'Q26': {'col_idx': 32, 'tên': 'Câu hỏi 18', 'loại': 'likert', 'trụ_cột': 'TC5'},
    'Q27': {'col_idx': 33, 'tên': 'Câu hỏi 19', 'loại': 'likert', 'trụ_cột': 'TC5'},
    'Q28': {'col_idx': 34, 'tên': 'Câu hỏi 20', 'loại': 'likert', 'trụ_cột': 'TC5'},
    'Q29': {'col_idx': 35, 'tên': 'Câu hỏi 21', 'loại': 'likert', 'trụ_cột': 'TC5'},
    'Q30': {'col_idx': 36, 'tên': 'Ý định ở lại', 'loại': 'intent', 'trụ_cột': None},
    'Q31': {'col_idx': 37, 'tên': 'eNPS', 'loại': 'enps', 'trụ_cột': None},
    'Q32': {'col_idx': 38, 'tên': 'Thích nhất', 'loại': 'open', 'trụ_cột': None},
    'Q33': {'col_idx': 39, 'tên': 'Giúp gắn bó', 'loại': 'open', 'trụ_cột': None},
    'Q34': {'col_idx': 40, 'tên': 'Cần cải thiện', 'loại': 'open', 'trụ_cột': None},
}

CODEBOOK_3B = {
    'Q1': {'col_idx': 1, 'tên': 'Năm sinh', 'loại': 'nhân_khẩu', 'trụ_cột': None},
    'Q2': {'col_idx': 2, 'tên': 'Giới tính', 'loại': 'nhân_khẩu', 'trụ_cột': None},
    'Q5': {'col_idx': 5, 'tên': 'Thâm niên', 'loại': 'nhân_khẩu', 'trụ_cột': None},
    'Q9': {'col_idx': 15, 'tên': 'Câu hỏi 1', 'loại': 'likert', 'trụ_cột': 'TC1'},
    'Q10': {'col_idx': 16, 'tên': 'Câu hỏi 2', 'loại': 'likert', 'trụ_cột': 'TC1'},
    'Q11': {'col_idx': 17, 'tên': 'Câu hỏi 3', 'loại': 'likert', 'trụ_cột': 'TC1'},
    'Q12': {'col_idx': 18, 'tên': 'Câu hỏi 4', 'loại': 'likert', 'trụ_cột': 'TC1'},
    'Q13': {'col_idx': 19, 'tên': 'Câu hỏi 5', 'loại': 'likert', 'trụ_cột': 'TC2'},
    'Q14': {'col_idx': 20, 'tên': 'Câu hỏi 6', 'loại': 'likert', 'trụ_cột': 'TC2'},
    'Q15': {'col_idx': 21, 'tên': 'Câu hỏi 7', 'loại': 'likert', 'trụ_cột': 'TC2'},
    'Q16': {'col_idx': 22, 'tên': 'Câu hỏi 8', 'loại': 'likert', 'trụ_cột': 'TC2'},
    'Q17': {'col_idx': 23, 'tên': 'Câu hỏi 9', 'loại': 'likert', 'trụ_cột': 'TC2'},
    'Q18': {'col_idx': 24, 'tên': 'Câu hỏi 10', 'loại': 'likert', 'trụ_cột': 'TC3'},
    'Q19': {'col_idx': 25, 'tên': 'Câu hỏi 11', 'loại': 'likert', 'trụ_cột': 'TC3'},
    'Q20': {'col_idx': 26, 'tên': 'Câu hỏi 12', 'loại': 'likert', 'trụ_cột': 'TC3'},
    'Q21': {'col_idx': 27, 'tên': 'Câu hỏi 13', 'loại': 'likert', 'trụ_cột': 'TC3'},
    'Q22': {'col_idx': 28, 'tên': 'Câu hỏi 14', 'loại': 'likert', 'trụ_cột': 'TC4'},
    'Q23': {'col_idx': 29, 'tên': 'Câu hỏi 15', 'loại': 'likert', 'trụ_cột': 'TC4'},
    'Q24': {'col_idx': 30, 'tên': 'Câu hỏi 16', 'loại': 'likert', 'trụ_cột': 'TC4'},
    'Q25': {'col_idx': 31, 'tên': 'Câu hỏi 17', 'loại': 'likert', 'trụ_cột': 'TC4'},
    'Q26': {'col_idx': 32, 'tên': 'Câu hỏi 18', 'loại': 'likert', 'trụ_cột': 'TC5'},
    'Q27': {'col_idx': 33, 'tên': 'Câu hỏi 19', 'loại': 'likert', 'trụ_cột': 'TC5'},
    'Q28': {'col_idx': 34, 'tên': 'Câu hỏi 20', 'loại': 'likert', 'trụ_cột': 'TC5'},
    'Q29': {'col_idx': 35, 'tên': 'Câu hỏi 21', 'loại': 'likert', 'trụ_cột': 'TC5'},
    'Q30': {'col_idx': 36, 'tên': 'Ý định ở lại', 'loại': 'intent', 'trụ_cột': None},
    'Q31': {'col_idx': 37, 'tên': 'eNPS', 'loại': 'enps', 'trụ_cột': None},
    'Q32': {'col_idx': 38, 'tên': 'Thích nhất', 'loại': 'open', 'trụ_cột': None},
    'Q33': {'col_idx': 39, 'tên': 'Giúp gắn bó', 'loại': 'open', 'trụ_cột': None},
    'Q34': {'col_idx': 40, 'tên': 'Cần cải thiện', 'loại': 'open', 'trụ_cột': None},
}


# ============================================================
# 9. PILLAR METADATA & HELPERS
# ============================================================

PILLAR_META = {
    'TC1': {
        'name': 'Niềm tin lãnh đạo',
        'short': 'Niềm tin LĐ',
        'icon': '',
        'color': '#6366F1',
        'description': 'Niềm tin vào Ban Lãnh đạo và định hướng chiến lược của tổ chức',
        'group_descriptions': {
            '1A': 'Niềm tin vào Ban lãnh đạo cấp công ty và sự kịp thời của các thông báo thay đổi.',
            '1B': 'Niềm tin vào định hướng bền vững của Ban lãnh đạo cấp công ty và thông báo kịp thời.',
            '2A': 'Niềm tin vào Ban lãnh đạo cấp công ty và việc truyền thông thay đổi kịp thời.',
            '2B': 'Niềm tin vào BOD/SMT, định hướng chiến lược và sự hỗ trợ kịp thời từ các phòng ban HO (HR, Tech...).',
            '3A': 'Niềm tin vào Senior Leadership, lý do của các quyết định lớn và sự nhất quán trong hành động.',
            '3B': 'Niềm tin vào C-Level/BOD, quyết định dựa trên dữ liệu và không gian chủ động điều hành.'
        }
    },
    'TC2': {
        'name': 'Quản lý trực tiếp (MEI)',
        'short': 'QL trực tiếp',
        'icon': '',
        'color': '#0EA5E9',
        'description': 'Năng lực hỗ trợ, công bằng và phản hồi của quản lý trực tiếp (AM/TBC/Leader)',
        'group_descriptions': {
            '1A': 'Đánh giá AM/TBC/Leader tại bưu cục: hỗ trợ sự cố, phân đơn công bằng, phản hồi thường xuyên.',
            '1B': 'Đánh giá Điều phối viên/Giám sát: giải quyết nhanh vấn đề trên tuyến, phân lịch chạy công bằng.',
            '2A': 'Đánh giá Quản lý Kho/Giám sát: phân ca công bằng, lắng nghe và ra quyết định vì lợi ích chung.',
            '2B': 'Đánh giá Giám đốc Vùng/Khối: giao quyền hạn rõ ràng, tạo an toàn tâm lý (psychological safety).',
            '3A': 'Đánh giá Manager/Trưởng phòng: quan tâm phát triển nghề nghiệp, trao quyền và phản hồi thường xuyên.',
            '3B': 'Đánh giá C-Level & Đồng cấp: nhận phản hồi trung thực, đầu tư coaching và psychological safety upward.'
        }
    },
    'TC3': {
        'name': 'Công việc & phát triển',
        'short': 'CV & Phát triển',
        'icon': '',
        'color': '#F59E0B',
        'description': 'Công cụ, quy trình, lộ trình thăng tiến và điều kiện làm việc hàng ngày',
        'group_descriptions': {
            '1A': 'Đánh giá App Driver, phương tiện/đồng phục và khối lượng đơn hàng (workload bền vững).',
            '1B': 'Đánh giá Xe, an toàn trên tuyến đường và lịch chạy hợp lý (thời gian nghỉ ngơi).',
            '2A': 'Đánh giá PDA, thiết bị kho, quy trình phân loại và khối lượng công việc trong ca.',
            '2B': 'Đánh giá Hệ thống quản lý, tính khả thi của KPI và lộ trình thăng tiến thực tế.',
            '3A': 'Đánh giá Quy trình nội bộ, hệ thống thông tin và hiệu quả phối hợp liên phòng ban.',
            '3B': 'Đánh giá Dữ liệu ra quyết định, cơ cấu tổ chức giảm rào cản và không gian thử nghiệm.'
        }
    },
    'TC4': {
        'name': 'Thu nhập & minh bạch',
        'short': 'Thu nhập & MB',
        'icon': '',
        'color': '#10B981',
        'description': 'Mức thu nhập, cách tính lương, minh bạch phạt/truy thu và hỗ trợ sự cố tài chính',
        'group_descriptions': {
            '1A': 'Sự công bằng của Pay theo đơn, tính minh bạch trên App (phạt/thu nhập) và phân đơn khu vực.',
            '1B': 'Sự công bằng của Pay theo quãng đường, minh bạch phụ cấp (đường dài, ca đêm).',
            '2A': 'Sự công bằng của Pay theo sức lao động, cơ hội tăng ca (OT) được phân bổ đều.',
            '2B': 'Đãi ngộ phản ánh đúng trách nhiệm và cơ hội thăng tiến dựa trên năng lực (merit-based).',
            '3A': 'Đãi ngộ tương xứng đóng góp và chính sách đánh giá hiệu suất minh bạch, rõ ràng.',
            '3B': 'Phân bổ nguồn lực chiến lược (ngân sách, nhân sự) và đãi ngộ xứng đáng với thành tích lãnh đạo.'
        }
    },
    'TC5': {
        'name': 'Môi trường & gắn kết',
        'short': 'Môi trường & GK',
        'icon': '',
        'color': '#EF4444',
        'description': 'An toàn, đồng nghiệp, niềm tự hào và sức khỏe tinh thần',
        'group_descriptions': {
            '1A': 'An toàn giao thông, tinh thần hỗ trợ tại bưu cục và sự Tôn trọng (Dignity) đối với Shipper.',
            '1B': 'An toàn nghề nghiệp, tinh thần hỗ trợ đội xe và sự Tôn trọng đối với Tài xế.',
            '2A': 'Điều kiện vật lý kho (nhiệt độ, bụi), an toàn lao động và sự Tôn trọng đối với NV Kho.',
            '2B': 'Sự phối hợp đồng cấp giữa các QL, niềm tự hào tuyến đầu và Tôn trọng 2 chiều.',
            '3A': 'Văn hóa hợp tác không cạnh tranh tiêu cực, áp lực kiểm soát được và cảm giác thuộc về (Belonging).',
            '3B': 'Khối lượng công việc lãnh đạo (Workload sustainability) và sự phối hợp đồng cấp thực chất.'
        }
    },
}

PILLAR_ORDER = ['TC1', 'TC2', 'TC3', 'TC4', 'TC5']

_CODEBOOK_REGISTRY = {
    '1A': CODEBOOK_1A,
    '1B': CODEBOOK_1B,
    '2A': CODEBOOK_2A,
    '2B': CODEBOOK_2B,
    '3A': CODEBOOK_3A,
    '3B': CODEBOOK_3B,
}

# ============================================================
# 10. SEMANTIC QUESTION-ROLE MAP (theo KE_HOACH_PHAN_TICH_5_TRU_COT)
# ============================================================
#
# Tài liệu KE_HOACH định nghĩa cấu trúc câu hỏi → trụ cột KHÁC NHAU giữa
# nhóm 1A/1B (frontline) và 2A/2B/3A/3B (back office / quản lý):
#
#   | Trụ cột | 1A/1B        | 2A/2B/3A/3B  |
#   |---------|--------------|--------------|
#   | TC1     | Q9-Q10 (2)   | Q9-Q12  (4)  |
#   | TC2     | Q11-Q15 (5)  | Q13-Q17 (5)  |
#   | TC3     | Q16-Q20 (5)  | Q18-Q21 (4)  |
#   | TC4     | Q21-Q25 (5)  | Q22-Q25 (4)  |
#   | TC5     | Q26-Q29 (4)  | Q26-Q29 (4)  |
#
# Vì cùng một "vai trò phân tích" (ví dụ: câu về công cụ, câu về thăng tiến,
# câu về thu nhập...) nằm ở các SỐ CÂU KHÁC NHAU tùy nhóm, engine phân tích
# KHÔNG được hard-code số câu. Thay vào đó, ta tra "vai trò" (role) → mã câu
# theo từng nhóm thông qua bảng dưới đây.
#
# Các vai trò chuẩn (role keys):
#   info_trust       - Tin vào BLĐ/định hướng (TC1)
#   info_timely      - Thông báo thay đổi kịp thời (TC1)
#   mgr_support      - Quản lý trực tiếp hỗ trợ (TC2)
#   mgr_fairness     - Quản lý phân bổ/xử lý công bằng (TC2)
#   mgr_feedback     - Quản lý phản hồi/ghi nhận (TC2)
#   tool             - Công cụ / thiết bị / app (TC3)
#   career           - Lộ trình thăng tiến (TC3)
#   change_guide     - Hướng dẫn khi thay đổi quy trình (TC3)
#   workload         - Cường độ / khối lượng công việc (TC3)
#   income_fair      - Thu nhập phản ánh công sức / công bằng (TC4)
#   transparency     - Minh bạch cách tính / phạt / phụ cấp (TC4)
#   incident_support - Hỗ trợ khi gặp sự cố ảnh hưởng thu nhập (TC4)
#   peer             - Đồng nghiệp / tập thể hỗ trợ (TC5)
#   pride            - Tự hào về tổ chức (TC5)
#   pressure         - Áp lực không ảnh hưởng cuộc sống (TC5)

# Layout 1A — Shipper (TC5: Q26 ATGT, Q27 đồng nghiệp, Q28 tự hào, Q29 áp lực)
_ROLES_1A = {
    'info_trust': 'Q9',  'info_timely': 'Q10',
    'mgr_support': 'Q11', 'mgr_fairness': 'Q12', 'mgr_feedback': 'Q15',
    'tool': 'Q16', 'workload': 'Q18', 'career': 'Q19', 'change_guide': 'Q20',
    'income_fair': 'Q21', 'transparency': 'Q22', 'incident_support': 'Q25',
    'peer': 'Q27', 'pride': 'Q28', 'pressure': 'Q29',
}

# Layout 1B — Tài xế (TC5: Q26 đội xe, Q27 tự hào, Q28 áp lực, Q29 được tôn trọng)
_ROLES_1B = {
    'info_trust': 'Q9',  'info_timely': 'Q10',
    'mgr_support': 'Q11', 'mgr_fairness': 'Q12', 'mgr_feedback': 'Q15',
    'tool': 'Q16', 'workload': 'Q18', 'career': 'Q19', 'change_guide': 'Q20',
    'income_fair': 'Q21', 'transparency': 'Q22', 'incident_support': 'Q25',
    'peer': 'Q26', 'pride': 'Q27', 'pressure': 'Q28',
}

# Layout 2A — NV Vận hành Kho (dùng C-column names khớp với QUESTION_MAP)
_ROLES_2A = {
    'info_trust':   'C1',  'info_timely':  'C2',
    'mgr_support':  'C4',  'mgr_fairness': 'C3',  'mgr_feedback': 'C4',
    'tool':         'C7',  'workload':     'C9',  'career':       'C10',
    'income_fair':  'C12', 'transparency': 'C13',
    'peer':         'C19', 'pride':        None,   'pressure':     'C20',
    'respect':      'C21', 'belonging':    'C21',
}

# Layout 2B — Quản lý Tuyến đầu (dùng C-column names khớp với QUESTION_MAP)
_ROLES_2B = {
    'info_trust':   'C1',  'info_timely':  'C4',
    'mgr_support':  'C6',  'mgr_fairness': 'C7',  'mgr_feedback': 'C9',
    'tool':         'C10', 'workload':     'C12', 'career':       'C13',
    'income_fair':  'C15', 'transparency': 'C17',
    'peer':         'C18', 'pride':        'C19', 'pressure':     'C20',
    'respect':      'C21', 'belonging':    'C19',
}

# Layout 3A — NV Văn phòng / Hỗ trợ HO (dùng C-column names khớp với QUESTION_MAP)
_ROLES_3A = {
    'info_trust':   'C1',  'info_timely':  'C3',
    'mgr_support':  'C8',  'mgr_fairness': 'C7',  'mgr_feedback': 'C8',
    'tool':         'C10', 'workload':     'C14', 'career':       'C13',
    'income_fair':  'C15', 'transparency': 'C17',
    'peer':         'C18', 'pride':        'C20', 'pressure':     'C19',
    'respect':      None,  'belonging':    'C21',
}

# Layout 3B — Manager / Senior Manager / Director HO (dùng C-column names)
_ROLES_3B = {
    'info_trust':   'C1',  'info_timely':  None,
    'mgr_support':  'C6',  'mgr_fairness': 'C5',  'mgr_feedback': 'C6',
    'tool':         'C9',  'workload':     'C18', 'career':       'C13',
    'income_fair':  'C14', 'transparency': 'C16',
    'peer':         'C21', 'pride':        'C20', 'pressure':     'C18',
    'respect':      None,  'belonging':    'C20',
}

PILLAR_QUESTION_ROLES = {
    '1A': _ROLES_1A,
    '1B': _ROLES_1B,
    '2A': _ROLES_2A,
    '2B': _ROLES_2B,
    '3A': _ROLES_3A,
    '3B': _ROLES_3B,
}


def get_role_question(group_id, role):
    """Trả về mã câu hỏi (vd 'Q16') đóng vai trò `role` cho nhóm `group_id`.

    Returns None nếu nhóm/role không tồn tại. Engine phân tích nên dùng hàm này
    thay vì hard-code số câu, để đúng cho cả 6 nhóm.
    """
    return PILLAR_QUESTION_ROLES.get(group_id, _ROLES_1A).get(role)


def get_pillar_description(pillar_id, group_id=None):
    """Return the context-specific pillar description based on the user group."""
    meta = PILLAR_META.get(pillar_id)
    if not meta:
        return ""
    
    if group_id and group_id in meta.get('group_descriptions', {}):
        return meta['group_descriptions'][group_id]
    
    return meta.get('description', '')


def get_codebook(group_id):
    """Return codebook dict for a survey group."""
    return _CODEBOOK_REGISTRY.get(group_id, CODEBOOK_1A)


def get_question_label(group_id, question_id):
    """Return short label for a question. Supports both Q and V3 (C, D) notations."""
    cb = get_codebook(group_id)
    lookup_id = question_id
    if isinstance(question_id, str):
        if question_id.startswith('C') and question_id[1:].isdigit():
            idx = int(question_id[1:])
            lookup_id = f'Q{idx+8}'
        elif question_id.startswith('D') and question_id[1:].isdigit():
            idx = int(question_id[1:])
            lookup_id = f'Q{idx}'
            
    if lookup_id in cb:
        return cb[lookup_id].get('tên', question_id)
    return question_id
