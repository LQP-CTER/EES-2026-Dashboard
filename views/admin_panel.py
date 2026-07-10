import streamlit as st
import json
import os
import time
from datetime import datetime, timedelta
import pandas as pd

APP_STATE_FILE   = os.path.join("config", "app_state.json")
SESSIONS_FILE    = os.path.join("config", "active_sessions.json")
ACCESS_LOGS_FILE = os.path.join("config", "access_logs.csv")

ONLINE_THRESHOLD_SECONDS = 10 * 60


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

def load_active_sessions() -> dict:
    if os.path.exists(SESSIONS_FILE):
        try:
            with open(SESSIONS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def load_access_logs() -> pd.DataFrame:
    if not os.path.exists(ACCESS_LOGS_FILE):
        return pd.DataFrame(columns=["timestamp", "email", "name", "role", "login_method"])
    try:
        df = pd.read_csv(ACCESS_LOGS_FILE, encoding="utf-8")
        if "timestamp" in df.columns:
            df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
            df = df.sort_values("timestamp", ascending=False)
        return df
    except Exception:
        return pd.DataFrame(columns=["timestamp", "email", "name", "role", "login_method"])

def _role_badge_html(role: str) -> str:
    r = str(role).strip().upper()
    if r == "ADMIN":
        return (
            '<span style="background:linear-gradient(135deg,#DC2626,#EF4444);color:white;'
            'font-size:0.58rem;font-weight:800;padding:4px 10px;border-radius:6px;'
            'letter-spacing:0.07em;text-transform:uppercase;'
            'box-shadow:0 4px 12px rgba(220,38,38,0.25);">ADMIN</span>'
        )
    return (
        '<span style="background:linear-gradient(135deg,#1E40AF,#3B82F6);color:white;'
        'font-size:0.58rem;font-weight:800;padding:4px 10px;border-radius:6px;'
        'letter-spacing:0.07em;text-transform:uppercase;'
        'box-shadow:0 4px 12px rgba(30,64,175,0.25);">USER</span>'
    )

def _avatar_html(name: str, picture: str = "", size: int = 42) -> str:
    letter = (name or "?")[0].upper()
    if picture:
        return (
            f'<div style="position:relative;width:{size}px;height:{size}px;flex-shrink:0;">'
            f'<div style="position:absolute;inset:-3px;border-radius:50%;'
            f'background:conic-gradient(#FF5200,#3B82F6,#22C55E,#FF5200);'
            f'animation:adm-ring 4s linear infinite;opacity:0.5;"></div>'
            f'<img src="{picture}" style="position:relative;width:{size}px;height:{size}px;'
            f'border-radius:50%;object-fit:cover;border:2px solid #fff;'
            f'box-shadow:0 4px 16px rgba(0,0,0,0.10);">'
            f'</div>'
        )
    return (
        f'<div style="width:{size}px;height:{size}px;border-radius:50%;'
        f'background:linear-gradient(135deg,#0A1F44,#1D4ED8);'
        f'display:flex;align-items:center;justify-content:center;'
        f'color:white;font-weight:800;font-size:{int(size*0.42)}px;flex-shrink:0;'
        f'box-shadow:0 4px 16px rgba(29,78,216,0.30);'
        f'transition:transform 0.3s ease;" '
        f'onmouseover="this.style.transform=\'scale(1.08)\'" '
        f'onmouseout="this.style.transform=\'scale(1)\'">{letter}</div>'
    )

def _time_ago(ts_seconds: float) -> str:
    diff = time.time() - ts_seconds
    if diff < 60:
        return "vừa xong"
    elif diff < 3600:
        return f"{int(diff // 60)} phút trước"
    elif diff < 86400:
        return f"{int(diff // 3600)} giờ trước"
    return f"{int(diff // 86400)} ngày trước"

_SVG_ICONS = {
    "shield": '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>',
    "pulse": '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/></svg>',
    "megaphone": '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m3 11 18-5v12L3 13v-2z"/><path d="M11.6 16.8a3 3 0 1 1-5.8-1.6"/></svg>',
    "cpu": '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="4" y="4" width="16" height="16" rx="2"/><rect x="9" y="9" width="6" height="6"/><path d="M15 2v2"/><path d="M15 20v2"/><path d="M2 15h2"/><path d="M2 9h2"/><path d="M20 15h2"/><path d="M20 9h2"/><path d="M9 2v2"/><path d="M9 20v2"/></svg>',
    "chart": '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="6" y1="20" x2="6" y2="14"/></svg>',
    "users": '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M22 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>',
    "calendar": '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="4" width="18" height="18" rx="2" ry="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg>',
    "lock": '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="11" width="18" height="11" rx="2" ry="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/></svg>',
    "unlock": '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="11" width="18" height="11" rx="2" ry="2"/><path d="M7 11V7a5 5 0 0 1 9.9-1"/></svg>',
    "trash": '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/></svg>',
    "download": '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>',
    "refresh": '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="23 4 23 10 17 10"/><polyline points="1 20 1 14 7 14"/><path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"/></svg>',
    "empty_users": '<svg width="80" height="80" viewBox="0 0 24 24" fill="none" stroke="#CBD5E1" stroke-width="1.2" stroke-linecap="round" stroke-linejoin="round"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>',
    "empty_logs": '<svg width="80" height="80" viewBox="0 0 24 24" fill="none" stroke="#CBD5E1" stroke-width="1.2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/><polyline points="10 9 9 9 8 9"/></svg>',
}

_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Exo+2:ital,wght@0,300;0,400;0,500;0,600;0,700;0,800;0,900;1,400&display=swap');

.adm-wrap { font-family: 'Exo 2', sans-serif; color: #0A1F44; }

/* ═══════ PAGE HEADER ═══════ */
.adm-page-header {
    padding: 40px 44px;
    border-radius: 24px;
    margin-bottom: 40px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    background: linear-gradient(135deg, #0A1F44 0%, #173872 50%, #1D4ED8 100%);
    box-shadow: 0 24px 48px rgba(10,31,68,0.18), inset 0 1px 0 rgba(255,255,255,0.08);
    position: relative;
    overflow: hidden;
}
.adm-page-header::before {
    content: '';
    position: absolute;
    inset: 0;
    background:
        radial-gradient(circle at 85% 15%, rgba(255,82,0,0.18) 0%, transparent 40%),
        radial-gradient(circle at 15% 85%, rgba(59,130,246,0.15) 0%, transparent 40%),
        radial-gradient(circle at 50% 50%, rgba(255,255,255,0.03) 0%, transparent 60%);
}
.adm-page-header::after {
    content: '';
    position: absolute;
    inset: 0;
    background-image:
        radial-gradient(circle at 20% 30%, rgba(255,255,255,0.04) 1px, transparent 1px),
        radial-gradient(circle at 80% 70%, rgba(255,255,255,0.03) 1px, transparent 1px),
        radial-gradient(circle at 60% 20%, rgba(255,255,255,0.03) 1px, transparent 1px);
    background-size: 60px 60px, 80px 80px, 40px 40px;
    animation: adm-dots 20s linear infinite;
}
@keyframes adm-dots {
    0% { transform: translateY(0); }
    100% { transform: translateY(-60px); }
}

.adm-header-shapes {
    position: absolute;
    inset: 0;
    pointer-events: none;
    overflow: hidden;
}
.adm-shape {
    position: absolute;
    border-radius: 50%;
    opacity: 0.06;
    background: #FFFFFF;
}
.adm-shape-1 {
    width: 200px; height: 200px;
    top: -60px; right: -40px;
    animation: adm-float 8s ease-in-out infinite;
}
.adm-shape-2 {
    width: 120px; height: 120px;
    bottom: -30px; left: 10%;
    animation: adm-float 6s ease-in-out infinite reverse;
}
.adm-shape-3 {
    width: 80px; height: 80px;
    top: 20%; right: 25%;
    border-radius: 16px;
    transform: rotate(45deg);
    animation: adm-float 10s ease-in-out infinite;
}
@keyframes adm-float {
    0%, 100% { transform: translateY(0) rotate(0deg); }
    33% { transform: translateY(-12px) rotate(3deg); }
    66% { transform: translateY(8px) rotate(-2deg); }
}

.adm-page-header-content { position: relative; z-index: 2; }
.adm-kicker {
    font-size: 0.62rem;
    font-weight: 800;
    letter-spacing: 0.22em;
    text-transform: uppercase;
    color: #FF8C42;
    margin-bottom: 14px;
    display: inline-flex;
    align-items: center;
    gap: 8px;
    background: rgba(255,82,0,0.12);
    padding: 6px 16px;
    border-radius: 999px;
    border: 1px solid rgba(255,82,0,0.2);
}
.adm-kicker-dot {
    width: 6px; height: 6px;
    border-radius: 50%;
    background: #FF5200;
    animation: adm-pulse 2s ease-in-out infinite;
}
.adm-page-title {
    font-size: 2.4rem;
    font-weight: 900;
    letter-spacing: -0.04em;
    color: #FFFFFF;
    margin: 0 0 10px;
    line-height: 1.1;
}
.adm-page-sub {
    font-size: 0.92rem;
    color: rgba(255,255,255,0.65);
    font-weight: 500;
    margin: 0;
    max-width: 480px;
    line-height: 1.6;
}
.adm-status-pill {
    display: inline-flex;
    align-items: center;
    gap: 10px;
    padding: 12px 24px;
    border-radius: 999px;
    border: 1px solid rgba(255,255,255,0.12);
    background: rgba(255,255,255,0.08);
    backdrop-filter: blur(16px);
    font-size: 0.72rem;
    font-weight: 800;
    color: #FFFFFF;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    white-space: nowrap;
    position: relative;
    z-index: 2;
    box-shadow: 0 8px 32px rgba(0,0,0,0.12), inset 0 1px 0 rgba(255,255,255,0.1);
}
.adm-status-dot {
    width: 8px; height: 8px;
    border-radius: 50%;
    background: #4ADE80;
    box-shadow: 0 0 0 4px rgba(74,222,128,0.2), 0 0 12px rgba(74,222,128,0.4);
    animation: adm-pulse 2s ease-in-out infinite;
}
@keyframes adm-pulse {
    0%,100% { opacity: 1; transform: scale(1); }
    50%      { opacity: 0.6; transform: scale(1.15); }
}
@keyframes adm-ring {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
}

/* ═══════ SECTION HEADER ═══════ */
.adm-section-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin: 52px 0 28px;
    padding-bottom: 18px;
    border-bottom: 2px solid #F1F5F9;
    position: relative;
}
.adm-section-header::after {
    content: '';
    position: absolute;
    bottom: -2px;
    left: 0;
    width: 80px;
    height: 2px;
    background: linear-gradient(90deg, #FF5200, transparent);
}
.adm-section-title {
    font-size: 1.15rem;
    font-weight: 800;
    color: #0A1F44;
    letter-spacing: -0.02em;
    margin: 0;
    display: flex;
    align-items: center;
    gap: 14px;
}
.adm-section-num {
    font-size: 0.65rem;
    font-weight: 900;
    color: #FF5200;
    background: linear-gradient(135deg, #FFF4EF, #FFE5D6);
    width: 28px; height: 28px;
    border-radius: 8px;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    border: 1px solid #FFD5BF;
    flex-shrink: 0;
}
.adm-section-accent {
    width: 4px; height: 20px;
    background: linear-gradient(180deg, #FF5200, #FF8C42);
    border-radius: 4px;
    display: inline-block;
    flex-shrink: 0;
}
.adm-section-tag {
    font-size: 0.62rem;
    font-weight: 800;
    color: #64748B;
    text-transform: uppercase;
    letter-spacing: 0.14em;
    background: #F8FAFC;
    padding: 6px 16px;
    border-radius: 999px;
    border: 1px solid #E2E8F0;
}

/* ═══════ METRIC CARDS ═══════ */
.adm-metrics-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 22px;
    margin-bottom: 32px;
}
.adm-metric-card {
    background: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 20px;
    padding: 30px 32px;
    position: relative;
    overflow: hidden;
    box-shadow: 0 4px 16px rgba(10,31,68,0.04);
    transition: transform 0.3s cubic-bezier(.4,0,.2,1), box-shadow 0.3s ease, border-color 0.3s ease;
}
.adm-metric-card:hover {
    transform: translateY(-6px);
    box-shadow: 0 20px 48px rgba(10,31,68,0.10);
    border-color: #CBD5E1;
}
.adm-metric-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 4px;
}
.adm-metric-card.accent-orange::before { background: linear-gradient(90deg, #FF5200, #FF8C42); }
.adm-metric-card.accent-blue::before  { background: linear-gradient(90deg, #1D4ED8, #3B82F6); }
.adm-metric-card.accent-green::before { background: linear-gradient(90deg, #16A34A, #4ADE80); }

.adm-metric-card::after {
    content: '';
    position: absolute;
    bottom: -30px; right: -30px;
    width: 100px; height: 100px;
    border-radius: 50%;
    opacity: 0.04;
}
.adm-metric-card.accent-orange::after { background: #FF5200; }
.adm-metric-card.accent-blue::after  { background: #1D4ED8; }
.adm-metric-card.accent-green::after { background: #16A34A; }

.adm-metric-icon {
    width: 44px; height: 44px;
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    margin-bottom: 18px;
}
.adm-metric-icon.icon-orange { background: #FFF3EE; color: #FF5200; }
.adm-metric-icon.icon-blue   { background: #EFF6FF; color: #1D4ED8; }
.adm-metric-icon.icon-green  { background: #F0FDF4; color: #16A34A; }

.adm-metric-label {
    font-size: 0.68rem;
    font-weight: 800;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    color: #64748B;
    margin-bottom: 10px;
    display: block;
}
.adm-metric-val {
    font-size: 3rem;
    font-weight: 900;
    color: #0A1F44;
    letter-spacing: -0.04em;
    line-height: 1;
    display: block;
}
.adm-metric-sub {
    font-size: 0.78rem;
    color: #94A3B8;
    margin-top: 10px;
    font-weight: 600;
    display: flex;
    align-items: center;
    gap: 6px;
}
.adm-metric-sub-dot {
    width: 4px; height: 4px;
    border-radius: 50%;
    background: #CBD5E1;
    display: inline-block;
}

/* ═══════ CONTROL CARDS ═══════ */
.adm-ctrl-card {
    background: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 20px;
    padding: 30px 32px;
    height: 100%;
    box-shadow: 0 4px 16px rgba(15,23,42,0.03);
    transition: border-color 0.3s ease, box-shadow 0.3s ease, transform 0.3s ease;
    position: relative;
    overflow: hidden;
}
.adm-ctrl-card:hover {
    border-color: #CBD5E1;
    box-shadow: 0 12px 32px rgba(15,23,42,0.07);
    transform: translateY(-2px);
}
.adm-ctrl-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0;
    width: 4px; height: 100%;
    border-radius: 20px 0 0 20px;
}
.adm-ctrl-card.border-orange::before { background: linear-gradient(180deg, #FF5200, #FF8C42); }
.adm-ctrl-card.border-blue::before   { background: linear-gradient(180deg, #1D4ED8, #3B82F6); }
.adm-ctrl-card.border-green::before  { background: linear-gradient(180deg, #16A34A, #4ADE80); }
.adm-ctrl-card.border-purple::before { background: linear-gradient(180deg, #7C3AED, #A78BFA); }

.adm-ctrl-header {
    display: flex;
    align-items: center;
    gap: 14px;
    margin-bottom: 12px;
}
.adm-ctrl-icon {
    width: 40px; height: 40px;
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
}
.adm-ctrl-icon.icon-orange { background: #FFF3EE; color: #FF5200; }
.adm-ctrl-icon.icon-blue   { background: #EFF6FF; color: #1D4ED8; }
.adm-ctrl-icon.icon-green  { background: #F0FDF4; color: #16A34A; }
.adm-ctrl-icon.icon-purple { background: #F5F3FF; color: #7C3AED; }

.adm-ctrl-title {
    font-size: 0.88rem;
    font-weight: 800;
    color: #0A1F44;
    margin: 0;
    letter-spacing: -0.01em;
}
.adm-ctrl-desc {
    font-size: 0.82rem;
    color: #64748B;
    font-weight: 500;
    margin: 0 0 22px;
    line-height: 1.65;
    display: block;
}

/* ═══════ USER CARDS ═══════ */
.adm-user-card {
    display: flex;
    align-items: center;
    gap: 18px;
    padding: 18px 26px;
    border: 1px solid #E2E8F0;
    border-radius: 16px;
    margin-bottom: 12px;
    background: #FFFFFF;
    transition: all 0.25s cubic-bezier(.4,0,.2,1);
    box-shadow: 0 2px 8px rgba(15,23,42,0.02);
    position: relative;
    overflow: hidden;
}
.adm-user-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0;
    width: 3px; height: 100%;
    background: linear-gradient(180deg, #22C55E, #4ADE80);
    opacity: 0;
    transition: opacity 0.25s ease;
    border-radius: 16px 0 0 16px;
}
.adm-user-card:hover {
    border-color: #94A3B8;
    box-shadow: 0 12px 28px rgba(15,23,42,0.07);
    transform: translateX(4px);
}
.adm-user-card:hover::before { opacity: 1; }

.adm-user-info { flex: 1; min-width: 0; }
.adm-user-name {
    font-size: 0.95rem;
    font-weight: 800;
    color: #0A1F44;
    display: flex;
    align-items: center;
    gap: 10px;
    flex-wrap: wrap;
    margin-bottom: 4px;
}
.adm-user-email {
    font-size: 0.78rem;
    color: #64748B;
    font-weight: 500;
}
.adm-user-meta {
    text-align: right;
    flex-shrink: 0;
}
.adm-online-dot {
    display: inline-flex;
    align-items: center;
    gap: 7px;
    font-size: 0.72rem;
    font-weight: 800;
    color: #16A34A;
    background: #F0FDF4;
    padding: 5px 12px;
    border-radius: 999px;
    border: 1px solid #BBF7D0;
}
.adm-online-dot::before {
    content: '';
    width: 7px; height: 7px;
    border-radius: 50%;
    background: #22C55E;
    flex-shrink: 0;
    box-shadow: 0 0 0 3px rgba(34,197,94,0.15);
    animation: adm-pulse 2s ease-in-out infinite;
}
.adm-user-ts {
    font-size: 0.68rem;
    color: #94A3B8;
    margin-top: 6px;
    font-weight: 600;
}

/* ═══════ ONLINE BADGE ═══════ */
.adm-online-badge {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    background: linear-gradient(135deg, #F0FDF4, #DCFCE7);
    border: 1px solid #BBF7D0;
    color: #15803D;
    font-size: 0.72rem;
    font-weight: 800;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    padding: 6px 16px;
    border-radius: 999px;
    vertical-align: middle;
    margin-left: 14px;
    box-shadow: 0 4px 12px rgba(21,128,61,0.08);
}
.adm-online-badge::before {
    content: '';
    width: 8px; height: 8px;
    border-radius: 50%;
    background: #22C55E;
    animation: adm-pulse 2s ease-in-out infinite;
}

/* ═══════ CLEANUP BOX ═══════ */
.adm-cleanup-box {
    background: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 20px;
    padding: 36px 40px;
    box-shadow: 0 4px 16px rgba(15,23,42,0.03);
    position: relative;
    overflow: hidden;
}
.adm-cleanup-box::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
    background: linear-gradient(90deg, #F59E0B, #FBBF24, #F59E0B);
}
.adm-cleanup-title {
    font-size: 0.88rem;
    font-weight: 800;
    color: #0A1F44;
    margin: 0 0 8px;
    display: flex;
    align-items: center;
    gap: 10px;
}
.adm-cleanup-desc {
    font-size: 0.82rem;
    color: #64748B;
    margin: 0 0 28px;
    line-height: 1.65;
    font-weight: 500;
}

/* ═══════ EMPTY STATES ═══════ */
.adm-empty-state {
    text-align: center;
    padding: 56px 24px;
    background: #FFFFFF;
    border: 1.5px dashed #E2E8F0;
    border-radius: 20px;
    margin-top: 16px;
    position: relative;
    overflow: hidden;
}
.adm-empty-state::before {
    content: '';
    position: absolute;
    inset: 0;
    background: radial-gradient(circle at 50% 0%, rgba(255,82,0,0.02), transparent 60%);
}
.adm-empty-icon {
    margin-bottom: 20px;
    opacity: 0.5;
}
.adm-empty-title {
    font-size: 1rem;
    font-weight: 700;
    color: #64748B;
    margin: 0 0 6px;
}
.adm-empty-desc {
    font-size: 0.82rem;
    color: #94A3B8;
    margin: 0;
    font-weight: 500;
}

/* ═══════ BUTTONS ═══════ */
.adm-wrap .stButton > button[kind="primary"],
.adm-wrap .stButton > button[data-testid="stFormSubmitButton"] button {
    background: linear-gradient(135deg, #FF5200, #FF7A33) !important;
    color: white !important;
    border: none !important;
    border-radius: 12px !important;
    font-weight: 700 !important;
    font-size: 0.85rem !important;
    padding: 12px 24px !important;
    letter-spacing: -0.01em !important;
    box-shadow: 0 4px 16px rgba(255,82,0,0.25) !important;
    transition: all 0.2s cubic-bezier(.4,0,.2,1) !important;
}
.adm-wrap .stButton > button[kind="primary"]:hover,
.adm-wrap .stButton > button[data-testid="stFormSubmitButton"] button:hover {
    background: linear-gradient(135deg, #E84A00, #FF5200) !important;
    box-shadow: 0 8px 24px rgba(255,82,0,0.35) !important;
    transform: translateY(-2px) !important;
}
.adm-wrap .stButton > button[kind="secondary"] {
    background: #F8FAFC !important;
    color: #475569 !important;
    border: 1.5px solid #E2E8F0 !important;
    border-radius: 12px !important;
    font-weight: 700 !important;
    font-size: 0.85rem !important;
    padding: 12px 24px !important;
    transition: all 0.2s cubic-bezier(.4,0,.2,1) !important;
}
.adm-wrap .stButton > button[kind="secondary"]:hover {
    background: #FFF3EE !important;
    color: #FF5200 !important;
    border-color: #FFD0B9 !important;
    box-shadow: 0 4px 12px rgba(255,82,0,0.1) !important;
    transform: translateY(-1px) !important;
}

/* ═══════ DATAFRAME ═══════ */
.adm-wrap .stDataFrame {
    border-radius: 16px !important;
    overflow: hidden !important;
    border: 1px solid #E2E8F0 !important;
    box-shadow: 0 4px 16px rgba(15,23,42,0.04) !important;
}
.adm-wrap .stDataFrame [data-testid="stDataFrameResizable"] {
    border-radius: 16px !important;
}

/* ═══════ TOGGLE ═══════ */
.adm-wrap .stToggle [data-baseweb="toggle"] > div {
    border-radius: 999px !important;
}

/* ═══════ TEXTAREA & INPUT ═══════ */
.adm-wrap textarea,
.adm-wrap [data-testid="stTextInput"] input {
    border-radius: 12px !important;
    border: 1.5px solid #E2E8F0 !important;
    transition: all 0.15s ease !important;
}
.adm-wrap textarea:focus,
.adm-wrap [data-testid="stTextInput"] input:focus {
    border-color: #FF5200 !important;
    box-shadow: 0 0 0 3px rgba(255,82,0,0.08) !important;
}

/* ═══════ SLIDER ═══════ */
.adm-wrap [data-testid="stSlider"] [role="slider"] {
    background: #FF5200 !important;
}

/* ═══════ DOWNLOAD BUTTON ═══════ */
.adm-wrap .stDownloadButton > button {
    background: #F8FAFC !important;
    color: #475569 !important;
    border: 1.5px solid #E2E8F0 !important;
    border-radius: 12px !important;
    font-weight: 700 !important;
    font-size: 0.82rem !important;
    transition: all 0.2s ease !important;
}
.adm-wrap .stDownloadButton > button:hover {
    background: #EFF6FF !important;
    color: #1D4ED8 !important;
    border-color: #93C5FD !important;
}
</style>
"""


def render():
    from utils.ai_generator import _get_groq_keys

    st.markdown(_CSS, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="adm-wrap">
        <div class="adm-page-header">
            <div class="adm-header-shapes">
                <div class="adm-shape adm-shape-1"></div>
                <div class="adm-shape adm-shape-2"></div>
                <div class="adm-shape adm-shape-3"></div>
            </div>
            <div class="adm-page-header-content">
                <span class="adm-kicker"><span class="adm-kicker-dot"></span> System Administration</span>
                <h1 class="adm-page-title">Admin Panel</h1>
                <p class="adm-page-sub">Quản lý hệ thống, theo dõi lưu lượng và kiểm soát truy cập cho EES 2026 Dashboard.</p>
            </div>
            <div class="adm-status-pill">
                <span class="adm-status-dot"></span>
                Authorized Session
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    state       = load_state()
    is_locked   = state.get("is_locked", False)
    announcement = state.get("announcement", {"active": False, "text": ""})
    ai_config   = state.get("ai_config", {"temperature": 0.3})

    st.markdown("""
    <div class="adm-section-header">
        <h2 class="adm-section-title">
            <span class="adm-section-num">01</span>
            <span class="adm-section-accent"></span>
            Quản lý Truy cập
        </h2>
        <span class="adm-section-tag">Workspace Control</span>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2, gap="large")

    with col1:
        st.markdown('<div class="adm-ctrl-card border-orange">', unsafe_allow_html=True)
        st.markdown(f"""
        <div class="adm-ctrl-header">
            <div class="adm-ctrl-icon icon-orange">{_SVG_ICONS['shield']}</div>
            <span class="adm-ctrl-title">Chế độ Bảo trì</span>
        </div>
        """, unsafe_allow_html=True)
        st.markdown('<span class="adm-ctrl-desc">Kích hoạt sẽ chặn truy cập toàn bộ tài khoản thường ngay lập tức. Tính năng này dành cho bảo trì khẩn cấp.</span>', unsafe_allow_html=True)
        new_status = st.toggle("Kích hoạt Chế độ Bảo trì", value=is_locked)
        if new_status != is_locked:
            state["is_locked"] = new_status
            save_state(state)
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="adm-ctrl-card border-blue">', unsafe_allow_html=True)
        st.markdown(f"""
        <div class="adm-ctrl-header">
            <div class="adm-ctrl-icon icon-blue">{_SVG_ICONS['pulse']}</div>
            <span class="adm-ctrl-title">Trạng thái Hệ thống</span>
        </div>
        """, unsafe_allow_html=True)
        st.markdown('<span class="adm-ctrl-desc">Kiểm tra tình trạng kết nối và phục vụ báo cáo hiện tại của toàn bộ Dashboard.</span>', unsafe_allow_html=True)
        if is_locked:
            st.error("ĐANG BẢO TRÌ — Hệ thống đang chặn truy cập bên ngoài.")
        else:
            st.success("HOẠT ĐỘNG BÌNH THƯỜNG — Đang phục vụ toàn bộ người dùng.")
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("""
    <div class="adm-section-header">
        <h2 class="adm-section-title">
            <span class="adm-section-num">02</span>
            <span class="adm-section-accent"></span>
            Thông báo &amp; Cấu hình
        </h2>
        <span class="adm-section-tag">Broadcast &amp; Config</span>
    </div>
    """, unsafe_allow_html=True)

    col3, col4 = st.columns(2, gap="large")

    with col3:
        st.markdown('<div class="adm-ctrl-card border-green">', unsafe_allow_html=True)
        st.markdown(f"""
        <div class="adm-ctrl-header">
            <div class="adm-ctrl-icon icon-green">{_SVG_ICONS['megaphone']}</div>
            <span class="adm-ctrl-title">Thông báo Toàn cục (Banner)</span>
        </div>
        """, unsafe_allow_html=True)
        st.markdown('<span class="adm-ctrl-desc">Thông báo sẽ hiển thị nổi bật ở đầu trang của tất cả người dùng khi được kích hoạt.</span>', unsafe_allow_html=True)
        new_ann_text   = st.text_area("Nội dung thông báo", value=announcement.get("text", ""), height=120, label_visibility="collapsed", placeholder="Nhập nội dung thông báo ở đây...")
        new_ann_active = st.toggle("Hiển thị Thông báo", value=announcement.get("active", False))
        if st.button("Lưu Thông báo", use_container_width=True, type="primary"):
            state["announcement"] = {"text": new_ann_text, "active": new_ann_active}
            save_state(state)
            st.toast("Đã cập nhật thông báo!")
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    with col4:
        st.markdown('<div class="adm-ctrl-card border-purple">', unsafe_allow_html=True)
        st.markdown(f"""
        <div class="adm-ctrl-header">
            <div class="adm-ctrl-icon icon-purple">{_SVG_ICONS['cpu']}</div>
            <span class="adm-ctrl-title">Cấu hình AI &amp; Dữ liệu</span>
        </div>
        """, unsafe_allow_html=True)
        groq_keys = _get_groq_keys()
        st.markdown(f'<span class="adm-ctrl-desc">Hệ thống phân tích AI đang có <strong>{len(groq_keys)} API key(s)</strong> khả dụng.</span>', unsafe_allow_html=True)
        new_temp = st.slider("Độ sáng tạo AI (Temperature)", 0.0, 1.0, float(ai_config.get("temperature", 0.3)), 0.05, label_visibility="visible")
        c41, c42 = st.columns(2)
        with c41:
            if st.button("Lưu Cấu hình AI", use_container_width=True, type="primary"):
                state["ai_config"] = {"temperature": new_temp}
                save_state(state)
                st.toast("Đã lưu cấu hình AI!")
        with c42:
            if st.button("Làm mới Cache", use_container_width=True, type="secondary"):
                st.cache_data.clear()
                st.toast("Đã xóa bộ nhớ đệm!")
        st.markdown('</div>', unsafe_allow_html=True)

    sessions = load_active_sessions()
    now = time.time()
    online_users = [
        data for data in sessions.values()
        if now - data.get("last_seen", 0) <= ONLINE_THRESHOLD_SECONDS
    ]
    online_users.sort(key=lambda x: x.get("last_seen", 0), reverse=True)
    n_online = len(online_users)

    st.markdown(f"""
    <div class="adm-section-header">
        <h2 class="adm-section-title">
            <span class="adm-section-num">03</span>
            <span class="adm-section-accent"></span>
            Ai đang xem Dashboard?
            <span class="adm-online-badge">{n_online} Online</span>
        </h2>
        <span class="adm-section-tag">Live Monitor · 10 phút gần nhất</span>
    </div>
    """, unsafe_allow_html=True)

    col_ref, _ = st.columns([1, 6])
    with col_ref:
        if st.button("Làm mới danh sách", key="refresh_online", use_container_width=True):
            st.rerun()

    if not online_users:
        st.markdown(f"""
        <div class="adm-empty-state">
            <div class="adm-empty-icon">{_SVG_ICONS['empty_users']}</div>
            <p class="adm-empty-title">Không có ai đang trực tuyến</p>
            <p class="adm-empty-desc">Hiện không có người dùng nào hoạt động trong 10 phút gần nhất.</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown('<div style="margin-top:16px;">', unsafe_allow_html=True)
        for user in online_users:
            u_email   = user.get("email", "")
            u_name    = user.get("name", u_email)
            u_picture = user.get("picture", "")
            u_auth    = user.get("authorization", {})
            u_role    = u_auth.get("role", "User") if isinstance(u_auth, dict) else "User"
            u_last    = user.get("last_seen", 0)
            avatar    = _avatar_html(u_name, u_picture, size=46)
            badge     = _role_badge_html(u_role)
            ago       = _time_ago(u_last)
            ts_str    = datetime.fromtimestamp(u_last).strftime("%H:%M  %d/%m/%Y") if u_last else "—"

            st.markdown(f"""
            <div class="adm-user-card">
                {avatar}
                <div class="adm-user-info">
                    <div class="adm-user-name">
                        {u_name}
                        {badge}
                    </div>
                    <div class="adm-user-email">{u_email}</div>
                </div>
                <div class="adm-user-meta">
                    <div class="adm-online-dot">Đang xem · {ago}</div>
                    <div class="adm-user-ts">{ts_str}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    df_logs = load_access_logs()
    total_logins  = len(df_logs)
    unique_users  = int(df_logs["email"].nunique()) if not df_logs.empty else 0
    today_str     = datetime.now().strftime("%Y-%m-%d")
    if not df_logs.empty and "timestamp" in df_logs.columns:
        today_logins = int(df_logs["timestamp"].dt.strftime("%Y-%m-%d").eq(today_str).sum())
    else:
        today_logins = 0

    st.markdown("""
    <div class="adm-section-header">
        <h2 class="adm-section-title">
            <span class="adm-section-num">04</span>
            <span class="adm-section-accent"></span>
            Lịch sử Đăng nhập
        </h2>
        <span class="adm-section-tag">Access Logs</span>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="adm-metrics-grid">
        <div class="adm-metric-card accent-orange">
            <div class="adm-metric-icon icon-orange">{_SVG_ICONS['chart']}</div>
            <span class="adm-metric-label">Tổng lượt truy cập</span>
            <span class="adm-metric-val">{total_logins:,}</span>
            <span class="adm-metric-sub"><span class="adm-metric-sub-dot"></span> Tất cả thời gian</span>
        </div>
        <div class="adm-metric-card accent-blue">
            <div class="adm-metric-icon icon-blue">{_SVG_ICONS['users']}</div>
            <span class="adm-metric-label">Người dùng duy nhất</span>
            <span class="adm-metric-val">{unique_users:,}</span>
            <span class="adm-metric-sub"><span class="adm-metric-sub-dot"></span> Unique email</span>
        </div>
        <div class="adm-metric-card accent-green">
            <div class="adm-metric-icon icon-green">{_SVG_ICONS['calendar']}</div>
            <span class="adm-metric-label">Lượt truy cập hôm nay</span>
            <span class="adm-metric-val">{today_logins:,}</span>
            <span class="adm-metric-sub"><span class="adm-metric-sub-dot"></span> {datetime.now().strftime("%d/%m/%Y")}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if df_logs.empty:
        st.markdown(f"""
        <div class="adm-empty-state">
            <div class="adm-empty-icon">{_SVG_ICONS['empty_logs']}</div>
            <p class="adm-empty-title">Chưa có lịch sử đăng nhập</p>
            <p class="adm-empty-desc">Lịch sử đăng nhập sẽ được ghi nhận tự động khi có người dùng truy cập.</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        display_df = df_logs.copy()
        if "timestamp" in display_df.columns:
            display_df["timestamp"] = display_df["timestamp"].dt.strftime("%H:%M  %d/%m/%Y")

        display_df.rename(columns={
            "timestamp":    "Thời gian",
            "email":        "Email",
            "name":         "Tên",
            "role":         "Vai trò (Role)",
            "login_method": "Phương thức",
        }, inplace=True)

        st.dataframe(
            display_df.head(300),
            use_container_width=True,
            hide_index=True,
        )

        csv_bytes = df_logs.to_csv(index=False).encode("utf-8")
        dl_col, _ = st.columns([1, 3])
        with dl_col:
            st.download_button(
                label="Tải về CSV",
                data=csv_bytes,
                file_name=f"access_logs_{today_str}.csv",
                mime="text/csv",
                key="dl_logs",
                use_container_width=True,
            )

    st.markdown("""
    <div class="adm-section-header">
        <h2 class="adm-section-title">
            <span class="adm-section-num">05</span>
            <span class="adm-section-accent"></span>
            Dọn dẹp Log
        </h2>
        <span class="adm-section-tag">VPS Optimization</span>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="adm-cleanup-box">
        <div class="adm-ctrl-header">
            <div class="adm-ctrl-icon icon-orange">{_SVG_ICONS['trash']}</div>
            <span class="adm-cleanup-title">Dọn dẹp Lịch sử</span>
        </div>
        <p class="adm-cleanup-desc">Xóa bớt lịch sử cũ để giữ file nhỏ gọn, tránh làm chậm server. Hệ thống tự động giữ tối đa 5.000 dòng — vượt quá sẽ tự cắt còn 3.000 dòng.</p>
    """, unsafe_allow_html=True)

    c_clean1, c_clean2 = st.columns(2, gap="large")

    with c_clean1:
        days_keep = st.number_input(
            "Giữ lại log trong bao nhiêu ngày gần đây?",
            min_value=1, max_value=365, value=30, step=1,
        )
        if st.button(f"Xóa log cũ hơn {int(days_keep)} ngày", use_container_width=True, type="secondary"):
            if not df_logs.empty and "timestamp" in df_logs.columns:
                cutoff = datetime.now() - timedelta(days=int(days_keep))
                kept    = df_logs[df_logs["timestamp"] >= cutoff]
                kept.to_csv(ACCESS_LOGS_FILE, index=False, encoding="utf-8")
                removed = len(df_logs) - len(kept)
                st.toast(f"Đã xóa {removed:,} dòng log cũ. Còn lại {len(kept):,} dòng.")
                st.rerun()
            else:
                st.toast("File log trống, không cần xóa.")

    with c_clean2:
        st.markdown("<br>", unsafe_allow_html=True)
        if "confirm_clear_all" not in st.session_state:
            st.session_state.confirm_clear_all = False

        if not st.session_state.confirm_clear_all:
            if st.button("Xóa TOÀN BỘ lịch sử đăng nhập", type="secondary", use_container_width=True):
                st.session_state.confirm_clear_all = True
                st.rerun()
        else:
            st.warning("Bạn chắc chắn muốn xóa TOÀN BỘ lịch sử? Hành động này không thể hoàn tác!")
            cc1, cc2 = st.columns(2)
            with cc1:
                if st.button("Xác nhận Xóa tất cả", type="primary", use_container_width=True):
                    try:
                        os.remove(ACCESS_LOGS_FILE)
                    except FileNotFoundError:
                        pass
                    st.session_state.confirm_clear_all = False
                    st.toast("Đã xóa toàn bộ lịch sử truy cập!")
                    st.rerun()
            with cc2:
                if st.button("Hủy bỏ", use_container_width=True):
                    st.session_state.confirm_clear_all = False
                    st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown("<br><br>", unsafe_allow_html=True)
