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
    
    try:
        stream = client.chat.completions.create(
            messages=[{"role": "system", "content": system_prompt}],
            model="qwen-2.5-32b",
            temperature=0.3,
            max_tokens=400,
            stream=True
        )
        for chunk in stream:
            if chunk.choices[0].delta.content is not None:
                yield chunk.choices[0].delta.content
    except Exception as e:
        try:
            # Fallback
            stream = client.chat.completions.create(
                messages=[{"role": "system", "content": system_prompt}],
                model="llama-3.1-8b-instant",
                temperature=0.3,
                max_tokens=400,
                stream=True
            )
            for chunk in stream:
                if chunk.choices[0].delta.content is not None:
                    yield chunk.choices[0].delta.content
        except Exception as e2:
            yield f"Lỗi kết nối AI (Groq API): {str(e2)}"

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
        cursor = "<span style='animation: blink 1s step-end infinite; border-right: 2px solid #FF5200; margin-left: 2px;'></span>" if is_typing else ""
        return f"""
        <div class="ai-insight-container" style="{custom_style}">
            <div class="ai-header" style="margin-bottom: 12px;">
                <div class="ai-icon">✨</div>
                <h4 class="ai-title">{title}</h4>
                <div class="ai-badge">Model: {badge}</div>
            </div>
            <div class="ai-content" style="font-size: 0.9rem; transition: all 0.2s;">
                {format_ai_html(content)}{cursor}
            </div>
        </div>
        """

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
