import streamlit as st
import json
import os
import time
from datetime import datetime, timedelta
import pandas as pd

APP_STATE_FILE   = os.path.join("config", "app_state.json")
SESSIONS_FILE    = os.path.join("config", "active_sessions.json")
ACCESS_LOGS_FILE = os.path.join("config", "access_logs.csv")

ONLINE_THRESHOLD_SECONDS = 10 * 60  # 10 phút = "đang xem"


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
        return '<span style="background:linear-gradient(135deg, #DC2626, #EF4444);color:white;font-size:0.58rem;font-weight:800;padding:4px 10px;border-radius:6px;letter-spacing:0.07em;text-transform:uppercase;box-shadow:0 4px 12px rgba(220,38,38,0.25);">ADMIN</span>'
    return '<span style="background:linear-gradient(135deg, #1E40AF, #3B82F6);color:white;font-size:0.58rem;font-weight:800;padding:4px 10px;border-radius:6px;letter-spacing:0.07em;text-transform:uppercase;box-shadow:0 4px 12px rgba(30,64,175,0.25);">USER</span>'

def _avatar_html(name: str, picture: str = "", size: int = 42) -> str:
    letter = (name or "?")[0].upper()
    if picture:
        return f'<img src="{picture}" style="width:{size}px;height:{size}px;border-radius:50%;object-fit:cover;border:2px solid #E2E8F0;box-shadow:0 4px 12px rgba(0,0,0,0.08);flex-shrink:0;transition:transform 0.3s ease;" onmouseover="this.style.transform=\'scale(1.1)\'" onmouseout="this.style.transform=\'scale(1)\'">'
    return (
        f'<div style="width:{size}px;height:{size}px;border-radius:50%;'
        f'background:linear-gradient(135deg,#0A1F44,#1D4ED8);'
        f'display:flex;align-items:center;justify-content:center;'
        f'color:white;font-weight:800;font-size:{int(size*0.42)}px;flex-shrink:0;box-shadow:0 4px 12px rgba(29,78,216,0.25);transition:transform 0.3s ease;" onmouseover="this.style.transform=\'scale(1.1)\'" onmouseout="this.style.transform=\'scale(1)\'">{letter}</div>'
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

_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');

/* ===== BASE ===== */
.adm-wrap { font-family: 'Inter', sans-serif; color: #0A1F44; }

/* ===== PAGE HEADER ===== */
.adm-page-header {
    padding: 32px 40px;
    border-radius: 24px;
    margin-bottom: 36px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    background: linear-gradient(135deg, #0A1F44 0%, #173872 100%);
    box-shadow: 0 20px 40px rgba(10,31,68,0.15), inset 0 1px 0 rgba(255,255,255,0.1);
    position: relative;
    overflow: hidden;
}
.adm-page-header::before {
    content: '';
    position: absolute;
    inset: 0;
    background: radial-gradient(circle at top right, rgba(255,82,0,0.15), transparent 40%),
                radial-gradient(circle at bottom left, rgba(59,130,246,0.15), transparent 40%);
}
.adm-page-header-content {
    position: relative;
    z-index: 2;
}
.adm-kicker {
    font-size: 0.65rem;
    font-weight: 800;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    color: #FFD5BF;
    margin-bottom: 12px;
    display: block;
}
.adm-page-title {
    font-size: 2.2rem;
    font-weight: 900;
    letter-spacing: -0.035em;
    color: #FFFFFF;
    margin: 0 0 10px;
    line-height: 1.1;
}
.adm-page-sub {
    font-size: 0.95rem;
    color: rgba(255,255,255,0.75);
    font-weight: 500;
    margin: 0;
}
.adm-status-pill {
    display: inline-flex;
    align-items: center;
    gap: 10px;
    padding: 10px 20px;
    border-radius: 999px;
    border: 1px solid rgba(255,255,255,0.15);
    background: rgba(255,255,255,0.1);
    backdrop-filter: blur(12px);
    font-size: 0.75rem;
    font-weight: 800;
    color: #FFFFFF;
    letter-spacing: 0.05em;
    text-transform: uppercase;
    white-space: nowrap;
    position: relative;
    z-index: 2;
    box-shadow: 0 8px 24px rgba(0,0,0,0.1);
}
.adm-status-dot {
    width: 8px; height: 8px;
    border-radius: 50%;
    background: #4ADE80;
    box-shadow: 0 0 0 4px rgba(74,222,128,0.25);
    animation: adm-pulse 2s ease-in-out infinite;
}
@keyframes adm-pulse {
    0%,100% { opacity: 1; transform: scale(1); }
    50%      { opacity: 0.6; transform: scale(1.1); }
}

/* ===== SECTION HEADER ===== */
.adm-section-header {
    display: flex;
    align-items: baseline;
    justify-content: space-between;
    margin: 50px 0 24px;
    padding-bottom: 16px;
    border-bottom: 2px solid #F1F5F9;
}
.adm-section-title {
    font-size: 1.15rem;
    font-weight: 800;
    color: #0A1F44;
    letter-spacing: -0.02em;
    margin: 0;
    display: flex;
    align-items: center;
    gap: 12px;
}
.adm-section-accent {
    width: 4px; height: 18px;
    background: linear-gradient(180deg, #FF5200, #FF8C42);
    border-radius: 4px;
    display: inline-block;
    flex-shrink: 0;
}
.adm-section-tag {
    font-size: 0.65rem;
    font-weight: 800;
    color: #FF5200;
    text-transform: uppercase;
    letter-spacing: 0.14em;
    background: linear-gradient(135deg, #FFF4EF, #FFE5D6);
    padding: 5px 14px;
    border-radius: 999px;
    border: 1px solid #FFD5BF;
    box-shadow: 0 2px 8px rgba(255,82,0,0.08);
}

/* ===== METRIC CARDS ===== */
.adm-metrics-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 20px;
    margin-bottom: 28px;
}
.adm-metric-card {
    background: rgba(255,255,255,0.8);
    backdrop-filter: blur(16px);
    border: 1px solid #E2E8F0;
    border-radius: 20px;
    padding: 28px 30px;
    position: relative;
    overflow: hidden;
    box-shadow: 0 12px 32px rgba(10,31,68,0.05);
    transition: transform 0.3s ease, box-shadow 0.3s ease, border-color 0.3s ease;
}
.adm-metric-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 20px 48px rgba(10,31,68,0.1);
    border-color: #CBD5E1;
}
.adm-metric-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 4px;
    background: linear-gradient(90deg, #FF5200, #FF8C42);
    opacity: 0.9;
}
.adm-metric-label {
    font-size: 0.7rem;
    font-weight: 800;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    color: #64748B;
    margin-bottom: 12px;
    display: block;
}
.adm-metric-val {
    font-size: 2.8rem;
    font-weight: 900;
    color: #0A1F44;
    letter-spacing: -0.04em;
    line-height: 1;
    display: block;
}
.adm-metric-sub {
    font-size: 0.8rem;
    color: #94A3B8;
    margin-top: 10px;
    font-weight: 600;
    display: block;
}

/* ===== CONTROL CARDS ===== */
.adm-ctrl-card {
    background: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 20px;
    padding: 28px 30px;
    height: 100%;
    box-shadow: 0 8px 24px rgba(15,23,42,0.04);
    transition: border-color 0.3s ease, box-shadow 0.3s ease;
}
.adm-ctrl-card:hover {
    border-color: #CBD5E1;
    box-shadow: 0 16px 36px rgba(15,23,42,0.08);
}
.adm-ctrl-title {
    font-size: 0.85rem;
    font-weight: 800;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: #0A1F44;
    margin: 0 0 8px;
    display: block;
}
.adm-ctrl-desc {
    font-size: 0.85rem;
    color: #64748B;
    font-weight: 500;
    margin: 0 0 22px;
    line-height: 1.6;
    display: block;
}

/* ===== ONLINE USER CARDS ===== */
.adm-user-card {
    display: flex;
    align-items: center;
    gap: 18px;
    padding: 16px 24px;
    border: 1px solid #E2E8F0;
    border-radius: 16px;
    margin-bottom: 12px;
    background: #FFFFFF;
    transition: all 0.2s ease;
    box-shadow: 0 2px 8px rgba(15,23,42,0.02);
}
.adm-user-card:hover {
    border-color: #94A3B8;
    box-shadow: 0 10px 24px rgba(15,23,42,0.06);
    transform: translateX(4px);
}
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
    font-size: 0.8rem;
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
    gap: 6px;
    font-size: 0.72rem;
    font-weight: 800;
    color: #16A34A;
}
.adm-online-dot::before {
    content: '';
    width: 8px; height: 8px;
    border-radius: 50%;
    background: #22C55E;
    flex-shrink: 0;
    box-shadow: 0 0 0 3px rgba(34,197,94,0.2);
}
.adm-user-ts {
    font-size: 0.7rem;
    color: #94A3B8;
    margin-top: 4px;
    font-weight: 600;
}

/* ===== ONLINE COUNT BADGE ===== */
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
    padding: 6px 14px;
    border-radius: 999px;
    vertical-align: middle;
    margin-left: 14px;
    box-shadow: 0 4px 12px rgba(21,128,61,0.1);
}
.adm-online-badge::before {
    content: '';
    width: 8px; height: 8px;
    border-radius: 50%;
    background: #22C55E;
    animation: adm-pulse 2s ease-in-out infinite;
}

/* ===== CLEANUP BOX ===== */
.adm-cleanup-box {
    background: linear-gradient(180deg, #FAFAFA, #FFFFFF);
    border: 1px solid #E2E8F0;
    border-radius: 20px;
    padding: 32px 36px;
    box-shadow: 0 8px 24px rgba(15,23,42,0.04);
}
.adm-cleanup-title {
    font-size: 0.85rem;
    font-weight: 800;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: #0A1F44;
    margin: 0 0 8px;
}
.adm-cleanup-desc {
    font-size: 0.85rem;
    color: #64748B;
    margin: 0 0 24px;
    line-height: 1.6;
    font-weight: 500;
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
            <div class="adm-page-header-content">
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

    col1, col2 = st.columns(2, gap="large")

    with col1:
        st.markdown('<div class="adm-ctrl-card">', unsafe_allow_html=True)
        st.markdown('<span class="adm-ctrl-title">Chế độ Bảo trì</span>', unsafe_allow_html=True)
        st.markdown('<span class="adm-ctrl-desc">Kích hoạt sẽ chặn truy cập toàn bộ tài khoản thường ngay lập tức. Tính năng này dành cho bảo trì khẩn cấp.</span>', unsafe_allow_html=True)
        new_status = st.toggle("Kích hoạt Chế độ Bảo trì", value=is_locked)
        if new_status != is_locked:
            state["is_locked"] = new_status
            save_state(state)
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="adm-ctrl-card">', unsafe_allow_html=True)
        st.markdown('<span class="adm-ctrl-title">Trạng thái Hệ thống</span>', unsafe_allow_html=True)
        st.markdown('<span class="adm-ctrl-desc">Kiểm tra tình trạng kết nối và phục vụ báo cáo hiện tại của toàn bộ Dashboard.</span>', unsafe_allow_html=True)
        if is_locked:
            st.error("ĐANG BẢO TRÌ — Hệ thống đang chặn truy cập bên ngoài.")
        else:
            st.success("HOẠT ĐỘNG BÌNH THƯỜNG — Đang phục vụ toàn bộ người dùng.")
        st.markdown('</div>', unsafe_allow_html=True)

    # ── Section 2: Announcement + AI Config ──────────────────────────────────
    st.markdown("""
    <div class="adm-section-header">
        <h2 class="adm-section-title">
            <span class="adm-section-accent"></span>
            Thông báo &amp; Cấu hình
        </h2>
        <span class="adm-section-tag">Broadcast &amp; Config</span>
    </div>
    """, unsafe_allow_html=True)

    col3, col4 = st.columns(2, gap="large")

    with col3:
        st.markdown('<div class="adm-ctrl-card">', unsafe_allow_html=True)
        st.markdown('<span class="adm-ctrl-title">Thông báo Toàn cục (Banner)</span>', unsafe_allow_html=True)
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
        st.markdown('<div class="adm-ctrl-card">', unsafe_allow_html=True)
        st.markdown('<span class="adm-ctrl-title">Cấu hình AI &amp; Dữ liệu</span>', unsafe_allow_html=True)
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
        st.markdown("""
        <div style="text-align:center;padding:50px 20px;background:rgba(255,255,255,0.6);backdrop-filter:blur(10px);border:1px dashed #CBD5E1;border-radius:16px;color:#94A3B8;margin-top:16px;">
            <p style="font-size:0.95rem;font-weight:600;margin:0;">Hiện không có ai đang trực tuyến trong 10 phút gần nhất.</p>
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
            Lịch sử Đăng nhập
        </h2>
        <span class="adm-section-tag">Access Logs</span>
    </div>
    """, unsafe_allow_html=True)

    # Metric cards
    st.markdown(f"""
    <div class="adm-metrics-grid">
        <div class="adm-metric-card">
            <span class="adm-metric-label">Tổng lượt truy cập</span>
            <span class="adm-metric-val">{total_logins:,}</span>
            <span class="adm-metric-sub">Tất cả thời gian</span>
        </div>
        <div class="adm-metric-card">
            <span class="adm-metric-label">Người dùng duy nhất</span>
            <span class="adm-metric-val">{unique_users:,}</span>
            <span class="adm-metric-sub">Unique email</span>
        </div>
        <div class="adm-metric-card">
            <span class="adm-metric-label">Lượt truy cập hôm nay</span>
            <span class="adm-metric-val">{today_logins:,}</span>
            <span class="adm-metric-sub">{datetime.now().strftime("%d/%m/%Y")}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Data table
    if df_logs.empty:
        st.markdown("""
        <div style="text-align:center;padding:50px 20px;background:rgba(255,255,255,0.6);backdrop-filter:blur(10px);border:1px dashed #CBD5E1;border-radius:16px;color:#94A3B8;">
            <p style="font-size:0.95rem;font-weight:600;margin:0;">Chưa có lịch sử đăng nhập nào được ghi nhận.</p>
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

    # Cleanup section
    st.markdown("""
    <div class="adm-section-header">
        <h2 class="adm-section-title">
            <span class="adm-section-accent"></span>
            Dọn dẹp Log
        </h2>
        <span class="adm-section-tag">VPS Optimization</span>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="adm-cleanup-box">', unsafe_allow_html=True)
    st.markdown('<p class="adm-cleanup-desc">Xóa bớt lịch sử cũ để giữ file nhỏ gọn, tránh làm chậm server. Hệ thống tự động giữ tối đa 5.000 dòng — vượt quá sẽ tự cắt còn 3.000 dòng.</p>', unsafe_allow_html=True)

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
