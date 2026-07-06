import streamlit as st
import pandas as pd
import sys, os
import importlib
import base64
import hashlib
import json
import re
import time
from datetime import datetime
from typing import Optional

import secrets
import threading

from streamlit_cookies_controller import CookieController

COOKIE_NAME = "ees_remember_token"
COOKIE_MAX_AGE = 60 * 60 * 24 * 30  # 30 days
cookie_controller = CookieController()

ACTIVE_SESSIONS_FILE = os.path.join("config", "active_sessions.json")
_sessions_lock = threading.Lock()

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
try:
    import config.groups
    importlib.reload(config.groups)
except Exception:
    pass

st.set_page_config(page_title="GHN EES 2026", page_icon="./img/Logo_EES.png", layout="wide", initial_sidebar_state="expanded")

# Tắt nội dung cũ trong lúc Streamlit rerun để trang mới hiển thị vùng loading riêng.
# Spinner mặc định được dùng như loading overlay toàn màn hình.
st.markdown("""
<style>
    /* Ẩn frame cũ để tránh trộn nội dung giữa hai trang.
       Chỉ áp dụng cho top-level stale (khi chuyển trang),
       không ảnh hưởng tới @st.fragment partial reruns. */
    .stApp > [data-stale="true"],
    .stApp > [data-testid="stale-element-container"] {
        display: none !important;
        opacity: 0 !important;
        visibility: hidden !important;
    }

    /* Fragment reruns: chỉ fade nhẹ thay vì ẩn hoàn toàn */
    [data-stale="true"] {
        opacity: 0.6 !important;
        transition: opacity 0.15s ease !important;
        pointer-events: none !important;
    }

    /* Loading overlay toàn màn hình trong lúc Streamlit xử lý. */
    [data-testid="stSpinner"] {
        position: fixed !important;
        top: 0 !important;
        left: 0 !important;
        width: 100vw !important;
        height: 100vh !important;
        transform: none !important;
        background: rgba(255, 255, 255, 0.9) !important;
        z-index: 99999 !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        backdrop-filter: blur(8px) !important;
    }
    
    [data-testid="stSpinner"] > div {
        display: flex !important;
        flex-direction: column !important;
        align-items: center !important;
        gap: 15px !important;
        transform: scale(1.3) !important;
        background: #FFFFFF !important;
        padding: 30px 40px !important;
        border-radius: 20px !important;
        box-shadow: 0 20px 40px rgba(10,31,68,0.1) !important;
        border: 1px solid rgba(255,82,0,0.1) !important;
    }
    
    /* Đổi màu vòng xoay loading sang màu cam GHN */
    [data-testid="stSpinner"] div[class*="st-"] circle {
        stroke: #FF5200 !important;
    }
    
    /* Chỉnh chữ loading */
    [data-testid="stSpinner"] p {
        font-family: 'Inter', sans-serif !important;
        font-size: 1.1rem !important;
        font-weight: 700 !important;
        color: #0A1F44 !important;
        margin: 0 !important;
    }
</style>
""", unsafe_allow_html=True)

# Cơ chế bypass login bằng ADMIN_TOKEN đã được gỡ bỏ.
# Mọi người dùng đều phải đăng nhập qua Google để lấy Role từ hệ thống phân quyền.

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
from utils.authorization import get_authorized_user, resolve_data_scope, apply_scope_filter

# Load client secrets
GOOGLE_CLIENT_ID     = st.secrets.get("GOOGLE_CLIENT_ID", "")
GOOGLE_CLIENT_SECRET = st.secrets.get("GOOGLE_CLIENT_SECRET", "")

# IMPORTANT:
# Google OAuth requires the redirect URI to match exactly what is configured
# in Google Cloud Console. Local development and Streamlit Cloud often need
# different values, so prefer an explicit secret and only fall back to localhost.
def _get_redirect_uri() -> str:
    secret_redirect = st.secrets.get("REDIRECT_URI", "").strip()
    if secret_redirect:
        return secret_redirect
    return "http://localhost:8501/"

REDIRECT_URI = _get_redirect_uri()

# --- SERVER-SIDE SESSION REGISTRY ---
def _load_active_sessions() -> dict:
    if os.path.exists(ACTIVE_SESSIONS_FILE):
        try:
            with open(ACTIVE_SESSIONS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def _save_active_sessions(sessions: dict):
    try:
        os.makedirs(os.path.dirname(ACTIVE_SESSIONS_FILE), exist_ok=True)
        with open(ACTIVE_SESSIONS_FILE, "w", encoding="utf-8") as f:
            json.dump(sessions, f, ensure_ascii=False, indent=4)
    except Exception:
        pass


def _get_remember_cookie() -> str:
    try:
        return cookie_controller.get(COOKIE_NAME) or ""
    except Exception:
        return ""


def _set_remember_cookie(token: str):
    try:
        cookie_controller.set(COOKIE_NAME, token, max_age=COOKIE_MAX_AGE)
    except Exception:
        pass


def _clear_remember_cookie():
    try:
        cookie_controller.remove(COOKIE_NAME)
    except Exception:
        pass

def _cleanup_expired_sessions(sessions: dict) -> dict:
    now = time.time()
    cleaned = {}
    for token, data in sessions.items():
        created_at = data.get("created_at", 0)
        last_seen = data.get("last_seen", 0)
        # Session expires after 12 hours (43200s) or after 1 hour of inactivity (3600s)
        if now - created_at < 43200 and now - last_seen < 3600:
            cleaned[token] = data
    return cleaned


ACCESS_LOGS_FILE = os.path.join("config", "access_logs.csv")
ACCESS_LOGS_MAX_ROWS = 5000   # Tự trim nếu vượt ngưỡng này
ACCESS_LOGS_KEEP_ROWS = 3000  # Giữ lại bao nhiêu dòng sau khi trim

def log_access(email: str, name: str, role: str, method: str = "google"):
    """Ghi nhận 1 lượt đăng nhập thành công vào file CSV.
    Tự động trim nếu file quá lớn."""
    import csv
    try:
        os.makedirs(os.path.dirname(ACCESS_LOGS_FILE), exist_ok=True)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        row = [timestamp, email, name, role, method]
        file_exists = os.path.exists(ACCESS_LOGS_FILE)
        with open(ACCESS_LOGS_FILE, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(["timestamp", "email", "name", "role", "login_method"])
            writer.writerow(row)
        # Auto-trim nếu quá nhiều dòng
        _trim_access_logs()
    except Exception:
        pass


def _trim_access_logs():
    """Nếu file log quá ACCESS_LOGS_MAX_ROWS dòng, chỉ giữ ACCESS_LOGS_KEEP_ROWS mới nhất."""
    import csv
    try:
        if not os.path.exists(ACCESS_LOGS_FILE):
            return
        with open(ACCESS_LOGS_FILE, "r", encoding="utf-8") as f:
            rows = list(csv.reader(f))
        if len(rows) <= ACCESS_LOGS_MAX_ROWS + 1:  # +1 for header
            return
        header = rows[0]
        data_rows = rows[1:]
        kept = data_rows[-ACCESS_LOGS_KEEP_ROWS:]  # giữ mới nhất
        with open(ACCESS_LOGS_FILE, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(header)
            writer.writerows(kept)
    except Exception:
        pass

def is_streamlit_session_active(session_id: str) -> bool:
    if not session_id:
        return False
    try:
        from streamlit.runtime import runtime
        rt = runtime.get_instance()
        if rt is not None:
            return rt.is_active_session(session_id)
    except Exception:
        pass
    return False

def get_current_streamlit_session_id() -> str:
    from streamlit.runtime.scriptrunner import get_script_run_ctx
    ctx = get_script_run_ctx()
    return ctx.session_id if ctx else ""

def get_sessions_lock():
    return _sessions_lock


# Mọi tài khoản đều phải xác thực, biến này chỉ giữ lại để không vỡ layout cũ
is_admin = False

def _get_authorization(email: str) -> Optional[dict]:
    try:
        return get_authorized_user(email)
    except Exception as exc:
        st.error(
            "Không đọc được Google Sheet phân quyền.\n\n"
            f"Chi tiết lỗi: `{exc}`"
        )
        st.stop()


def _clear_user_session():
    for _k in ["user_email", "user_name", "user_picture", "current_token", "user_authorization"]:
        st.session_state.pop(_k, None)


def _render_authorization_denied(email: str):
    st.markdown("""
    <style>
        [data-testid="stSidebar"] { display: none !important; }
        header[data-testid="stHeader"] { display: none !important; }
    </style>
    """, unsafe_allow_html=True)
    st.error(
        f"Email **{email}** chưa được cấp quyền truy cập dashboard.\n\n"
        "Vui lòng kiểm tra tab `Authorization` trong Google Sheet phân quyền và đảm bảo email có `status = ACTIVE`."
    )
    st.link_button("Quay lại trang đăng nhập", "/", use_container_width=False)
    st.stop()

def _render_login_page():
    auth_url = get_google_auth_url(GOOGLE_CLIENT_ID, REDIRECT_URI)

    _logo_path = os.path.join(os.path.dirname(__file__), "img", "Logo_EES.png")
    try:
        with open(_logo_path, "rb") as _f:
            _logo_b64 = base64.b64encode(_f.read()).decode()
        _logo_src = f"data:image/png;base64,{_logo_b64}"
    except Exception:
        _logo_src = "https://res.cloudinary.com/dd7gti2kn/image/upload/v1772778208/LOGO%20GHN/LOGO_INAN_1_lghbnf.png"

    _ghn_logo = "https://res.cloudinary.com/dd7gti2kn/image/upload/v1772773708/LOGO%20GHN/Logo/LOGO_INAN_sep2os.png"

    st.markdown("""
<style>
[data-testid="stSidebar"] { display: none !important; }
header[data-testid="stHeader"] { display: none !important; }

.stApp {
background: linear-gradient(135deg, #FFFFFF 0%, #FFF5F0 40%, #FFF0E8 70%, #FEF3ED 100%) !important;
}
.stApp::before {
content: '';
position: fixed;
inset: 0;
background:
radial-gradient(ellipse 55% 45% at 95% 5%, rgba(255,82,0,0.10) 0%, transparent 55%),
radial-gradient(ellipse 40% 40% at 5% 95%, rgba(10,31,68,0.06) 0%, transparent 60%),
radial-gradient(ellipse 30% 30% at 50% 50%, rgba(255,150,80,0.04) 0%, transparent 70%);
pointer-events: none;
z-index: 0;
}

.block-container {
max-width: 440px !important;
padding-top: 0 !important;
padding-bottom: 0 !important;
padding-left: 1rem !important;
padding-right: 1rem !important;
position: relative;
z-index: 1;
}

section.main > div {
display: flex !important;
flex-direction: column !important;
justify-content: center !important;
min-height: 100vh !important;
gap: 0 !important;
}

.lc-top {
background: #FFFFFF;
border: 1px solid rgba(226,232,240,0.8);
border-bottom: none;
border-radius: 24px 24px 0 0;
padding: 36px 32px 24px;
box-shadow:
0 0 0 1px rgba(255,82,0,0.05),
0 20px 60px rgba(15,23,42,0.08),
0 4px 16px rgba(15,23,42,0.04);
}

.lc-logo-wrap {
display: flex;
justify-content: center;
margin-bottom: 20px;
}
.lc-logo-main {
width: 160px;
height: auto;
object-fit: contain;
}

.lc-brand-bar {
display: flex;
align-items: center;
justify-content: center;
gap: 10px;
margin-bottom: 24px;
padding-bottom: 20px;
border-bottom: 1px solid #F1F5F9;
}
.lc-brand-icon {
width: 32px;
height: 32px;
object-fit: contain;
border-radius: 8px;
padding: 4px;
background: #FFF5F0;
border: 1px solid #FFD5C0;
}
.lc-brand-name {
font-size: 0.88rem;
font-weight: 700;
color: #0A1F44;
line-height: 1.2;
}
.lc-brand-sub {
font-size: 0.68rem;
color: #94A3B8;
display: block;
margin-top: 1px;
}

.lc-eyebrow {
font-size: 0.62rem;
font-weight: 700;
letter-spacing: 0.18em;
text-transform: uppercase;
color: #FF5200;
display: block;
margin-bottom: 6px;
text-align: center;
}
.lc-title {
font-size: 1.5rem;
font-weight: 800;
color: #0A1F44;
margin: 0 0 8px;
letter-spacing: -0.03em;
line-height: 1.15;
text-align: center;
}
.lc-desc {
font-size: 0.82rem;
color: #64748B;
line-height: 1.65;
margin-bottom: 24px;
text-align: center;
}

.gsi-btn {
display: flex;
align-items: center;
justify-content: center;
gap: 12px;
width: 100%;
background: #FFFFFF;
color: #1F2937 !important;
padding: 13px 20px;
border-radius: 14px;
border: 1.5px solid #E2E8F0;
font-weight: 700;
font-size: 0.92rem;
text-decoration: none !important;
cursor: pointer;
transition: all 0.2s ease;
box-shadow: 0 2px 8px rgba(15,23,42,0.06);
letter-spacing: -0.01em;
}
.gsi-btn:hover {
border-color: #CBD5E1;
box-shadow: 0 4px 16px rgba(15,23,42,0.10);
transform: translateY(-1px);
text-decoration: none !important;
}

.lc-divider {
display: flex;
align-items: center;
gap: 14px;
margin: 18px 0 0;
}
.lc-divider-line {
flex: 1;
height: 1px;
background: #E2E8F0;
}
.lc-divider-text {
font-size: 0.68rem;
font-weight: 600;
letter-spacing: 0.12em;
text-transform: uppercase;
color: #94A3B8;
}

.lc-bottom {
background: #FFFFFF;
border: 1px solid rgba(226,232,240,0.8);
border-top: none;
border-radius: 0 0 24px 24px;
padding: 20px 32px 28px;
box-shadow:
0 0 0 1px rgba(255,82,0,0.05),
0 20px 60px rgba(15,23,42,0.08),
0 4px 16px rgba(15,23,42,0.04);
}

.lc-field-label {
display: block;
font-size: 0.7rem;
font-weight: 700;
color: #64748B;
margin-bottom: 8px;
letter-spacing: 0.06em;
text-transform: uppercase;
}

[data-testid="stTextInput"] input {
background: #F8FAFC !important;
border: 1.5px solid #E2E8F0 !important;
border-radius: 12px !important;
color: #0F172A !important;
padding: 13px 16px !important;
font-size: 0.92rem !important;
transition: all 0.15s ease !important;
}
[data-testid="stTextInput"] input::placeholder {
color: #CBD5E1 !important;
}
[data-testid="stTextInput"] input:focus {
border-color: #FF5200 !important;
background: #FFFFFF !important;
box-shadow: 0 0 0 3px rgba(255,82,0,0.10) !important;
}

[data-testid="stFormSubmitButton"] button {
background: #FF5200 !important;
color: white !important;
border: none !important;
border-radius: 12px !important;
font-weight: 700 !important;
padding: 13px 20px !important;
font-size: 0.92rem !important;
letter-spacing: -0.01em !important;
box-shadow: 0 4px 16px rgba(255,82,0,0.30) !important;
transition: all 0.2s ease !important;
}
[data-testid="stFormSubmitButton"] button:hover {
background: #E84A00 !important;
box-shadow: 0 6px 24px rgba(255,82,0,0.45) !important;
transform: translateY(-1px) !important;
}

.lc-footer {
text-align: center;
margin-top: 18px;
padding-top: 16px;
border-top: 1px solid #F1F5F9;
}
.lc-footer-text {
font-size: 0.7rem;
color: #94A3B8;
line-height: 1.5;
}
.lc-footer-dot {
display: inline-block;
width: 5px; height: 5px;
background: #22C55E;
border-radius: 50%;
vertical-align: middle;
margin-right: 5px;
animation: pulse-dot 2s ease-in-out infinite;
}
@keyframes pulse-dot {
0%, 100% { opacity: 1; }
50% { opacity: 0.4; }
}

.stAlert { border-radius: 12px !important; margin-top: 12px !important; }
[data-testid="stForm"] { 
    background: #FFFFFF !important; 
    border: 1px solid rgba(226,232,240,0.8) !important; 
    border-radius: 24px !important; 
    padding: 36px 32px 32px !important; 
    box-shadow: 0 0 0 1px rgba(255,82,0,0.05), 0 20px 60px rgba(15,23,42,0.08), 0 4px 16px rgba(15,23,42,0.04) !important; 
}
</style>
""", unsafe_allow_html=True)

    with st.form("login_form", clear_on_submit=False):
        st.markdown(f"""
<div class="lc-logo-wrap">
<img class="lc-logo-main" src="{_ghn_logo}" alt="Giao Hang Nhanh">
</div>
<span class="lc-eyebrow">Cổng đăng nhập</span>
<div class="lc-title">Chào mừng trở lại</div>
<p class="lc-desc">Vui lòng đăng nhập để tiếp tục truy cập hệ thống.</p>
<a href="{auth_url}" target="_self" class="gsi-btn">
<img src="https://www.gstatic.com/firebasejs/ui/2.0.0/images/auth/google.svg" width="20" height="20">
Đăng nhập với Google
</a>
<div class="lc-divider">
<div class="lc-divider-line"></div>
<span class="lc-divider-text">hoặc dùng mã bảo mật</span>
<div class="lc-divider-line"></div>
</div>
""", unsafe_allow_html=True)

        st.markdown("<span class='lc-field-label'>Mã đăng nhập</span>", unsafe_allow_html=True)
        code_input = st.text_input("Access Code", type="password", label_visibility="collapsed", placeholder="Nhập mã bảo mật")
        submitted = st.form_submit_button("Đăng nhập bằng Mã", use_container_width=True)

        if submitted:
            code = code_input.strip()
            if not code:
                st.error("Vui lòng nhập mã đăng nhập.")
            elif code == st.secrets.get("ACCESS_CODE", "EX-TEAM-EES-2026"):
                email = "ex-team@ghn.vn"
                # Không kiểm tra Google Sheet cho tài khoản dùng mã chung, tự động cấp quyền User xem toàn bộ dữ liệu
                authorization = {
                    "email": email,
                    "idnv": "EX-TEAM",
                    "full_name": "Thành viên EX-TEAM",
                    "job_title": "Executive Team",
                    "role": "User",
                    "divisions": [],
                    "departments": [],
                    "sections": [],
                    "all_data_flag": True
                }
                name = "Thành viên EX-TEAM"
                picture = ""
                secure_token = secrets.token_urlsafe(32)
                now = time.time()
                current_sid = get_current_streamlit_session_id()
                with _sessions_lock:
                    sessions = _load_active_sessions()
                    sessions = _cleanup_expired_sessions(sessions)
                    sessions[secure_token] = {
                        "email": email,
                        "name": name,
                        "picture": picture,
                        "authorization": authorization,
                        "streamlit_session_id": current_sid,
                        "last_seen": now,
                        "created_at": now
                    }
                    _save_active_sessions(sessions)
                st.session_state.user_email = email
                st.session_state.user_name = name
                st.session_state.user_picture = picture
                st.session_state.current_token = secure_token
                st.session_state.user_authorization = authorization
                _role = authorization.get("role", "User") if isinstance(authorization, dict) else "User"
                log_access(email, name, _role, method="access_code")
                _set_remember_cookie(secure_token)
                st.query_params.clear()
                st.query_params["s"] = secure_token
                st.rerun()
            else:
                st.error("Mã đăng nhập không chính xác. Vui lòng thử lại.")

    st.markdown("""
<div class="lc-footer">
<span class="lc-footer-dot"></span>
<span class="lc-footer-text">Hệ thống bảo mật · Chỉ dành cho nội bộ GHN &amp; Scommerce</span>
</div>
</div>
""", unsafe_allow_html=True)


def _render_security_error_page():
    st.markdown("""
    <style>
        [data-testid="stSidebar"] { display: none !important; }
        header[data-testid="stHeader"] { display: none !important; }
        .login-wrap {
            display: flex; flex-direction: column; align-items: center;
            justify-content: center; min-height: 80vh; gap: 24px;
        }
        .login-card {
            background: white; border-radius: 20px; padding: 48px 56px;
            box-shadow: 0 8px 40px rgba(0,0,0,0.12);
            text-align: center; max-width: 480px; width: 100%;
            border-top: 4px solid #DC2626;
        }
        .login-title { font-size: 1.5rem; font-weight: 800; color: #DC2626; margin: 16px 0 8px; }
        .login-subtitle { font-size: 0.9rem; color: #475569; margin-bottom: 28px; line-height: 1.6; }
        .login-divider { border: none; border-top: 1px solid #E2E8F0; margin: 20px 0; }
        .google-btn {
            display: inline-block; background-color: #FF5200; color: white !important;
            text-decoration: none; padding: 12px 24px; border-radius: 8px;
            font-weight: 600; font-size: 1rem; width: 100%; text-align: center;
            box-sizing: border-box; transition: background-color 0.2s; margin-top: 10px;
        }
        .google-btn:hover { background-color: #E64A00; text-decoration: none; }
    </style>
    <div class="login-wrap">
        <div class="login-card">
            <div style="font-size: 1.5rem; font-weight: 700; color: #64748B; margin-bottom: 10px;">[Khoa]</div>
            <div class="login-title">Liên Kết Đã Được Sử Dụng</div>
            <div class="login-subtitle">
                Đường dẫn đăng nhập này hiện đang được mở ở một trình duyệt hoặc thiết bị khác để bảo vệ an toàn thông tin.<br><br>
                Vui lòng nhấp nút bên dưới để tự đăng nhập bằng tài khoản Google GHN của bạn.
            </div>
            <hr class="login-divider">
            <a href="/" target="_self" class="google-btn">
                Quay lại Trang Đăng Nhập
            </a>
        </div>
    </div>
    """, unsafe_allow_html=True)


if not is_admin:
    current_sid = get_current_streamlit_session_id()

    # 1. Xử lý callback OAuth (có ?code= trên URL)
    if "code" in st.query_params:
        code = st.query_params.get("code")
        
        # Ngăn chặn việc xử lý cùng một code 2 lần (Streamlit thỉnh thoảng rerun kép)
        if st.session_state.get("last_processed_oauth_code") == code:
            st.query_params.clear()
            st.rerun()
            
        st.session_state["last_processed_oauth_code"] = code
        
        with st.spinner("Đang xác thực Google..."):
            user_info = get_user_info(code, GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, REDIRECT_URI)

        if user_info and "email" in user_info:
            email = user_info["email"]
            authorization = _get_authorization(email)
            if authorization is not None:
                name = user_info.get("name", "User")
                picture = user_info.get("picture", "")
                
                secure_token = secrets.token_urlsafe(32)
                now = time.time()
                
                with _sessions_lock:
                    sessions = _load_active_sessions()
                    sessions = _cleanup_expired_sessions(sessions)
                    sessions[secure_token] = {
                        "email": email,
                        "name": name,
                        "picture": picture,
                        "authorization": authorization,
                        "streamlit_session_id": current_sid,
                        "last_seen": now,
                        "created_at": now
                    }
                    _save_active_sessions(sessions)
                
                st.session_state.user_email = email
                st.session_state.user_name = name
                st.session_state.user_picture = picture
                st.session_state.current_token = secure_token
                st.session_state.user_authorization = authorization
                _role = authorization.get("role", "User") if isinstance(authorization, dict) else "User"
                log_access(email, name, _role, method="google")
                _set_remember_cookie(secure_token)
                
                st.query_params.clear()
                st.query_params["s"] = secure_token
                st.rerun()
            else:
                st.query_params.clear()
                st.query_params["error"] = "1"  # Tránh tự động redirect loop
                _clear_user_session()
                _render_authorization_denied(email)
        else:
            st.query_params.clear()
            st.query_params["error"] = "1"  # Tránh tự động redirect loop
            st.error("Xác thực Google thất bại. Vui lòng thử lại.")
            _render_login_page()
            st.stop()

    # 2. Đồng bộ session từ URL, Session State hoặc remember cookie
    user_email = st.session_state.get("user_email")
    current_token = st.session_state.get("current_token") or _get_remember_cookie()

    if user_email and current_token:
        authorization = _get_authorization(user_email)
        if authorization is None:
            with _sessions_lock:
                sessions = _load_active_sessions()
                sessions.pop(current_token, None)
                _save_active_sessions(sessions)
            _clear_user_session()
            _clear_remember_cookie()
            st.query_params.clear()
            st.query_params["error"] = "1"
            _render_authorization_denied(user_email)

        st.session_state.user_authorization = authorization

        # User đã đăng nhập trong session này, cập nhật last_seen
        with _sessions_lock:
            sessions = _load_active_sessions()
            if current_token in sessions:
                sessions[current_token]["last_seen"] = time.time()
                sessions[current_token]["streamlit_session_id"] = current_sid
                sessions[current_token]["authorization"] = authorization
                _save_active_sessions(sessions)
            else:
                # Token không còn tồn tại trên server (hết hạn hoặc bị xóa)
                _clear_user_session()
                st.query_params.clear()
                st.rerun()
                
        # Giữ tham số s= trên URL đồng bộ với token hiện tại
        if st.query_params.get("s") != current_token:
            st.query_params["s"] = current_token
            
    else:
        # User chưa có thông tin trong session_state -> Đọc từ URL token ?s=
        query_token = st.query_params.get("s")
        if query_token:
            with _sessions_lock:
                sessions = _load_active_sessions()
                sessions = _cleanup_expired_sessions(sessions)
                
                if query_token in sessions:
                    data = sessions[query_token]
                    authorization = _get_authorization(data.get("email", ""))
                    if authorization is None:
                        sessions.pop(query_token, None)
                        _save_active_sessions(sessions)
                        _clear_user_session()
                        _clear_remember_cookie()
                        st.query_params.clear()
                        st.query_params["error"] = "1"
                        _render_authorization_denied(data.get("email", ""))

                    old_sid = data.get("streamlit_session_id")
                    
                    # Kiểm tra xem session cũ có thực sự còn active (WebSocket kết nối) không
                    if old_sid and old_sid != current_sid and is_streamlit_session_active(old_sid):
                        # GUEST MODE / SAO CHÉP LINK TRÙNG LẶP: Chặn đứng!
                        _render_security_error_page()
                        st.stop()
                    else:
                        # Hợp lệ (F5 hoặc tab mới sau khi tắt tab cũ): khôi phục & xoay vòng token bảo mật
                        new_token = secrets.token_urlsafe(32)
                        now = time.time()
                        
                        sessions[new_token] = {
                            "email": data["email"],
                            "name": data["name"],
                            "picture": data["picture"],
                            "authorization": authorization,
                            "streamlit_session_id": current_sid,
                            "last_seen": now,
                            "created_at": now
                        }
                        sessions.pop(query_token, None)
                        _save_active_sessions(sessions)
                        
                        st.session_state.user_email = data["email"]
                        st.session_state.user_name = data["name"]
                        st.session_state.user_picture = data["picture"]
                        st.session_state.current_token = new_token
                        st.session_state.user_authorization = authorization
                        
                        st.query_params.clear()
                        st.query_params["s"] = new_token
                        st.rerun()
                else:
                    # Token không hợp lệ hoặc đã hết hạn
                    st.query_params.clear()
                    st.query_params["error"] = "1"
                    _render_login_page()
                    st.stop()
        else:
            # Chưa đăng nhập và không có token trên URL:
            # Thử khôi phục từ remember cookie trước khi hiện trang login
            cookie_token = _get_remember_cookie()
            if cookie_token:
                with _sessions_lock:
                    sessions = _load_active_sessions()
                    sessions = _cleanup_expired_sessions(sessions)

                    if cookie_token in sessions:
                        data = sessions[cookie_token]
                        authorization = _get_authorization(data.get("email", ""))
                        if authorization is None:
                            sessions.pop(cookie_token, None)
                            _save_active_sessions(sessions)
                            _clear_remember_cookie()
                            st.query_params.clear()
                            st.query_params["error"] = "1"
                            _render_authorization_denied(data.get("email", ""))

                        new_token = secrets.token_urlsafe(32)
                        now = time.time()

                        sessions[new_token] = {
                            "email": data["email"],
                            "name": data["name"],
                            "picture": data["picture"],
                            "authorization": authorization,
                            "streamlit_session_id": current_sid,
                            "last_seen": now,
                            "created_at": now
                        }
                        sessions.pop(cookie_token, None)
                        _save_active_sessions(sessions)

                        st.session_state.user_email = data["email"]
                        st.session_state.user_name = data["name"]
                        st.session_state.user_picture = data["picture"]
                        st.session_state.current_token = new_token
                        st.session_state.user_authorization = authorization

                        _set_remember_cookie(new_token)
                        st.query_params.clear()
                        st.query_params["s"] = new_token
                        st.rerun()
                    else:
                        _clear_remember_cookie()

            # Cookie không hợp lệ hoặc không có -> Hiện trang Login
            if st.query_params.get("logout") == "1" or st.query_params.get("error") == "1":
                is_err = st.query_params.get("error") == "1"
                st.query_params.clear()
                if is_err:
                    st.toast("Phiên đăng nhập hết hạn hoặc xảy ra lỗi. Vui lòng đăng nhập lại.")
                else:
                    st.toast("Đăng xuất thành công.")

                _render_login_page()
                st.stop()
            else:
                _render_login_page()
                st.stop()

# Kiểm tra Role Admin thực sự từ Google Sheets sau khi user đã đăng nhập
_auth_info = st.session_state.get("user_authorization", {})
is_real_admin = isinstance(_auth_info, dict) and _auth_info.get("role", "").upper() == "ADMIN"


if is_locked and not is_real_admin:
    st.markdown("""
    <div style='text-align: center; margin-top: 100px;'>
        <img src='https://res.cloudinary.com/dd7gti2kn/image/upload/v1772773708/LOGO%20GHN/Logo/LOGO_INAN_sep2os.png' width='200'>
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
from config.groups import get_available_groups, GROUP_REGISTRY
from views import (
    overview_ees_2026,
    company_overview, hris_linkage,
    view_a_current_state, view_b_problem_groups,
    view_c_key_issues, view_d_root_cause,
    view_e_impact_risk, view_g_kpi_impact,
    view_h_appendix, view_i_data_trust
)
from shared.codebook import PILLAR_META, PILLAR_ORDER
from shared.loading import TerminalLoader

# --- BACKGROUND DATA PRELOADING ---
if "data_preloaded" not in st.session_state:
    st.session_state.data_preloaded = True
    try:
        from streamlit.runtime.scriptrunner import add_script_run_ctx
        import threading
        
        def _preload_task():
            try:
                load_all_available()
            except Exception as e:
                pass
                
        preload_thread = threading.Thread(target=_preload_task, daemon=True)
        add_script_run_ctx(preload_thread)
        preload_thread.start()
    except Exception:
        pass

# ── WebSocket Keepalive — ping mỗi 25s để tránh idle disconnect ─────────────
st.markdown("""
<script>
(function() {
    var _kes_interval = null;
    function _kes_start() {
        if (_kes_interval) return;
        _kes_interval = setInterval(function() {
            fetch('/_stcore/health')
                .then(function() {})
                .catch(function() {});
        }, 25000);
    }
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', _kes_start);
    } else {
        _kes_start();
    }
})();
</script>
""", unsafe_allow_html=True)

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

/* Hide stale elements while the newly selected page is loading.
   Scoped to top-level to avoid interfering with @st.fragment. */
.stApp > [data-testid="stale-element-container"], 
.stApp > div.st-emotion-cache-1kyxreq[data-stale="true"] {
    opacity: 0 !important;
    transition: none !important;
    visibility: hidden !important;
}

html, body, .stApp {
    font-family: 'Inter', 'Segoe UI', system-ui, -apple-system, sans-serif !important;
    background:
        radial-gradient(circle at top right, rgba(255, 82, 0, 0.06), transparent 22%),
        linear-gradient(180deg, #F8FAFC 0%, #F8FAFC 100%) !important;
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
    display: flex;
    align-items: center;
    gap: 12px;
}
.sb-logo {
    height: 36px;
    object-fit: contain;
    display: block;
}
.sb-text {
    display: flex;
    flex-direction: column;
    justify-content: center;
    min-width: 0;
}
.sb-title {
    font-size: 1.05rem;
    font-weight: 800;
    color: #0A1F44;
    display: block;
    line-height: 1.2;
    white-space: nowrap;
}
.sb-sub {
    font-size: 0.68rem;
    color: #94A3B8;
    display: block;
    margin-top: 5px;
    font-weight: 500;
    line-height: 1.25;
    white-space: nowrap;
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
    background: rgba(255,255,255,0.88) !important;
    border: 1px solid #E2E8F0 !important;
    border-radius: 14px !important;
    padding: 6px !important;
    gap: 2px !important;
    box-shadow: 0 10px 30px rgba(15,23,42,0.05) !important;
    backdrop-filter: blur(10px);
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
    border-radius: 14px;
    padding: 20px 22px;
    height: 100%;
    transition: all 0.15s ease;
    position: relative;
    overflow: hidden;
    box-shadow: 0 1px 3px rgba(15,23,42,0.04);
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
    border-radius: 10px !important;
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
    border-radius: 14px !important;
    padding: 16px 20px !important;
    box-shadow: 0 1px 3px rgba(15,23,42,0.04);
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

st.markdown("""
<style>
/* ═══════ MOBILE RESPONSIVE LAYER ═══════
   Desktop stays controlled by the main CSS above. These rules only apply to
   tablet/phone widths so the current web layout is not affected. */
@media (max-width: 768px) {
    html, body, .stApp {
        overflow-x: hidden !important;
    }

    .block-container {
        padding-top: 1.1rem !important;
        padding-left: 0.8rem !important;
        padding-right: 0.8rem !important;
        padding-bottom: 2rem !important;
    }

    /* Let phone users collapse/open the sidebar when Streamlit renders it as a drawer. */
    [data-testid="stSidebarCollapseButton"],
    button[title="Collapse sidebar"],
    button[aria-label="Collapse sidebar"],
    button[aria-label="Close sidebar"],
    button[title="Close sidebar"],
    button[aria-label="Thu nhỏ thanh bên"],
    button[title="Thu nhỏ thanh bên"] {
        display: flex !important;
        visibility: visible !important;
        opacity: 1 !important;
    }

    /* Safari can render Streamlit's Material Symbol name as literal text
       (for example "keyboard_double_arrow_left"). Replace it with CSS. */
    [data-testid="stSidebarCollapseButton"] button,
    button[title="Collapse sidebar"],
    button[aria-label="Collapse sidebar"],
    button[aria-label="Close sidebar"],
    button[title="Close sidebar"],
    button[aria-label="Thu nhỏ thanh bên"],
    button[title="Thu nhỏ thanh bên"] {
        width: 38px !important;
        height: 38px !important;
        min-width: 38px !important;
        padding: 0 !important;
        border-radius: 10px !important;
        align-items: center !important;
        justify-content: center !important;
        overflow: hidden !important;
        color: transparent !important;
        font-size: 0 !important;
        line-height: 0 !important;
    }

    [data-testid="stSidebarCollapseButton"] button span,
    button[title="Collapse sidebar"] span,
    button[aria-label="Collapse sidebar"] span,
    button[aria-label="Close sidebar"] span,
    button[title="Close sidebar"] span,
    button[aria-label="Thu nhỏ thanh bên"] span,
    button[title="Thu nhỏ thanh bên"] span {
        display: none !important;
        font-size: 0 !important;
        width: 0 !important;
        overflow: hidden !important;
    }

    [data-testid="stSidebarCollapseButton"] button::before,
    button[title="Collapse sidebar"]::before,
    button[aria-label="Collapse sidebar"]::before,
    button[aria-label="Close sidebar"]::before,
    button[title="Close sidebar"]::before,
    button[aria-label="Thu nhỏ thanh bên"]::before,
    button[title="Thu nhỏ thanh bên"]::before {
        content: "" !important;
        display: block !important;
        width: 9px !important;
        height: 9px !important;
        border-left: 2px solid #475569 !important;
        border-bottom: 2px solid #475569 !important;
        transform: rotate(45deg) !important;
        margin-left: 4px !important;
    }

    [data-testid="stSidebar"] {
        width: min(88vw, 330px) !important;
        min-width: min(88vw, 330px) !important;
        max-width: min(88vw, 330px) !important;
    }

    [data-testid="stSidebar"] section[data-testid="stSidebarContent"] {
        padding-bottom: 1rem !important;
        overflow-x: hidden !important;
    }

    .sb-brand {
        padding: 16px 16px 12px !important;
        gap: 8px !important;
    }

    .sb-logo {
        height: 30px !important;
        margin-bottom: 0 !important;
    }

    .sb-title {
        font-size: 0.98rem !important;
    }

    .sb-sub {
        font-size: 0.61rem !important;
        margin-top: 4px !important;
    }

    .sb-section {
        padding: 12px 16px 6px !important;
    }

    /* Streamlit columns and explicit horizontal blocks should stack on phones. */
    [data-testid="column"] {
        width: 100% !important;
        flex: 1 1 100% !important;
        min-width: 0 !important;
    }

    div[data-testid="stHorizontalBlock"] {
        gap: 0.75rem !important;
    }

    .pg-header {
        flex-direction: column !important;
        align-items: flex-start !important;
        gap: 12px !important;
        margin-bottom: 22px !important;
        padding-bottom: 18px !important;
    }

    .pg-title {
        font-size: clamp(1.75rem, 8vw, 2.35rem) !important;
        line-height: 1.08 !important;
    }

    .pg-subtitle {
        font-size: 0.82rem !important;
    }

    .pg-badge {
        align-self: flex-start !important;
        padding: 5px 11px !important;
    }

    .hero-card {
        padding: 22px 18px !important;
        border-radius: 14px !important;
    }

    .hero-title {
        font-size: 1.28rem !important;
    }

    .hero-metrics,
    .ghn-metrics,
    .ghn-context,
    .ghn-process-flow,
    .dt-grid,
    .dt-metrics,
    .dt-proof-grid,
    .ed-metrics-grid,
    .ed-masonry,
    .ed-team-grid {
        grid-template-columns: 1fr !important;
    }

    .ghn-shell,
    .dt-shell,
    .ed-hero-shell,
    .ed-team-section {
        padding: 20px !important;
        border-radius: 20px !important;
        margin-left: 0 !important;
        margin-right: 0 !important;
    }

    .ghn-hero,
    .dt-hero,
    .ed-hero-shell,
    .ed-timeline-section {
        grid-template-columns: 1fr !important;
        gap: 18px !important;
        transform: none !important;
    }

    .ghn-command {
        min-height: 235px !important;
        padding: 20px !important;
        transform: none !important;
        border-radius: 18px !important;
    }

    .ghn-title,
    .dt-title,
    .ed-headline {
        font-size: clamp(2rem, 10vw, 2.75rem) !important;
        line-height: 1.08 !important;
        letter-spacing: -0.035em !important;
    }

    .ghn-command-score {
        font-size: clamp(3rem, 17vw, 4.3rem) !important;
    }

    .ghn-metric,
    .ghn-process-card,
    .custom-metric-card,
    .premium-kpi-card,
    [data-testid="stMetric"] {
        padding: 16px !important;
        border-radius: 14px !important;
    }

    .ghn-metric-value,
    .ghn-process-value,
    .metric-value,
    [data-testid="stMetricValue"] {
        font-size: clamp(1.7rem, 8vw, 2.2rem) !important;
        white-space: normal !important;
        overflow-wrap: anywhere !important;
    }

    .sample-flow-panel {
        padding: 12px 14px !important;
        border-radius: 12px !important;
    }

    .sample-flow-head {
        align-items: flex-start !important;
    }

    .sample-flow-desc {
        width: 100% !important;
        margin-left: 0 !important;
        line-height: 1.45 !important;
    }

    .sample-flow-body {
        flex-direction: column !important;
        align-items: stretch !important;
        gap: 10px !important;
    }

    .sample-flow-step {
        text-align: left !important;
        border: 1px solid #E2E8F0 !important;
        border-radius: 10px !important;
        padding: 11px 12px !important;
        background: #FFFFFF !important;
    }

    .sample-flow-arrow {
        display: none !important;
    }

    .sample-flow-progress {
        width: 100% !important;
        min-width: 0 !important;
    }

    .stTabs [data-baseweb="tab-list"] {
        overflow-x: auto !important;
        flex-wrap: nowrap !important;
        justify-content: flex-start !important;
        scrollbar-width: thin !important;
    }

    .stTabs [data-baseweb="tab"] {
        flex: 0 0 auto !important;
        padding: 9px 14px !important;
        min-width: max-content !important;
        font-size: 0.78rem !important;
    }

    [data-testid="stDataFrame"],
    [data-testid="stTable"] {
        max-width: 100% !important;
        overflow-x: auto !important;
    }

    .js-plotly-plot,
    .plot-container,
    [data-testid="stPlotlyChart"] {
        max-width: 100% !important;
        overflow-x: auto !important;
    }

    img,
    video,
    iframe {
        max-width: 100% !important;
    }

    video {
        height: auto !important;
        border-radius: 14px !important;
    }

    .tl-box {
        margin: 10px 0 14px !important;
        border-radius: 9px !important;
    }

    .tl-body {
        font-size: 11px !important;
        overflow-x: auto !important;
    }

    .tl-row {
        white-space: normal !important;
        align-items: flex-start !important;
    }

    .ed-masonry {
        grid-auto-rows: auto !important;
    }

    .ed-masonry-item,
    .ed-masonry-item-large,
    .ed-masonry-item-tall,
    .ed-masonry-item-wide {
        grid-column: auto !important;
        grid-row: auto !important;
        min-height: 220px !important;
    }

    .ed-timeline-node {
        flex-direction: column !important;
        gap: 10px !important;
    }

    .ed-timeline-big-num {
        min-width: 0 !important;
        text-align: left !important;
        font-size: 2.8rem !important;
    }

    .ai-content {
        max-height: none !important;
        font-size: 0.82rem !important;
    }
}

@media (max-width: 480px) {
    .block-container {
        padding-left: 0.65rem !important;
        padding-right: 0.65rem !important;
    }

    .ghn-shell,
    .dt-shell,
    .ed-hero-shell,
    .ed-team-section,
    .hero-card {
        padding: 16px !important;
        border-radius: 18px !important;
    }

    .ghn-mini-grid {
        grid-template-columns: 1fr !important;
    }

    .stButton > button {
        width: 100% !important;
    }
}
</style>
""", unsafe_allow_html=True)


# ── State & Setup ───────────────────────────────────────────────────────────
available = get_available_groups()
group_opts = list(available.keys())

# Lọc nhóm khảo sát theo survey_groups của user (nếu bị giới hạn)
_auth_info_groups = st.session_state.get("user_authorization", {})
if isinstance(_auth_info_groups, dict):
    _allowed_groups = _auth_info_groups.get("survey_groups", ["ALL"])
    if _allowed_groups and "ALL" not in _allowed_groups:
        group_opts = [g for g in group_opts if g in _allowed_groups]

def _safe_tenure_index(value):
    try:
        return tenure_opts.index(value)
    except ValueError:
        return 0  # Fallback to 'Tất cả'

if 'global_tenure' not in st.session_state:
    st.session_state.global_tenure = 'Tất cả'

tenure_opts = [
    'Tất cả', 'Dưới 1 tháng', 'Trên 1 đến 3 tháng', 'Trên 3 đến 6 tháng',
    'Trên 6 đến 9 tháng', 'Trên 9 đến 12 tháng', 'Trên 1 đến 2 năm',
    'Trên 2 đến 3 năm', 'Trên 3 đến 5 năm', 'Trên 5 năm', 'Khác'
]

def apply_global_filters(df):
    if df is None or df.empty:
        return df
    if st.session_state.global_tenure != 'Tất cả':
        if 'Q5' in df.columns:
            return df[df['Q5'] == st.session_state.global_tenure]
    return df

OVERVIEW_LABEL = "EES 2026 Overview"
COMPANY_LABEL = "Tổng quan GHN"
main_loading_slot = st.empty()
page_loader = None

# Phạm vi data của user hiện tại (theo Google Sheet phân quyền)
user_scope = resolve_data_scope(st.session_state.get("user_authorization"))
scope_restricted = not user_scope.get("unrestricted", True)

with st.sidebar:

    # Brand block
    st.markdown("""
    <div class="sb-brand">
        <img src="https://res.cloudinary.com/dd7gti2kn/image/upload/t_justlog/LOGO%20GHN/Logo/LOGO_INAN_1_lghbnf.png" class="sb-logo" alt="GHN Logo">
        <div class="sb-text">
            <span class="sb-title">EES 2026 Dashboard</span>
            <span class="sb-sub">Employee Engagement Survey · 2026</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Main navigation
    st.markdown('<span class="sb-section">Phân khúc báo cáo</span>', unsafe_allow_html=True)
    import streamlit_antd_components as sac

    menu_items = []

    # Top-level items (value = label, không cần prefix)
    menu_items.append(sac.MenuItem(OVERVIEW_LABEL, icon='house'))

    if not scope_restricted:
        menu_items.append(sac.MenuItem("Độ tin cậy dữ liệu", icon='shield-check'))

    menu_items.append(sac.MenuItem(COMPANY_LABEL, icon='graph-up', tag=sac.Tag("Core", color="blue", bordered=False)))

    # Group items với child có value duy nhất: "{group_id}__{child_label}"
    for g in group_opts:
        label = available[g]['label']
        group_children = []

        # 1. Tổng quan Khảo sát
        group_children.append(sac.MenuItem(f"{g}__Tổng quan Khảo sát"))

        # 2. Các trụ cột
        for p in PILLAR_ORDER:
            p_name = PILLAR_META[p]['name']
            group_children.append(sac.MenuItem(f"{g}__{p_name}"))

        # 3. Đo lường Impact & Xem Báo Cáo
        group_children.append(sac.MenuItem(f"{g}__Đo lường Impact"))
        group_children.append(sac.MenuItem(f"{g}__Xem Báo Cáo"))

        menu_items.append(sac.MenuItem(label, icon='diagram-3', children=group_children))

    menu_items.append(sac.MenuItem("Phụ lục", icon='book'))

    if is_real_admin:
        menu_items.append(sac.MenuItem("Admin Panel", icon="gear"))

    # Format function: hiển thị title, bỏ qua value prefix
    _PILLAR_MENU_LABELS = {
        PILLAR_META[pillar_id]["name"]: f"{pillar_id} - {PILLAR_META[pillar_id]['name']}"
        for pillar_id in PILLAR_ORDER
    }

    def _menu_format(v):
        if isinstance(v, str) and "__" in v:
            v = v.split("__", 1)[1]
        return _PILLAR_MENU_LABELS.get(v, v)

    # return_index=False → trả về value của MenuItem được chọn
    sel_value = sac.menu(
        menu_items,
        key='sac_main_menu',
        return_index=False,
        format_func=_menu_format,
        size='sm',
        open_all=False,
        variant='subtle',
        color='indigo',
    )

    # Mapping value → (dashboard, nav)
    _NAV_MAP = {
        OVERVIEW_LABEL: (OVERVIEW_LABEL, None),
        COMPANY_LABEL: (COMPANY_LABEL, None),
        "Phụ lục": ("Phụ lục", None),
        "Độ tin cậy dữ liệu": ("Độ tin cậy dữ liệu", None),
        "Admin Panel": ("Admin Panel", None),
    }
    # Child items + parent items của các group (value duy nhất nên không bị ghi đè)
    for g in group_opts:
        grp_label = available[g]['label']
        # Parent click → navigate to "Tổng quan Khảo sát" của group đó
        _NAV_MAP[grp_label] = (grp_label, "Tổng quan Khảo sát")
        _NAV_MAP[f"{g}__Tổng quan Khảo sát"] = (grp_label, "Tổng quan Khảo sát")
        _NAV_MAP[f"{g}__Đo lường Impact"] = (grp_label, "Đo lường Impact")
        _NAV_MAP[f"{g}__Xem Báo Cáo"] = (grp_label, "Xem Báo Cáo")
        for p in PILLAR_ORDER:
            p_name = PILLAR_META[p]['name']
            _NAV_MAP[f"{g}__{p_name}"] = (grp_label, p_name)

    sel_dashboard, sel_nav = _NAV_MAP.get(sel_value, (OVERVIEW_LABEL, None))

    st.markdown('<div class="sb-divider"></div>', unsafe_allow_html=True)

    is_overview = (sel_dashboard == OVERVIEW_LABEL)
    is_company = (sel_dashboard == COMPANY_LABEL)
    is_appendix = (sel_dashboard == "Phụ lục")
    is_data_trust = (sel_dashboard == "Độ tin cậy dữ liệu")
    is_admin_panel = (sel_dashboard == "Admin Panel")

    # Initialize scope variables
    sel_group   = None
    df_filtered = None
    n_before    = 0

    if is_appendix or is_data_trust or is_overview or is_admin_panel:
        pass

    elif is_company:
        # Company-level tenure filter
        st.markdown('<span class="sb-section">Bộ lọc</span>', unsafe_allow_html=True)
        sel_tenure_sb = st.selectbox(
            "Thâm niên", tenure_opts,
            index=_safe_tenure_index(st.session_state.global_tenure),
            key="tenure_co"
        )
        st.session_state.global_tenure = sel_tenure_sb

    elif not is_overview:
        # Identify selected group
        for g in group_opts:
            if available[g]['label'] == sel_dashboard:
                sel_group = g
                break
        
        if sel_group is None:
            st.error(f"Không tìm thấy nhóm khảo sát: {sel_dashboard}")
            st.stop()

        # Filters
        st.markdown('<span class="sb-section">Bộ lọc</span>', unsafe_allow_html=True)

        # Load raw data (for building filter options)
        _grp_label = GROUP_REGISTRY.get(sel_group, {}).get("short", sel_group)
        page_loader = TerminalLoader(main_loading_slot, f"Đang tải dữ liệu nhóm {sel_group}")
        try:
            page_loader.add(f"Đang tải dữ liệu khảo sát nhóm {sel_group} - {_grp_label}...")
            df_raw, n_before = load_group(sel_group)
            # Áp dụng phân quyền phạm vi (vd chỉ xem Section/Department được cấp)
            df_raw, _ = apply_scope_filter(df_raw, st.session_state.get("user_authorization"))
            page_loader.add(f"Đã tải dữ liệu khảo sát nhóm {sel_group} ({len(df_raw):,} mẫu trong phạm vi).", "ok")
            page_loader.add("Đang chuẩn bị bộ lọc phòng ban / section...")
        except Exception as e:
            st.error(f"Không thể tải dữ liệu cho nhóm {sel_group}: {e}")
            import traceback
            st.code(traceback.format_exc())
            st.stop()


        sel_tenure_sb = st.selectbox(
            "Thâm niên", tenure_opts,
            index=_safe_tenure_index(st.session_state.global_tenure),
            key="tenure_grp"
        )
        st.session_state.global_tenure = sel_tenure_sb
        df_filtered_tenure = apply_global_filters(df_raw)
        # Benchmark phải nằm trong đúng phạm vi được cấp quyền. Với user toàn quyền,
        # đây vẫn là toàn nhóm; với user giới hạn, không làm lộ số liệu ngoài scope.
        df_bench_group = df_filtered_tenure.copy()

        div_opts = ['Tất cả Khối']
        if 'division' in df_filtered_tenure.columns:
            div_opts += sorted(df_filtered_tenure['division'].dropna().unique().tolist())
        sel_div = st.selectbox("Khối", div_opts, key=f"filter_div_{sel_group}")

        dept_opts = ['Tất cả Phòng ban']
        if sel_div != 'Tất cả Khối' and 'department' in df_filtered_tenure.columns:
            dept_opts += sorted(
                df_filtered_tenure[df_filtered_tenure['division'] == sel_div]
                ['department'].dropna().unique().tolist()
            )
        elif 'department' in df_filtered_tenure.columns:
            dept_opts += sorted(df_filtered_tenure['department'].dropna().unique().tolist())
        sel_dept = st.selectbox(
            "Phòng ban",
            dept_opts,
            key=f"filter_dept_{sel_group}_{sel_div}",
        )

        sec_opts = ['Tất cả Section']
        if sel_dept != 'Tất cả Phòng ban' and 'section' in df_filtered_tenure.columns:
            sec_opts += sorted(
                df_filtered_tenure[df_filtered_tenure['department'] == sel_dept]
                ['section'].dropna().unique().tolist()
            )
        elif 'section' in df_filtered_tenure.columns:
            sec_opts += sorted(df_filtered_tenure['section'].dropna().unique().tolist())
        sel_sec = st.selectbox(
            "Section",
            sec_opts,
            key=f"filter_sec_{sel_group}_{sel_div}_{sel_dept}",
        )

        # Apply all filters
        df_filtered = df_filtered_tenure.copy()
        if sel_div != 'Tất cả Khối' and 'division' in df_filtered.columns:
            df_filtered = df_filtered[df_filtered['division'] == sel_div]
        if sel_dept != 'Tất cả Phòng ban' and 'department' in df_filtered.columns:
            df_filtered = df_filtered[df_filtered['department'] == sel_dept]
        if sel_sec != 'Tất cả Section' and 'section' in df_filtered.columns:
            df_filtered = df_filtered[df_filtered['section'] == sel_sec]

    # Spacer
    st.markdown('<div style="height: 40px;"></div>', unsafe_allow_html=True)
    
    # User info + logout (Moved to bottom)
    _u_email   = st.session_state.get("user_email", "")
    _u_name    = st.session_state.get("user_name", _u_email)
    _u_picture = st.session_state.get("user_picture", "")
    if _u_email:
        _u_auth = st.session_state.get("user_authorization", {})
        _u_role = _u_auth.get("role", "User") if isinstance(_u_auth, dict) else "User"
        _role_str = str(_u_role).strip().upper()
        
        if _role_str == "ADMIN":
            _role_badge = '<span style="background-color: #DC2626; color: white; font-size: 0.55rem; font-weight: 800; padding: 2px 6px; border-radius: 4px; margin-left: 6px; letter-spacing: 0.05em; vertical-align: middle;">ADMIN</span>'
        else:
            _role_badge = '<span style="background-color: #3B82F6; color: white; font-size: 0.55rem; font-weight: 800; padding: 2px 6px; border-radius: 4px; margin-left: 6px; letter-spacing: 0.05em; vertical-align: middle;">USER</span>'

        _avatar_html = f'<img src="{_u_picture}" style="width:32px;height:32px;border-radius:50%;object-fit:cover;border:2px solid #FF5200;">' if _u_picture else f'<div style="width:32px;height:32px;border-radius:50%;background:#FF5200;display:flex;align-items:center;justify-content:center;color:white;font-weight:700;font-size:0.9rem;">{_u_name[0].upper()}</div>'
        st.markdown(f"""
        <div style="display:flex;align-items:center;gap:10px;padding:15px 0 10px;margin-top:auto;border-top:1px solid #E2E8F0;">
            {_avatar_html}
            <div>
                <div style="font-size:0.82rem;font-weight:700;color:#0F172A;line-height:1.2;display:flex;align-items:center;">
                    {_u_name} {_role_badge}
                </div>
                <div style="font-size:0.72rem;color:#64748B;">{_u_email}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Đăng xuất"):
            # Xóa token khỏi server-side registry
            token = st.session_state.get("current_token")
            if token:
                with _sessions_lock:
                    sessions = _load_active_sessions()
                    sessions.pop(token, None)
                    _save_active_sessions(sessions)

            # Dọn sạch session state, cookie và query parameters
            _clear_user_session()
            _clear_remember_cookie()
            st.query_params.clear()
            st.query_params["logout"] = "1"
            st.rerun()

# ── MAIN CONTENT ─────────────────────────────────────────────────────────────
if is_overview:
    try:
        overview_ees_2026.render()
    except Exception as e:
        st.error(f"Lỗi khi tải Overview EES 2026: {e}")
        import traceback
        st.code(traceback.format_exc())

elif is_data_trust:
    if scope_restricted:
        st.info("Trang Độ tin cậy dữ liệu chỉ dành cho tài khoản xem toàn công ty.")
        st.stop()
    try:
        loader = TerminalLoader(main_loading_slot, "Đang tải dữ liệu độ tin cậy")
        loader.add("Đang tải dữ liệu EES 2026...")
        summary_df = view_i_data_trust.compute_reliability_table(log_callback=loader.add)
        loader.add("Đang dựng giao diện Thẩm định & Độ tin cậy dữ liệu...")
        loader.done()
        loader.clear()
        view_i_data_trust.render(summary_df=summary_df)
    except Exception as e:
        st.error(f"Lỗi khi tải Độ tin cậy dữ liệu: {e}")
        import traceback
        st.code(traceback.format_exc())

elif is_admin_panel:
    try:
        from views import admin_panel
        admin_panel.render()
    except Exception as e:
        st.error(f"Lỗi khi tải Admin Panel: {e}")
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
        loader = TerminalLoader(main_loading_slot, "Đang tải dữ liệu toàn công ty")
        

        
        loader.add("Đang tải dữ liệu EES 2026...")
        all_data = load_all_available(log_callback=loader.add)
        loader.add("Đang áp dụng phân quyền & bộ lọc thâm niên...")
        _auth = st.session_state.get("user_authorization")
        filtered_all_data = {}
        for k, v in all_data.items():
            _df0, _n_before0 = v
            _df_scoped, _sinfo = apply_scope_filter(_df0, _auth)
            # Giữ nguyên n_before (raw count) cho user toàn quyền; user bị giới hạn
            # dùng số mẫu trong phạm vi để tỷ lệ phản hồi không bị sai lệch.
            _n_b = _n_before0 if _sinfo["unrestricted"] else len(_df_scoped)
            filtered_all_data[k] = (apply_global_filters(_df_scoped), _n_b)
        # User bị giới hạn: bỏ các nhóm không có dữ liệu thuộc phạm vi
        if scope_restricted:
            filtered_all_data = {k: v for k, v in filtered_all_data.items() if not v[0].empty}
        loader.add("Đang tính toán KPI và dựng giao diện Tổng quan GHN...")
        loader.done()
        if scope_restricted and not filtered_all_data:
            loader.clear()
            st.info("Bạn không có dữ liệu thuộc phạm vi được cấp quyền.")
        else:
            company_overview.render(
                filtered_all_data,
                available,
                scope_restricted=scope_restricted,
            )
            loader.clear()  # Clear AFTER render hoàn thành — tránh trang trắng
    except Exception as e:
        st.error(f"Lỗi khi tải view Tổng quan: {e}")
        import traceback
        st.code(traceback.format_exc())

else:
    cfg    = available[sel_group]
    n_resp = df_filtered.shape[0] if df_filtered is not None else 0

    # User bị giới hạn và nhóm này không có dữ liệu trong phạm vi
    if scope_restricted and (df_filtered is None or df_filtered.empty):
        if page_loader is not None: page_loader.clear()
        st.warning(
            "Nhóm khảo sát này không có dữ liệu thuộc phạm vi bạn được cấp quyền xem. "
            "Vui lòng chọn nhóm khảo sát khác từ sidebar."
        )
        st.stop()

    if page_loader is not None:
        page_loader.add("Đang áp dụng bộ lọc thâm niên / phòng ban...")
        _view_label = sel_nav or "phân tích nhóm"
        page_loader.add(f"Đang tính toán KPI và dựng giao diện {_view_label}...")
        page_loader.done()
        page_loader.clear()

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
        sel_pillar = None
        for p_id in PILLAR_ORDER:
            if sel_nav and PILLAR_META[p_id]['name'] in sel_nav:
                sel_pillar = p_id
                break

        if sel_nav == "Tổng quan Khảo sát":
            view_a_current_state.render(df_filtered, cfg, group_id=sel_group, df_bench=df_bench_group)
        elif sel_nav == "Xem Báo Cáo":
            from views import narrative_flow
            narrative_flow.render_narrative(df_filtered, cfg, sel_group, df_bench=df_bench_group)
        elif sel_pillar:
            from views import pillar_renderer
            pillar_renderer.render(df_filtered, cfg, sel_group, sel_pillar)
        elif sel_nav and "Đo lường Impact" in sel_nav:
            view_g_kpi_impact.render(df_filtered, cfg)
        else:
            st.info("Chọn một trụ cột từ sidebar bên trái.")
    except Exception as e:
        st