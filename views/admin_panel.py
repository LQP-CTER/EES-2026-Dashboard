import streamlit as st
import json
import os
import csv
import time
from datetime import datetime, timedelta
import pandas as pd

APP_STATE_FILE   = os.path.join("config", "app_state.json")
SESSIONS_FILE    = os.path.join("config", "active_sessions.json")
ACCESS_LOGS_FILE = os.path.join("config", "access_logs.csv")

ONLINE_THRESHOLD_SECONDS = 10 * 60  # 10 phut = "dang xem"


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────
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
        return '<span style="background:#DC2626;color:white;font-size:0.58rem;font-weight:800;padding:2px 8px;border-radius:3px;letter-spacing:0.07em;text-transform:uppercase;">ADMIN</span>'
    return '<span style="background:#1E40AF;color:white;font-size:0.58rem;font-weight:800;padding:2px 8px;border-radius:3px;letter-spacing:0.07em;text-transform:uppercase;">USER</span>'

def _avatar_html(name: str, picture: str = "", size: int = 36) -> str:
    letter = (name or "?")[0].upper()
    if picture:
        return f'<img src="{picture}" style="width:{size}px;height:{size}px;border-radius:50%;object-fit:cover;border:2px solid #E2E8F0;flex-shrink:0;">'
    return (
        f'<div style="width:{size}px;height:{size}px;border-radius:50%;'
        f'background:linear-gradient(135deg,#0A1F44,#1D4ED8);'
        f'display:flex;align-items:center;justify-content:center;'
        f'color:white;font-weight:800;font-size:{int(size*0.42)}px;flex-shrink:0;">{letter}</div>'
    )

def _time_ago(ts_seconds: float) -> str:
    diff = time.time() - ts_seconds
    if diff < 60:
        return "vua xong"
    elif diff < 3600:
        return f"{int(diff // 60)} phut truoc"
    elif diff < 86400:
        return f"{int(diff // 3600)} gio truoc"
    return f"{int(diff // 86400)} ngay truoc"

_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');

/* ===== BASE ===== */
.adm-wrap { font-family: 'Inter', sans-serif; color: #0A1F44; }

/* ===== PAGE HEADER ===== */
.adm-page-header {
    padding: 0 0 28px;
    border-bottom: 2px solid #F1F5F9;
    margin-bottom: 36px;
    display: flex;
    align-items: flex-end;
    justify-content: space-between;
}
.adm-kicker {
    font-size: 0.65rem;
    font-weight: 800;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    color: #FF5200;
    margin-bottom: 8px;
    display: block;
}
.adm-page-title {
    font-size: 1.9rem;
    font-weight: 900;
    letter-spacing: -0.035em;
    color: #0A1F44;
    margin: 0 0 6px;
    line-height: 1.1;
}
.adm-page-sub {
    font-size: 0.88rem;
    color: #64748B;
    font-weight: 500;
    margin: 0;
}
.adm-status-pill {
    display: inline-flex;
    align-items: center;
    gap: 7px;
    padding: 7px 14px;
    border-radius: 999px;
    border: 1px solid #E2E8F0;
    background: #F8FAFC;
    font-size: 0.7rem;
    font-weight: 700;
    color: #475569;
    letter-spacing: 0.05em;
    text-transform: uppercase;
    white-space: nowrap;
}
.adm-status-dot {
    width: 7px; height: 7px;
    border-radius: 50%;
    background: #22C55E;
    box-shadow: 0 0 0 3px rgba(34,197,94,0.2);
    animation: adm-pulse 2s ease-in-out infinite;
}
@keyframes adm-pulse {
    0%,100% { opacity: 1; }
    50%      { opacity: 0.45; }
}

/* ===== SECTION HEADER ===== */
.adm-section-header {
    display: flex;
    align-items: baseline;
    justify-content: space-between;
    margin: 40px 0 20px;
    padding-bottom: 14px;
    border-bottom: 1.5px solid #F1F5F9;
}
.adm-section-title {
    font-size: 1.05rem;
    font-weight: 800;
    color: #0A1F44;
    letter-spacing: -0.02em;
    margin: 0;
    display: flex;
    align-items: center;
    gap: 10px;
}
.adm-section-accent {
    width: 3px; height: 16px;
    background: #FF5200;
    border-radius: 2px;
    display: inline-block;
    flex-shrink: 0;
}
.adm-section-tag {
    font-size: 0.65rem;
    font-weight: 800;
    color: #FF5200;
    text-transform: uppercase;
    letter-spacing: 0.14em;
    background: #FFF4EF;
    padding: 3px 10px;
    border-radius: 999px;
    border: 1px solid #FFD5BF;
}

/* ===== METRIC CARDS (overview style) ===== */
.adm-metrics-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 16px;
    margin-bottom: 24px;
}
.adm-metric-card {
    background: #F8FAFC;
    border: 1px solid #E2E8F0;
    border-radius: 16px;
    padding: 22px 26px 24px;
    position: relative;
    overflow: hidden;
}
.adm-metric-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
    background: linear-gradient(90deg, #FF5200, #FF8C42);
    border-radius: 16px 16px 0 0;
}
.adm-metric-label {
    font-size: 0.65rem;
    font-weight: 800;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    color: #94A3B8;
    margin-bottom: 10px;
    display: block;
}
.adm-metric-val {
    font-size: 2.4rem;
    font-weight: 900;
    color: #0A1F44;
    letter-spacing: -0.04em;
    line-height: 1;
    display: block;
}
.adm-metric-sub {
    font-size: 0.75rem;
    color: #64748B;
    margin-top: 8px;
    font-weight: 600;
    display: block;
}

/* ===== CONTROL CARDS ===== */
.adm-ctrl-card {
    background: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 16px;
    padding: 24px 26px;
    height: 100%;
    box-shadow: 0 1px 4px rgba(15,23,42,0.04);
}
.adm-ctrl-title {
    font-size: 0.78rem;
    font-weight: 800;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: #0A1F44;
    margin: 0 0 6px;
    display: block;
}
.adm-ctrl-desc {
    font-size: 0.78rem;
    color: #94A3B8;
    font-weight: 500;
    margin: 0 0 18px;
    line-height: 1.5;
    display: block;
}

/* ===== ONLINE USER CARDS ===== */
.adm-user-card {
    display: flex;
    align-items: center;
    gap: 14px;
    padding: 14px 20px;
    border: 1px solid #E2E8F0;
    border-radius: 12px;
    margin-bottom: 10px;
    background: #FFFFFF;
    transition: border-color 0.15s ease, box-shadow 0.15s ease;
}
.adm-user-card:hover {
    border-color: #CBD5E1;
    box-shadow: 0 2px 10px rgba(15,23,42,0.05);
}
.adm-user-info { flex: 1; min-width: 0; }
.adm-user-name {
    font-size: 0.88rem;
    font-weight: 700;
    color: #0A1F44;
    display: flex;
    align-items: center;
    gap: 8px;
    flex-wrap: wrap;
    margin-bottom: 2px;
}
.adm-user-email {
    font-size: 0.73rem;
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
    gap: 5px;
    font-size: 0.68rem;
    font-weight: 700;
    color: #16A34A;
}
.adm-online-dot::before {
    content: '';
    width: 6px; height: 6px;
    border-radius: 50%;
    background: #22C55E;
    flex-shrink: 0;
}
.adm-user-ts {
    font-size: 0.65rem;
    color: #CBD5E1;
    margin-top: 3px;
}

/* ===== LOG TABLE ===== */
.adm-log-header {
    background: #0A1F44;
    color: white;
    border-radius: 10px 10px 0 0;
    padding: 0;
    overflow: hidden;
}

/* ===== ONLINE COUNT BADGE ===== */
.adm-online-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: #F0FDF4;
    border: 1px solid #BBF7D0;
    color: #15803D;
    font-size: 0.68rem;
    font-weight: 800;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    padding: 4px 12px;
    border-radius: 999px;
    vertical-align: middle;
    margin-left: 12px;
}
.adm-online-badge::before {
    content: '';
    width: 6px; height: 6px;
    border-radius: 50%;
    background: #22C55E;
    animation: adm-pulse 2s ease-in-out infinite;
}

/* ===== CLEANUP BOX ===== */
.adm-cleanup-box {
    background: #FAFAFA;
    border: 1px solid #E2E8F0;
    border-radius: 14px;
    padding: 24px 26px;
}
.adm-cleanup-title {
    font-size: 0.78rem;
    font-weight: 800;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: #0A1F44;
    margin: 0 0 5px;
}
.adm-cleanup-desc {
    font-size: 0.77rem;
    color: #94A3B8;
    margin: 0 0 20px;
}
</style>
"""


# ─────────────────────────────────────────────────────────────────────────────
# Main Render
# ─────────────────────────────────────────────────────────────────────────────
def render():
    from utils.ai_generator import _get_groq_keys

    st.markdown(_CSS, unsafe_allow_html=True)

    # ── Page Header ──────────────────────────────────────────────────────────
    st.markdown("""
    <div class="adm-wrap">
        <div class="adm-page-header">
            <div>
                <span class="adm-kicker">System Administration</span>
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

    # ── Section 1: Access Control ─────────────────────────────────────────────
    st.markdown("""
    <div class="adm-section-header">
        <h2 class="adm-section-title">
            <span class="adm-section-accent"></span>
            Quản lý Truy cập
        </h2>
        <span class="adm-section-tag">Workspace Control</span>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2, gap="medium")

    with col1:
        st.markdown('<div class="adm-ctrl-card">', unsafe_allow_html=True)
        st.markdown('<span class="adm-ctrl-title">Che do Bao tri</span>', unsafe_allow_html=True)
        st.markdown('<span class="adm-ctrl-desc">Kich hoat se chan truy cap toan bo tai khoan thuong ngay lap tuc.</span>', unsafe_allow_html=True)
        new_status = st.toggle("Kich hoat Che do Bao tri", value=is_locked)
        if new_status != is_locked:
            state["is_locked"] = new_status
            save_state(state)
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="adm-ctrl-card">', unsafe_allow_html=True)
        st.markdown('<span class="adm-ctrl-title">Trang thai He thong</span>', unsafe_allow_html=True)
        st.markdown('<span class="adm-ctrl-desc">Kiem tra tinh trang ket noi va phuc vu bao cao hien tai.</span>', unsafe_allow_html=True)
        if is_locked:
            st.error("DANG BAO TRI — He thong dang chan truy cap ben ngoai.")
        else:
            st.success("HOAT DONG BINH THUONG — Dang phuc vu toan bo nguoi dung.")
        st.markdown('</div>', unsafe_allow_html=True)

    # ── Section 2: Announcement + AI Config ──────────────────────────────────
    st.markdown("""
    <div class="adm-section-header">
        <h2 class="adm-section-title">
            <span class="adm-section-accent"></span>
            Thong bao &amp; Cau hinh
        </h2>
        <span class="adm-section-tag">Broadcast &amp; Config</span>
    </div>
    """, unsafe_allow_html=True)

    col3, col4 = st.columns(2, gap="medium")

    with col3:
        st.markdown('<div class="adm-ctrl-card">', unsafe_allow_html=True)
        st.markdown('<span class="adm-ctrl-title">Thong bao Toan cuc (Banner)</span>', unsafe_allow_html=True)
        st.markdown('<span class="adm-ctrl-desc">Thong bao se hien thi noi bat o dau trang cua tat ca nguoi dung.</span>', unsafe_allow_html=True)
        new_ann_text   = st.text_area("Noi dung thong bao", value=announcement.get("text", ""), height=96, label_visibility="collapsed", placeholder="Nhap noi dung thong bao o day...")
        new_ann_active = st.toggle("Hien thi Thong bao", value=announcement.get("active", False))
        if st.button("Luu Thong bao", use_container_width=True):
            state["announcement"] = {"text": new_ann_text, "active": new_ann_active}
            save_state(state)
            st.toast("Da cap nhat thong bao!")
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    with col4:
        st.markdown('<div class="adm-ctrl-card">', unsafe_allow_html=True)
        st.markdown('<span class="adm-ctrl-title">Cau hinh AI &amp; Du lieu</span>', unsafe_allow_html=True)
        groq_keys = _get_groq_keys()
        st.markdown(f'<span class="adm-ctrl-desc">Groq API: <strong>{len(groq_keys)} key(s)</strong> kha dung hien tai.</span>', unsafe_allow_html=True)
        new_temp = st.slider("Do sang tao AI (Temperature)", 0.0, 1.0, float(ai_config.get("temperature", 0.3)), 0.05, label_visibility="visible")
        c41, c42 = st.columns(2)
        with c41:
            if st.button("Luu Cau hinh AI", use_container_width=True):
                state["ai_config"] = {"temperature": new_temp}
                save_state(state)
                st.toast("Da luu cau hinh AI!")
        with c42:
            if st.button("Lam moi Cache", use_container_width=True):
                st.cache_data.clear()
                st.toast("Da xoa bo nho dem!")
        st.markdown('</div>', unsafe_allow_html=True)

    # ── Section 3: Live Online Users ─────────────────────────────────────────
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
            <span class="adm-section-accent"></span>
            Ai dang xem Dashboard?
            <span class="adm-online-badge">{n_online} Online</span>
        </h2>
        <span class="adm-section-tag">Live Monitor · 10 phut gan nhat</span>
    </div>
    """, unsafe_allow_html=True)

    col_ref, _ = st.columns([1, 6])
    with col_ref:
        if st.button("Lam moi danh sach", key="refresh_online", use_container_width=True):
            st.rerun()

    if not online_users:
        st.markdown("""
        <div style="text-align:center;padding:40px 20px;background:#F8FAFC;border:1px solid #E2E8F0;border-radius:14px;color:#94A3B8;">
            <p style="font-size:0.88rem;font-weight:600;margin:0;">Hien khong co ai dang truc tuyen trong 10 phut gan nhat.</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        for user in online_users:
            u_email   = user.get("email", "")
            u_name    = user.get("name", u_email)
            u_picture = user.get("picture", "")
            u_auth    = user.get("authorization", {})
            u_role    = u_auth.get("role", "User") if isinstance(u_auth, dict) else "User"
            u_last    = user.get("last_seen", 0)
            avatar    = _avatar_html(u_name, u_picture, size=38)
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
                    <div class="adm-online-dot">Dang xem · {ago}</div>
                    <div class="adm-user-ts">{ts_str}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

    # ── Section 4: Access Logs ────────────────────────────────────────────────
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
            <span class="adm-section-accent"></span>
            Lich su Dang nhap
        </h2>
        <span class="adm-section-tag">Access Logs</span>
    </div>
    """, unsafe_allow_html=True)

    # Metric cards
    st.markdown(f"""
    <div class="adm-metrics-grid">
        <div class="adm-metric-card">
            <span class="adm-metric-label">Tong luot truy cap</span>
            <span class="adm-metric-val">{total_logins:,}</span>
            <span class="adm-metric-sub">Tat ca thoi gian</span>
        </div>
        <div class="adm-metric-card">
            <span class="adm-metric-label">Nguoi dung duy nhat</span>
            <span class="adm-metric-val">{unique_users:,}</span>
            <span class="adm-metric-sub">Unique email</span>
        </div>
        <div class="adm-metric-card">
            <span class="adm-metric-label">Luot truy cap hom nay</span>
            <span class="adm-metric-val">{today_logins:,}</span>
            <span class="adm-metric-sub">{datetime.now().strftime("%d/%m/%Y")}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Data table
    if df_logs.empty:
        st.markdown("""
        <div style="text-align:center;padding:40px 20px;background:#F8FAFC;border:1px solid #E2E8F0;border-radius:14px;color:#94A3B8;">
            <p style="font-size:0.88rem;font-weight:600;margin:0;">Chua co lich su dang nhap nao duoc ghi nhan.</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        display_df = df_logs.copy()
        if "timestamp" in display_df.columns:
            display_df["timestamp"] = display_df["timestamp"].dt.strftime("%H:%M  %d/%m/%Y")

        display_df.rename(columns={
            "timestamp":    "Thoi gian",
            "email":        "Email",
            "name":         "Ten",
            "role":         "Role",
            "login_method": "Phuong thuc",
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
                label="Tai ve CSV",
                data=csv_bytes,
                file_name=f"access_logs_{today_str}.csv",
                mime="text/csv",
                key="dl_logs",
                use_container_width=True,
            )

    # Cleanup section
    st.markdown("""
    <div class="adm-section-header">
        <h2 class="adm-section-title">
            <span class="adm-section-accent"></span>
            Don dep Log
        </h2>
        <span class="adm-section-tag">VPS Optimization</span>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="adm-cleanup-box">', unsafe_allow_html=True)
    st.markdown('<p class="adm-cleanup-desc">Xoa bot lich su cu de giu file nho gon, tranh lam cham server. File log tu dong giu toi da 5.000 dong — vuot qua se tu trim con 3.000 dong.</p>', unsafe_allow_html=True)

    c_clean1, c_clean2 = st.columns(2, gap="large")

    with c_clean1:
        days_keep = st.number_input(
            "Giu lai log trong bao nhieu ngay gan day?",
            min_value=1, max_value=365, value=30, step=1,
        )
        if st.button(f"Xoa log cu hon {int(days_keep)} ngay", use_container_width=True):
            if not df_logs.empty and "timestamp" in df_logs.columns:
                cutoff = datetime.now() - timedelta(days=int(days_keep))
                kept    = df_logs[df_logs["timestamp"] >= cutoff]
                kept.to_csv(ACCESS_LOGS_FILE, index=False, encoding="utf-8")
                removed = len(df_logs) - len(kept)
                st.toast(f"Da xoa {removed:,} dong log cu. Con lai {len(kept):,} dong.")
                st.rerun()
            else:
                st.toast("File log trong, khong can xoa.")

    with c_clean2:
        st.markdown("<br>", unsafe_allow_html=True)
        if "confirm_clear_all" not in st.session_state:
            st.session_state.confirm_clear_all = False

        if not st.session_state.confirm_clear_all:
            if st.button("Xoa TOAN BO lich su dang nhap", type="secondary", use_container_width=True):
                st.session_state.confirm_clear_all = True
                st.rerun()
        else:
            st.warning("Ban chac chan muon xoa TOAN BO lich su? Hanh dong nay khong the hoan tac!")
            cc1, cc2 = st.columns(2)
            with cc1:
                if st.button("Xac nhan Xoa tat ca", type="primary", use_container_width=True):
                    try:
                        os.remove(ACCESS_LOGS_FILE)
                    except FileNotFoundError:
                        pass
                    st.session_state.confirm_clear_all = False
                    st.toast("Da xoa toan bo lich su truy cap!")
                    st.rerun()
            with cc2:
                if st.button("Huy bo", use_container_width=True):
                    st.session_state.confirm_clear_all = False
                    st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown("<br><br>", unsafe_allow_html=True)
