import streamlit as st
import os
import json
import re
from groq import Groq

import hashlib

def get_groq_client():
    try:
        api_key = st.secrets.get("GROQ_API_KEY", os.environ.get("GROQ_API_KEY", ""))
        if not api_key:
            api_key = os.environ.get("GROQ_API_KEY", "")
        if api_key:
            return Groq(api_key=api_key)
    except Exception as e:
        print("Error initializing Groq client:", e)
    return None

def get_cache_key(data_json, context_prompt):
    return hashlib.md5((data_json + context_prompt).encode()).hexdigest()

def generate_ees_insight_stream(data_json, context_prompt, lang='VN'):
    client = get_groq_client()
    if not client:
        yield "⚠️ Cảnh báo: Lỗi khởi tạo Groq. Vui lòng kiểm tra lại GROQ_API_KEY trong file secrets.toml"
        return

    system_prompt = f"""
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
    
    models_to_try = [
        "qwen-2.5-32b",
        "llama-3.3-70b-versatile",
        "llama-3.1-8b-instant",
        "mixtral-8x7b-32768",
        "gemma2-9b-it"
    ]
    
    last_error = ""
    import time
    for model in models_to_try:
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
            return  # Thành công thì thoát luôn
        except Exception as e:
            last_error = str(e)
            # Nếu lỗi Rate Limit (429), nghỉ 2s rồi thử model tiếp theo
            if "rate_limit_exceeded" in str(e).lower() or "429" in str(e):
                time.sleep(2)
            continue
            
    yield f"Lỗi kết nối AI (Groq API) sau khi thử nhiều model: {last_error}"


def validate_warning_signals_with_ai(signals_batch):
    """
    Dùng LLM (Groq) làm 'thẩm phán' xác nhận lại tín hiệu cảnh báo.
    Rule-based phát hiện ứng viên, LLM xác nhận ngữ cảnh thực sự tiêu cực hay không.
    
    Args:
        signals_batch: list of dict, mỗi dict có keys: 'index', 'signal_type', 'phrase', 'full_text'
    Returns:
        dict {index: {'valid': bool, 'reason': str}}
    """
    if not signals_batch:
        return {}
    
    # Check cache first
    cache_key_data = json.dumps([s['full_text'][:100] + s['phrase'] for s in signals_batch], ensure_ascii=False)
    cache_key = f"ai_validate_{hashlib.md5(cache_key_data.encode()).hexdigest()}"
    
    if cache_key in st.session_state:
        return st.session_state[cache_key]
    
    client = get_groq_client()
    if not client:
        # Nếu không có API key, giữ nguyên tất cả signals
        return {s['index']: {'valid': True, 'reason': 'Không có AI để xác nhận'} for s in signals_batch}
    
    # Xây prompt cho LLM
    items_text = ""
    for i, s in enumerate(signals_batch[:20]):  # Giới hạn 20 items mỗi batch
        items_text += f"\n[{i}] Loại: {s['signal_type']} | Từ khóa: \"{s['phrase']}\" | Câu gốc: \"{s['full_text'][:200]}\""
    
    system_prompt = f"""Bạn là chuyên gia phân tích ngôn ngữ tiếng Việt trong bối cảnh khảo sát nhân viên.

NHIỆM VỤ: Xác định mỗi câu phản hồi dưới đây THỰC SỰ mang tín hiệu tiêu cực hay không.

HƯỚNG DẪN QUAN TRỌNG:
- Nếu câu nói mang ý tích cực hoặc trung lập (VD: "vui vẻ bớt áp lực", "làm nhiều thu nhập cao", "có đồng nghiệp giúp đỡ nên bớt mệt", "áp lực nhưng vượt qua được") → Trả "KHÔNG" (false positive).
- Nếu câu nói thực sự phàn nàn, tiêu cực, kiệt sức (VD: "quá áp lực không chịu nổi", "mệt mỏi muốn nghỉ", "làm nhiều mà lương thấp") → Trả "CÓ" (true positive).
- Chú ý: "bớt áp lực", "giảm áp lực", "không áp lực" → KHÔNG phải cảnh báo.
- "làm nhiều" + ngữ cảnh tích cực (thu nhập cao, vui) → KHÔNG phải cảnh báo.

Danh sách cần phân loại:
{items_text}

YÊU CẦU OUTPUT: Trả lời CHÍNH XÁC theo format JSON array, mỗi phần tử là một object:
[{{"id": 0, "valid": true/false, "reason": "lý do ngắn gọn"}}]

CHỈ TRẢ JSON, KHÔNG viết gì thêm."""

    models_to_try = [
        "qwen-2.5-32b",
        "llama-3.3-70b-versatile",
        "llama-3.1-8b-instant",
    ]
    
    import time
    for model in models_to_try:
        try:
            response = client.chat.completions.create(
                messages=[{"role": "system", "content": system_prompt}],
                model=model,
                temperature=0.1,
                max_tokens=2000,
                stream=False
            )
            raw = response.choices[0].message.content.strip()
            
            # Parse JSON từ response
            # Tìm JSON array trong response
            json_match = re.search(r'\[.*\]', raw, re.DOTALL)
            if json_match:
                results = json.loads(json_match.group())
            else:
                results = json.loads(raw)
            
            # Map kết quả về index gốc
            output = {}
            for r in results:
                batch_idx = r.get('id', -1)
                if 0 <= batch_idx < len(signals_batch):
                    original_idx = signals_batch[batch_idx]['index']
                    output[original_idx] = {
                        'valid': r.get('valid', True),
                        'reason': r.get('reason', '')
                    }
            
            # Bổ sung các signal không có trong kết quả (giữ nguyên)
            for s in signals_batch:
                if s['index'] not in output:
                    output[s['index']] = {'valid': True, 'reason': 'Chưa xác nhận'}
            
            st.session_state[cache_key] = output
            return output
            
        except Exception as e:
            if "rate_limit_exceeded" in str(e).lower() or "429" in str(e):
                time.sleep(2)
            continue
    
    # Fallback: giữ tất cả nếu LLM fail
    fallback = {s['index']: {'valid': True, 'reason': 'LLM không khả dụng'} for s in signals_batch}
    st.session_state[cache_key] = fallback
    return fallback

def format_ai_html(text):
    html = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', text)
    html = re.sub(r'\*(.*?)\*', r'<em>\1</em>', html)
    html = re.sub(r'(?m)^[-*]\s+', '<br>• ', html)
    html = re.sub(r'(?m)^\d+\.\s+', '<br>🔹 ', html)
    html = html.replace('\n', '<br>')
    return html

def render_ai_insight_card(title, data_dict, context_prompt, badge="EES-Analyzer-v2.0", custom_style=""):
    """
    Render a standard Glassmorphism AI insight card with Typing Effect.
    Uses session_state to cache the result and prevent re-streaming.
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
        # Load from cache
        container.markdown(_build_html(st.session_state[cache_key]), unsafe_allow_html=True)
    else:
        # Stream from API
        full_text = ""
        for chunk in generate_ees_insight_stream(data_json, context_prompt):
            full_text += chunk
            container.markdown(_build_html(full_text, is_typing=True), unsafe_allow_html=True)
        
        # Save to cache when done
        st.session_state[cache_key] = full_text
        container.markdown(_build_html(full_text), unsafe_allow_html=True)
