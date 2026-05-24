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

st.set_page_config(page_title="GHN EES 2026", layout="wide", initial_sidebar_state="collapsed")

# Import loaders and views
from utils.data_loader import load_group, load_all_available
from config.groups import get_available_groups
from views import (
    company_overview, group_detail, org_drilldown,
    hris_linkage, deep_dive, nlp_analysis,
    early_warning, action_priorities
)

# ── Custom CSS ──
st.markdown("""
<style>
/* Adjust main container */
.block-container {
    padding-top: 3.5rem;
    padding-left: 3rem;
    padding-right: 3rem;
    max-width: 100%;
}

/* Premium Modern White Background */
.stApp {
    background-color: #F4F7FE;
}

/* Global Font */
html, body, [data-testid="stAppViewContainer"], [data-testid="stSidebar"], .stApp {
    font-family: 'Inter', 'Outfit', 'Segoe UI', system-ui, sans-serif !important;
}

/* Premium Sidebar Base - Clean White */
[data-testid="stSidebar"] {
    background: #FFFFFF !important;
    border-right: 1px solid #E2E8F0 !important;
}

/* Targeted Sidebar Text Elements */
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p,
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h1,
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h2,
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h3,
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h4,
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] span {
    color: #4A5568 !important;
}

/* Premium Sidebar Navigation Menu */
[data-testid="stSidebar"] div[role="radiogroup"] {
    gap: 8px !important;
    display: flex !important;
    flex-direction: column !important;
    margin-top: 10px !important;
}
[data-testid="stSidebar"] div[role="radiogroup"] > label {
    padding: 12px 16px !important;
    border-radius: 12px !important;
    background-color: transparent !important;
    border: none !important;
    transition: all 0.2s ease-in-out !important;
    cursor: pointer !important;
    margin-bottom: 4px !important;
    display: flex !important;
    align-items: center !important;
    color: #718096 !important;
    position: relative !important;
}
[data-testid="stSidebar"] div[role="radiogroup"] > label p {
    font-size: 0.95rem !important;
    line-height: 1.4 !important;
    font-weight: 500 !important;
    margin: 0 !important;
    color: #718096 !important;
}
[data-testid="stSidebar"] div[role="radiogroup"] > label:hover {
    background-color: #F7FAFC !important;
    color: #2D3748 !important;
}
[data-testid="stSidebar"] div[role="radiogroup"] > label:hover p {
    color: #2D3748 !important;
}
[data-testid="stSidebar"] div[role="radiogroup"] > label:has(input:checked) {
    background-color: rgba(67, 24, 255, 0.08) !important;
    color: #4318FF !important;
}
[data-testid="stSidebar"] div[role="radiogroup"] > label:has(input:checked) p {
    font-weight: 700 !important;
    color: #4318FF !important;
}
/* Hide the actual radio circle */
[data-testid="stSidebar"] div[role="radiogroup"] > label > div:first-child {
    display: none !important;
}

/* ══════════════════════════════════════════════════════════════
   PROFESSIONAL AI INSIGHT CONTAINER (Clean & Minimalist)
   ══════════════════════════════════════════════════════════════ */
.ai-insight-container {
    background: #FFFFFF !important;
    border: 1px solid rgba(0, 0, 0, 0.03) !important;
    border-radius: 20px !important;
    padding: 24px 24px !important;
    margin-bottom: 24px !important;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.02) !important;
    font-family: 'Inter', sans-serif !important;
    position: relative;
    overflow: hidden;
}
.ai-insight-container::after {
    content: '';
    position: absolute;
    top: 0; left: 0; width: 4px; height: 100%;
    background: linear-gradient(180deg, #4318FF 0%, #05CD99 100%);
    border-radius: 20px 0 0 20px;
}
.ai-header {
    display: flex !important;
    align-items: center !important;
    gap: 10px !important;
    margin-bottom: 12px !important;
}
.ai-icon {
    font-size: 1.2rem !important;
    filter: drop-shadow(0 1px 2px rgba(255,82,0,0.2)) !important;
}
.ai-title {
    font-family: 'JetBrains Mono', 'Courier New', monospace !important;
    font-size: 0.85rem !important;
    color: #475569 !important;
    text-transform: uppercase !important;
    letter-spacing: 1.2px !important;
    font-weight: 700 !important;
    margin: 0 !important;
}
.ai-badge {
    background: rgba(67, 24, 255, 0.05) !important;
    color: #4318FF !important;
    padding: 4px 12px !important;
    border-radius: 8px !important;
    font-size: 0.7rem !important;
    font-weight: 700 !important;
    margin-left: auto !important;
    letter-spacing: 0.5px !important;
    text-transform: uppercase !important;
    border: none !important;
}
.ai-content {
    font-size: 0.95rem !important;
    line-height: 1.6 !important;
    color: #A3AED0 !important;
}
.ai-content strong {
    color: #2B3674 !important;
    font-weight: 700 !important;
}
.ai-highlight {
    color: #05CD99 !important;
    font-weight: 700 !important;
    background: rgba(5, 205, 153, 0.06) !important;
    padding: 1px 6px !important;
    border-radius: 4px !important;
}
.ai-warning {
    color: #EE5D50 !important;
    font-weight: 700 !important;
    background: rgba(238, 93, 80, 0.06) !important;
    padding: 1px 6px !important;
    border-radius: 4px !important;
}


/* Premium Header Styling */
.ghn-header-container {
    background: rgba(255, 255, 255, 0.45) !important;
    backdrop-filter: blur(30px) !important;
    -webkit-backdrop-filter: blur(30px) !important;
    padding: 24px 36px;
    border-radius: 24px;
    box-shadow: 0 10px 40px rgba(10,31,68,0.02) !important;
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 36px;
    border: 1px solid rgba(255, 255, 255, 0.6) !important;
    transition: all 0.3s ease;
}
.ghn-header-container:hover {
    box-shadow: 0 16px 48px rgba(10, 31, 68, 0.04) !important;
    background: rgba(255, 255, 255, 0.55) !important;
}
.ghn-logo-box {
    background: linear-gradient(135deg, #FF5200 0%, #E64A00 100%) !important;
    color: white !important;
    font-weight: 900 !important;
    padding: 14px 22px !important;
    border-radius: 16px !important;
    font-size: 1.4rem !important;
    margin-right: 24px;
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: 0 8px 24px rgba(255,82,0,0.22) !important;
    transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1) !important;
    letter-spacing: -0.03em !important;
}
.ghn-logo-box:hover {
    transform: translateY(-2px) scale(1.03) !important;
    box-shadow: 0 12px 28px rgba(255,82,0,0.35) !important;
}
.ghn-title {
    font-size: 1.5rem;
    font-weight: 900;
    color: #0A1F44;
    margin: 0;
    line-height: 1.25;
    letter-spacing: -0.025em;
}
.ghn-subtitle {
    font-size: 0.88rem;
    color: #64748B;
    margin: 0;
    margin-top: 6px;
    font-weight: 500;
}
.ghn-badges {
    display: flex;
    gap: 12px;
    align-items: center;
}
.badge-live {
    background: rgba(16, 185, 129, 0.08) !important;
    color: #059669 !important;
    padding: 6px 14px;
    border-radius: 20px;
    font-size: 0.75rem;
    font-weight: 700;
    display: flex;
    align-items: center;
    gap: 8px;
    border: 1px solid rgba(16,185,129,0.15) !important;
}
.badge-internal {
    background: rgba(245, 158, 11, 0.08) !important;
    color: #D97706 !important;
    padding: 6px 14px;
    border-radius: 20px;
    font-size: 0.75rem;
    font-weight: 700;
    border: 1px solid rgba(245,158,11,0.15) !important;
}
@keyframes pulseGreen {
    0% { transform: scale(0.92); box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.6); }
    70% { transform: scale(1); box-shadow: 0 0 0 5px rgba(16, 185, 129, 0); }
    100% { transform: scale(0.92); box-shadow: 0 0 0 0 rgba(16, 185, 129, 0); }
}
.dot-pulse {
    display: inline-block;
    width: 7px;
    height: 7px;
    background-color: #10B981;
    border-radius: 50%;
    animation: pulseGreen 2s infinite;
}

/* Animations */
@keyframes fadeInUp {
    from {
        opacity: 0;
        transform: translateY(12px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}
.stApp {
    animation: fadeInUp 0.5s ease-out forwards;
}
.hero-card, .custom-metric-card, .ai-insight-container {
    animation: fadeInUp 0.6s ease-out forwards;
}


/* Glassmorphism Metric Cards & Premium Cards */
.custom-metric-card, .premium-kpi-card {
    background: rgba(255, 255, 255, 0.65);
    backdrop-filter: blur(24px);
    -webkit-backdrop-filter: blur(24px);
    border-radius: 24px;
    padding: 24px 28px;
    box-shadow: 0 8px 30px rgba(10,31,68,0.015);
    border: 1px solid rgba(255, 255, 255, 0.45);
    transition: all 0.35s cubic-bezier(0.25, 0.8, 0.25, 1);
    display: flex;
    flex-direction: column;
    height: 100%;
    position: relative;
    overflow: hidden;
}
.custom-metric-card::before, .premium-kpi-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; width: 100%; height: 4px;
    background: linear-gradient(90deg, #0A1F44 0%, #FF5200 100%);
    opacity: 0;
    transition: opacity 0.3s ease;
}
.custom-metric-card:hover, .premium-kpi-card:hover {
    transform: translateY(-6px);
    box-shadow: 0 20px 40px rgba(10, 31, 68, 0.06);
    border-color: rgba(255, 82, 0, 0.25);
    background: rgba(255, 255, 255, 0.8);
}
.custom-metric-card:hover::before, .premium-kpi-card:hover::before {
    opacity: 1;
}

.metric-title {
    font-size: 0.85rem;
    color: #64748B;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin-bottom: 12px;
}
.metric-value-row {
    display: flex;
    align-items: baseline;
    gap: 8px;
    margin-bottom: 12px;
}
.metric-value {
    font-size: 2.4rem;
    font-weight: 900;
    color: #0A1F44;
    line-height: 1;
    letter-spacing: -0.03em;
}
.metric-unit {
    font-size: 1.05rem;
    color: #94A3B8;
    font-weight: 600;
}
.metric-delta {
    display: inline-flex;
    align-items: center;
    gap: 4px;
    font-size: 0.78rem;
    font-weight: 700;
    padding: 5px 12px;
    border-radius: 8px;
    width: fit-content;
}
.delta-positive { background: #ECFDF5; color: #059669; border: 1px solid rgba(16,185,129,0.18); }
.delta-negative { background: #FEF2F2; color: #DC2626; border: 1px solid rgba(220,38,38,0.18); }
.delta-neutral { background: #F8FAFC; color: #64748B; border: 1px solid rgba(100,116,139,0.18); }

/* Premium Dark Hero Card */
.hero-card {
    background: linear-gradient(135deg, #0A1F44 0%, #061530 100%);
    color: #F8FAFC !important;
    border-radius: 28px;
    padding: 36px 42px;
    box-shadow: 0 20px 50px rgba(10, 31, 68, 0.2);
    border: 1px solid rgba(255, 255, 255, 0.08);
    margin-bottom: 36px;
    position: relative;
    overflow: hidden;
}
.hero-card::before {
    content: '';
    position: absolute;
    top: -40%; right: -15%;
    width: 400px; height: 400px;
    background: radial-gradient(circle, rgba(255, 82, 0, 0.2) 0%, transparent 70%);
    filter: blur(45px);
    pointer-events: none;
}
.hero-card::after {
    content: '';
    position: absolute;
    bottom: -30%; left: -10%;
    width: 300px; height: 300px;
    background: radial-gradient(circle, rgba(0, 111, 173, 0.15) 0%, transparent 70%);
    filter: blur(40px);
    pointer-events: none;
}
.hero-title {
    font-size: 1.65rem;
    font-weight: 800;
    color: #FFFFFF !important;
    margin: 0 0 8px 0;
    display: flex;
    align-items: center;
    gap: 14px;
}
.hero-subtitle {
    font-size: 1rem;
    color: #94A3B8 !important;
    margin: 0 0 32px 0;
    font-weight: 500;
}
.hero-metrics {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
    gap: 24px;
    position: relative;
    z-index: 10;
}
.hero-metric-box {
    display: flex;
    flex-direction: column;
    gap: 8px;
    background: rgba(255, 255, 255, 0.03);
    padding: 22px;
    border-radius: 20px;
    border: 1px solid rgba(255, 255, 255, 0.06);
    transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
}
.hero-metric-box:hover {
    background: rgba(255, 255, 255, 0.07);
    border-color: rgba(255, 82, 0, 0.35);
    transform: translateY(-3px);
    box-shadow: 0 10px 24px rgba(255, 82, 0, 0.12);
}
.hero-metric-label {
    font-size: 0.82rem;
    color: #94A3B8 !important;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.08em;
}
.hero-metric-value {
    font-size: 2.8rem;
    font-weight: 900;
    color: #FFFFFF !important;
    line-height: 1;
    letter-spacing: -0.03em;
}

/* Streamlit Inputs override */
div[data-baseweb="select"] > div {
    border-radius: 14px !important;
    border-color: #E2E8F0 !important;
    background-color: white !important;
    box-shadow: 0 2px 10px rgba(10,31,68,0.02) !important;
    transition: all 0.2s !important;
}
div[data-baseweb="select"] > div:hover {
    border-color: #CBD5E1 !important;
}

/* Elegant Left-Accented Insight Squares - Modern White UI */
.insight-square {
    background: #FFFFFF;
    border-radius: 20px;
    padding: 26px;
    height: 100%;
    border: 1px solid rgba(0, 0, 0, 0.03);
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.02);
    transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
    position: relative;
    overflow: hidden;
}
.insight-square::after {
    content: '';
    position: absolute;
    top: 0; left: 0; width: 4px; height: 100%;
    border-radius: 20px 0 0 20px;
}
.insight-square-total::after { background: #4318FF; }
.insight-square-top::after { background: #05CD99; }
.insight-square-warning::after { background: #FFB547; }
.insight-square-recommend::after { background: #EE5D50; }

.insight-square:hover {
    transform: translateY(-4px);
    box-shadow: 0 16px 36px rgba(0, 0, 0, 0.05);
}
.insight-header {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 16px;
    padding-bottom: 12px;
    border-bottom: 1px solid rgba(0, 0, 0, 0.03);
}
.insight-icon {
    width: 38px;
    height: 38px;
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.2rem;
    background: rgba(67, 24, 255, 0.05);
    color: #4318FF;
}
.insight-title {
    font-weight: 700;
    color: #2B3674;
    font-size: 1rem;
    margin: 0;
}
.insight-body {
    font-size: 0.92rem;
    color: #A3AED0;
    line-height: 1.65;
}
.insight-highlight {
    font-weight: 700;
    color: #4318FF;
}

/* Custom Segmented Tabs */
.stTabs [data-baseweb="tab-list"] {
    gap: 10px;
    background-color: #FFFFFF;
    padding: 8px;
    border-radius: 16px;
    border: 1px solid rgba(0,0,0,0.03) !important;
    box-shadow: 0 4px 20px rgba(0,0,0,0.02);
}
.stTabs [data-baseweb="tab"] {
    height: auto !important;
    padding: 12px 28px !important;
    background-color: transparent !important;
    border-radius: 12px !important;
    border: none !important;
    color: #A3AED0 !important;
    font-weight: 600 !important;
    transition: all 0.28s cubic-bezier(0.4, 0, 0.2, 1) !important;
}
.stTabs [data-baseweb="tab"]:hover {
    color: #2B3674 !important;
    background-color: rgba(67, 24, 255, 0.03) !important;
}
.stTabs [aria-selected="true"] {
    background-color: #4318FF !important;
    color: #FFFFFF !important;
    box-shadow: 0 6px 16px rgba(67, 24, 255, 0.2) !important;
    font-weight: 700 !important;
}
.stTabs [data-baseweb="tab-highlight-bar"] {
    display: none !important;
}

/* Premium Segmented Controls for st.pills */
div[data-testid="stBaseButton-pill"] {
    background-color: #FFFFFF !important;
    color: #A3AED0 !important;
    border: 1px solid rgba(0, 0, 0, 0.05) !important;
    padding: 8px 20px !important;
    border-radius: 16px !important;
    font-weight: 600 !important;
    font-size: 0.9rem !important;
    transition: all 0.22s ease-in-out !important;
    box-shadow: 0 2px 10px rgba(0,0,0,0.01) !important;
}
div[data-testid="stBaseButton-pill"]:hover {
    color: #4318FF !important;
    background-color: rgba(67, 24, 255, 0.03) !important;
    border-color: rgba(67, 24, 255, 0.2) !important;
    transform: translateY(-1px) !important;
}
div[data-testid="stBaseButton-pill"][aria-selected="true"] {
    background-color: #4318FF !important;
    color: #FFFFFF !important;
    border-color: #4318FF !important;
    box-shadow: 0 8px 20px rgba(67, 24, 255, 0.2) !important;
    font-weight: 700 !important;
}

/* Styled Framework Callouts */
.framework-callout {
    background: linear-gradient(135deg, rgba(10,31,68,0.02) 0%, rgba(255,82,0,0.01) 100%);
    border: 1px solid rgba(10,31,68,0.05);
    border-left: 5px solid #006FAD;
    border-radius: 16px;
    padding: 20px 24px;
    margin-bottom: 24px;
}
.framework-callout-title {
    font-weight: 800;
    font-size: 1.05rem;
    color: #0A1F44;
    margin-top: 0;
    margin-bottom: 8px;
    display: flex;
    align-items: center;
    gap: 8px;
}

/* Beautiful Interactive Attrition Simulator Display */
.sim-gauge-container {
    background: radial-gradient(circle at 100% 0%, rgba(255, 82, 0, 0.05) 0%, transparent 60%), rgba(255,255,255,0.7);
    border: 1px solid rgba(255, 255, 255, 0.6);
    border-radius: 24px;
    padding: 32px;
    text-align: center;
    box-shadow: 0 10px 30px rgba(0,0,0,0.01);
}
.sim-risk-value {
    font-size: 4rem;
    font-weight: 900;
    line-height: 1;
    letter-spacing: -0.04em;
    margin: 16px 0;
    transition: all 0.3s ease;
}
.sim-risk-meter {
    height: 10px;
    width: 100%;
    background-color: #E2E8F0;
    border-radius: 5px;
    overflow: hidden;
    margin-top: 12px;
    margin-bottom: 12px;
}
.sim-risk-bar {
    height: 100%;
    border-radius: 5px;
    transition: width 0.4s ease, background-color 0.4s ease;
}
</style>
""", unsafe_allow_html=True)

# ── Render Header ──
st.markdown("""<div style="background: linear-gradient(135deg, #ffffff 0%, #fcfdfd 100%); border-radius: 20px; border: 1px solid rgba(0,0,0,0.04); box-shadow: 0 10px 30px rgba(0,0,0,0.02); display: flex; align-items: center; justify-content: space-between; padding: 20px 28px; margin-bottom: 32px; transition: transform 0.3s ease, box-shadow 0.3s ease;" onmouseover="this.style.transform='translateY(-2px)'; this.style.boxShadow='0 15px 35px rgba(0,0,0,0.04)';" onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='0 10px 30px rgba(0,0,0,0.02)';">
<div style="display: flex; align-items: center; gap: 24px;">
    <!-- Minimalist Premium Logo -->
    <div style="display: flex; align-items: center; justify-content: center; padding-right: 24px; border-right: 2px solid #F1F5F9;">
        <img src="https://res.cloudinary.com/dd7gti2kn/image/upload/v1772778161/LOGO%20GHN/LOGO_CHUAN_hviaug.png" style="height: 48px; width: auto; object-fit: contain; drop-shadow: 0 4px 10px rgba(0,0,0,0.05);">
    </div>
    <!-- Elegant Typography -->
    <div style="display: flex; flex-direction: column; gap: 6px;">
        <div style="display: flex; align-items: center; gap: 12px;">
            <h1 style="margin: 0; font-size: 1.3rem; font-weight: 900; color: #0A1F44; letter-spacing: -0.01em; line-height: 1;">EES 2026 DATA ANALYSIS</h1>
            <span style="background: rgba(67, 24, 255, 0.06); color: #4318FF; font-size: 0.7rem; padding: 3px 10px; border-radius: 8px; font-weight: 800; letter-spacing: 0.5px;">NỘI BỘ</span>
        </div>
        <p style="margin: 0; font-size: 0.85rem; color: #64748B; font-weight: 500;">Khảo sát Mức độ Gắn kết Nhân viên (EES) • Q1/2026 • Quy mô: 23,000+ nhân sự</p>
    </div>
</div>
<!-- Right Side Badges -->
<div style="display: flex; align-items: center; gap: 16px;">
    <div style="display: flex; align-items: center; gap: 6px; background: #F8FAFC; padding: 6px 14px; border-radius: 12px; border: 1px solid rgba(0,0,0,0.03);">
        <span style="width: 8px; height: 8px; background: #05CD99; border-radius: 50%; box-shadow: 0 0 0 3px rgba(5,205,153,0.2);"></span>
        <span style="font-size: 0.8rem; font-weight: 800; color: #334155; letter-spacing: 0.5px;">LIVE</span>
    </div>
    <div style="font-size: 0.8rem; font-weight: 600; color: #94A3B8; background: #F1F5F9; padding: 6px 14px; border-radius: 12px;">
        Cập nhật: Hôm nay
    </div>
</div>
</div>""", unsafe_allow_html=True)

# ── Navigation & Global Filters ──
available = get_available_groups()
group_opts = list(available.keys())

if 'global_tenure' not in st.session_state:
    st.session_state.global_tenure = 'Tất cả'

tenure_opts = [
    'Tất cả', 'Dưới 1 tháng', 'Trên 1 đến 3 tháng', 'Trên 3 đến 6 tháng', 
    'Trên 6 đến 9 tháng', 'Trên 9 đến 12 tháng', 'Trên 1 đến 2 năm', 
    'Trên 2 đến 3 năm', 'Trên 3 đến 5 năm', 'Trên 5 năm', 'Chưa xác định'
]

def apply_global_filters(df):
    if st.session_state.global_tenure != 'Tất cả':
        if 'Q5' in df.columns:
            return df[df['Q5'] == st.session_state.global_tenure]
    return df

def get_sidebar_label(item_label):
    if "Tổng quan" in item_label:
        return "Tổng quan Toàn Hệ thống"
    elif "1A" in item_label:
        return "Nhóm 1A — Shipper / NVPTTT"
    elif "1B" in item_label:
        return "Nhóm 1B — Tài xế GXT/TXXT"
    return item_label

COMPANY_LABEL = "🌐 Tổng quan Toàn Hệ thống"
dashboard_options = [COMPANY_LABEL] + [get_sidebar_label(available[g]['label']) for g in group_opts]

st.markdown("""<div style="background: #FFFFFF; border-radius: 20px; border: none; padding: 20px 24px 20px 24px; box-shadow: 0 4px 20px rgba(0,0,0,0.02); margin-bottom: 24px;">
<h3 style="margin-top: 0; color: #2B3674; font-size: 0.95rem; font-weight: 800; letter-spacing: 0.05em; text-transform: uppercase; margin-bottom: 16px;">🎯 Tùy chỉnh Phân tích</h3>
</div>""", unsafe_allow_html=True)
sel_col1, sel_col2, sel_col3, sel_col4, sel_col5 = st.columns(5)
with sel_col1:
    sel_dashboard = st.selectbox("📌 Phân khúc Báo cáo", dashboard_options)

# ── Route to Main Dashboard vs Group Dashboards ──
if sel_dashboard == COMPANY_LABEL:
    # 1. COMPANY DASHBOARD
    with sel_col2:
        sel_tenure = st.selectbox("⏱️ Lọc Thâm niên (Global)", tenure_opts, index=tenure_opts.index(st.session_state.global_tenure))
        st.session_state.global_tenure = sel_tenure

    st.write("") # Spacer

    st.markdown('<h2 style="font-size:1.5rem; color:#0A1F44; font-weight:800; margin-bottom:1rem;">Tổng quan Toàn Công ty</h2>', unsafe_allow_html=True)
    try:
        all_data = load_all_available()
        # Apply global filters to all dataframes in the dictionary
        filtered_all_data = {k: (apply_global_filters(v[0]), v[1]) for k, v in all_data.items()}
        company_overview.render(filtered_all_data, available)
    except Exception as e:
        st.error(f"Lỗi khi tải view Tổng quan: {e}")
        import traceback
        st.code(traceback.format_exc())

else:
    # 2. GROUP DASHBOARDS
    # Find which group was selected
    sel_group = None
    for g in group_opts:
        if g in sel_dashboard:
            sel_group = g
            break
            
    df, n_before = load_group(sel_group)
    cfg = available[sel_group]
    
    with sel_col2:
        sel_tenure = st.selectbox("⏱️ Thâm niên (Global)", tenure_opts, index=tenure_opts.index(st.session_state.global_tenure))
        st.session_state.global_tenure = sel_tenure
        
    df_filtered_tenure = apply_global_filters(df)
    
    with sel_col3:
        div_opts = ['Tất cả Khối'] + sorted(df_filtered_tenure['division'].dropna().unique().tolist()) if 'division' in df_filtered_tenure.columns else ['Tất cả Khối']
        sel_div = st.selectbox("🏢 Khối", div_opts)
    with sel_col4:
        dept_opts = ['Tất cả Phòng ban']
        if sel_div != 'Tất cả Khối':
            dept_opts += sorted(df_filtered_tenure[df_filtered_tenure['division'] == sel_div]['department'].dropna().unique().tolist())
        elif 'department' in df_filtered_tenure.columns:
            dept_opts += sorted(df_filtered_tenure['department'].dropna().unique().tolist())
        sel_dept = st.selectbox("🏘️ Phòng ban", dept_opts)
    with sel_col5:
        sec_opts = ['Tất cả Section']
        if sel_dept != 'Tất cả Phòng ban':
            sec_opts += sorted(df_filtered_tenure[df_filtered_tenure['department'] == sel_dept]['section'].dropna().unique().tolist())
        elif 'section' in df_filtered_tenure.columns:
            sec_opts += sorted(df_filtered_tenure['section'].dropna().unique().tolist())
        sel_sec = st.selectbox("📍 Section", sec_opts)

    # Apply filters
    df_filtered = df_filtered_tenure.copy()
    if sel_div != 'Tất cả Khối': df_filtered = df_filtered[df_filtered['division'] == sel_div]
    if sel_dept != 'Tất cả Phòng ban': df_filtered = df_filtered[df_filtered['department'] == sel_dept]
    if sel_sec != 'Tất cả Section': df_filtered = df_filtered[df_filtered['section'] == sel_sec]

    st.markdown("""
    <div style="margin-top: 16px; margin-bottom: 12px; display: flex; align-items: center; gap: 8px;">
        <span style="font-size: 0.72rem; font-weight: 800; color: #FF5200; letter-spacing: 0.1em; text-transform: uppercase;">📊 CHỌN GÓC NHÌN PHÂN TÍCH</span>
    </div>
    """, unsafe_allow_html=True)

    # Group Sub-Navigation
    NAV_OPTIONS = [
        "🏢 Chi tiết Nhóm",
        "👥 Phân tích Tổ chức",
        "💰 HRIS (Thu nhập)",
        "🔍 Deep Dive",
        "💬 Câu hỏi Mở (NLP)",
        "🚨 Cảnh báo Sớm",
        "⚡ Ma trận Ưu tiên"
    ]
    sel_nav = st.pills("Góc nhìn Phân tích", NAV_OPTIONS, default="🏢 Chi tiết Nhóm", label_visibility="collapsed")
    st.divider()
    
    # Route to Views
    try:
        if sel_nav == "🏢 Chi tiết Nhóm":
            group_detail.render(df_filtered, cfg)
        elif sel_nav == "👥 Phân tích Tổ chức":
            org_drilldown.render(df_filtered, cfg)
        elif sel_nav == "💰 HRIS (Thu nhập)":
            hris_linkage.render(df_filtered, cfg, sel_group)
        elif sel_nav == "🔍 Deep Dive":
            deep_dive.render(df_filtered, cfg, sel_group)
        elif sel_nav == "💬 Câu hỏi Mở (NLP)":
            nlp_analysis.render(df_filtered, cfg)
        elif sel_nav == "🚨 Cảnh báo Sớm":
            early_warning.render(df_filtered, cfg)
        elif sel_nav == "⚡ Ma trận Ưu tiên":
            action_priorities.render(df_filtered, cfg)
        else:
            st.info("Vui lòng chọn một chức năng từ thanh menu bên trên.")
    except Exception as e:
        st.error(f"Lỗi khi tải phân tích nhóm: {e}")
        import traceback
        st.code(traceback.format_exc())
