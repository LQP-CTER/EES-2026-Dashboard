import streamlit as st
import os
import json
import re
import time
import hashlib
from groq import Groq

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
    return hashlib.md5((data_json + context_prompt).encode()).hexdigest()


# ============================================================
# AI INSIGHT GENERATION (STREAM)
# Thử Key 1 → nếu 429 chuyển Key 2 → thử từng model
# ============================================================

# Danh sách model đã kiểm tra thực tế qua API Groq (2026-05-28)
# Chỉ giữ các model đã PASS test - các model khác đã bị decommissioned
GROQ_MODELS = [
    "llama-3.3-70b-versatile",              # Mạnh nhất, ưu tiên 1
    "meta-llama/llama-4-scout-17b-16e-instruct",  # Llama 4 Scout - nhanh
    "llama-3.1-8b-instant",                # Nhẹ, fallback nhanh
    "qwen/qwen3-32b",                      # Qwen3 - trong active list
    "compound-beta",                       # Groq compound model
]

def _build_insight_system_prompt(data_json, context_prompt, lang='VN'):
    return f"""
Bạn là một Chuyên gia Trải nghiệm Nhân viên (Employee Experience - EX) & Phân tích Dữ liệu Nhân sự (People Analytics/Quantitative Analyst) cấp cao.
Dưới đây là dữ liệu trích xuất từ khảo sát Employee Engagement Survey (EES).
Dữ liệu JSON:
{data_json}

Nhiệm vụ:
{context_prompt}

YÊU CẦU ĐỊNH DẠNG VÀ TÔNG VĂN NGHIÊM NGẶT:
1. Tông văn (Tone of voice): Khách quan, chuyên môn sâu, dựa trên dữ liệu (data-driven), chiến lược và đi thẳng vào vấn đề.
2. Tuyệt đối KHÔNG DÙNG các từ ngữ quá kịch tính (ví dụ: TUYỆT ĐỐI KHÔNG dùng "đột biến", "kinh hoàng", "báo động đỏ").
3. SỬ DỤNG ĐÚNG thuật ngữ chuyên ngành HR Analytics: Engagement Index (EI), eNPS, Attrition Risk, Driver Analysis, Cohort, Root-cause, Turnover rate.
4. KHÔNG SỬ DỤNG ký tự Markdown như **, *, #. KHÔNG viết Tiêu đề. KHÔNG dùng Bullet points.
5. TUYỆT ĐỐI KHÔNG mở đầu bằng các từ chào hỏi (ví dụ: "Kính gửi...", "Chào bạn...", "Thưa..."). Bắt đầu phân tích ngay lập tức.
6. TUYỆT ĐỐI KHÔNG viết các câu kết luận sáo rỗng, chung chung (ví dụ: "cần tiếp tục theo dõi...", "cần lưu ý rằng...", "điều này cho thấy..."). Chỉ viết Insight thực sự có giá trị.
7. BẮT BUỘC viết dưới dạng MỘT HOẶC HAI ĐOẠN VĂN liền mạch. Đi thẳng vào insight cốt lõi.
8. Độ dài tối đa: 2-3 câu ngắn gọn, súc tích, đậm chất tư duy chiến lược.
9. Để nhấn mạnh, DÙNG thẻ HTML: `<span class="ai-highlight">` cho chỉ số tốt và `<span class="ai-warning">` cho rủi ro.
10. Ngôn ngữ: {'Tiếng Việt' if lang == 'VN' else 'English'}.
"""


def generate_ees_insight_stream(data_json, context_prompt, lang='VN'):
    system_prompt = _build_insight_system_prompt(data_json, context_prompt, lang)
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
    # Thử từng key, với mỗi key thử từng model. Groq rate limit là theo model,
    # nên nếu 1 model bị 429 thì vẫn tiếp tục thử model khác trên cùng key đó.
    for client in all_clients:
        for model in GROQ_MODELS:
            try:
                stream = client.chat.completions.create(
                    messages=[{"role": "system", "content": system_prompt}],
                    model=model,
                    temperature=ai_temp,
                    max_tokens=1500,
                    stream=True
                )
                for chunk in stream:
                    if chunk.choices[0].delta.content is not None:
                        yield chunk.choices[0].delta.content
                return  # Thành công
            except Exception as e:
                last_error = str(e)
                if "rate_limit_exceeded" in last_error.lower() or "429" in last_error:
                    time.sleep(0.5)  # Nghỉ xíu rồi thử model khác
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
    validator_models = ["llama-3.3-70b-versatile", "meta-llama/llama-4-scout-17b-16e-instruct", "llama-3.1-8b-instant", "qwen/qwen3-32b", "compound-beta"]
    for client in get_groq_clients_all():
        for model in validator_models:
            try:
                response = client.chat.completions.create(
                    messages=[{"role": "system", "content": validation_prompt}],
                    model=model,
                    temperature=0.1,
                    max_tokens=2000,
                    stream=False
                )
                raw = response.choices[0].message.content.strip()
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

def format_ai_html(text):
    html = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', text)
    html = re.sub(r'\*(.*?)\*', r'<em>\1</em>', html)
    html = re.sub(r'(?m)^[-*]\s+', '<br>• ', html)
    html = re.sub(r'(?m)^\d+\.\s+', '<br> ', html)
    html = html.replace('\n', '<br>')
    return html


def render_ai_insight_card(title, data_dict, context_prompt, badge="EES-Analyzer-v2.0", custom_style="", target_container=None):
    """
    Render AI insight card với Groq dual-key streaming.
    Cache kết quả trong session_state để không gọi lại API khi F5.
    """
    data_json = json.dumps(data_dict, ensure_ascii=False)
    cache_key = f"ai_insight_{get_cache_key(data_json, context_prompt)}"

    container = target_container if target_container is not None else st.empty()

    def _build_html(content, is_typing=False):
        cursor = "<span style='border-right:2px solid #FF5200;margin-left:2px;opacity:0.7'></span>" if is_typing else ""
        return (
            f'<div class="ai-insight-container" style="{custom_style}">'
            f'<div class="ai-header">'
            f'<div class="ai-icon"><img src="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAIAAAD8GO2jAAADT0lEQVR4nO1WTWwVVRT+zp15f33PlhojIivKAl0RiKgNCalhUV2ZEBODC+PPorpxQQIoG10TMLjDjQloSKORjUlTF6AYFdPUrjRFTU0auwBCAi/w/mbmns+cmVc0ffPo66I7Tu7M3HvPPd+558w5514hic0kt6noeKhgAAr7cnp/vnQfgOiNDMlYPdObHUVh/jTJZh3UdMu0N4FKVcKCMZMYrUZqTMoCIU6GRnKN6FFAQoTNuh7dJ3frCARJIkHAexGePSjHv7Ylpw/L3CWtlUQTBCE9WRsJTs1JdTQTH8ACQG4u40bsyuAQ4CHFgFcu8u1/bMvfX0Q5CG7VGUKaYBvceqcvztp/kFlw+7p+/Jrs3Me7N93laXjP0z9i7huGBfNHEuG5l+XIfoROXzgsw49zad4d+UJGt/VaYN7OoXZDo5Z2Wsn7BzgBf/adbDpemI1/nc36/uy7xjp+QDtNjdpsN3KR+iggqT45Ns4J6KGCX7lG9UziLiuJqd6vXNNDRU4gOfY8ve8Hk1eLfGKvKxdk4Spqjjt2u+27zPVBaHFFtQ7Ebd/FHbtRc7Lwi/5w4b7gGspTIOnk5XMoCCLF2B4bqu+yMm42HNvDSFEQfnfuP8F1FJBwjlELK4tSJBQYfTKN914iHt1mqVKkrCyaiHO9+d+nXEctiVtZIqF5Z7VCrLUUjXr6FUQta3nUoyCDKtdQGaYHSsD8DNUbirmF1tIhVTk/I2VIQlaGTeS++AMtMCAJi9y5Fx3hUAlLf/HzE3CBNQOQrK/nP5ClP1kpoSMytlfCYroDGfREk8kpCKEqtQDTJ/2ZN3T5NwvQJNbl3/XMmzJ9EtUAqlZaJ6f64uRXU1U450+9KjNf4rESkgT3PKoOT4wZ9/rf0lA8EjAI5VZHX3olOPpVJjKwAptM8/nDF2X+Z2wJEBaQRBKpMYvOHOJj3PZ8Zlw+mpVKzZyTV037nwdZUWo39NP38O1nEgPF1dqYQCKwAEy+JVOfSLmWU4LWV7CqA4Au/oRL5/nHVanfsNXDW/HUuBx83T29///LNq4gE05Tr5sTWeBXR7p4qgbdH33gI1O9qbEStEo+MVwL3HVog2cy08UP3PLAt4r8/cjG1j+82Q1Am367/hffvQmZc1fQbgAAAABJRU5ErkJggg==" style="width: 16px; height: 16px;" alt="Ultramarines Logo" /></div>'
            f'<h4 class="ai-title">{title}</h4>'
            f'<div class="ai-badge">{badge}</div>'
            f'</div>'
            f'<div class="ai-content">{format_ai_html(content)}{cursor}</div>'
            f'</div>'
        )

    if cache_key in st.session_state:
        container.markdown(_build_html(st.session_state[cache_key]), unsafe_allow_html=True)
    else:
        full_text = ""
        for chunk in generate_ees_insight_stream(data_json, context_prompt):
            full_text += chunk
            container.markdown(_build_html(full_text, is_typing=True), unsafe_allow_html=True)
        st.session_state[cache_key] = full_text
        container.markdown(_build_html(full_text), unsafe_allow_html=True)
