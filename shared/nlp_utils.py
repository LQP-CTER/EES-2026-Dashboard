"""
NLP UTILITIES – EES 2026
Tiền xử lý ngôn ngữ tự nhiên tiếng Việt cho câu hỏi mở.
"""

import re
import unicodedata
from collections import Counter

# ============================================================
# 1. TỪ ĐIỂN ĐỒNG NGHĨA NGÀNH VẬN CHUYỂN
# ============================================================

SYNONYM_MAP = {
    # Giao hàng
    'ship hàng': 'giao_hàng', 'đi giao': 'giao_hàng', 'giao đơn': 'giao_hàng',
    'giao kiện': 'giao_hàng', 'đi ship': 'giao_hàng', 'giao hàng': 'giao_hàng',
    # Bưu cục
    'bc': 'bưu_cục', 'buu cuc': 'bưu_cục', 'trạm': 'bưu_cục',
    'điểm giao': 'bưu_cục', 'bưu cục': 'bưu_cục',
    # Thu nhập
    'lương': 'thu_nhập', 'tiền': 'thu_nhập', 'đơn giá': 'thu_nhập',
    'thu nhập': 'thu_nhập', 'income': 'thu_nhập', 'luong': 'thu_nhập',
    'lương bổng': 'thu_nhập',
    # Phạt
    'phạt cod': 'phạt', 'truy thu': 'phạt', 'trừ tiền': 'phạt',
    'bị phạt': 'phạt', 'phạt': 'phạt', 'phat': 'phạt',
    # Quản lý
    'sếp': 'quản_lý', 'ql': 'quản_lý', 'trưởng nhóm': 'quản_lý',
    'am': 'quản_lý', 'anh quản lý': 'quản_lý', 'chị quản lý': 'quản_lý',
    'quản lý': 'quản_lý', 'leader': 'quản_lý', 'tbc': 'quản_lý',
    # Ứng dụng
    'app': 'ứng_dụng', 'phần mềm': 'ứng_dụng', 'hệ thống': 'ứng_dụng',
    'tool': 'ứng_dụng', 'ứng dụng': 'ứng_dụng',
    # Đồng nghiệp
    'anh em': 'đồng_nghiệp', 'team': 'đồng_nghiệp', 'nhóm': 'đồng_nghiệp',
    'bạn bè': 'đồng_nghiệp', 'đồng đội': 'đồng_nghiệp', 'đồng nghiệp': 'đồng_nghiệp',
    'ae': 'đồng_nghiệp',
    # Phúc lợi
    'chế độ': 'phúc_lợi', 'bảo hiểm': 'phúc_lợi', 'thưởng': 'phúc_lợi',
    'quyền lợi': 'phúc_lợi', 'phụ cấp': 'phúc_lợi', 'phúc lợi': 'phúc_lợi',
}

# ============================================================
# 2. BẢNG ÁNH XẠ VIẾT TẮT NỘI BỘ
# ============================================================

ABBREVIATION_MAP = {
    'am': 'Area Manager',
    'tbc': 'Trưởng Bưu Cục',
    'bc': 'Bưu Cục',
    'ho': 'Head Office',
    'ktc': 'Kho Trung Chuyển',
    'cod': 'Cash On Delivery',
    'gtc': 'Giao Thành Công',
    'ltc': 'Lấy Thành Công',
    'nvpttt': 'Nhân Viên Phát Triển Thị Trường',
    'gxt': 'Giao Xe Tải',
    'txxt': 'Tài Xế Xe Tải',
    'nvxl': 'Nhân Viên Xử Lý',
    'aov': 'Average Order Value',
    'ghn': 'Giao Hàng Nhanh',
    'nv': 'Nhân Viên',
    'cv': 'Công Việc',
    'lv': 'Làm Việc',
    'tg': 'Thời Gian',
    'mn': 'Mọi Người',
}

# ============================================================
# 3. DANH SÁCH TỪ DỪNG TÙY CHỈNH
# ============================================================

# Giữ lại: "không", "chưa", "thiếu", "ít", "nhiều", "quá", "lắm"
STOP_WORDS = {
    'của', 'và', 'tôi', 'là', 'có', 'được', 'cho', 'với',
    'trong', 'này', 'đó', 'thì', 'để', 'các', 'những',
    'một', 'hay', 'mà', 'khi', 'cũng', 'nên', 'rất',
    'bạn', 'mình', 'em', 'tui', 'ạ', 'nhé', 'nha',
    'vì', 'do', 'tại', 'nếu', 'thì', 'đều', 'sẽ',
    'đang', 'đã', 'vẫn', 'cần', 'phải', 'nào',
}

# ============================================================
# 4. TỪ ĐIỂN TÍN HIỆU CẢNH BÁO SỚM
# ============================================================

WARNING_SIGNALS = {
    'ý_định_nghỉ': [
        'sắp nghỉ', 'đang tìm chỗ khác', 'không ở lâu', 'nghỉ việc',
        'tìm việc khác', 'chuyển công ty', 'không gắn bó', 'muốn nghỉ',
        'sắp đi', 'không tiếp tục', 'tính nghỉ', 'đang nghĩ đến nghỉ',
    ],
    'kiệt_sức': [
        'mệt mỏi', 'áp lực', 'không chịu nổi', 'kiệt sức', 'quá tải',
        'stress', 'căng thẳng', 'mệt', 'oải', 'cực quá', 'vất vả quá',
        'không có ngày nghỉ', 'làm nhiều',
    ],
    'bất_công': [
        'không công bằng', 'thiên vị', 'phân biệt', 'ưu tiên người quen',
        'bất công', 'không minh bạch', 'mập mờ', 'ko công bằng',
    ],
    'mất_niềm_tin': [
        'không còn tin', 'hứa rồi không làm', 'thất vọng', 'chán nản',
        'mất niềm tin', 'lừa', 'nói một đằng làm một nẻo',
    ],
    'xung_đột_ql': [
        'sếp không quan tâm', 'quản lý yếu', 'không được lắng nghe',
        'sếp tệ', 'ql không tốt', 'am không hỗ trợ', 'quản lý thiên vị',
    ],
}

# ============================================================
# 5. TỪ ĐIỂN CẢM XÚC RULE-BASED
# ============================================================

POSITIVE_WORDS = {
    'tốt', 'tuyệt', 'vui', 'hài lòng', 'thích', 'ổn định', 'thoải mái',
    'thân thiện', 'hỗ trợ', 'đoàn kết', 'nhiệt tình', 'chuyên nghiệp',
    'công bằng', 'minh bạch', 'phát triển', 'linh hoạt', 'an toàn',
    'ổn', 'ok', 'hòa đồng', 'vui vẻ', 'năng động', 'tự hào',
    'yêu', 'tốt lắm', 'rất tốt', 'xuất sắc', 'hiệu quả',
    'đều đặn', 'ổn định', 'rõ ràng', 'quan tâm', 'gắn kết',
}

NEGATIVE_WORDS = {
    'tệ', 'kém', 'buồn', 'chán', 'mệt', 'khó', 'thiếu', 'ít',
    'thấp', 'không tốt', 'không hài lòng', 'bất công', 'phạt',
    'trừ', 'truy thu', 'áp lực', 'kiệt sức', 'mệt mỏi', 'vất vả',
    'nghỉ', 'tệ quá', 'quá tải', 'lừa', 'thất vọng', 'chán nản',
    'mập mờ', 'không rõ ràng', 'phạt nhiều', 'lương thấp', 'giảm',
    'ko', 'không', 'chưa',
}

# ============================================================
# 6. HÀM TIỀN XỬ LÝ
# ============================================================

def preprocess_text(text):
    """
    Tiền xử lý văn bản tiếng Việt cho phân tích NLP.
    Thực hiện 8 bước theo tài liệu kỹ thuật.
    """
    if text is None or not isinstance(text, str):
        return None

    text = text.strip()

    # T8: Loại phản hồi không có ý nghĩa (< 3 ký tự hoặc chỉ ký tự đặc biệt)
    if len(text) < 3:
        return None
    if re.match(r'^[\.\,\!\?\-\+\=\_\*\#\@\&\$\%\^\~\`\/\\]+$', text):
        return None

    # Loại phản hồi "không ý kiến"
    lower = text.lower().strip()
    no_opinion = {'không', 'ko', 'k', 'khong', 'kh', 'khobg', 'khoong',
                  'không ý kiến', 'ko ý kiến', 'ok', 'okk', 'oke',
                  '.', '..', '...', '-', 'no', 'none', 'x', 'xx', 'xxx',
                  'không có', 'ko có', 'kh có', 'bình thường', 'bt',
                  'không có gì', 'chưa', 'chưa có', 'k có', 'kg'}
    if lower in no_opinion:
        return None

    # T1: Loại bỏ thông tin cá nhân (SĐT, email)
    text = re.sub(r'\b0\d{9,10}\b', '', text)
    text = re.sub(r'\b[\w.-]+@[\w.-]+\.\w+\b', '', text)

    # T2: Chuẩn hóa Unicode NFC
    text = unicodedata.normalize('NFC', text)

    # T3: Chuyển chữ thường
    text = text.lower()

    # T4: Sửa lỗi chính tả cơ bản
    corrections = {
        'luong': 'lương', 'luơng': 'lương', 'luớng': 'lương',
        'nương': 'lương', 'luờn': 'lương', 'thun nhập': 'thu nhập',
        'thủ nhập': 'thu nhập', 'thư nhập': 'thu nhập',
        'nhan vien': 'nhân viên', 'cong ty': 'công ty',
        'thuoèng': 'thường', 'thoai mai': 'thoải mái',
        'thoãi mái': 'thoải mái', 'thoái mái': 'thoải mái',
        'thổi mái': 'thoải mái', 'thoả mái': 'thoải mái',
    }
    for wrong, right in corrections.items():
        text = text.replace(wrong, right)

    # T6: Loại từ dừng (nhưng giữ phủ định)
    # Không loại ở đây vì cần ngữ cảnh cho phân tích cảm xúc

    # T7: Chuẩn hóa từ đồng nghĩa (cơ bản) sử dụng word boundary để tránh lỗi substring (VD: 'am' trong 'làm')
    for variant, standard in SYNONYM_MAP.items():
        pattern = r'\b' + re.escape(variant) + r'\b'
        text = re.sub(pattern, standard, text)

    # Loại biểu tượng cảm xúc
    text = re.sub(r'[^\w\sàáảãạâầấẩẫậăằắẳẵặèéẻẽẹêềếểễệìíỉĩịòóỏõọôồốổỗộơờớởỡợùúủũụưừứửữựỳýỷỹỵđ_]',
                  ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()

    if len(text) < 3:
        return None

    return text


def analyze_sentiment_rule(text):
    """
    Phân tích cảm xúc rule-based nâng cao với ranh giới từ và phủ định.
    Returns: ('tích_cực' | 'tiêu_cực' | 'trung_lập', confidence_score)
    """
    if text is None:
        return None, 0.0

    text_lower = text.lower()
    negation_words = ['không', 'ko', 'k', 'chưa', 'chả', 'đỡ', 'hết', 'ít']
    pos_count = 0
    neg_count = 0

    # Đếm từ tích cực
    for w in POSITIVE_WORDS:
        pattern = r'(?:^|\W)(' + re.escape(w) + r')(?:\W|$)'
        for match in re.finditer(pattern, text_lower):
            start_idx = match.start(1)
            context_before = text_lower[max(0, start_idx-15):start_idx].strip()
            words_before = context_before.split()
            # Nếu trước từ tích cực là từ phủ định -> biến thành tiêu cực
            if words_before and words_before[-1] in negation_words:
                neg_count += 1
            else:
                pos_count += 1

    # Đếm từ tiêu cực
    for w in NEGATIVE_WORDS:
        pattern = r'(?:^|\W)(' + re.escape(w) + r')(?:\W|$)'
        for match in re.finditer(pattern, text_lower):
            start_idx = match.start(1)
            context_before = text_lower[max(0, start_idx-15):start_idx].strip()
            words_before = context_before.split()
            # Nếu trước từ tiêu cực là từ phủ định -> biến thành tích cực
            if words_before and words_before[-1] in negation_words:
                pos_count += 1
            else:
                neg_count += 1

    total = pos_count + neg_count
    if total == 0:
        return 'trung_lập', 0.5

    if pos_count > neg_count:
        confidence = pos_count / total
        return 'tích_cực', confidence
    elif neg_count > pos_count:
        confidence = neg_count / total
        return 'tiêu_cực', confidence
    else:
        return 'trung_lập', 0.5


def detect_warning_signals(text):
    """
    Quét tín hiệu cảnh báo sớm trong phản hồi.
    Sử dụng regex ranh giới từ và kiểm tra từ phủ định (không, ko, k,...)
    Returns: list of (signal_type, matched_phrase)
    """
    if not isinstance(text, str):
        return []

    text_lower = text.lower()
    signals = []
    negation_words = ['không', 'ko', 'k', 'chưa', 'chả', 'đỡ', 'hết', 'ít']
    
    for signal_type, phrases in WARNING_SIGNALS.items():
        for phrase in phrases:
            # Dùng regex để đảm bảo tìm đúng từ nguyên vẹn (word boundary)
            pattern = r'(?:^|\W)(' + re.escape(phrase) + r')(?:\W|$)'
            for match in re.finditer(pattern, text_lower):
                start_idx = match.start(1)
                
                # Lấy 15 ký tự ngay trước cụm từ đó để kiểm tra phủ định
                context_before = text_lower[max(0, start_idx-15):start_idx].strip()
                words_before = context_before.split()
                
                # Nếu từ liền trước là từ phủ định thì bỏ qua
                if words_before and words_before[-1] in negation_words:
                    continue
                
                signals.append((signal_type, phrase))
                break  # Ghi nhận 1 lần cho cụm từ này là đủ
                
    return signals


def extract_ngrams(texts, n=2, top_k=20):
    """
    Trích xuất n-gram phổ biến nhất từ danh sách text.
    """
    ngram_counter = Counter()
    for text in texts:
        if text is None:
            continue
        words = text.split()
        if len(words) < n:
            continue
        for i in range(len(words) - n + 1):
            ngram = ' '.join(words[i:i+n])
            # Lọc ngram chỉ chứa từ dừng
            ngram_words = set(ngram.split())
            if not ngram_words.issubset(STOP_WORDS):
                ngram_counter[ngram] += 1
    return ngram_counter.most_common(top_k)


# ============================================================
# 7. PHÂN LOẠI CHỦ ĐỀ (TOPIC CLASSIFICATION)
# ============================================================

TOPIC_KEYWORDS = {
    '💰 Thu nhập & Đơn giá': [
        'thu_nhập', 'lương', 'tiền', 'đơn giá', 'gtc', 'ltc', 'đơn giao',
        'thu nhập', 'income', 'giá đơn', 'chiết khấu', 'hoa hồng',
        'lương thấp', 'thu nhập thấp', 'tăng lương', 'tăng thu nhập',
        'kiếm tiền', 'kiếm thu_nhập', 'thu nhập ổn', 'thu_nhập ổn',
        'đơn hàng', 'số đơn', 'đơn nhiều', 'đơn ít', 'ít đơn',
    ],
    '⚖️ Phạt & Chính sách': [
        'phạt', 'trừ tiền', 'truy thu', 'phạt cod', 'bị trừ',
        'chính sách phạt', 'quy định phạt', 'phạt nhiều', 'phạt nặng',
        'cod', 'tiền phạt', 'trừ lương', 'phạt vô lý', 'bất hợp lý',
        'chính sách', 'quy định', 'luật', 'nội quy',
    ],
    '👨‍💼 Quản lý trực tiếp': [
        'quản_lý', 'sếp', 'am', 'tbc', 'trưởng nhóm', 'leader',
        'quản lý', 'anh quản lý', 'chị quản lý', 'cấp trên',
        'hỗ trợ', 'lắng nghe', 'quan tâm', 'công bằng',
        'thiên vị', 'không công bằng', 'phân đơn',
    ],
    '🤝 Đồng nghiệp & Văn hóa': [
        'đồng_nghiệp', 'anh em', 'team', 'đồng nghiệp',
        'hoà đồng', 'hòa đồng', 'vui vẻ', 'thân thiện',
        'đoàn kết', 'gắn kết', 'hỗ trợ nhau', 'giúp đỡ',
        'tập thể', 'đồng đội', 'ae', 'mọi người',
    ],
    '🏢 Môi trường làm việc': [
        'môi trường', 'bưu_cục', 'trạm', 'kho', 'điểm giao',
        'nơi làm việc', 'bc', 'bưu cục', 'ktc',
        'thoải mái', 'tự do', 'linh hoạt', 'thoải mai',
        'thời gian', 'ca làm', 'giờ giấc', 'tự chủ',
    ],
    '📱 Công cụ & App': [
        'ứng_dụng', 'app', 'phần mềm', 'hệ thống', 'tool',
        'driver app', 'ứng dụng', 'lỗi app', 'app lỗi',
        'app driver', 'phần mềm lỗi', 'hệ thống lỗi',
    ],
    '🚀 Phát triển & Thăng tiến': [
        'phát triển', 'thăng tiến', 'lộ trình', 'học hỏi',
        'cơ hội', 'đào tạo', 'kỹ năng', 'kinh nghiệm',
        'học tập', 'nâng cao', 'tiến bộ', 'sự nghiệp',
    ],
    '🎁 Phúc lợi & Chế độ': [
        'phúc_lợi', 'bảo hiểm', 'thưởng', 'phụ cấp', 'chế độ',
        'phúc lợi', 'quyền lợi', 'nghỉ phép', 'ngày nghỉ',
        'bảo hiểm xã hội', 'bhxh', 'xăng', 'xăng xe',
        'hỗ trợ xăng', 'bảo hộ', 'đồng phục', 'quà',
    ],
    '😰 Áp lực & Cường độ': [
        'áp lực', 'mệt', 'mệt mỏi', 'kiệt sức', 'quá tải',
        'stress', 'căng thẳng', 'vất vả', 'cực', 'nặng',
        'nhiều hàng', 'hàng nặng', 'cồng kềnh', 'xa',
        'giao xa', 'đường xa', 'nắng', 'mưa', 'thời tiết',
    ],
    '🔄 Quy trình & Vận hành': [
        'quy trình', 'thay đổi', 'cải thiện', 'sắp xếp',
        'phân tuyến', 'lộ trình giao', 'routing', 'chuyến',
        'lấy hàng', 'giao_hàng', 'trả hàng', 'hoàn hàng',
        'call log', 'add chuyến', 'xử lý', 'sự cố',
    ],
    '🏆 Tự hào & Gắn bó': [
        'tự hào', 'yêu', 'gắn bó', 'ở lại', 'trung thành',
        'tốt', 'ổn', 'ổn định', 'lâu dài', 'hài lòng',
        'thương hiệu', 'ghn', 'giao hàng nhanh',
    ],
    '⚠️ Muốn nghỉ / Bất mãn': [
        'nghỉ việc', 'nghỉ', 'muốn nghỉ', 'sắp nghỉ',
        'tìm việc khác', 'chuyển công ty', 'không gắn bó',
        'thất vọng', 'chán', 'chán nản', 'bất công',
        'không tin', 'mất niềm tin', 'lừa', 'nói một đằng',
    ],
}

# Nhãn ngắn gọn cho chart
TOPIC_SHORT_LABELS = {
    '💰 Thu nhập & Đơn giá': 'Thu nhập',
    '⚖️ Phạt & Chính sách': 'Phạt/CS',
    '👨‍💼 Quản lý trực tiếp': 'Quản lý',
    '🤝 Đồng nghiệp & Văn hóa': 'Đồng nghiệp',
    '🏢 Môi trường làm việc': 'Môi trường',
    '📱 Công cụ & App': 'App/Tool',
    '🚀 Phát triển & Thăng tiến': 'Phát triển',
    '🎁 Phúc lợi & Chế độ': 'Phúc lợi',
    '😰 Áp lực & Cường độ': 'Áp lực',
    '🔄 Quy trình & Vận hành': 'Quy trình',
    '🏆 Tự hào & Gắn bó': 'Tự hào',
    '⚠️ Muốn nghỉ / Bất mãn': 'Bất mãn',
}


def classify_topics(text):
    """
    Phân loại chủ đề từ text (multi-label) với ranh giới từ và phủ định.
    Returns: list of topic names found in text.
    """
    if not isinstance(text, str):
        return []

    text_lower = text.lower()
    topics_found = []
    negation_words = ['không', 'ko', 'k', 'chưa', 'chả', 'đỡ', 'hết', 'ít']
    
    for topic, keywords in TOPIC_KEYWORDS.items():
        matched = False
        for kw in keywords:
            pattern = r'(?:^|\W)(' + re.escape(kw) + r')(?:\W|$)'
            for match in re.finditer(pattern, text_lower):
                start_idx = match.start(1)
                context_before = text_lower[max(0, start_idx-15):start_idx].strip()
                words_before = context_before.split()
                # Nếu từ liền trước là từ phủ định, bỏ qua
                if words_before and words_before[-1] in negation_words:
                    continue
                matched = True
                break
            if matched:
                topics_found.append(topic)
                break  # 1 match đủ để gán topic
                
    return topics_found if topics_found else ['❓ Khác']


def extract_topic_stats(texts, labels=None):
    """
    Tính thống kê topic từ danh sách texts.
    Returns: dict {topic: count}
    """
    topic_counts = Counter()
    for text in texts:
        if text is None:
            continue
        for topic in classify_topics(text):
            topic_counts[topic] += 1
    return topic_counts


def extract_topic_by_group(df, text_col, group_col, group_values=None):
    """
    Tính topic distribution theo nhóm (vd: eNPS_group).
    Returns: DataFrame (topic × group → count)
    """
    rows = []
    if group_values is None:
        group_values = df[group_col].dropna().unique()

    for gv in group_values:
        mask = (df[group_col] == gv) & df[text_col].notna()
        texts = df.loc[mask, text_col].tolist()
        n_total = len(texts)
        if n_total < 5:
            continue
        topic_counts = extract_topic_stats(texts)
        for topic, count in topic_counts.items():
            rows.append({
                'Group': gv,
                'Topic': topic,
                'Count': count,
                'Pct': count / n_total * 100,
                'N_total': n_total,
            })
    import pandas as pd
    return pd.DataFrame(rows)


def extract_representative_quotes(df, text_col, topic, n=5):
    """
    Lấy n câu trích dẫn tiêu biểu cho 1 topic.
    Ưu tiên câu ngắn gọn, rõ ràng (20-80 ký tự).
    """
    quotes = []
    for _, row in df.iterrows():
        text = row.get(text_col)
        if text is None:
            continue
        topics = classify_topics(text)
        if topic in topics:
            quotes.append(text)

    # Sort by length (prefer medium-length quotes)
    quotes.sort(key=lambda q: abs(len(q) - 50))
    return quotes[:n]

