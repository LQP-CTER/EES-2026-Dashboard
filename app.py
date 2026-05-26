import streamlit as st
import pandas as pd
import sys, os
import importlib

# Setup paths
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__))))

# Force reload shared modules to prevent caching issues in Streamlit
import shared.plotly_theme
importlib.reload(shared.plotly_theme)
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
GOOGLE_CLIENT_ID = st.secrets.get("GOOGLE_CLIENT_ID", "")
GOOGLE_CLIENT_SECRET = st.secrets.get("GOOGLE_CLIENT_SECRET", "")
REDIRECT_URI = st.secrets.get("REDIRECT_URI", "http://localhost:8501/")

is_admin = st.session_state.get("is_admin", False)

if not is_admin:
    # Check if redirect contains auth code
    if "code" in st.query_params:
        code = st.query_params.get("code")
        user_info = get_user_info(code, GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, REDIRECT_URI)
        if user_info and "email" in user_info:
            st.session_state.user_email = user_info["email"]
            st.session_state.user_name = user_info.get("name", "User")
            st.session_state.user_picture = user_info.get("picture", "")
        else:
            st.error("Xác thực Google thất bại. Vui lòng thử lại.")
        st.query_params.clear()
        st.rerun()

    # Tạm thời vô hiệu hóa Đăng nhập Google (Bypass 403 Error)
    user_email = st.session_state.get("user_email")
    if not user_email:
        user_email = "tester@ghn.vn"
        st.session_state.user_email = user_email

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
            <span style="font-size: 1.2rem;">📢</span>
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
    view_e_impact_risk, view_f_action_priority, view_g_kpi_impact
)

# ── Custom CSS ──────────────────────────────────────────────────────────────
st.markdown("""<style>
/* ═══════ BASE ═══════ */
/* Hide Streamlit Toolbar & Deploy Button */
#MainMenu {visibility: hidden !important;}
header, [data-testid="stHeader"] {
    display: block !important;
    visibility: visible !important;
    background: transparent !important;
    z-index: 999990 !important;
}
[data-testid="collapsedControl"],
[data-testid="stSidebarCollapseButton"],
button[aria-label="Expand sidebar"],
button[title="Expand sidebar"] {
    visibility: visible !important;
    display: flex !important;
    position: fixed !important;
    z-index: 999999 !important;
    background: #FF5200 !important;
    border-radius: 0 8px 8px 0 !important;
    box-shadow: 0 4px 12px rgba(255, 82, 0, 0.3) !important;
    top: 15px !important;
    left: 0px !important;
    width: 40px !important;
    height: 40px !important;
    justify-content: center !important;
    align-items: center !important;
    transition: background-color 0.2s ease !important;
    pointer-events: auto !important;
    cursor: pointer !important;
}
[data-testid="collapsedControl"]:hover,
[data-testid="stSidebarCollapseButton"]:hover,
button[aria-label="Expand sidebar"]:hover,
button[title="Expand sidebar"]:hover {
    background: #E04800 !important;
}
[data-testid="collapsedControl"] button,
[data-testid="stSidebarCollapseButton"] button {
    color: #FFFFFF !important;
    background: transparent !important;
    border: none !important;
    margin: 0 !important;
    padding: 0 !important;
    width: 100% !important;
    height: 100% !important;
    display: flex !important;
    justify-content: center !important;
    align-items: center !important;
    pointer-events: auto !important;
    cursor: pointer !important;
}
[data-testid="collapsedControl"] svg,
[data-testid="stSidebarCollapseButton"] svg,
button[aria-label="Expand sidebar"] svg,
button[title="Expand sidebar"] svg {
    fill: #FFFFFF !important;
    color: #FFFFFF !important;
    width: 22px !important;
    height: 22px !important;
}
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

/* ═══════ SIDEBAR NAV LABELS ═══════ */
.sb-section {
    font-size: 0.62rem;
    font-weight: 700;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: #94A3B8;
    padding: 14px 20px 5px;
    display: block;
}
.sb-divider {
    height: 1px;
    background: #F1F5F9;
    margin: 10px 0;
}

/* ═══════ SIDEBAR RADIO (NAV ITEMS) ═══════ */
[data-testid="stSidebar"] div[role="radiogroup"] {
    gap: 1px !important;
    display: flex !important;
    flex-direction: column !important;
    padding: 0 10px !important;
}
[data-testid="stSidebar"] div[role="radiogroup"] > label {
    padding: 9px 12px !important;
    border-radius: 7px !important;
    background: transparent !important;
    border: none !important;
    transition: background 0.12s ease !important;
    cursor: pointer !important;
}
[data-testid="stSidebar"] div[role="radiogroup"] > label p {
    font-size: 0.84rem !important;
    font-weight: 500 !important;
    color: #475569 !important;
    margin: 0 !important;
    line-height: 1.4 !important;
}
[data-testid="stSidebar"] div[role="radiogroup"] > label:hover {
    background: #F8FAFC !important;
}
[data-testid="stSidebar"] div[role="radiogroup"] > label:hover p {
    color: #1E293B !important;
}
[data-testid="stSidebar"] div[role="radiogroup"] > label:has(input:checked) {
    background: #FFF3EE !important;
}
[data-testid="stSidebar"] div[role="radiogroup"] > label:has(input:checked) p {
    font-weight: 600 !important;
    color: #FF5200 !important;
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

/* ═══════ PAGE HEADER ═══════ */
.pg-header {
    margin-bottom: 28px;
    padding-bottom: 20px;
    border-bottom: 1px solid #E2E8F0;
    display: flex;
    justify-content: space-between;
    align-items: flex-end;
}
.pg-eyebrow {
    font-size: 0.63rem;
    font-weight: 700;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: #94A3B8;
    margin: 0 0 4px;
}
.pg-title {
    font-size: 1.45rem;
    font-weight: 800;
    color: #0A1F44;
    margin: 0;
    letter-spacing: -0.025em;
    line-height: 1.25;
}
.pg-subtitle {
    font-size: 0.82rem;
    color: #64748B;
    margin: 5px 0 0;
    font-weight: 500;
}
.pg-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: #F0FDF4;
    color: #15803D;
    border: 1px solid #BBF7D0;
    padding: 5px 12px;
    border-radius: 20px;
    font-size: 0.7rem;
    font-weight: 700;
    letter-spacing: 0.04em;
    white-space: nowrap;
}
.pg-badge-dot {
    width: 6px;
    height: 6px;
    background: #22C55E;
    border-radius: 50%;
    display: inline-block;
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

/* ═══════ TABS ═══════ */
.stTabs [data-baseweb="tab-list"] {
    background: #F8FAFC !important;
    border: 1px solid #E2E8F0 !important;
    border-radius: 10px !important;
    padding: 4px !important;
    gap: 4px !important;
    box-shadow: none !important;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 7px !important;
    padding: 8px 20px !important;
    font-size: 0.84rem !important;
    font-weight: 500 !important;
    color: #64748B !important;
    background: transparent !important;
    border: none !important;
    transition: all 0.12s ease !important;
}
.stTabs [data-baseweb="tab"]:hover {
    color: #1E293B !important;
    background: rgba(0,0,0,0.03) !important;
}
.stTabs [aria-selected="true"] {
    background: #FFFFFF !important;
    color: #0A1F44 !important;
    font-weight: 600 !important;
    box-shadow: 0 1px 4px rgba(0,0,0,0.08) !important;
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
    width: 22px; height: 22px;
    background: #FFF3EE;
    border-radius: 6px;
    display: flex; align-items: center; justify-content: center;
    font-size: 0.68rem; font-weight: 800; color: #FF5200;
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

/* ═══════ DATAFRAME ═══════ */
[data-testid="stDataFrame"] { border-radius: 10px !important; overflow: hidden !important; }
</style>""", unsafe_allow_html=True)

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

COMPANY_LABEL = "Tổng quan Toàn Hệ thống"

# ── SIDEBAR ─────────────────────────────────────────────────────────────────
with st.sidebar:
    if st.session_state.get("is_admin", False):
        if st.button("⬅️ Trở về Admin Panel", use_container_width=True):
            st.session_state.preview_mode = False
            st.rerun()
        st.markdown('<div class="sb-divider"></div>', unsafe_allow_html=True)

    # [Đã ẩn Avatar và Nút Đăng xuất do đang dùng chế độ Bypass]

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
    main_nav_opts = [COMPANY_LABEL] + [available[g]['label'] for g in group_opts]
    sel_dashboard = st.radio("Nav", main_nav_opts, label_visibility="collapsed", key="main_nav")

    st.markdown('<div class="sb-divider"></div>', unsafe_allow_html=True)

    is_company = (sel_dashboard == COMPANY_LABEL)

    # Initialize scope variables
    sel_group   = None
    sel_nav     = None
    df_filtered = None
    n_before    = 0

    if is_company:
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

        # Sub-navigation
        st.markdown('<span class="sb-section">Góc nhìn phân tích</span>', unsafe_allow_html=True)
        SUB_NAV = [
            "A. Trạng thái Tổ chức",
            "B. Nhóm gặp vấn đề",
            "C. Vấn đề nghiêm trọng",
            "D. Nguyên nhân gốc rễ",
            "E. Rủi ro & Hệ lụy",
            "F. Ưu tiên hành động",
            "G. Đo lường Impact",
        ]
        sel_nav = st.radio("SubNav", SUB_NAV, label_visibility="collapsed", key="sub_nav")

        st.markdown('<div class="sb-divider"></div>', unsafe_allow_html=True)

        # Filters
        st.markdown('<span class="sb-section">Bộ lọc</span>', unsafe_allow_html=True)

        # Load raw data (for building filter options)
        df_raw, n_before = load_group(sel_group)

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

# ── MAIN CONTENT ─────────────────────────────────────────────────────────────
if is_company:
    st.markdown("""
    <div class="pg-header">
        <div>
            <p class="pg-eyebrow">GIAO HANG NHANH · EES 2026</p>
            <h1 class="pg-title">Tổng quan Toàn Hệ thống</h1>
            <p class="pg-subtitle">Khảo sát Mức độ Gắn kết Nhân viên · Quy mô: 23,000+ nhân sự</p>
        </div>
        <span class="pg-badge">
            <span class="pg-badge-dot"></span>Live · Cập nhật hôm nay
        </span>
    </div>
    """, unsafe_allow_html=True)

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
        if sel_nav == "A. Trạng thái Tổ chức":
            view_a_current_state.render(df_filtered, cfg)
        elif sel_nav == "B. Nhóm gặp vấn đề":
            view_b_problem_groups.render(df_filtered, cfg)
        elif sel_nav == "C. Vấn đề nghiêm trọng":
            view_c_key_issues.render(df_filtered, cfg)
        elif sel_nav == "D. Nguyên nhân gốc rễ":
            view_d_root_cause.render(df_filtered, cfg, sel_group)
            st.markdown("---")
            hris_linkage.render(df_filtered, cfg, sel_group)
        elif sel_nav == "E. Rủi ro & Hệ lụy":
            view_e_impact_risk.render(df_filtered, cfg)
        elif sel_nav == "F. Ưu tiên hành động":
            view_f_action_priority.render(df_filtered, cfg)
        elif sel_nav == "G. Đo lường Impact":
            view_g_kpi_impact.render(df_filtered, cfg)
        else:
            st.info("Chọn một góc nhìn từ sidebar bên trái.")
    except Exception as e:
        st.error(f"Lỗi khi tải phân tích: {e}")
        import traceback
        st.code(traceback.format_exc())
