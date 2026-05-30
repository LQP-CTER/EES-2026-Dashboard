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

# Layout back office / quản lý (2A/2B/3A/3B)
# TC5 = Q26-Q29 (generic). Quy ước: Q26 môi trường/đồng nghiệp, Q27 đồng nghiệp/
# phối hợp, Q28 tự hào/thuộc về, Q29 áp lực kiểm soát được.
_ROLES_BACKOFFICE = {
    'info_trust': 'Q9',  'info_timely': 'Q10',
    'mgr_support': 'Q13', 'mgr_fairness': 'Q14', 'mgr_feedback': 'Q17',
    'tool': 'Q18', 'workload': 'Q21', 'career': 'Q21', 'change_guide': 'Q20',
    'income_fair': 'Q22', 'transparency': 'Q23', 'incident_support': 'Q25',
    'peer': 'Q27', 'pride': 'Q28', 'pressure': 'Q29',
}

PILLAR_QUESTION_ROLES = {
    '1A': _ROLES_1A,
    '1B': _ROLES_1B,
    '2A': _ROLES_BACKOFFICE,
    '2B': _ROLES_BACKOFFICE,
    '3A': _ROLES_BACKOFFICE,
    '3B': _ROLES_BACKOFFICE,
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


def get_pillar_questions(group_id, pillar_id):
    """Return list of question codes (Q9, Q10, ...) belonging to a pillar."""
    cb = get_codebook(group_id)
    return [q for q, meta in cb.items() if meta.get('trụ_cột') == pillar_id]


def get_all_likert_questions(group_id):
    """Return all likert question codes (Q9-Q29)."""
    cb = get_codebook(group_id)
    return [q for q, meta in cb.items() if meta.get('loại') == 'likert']


def get_question_label(group_id, question_id):
    """Return short label for a question."""
    cb = get_codebook(group_id)
    if question_id in cb:
        return cb[question_id].get('tên', question_id)
    return question_id
