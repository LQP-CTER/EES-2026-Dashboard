import streamlit as st
import json
import os

APP_STATE_FILE = os.path.join("config", "app_state.json")

def load_state():
    if os.path.exists(APP_STATE_FILE):
        with open(APP_STATE_FILE, "r") as f:
            return json.load(f)
    return {"is_locked": False}

def save_state(state):
    with open(APP_STATE_FILE, "w") as f:
        json.dump(state, f, indent=4)

def render():
    st.markdown("""
    <div class="pg-header">
        <div>
            <p class="pg-eyebrow">ADMIN CONTROL PANEL</p>
            <h1 class="pg-title">Quản trị Hệ thống Dashboard</h1>
            <p class="pg-subtitle">Quyền truy cập cao nhất. Cẩn trọng khi thay đổi các cấu hình tại đây.</p>
        </div>
        <span class="pg-badge">
            <span class="pg-badge-dot"></span>Owner Mode
        </span>
    </div>
    """, unsafe_allow_html=True)
    
    state = load_state()
    is_locked = state.get("is_locked", False)
    
    st.markdown("### Trạng thái Dashboard")
    st.write("Sử dụng nút dưới đây để khóa hệ thống. Khi bị khóa, người dùng thường sẽ không thể truy cập bất kỳ báo cáo nào và chỉ thấy trang thông báo bảo trì.")
    
    # Toggle logic
    new_status = st.toggle("Khóa Dashboard (Bảo trì hệ thống)", value=is_locked)
    
    if new_status != is_locked:
        state["is_locked"] = new_status
        save_state(state)
        st.success("Đã cập nhật trạng thái hệ thống thành công!")
        st.rerun()
        
    st.markdown("---")
    
    # Action buttons
    col1, col2 = st.columns([1, 1])
    with col1:
        st.info("Trạng thái hiện tại: " + ("🔴 ĐANG KHÓA" if is_locked else "🟢 HOẠT ĐỘNG BÌNH THƯỜNG"))
    
    with col2:
        if st.button("Xem Dashboard như User thường"):
            st.session_state.preview_mode = True
            st.rerun()
