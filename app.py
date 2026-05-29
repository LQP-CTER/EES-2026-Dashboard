import streamlit as st
import pandas as pd
import sys, os
import importlib
import base64
import hashlib
import json
import re
import time

# Setup paths
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__))))

# Force reload shared modules to prevent caching issues in Streamlit
try:
    import shared.plotly_theme
    importlib.reload(shared.plotly_theme)
except Exception:
    pass
try:
    import shared.nlp_utils
    importlib.reload(shared.nlp_utils)
except Exception:
    pass
try:
    import shared.codebook
    importlib.reload(shared.codebook)
except Exception:
    pass
try:
    import shared.workforce_mapper
    importlib.reload(shared.workforce_mapper)
except Exception:
    pass

st.set_page_config(page_title="GHN EES 2026", page_icon="./img/Logo_EES.png", layout="wide", initial_sidebar_state="expanded")

# Check Admin Token
if 'token' in st.query_params:
    if st.query_params['token'] == st.secrets.get("ADMIN_TOKEN", ""):
        st.session_state.is_admin = True
    st.query_params.clear()

if 'preview_mode' not in st.session_state:
    st.session_state.preview_mode = False

import json
APP_STATE_FILE = os.path.join("config", "app_state.json")
is_locked = False
announcement = {"active": False, "text": ""}
if os.path.exists(APP_STATE_FILE):
    with open(APP_STATE_FILE, "r") as f:
        state_data = json.load(f)
        is_locked = state_data.get("is_locked", False)
        announcement = state_data.get("announcement", {"active": False, "text": ""})

# --- AUTHENTICATION FLOW ---
from utils.auth import get_google_auth_url, get_user_info

# Load client secrets
GOOGLE_CLIENT_ID     = st.secrets.get("GOOGLE_CLIENT_ID", "")
GOOGLE_CLIENT_SECRET = st.secrets.get("GOOGLE_CLIENT_SECRET", "")
REDIRECT_URI         = st.secrets.get("REDIRECT_URI", "http://localhost:8501/")
_domains_raw = st.secrets.get("ALLOWED_DOMAINS", "ghn.vn,scommerce.asia")
ALLOWED_DOMAINS = [d.strip().lower() for d in _domains_raw.split(",")] if isinstance(_domains_raw, str) else [d.lower() for d in _domains_raw]

# Auth token secret (for persisting login across F5 via query_params)
_AUTH_SECRET = st.secrets.get("ADMIN_TOKEN", GOOGLE_CLIENT_SECRET or "ees2026-fallback-secret")


def _make_auth_token(email: str, name: str, picture: str) -> str:
    # Thêm timestamp hết hạn (12 tiếng = 43200 giây)
    exp = int(time.time()) + 43200
    # Thêm 'v3' để vô hiệu hóa toàn bộ token cũ
    payload = base64.urlsafe_b64encode(f"{email}|{name}|{picture}|{exp}|v3".encode()).decode()
    sig = hashlib.sha256(f"{email}{exp}{_AUTH_SECRET}_v3".encode()).hexdigest()[:16]
    return f"{payload}.{sig}"


def _verify_auth_token(token: str):
    if not token or "." not in token:
        return None
    try:
        payload, sig = token.rsplit(".", 1)
        decoded = base64.urlsafe_b64decode(payload.encode()).decode()
        parts = decoded.split("|")
        if len(parts) < 5 or parts[-1] != "v3":
            return None # Reject old v1/v2 tokens
        email, name, picture, exp_str = parts[0], parts[1], parts[2], parts[3]
        
        # Kiểm tra token đã hết hạn chưa
        if int(time.time()) > int(exp_str):
            return None
            
        expected_sig = hashlib.sha256(f"{email}{exp_str}{_AUTH_SECRET}_v3".encode()).hexdigest()[:16]
        if sig != expected_sig:
            return None
        return {"email": email, "name": name, "picture": picture}
    except Exception:
        return None


LOCALSTORAGE_KEY = "ees2026_auth_token"

def _save_token_to_browser(token: str):
    """Inject JS to save auth token to localStorage."""
    import streamlit.components.v1 as components
    components.html(f"""
    <script>
        (function() {{
            try {{
                window.parent.localStorage.setItem('{LOCALSTORAGE_KEY}', '{token}');
            }} catch(e) {{}}
        }})();
    </script>
    """, width=0, height=0)


def _inject_restore_from_localstorage():
    """Inject JS to read token from localStorage and redirect with ?s= if missing from URL."""
    import streamlit.components.v1 as components
    components.html(f"""
    <script>
        (function() {{
            try {{
                var token = window.parent.localStorage.getItem('{LOCALSTORAGE_KEY}');
                if (token) {{
                    var url = new URL(window.parent.location.href);
                    if (!url.searchParams.get('s')) {{
                        url.searchParams.set('s', token);
                        window.parent.location.replace(url.toString());
                    }}
                }}
            }} catch(e) {{}}
        }})();
    </script>
    """, width=0, height=0)


def _clear_token_from_browser():
    """Inject JS to remove auth token from localStorage (logout)."""
    import streamlit.components.v1 as components
    components.html(f"""
    <script>
        (function() {{
            try {{
                window.parent.localStorage.removeItem('{LOCALSTORAGE_KEY}');
            }} catch(e) {{}}
        }})();
    </script>
    """, width=0, height=0)


is_admin = st.session_state.get("is_admin", False)

def _is_allowed_email(email: str) -> bool:
    if not email:
        return False
    domain = email.split("@")[-1].lower()
    return domain in [d.lower() for d in ALLOWED_DOMAINS]

def _render_login_page():
    auth_url = get_google_auth_url(GOOGLE_CLIENT_ID, REDIRECT_URI)
    
    st.markdown(f"""
    <style>
        [data-testid="stSidebar"] {{ display: none !important; }}
        header[data-testid="stHeader"] {{ display: none !important; }}
        .login-wrap {{
            display: flex; flex-direction: column; align-items: center;
            justify-content: center; min-height: 80vh; gap: 24px;
        }}
        .login-card {{
            background: white; border-radius: 20px; padding: 48px 56px;
            box-shadow: 0 8px 40px rgba(0,0,0,0.12);
            text-align: center; max-width: 480px; width: 100%;
        }}
        .login-title {{ font-size: 1.6rem; font-weight: 800; color: #0A1F44; margin: 16px 0 8px; }}
        .login-subtitle {{ font-size: 0.9rem; color: #64748B; margin-bottom: 28px; line-height: 1.5; }}
        .login-note {{ font-size: 0.8rem; color: #94A3B8; margin-top: 24px; }}
        .login-divider {{ border: none; border-top: 1px solid #E2E8F0; margin: 20px 0; }}
        .google-btn {{
            display: inline-block; background-color: #FF5200; color: white !important;
            text-decoration: none; padding: 12px 24px; border-radius: 8px;
            font-weight: 600; font-size: 1rem; width: 100%; text-align: center;
            box-sizing: border-box; transition: background-color 0.2s; margin-top: 10px;
        }}
        .google-btn:hover {{ background-color: #E64A00; text-decoration: none; }}
    </style>
    <div class="login-wrap">
        <div class="login-card">
            <img src="https://res.cloudinary.com/dd7gti2kn/image/upload/v1772778208/LOGO%20GHN/LOGO_INAN_1_lghbnf.png" width="140">
            <div class="login-title">GHN EES 2026 Dashboard</div>
            <div class="login-subtitle">
                Hệ thống phân tích Trải nghiệm Nhân viên<br>dành riêng cho nội bộ GHN & Scommerce
            </div>
            <hr class="login-divider">
            <a href="{auth_url}" target="_blank" class="google-btn">
                Đăng nhập bằng Google
            </a>
            <div class="login-note">Bảo mật bởi Google OAuth 2.0</div>
        </div>
    </div>
    """, unsafe_allow_html=True)


if not is_admin:
    # 1. Xử lý callback OAuth (có ?code= trên URL)
    if "code" in st.query_params:
        code = st.query_params.get("code")
        with st.spinner("Đang xác thực..."):
            user_info = get_user_info(code, GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, REDIRECT_URI)

        if user_info and "email" in user_info:
            email = user_info["email"]
            if _is_allowed_email(email):
                name = user_info.get("name", "User")
                picture = user_info.get("picture", "")
                st.session_state.user_email = email
                st.session_state.user_name = name
                st.session_state.user_picture = picture
                token = _make_auth_token(email, name, picture)
                st.query_params.clear()
                st.query_params["s"] = token
                _save_token_to_browser(token)
                st.rerun()
            else:
                st.query_params.clear()
                st.session_state.pop("user_email", None)
                st.error(
                    f"Email **{email}** không được phép truy cập.\n\n"
                    "Chỉ email `@ghn.vn` hoặc `@scommerce.asia` mới có quyền vào hệ thống."
                )
                _render_login_page()
                st.stop()
        else:
            st.query_params.clear()
            st.error("Xác thực Google thất bại. Vui lòng thử lại.")
            _render_login_page()
            st.stop()

    # 2. Restore session từ auth token trên URL hoặc localStorage
    user_email = st.session_state.get("user_email")
    if not user_email:
        auth_token = st.query_params.get("s")
        if not auth_token:
            # Chưa có token trên URL → inject JS để đọc từ localStorage và redirect
            _inject_restore_from_localstorage()
            _render_login_page()
            st.stop()
        if auth_token:
            token_data = _verify_auth_token(auth_token)
            if token_data and _is_allowed_email(token_data["email"]):
                st.session_state.user_email = token_data["email"]
                st.session_state.user_name = token_data["name"]
                st.session_state.user_picture = token_data["picture"]
            else:
                st.query_params.clear()
                _clear_token_from_browser()
                _render_login_page()
                st.stop()

    # 3. Nếu vẫn chưa có user → hiện trang login
    user_email = st.session_state.get("user_email")
    if not user_email or not _is_allowed_email(user_email):
        _render_login_page()
        st.stop()

if is_admin and not st.session_state.preview_mode:
    # Render admin panel
    from views import admin_panel
    admin_panel.render()
    st.stop()

if is_locked and not is_admin:
    st.markdown("""
    <div style='text-align: center; margin-top: 100px;'>
        <img src='https://res.cloudinary.com/dd7gti2kn/image/upload/v1772778208/LOGO%20GHN/LOGO_INAN_1_lghbnf.png' width='200'>
        <h1 style='color: #0A1F44; margin-top: 30px;'>Hệ Thống Đang Bảo Trì</h1>
        <p style='color: #64748B; font-size: 1.1rem;'>Dashboard hiện đang tạm khóa để cập nhật dữ liệu. Vui lòng quay lại sau.</p>
    </div>
    <style>
        [data-testid="stSidebar"] { display: none !important; }
        header[data-testid="stHeader"] { display: none !important; }
    </style>
    """, unsafe_allow_html=True)
    st.stop()

# --- GLOBAL ANNOUNCEMENT BANNER ---
if announcement.get("active") and announcement.get("text"):
    st.markdown(f"""
    <div style="background-color: #FFF3EE; border-left: 4px solid #FF5200; padding: 12px 20px; border-radius: 4px; margin-bottom: 20px; box-shadow: 0 1px 2px rgba(0,0,0,0.05);">
        <div style="display: flex; align-items: center; gap: 10px;">
            <span style="font-size: 1.2rem;"></span>
            <span style="color: #0F172A; font-weight: 500; font-size: 0.95rem;">{announcement['text']}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

# Import loaders and views
from utils.data_loader import load_group, load_all_available
from config.groups import get_available_groups
from views import (
    company_overview, hris_linkage,
    view_a_current_state, view_b_problem_groups,
    view_c_key_issues, view_d_root_cause,
    view_e_impact_risk, view_f_action_priority, view_g_kpi_impact,
    view_h_appendix, view_i_data_trust
)
from shared.codebook import PILLAR_META, PILLAR_ORDER

# ── Custom CSS ──────────────────────────────────────────────────────────────
st.markdown("""<style>
/* ═══════ BASE ═══════ */
/* Hide Streamlit Toolbar & Deploy Button */
#MainMenu {visibility: hidden !important;}
footer {visibility: hidden !important;}
.stAppDeployButton {display:none !important;}
.stDeployButton {display:none !important;}
[data-testid="stToolbar"] {display: none !important;}
/* Hide Streamlit Cloud Viewer Badge (Avatar/Profile) */
.viewerBadge_container {display: none !important;}
.viewerBadge_link {display: none !important;}
[class*="viewerBadge"] {display: none !important;}

html, body, .stApp {
    font-family: 'Inter', 'Segoe UI', system-ui, -apple-system, sans-serif !important;
    background-color: #F8FAFC !important;
    color: #1E293B !important;
}
.block-container {
    padding-top: 4.5rem !important;
    padding-left: 2.5rem !important;
    padding-right: 2.5rem !important;
    max-width: 100% !important;
}

/* Make sidebar un-closeable per user request */
[data-testid="stSidebarCollapseButton"],
button[title="Collapse sidebar"],
button[aria-label="Collapse sidebar"],
button[aria-label="Thu nhỏ thanh bên"],
button[title="Thu nhỏ thanh bên"] {
    display: none !important;
}

/* ═══════ SIDEBAR BASE ═══════ */
[data-testid="stSidebar"] {
    background: #FFFFFF !important;
    border-right: 1px solid #E2E8F0 !important;
}
[data-testid="stSidebar"] > div:first-child,
[data-testid="stSidebar"] section[data-testid="stSidebarContent"] {
    padding-top: 0 !important;
}

/* ═══════ SIDEBAR BRAND ═══════ */
.sb-brand {
    padding: 22px 20px 16px;
    border-bottom: 1px solid #F1F5F9;
    margin-bottom: 4px;
}
.sb-logo {
    height: 36px;
    object-fit: contain;
    margin-bottom: 12px;
    display: block;
}
.sb-title {
    font-size: 0.875rem;
    font-weight: 700;
    color: #0A1F44;
    display: block;
    line-height: 1.3;
}
.sb-sub {
    font-size: 0.72rem;
    color: #94A3B8;
    display: block;
    margin-top: 3px;
    font-weight: 500;
}

/* ═══════ SIDEBAR NAV LABELS — Executive Style ═══════ */
.sb-section {
    font-size: 0.64rem;
    font-weight: 700;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color: #64748B;
    padding: 16px 20px 6px;
    display: block;
}
.sb-divider {
    height: 1px;
    background: #E2E8F0;
    margin: 12px 0;
}

/* ═══════ SIDEBAR RADIO (NAV ITEMS) — Executive Style ═══════ */
[data-testid="stSidebar"] div[role="radiogroup"] {
    gap: 2px !important;
    display: flex !important;
    flex-direction: column !important;
    padding: 0 12px !important;
}
[data-testid="stSidebar"] div[role="radiogroup"] > label {
    padding: 10px 14px !important;
    border-radius: 8px !important;
    background: transparent !important;
    border: none !important;
    transition: all 0.15s ease !important;
    cursor: pointer !important;
}
[data-testid="stSidebar"] div[role="radiogroup"] > label p {
    font-size: 0.85rem !important;
    font-weight: 500 !important;
    color: #475569 !important;
    margin: 0 !important;
    line-height: 1.4 !important;
}
[data-testid="stSidebar"] div[role="radiogroup"] > label:hover {
    background: #F8FAFC !important;
}
[data-testid="stSidebar"] div[role="radiogroup"] > label:hover p {
    color: #0A1F44 !important;
}
[data-testid="stSidebar"] div[role="radiogroup"] > label:has(input:checked) {
    background: #0A1F44 !important;
    box-shadow: 0 2px 6px rgba(10,31,68,0.12) !important;
}
[data-testid="stSidebar"] div[role="radiogroup"] > label:has(input:checked) p {
    font-weight: 600 !important;
    color: #FFFFFF !important;
}
[data-testid="stSidebar"] div[role="radiogroup"] > label > div:first-child {
    display: none !important;
}

/* ═══════ SIDEBAR SELECT LABELS ═══════ */
[data-testid="stSidebar"] [data-baseweb="select"] > div {
    border-radius: 8px !important;
    border-color: #E2E8F0 !important;
    background: #F8FAFC !important;
    font-size: 0.82rem !important;
}
[data-testid="stSidebar"] .stSelectbox label,
[data-testid="stSidebar"] .stSelectbox > label {
    font-size: 0.72rem !important;
    font-weight: 600 !important;
    color: #64748B !important;
    text-transform: uppercase !important;
    letter-spacing: 0.07em !important;
}

/* ═══════ PAGE HEADER — Executive Style ═══════ */
.pg-header {
    margin-bottom: 32px;
    padding-bottom: 24px;
    border-bottom: 2px solid #F1F5F9;
    display: flex;
    justify-content: space-between;
    align-items: flex-end;
}
.pg-eyebrow {
    font-size: 0.65rem;
    font-weight: 700;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color: #64748B;
    margin: 0 0 6px;
}
.pg-title {
    font-size: 1.6rem;
    font-weight: 800;
    color: #0A1F44;
    margin: 0;
    letter-spacing: -0.03em;
    line-height: 1.2;
}
.pg-subtitle {
    font-size: 0.85rem;
    color: #64748B;
    margin: 8px 0 0;
    font-weight: 500;
}
.pg-badge {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    background: #F0FDF4;
    color: #15803D;
    border: 1px solid #BBF7D0;
    padding: 6px 14px;
    border-radius: 20px;
    font-size: 0.72rem;
    font-weight: 700;
    letter-spacing: 0.04em;
    white-space: nowrap;
    box-shadow: 0 1px 3px rgba(21,128,61,0.08);
}
.pg-badge-dot {
    width: 7px;
    height: 7px;
    background: #22C55E;
    border-radius: 50%;
    display: inline-block;
    animation: pulse-dot 2s ease-in-out infinite;
}
@keyframes pulse-dot {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.5; }
}

/* ═══════ SECTION HEADERS ═══════ */
.sec-h3 {
    font-size: 0.92rem;
    font-weight: 700;
    color: #0A1F44;
    margin: 30px 0 14px;
    padding-bottom: 10px;
    border-bottom: 1px solid #F1F5F9;
    display: flex;
    align-items: center;
    gap: 8px;
}
.sec-accent {
    width: 3px;
    height: 15px;
    background: #FF5200;
    border-radius: 2px;
    display: inline-block;
    flex-shrink: 0;
}
.sec-desc {
    font-size: 0.82rem;
    color: #64748B;
    margin: -8px 0 18px;
    font-weight: 500;
}

/* ═══════ TABS — Executive Style ═══════ */
.stTabs [data-baseweb="tab-list"] {
    background: #FFFFFF !important;
    border: 1px solid #E2E8F0 !important;
    border-radius: 12px !important;
    padding: 6px !important;
    gap: 2px !important;
    box-shadow: 0 1px 3px rgba(0,0,0,0.04) !important;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 8px !important;
    padding: 10px 24px !important;
    font-size: 0.85rem !important;
    font-weight: 500 !important;
    color: #64748B !important;
    background: transparent !important;
    border: none !important;
    transition: all 0.15s ease !important;
    letter-spacing: -0.01em !important;
}
.stTabs [data-baseweb="tab"]:hover {
    color: #0A1F44 !important;
    background: #F8FAFC !important;
}
.stTabs [aria-selected="true"] {
    background: #0A1F44 !important;
    color: #FFFFFF !important;
    font-weight: 600 !important;
    box-shadow: 0 2px 8px rgba(10,31,68,0.15) !important;
}
.stTabs [data-baseweb="tab-highlight-bar"] {
    display: none !important;
}

/* ═══════ PILLS / SEGMENTED CONTROL ═══════ */
div[data-testid="stBaseButton-pill"] {
    background: #F8FAFC !important;
    color: #475569 !important;
    border: 1px solid #E2E8F0 !important;
    border-radius: 8px !important;
    font-weight: 500 !important;
    font-size: 0.83rem !important;
    padding: 7px 16px !important;
    transition: all 0.12s ease !important;
    box-shadow: none !important;
}
div[data-testid="stBaseButton-pill"]:hover {
    background: #FFF3EE !important;
    color: #FF5200 !important;
    border-color: #FFD0B9 !important;
}
div[data-testid="stBaseButton-pill"][aria-selected="true"] {
    background: #FF5200 !important;
    color: #FFFFFF !important;
    border-color: #FF5200 !important;
    font-weight: 600 !important;
}

/* ═══════ SELECT & INPUT ═══════ */
div[data-baseweb="select"] > div {
    border-radius: 8px !important;
    border-color: #E2E8F0 !important;
    background: #FFFFFF !important;
    font-size: 0.875rem !important;
    transition: border-color 0.12s ease !important;
}
div[data-baseweb="select"] > div:hover {
    border-color: #CBD5E1 !important;
}

/* ═══════ AI INSIGHT CARD ═══════ */
.ai-insight-container {
    background: #FFFFFF !important;
    border: 1px solid #E2E8F0 !important;
    border-radius: 12px !important;
    padding: 20px 22px !important;
    margin-bottom: 20px !important;
    position: relative !important;
    overflow: hidden !important;
}
.ai-insight-container::before {
    content: '';
    position: absolute;
    left: 0; top: 0;
    width: 3px; height: 100%;
    background: #FF5200;
    border-radius: 12px 0 0 12px;
}
.ai-header {
    display: flex !important;
    align-items: center !important;
    gap: 8px !important;
    margin-bottom: 10px !important;
}
.ai-icon {
    width: 26px; height: 26px;
    background: #FFF3EE;
    border-radius: 7px;
    display: flex; align-items: center; justify-content: center;
    color: #FF5200;
    flex-shrink: 0;
}
.ai-title {
    font-size: 0.7rem !important;
    font-weight: 700 !important;
    color: #64748B !important;
    text-transform: uppercase !important;
    letter-spacing: 0.09em !important;
    margin: 0 !important;
    font-family: 'Inter', sans-serif !important;
}
.ai-badge {
    background: #F8FAFC !important;
    color: #64748B !important;
    padding: 2px 8px !important;
    border-radius: 6px !important;
    font-size: 0.63rem !important;
    font-weight: 600 !important;
    margin-left: auto !important;
    letter-spacing: 0.04em !important;
    text-transform: uppercase !important;
    border: 1px solid #E2E8F0 !important;
}
.ai-content {
    font-size: 0.875rem !important;
    line-height: 1.7 !important;
    color: #475569 !important;
    max-height: 300px !important;
    overflow-y: auto !important;
    padding-right: 8px !important;
}
.ai-content::-webkit-scrollbar {
    width: 5px;
}
.ai-content::-webkit-scrollbar-track {
    background: #F8FAFC;
    border-radius: 4px;
}
.ai-content::-webkit-scrollbar-thumb {
    background: #CBD5E1;
    border-radius: 4px;
}
.ai-content::-webkit-scrollbar-thumb:hover {
    background: #94A3B8;
}
.ai-content strong {
    color: #0A1F44 !important;
    font-weight: 700 !important;
}
.ai-highlight {
    color: #15803D !important;
    font-weight: 700 !important;
    background: #F0FDF4 !important;
    padding: 1px 5px !important;
    border-radius: 4px !important;
}
.ai-warning {
    color: #DC2626 !important;
    font-weight: 700 !important;
    background: #FEF2F2 !important;
    padding: 1px 5px !important;
    border-radius: 4px !important;
}

/* ═══════ INSIGHT SQUARES ═══════ */
.insight-square {
    background: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 12px;
    padding: 20px;
    height: 100%;
    transition: border-color 0.15s ease;
    position: relative;
    overflow: hidden;
}
.insight-square::before {
    content: '';
    position: absolute;
    top: 0; left: 0;
    width: 3px; height: 100%;
    border-radius: 12px 0 0 12px;
}
.insight-square-total::before  { background: #FF5200; }
.insight-square-top::before    { background: #10B981; }
.insight-square-warning::before { background: #F59E0B; }
.insight-square-recommend::before { background: #EF4444; }
.insight-square:hover { border-color: #CBD5E1; }
.insight-header {
    display: flex; align-items: center; gap: 10px;
    margin-bottom: 12px; padding-bottom: 10px;
    border-bottom: 1px solid #F1F5F9;
}
.insight-icon {
    width: 30px; height: 30px;
    border-radius: 7px;
    display: flex; align-items: center; justify-content: center;
    font-size: 0.72rem; font-weight: 700;
    background: #FFF3EE; color: #FF5200;
    flex-shrink: 0;
}
.insight-title  { font-weight: 700; color: #0A1F44; font-size: 0.88rem; margin: 0; }
.insight-body   { font-size: 0.875rem; color: #475569; line-height: 1.65; }
.insight-highlight { font-weight: 700; color: #FF5200; }

/* ═══════ KPI / METRIC CARDS ═══════ */
.custom-metric-card, .premium-kpi-card {
    background: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 12px;
    padding: 20px 22px;
    height: 100%;
    transition: border-color 0.15s ease;
    position: relative;
    overflow: hidden;
}
.custom-metric-card:hover, .premium-kpi-card:hover { border-color: #CBD5E1; }
.metric-title {
    font-size: 0.68rem; font-weight: 700;
    text-transform: uppercase; letter-spacing: 0.09em;
    color: #94A3B8; margin-bottom: 14px;
}
.metric-value-row { display: flex; align-items: baseline; gap: 6px; margin-bottom: 10px; }
.metric-value { font-size: 2.2rem; font-weight: 900; color: #0A1F44; line-height: 1; letter-spacing: -0.03em; }
.metric-unit  { font-size: 1rem; color: #94A3B8; font-weight: 600; }
.metric-delta {
    display: inline-flex; align-items: center; gap: 4px;
    font-size: 0.72rem; font-weight: 600;
    padding: 3px 10px; border-radius: 20px; width: fit-content;
}
.delta-positive  { background: #F0FDF4; color: #16A34A; }
.delta-negative  { background: #FEF2F2; color: #DC2626; }
.delta-neutral   { background: #F8FAFC; color: #64748B;  }

/* ═══════ FRAMEWORK CALLOUT ═══════ */
.framework-callout {
    background: #FAFAFA;
    border: 1px solid #E2E8F0;
    border-left: 3px solid #FF5200;
    border-radius: 10px;
    padding: 18px 22px;
    margin-bottom: 20px;
}
.framework-callout-title {
    font-weight: 700; font-size: 0.9rem; color: #0A1F44;
    margin: 0 0 6px;
    display: flex; align-items: center; gap: 8px;
}

/* ═══════ SIMULATION GAUGE ═══════ */
.sim-gauge-container {
    background: #FFFFFF; border: 1px solid #E2E8F0;
    border-radius: 12px; padding: 28px; text-align: center;
}
.sim-risk-value {
    font-size: 3.5rem; font-weight: 900; line-height: 1;
    letter-spacing: -0.04em; margin: 14px 0; transition: all 0.3s ease;
}
.sim-risk-meter {
    height: 8px; width: 100%; background: #F1F5F9;
    border-radius: 4px; overflow: hidden; margin: 10px 0;
}
.sim-risk-bar { height: 100%; border-radius: 4px; transition: width 0.35s ease; }

/* ═══════ HERO CARD (legacy compatibility) ═══════ */
.hero-card {
    background: #0A1F44; color: #F8FAFC !important;
    border-radius: 16px; padding: 32px 40px;
    margin-bottom: 28px; position: relative; overflow: hidden;
}
.hero-card::before {
    content: ''; position: absolute;
    top: -30%; right: -10%;
    width: 280px; height: 280px;
    background: radial-gradient(circle, rgba(255,82,0,0.22) 0%, transparent 70%);
    filter: blur(40px); pointer-events: none;
}
.hero-title    { font-size: 1.5rem; font-weight: 800; color: #FFF !important; margin: 0 0 6px; }
.hero-subtitle { font-size: 0.9rem;  color: #94A3B8 !important; margin: 0 0 28px; }
.hero-metrics  { display: grid; grid-template-columns: repeat(auto-fit, minmax(160px, 1fr)); gap: 20px; position: relative; z-index: 10; }
.hero-metric-box {
    background: rgba(255,255,255,0.04); padding: 20px;
    border-radius: 12px; border: 1px solid rgba(255,255,255,0.07);
    transition: all 0.25s ease;
}
.hero-metric-box:hover { background: rgba(255,255,255,0.08); border-color: rgba(255,82,0,0.3); }
.hero-metric-label { font-size: 0.72rem; color: #94A3B8 !important; font-weight: 700; text-transform: uppercase; letter-spacing: 0.08em; }
.hero-metric-value { font-size: 2.5rem; font-weight: 900; color: #FFF !important; line-height: 1; letter-spacing: -0.03em; }

/* ═══════ DATAFRAME — Executive Style ═══════ */
[data-testid="stDataFrame"] { 
    border-radius: 12px !important; 
    overflow: hidden !important;
    border: 1px solid #E2E8F0 !important;
    box-shadow: 0 1px 3px rgba(0,0,0,0.04) !important;
}

/* ═══════ EXPANDER — Clean Style ═══════ */
.streamlit-expanderHeader {
    font-size: 0.85rem !important;
    font-weight: 600 !important;
    color: #0A1F44 !important;
    padding: 12px 16px !important;
    background: #F8FAFC !important;
    border-radius: 8px !important;
    border: 1px solid #E2E8F0 !important;
}
.streamlit-expanderContent {
    padding: 16px !important;
    border: 1px solid #E2E8F0 !important;
    border-top: none !important;
    border-radius: 0 0 8px 8px !important;
    background: #FFFFFF !important;
}

/* ═══════ BUTTONS — Professional ═══════ */
.stButton > button {
    border-radius: 8px !important;
    font-weight: 600 !important;
    font-size: 0.85rem !important;
    padding: 8px 20px !important;
    transition: all 0.15s ease !important;
    border: 1px solid #E2E8F0 !important;
    background: #FFFFFF !important;
    color: #0A1F44 !important;
}
.stButton > button:hover {
    border-color: #0A1F44 !important;
    box-shadow: 0 2px 6px rgba(10,31,68,0.1) !important;
}
.stButton > button[kind="primary"] {
    background: #0A1F44 !important;
    color: #FFFFFF !important;
    border-color: #0A1F44 !important;
}
.stButton > button[kind="primary"]:hover {
    background: #1B2559 !important;
}

/* ═══════ METRICS — Clean ═══════ */
[data-testid="stMetric"] {
    background: #FFFFFF !important;
    border: 1px solid #E2E8F0 !important;
    border-radius: 12px !important;
    padding: 16px 20px !important;
}
[data-testid="stMetricLabel"] {
    font-size: 0.72rem !important;
    font-weight: 700 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.08em !important;
    color: #64748B !important;
}
[data-testid="stMetricValue"] {
    font-size: 1.8rem !important;
    font-weight: 800 !important;
    color: #0A1F44 !important;
    letter-spacing: -0.02em !important;
}
</style>
""", unsafe_allow_html=True)


# ── State & Setup ───────────────────────────────────────────────────────────
available = get_available_groups()
group_opts = list(available.keys())

if 'global_tenure' not in st.session_state:
    st.session_state.global_tenure = 'Tất cả'

tenure_opts = [
    'Tất cả', 'Dưới 1 tháng', 'Trên 1 đến 3 tháng', 'Trên 3 đến 6 tháng',
    'Trên 6 đến 9 tháng', 'Trên 9 đến 12 tháng', 'Trên 1 đến 2 năm',
    'Trên 2 đến 3 năm', 'Trên 3 đến 5 năm', 'Trên 5 năm', 'Khác'
]

def apply_global_filters(df):
    if st.session_state.global_tenure != 'Tất cả':
        if 'Q5' in df.columns:
            return df[df['Q5'] == st.session_state.global_tenure]
    return df

COMPANY_LABEL = "Tổng quan GHN"

# ── SIDEBAR ─────────────────────────────────────────────────────────────────
with st.sidebar:
    if st.session_state.get("is_admin", False):
        if st.button("Trở về Admin Panel", width='stretch'):
            st.session_state.preview_mode = False
            st.rerun()
        st.markdown('<div class="sb-divider"></div>', unsafe_allow_html=True)

    # Brand block
    st.markdown("""
    <div class="sb-brand">
        <img src="https://res.cloudinary.com/dd7gti2kn/image/upload/v1772778208/LOGO%20GHN/LOGO_INAN_1_lghbnf.png" class="sb-logo" alt="GHN Logo">
        <span class="sb-title">EES 2026 Dashboard</span>
        <span class="sb-sub">Employee Engagement Survey · 2026</span>
    </div>
    """, unsafe_allow_html=True)

    # Main navigation
    st.markdown('<span class="sb-section">Phân khúc báo cáo</span>', unsafe_allow_html=True)
    main_nav_opts = [COMPANY_LABEL] + [available[g]['label'] for g in group_opts] + ["Độ tin cậy dữ liệu", "Phụ lục"]
    sel_dashboard = st.radio("Nav", main_nav_opts, label_visibility="collapsed", key="main_nav")

    st.markdown('<div class="sb-divider"></div>', unsafe_allow_html=True)

    is_company = (sel_dashboard == COMPANY_LABEL)
    is_appendix = (sel_dashboard == "Phụ lục")
    is_data_trust = (sel_dashboard == "Độ tin cậy dữ liệu")

    # Initialize scope variables
    sel_group   = None
    sel_nav     = None
    df_filtered = None
    n_before    = 0

    if is_appendix or is_data_trust:
        pass

    elif is_company:
        # Company-level tenure filter
        st.markdown('<span class="sb-section">Bộ lọc</span>', unsafe_allow_html=True)
        sel_tenure_sb = st.selectbox(
            "Thâm niên", tenure_opts,
            index=tenure_opts.index(st.session_state.global_tenure),
            key="tenure_co"
        )
        st.session_state.global_tenure = sel_tenure_sb

    else:
        # Identify selected group
        for g in group_opts:
            if available[g]['label'] == sel_dashboard:
                sel_group = g
                break
        
        if sel_group is None:
            st.error(f"Không tìm thấy nhóm khảo sát: {sel_dashboard}")
            st.stop()

        # Sub-navigation - updated
        st.markdown('<span class="sb-section">Trụ cột trải nghiệm</span>', unsafe_allow_html=True)
        SUB_NAV = ["Tổng quan Tổ chức"] + [f"{PILLAR_META[p]['name']}" for p in PILLAR_ORDER]
        SUB_NAV.append("Đo lường Impact")
        SUB_NAV.append("Xem Báo Cáo")
        sel_nav = st.radio("SubNav", SUB_NAV, label_visibility="collapsed", key="sub_nav")

        st.markdown('<div class="sb-divider"></div>', unsafe_allow_html=True)

        # Filters
        st.markdown('<span class="sb-section">Bộ lọc</span>', unsafe_allow_html=True)

        # Load raw data (for building filter options)
        try:
            df_raw, n_before = load_group(sel_group)
        except Exception as e:
            st.error(f"Không thể tải dữ liệu cho nhóm {sel_group}: {e}")
            import traceback
            st.code(traceback.format_exc())
            st.stop()

        sel_tenure_sb = st.selectbox(
            "Thâm niên", tenure_opts,
            index=tenure_opts.index(st.session_state.global_tenure),
            key="tenure_grp"
        )
        st.session_state.global_tenure = sel_tenure_sb
        df_filtered_tenure = apply_global_filters(df_raw)

        div_opts = ['Tất cả Khối']
        if 'division' in df_filtered_tenure.columns:
            div_opts += sorted(df_filtered_tenure['division'].dropna().unique().tolist())
        sel_div = st.selectbox("Khối", div_opts)

        dept_opts = ['Tất cả Phòng ban']
        if sel_div != 'Tất cả Khối':
            dept_opts += sorted(
                df_filtered_tenure[df_filtered_tenure['division'] == sel_div]
                ['department'].dropna().unique().tolist()
            )
        elif 'department' in df_filtered_tenure.columns:
            dept_opts += sorted(df_filtered_tenure['department'].dropna().unique().tolist())
        sel_dept = st.selectbox("Phòng ban", dept_opts)

        sec_opts = ['Tất cả Section']
        if sel_dept != 'Tất cả Phòng ban':
            sec_opts += sorted(
                df_filtered_tenure[df_filtered_tenure['department'] == sel_dept]
                ['section'].dropna().unique().tolist()
            )
        elif 'section' in df_filtered_tenure.columns:
            sec_opts += sorted(df_filtered_tenure['section'].dropna().unique().tolist())
        sel_sec = st.selectbox("Section", sec_opts)

        # Apply all filters
        df_filtered = df_filtered_tenure.copy()
        if sel_div  != 'Tất cả Khối':      df_filtered = df_filtered[df_filtered['division']    == sel_div]
        if sel_dept != 'Tất cả Phòng ban': df_filtered = df_filtered[df_filtered['department']  == sel_dept]
        if sel_sec  != 'Tất cả Section':   df_filtered = df_filtered[df_filtered['section']     == sel_sec]

    # Spacer
    st.markdown('<div style="height: 40px;"></div>', unsafe_allow_html=True)
    
    # User info + logout (Moved to bottom)
    _u_email   = st.session_state.get("user_email", "")
    _u_name    = st.session_state.get("user_name", _u_email)
    _u_picture = st.session_state.get("user_picture", "")
    if _u_email:
        _avatar_html = f'<img src="{_u_picture}" style="width:32px;height:32px;border-radius:50%;object-fit:cover;border:2px solid #FF5200;">' if _u_picture else f'<div style="width:32px;height:32px;border-radius:50%;background:#FF5200;display:flex;align-items:center;justify-content:center;color:white;font-weight:700;font-size:0.9rem;">{_u_name[0].upper()}</div>'
        st.markdown(f"""
        <div style="display:flex;align-items:center;gap:10px;padding:15px 0 10px;margin-top:auto;border-top:1px solid #E2E8F0;">
            {_avatar_html}
            <div>
                <div style="font-size:0.82rem;font-weight:700;color:#0F172A;line-height:1.2;">{_u_name}</div>
                <div style="font-size:0.72rem;color:#64748B;">{_u_email}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("Đăng xuất"):
                for _k in ["user_email", "user_name", "user_picture"]:
                    st.session_state.pop(_k, None)
                st.query_params.clear()
                _clear_token_from_browser()  # Xóa token khỏi localStorage
                st.rerun()

# ── MAIN CONTENT ─────────────────────────────────────────────────────────────
if is_data_trust:
    try:
        view_i_data_trust.render()
    except Exception as e:
        st.error(f"Lỗi khi tải Độ tin cậy dữ liệu: {e}")
        import traceback
        st.code(traceback.format_exc())

elif is_appendix:
    try:
        view_h_appendix.render()
    except Exception as e:
        st.error(f"Lỗi khi tải Phụ lục: {e}")
        import traceback
        st.code(traceback.format_exc())

elif is_company:
    try:
        all_data = load_all_available()
        filtered_all_data = {k: (apply_global_filters(v[0]), v[1]) for k, v in all_data.items()}
        company_overview.render(filtered_all_data, available)
    except Exception as e:
        st.error(f"Lỗi khi tải view Tổng quan: {e}")
        import traceback
        st.code(traceback.format_exc())

else:
    cfg    = available[sel_group]
    n_resp = df_filtered.shape[0] if df_filtered is not None else 0

    st.markdown(f"""
    <div class="pg-header">
        <div>
            <p class="pg-eyebrow">EES 2026 · {sel_nav or 'Chi tiết Nhóm'}</p>
            <h1 class="pg-title">{cfg['label']}</h1>
            <p class="pg-subtitle">2026 · {n_resp:,} phản hồi hợp lệ</p>
        </div>
        <span class="pg-badge">
            <span class="pg-badge-dot"></span>Live · Cập nhật hôm nay
        </span>
    </div>
    """, unsafe_allow_html=True)

    try:
        # Detect which pillar is selected
        sel_pillar = None
        for p_id in PILLAR_ORDER:
            if sel_nav and PILLAR_META[p_id]['name'] in sel_nav:
                sel_pillar = p_id
                break

        if sel_nav == "Tổng quan Tổ chức":
            view_a_current_state.render(df_filtered, cfg)
        elif sel_nav == "Xem Báo Cáo":
            from views import narrative_flow
            narrative_flow.render_narrative(df_filtered, cfg, sel_group)
        elif sel_pillar:
            from views import pillar_renderer
            pillar_renderer.render(df_filtered, cfg, sel_group, sel_pillar)
        elif sel_nav and "Đo lường Impact" in sel_nav:
            view_g_kpi_impact.render(df_filtered, cfg)
        else:
            st.info("Chọn một trụ cột từ sidebar bên trái.")
    except Exception as e:
        st.error(f"Lỗi khi tải phân tích: {e}")
        import traceback
        st.code(traceback.format_exc())
