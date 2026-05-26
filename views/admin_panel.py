import streamlit as st
import json
import os
import time
from utils.data_loader import load_all_available
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
    
    # Initialize defaults if not present
    is_locked = state.get("is_locked", False)
    announcement = state.get("announcement", {"active": False, "text": ""})
    ai_config = state.get("ai_config", {"temperature": 0.3})
    
    # --- ROW 1 ---
    col1, col2 = st.columns([1, 1])
    
    with col1:
        # Access Management
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
        # System Status & Health
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
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="margin-bottom: 20px;">
                <div class="status-badge status-active">
                    <div class="indicator-dot indicator-green"></div>
                    HOẠT ĐỘNG BÌNH THƯỜNG (ONLINE)
                </div>
            </div>
            """, unsafe_allow_html=True)
            
        st.markdown("<hr style='border: none; border-top: 1px solid #F1F5F9; margin: 16px 0;'>", unsafe_allow_html=True)
        
        # Health Check
        groq_keys = _get_groq_keys()
        n_keys = len(groq_keys)
        
        st.markdown(f"""
            <p style="color: #0F172A; font-weight: 600; font-size: 0.95rem; margin-bottom: 8px;">Health Check</p>
            <p style="color: #475569; font-size: 0.85rem; margin-bottom: 4px;">• API Groq: <strong>{n_keys} key(s) đang khả dụng</strong></p>
        """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        # Cache Control
        if st.button("Làm mới bộ nhớ đệm (Clear Cache)", use_container_width=True):
            st.cache_data.clear()
            st.toast("Đã xóa bộ nhớ đệm thành công!", icon="✅")
            
        st.markdown('</div>', unsafe_allow_html=True)

    # --- ROW 2 ---
    col3, col4 = st.columns([1, 1])
    
    with col3:
        # Announcements
        st.markdown("""
        <div class="admin-card">
            <div class="admin-card-header">
                <div class="admin-card-icon">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 17H2a3 3 0 0 0 3-3V9a7 7 0 0 1 14 0v5a3 3 0 0 0 3 3zm-8.27 4a2 2 0 0 1-3.46 0"></path></svg>
                </div>
                <h3 class="admin-card-title">Thông báo Toàn cục (Banner)</h3>
            </div>
            <p style="color: #475569; font-size: 0.9rem; line-height: 1.6; margin-bottom: 20px;">
                Cài đặt một thông báo nổi bật xuất hiện ở đầu trang của tất cả người dùng.
            </p>
        """, unsafe_allow_html=True)
        
        new_ann_text = st.text_area("Nội dung thông báo", value=announcement.get("text", ""), height=100)
        new_ann_active = st.toggle("Hiển thị Thông báo", value=announcement.get("active", False))
        
        if st.button("Lưu Thông báo"):
            state["announcement"] = {
                "text": new_ann_text,
                "active": new_ann_active
            }
            save_state(state)
            st.toast("Đã cập nhật thông báo!", icon="✅")
            st.rerun()
            
        st.markdown('</div>', unsafe_allow_html=True)

    with col4:
        # AI Config
        st.markdown("""
        <div class="admin-card">
            <div class="admin-card-header">
                <div class="admin-card-icon">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="16" x2="12" y2="12"></line><line x1="12" y1="8" x2="12.01" y2="8"></line></svg>
                </div>
                <h3 class="admin-card-title">Cấu hình AI (Groq)</h3>
            </div>
            <p style="color: #475569; font-size: 0.9rem; line-height: 1.6; margin-bottom: 20px;">
                Điều chỉnh thông số của mô hình AI khi tạo nhận xét (Insight).
            </p>
        """, unsafe_allow_html=True)
        
        new_temp = st.slider("Độ sáng tạo (Temperature)", min_value=0.0, max_value=1.0, value=float(ai_config.get("temperature", 0.3)), step=0.1)
        
        if st.button("Lưu Cấu hình AI"):
            state["ai_config"] = {
                "temperature": new_temp
            }
            save_state(state)
            st.toast("Đã lưu cấu hình AI!", icon="✅")

        st.markdown("<hr style='border: none; border-top: 1px solid #F1F5F9; margin: 24px 0;'>", unsafe_allow_html=True)
        
        st.markdown("""
            <p style="color: #0F172A; font-weight: 600; font-size: 0.95rem; margin-bottom: 8px;">Môi trường Giả lập</p>
        """, unsafe_allow_html=True)
        
        if st.button("Truy cập với quyền tiêu chuẩn (User)", use_container_width=True):
            st.session_state.preview_mode = True
            st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)

