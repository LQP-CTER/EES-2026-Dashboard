import streamlit as st
import os
import json
import re
import time
import hashlib
from groq import Groq

# ============================================================
# MULTI-PROVIDER AI CLIENT
# Groq: AI Insight cards (stream)
# Gemini: AI Validator + AI Insight fallback (non-stream, nhanh hơn)
# ============================================================

def get_groq_client():
    try:
        api_key = st.secrets.get("GROQ_API_KEY", os.environ.get("GROQ_API_KEY", ""))
        if not api_key:
            api_key = os.environ.get("GROQ_API_KEY", "")
        if api_key and api_key != "dien-api-key-cua-ban-vao-day":
            return Groq(api_key=api_key)
    except Exception as e:
        print("Error initializing Groq client:", e)
    return None


def get_gemini_client():
    try:
        import google.generativeai as genai
        api_key = st.secrets.get("GEMINI_API_KEY", os.environ.get("GEMINI_API_KEY", ""))
        if not api_key:
            api_key = os.environ.get("GEMINI_API_KEY", "")
        if api_key:
            genai.configure(api_key=api_key)
            return genai
    except Exception as e:
        print("Error initializing Gemini client:", e)
    return None


def get_cache_key(data_json, context_prompt):
    return hashlib.md5((data_json + context_prompt).encode()).hexdigest()


# ============================================================
# AI INSIGHT GENERATION (STREAM — Groq primary, Gemini fallback)
# ============================================================

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
2. Tuyệt đối KHÔNG DÙNG các từ ngữ quá kịch tính, cảm xúc, hoặc dịch gượng ép (ví dụ: TUYỆT ĐỐI KHÔNG dùng từ "đột biến", "kinh hoàng", "báo động đỏ", v.v.).
3. SỬ DỤNG ĐÚNG thuật ngữ chuyên ngành HR Analytics được chuẩn hóa: Engagement Index (EI), eNPS, Attrition Risk, Driver Analysis, Cohort, Root-cause, Turnover rate, Survival Analysis, Touchpoint, Moments that matter.
4. KHÔNG SỬ DỤNG ký tự Markdown như **, *, #. KHÔNG viết Tiêu đề (Headers). KHÔNG dùng danh sách gạch đầu dòng (Bullet points) hay đánh số.
5. BẮT BUỘC viết dưới dạng MỘT HOẶC HAI ĐOẠN VĂN bản liền mạch (Paragraphs). Đi thẳng vào insight cốt lõi và số liệu, tránh nói lời sáo rỗng.
6. Độ dài tối đa: 2-3 câu ngắn gọn, súc tích, đậm chất tư duy chiến lược.
7. Để nhấn mạnh, HÃY DÙNG thẻ HTML: `<span class="ai-highlight">` cho nhóm xuất sắc/chỉ số tốt và `<span class="ai-warning">` cho rủi ro/chỉ số xấu.
8. Ngôn ngữ: {'Tiếng Việt' if lang == 'VN' else 'English'}.
"""


def _try_gemini_insight(data_json, context_prompt, lang='VN'):
    """Gọi Gemini (non-stream) làm fallback cho AI Insight."""
    genai = get_gemini_client()
    if not genai:
        return None
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        prompt = _build_insight_system_prompt(data_json, context_prompt, lang)
        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=0.3,
                max_output_tokens=400,
            )
        )
        return response.text
    except Exception as e:
        print(f"Gemini insight error: {e}")
        return None


def generate_ees_insight_stream(data_json, context_prompt, lang='VN'):
    client = get_groq_client()
    
    # Nếu không có Groq key → dùng Gemini thẳng
    if not client:
        result = _try_gemini_insight(data_json, context_prompt, lang)
        if result:
            yield result
        else:
            yield "⚠️ Cảnh báo: Không có API key hợp lệ. Vui lòng kiểm tra secrets.toml"
        return

    system_prompt = _build_insight_system_prompt(data_json, context_prompt, lang)
    
    groq_models = [
        "qwen-2.5-32b",
        "llama-3.3-70b-versatile",
        "llama-3.1-8b-instant",
        "mixtral-8x7b-32768",
        "gemma2-9b-it"
    ]
    
    last_error = ""
    for model in groq_models:
        try:
            stream = client.chat.completions.create(
                messages=[{"role": "system", "content": system_prompt}],
                model=model,
                temperature=0.3,
                max_tokens=400,
                stream=True
            )
            for chunk in stream:
                if chunk.choices[0].delta.content is not None:
                    yield chunk.choices[0].delta.content
            return  # Thành công
        except Exception as e:
            last_error = str(e)
            if "rate_limit_exceeded" in str(e).lower() or "429" in str(e):
                time.sleep(1)
            continue
    
    # Groq thất bại hoàn toàn → fallback sang Gemini
    result = _try_gemini_insight(data_json, context_prompt, lang)
    if result:
        yield result
    else:
        yield f"Lỗi kết nối tất cả AI providers: {last_error}"


# ============================================================
# AI VALIDATOR (NON-STREAM — Gemini primary, Groq fallback)
# Gemini nhanh hơn cho JSON tasks, dùng làm primary ở đây
# ============================================================

def validate_warning_signals_with_ai(signals_batch):
    """
    Dùng LLM làm 'thẩm phán' xác nhận lại tín hiệu cảnh báo.
    Gemini là primary (nhanh, free), Groq là fallback.
    
    Args:
        signals_batch: list of dict với keys: 'index', 'signal_type', 'phrase', 'full_text'
    Returns:
        dict {index: {'valid': bool, 'reason': str}}
    """
    if not signals_batch:
        return {}
    
    # Cache check
    cache_key_data = json.dumps([s['full_text'][:100] + s['phrase'] for s in signals_batch], ensure_ascii=False)
    cache_key = f"ai_validate_{hashlib.md5(cache_key_data.encode()).hexdigest()}"
    
    if cache_key in st.session_state:
        return st.session_state[cache_key]
    
    # Build prompt
    items_text = ""
    for i, s in enumerate(signals_batch[:20]):
        items_text += f"\n[{i}] Loại: {s['signal_type']} | Từ khóa: \"{s['phrase']}\" | Câu gốc: \"{s['full_text'][:200]}\""
    
    validation_prompt = f"""Bạn là chuyên gia phân tích ngôn ngữ tiếng Việt trong bối cảnh khảo sát nhân viên.

NHIỆM VỤ: Xác định mỗi câu phản hồi dưới đây THỰC SỰ mang tín hiệu tiêu cực hay không.

HƯỚNG DẪN QUAN TRỌNG:
- Nếu câu nói mang ý tích cực hoặc trung lập (VD: "vui vẻ bớt áp lực", "làm nhiều thu nhập cao", "có đồng nghiệp giúp đỡ nên bớt mệt", "áp lực nhưng vượt qua được") → valid: false
- Nếu câu nói thực sự phàn nàn, tiêu cực, kiệt sức (VD: "quá áp lực không chịu nổi", "mệt mỏi muốn nghỉ", "làm nhiều mà lương thấp") → valid: true
- "bớt áp lực", "giảm áp lực", "không áp lực" → valid: false
- "làm nhiều" + ngữ cảnh tích cực → valid: false

Danh sách cần phân loại:
{items_text}

OUTPUT: Chỉ trả JSON array, không viết gì thêm:
[{{"id": 0, "valid": true/false, "reason": "lý do ngắn"}}]"""

    def _parse_ai_result(raw_text):
        """Parse JSON từ response text."""
        json_match = re.search(r'\[.*?\]', raw_text, re.DOTALL)
        if json_match:
            return json.loads(json_match.group())
        return json.loads(raw_text)
    
    def _map_results(results, signals_batch):
        """Map AI results về index gốc."""
        output = {}
        for r in results:
            batch_idx = r.get('id', -1)
            if 0 <= batch_idx < len(signals_batch):
                original_idx = signals_batch[batch_idx]['index']
                output[original_idx] = {
                    'valid': r.get('valid', True),
                    'reason': r.get('reason', '')
                }
        # Bổ sung items không có trong kết quả
        for s in signals_batch:
            if s['index'] not in output:
                output[s['index']] = {'valid': True, 'reason': 'Chưa xác nhận'}
        return output

    # ── Try Gemini first (primary for JSON tasks) ──
    genai = get_gemini_client()
    if genai:
        try:
            model = genai.GenerativeModel('gemini-1.5-flash')
            response = model.generate_content(
                validation_prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.1,
                    max_output_tokens=2000,
                )
            )
            results = _parse_ai_result(response.text.strip())
            output = _map_results(results, signals_batch)
            st.session_state[cache_key] = output
            return output
        except Exception as e:
            print(f"Gemini validator error: {e}")
    
    # ── Fallback: Try Groq ──
    client = get_groq_client()
    if client:
        groq_models = ["qwen-2.5-32b", "llama-3.3-70b-versatile", "llama-3.1-8b-instant"]
        for model in groq_models:
            try:
                response = client.chat.completions.create(
                    messages=[{"role": "system", "content": validation_prompt}],
                    model=model,
                    temperature=0.1,
                    max_tokens=2000,
                    stream=False
                )
                raw = response.choices[0].message.content.strip()
                results = _parse_ai_result(raw)
                output = _map_results(results, signals_batch)
                st.session_state[cache_key] = output
                return output
            except Exception as e:
                if "rate_limit_exceeded" in str(e).lower() or "429" in str(e):
                    time.sleep(2)
                continue
    
    # Cả 2 fail → giữ tất cả
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
    html = re.sub(r'(?m)^\d+\.\s+', '<br>🔹 ', html)
    html = html.replace('\n', '<br>')
    return html


def render_ai_insight_card(title, data_dict, context_prompt, badge="EES-Analyzer-v2.0", custom_style=""):
    """
    Render AI insight card với Groq streaming + Gemini fallback.
    Cache kết quả trong session_state để không gọi lại API.
    """
    data_json = json.dumps(data_dict, ensure_ascii=False)
    cache_key = f"ai_insight_{get_cache_key(data_json, context_prompt)}"
    
    container = st.empty()
    
    def _build_html(content, is_typing=False):
        cursor = "<span style='border-right:2px solid #FF5200;margin-left:2px;opacity:0.7'></span>" if is_typing else ""
        html = (
            f'<div class="ai-insight-container" style="{custom_style}">'
            f'<div class="ai-header">'
            f'<div class="ai-icon">AI</div>'
            f'<h4 class="ai-title">{title}</h4>'
            f'<div class="ai-badge">{badge}</div>'
            f'</div>'
            f'<div class="ai-content">{format_ai_html(content)}{cursor}</div>'
            f'</div>'
        )
        return html

    if cache_key in st.session_state:
        container.markdown(_build_html(st.session_state[cache_key]), unsafe_allow_html=True)
    else:
        full_text = ""
        for chunk in generate_ees_insight_stream(data_json, context_prompt):
            full_text += chunk
            container.markdown(_build_html(full_text, is_typing=True), unsafe_allow_html=True)
        
        st.session_state[cache_key] = full_text
        container.markdown(_build_html(full_text), unsafe_allow_html=True)
