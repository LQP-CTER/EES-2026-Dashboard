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


def split_sentences(text):
    """
    Tách câu/mệnh đề tiếng Việt để phân tích riêng từng ý.
    VD: "lương thấp nhưng vui vẻ" → ["lương thấp", "vui vẻ"]
    """
    if not isinstance(text, str) or len(text) < 5:
        return [text] if isinstance(text, str) else []
    
    # Tách theo dấu câu
    parts = re.split(r'[.!?;]\s*', text)
    
    # Tách tiếp theo liên từ đối lập
    refined = []
    for part in parts:
        sub_parts = re.split(
            r',\s*(?:nhưng|tuy nhiên|còn|mà|tuy|song|thế nhưng|dù vậy|mặc dù|tuy vậy)\s',
            part
        )
        refined.extend(sub_parts)
    
    return [p.strip() for p in refined if len(p.strip()) > 5]


def analyze_sentiment_rule(text):
    """
    Phân tích cảm xúc rule-based nâng cao với ranh giới từ và phủ định.
    Returns: ('tích_cực' | 'tiêu_cực' | 'trung_lập', confidence_score)
    """
    if text is None:
        return None, 0.0

    text_lower = text.lower()
    negation_words = ['không', 'ko', 'k', 'chưa', 'chả', 'đỡ', 'hết', 'ít', 'chẳng']
    pos_count = 0
    neg_count = 0

    # Đếm từ tích cực
    for w in POSITIVE_WORDS:
        pattern = r'(?:^|\W)(' + re.escape(w) + r')(?:\W|$)'
        for match in re.finditer(pattern, text_lower):
            start_idx = match.start(1)
            context_before = text_lower[max(0, start_idx-25):start_idx].strip()
            words_before = context_before.split()
            # Nếu trước từ tích cực là từ phủ định -> biến thành tiêu cực
            if any(w_b in negation_words for w_b in words_before[-3:]):
                neg_count += 1
            else:
                pos_count += 1

    # Đếm từ tiêu cực
    for w in NEGATIVE_WORDS:
        pattern = r'(?:^|\W)(' + re.escape(w) + r')(?:\W|$)'
        for match in re.finditer(pattern, text_lower):
            start_idx = match.start(1)
            context_before = text_lower[max(0, start_idx-25):start_idx].strip()
            words_before = context_before.split()
            # Nếu trước từ tiêu cực là từ phủ định -> biến thành tích cực
            if any(w_b in negation_words for w_b in words_before[-3:]):
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


def compute_sentiment_intensity(text):
    """
    Tính cường độ cảm xúc từ -1.0 (cực kỳ tiêu cực) đến +1.0 (cực kỳ tích cực).
    Sử dụng tách câu để phân tích từng mệnh đề riêng biệt.
    Returns: (float score, str label)
    """
    if not isinstance(text, str):
        return 0.0, 'trung_lập'
    
    sentences = split_sentences(text)
    if not sentences:
        return 0.0, 'trung_lập'
    
    total_score = 0.0
    n_sentences = 0
    
    for sent in sentences:
        sentiment, confidence = analyze_sentiment_rule(sent)
        if sentiment == 'tích_cực':
            total_score += confidence
        elif sentiment == 'tiêu_cực':
            total_score -= confidence
        n_sentences += 1
    
    if n_sentences == 0:
        return 0.0, 'trung_lập'
    
    avg_score = total_score / n_sentences
    
    # Clamp to [-1, 1]
    avg_score = max(-1.0, min(1.0, avg_score))
    
    if avg_score > 0.15:
        label = 'tích_cực'
    elif avg_score < -0.15:
        label = 'tiêu_cực'
    else:
        label = 'trung_lập'
    
    return round(avg_score, 3), label


def detect_warning_signals(text):
    """
    Quét tín hiệu cảnh báo sớm trong phản hồi.
    Sử dụng regex ranh giới từ và kiểm tra từ phủ định (không, ko, k,...),
    đồng thời lọc bỏ các bối cảnh tích cực làm trung hòa cảnh báo (vượt qua, quen rồi).
    Returns: list of (signal_type, matched_phrase)
    """
    if not isinstance(text, str):
        return []

    text_lower = text.lower()
    signals = []
    negation_words = ['không', 'ko', 'k', 'chưa', 'chả', 'đỡ', 'hết', 'ít', 'chẳng']
    neutralizing_words = ['vượt qua', 'vượt lên', 'chấp nhận', 'cố gắng', 'quen rồi', 'xứng đáng', 'đền đáp', 'ok', 'ổn', 'bình thường', 'tốt']
    
    for signal_type, phrases in WARNING_SIGNALS.items():
        for phrase in phrases:
            # Dùng regex để đảm bảo tìm đúng từ nguyên vẹn (word boundary)
            pattern = r'(?:^|\W)(' + re.escape(phrase) + r')(?:\W|$)'
            for match in re.finditer(pattern, text_lower):
                start_idx = match.start(1)
                end_idx = match.end(1)
                
                # Lấy 25 ký tự trước để kiểm tra phủ định (khoảng 3-4 từ)
                context_before = text_lower[max(0, start_idx-25):start_idx].strip()
                words_before = context_before.split()
                
                # Nếu từ liền trước (trong vòng 3 từ) là từ phủ định thì bỏ qua (VD: "k bị áp lực")
                if any(w in negation_words for w in words_before[-3:]):
                    continue
                    
                # Lấy 40 ký tự sau để kiểm tra trung hòa (khoảng 5-7 từ)
                context_after = text_lower[end_idx:min(len(text_lower), end_idx+40)].strip()
                words_after = context_after.split()
                
                # Nếu các từ theo sau làm trung hòa tín hiệu thì bỏ qua (VD: "áp lực cần phải vượt qua")
                is_neutral = False
                for nw in neutralizing_words:
                    # Kiểm tra xem từ trung hòa có xuất hiện trong đoạn context sau không
                    if nw in context_after:
                        is_neutral = True
                        break
                
                if is_neutral:
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
# 7B. TRÍCH XUẤT ĐỀ XUẤT HÀNH ĐỘNG
# ============================================================

ACTION_PATTERNS = [
    r'(?:nên|cần|mong|muốn|đề xuất|kiến nghị|ước gì|nếu được|hy vọng|mong muốn|mong rằng|xin|đề nghị|yêu cầu|kính mong)\s+(.{10,})',
    r'(?:hãy|vui lòng|làm ơn|xin hãy)\s+(.{10,})',
    r'(?:cải thiện|nâng cao|tăng|giảm|bỏ|thêm|sửa|đổi|thay đổi)\s+(.{8,})',
]

def extract_action_suggestions(texts):
    """
    Trích xuất các câu có tính chất đề xuất/kiến nghị từ danh sách phản hồi.
    Returns: list of dict {text, pattern_matched, topic}
    """
    suggestions = []
    seen = set()
    
    for text in texts:
        if not isinstance(text, str) or len(text) < 15:
            continue
        
        text_lower = text.lower()
        for pattern in ACTION_PATTERNS:
            match = re.search(pattern, text_lower)
            if match:
                # Tránh trùng lặp
                key = text[:50]
                if key in seen:
                    continue
                seen.add(key)
                
                topics = classify_topics(text)
                topic_str = topics[0] if topics else '❓ Khác'
                
                _, tone_label = compute_sentiment_intensity(text)
                
                suggestions.append({
                    'text': text,
                    'topic': topic_str,
                    'tone': tone_label,
                })
                break  # 1 match per text is enough
    
    return suggestions


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
    negation_words = ['không', 'ko', 'k', 'chưa', 'chả', 'đỡ', 'hết', 'ít', 'chẳng']
    
    for topic, keywords in TOPIC_KEYWORDS.items():
        matched = False
        for kw in keywords:
            pattern = r'(?:^|\W)(' + re.escape(kw) + r')(?:\W|$)'
            for match in re.finditer(pattern, text_lower):
                start_idx = match.start(1)
                context_before = text_lower[max(0, start_idx-25):start_idx].strip()
                words_before = context_before.split()
                # Nếu từ liền trước là từ phủ định, bỏ qua
                if any(w in negation_words for w in words_before[-3:]):
                    continue
                matched = True
                break
            if matched:
                topics_found.append(topic)
                break  # 1 match đủ để gán topic
                
    return topics_found if topics_found else ['❓ Khác']


def classify_topics_with_tone(text):
    """
    Phân loại chủ đề kèm giọng điệu (tone) của từng chủ đề.
    Returns: list of (topic_name, tone_label, intensity_score)
    VD: [('💰 Thu nhập & Đơn giá', 'tiêu_cực', -0.7)]
    """
    if not isinstance(text, str):
        return []
    
    topics = classify_topics(text)
    if not topics or topics == ['❓ Khác']:
        intensity, tone = compute_sentiment_intensity(text)
        return [('❓ Khác', tone, intensity)]
    
    # Tách câu để gán tone chính xác hơn cho từng topic
    sentences = split_sentences(text)
    results = []
    
    for topic in topics:
        # Tìm câu nào liên quan đến topic này
        topic_keywords = TOPIC_KEYWORDS.get(topic, [])
        relevant_sentences = []
        
        for sent in sentences:
            sent_lower = sent.lower()
            for kw in topic_keywords:
                if kw in sent_lower:
                    relevant_sentences.append(sent)
                    break
        
        if relevant_sentences:
            # Tính sentiment intensity chỉ cho các câu liên quan
            combined = '. '.join(relevant_sentences)
            intensity, tone = compute_sentiment_intensity(combined)
        else:
            # Fallback: dùng toàn bộ text
            intensity, tone = compute_sentiment_intensity(text)
        
        results.append((topic, tone, intensity))
    
    return results


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


def extract_topic_stats_with_tone(texts):
    """
    Tính thống kê topic kèm tone từ danh sách texts.
    Returns: dict {topic: {'positive': count, 'negative': count, 'neutral': count, 'total': count}}
    """
    topic_tone = {}
    for text in texts:
        if text is None:
            continue
        results = classify_topics_with_tone(text)
        for topic, tone, _ in results:
            if topic not in topic_tone:
                topic_tone[topic] = {'positive': 0, 'negative': 0, 'neutral': 0, 'total': 0}
            topic_tone[topic]['total'] += 1
            if tone == 'tích_cực':
                topic_tone[topic]['positive'] += 1
            elif tone == 'tiêu_cực':
                topic_tone[topic]['negative'] += 1
            else:
                topic_tone[topic]['neutral'] += 1
    return topic_tone


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

