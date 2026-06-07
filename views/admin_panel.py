import streamlit as st
import json
import os
import csv
import time
from datetime import datetime, timedelta

import pandas as pd

APP_STATE_FILE  = os.path.join("config", "app_state.json")
SESSIONS_FILE   = os.path.join("config", "active_sessions.json")
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
        return '<span style="background:#DC2626;color:white;font-size:0.6rem;font-weight:800;padding:2px 7px;border-radius:4px;letter-spacing:0.05em;">ADMIN</span>'
    return '<span style="background:#3B82F6;color:white;font-size:0.6rem;font-weight:800;padding:2px 7px;border-radius:4px;letter-spacing:0.05em;">USER</span>'

def _avatar_html(name: str, picture: str = "") -> str:
    letter = (name or "?")[0].upper()
    if picture:
        return f'<img src="{picture}" style="width:34px;height:34px;border-radius:50%;object-fit:cover;border:2px solid #E2E8F0;">'
    return f'<div style="width:34px;height:34px;border-radius:50%;background:linear-gradient(135deg,#FF5200,#0A1F44);display:flex;align-items:center;justify-content:center;color:white;font-weight:700;font-size:0.9rem;flex-shrink:0;">{letter}</div>'

def _time_ago(ts_seconds: float) -> str:
    diff = time.time() - ts_seconds
    if diff < 60:
        return "vừa xong"
    elif diff < 3600:
        return f"{int(diff // 60)} phút trước"
    elif diff < 86400:
        return f"{int(diff // 3600)} giờ trước"
    return f"{int(diff // 86400)} ngày trước"


# ─────────────────────────────────────────────────────────────────────────────
# Main Render
# ─────────────────────────────────────────────────────────────────────────────
def render():
    from utils.ai_generator import _get_groq_keys

    st.markdown("""
    <div class="pg-header" style="margin-bottom: 24px; border-bottom: 2px solid #F1F5F9; padding-bottom: 24px;">
        <div>
            <p class="pg-eyebrow" style="color: #64748B; letter-spacing: 0.15em;">SYSTEM ADMINISTRATION</p>
            <h1 class="pg-title" style="color: #0F172A; font-weight: 700; letter-spacing: -0.02em;">Workspace Access Control</h1>
            <p class="pg-subtitle" style="color: #475569; font-size: 0.95rem;">Thiết lập trạng thái hoạt động, phân quyền và theo dõi lưu lượng truy cập.</p>
        </div>
        <span class="pg-badge" style="background: #F8FAFC; color: #475569; border: 1px solid #E2E8F0; border-radius: 4px; font-weight: 600;">
            <span class="pg-badge-dot" style="background: #3B82F6;"></span>Authorized Session
        </span>
    </div>
    """, unsafe_allow_html=True)

    state = load_state()
    is_locked   = state.get("is_locked", False)
    announcement = state.get("announcement", {"active": False, "text": ""})
    ai_config   = state.get("ai_config", {"temperature": 0.3})

    # ── Section 1: Access Control ─────────────────────────────────────────────
    col1, col2 = st.columns([1, 1])

    with col1:
        with st.container(border=True):
            st.markdown("####  Quản lý Truy cập")
            st.caption("Kích hoạt chế độ bảo trì sẽ lập tức chặn quyền truy cập đối với tất cả tài khoản thông thường.")
            new_status = st.toggle("Kích hoạt Chế độ Bảo trì", value=is_locked)
            if new_status != is_locked:
                state["is_locked"] = new_status
                save_state(state)
                st.rerun()

    with col2:
        with st.container(border=True):
            st.markdown("####  Trạng thái Hệ thống")
            st.caption("Tình trạng kết nối và phục vụ báo cáo cho người dùng ngoài.")
            if is_locked:
                st.error("**ĐANG BẢO TRÌ (MAINTENANCE)** - Hệ thống đang chặn truy cập ngoài.")
            else:
                st.success("**HOẠT ĐỘNG BÌNH THƯỜNG (ONLINE)** - Đang phục vụ toàn bộ user.")

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Section 2: Announcement + AI ─────────────────────────────────────────
    col3, col4 = st.columns([1, 1])

    with col3:
        with st.container(border=True):
            st.markdown("####  Thông báo Toàn cục (Banner)")
            st.caption("Cài đặt thông báo nổi bật ở đầu trang của tất cả người dùng.")
            new_ann_text   = st.text_area("Nội dung thông báo", value=announcement.get("text", ""), height=100)
            new_ann_active = st.toggle("Hiển thị Thông báo", value=announcement.get("active", False))
            if st.button("Lưu Thông báo", width='stretch'):
                state["announcement"] = {"text": new_ann_text, "active": new_ann_active}
                save_state(state)
                st.toast("Đã cập nhật thông báo!", icon="")
                st.rerun()

    with col4:
        with st.container(border=True):
            st.markdown("####  Cấu hình & Dữ liệu")
            groq_keys = _get_groq_keys()
            st.caption(f"Trạng thái kết nối Groq API: **{len(groq_keys)} key(s) khả dụng**")
            new_temp = st.slider("Độ sáng tạo AI (Temperature)", 0.0, 1.0, float(ai_config.get("temperature", 0.3)), 0.1)
            st.markdown("<br>", unsafe_allow_html=True)
            c41, c42 = st.columns(2)
            with c41:
                if st.button("Lưu Cấu hình AI", width='stretch'):
                    state["ai_config"] = {"temperature": new_temp}
                    save_state(state)
                    st.toast("Đã lưu cấu hình AI!", icon="")
            with c42:
                if st.button("Làm mới Bộ nhớ đệm", width='stretch'):
                    st.cache_data.clear()
                    st.toast("Đã xóa bộ nhớ đệm thành công!", icon="")

    st.markdown("---")

    # ── Section 3: Ai đang Online ─────────────────────────────────────────────
    sessions = load_active_sessions()
    now = time.time()
    online_users = []
    for token, data in sessions.items():
        last_seen = data.get("last_seen", 0)
        if now - last_seen <= ONLINE_THRESHOLD_SECONDS:
            online_users.append(data)

    online_users.sort(key=lambda x: x.get("last_seen", 0), reverse=True)

    st.markdown(f"""
    <div style="display:flex;align-items:center;gap:12px;margin-bottom:16px;">
        <div>
            <p class="pg-eyebrow" style="margin:0;color:#64748B;letter-spacing:0.15em;">LIVE MONITOR</p>
            <h2 style="margin:0;font-size:1.15rem;font-weight:800;color:#0A1F44;">
                Ai đang xem Dashboard?
                <span style="background:#22C55E;color:white;font-size:0.65rem;font-weight:800;padding:3px 9px;border-radius:20px;margin-left:10px;vertical-align:middle;">
                    {len(online_users)} ONLINE
                </span>
            </h2>
            <p style="margin:4px 0 0;font-size:0.78rem;color:#94A3B8;">Tài khoản hoạt động trong 10 phút gần nhất · Dữ liệu từ Active Sessions</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    col_ref, _ = st.columns([1, 5])
    with col_ref:
        if st.button("🔄 Làm mới", key="refresh_online"):
            st.rerun()

    if not online_users:
        st.info("Hiện không có ai đang trực tuyến (trong 10 phút gần nhất).")
    else:
        # Vẽ từng user card
        for user in online_users:
            u_email   = user.get("email", "")
            u_name    = user.get("name", u_email)
            u_picture = user.get("picture", "")
            u_auth    = user.get("authorization", {})
            u_role    = u_auth.get("role", "User") if isinstance(u_auth, dict) else "User"
            u_last    = user.get("last_seen", 0)
            avatar    = _avatar_html(u_name, u_picture)
            badge     = _role_badge_html(u_role)
            ago       = _time_ago(u_last)
            ts_str    = datetime.fromtimestamp(u_last).strftime("%H:%M:%S %d/%m/%Y") if u_last else "—"

            st.markdown(f"""
            <div style="display:flex;align-items:center;gap:14px;padding:12px 18px;border:1px solid #E2E8F0;border-radius:10px;margin-bottom:8px;background:#FAFAFA;">
                {avatar}
                <div style="flex:1;min-width:0;">
                    <div style="display:flex;align-items:center;gap:8px;flex-wrap:wrap;">
                        <span style="font-weight:700;font-size:0.88rem;color:#0A1F44;">{u_name}</span>
                        {badge}
                        <span style="font-size:0.72rem;color:#94A3B8;margin-left:auto;">Hoạt động: {ago}</span>
                    </div>
                    <div style="font-size:0.75rem;color:#64748B;margin-top:2px;">{u_email}</div>
                </div>
                <div style="text-align:right;flex-shrink:0;">
                    <div style="display:flex;align-items:center;gap:5px;">
                        <span style="width:7px;height:7px;background:#22C55E;border-radius:50%;display:inline-block;"></span>
                        <span style="font-size:0.7rem;color:#22C55E;font-weight:700;">Online</span>
                    </div>
                    <div style="font-size:0.68rem;color:#CBD5E1;margin-top:2px;">{ts_str}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("---")

    # ── Section 4: Access Logs ────────────────────────────────────────────────
    df_logs = load_access_logs()
    total_logins  = len(df_logs)
    unique_users  = df_logs["email"].nunique() if not df_logs.empty else 0
    today_str     = datetime.now().strftime("%Y-%m-%d")
    if not df_logs.empty and "timestamp" in df_logs.columns:
        today_logins = int(df_logs["timestamp"].dt.strftime("%Y-%m-%d").eq(today_str).sum())
    else:
        today_logins = 0

    st.markdown("""
    <div style="margin-bottom:16px;">
        <p class="pg-eyebrow" style="margin:0;color:#64748B;letter-spacing:0.15em;">ACCESS LOGS</p>
        <h2 style="margin:0;font-size:1.15rem;font-weight:800;color:#0A1F44;">Lịch sử Đăng nhập</h2>
        <p style="margin:4px 0 0;font-size:0.78rem;color:#94A3B8;">Ghi nhận mỗi lần đăng nhập thành công vào hệ thống</p>
    </div>
    """, unsafe_allow_html=True)

    # Metrics
    m1, m2, m3 = st.columns(3)
    m1.metric("Tổng lượt truy cập", f"{total_logins:,}")
    m2.metric("Người dùng duy nhất (Unique)", f"{unique_users:,}")
    m3.metric("Lượt truy cập hôm nay", f"{today_logins:,}")

    st.markdown("<br>", unsafe_allow_html=True)

    # Hiển thị bảng logs
    if df_logs.empty:
        st.info("Chưa có lịch sử đăng nhập nào được ghi nhận.")
    else:
        display_df = df_logs.copy()
        if "timestamp" in display_df.columns:
            display_df["timestamp"] = display_df["timestamp"].dt.strftime("%H:%M:%S %d/%m/%Y")
        display_df.columns = [
            c.replace("timestamp", "Thời gian")
             .replace("email", "Email")
             .replace("name", "Tên")
             .replace("role", "Role")
             .replace("login_method", "Phương thức")
            for c in display_df.columns
        ]
        st.dataframe(
            display_df.head(200),
            use_container_width=True,
            hide_index=True,
        )

        # Download
        csv_bytes = df_logs.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="⬇ Tải về CSV",
            data=csv_bytes,
            file_name=f"access_logs_{today_str}.csv",
            mime="text/csv",
            key="dl_logs",
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # Cleanup controls
    with st.container(border=True):
        st.markdown("#### 🗑️  Dọn dẹp Log (Giảm tải VPS)")
        st.caption("Xóa bớt lịch sử cũ để giữ file nhỏ gọn, tránh nặng server.")

        c_clean1, c_clean2 = st.columns(2)

        with c_clean1:
            days_keep = st.number_input(
                "Giữ lại log trong bao nhiêu ngày gần đây?",
                min_value=1, max_value=365, value=30, step=1,
                help="Các dòng cũ hơn số ngày này sẽ bị xóa"
            )
            if st.button(f"🧹 Xóa log cũ hơn {days_keep} ngày", width='stretch'):
                if not df_logs.empty and "timestamp" in df_logs.columns:
                    cutoff = datetime.now() - timedelta(days=int(days_keep))
                    kept = df_logs[df_logs["timestamp"] >= cutoff]
                    kept.to_csv(ACCESS_LOGS_FILE, index=False, encoding="utf-8")
                    removed = len(df_logs) - len(kept)
                    st.toast(f"Đã xóa {removed:,} dòng log cũ. Còn lại: {len(kept):,} dòng.", icon="🧹")
                    st.rerun()
                else:
                    st.toast("File log trống, không cần xóa.", icon="✅")

        with c_clean2:
            st.markdown("<br>", unsafe_allow_html=True)
            if "confirm_clear_all" not in st.session_state:
                st.session_state.confirm_clear_all = False

            if not st.session_state.confirm_clear_all:
                if st.button("🗑️ Xóa TOÀN BỘ log", type="secondary", width='stretch'):
                    st.session_state.confirm_clear_all = True
                    st.rerun()
            else:
                st.warning("⚠️ Bạn chắc chắn muốn xóa **toàn bộ** lịch sử? Hành động này không thể hoàn tác!")
                cc1, cc2 = st.columns(2)
                with cc1:
                    if st.button("✅ Xác nhận Xóa tất cả", type="primary", width='stretch'):
                        try:
                            os.remove(ACCESS_LOGS_FILE)
                        except FileNotFoundError:
                            pass
                        st.session_state.confirm_clear_all = False
                        st.toast("Đã xóa toàn bộ lịch sử truy cập!", icon="🗑️")
                        st.rerun()
                with cc2:
                    if st.button("❌ Huỷ bỏ", width='stretch'):
                        st.session_state.confirm_clear_all = False
                        st.rerun()
