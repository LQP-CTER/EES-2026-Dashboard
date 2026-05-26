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
    <style>
    .admin-card {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 24px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        margin-bottom: 24px;
        height: 100%;
    }
    .status-badge {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        padding: 8px 16px;
        border-radius: 20px;
        font-weight: 700;
        font-size: 0.9rem;
    }
    .status-locked {
        background: #FEF2F2;
        color: #DC2626;
        border: 1px solid #FECACA;
    }
    .status-active {
        background: #F0FDF4;
        color: #16A34A;
        border: 1px solid #BBF7D0;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="pg-header">
        <div>
            <p class="pg-eyebrow" style="color: #FF5200;">GHN OWNER PRIVILEGE</p>
            <h1 class="pg-title">Quản trị Hệ thống Dashboard</h1>
            <p class="pg-subtitle">Quyền truy cập cao nhất. Cẩn trọng khi thay đổi các cấu hình tại đây.</p>
        </div>
        <span class="pg-badge" style="background: #FFF3EE; color: #FF5200; border-color: #FFD0B9;">
            <span class="pg-badge-dot" style="background: #FF5200;"></span>Owner Mode
        </span>
    </div>
    """, unsafe_allow_html=True)
    
    state = load_state()
    is_locked = state.get("is_locked", False)
    
    col1, col2 = st.columns([3, 2])
    
    with col1:
        st.markdown('<div class="admin-card">', unsafe_allow_html=True)
        st.markdown("### 🔒 Kiểm soát Truy cập (Access Control)")
        st.write("Sử dụng tính năng này để tạm thời chặn người dùng truy cập vào báo cáo (ví dụ: khi đang cập nhật dữ liệu hoặc bảo trì hệ thống).")
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        new_status = st.toggle(
            "Khóa Dashboard (Kích hoạt chế độ bảo trì)", 
            value=is_locked,
            help="Bật tùy chọn này sẽ lập tức chặn mọi luồng xem báo cáo của nhân viên."
        )
        
        if new_status != is_locked:
            state["is_locked"] = new_status
            save_state(state)
            st.toast("Trạng thái đã được cập nhật thành công!", icon="✅")
            st.rerun()
            
        st.markdown('</div>', unsafe_allow_html=True)
        
    with col2:
        st.markdown('<div class="admin-card">', unsafe_allow_html=True)
        st.markdown("### 📊 Trạng thái Hiện tại")
        
        if is_locked:
            st.markdown("""
            <div class="status-badge status-locked">
                🔴 HỆ THỐNG ĐANG KHÓA
            </div>
            <p style="margin-top: 12px; font-size: 0.85rem; color: #64748B;">
                Người dùng chỉ thấy màn hình bảo trì. Các URL truy cập báo cáo đều bị chặn.
            </p>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="status-badge status-active">
                🟢 ĐANG HOẠT ĐỘNG
            </div>
            <p style="margin-top: 12px; font-size: 0.85rem; color: #64748B;">
                Người dùng có thể truy cập toàn bộ hệ thống báo cáo bình thường.
            </p>
            """, unsafe_allow_html=True)
            
        st.markdown("<hr style='margin: 20px 0; border-color: #E2E8F0;'>", unsafe_allow_html=True)
        
        st.markdown("### 👁️ Chế độ Xem trước")
        st.write("Chuyển sang góc nhìn của người dùng.")
        if st.button("Xem Dashboard như User", use_container_width=True, type="primary"):
            st.session_state.preview_mode = True
            st.rerun()
            
        st.markdown('</div>', unsafe_allow_html=True)
