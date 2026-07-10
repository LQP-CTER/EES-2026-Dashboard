import streamlit as st
import os
import json
import re
import time
import hashlib
from groq import Groq

_AI_LOGO_B64 = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAIAAAD8GO2jAAADT0lEQVR4nO1WTWwVVRT+zp15f33PlhojIivKAl0RiKgNCalhUV2ZEBODC+PPorpxQQIoG10TMLjDjQloSKORjUlTF6AYFdPUrjRFTU0auwBCAi/w/mbmns+cmVc0ffPo66I7Tu7M3HvPPd+558w5514hic0kt6noeKhgAAr7cnp/vnQfgOiNDMlYPdObHUVh/jTJZh3UdMu0N4FKVcKCMZMYrUZqTMoCIU6GRnKN6FFAQoTNuh7dJ3frCARJIkHAexGePSjHv7Ylpw/L3CWtlUQTBCE9WRsJTs1JdTQTH8ACQG4u40bsyuAQ4CHFgFcu8u1/bMvfX0Q5CG7VGUKaYBvceqcvztp/kFlw+7p+/Jrs3Me7N93laXjP0z9i7huGBfNHEuG5l+XIfoROXzgsw49zad4d+UJGt/VaYN7OoXZDo5Z2Wsn7BzgBf/adbDpemI1/nc36/uy7xjp+QDtNjdpsN3KR+iggqT45Ns4J6KGCX7lG9UziLiuJqd6vXNNDRU4gOfY8ve8Hk1eLfGKvKxdk4Spqjjt2u+27zPVBaHFFtQ7Ebd/FHbtRc7Lwi/5w4b7gGspTIOnk5XMoCCLF2B4bqu+yMm42HNvDSFEQfnfuP8F1FJBwjlELK4tSJBQYfTKN914iHt1mqVKkrCyaiHO9+d+nXEctiVtZIqF5Z7VCrLUUjXr6FUQta3nUoyCDKtdQGaYHSsD8DNUbirmF1tIhVTk/I2VIQlaGTeS++AMtMCAJi9y5Fx3hUAlLf/HzE3CBNQOQrK/nP5ClP1kpoSMytlfCYroDGfREk8kpCKEqtQDTJ/2ZN3T5NwvQJNbl3/XMmzJ9EtUAqlZaJ6f64uRXU1U450+9KjNf4rESkgT3PKoOT4wZ9/rf0lA8EjAI5VZHX3olOPpVJjKwAptM8/nDF2X+Z2wJEBaQRBKpMYvOHOJj3PZ8Zlw+mpVKzZyTV037nwdZUWo39NP38O1nEgPF1dqYQCKwAEy+JVOfSLmWU4LWV7CqA4Au/oRL5/nHVanfsNXDW/HUuBx83T29///LNq4gE05Tr5sTWeBXR7p4qgbdH33gI1O9qbEStEo+MVwL3HVog2cy08UP3PLAt4r8/cjG1j+82Q1Am367/hffvQmZc1fQbgAAAABJRU5ErkJggg=="
MASTER_REPORT_VOICE_VERSION = "master-report-v6"


def get_master_report_voice_prompt():
    """Editorial voice aligned to the GHN deep analyst report."""
    return """
GIỌNG VĂN THAM CHIẾU: GHN.EES 2026.Report Deep Analyst_Final.pdf

I. YÊU CẦU GIỌNG VĂN:
   • Viết như một người thật đang tổng hợp và báo cáo lại.
   • Mở bằng nhận định chính, rồi mới đi vào số liệu hoặc diễn giải cần thiết.
   • Giữ nhịp văn tự nhiên. Nếu cần, chấp nhận câu ngắn hoặc chưa hoàn hảo tuyệt đối miễn đọc chân thật.
   • Giọng điềm tĩnh, chắc, mạch lạc. Không lên gân. Không tạo cảm giác "AI đang phân tích".

II. /ghost - BẤT BUỘC ÁP DỤNG:
   • Viết lại như một người thật.
   • Không dùng văn phong AI.
   • Không dùng các câu chuyển ý sáo rỗng lặp đi lặp lại.
   • Không dùng dấu gạch ngang dài.
   • Không cố làm cho câu quá tròn trịa nếu như cách viết tự nhiên sẽ ngắn hơn.

III. KỶ LUẬT SUY LUẬN:
   • Phân biệt rõ điều dữ liệu nói trực tiếp và điều được diễn giải.
   • Chỉ khẳng định mạnh với số liệu hiện diện rõ trong dữ liệu đầu vào.
   • Với diễn giải, dùng mức độ vừa phải: "cho thấy", "phản ánh", "có thể đến từ", "nhiều khả năng liên quan đến".
   • Nếu base nhỏ, dữ liệu lệch, hoặc chưa đủ chắc, phải nói rõ: "mang tính tham khảo", "nên xem như tín hiệu để theo dõi", "chưa đủ để kết luận".
   • Không nhảy từ một dấu hiệu sang kết luận nguyên nhân gốc nếu dữ liệu chưa đủ.

IV. NHỮNG GÌ CẦN TRÁNH:
   • Tránh các cụm dễ lộ chất AI như: "Nhìn chung", "Đặc biệt", "điều này phản ánh rằng", "để cải thiện điểm này", "điều này cho thấy rằng", "điều này gợi ý rằng", "vì vậy có thể thấy", "có thể nói rằng" nếu không thật sự cần.
   • Không dùng các nhãn kịch tính hoặc chối tai như: "điểm đau", "nút thắt lớn", "khủng hoảng", "báo động đỏ", "bộc lộ yếu kém".
   • Không đặt tên vấn đề theo kiểu sáng tác khái niệm.
   • Không dùng jargon tư vấn hoặc AI nặng nếu không thực sự cần.
   • Không viết kiểu checklist máy móc ra mặt chữ.

V. KHUÔN VIẾT MONG MUỐN:
   • Ưu tiên 2 đến 3 đoạn ngắn, mỗi đoạn gói một ý chính. Có thể linh hoạt nếu dữ liệu quá ít hoặc nhiệm vụ phù hợp với bullet.
   • Mỗi đoạn chỉ nên chứa 1 ý chính.
   • Ưu tiên câu cụ thể, gần nghĩa thực tế vận hành, ít khẩu hiệu.
   • Khi có nhiều ý, sắp theo thứ tự: kết luận chính, điểm cần lưu ý, rồi đến hàm ý hành động.

VI. NGÔN NGỮ THAM CHIẾU TỪ BÁO CÁO:
   • Ưu tiên các cụm tự nhiên như: "bức tranh chung khá tích cực, nhưng chưa đồng đều", "điểm cần cải thiện", "mối quan tâm lớn", "điểm nên lưu ý", "nhóm cần được quan tâm hơn", "không nên chỉ nhìn chỉ số tổng".
   • Khi so sánh giữa nhóm hoặc đơn vị, nói rõ mức chênh và ý nghĩa của chênh lệch đó.
   • Khi nói về giữ chân, burnout, thu nhập, quản lý trực tiếp, niềm tin lãnh đạo, hãy nối về bối cảnh vận hành thay vì mô tả trừu tượng.
"""
# ============================================================
# DUAL GROQ KEY — ROUND-ROBIN LOAD BALANCER
# Key 1 và Key 2 luân phiên xử lý request.
# Nếu Key đang dùng bị Rate Limit (429) → tự động chuyển key kia.
# ============================================================

def _get_groq_keys():
    """Trả về danh sách Groq API keys hợp lệ. Hỗ trợ Local và Snowflake SiS."""
    keys = []
    
    # 1. Thử lấy từ Snowflake (nếu đang chạy trên Streamlit in Snowflake)
    try:
        import _snowflake
        # Đọc secret từ cấu hình Snowflake
        for sf_secret_name in ["groq_key", "groq_key_2"]:
            try:
                k = _snowflake.get_generic_secret_string(sf_secret_name)
                if k and k != "dien-api-key-cua-ban-vao-day":
                    keys.append(k)
            except Exception:
                pass
    except ImportError:
        pass # Không có _snowflake, nghĩa là đang chạy local
        
    # Nếu trên Snowflake đã lấy được key thì ưu tiên dùng luôn
    if keys:
        return keys

    # 2. Fallback: Local/Môi trường thường dùng st.secrets hoặc os.environ
    for env_name in ["GROQ_API_KEY", "GROQ_API_KEY_2"]:
        try:
            k = st.secrets.get(env_name, os.environ.get(env_name, ""))
        except Exception:
            k = os.environ.get(env_name, "")
        if k and k != "dien-api-key-cua-ban-vao-day":
            keys.append(k)
            
    return keys


def get_groq_client():
    """Lấy Groq client theo round-robin (dùng xen kẽ Key 1 và Key 2)."""
    keys = _get_groq_keys()
    if not keys:
        return None
    if '_groq_key_idx' not in st.session_state:
        st.session_state['_groq_key_idx'] = 0
    idx = st.session_state['_groq_key_idx'] % len(keys)
    st.session_state['_groq_key_idx'] = (idx + 1) % len(keys)
    try:
        return Groq(api_key=keys[idx])
    except Exception as e:
        print(f"Groq client error (key {idx+1}):", e)
        return None


def get_groq_clients_all():
    """Trả về list tất cả Groq clients để thử lần lượt khi gặp 429."""
    clients = []
    for k in _get_groq_keys():
        try:
            clients.append(Groq(api_key=k))
        except Exception:
            pass
    return clients


def get_cache_key(data_json, context_prompt):
    return hashlib.md5((MASTER_REPORT_VOICE_VERSION + data_json + context_prompt).encode()).hexdigest()


# ============================================================
# AI INSIGHT GENERATION (STREAM)
# Thử Key 1 → nếu 429 chuyển Key 2 → thử từng model
# ============================================================

# Danh sách model đã kiểm tra thực tế qua API Groq (2026-05-28)
# Chỉ giữ các model đã PASS test - các model khác đã bị decommissioned
GROQ_MODELS = [
    "qwen/qwen3.6-27b",                    # Primary model per current dashboard tuning
    "llama-3.3-70b-versatile",             # Fallback if Qwen is unavailable or rate-limited
    "meta-llama/llama-4-scout-17b-16e-instruct",
    "llama-3.1-8b-instant",
]

def _build_insight_system_prompt(data_json, context_prompt, lang='VN'):
    return f"""
Bạn là một Chuyên gia Tư vấn Trải nghiệm Nhân viên (Employee Experience) và Phân tích Dữ liệu Nhân sự (People Analytics) cấp cao. Bạn đang viết báo cáo cho Ban Lãnh đạo của GHN.

Dưới đây là dữ liệu trích xuất từ khảo sát Employee Engagement Survey (EES) 2026.
Dữ liệu JSON:
{data_json}

Nhiệm vụ:
{context_prompt}

QUY TẮC BẮT BUỘC VỀ TÍNH CHÍNH XÁC CỦA DỮ LIỆU (ZERO-HALLUCINATION):
A. CHỈ phân tích dựa trên các trường và giá trị CÓ TRONG JSON bên trên. TUYỆT ĐỐI KHÔNG đề cập, trích dẫn, hoặc ám chỉ bất kỳ chỉ số, con số, metric, hoặc tỷ lệ phần trăm nào KHÔNG XUẤT HIỆN trong dữ liệu JSON được cung cấp.
B. Mọi con số bạn viết trong bài phân tích PHẢI khớp chính xác với một giá trị trong JSON.
C. Nếu bạn không chắc chắn một chỉ số có trong JSON hay không, HÃY BỎ QUA chỉ số đó.
D. KHÔNG tự tính toán, suy diễn, hoặc ngoại suy thêm bất kỳ con số nào ngoài những gì JSON cung cấp.

{get_master_report_voice_prompt()}

YÊU CẦU TRÌNH BÀY:
1. Ngôn ngữ: {'Tiếng Việt' if lang == 'VN' else 'English'}.
2. Viết như một đoạn trong báo cáo phân tích nội bộ đã phát hành, không viết như chatbot hoặc consultant pitch.
3. Ưu tiên mở đầu bằng kết luận chính, sau đó mới giải thích bằng số liệu.
4. Không dùng lời chào, không tự giới thiệu vai trò, không kết luận sáo rỗng.
5. Không dùng ký tự Markdown # hoặc bảng Markdown. Chỉ dùng bullet khi nhiệm vụ cụ thể yêu cầu danh sách.
6. Khi cần nhấn mạnh trong đoạn văn, dùng `**...**` cho 1 nhận định chính và 1 đến 2 ý quan trọng. Có thể dùng thêm `<span class="ai-highlight">` cho tín hiệu tích cực và `<span class="ai-warning">` cho rủi ro khi thật sự cần.
7. Giữ rất gọn: tối đa 2 đoạn ngắn, thường chỉ 3 câu tổng. Chỉ dùng bullet khi nhiệm vụ thực sự cần liệt kê.
8. Nếu dữ liệu chưa đủ chắc, phải nói rõ mức độ thận trọng ngay trong câu viết.
9. Ưu tiên câu tự nhiên, ngắn và có trọng tâm. Tránh lặp lại cùng một ý bằng nhiều câu diễn đạt khác nhau, và không nhắc lại tên field kỹ thuật trong JSON như `pillar_mean`, `weakest_item`, `negative_rate`.
10. Không dùng các cụm như "điểm đau", "Nhìn chung", "Đặc biệt", "điều này phản ánh rằng", "để cải thiện điểm này", "điều này gợi ý rằng", "điều này cho thấy rằng" trừ khi prompt nhiệm vụ yêu cầu nguyên văn.
11. Không cố mở bài bằng một câu dẫn khuôn mẫu. Có thể vào thẳng nhận định chính nếu dữ liệu đã đủ rõ.
12. Tránh viết thành một khối chữ dài. Người đọc phải nhìn thấy ngay ý chính và một điểm cần lưu ý."""


def generate_ees_insight_stream(data_json, context_prompt, lang='VN'):
    user_prompt = _build_insight_system_prompt(data_json, context_prompt, lang)
    all_clients = get_groq_clients_all()

    APP_STATE_FILE = os.path.join("config", "app_state.json")
    ai_temp = 0.3
    try:
        if os.path.exists(APP_STATE_FILE):
            with open(APP_STATE_FILE, "r") as f:
                ai_temp = float(json.load(f).get("ai_config", {}).get("temperature", 0.3))
    except Exception:
        pass

    if not all_clients:
        yield "Cảnh báo: Không có Groq API key hợp lệ. Vui lòng kiểm tra secrets.toml"
        return

    last_error = ""
    for client in all_clients:
        for model in GROQ_MODELS:
            try:
                stream = client.chat.completions.create(
                    messages=[
                        {"role": "system", "content": "Bạn là chuyên gia phân tích nội bộ của GHN. Chỉ trả lời bằng nội dung cuối cùng cho người đọc, không hiển thị suy luận nội bộ hoặc thẻ <think>."},
                        {"role": "user", "content": user_prompt},
                    ],
                    model=model,
                    temperature=ai_temp,
                    max_tokens=1500,
                    stream=True
                )
                raw_text = ""
                for chunk in stream:
                    if chunk.choices[0].delta.content is not None:
                        raw_text += chunk.choices[0].delta.content

                cleaned_text = sanitize_ai_insight_text(raw_text)
                if not cleaned_text:
                    last_error = f"{model}: empty_or_reasoning_only_output"
                    continue

                yield cleaned_text
                return
            except Exception as e:
                last_error = str(e)
                if "rate_limit_exceeded" in last_error.lower() or "429" in last_error:
                    time.sleep(0.5)
                continue

    yield f"Không thể kết nối AI sau khi thử {len(all_clients)} key và tất cả các model: {last_error[:120]}"


# ============================================================
# AI VALIDATOR (NON-STREAM)
# Dùng để xác nhận tín hiệu cảnh báo NLP — cần JSON output
# Thử Key 1 → nếu 429 chuyển Key 2
# ============================================================

def validate_warning_signals_with_ai(signals_batch):
    """
    Dùng LLM làm 'thẩm phán' xác nhận tín hiệu cảnh báo NLP.
    Rule-based phát hiện ứng viên → LLM lọc false positive.

    Args:
        signals_batch: list of dict {'index', 'signal_type', 'phrase', 'full_text'}
    Returns:
        dict {index: {'valid': bool, 'reason': str}}
    """
    if not signals_batch:
        return {}

    # Cache check
    cache_key_data = json.dumps(
        [s['full_text'][:100] + s['phrase'] for s in signals_batch], ensure_ascii=False
    )
    cache_key = f"ai_validate_{hashlib.md5(cache_key_data.encode()).hexdigest()}"
    if cache_key in st.session_state:
        return st.session_state[cache_key]

    # Build prompt
    items_text = ""
    for i, s in enumerate(signals_batch[:20]):
        items_text += f"\n[{i}] Loại: {s['signal_type']} | Từ khóa: \"{s['phrase']}\" | Câu gốc: \"{s['full_text'][:200]}\""

    validation_prompt = f"""Bạn là chuyên gia phân tích ngôn ngữ tiếng Việt trong bối cảnh khảo sát nhân viên.

NHIỆM VỤ: Xác định mỗi câu phản hồi dưới đây THỰC SỰ mang tín hiệu tiêu cực hay không.

HƯỚNG DẪN:
- Ý tích cực/trung lập (VD: "vui vẻ bớt áp lực", "làm nhiều thu nhập cao", "có đồng nghiệp giúp đỡ nên bớt mệt") → valid: false
- Ý tiêu cực thực sự (VD: "quá áp lực không chịu nổi", "mệt mỏi muốn nghỉ", "lương thấp không đủ sống") → valid: true
- "bớt áp lực", "không áp lực", "giảm áp lực" → valid: false
- "làm nhiều" + ngữ cảnh tích cực → valid: false

Danh sách cần phân loại:
{items_text}

OUTPUT: Chỉ trả JSON array, không viết gì thêm:
[{{"id": 0, "valid": true/false, "reason": "lý do ngắn"}}]"""

    def _parse_result(raw_text):
        m = re.search(r'\[.*?\]', raw_text, re.DOTALL)
        return json.loads(m.group() if m else raw_text)

    def _map_results(results):
        output = {}
        for r in results:
            batch_idx = r.get('id', -1)
            if 0 <= batch_idx < len(signals_batch):
                original_idx = signals_batch[batch_idx]['index']
                output[original_idx] = {
                    'valid': r.get('valid', True),
                    'reason': r.get('reason', '')
                }
        for s in signals_batch:
            if s['index'] not in output:
                output[s['index']] = {'valid': True, 'reason': 'Chưa xác nhận'}
        return output

    # Thử tất cả Groq keys × models
    validator_models = ["qwen/qwen3.6-27b", "llama-3.3-70b-versatile", "meta-llama/llama-4-scout-17b-16e-instruct", "llama-3.1-8b-instant"]
    for client in get_groq_clients_all():
        for model in validator_models:
            try:
                response = client.chat.completions.create(
                    messages=[
                        {"role": "system", "content": "Bạn là bộ phân loại tín hiệu khảo sát. Chỉ trả về JSON hợp lệ, không hiển thị suy luận nội bộ hoặc thẻ <think>."},
                        {"role": "user", "content": validation_prompt},
                    ],
                    model=model,
                    temperature=0.1,
                    max_tokens=2000,
                    stream=False
                )
                raw = response.choices[0].message.content.strip()
                raw = re.sub(r'<think>.*?(</think>|$)', '', raw, flags=re.DOTALL | re.IGNORECASE).strip()
                results = _parse_result(raw)
                output = _map_results(results)
                st.session_state[cache_key] = output
                return output
            except Exception as e:
                if "rate_limit_exceeded" in str(e).lower() or "429" in str(e):
                    break  # Key rate limited → thử key tiếp theo
                continue

    # Tất cả fail → giữ nguyên (coi như hợp lệ)
    fallback = {s['index']: {'valid': True, 'reason': 'AI không khả dụng'} for s in signals_batch}
    st.session_state[cache_key] = fallback
    return fallback


# ============================================================
# HTML FORMATTING & RENDER CARD
# ============================================================

def sanitize_ai_insight_text(text):
    text = text.strip()
    if not text:
        return text

    text = re.sub(r'<think>.*?(</think>|$)', '', text, flags=re.DOTALL | re.IGNORECASE)
    replacements = [
        (r'(?im)^\s*Nhìn chung\s*[,:-]?\s*', ''),
        (r'(?im)^\s*Đặc biệt\s*[,:-]?\s*', ''),
        (r'(?i)\bĐiều này phản ánh rằng\b', 'Điều này cho thấy'),
        (r'(?i)\bĐiều này gợi ý rằng\b', 'Có thể hiểu rằng'),
        (r'(?i)\bĐiều này cho thấy rằng\b', 'Điều này cho thấy'),
        (r'(?i)\bĐể cải thiện điểm này\b', 'Để cải thiện'),
        (r'(?i)\bđiểm đau\b', 'điểm cần lưu ý'),
    ]
    for pattern, replacement in replacements:
        text = re.sub(pattern, replacement, text)

    text = re.sub(r'\n\s*\n+', '\n', text)
    text = re.sub(r'[ \t]{2,}', ' ', text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip(' \n')


def format_ai_html(text):
    text = sanitize_ai_insight_text(text)
    # Collapse blank paragraphs so insight text stays visually continuous.
    text = re.sub(r'\n\s*\n+', '\n', text.strip())
    html = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', text)
    html = re.sub(r'\*(.*?)\*', r'<em>\1</em>', html)
    html = re.sub(r'(?m)^(Điểm mạnh nhất|Điểm cần lưu ý|Mối cần lưu ý|Hàm ý hành động|Khuyến nghị)\s*:', r'<strong>\1:</strong>', html)
    if '<strong>' not in html:
        html = re.sub(r'^([^.!?]{20,140}[.!?])', r'<strong>\1</strong>', html, count=1)
    html = re.sub(r'(?m)^[-*]\s+', '• ', html)
    html = html.replace('\n', '<br>')
    return html


def _get_scope_prefix() -> str:
    """Trả về context prefix phạm vi nếu user bị giới hạn.

    Inject vào đầu mọi AI prompt để model biết đây là phân tích
    cho một đơn vị cụ thể, không suy luận toàn GHN.
    """
    try:
        auth = st.session_state.get("user_authorization", {})
        if not isinstance(auth, dict):
            return ""
        if auth.get("role", "").upper() == "ADMIN":
            return ""
        views = [str(v).strip().upper() for v in auth.get("survey_view", []) if str(v).strip()]
        if not views or "ALL" in views or "COMPANY" in views:
            return ""
        _level_map = {
            "SECTION": ("sections", "Team/Section"),
            "DEPARTMENT": ("departments", "Phòng ban"),
            "PHONG_BAN": ("departments", "Phòng ban"),
            "DIVISION": ("divisions", "Khối"),
            "KHOI": ("divisions", "Khối"),
        }
        for lk in ("SECTION", "DEPARTMENT", "PHONG_BAN", "DIVISION", "KHOI"):
            if lk in views:
                field, label = _level_map[lk]
                units = [u for u in auth.get(field, []) if u]
                if units:
                    unit_str = ", ".join(units)
                    return (
                        f"[BỐI CẢNH PHÂN TÍCH: Dữ liệu dưới đây CHỈ thuộc {label} '{unit_str}'. "
                        f"Phân tích theo góc nhìn của {label} này — "
                        f"KHÔNG suy luận hoặc so sánh sang các đơn vị ngoài phạm vi cung cấp.]\n\n"
                    )
        return ""
    except Exception:
        return ""

def render_ai_insight_card(title, data_dict, context_prompt, badge="EES-Analyzer-v2.0", custom_style="", target_container=None):
    """
    Render AI insight card với Groq dual-key streaming.
    Cache kết quả trong session_state để không gọi lại API khi F5.
    """
    context_prompt = _get_scope_prefix() + context_prompt
    data_json = json.dumps(data_dict, ensure_ascii=False)
    cache_key = f"ai_insight_{get_cache_key(data_json, context_prompt)}"

    container = target_container if target_container is not None else st.empty()

    def _build_html(content, is_typing=False):
        cursor = "<span style='border-right:2px solid #FF5200;margin-left:2px;opacity:0.7'></span>" if is_typing else ""
        return (
            f'<div class="ai-insight-container" style="{custom_style}">'
            f'<div class="ai-header">'

            f'<h4 class="ai-title">{title}</h4>'
            f'<div class="ai-badge">{badge}</div>'
            f'</div>'
            f'<div class="ai-content">{format_ai_html(content)}{cursor}</div>'
            f'</div>'
        )

    if cache_key in st.session_state:
        container.markdown(_build_html(sanitize_ai_insight_text(st.session_state[cache_key])), unsafe_allow_html=True)
    else:
        full_text = ""
        for chunk in generate_ees_insight_stream(data_json, context_prompt):
            full_text += chunk
            container.markdown(_build_html(full_text, is_typing=True), unsafe_allow_html=True)
        final_text = sanitize_ai_insight_text(full_text)
        st.session_state[cache_key] = final_text
        container.markdown(_build_html(final_text), unsafe_allow_html=True)

def render_ai_insight_card_dual(
        title, data_dict, prompt_short, prompt_long,
        badge="EES-Analyzer-v2.0", custom_style=""):
    # Short: auto-streams on load.  Long: lazy on button click.  Both cached.
    _sp = _get_scope_prefix()
    prompt_short = _sp + prompt_short
    prompt_long  = _sp + prompt_long
    data_json = json.dumps(data_dict, ensure_ascii=False)
    ck_s = f"ai_insight_{get_cache_key(data_json, prompt_short)}"
    ck_l = f"ai_insight_long_{get_cache_key(data_json, prompt_long)}"
    ekey = f"ai_expand_{ck_s[:14]}"
    dbrd = "margin-top:12px;border-top:2px solid rgba(67,24,255,0.18);"

    def _html(content, is_typing=False, xs=''):
        cur = (
            "<span style='border-right:2px solid #FF5200;"
            "margin-left:2px;opacity:0.7'></span>"
            if is_typing else ''
        )
        s = f"{custom_style} {xs}".strip()
        return (
            f'<div class="ai-insight-container" style="{s}">'
            f'<div class="ai-header">'
            f'<h4 class="ai-title">{title}</h4>'
            f'<div class="ai-badge">{badge}</div>'
            '</div>'
            f'<div class="ai-content">{format_ai_html(content)}{cur}</div>'
            '</div>'
        )

    sc = st.empty()
    if ck_s in st.session_state:
        sc.markdown(_html(sanitize_ai_insight_text(st.session_state[ck_s])), unsafe_allow_html=True)
    else:
        txt = ""
        for chunk in generate_ees_insight_stream(data_json, prompt_short):
            txt += chunk
            sc.markdown(_html(txt, is_typing=True), unsafe_allow_html=True)
        final_short = sanitize_ai_insight_text(txt)
        st.session_state[ck_s] = final_short
        sc.markdown(_html(final_short), unsafe_allow_html=True)

    col_btn, _ = st.columns([1, 4])
    with col_btn:
        if not st.session_state.get(ekey):
            if st.button("Xem phân tích chi tiết",
                         key=f"btn_exp_{ck_s[:12]}"):
                st.session_state[ekey] = True
        else:
            if st.button("Thu gọn",
                         key=f"btn_col_{ck_s[:12]}"):
                del st.session_state[ekey]

    if st.session_state.get(ekey):
        lc = st.empty()
        if ck_l in st.session_state:
            lc.markdown(
                _html(sanitize_ai_insight_text(st.session_state[ck_l]), xs=dbrd),
                unsafe_allow_html=True
            )
        else:
            txt = ""
            for chunk in generate_ees_insight_stream(data_json, prompt_long):
                txt += chunk
                lc.markdown(
                    _html(txt, is_typing=True, xs=dbrd),
                    unsafe_allow_html=True
                )
            final_long = sanitize_ai_insight_text(txt)
            st.session_state[ck_l] = final_long
            lc.markdown(_html(final_long, xs=dbrd), unsafe_allow_html=True)
