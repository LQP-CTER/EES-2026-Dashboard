import streamlit as st
import json
import os
from utils.ai_generator import _get_groq_keys

APP_STATE_FILE = os.path.join("config", "app_state.json")

def load_state():
    if os.path.exists(APP_STATE_FILE):
        with open(APP_STATE_FILE, "r") as f:
            return json.load(f)
    return {
        "is_locked": False,
        "announcement": {"active": False, "text": ""},
        "ai_config": {"temperature": 0.3}
    }

def save_state(state):
    with open(APP_STATE_FILE, "w") as f:
        json.dump(state, f, indent=4)

def render():
    st.markdown("""
    <div class="pg-header" style="margin-bottom: 24px; border-bottom: 2px solid #F1F5F9; padding-bottom: 24px;">
        <div>
            <p class="pg-eyebrow" style="color: #64748B; letter-spacing: 0.15em;">SYSTEM ADMINISTRATION</p>
            <h1 class="pg-title" style="color: #0F172A; font-weight: 700; letter-spacing: -0.02em;">Workspace Access Control</h1>
            <p class="pg-subtitle" style="color: #475569; font-size: 0.95rem;">Thiết lập trạng thái hoạt động và quyền truy cập toàn cầu cho EES 2026 Dashboard.</p>
        </div>
        <span class="pg-badge" style="background: #F8FAFC; color: #475569; border: 1px solid #E2E8F0; border-radius: 4px; font-weight: 600;">
            <span class="pg-badge-dot" style="background: #3B82F6;"></span>Authorized Session
        </span>
    </div>
    """, unsafe_allow_html=True)
    
    state = load_state()
    is_locked = state.get("is_locked", False)
    announcement = state.get("announcement", {"active": False, "text": ""})
    ai_config = state.get("ai_config", {"temperature": 0.3})
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        with st.container(border=True):
            st.markdown("#### 🔒 Quản lý Truy cập")
            st.caption("Kích hoạt chế độ bảo trì sẽ lập tức chặn quyền truy cập đối với tất cả tài khoản thông thường.")
            
            new_status = st.toggle("Kích hoạt Chế độ Bảo trì", value=is_locked)
            if new_status != is_locked:
                state["is_locked"] = new_status
                save_state(state)
                st.rerun()

    with col2:
        with st.container(border=True):
            st.markdown("#### 📊 Trạng thái Hệ thống")
            st.caption("Tình trạng kết nối và phục vụ báo cáo cho người dùng ngoài.")
            if is_locked:
                st.error("**ĐANG BẢO TRÌ (MAINTENANCE)** - Hệ thống đang chặn truy cập ngoài.")
            else:
                st.success("**HOẠT ĐỘNG BÌNH THƯỜNG (ONLINE)** - Đang phục vụ toàn bộ user.")

    st.markdown("<br>", unsafe_allow_html=True)

    col3, col4 = st.columns([1, 1])
    
    with col3:
        with st.container(border=True):
            st.markdown("#### 📢 Thông báo Toàn cục (Banner)")
            st.caption("Cài đặt thông báo nổi bật ở đầu trang của tất cả người dùng.")
            new_ann_text = st.text_area("Nội dung thông báo", value=announcement.get("text", ""), height=100)
            new_ann_active = st.toggle("Hiển thị Thông báo", value=announcement.get("active", False))
            
            if st.button("Lưu Thông báo", use_container_width=True):
                state["announcement"] = {"text": new_ann_text, "active": new_ann_active}
                save_state(state)
                st.toast("Đã cập nhật thông báo!", icon="✅")
                st.rerun()

    with col4:
        with st.container(border=True):
            st.markdown("#### 🧠 Cấu hình & Dữ liệu")
            
            groq_keys = _get_groq_keys()
            n_keys = len(groq_keys)
            st.caption(f"Trạng thái kết nối Groq API: **{n_keys} key(s) khả dụng**")
            
            new_temp = st.slider("Độ sáng tạo AI (Temperature)", 0.0, 1.0, float(ai_config.get("temperature", 0.3)), 0.1)
            
            st.markdown("<br>", unsafe_allow_html=True)
            c41, c42 = st.columns(2)
            with c41:
                if st.button("Lưu Cấu hình AI", use_container_width=True):
                    state["ai_config"] = {"temperature": new_temp}
                    save_state(state)
                    st.toast("Đã lưu cấu hình AI!", icon="✅")
            with c42:
                if st.button("Làm mới Bộ nhớ đệm", use_container_width=True):
                    st.cache_data.clear()
                    st.toast("Đã xóa bộ nhớ đệm thành công!", icon="✅")

    st.markdown("---")
    if st.button("Giả lập Truy cập User", use_container_width=True, type="primary"):
        st.session_state.preview_mode = True
        st.rerun()


