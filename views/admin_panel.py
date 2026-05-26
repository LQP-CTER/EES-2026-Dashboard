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
        border-radius: 8px;
        padding: 32px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.02);
        margin-bottom: 24px;
        height: 100%;
    }
    .admin-card-header {
        display: flex;
        align-items: center;
        gap: 12px;
        margin-bottom: 20px;
        padding-bottom: 16px;
        border-bottom: 1px solid #F1F5F9;
    }
    .admin-card-icon {
        width: 32px;
        height: 32px;
        display: flex;
        align-items: center;
        justify-content: center;
        background: #F8FAFC;
        border-radius: 6px;
        color: #475569;
    }
    .admin-card-title {
        font-size: 1.05rem;
        font-weight: 600;
        color: #0F172A;
        margin: 0;
        letter-spacing: -0.01em;
    }
    .status-badge {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        padding: 6px 14px;
        border-radius: 4px;
        font-weight: 600;
        font-size: 0.8rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .status-locked {
        background: #FEF2F2;
        color: #B91C1C;
        border: 1px solid #FCA5A5;
    }
    .status-active {
        background: #F0FDF4;
        color: #15803D;
        border: 1px solid #86EFAC;
    }
    .indicator-dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
    }
    .indicator-red { background: #DC2626; }
    .indicator-green { background: #16A34A; }
    .stButton>button {
        border-radius: 6px !important;
        font-weight: 500 !important;
        letter-spacing: 0.02em !important;
        font-size: 0.85rem !important;
        padding: 12px 24px !important;
        border: 1px solid #E2E8F0 !important;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="pg-header" style="margin-bottom: 40px; border-bottom: 2px solid #F1F5F9; padding-bottom: 24px;">
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
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("""
        <div class="admin-card">
            <div class="admin-card-header">
                <div class="admin-card-icon">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="11" width="18" height="11" rx="2" ry="2"></rect><path d="M7 11V7a5 5 0 0 1 10 0v4"></path></svg>
                </div>
                <h3 class="admin-card-title">Quản lý Truy cập</h3>
            </div>
            <p style="color: #475569; font-size: 0.9rem; line-height: 1.6; margin-bottom: 24px;">
                Chuyển đổi trạng thái hoạt động của hệ thống. Kích hoạt chế độ bảo trì sẽ lập tức chặn quyền truy cập đối với tất cả tài khoản thông thường.
            </p>
        """, unsafe_allow_html=True)
        
        new_status = st.toggle(
            "Kích hoạt Chế độ Bảo trì", 
            value=is_locked,
            help="Tạm ngừng cung cấp báo cáo cho toàn bộ hệ thống."
        )
        
        if new_status != is_locked:
            state["is_locked"] = new_status
            save_state(state)
            st.rerun()
            
        st.markdown('</div>', unsafe_allow_html=True)
        
    with col2:
        st.markdown("""
        <div class="admin-card">
            <div class="admin-card-header">
                <div class="admin-card-icon">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path><polyline points="22 4 12 14.01 9 11.01"></polyline></svg>
                </div>
                <h3 class="admin-card-title">Trạng thái Hệ thống</h3>
            </div>
        """, unsafe_allow_html=True)
        
        if is_locked:
            st.markdown("""
            <div style="margin-bottom: 20px;">
                <div class="status-badge status-locked">
                    <div class="indicator-dot indicator-red"></div>
                    ĐANG BẢO TRÌ (MAINTENANCE)
                </div>
            </div>
            <p style="font-size: 0.9rem; color: #475569; line-height: 1.6; margin-bottom: 32px;">
                Hệ thống báo cáo đang tạm dừng hoạt động. Tất cả truy cập đều được điều hướng về trang thông báo bảo trì.
            </p>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="margin-bottom: 20px;">
                <div class="status-badge status-active">
                    <div class="indicator-dot indicator-green"></div>
                    HOẠT ĐỘNG BÌNH THƯỜNG (ONLINE)
                </div>
            </div>
            <p style="font-size: 0.9rem; color: #475569; line-height: 1.6; margin-bottom: 32px;">
                Hệ thống đang phục vụ. Người dùng có thể truy cập đầy đủ các phân hệ báo cáo dựa trên phân quyền sẵn có.
            </p>
            """, unsafe_allow_html=True)
            
        st.markdown("<hr style='border: none; border-top: 1px solid #F1F5F9; margin: 0 0 24px 0;'>", unsafe_allow_html=True)
        
        st.markdown("""
            <p style="color: #0F172A; font-weight: 600; font-size: 0.95rem; margin-bottom: 8px;">Môi trường Giả lập (Preview)</p>
            <p style="color: #475569; font-size: 0.85rem; margin-bottom: 16px;">Mô phỏng phiên truy cập để kiểm tra tính toàn vẹn của báo cáo.</p>
        """, unsafe_allow_html=True)
        
        if st.button("Truy cập với quyền tiêu chuẩn (User)", use_container_width=True):
            st.session_state.preview_mode = True
            st.rerun()
            
        st.markdown('</div>', unsafe_allow_html=True)
