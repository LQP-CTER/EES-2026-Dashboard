import streamlit as st
from views.map_helper import create_vietnam_map
import base64
import os
from shared.plotly_theme import apply_theme


def get_base64_image(filename):
    base_path = os.path.join(os.path.dirname(__file__), '..', 'img', 'EES2026')
    path = os.path.join(base_path, filename)
    try:
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    except Exception:
        return ""


def render():
    apply_theme()

    # ── Cloudinary assets ────────────────────────────────────────────────────
    img1 = "https://res.cloudinary.com/dd7gti2kn/image/upload/v1780393860/LOGO%20GHN/EES_2026_-_CPO_ngang_ayvreb.png"
    img2 = "https://res.cloudinary.com/dd7gti2kn/image/upload/v1780393847/LOGO%20GHN/CPO_kick-off_1_edlqb4.png"
    img3 = "https://res.cloudinary.com/dd7gti2kn/image/upload/v1780393855/LOGO%20GHN/EES_2026_-_GDV_a_Vu%CC%83_ew1dix.png"
    img4 = "https://res.cloudinary.com/dd7gti2kn/image/upload/v1780392210/LOGO%20GHN/Mr_Nguye%CC%82%CC%83n_Va%CC%82n_Ta%CC%82n_Regional_Director_Gia%CC%81m_%C4%90o%CC%82%CC%81c_Vu%CC%80ng_rbzjr3.png"

    main_video_url = "https://res.cloudinary.com/dd7gti2kn/video/upload/v1780395113/LOGO%20GHN/IMG_0734_nhqt02.mp4"
    highlight_url = "https://res.cloudinary.com/dd7gti2kn/video/upload/v1780389451/LOGO%20GHN/Action_video_dgq3f7.mp4"
    playlist = [
        (main_video_url, "Nhìn lại EES 2025"),
        ("https://res.cloudinary.com/dd7gti2kn/video/upload/v1780393976/LOGO%20GHN/IMG_1233_wgzajm.mp4", "Giới thiệu EES 2026"),
        ("https://res.cloudinary.com/dd7gti2kn/video/upload/v1780393954/LOGO%20GHN/IMG_1232_ykz6pz.mp4", "EES Race 2026"),
        (highlight_url, "Highlight"),
        ("https://res.cloudinary.com/dd7gti2kn/video/upload/v1780393907/LOGO%20GHN/IMG_1723_gdh1gs.mp4", "EES 2026 Vinh danh")
    ]

    # ── Global page CSS (no video rules here) ────────────────────────────────
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:ital,wght@0,400;0,600;0,800;0,900;1,400;1,600;1,800;1,900&display=swap');
    
    /* Override for the whole page */
    html, body, [class*="st-"], .ed-container * {
        font-family: 'Montserrat', sans-serif !important;
    }
    </style>

    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');

    .ed-container { font-family:'Montserrat', sans-serif; color:#0A1F44; max-width:1200px; }

    /* Hero */
    .ed-hero { margin-bottom: 52px; }
    .ed-kicker {
        font-size:.72rem; font-weight:800; letter-spacing:.18em;
        text-transform:uppercase; color:#FF5200; margin-bottom:14px; display:block;
    }
    .ed-headline {
        font-size:3.2rem; font-weight:900; letter-spacing:-.03em;
        line-height:1.08; margin:0 0 36px; color:#0A1F44;
    }

    /* Metric cards */
    .ed-metrics-grid {
        display:grid; grid-template-columns:repeat(4,1fr);
        gap:16px; padding-top:36px; border-top:2px solid #E2E8F0;
    }
    .ed-metric-item {
        background:#F8FAFC; border:1px solid #E2E8F0; border-radius:16px;
        padding:20px 24px 22px; display:flex; flex-direction:column;
        position:relative; overflow:hidden;
    }
    .ed-metric-item::before {
        content:''; position:absolute; top:0; left:0; right:0; height:3px;
        background:linear-gradient(90deg,#FF5200,#FF8C42);
        border-radius:16px 16px 0 0;
    }
    .ed-metric-label {
        font-size:.7rem; font-weight:700; text-transform:uppercase;
        letter-spacing:.1em; color:#94A3B8; margin-bottom:10px;
    }
    .ed-metric-val {
        font-size:2.4rem; font-weight:900; color:#0A1F44;
        letter-spacing:-.03em; line-height:1;
    }
    .ed-metric-sub { font-size:.78rem; color:#64748B; margin-top:8px; font-weight:600; }
    .ed-metric-sub.positive { color:#10B981; }

    /* Section header */
    .ed-section-header {
        display:flex; align-items:baseline; justify-content:space-between;
        margin-bottom:24px; margin-top:52px;
    }
    .ed-section-title {
        font-size:2rem; font-weight:900; letter-spacing:-.03em; color:#0A1F44; margin:0;
    }
    .ed-section-tag {
        font-size:.72rem; font-weight:800; color:#FF5200; text-transform:uppercase;
        letter-spacing:.15em; background:#FFF4EF; padding:4px 12px;
        border-radius:999px; border:1px solid #FFD5BF;
    }

    /* Masonry */
    .ed-masonry {
        display:grid; grid-template-columns:repeat(4,1fr);
        grid-auto-rows:210px; gap:16px; margin-bottom:72px;
    }
    .ed-masonry-item { border-radius:16px; overflow:hidden; position:relative; background:#F1F5F9; }
    .ed-masonry-item img { width:100%; height:100%; object-fit:cover; transition:transform .7s cubic-bezier(.4,0,.2,1); }
    .ed-masonry-item:hover img { transform:scale(1.06); }
    .ed-masonry-overlay {
        position:absolute; inset:0;
        background:linear-gradient(to top,rgba(10,31,68,.75) 0%,transparent 55%);
        opacity:0; transition:opacity .4s ease;
    }
    .ed-masonry-item:hover .ed-masonry-overlay { opacity:1; }
    .ed-masonry-caption {
        position:absolute; bottom:18px; left:18px; z-index:2; color:#fff;
        font-weight:700; font-size:1rem; opacity:0; transform:translateY(10px);
        transition:all .4s ease;
    }
    .ed-masonry-item:hover .ed-masonry-caption { opacity:1; transform:translateY(0); }
    .ed-masonry-item-large { grid-column:span 2; grid-row:span 2; }
    .ed-masonry-item-tall  { grid-row:span 2; }
    .ed-masonry-item-wide  { grid-column:span 2; }

    /* Timeline */
    .ed-timeline-section {
        display:grid; grid-template-columns:1fr 2fr; gap:72px;
        padding:72px 0; border-top:2px solid #F1F5F9; margin-bottom:72px;
    }
    .ed-timeline-left h2 {
        font-size:3rem; font-weight:900; line-height:1.08; margin:0 0 20px;
        letter-spacing:-.04em; color:#0A1F44;
    }
    .ed-timeline-left p { color:#64748B; font-size:1.05rem; line-height:1.7; font-weight:500; margin:0; }
    .ed-timeline-right { display:flex; flex-direction:column; gap:44px; padding-top:8px; }
    .ed-timeline-node { display:flex; gap:32px; align-items:flex-start; }
    .ed-timeline-big-num {
        font-size:3.8rem; font-weight:900; color:#FF5200; line-height:.85;
        letter-spacing:-.04em; min-width:130px; text-align:right; flex-shrink:0;
        word-break:keep-all; white-space:nowrap;
    }
    .ed-timeline-content h4 {
        font-size:1.4rem; font-weight:800; margin:0 0 10px;
        color:#0A1F44; letter-spacing:-.02em;
    }
    .ed-timeline-content p { font-size:1rem; color:#64748B; line-height:1.65; margin:0; }

    /* Team */
    .ed-team-section {
        padding:34px;
        margin-bottom:90px;
        border-radius:28px;
        background:
            radial-gradient(circle at 10% 0%, rgba(255,82,0,.12), transparent 32%),
            linear-gradient(135deg, #FFFFFF 0%, #F8FAFC 58%, #EEF6FF 100%);
        border:1px solid rgba(226,232,240,.95);
        box-shadow:0 24px 64px rgba(10,31,68,.11), inset 0 1px 0 rgba(255,255,255,.96);
    }
    .ed-team-grid { display:grid; grid-template-columns:repeat(4,1fr); gap:18px; margin-top:28px; perspective:1100px; }
    .ed-team-card {
        background:rgba(255,255,255,.84); backdrop-filter:blur(14px);
        border:1.5px solid #E2E8F0; border-radius:22px;
        padding:24px; transition:box-shadow .3s ease, transform .3s ease, border-color .3s ease;
        position:relative; overflow:hidden;
    }
    .ed-team-card::before {
        content:''; position:absolute; inset:0 0 auto 0; height:4px;
        background:linear-gradient(90deg,#FF5200,#0052CC);
    }
    .ed-team-card:hover { box-shadow:0 20px 48px rgba(10,31,68,.14); transform:translateY(-8px) translateZ(32px) rotateX(2deg); border-color:rgba(255,82,0,.32); }
    .ed-team-avatar {
        width:46px; height:46px; border-radius:16px;
        display:flex; align-items:center; justify-content:center;
        color:#fff; font-weight:900; font-size:.95rem;
        background:linear-gradient(145deg,#0A1F44,#0052CC);
        box-shadow:0 14px 24px rgba(10,31,68,.18);
        margin-bottom:18px;
    }
    .ed-team-role { font-size:.68rem; font-weight:800; text-transform:uppercase; letter-spacing:.14em; color:#FF5200; margin-bottom:8px; }
    .ed-team-name { font-size:1.25rem; font-weight:800; color:#0A1F44; letter-spacing:-.02em; margin-bottom:10px; }
    .ed-team-desc { font-size:.9rem; color:#64748B; line-height:1.6; }
    .ed-team-badge {
        display:inline-block; margin-top:14px; font-size:.72rem; font-weight:700;
        color:#0A1F44; background:#F1F5F9; padding:3px 10px; border-radius:999px;
    }

    /* 3D Overview refresh */
    .ed-container {
        margin:0 auto;
        perspective:1200px;
    }
    .ed-hero {
        margin-bottom:52px;
        position:relative;
    }
    .ed-hero-shell {
        position:relative;
        overflow:hidden;
        border-radius:28px;
        padding:42px;
        min-height:430px;
        background:
            radial-gradient(circle at 86% 18%, rgba(255,82,0,.20), transparent 30%),
            linear-gradient(135deg, #FFFFFF 0%, #F8FAFC 46%, #EEF6FF 100%);
        border:1px solid rgba(148,163,184,.30);
        box-shadow:
            0 28px 70px rgba(10,31,68,.16),
            inset 0 1px 0 rgba(255,255,255,.95);
        display:grid;
        grid-template-columns:minmax(0,1.1fr) minmax(360px,.9fr);
        gap:34px;
        transform-style:preserve-3d;
    }
    .ed-hero-shell::before {
        content:'';
        position:absolute;
        inset:18px;
        border:1px solid rgba(255,255,255,.72);
        border-radius:22px;
        pointer-events:none;
    }
    .ed-hero-shell::after {
        content:'';
        position:absolute;
        width:420px;
        height:420px;
        right:-160px;
        bottom:-190px;
        background:conic-gradient(from 160deg, rgba(255,82,0,.34), rgba(0,82,204,.20), rgba(16,185,129,.18), rgba(255,82,0,.34));
        filter:blur(8px);
        opacity:.78;
        border-radius:50%;
        transform:translateZ(-40px);
    }
    .ed-hero-copy {
        position:relative;
        z-index:2;
        transform:translateZ(44px);
    }
    .ed-kicker {
        display:inline-flex;
        align-items:center;
        gap:8px;
        width:max-content;
        padding:7px 12px;
        border-radius:999px;
        background:#FFF4EF;
        border:1px solid #FFD5BF;
        box-shadow:0 10px 24px rgba(255,82,0,.10);
    }
    .ed-kicker::before {
        content:'';
        width:8px;
        height:8px;
        border-radius:50%;
        background:#10B981;
        box-shadow:0 0 0 5px rgba(16,185,129,.14);
    }
    .ed-headline {
        max-width:760px;
        margin-top:22px;
        margin-bottom:18px;
        font-size:3.45rem;
    }
    .ed-hero-sub {
        max-width:620px;
        color:#475569;
        font-size:1.02rem;
        line-height:1.72;
        font-weight:600;
        margin:0 0 28px;
    }
    .ed-metrics-grid {
        border-top:0;
        padding-top:0;
        grid-column:1 / -1;
        position:relative;
        z-index:4;
        grid-template-columns:repeat(4,minmax(0,1fr));
        gap:18px;
        max-width:none;
        width:100%;
    }
    .ed-metric-item {
        background:rgba(255,255,255,.78);
        backdrop-filter:blur(16px);
        border:1px solid rgba(226,232,240,.95);
        border-radius:18px;
        min-width:0;
        padding:20px 24px 22px;
        overflow:visible;
        box-shadow:0 18px 34px rgba(10,31,68,.10);
        transform:translateZ(28px);
        transition:transform .28s ease, box-shadow .28s ease, border-color .28s ease;
    }
    .ed-metric-label {
        min-height:32px;
        line-height:1.35;
    }
    .ed-metric-val {
        display:block;
        white-space:nowrap;
        word-break:keep-all;
        overflow-wrap:normal;
        font-size:clamp(2rem, 2.45vw, 2.55rem);
        line-height:.95;
        letter-spacing:-.04em;
        font-variant-numeric:tabular-nums;
    }
    .ed-metric-sub {
        line-height:1.45;
    }
    .ed-metric-item:hover {
        transform:translateY(-6px) translateZ(52px) rotateX(2deg);
        box-shadow:0 26px 52px rgba(10,31,68,.16);
        border-color:rgba(255,82,0,.34);
    }
    .ed-command-panel {
        position:relative;
        z-index:2;
        min-height:340px;
        align-self:stretch;
        border-radius:24px;
        padding:26px;
        background:linear-gradient(145deg, rgba(10,31,68,.96), rgba(0,82,204,.82));
        box-shadow:
            0 28px 58px rgba(10,31,68,.28),
            inset 0 1px 0 rgba(255,255,255,.18);
        overflow:hidden;
        transform:rotateY(-8deg) rotateX(4deg) translateZ(36px);
        transform-origin:center;
    }
    .ed-command-panel::before {
        content:'';
        position:absolute;
        inset:0;
        background:
            linear-gradient(rgba(255,255,255,.065) 1px, transparent 1px),
            linear-gradient(90deg, rgba(255,255,255,.055) 1px, transparent 1px);
        background-size:32px 32px;
        mask-image:linear-gradient(to bottom, black, transparent 92%);
    }
    .ed-command-top {
        position:relative;
        z-index:2;
        display:flex;
        justify-content:space-between;
        align-items:flex-start;
        color:#fff;
    }
    .ed-command-label {
        display:block;
        font-size:.68rem;
        font-weight:800;
        letter-spacing:.16em;
        text-transform:uppercase;
        color:#FFD5BF;
        margin-bottom:10px;
    }
    .ed-command-score {
        font-size:4.3rem;
        line-height:.9;
        font-weight:900;
        letter-spacing:-.05em;
    }
    .ed-command-unit {
        font-size:.78rem;
        color:rgba(255,255,255,.68);
        font-weight:700;
        margin-top:8px;
    }
    .ed-command-chip {
        color:#fff;
        border:1px solid rgba(255,255,255,.24);
        background:rgba(255,255,255,.10);
        border-radius:999px;
        padding:7px 11px;
        font-size:.72rem;
        font-weight:800;
        backdrop-filter:blur(12px);
    }
    /* ── Pillar tags — replaces orbit/pills ── */
    .ed-pillars {
        position:absolute;
        left:26px;
        right:26px;
        bottom:28px;
        display:flex;
        flex-direction:column;
        gap:6px;
    }
    .ed-pillar-row {
        display:flex;
        gap:6px;
    }
    .ed-pillar-tag {
        display:inline-flex;
        align-items:center;
        gap:5px;
        padding:5px 10px;
        border-radius:999px;
        color:rgba(255,255,255,.90);
        background:rgba(255,255,255,.10);
        border:1px solid rgba(255,255,255,.18);
        font-size:.62rem;
        font-weight:700;
        letter-spacing:.01em;
        backdrop-filter:blur(10px);
        white-space:nowrap;
    }
    .ed-pillar-tag::before {
        content:'';
        width:6px;
        height:6px;
        border-radius:50%;
        background:#FF5200;
        flex-shrink:0;
    }
    .ed-pillar-divider {
        height:1px;
        background:rgba(255,255,255,.12);
        margin:4px 0 2px;
    }
    /* ── Bar chart — right side ── */
    .ed-command-bars {
        position:absolute;
        right:26px;
        bottom:116px;
        z-index:2;
        display:flex;
        align-items:flex-end;
        gap:8px;
        height:80px;
    }
    .ed-command-bars span {
        width:14px;
        border-radius:999px 999px 4px 4px;
        background:linear-gradient(180deg,#FFFFFF,#FFD5BF 42%,#FF5200);
        opacity:.88;
        box-shadow:0 8px 14px rgba(0,0,0,.18);
    }
    .ed-command-bars span:nth-child(1) { height:32px; }
    .ed-command-bars span:nth-child(2) { height:56px; }
    .ed-command-bars span:nth-child(3) { height:42px; }
    .ed-command-bars span:nth-child(4) { height:72px; }

    @media (max-width: 1080px) {
        .ed-hero-shell { grid-template-columns:1fr; padding:32px; }
        .ed-command-panel { transform:translateZ(24px); min-height:320px; }
        .ed-metrics-grid { grid-template-columns:repeat(2,minmax(0,1fr)); }
        .ed-team-grid { grid-template-columns:repeat(2,1fr); }
    }
    @media (max-width: 760px) {
        .ed-hero-shell { padding:24px; border-radius:22px; }
        .ed-headline { font-size:2.35rem; }
        .ed-metrics-grid { grid-template-columns:1fr; max-width:none; }
        .ed-command-panel { display:none; }
        .ed-team-grid { grid-template-columns:1fr; }
    }
    </style>
    """, unsafe_allow_html=True)

    def _jt_icon(kind: str) -> str:
        icons = {
            "kickoff": '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M13.5 4.5 19 10l-5.5 5.5"/><path d="M19 10H5"/><path d="M8 14.5 5 18v-3.5"/></svg>',
            "scan": '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M7 4.5h10a1.5 1.5 0 0 1 1.5 1.5v12A1.5 1.5 0 0 1 17 19.5H7A1.5 1.5 0 0 1 5.5 18V6A1.5 1.5 0 0 1 7 4.5Z"/><path d="M9 8h6M9 12h6M9 16h4"/></svg>',
            "gear": '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 8.5a3.5 3.5 0 1 0 0 7 3.5 3.5 0 0 0 0-7Z"/><path d="M12 3.5v2.2M12 18.3v2.2M4.7 12H2.5M21.5 12h-2.2M6.1 6.1 4.6 4.6M19.4 19.4l-1.5-1.5M17.9 6.1l1.5-1.5M6.1 17.9l-1.5 1.5"/><path d="M12 5.7a6.3 6.3 0 1 1 0 12.6 6.3 6.3 0 0 1 0-12.6Z"/></svg>',
            "report": '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M7 3.5h7l3.5 3.5V20.5H7z"/><path d="M14 3.5V7h3.5"/><path d="M9 11h6M9 14.5h6M9 18h4"/></svg>',
        }
        return icons.get(kind, icons["report"])

    # ── 1. HERO (stats) ──────────────────────────────────────────────────────
    st.markdown("""
    <div class="ed-container">
        <div class="ed-hero">
            <div class="ed-hero-shell">
                <div class="ed-hero-copy">
                    <span class="ed-kicker">Employee Engagement Survey 2026</span>
                    <h1 class="ed-headline">Hành trình EES 2026 - Phía sau những con số</h1>
                    <p class="ed-hero-sub">Một lớp tổng quan điều hành về quy mô triển khai, chất lượng dữ liệu và những nguyên tắc được áp dụng để đảm bảo kết quả EES 2026 phản ánh trung thực tiếng nói của nhân viên GHN.</p>
                </div>
                <div class="ed-command-panel">
                    <div class="ed-command-top">
                        <div>
                            <span class="ed-command-label">Engagement Intelligence</span>
                            <div class="ed-command-score">73.3</div>
                            <div class="ed-command-unit">EI score · Validated dataset</div>
                        </div>
                        <span class="ed-command-chip">Live Overview</span>
                    </div>
                    <div class="ed-command-bars">
                        <span></span><span></span><span></span><span></span>
                    </div>
                    <div class="ed-pillars">
                        <div class="ed-pillar-divider"></div>
                        <div class="ed-pillar-row">
                            <span class="ed-pillar-tag">Niềm tin lãnh đạo</span>
                            <span class="ed-pillar-tag">Quản lý trực tiếp</span>
                        </div>
                        <div class="ed-pillar-row">
                            <span class="ed-pillar-tag">Công việc &amp; phát triển</span>
                            <span class="ed-pillar-tag">Thu nhập &amp; minh bạch</span>
                        </div>
                        <div class="ed-pillar-row">
                            <span class="ed-pillar-tag">Môi trường &amp; phát triển</span>
                        </div>
                    </div>
                </div>
                <div class="ed-metrics-grid">
                    <div class="ed-metric-item">
                        <span class="ed-metric-label">Quy mô</span>
                        <span class="ed-metric-val">21,353</span>
                        <span class="ed-metric-sub">Nhân sự toàn GHN</span>
                    </div>
                    <div class="ed-metric-item">
                        <span class="ed-metric-label">Phản hồi</span>
                        <span class="ed-metric-val">20,005</span>
                        <span class="ed-metric-sub">Phản hồi thu thập</span>
                    </div>
                    <div class="ed-metric-item">
                        <span class="ed-metric-label">Tỷ lệ tham gia</span>
                        <span class="ed-metric-val">93.7%</span>
                        <span class="ed-metric-sub positive">▲ +17.8% so với 2025</span>
                    </div>
                    <div class="ed-metric-item">
                        <span class="ed-metric-label">Mức gắn kết</span>
                        <span class="ed-metric-val">73.3</span>
                        <span class="ed-metric-sub">Điểm EI tổng thể</span>
                    </div>
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── 2. VIDEO SECTION ─────────────────────────────────────────────────────
    # Playlist is defined above

    dock_cards = ""
    for i, (url, label) in enumerate(playlist):
        active = "dock-card-active" if i == 0 else ""
        dock_cards += f"""
        <div class="dock-card {active}" data-src="{url}" data-label="{label}">
            <video class="dock-video" muted loop playsinline preload="metadata">
                <source src="{url}" type="video/mp4">
            </video>
            <div class="dock-card-scrim"></div>
            <div class="dock-eq"><span></span><span></span><span></span></div>
            <span class="dock-card-title">{label}</span>
        </div>"""

    video_html = f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{
    font-family: 'Montserrat', sans-serif;
    background: transparent;
    padding: 4px 8px 28px;
  }}

  .video-stage {{
    position: relative;
    padding: 28px;
    border-radius: 28px;
    background:
      radial-gradient(circle at 88% 20%, rgba(255,82,0,.16), transparent 28%),
      linear-gradient(135deg, #FFFFFF 0%, #F8FAFC 54%, #EEF6FF 100%);
    border: 1px solid rgba(148,163,184,.28);
    box-shadow: 0 24px 64px rgba(10,31,68,.12), inset 0 1px 0 rgba(255,255,255,.95);
    overflow: visible;
  }}
  .video-stage::before {{
    content: '';
    position: absolute;
    inset: 14px;
    border-radius: 22px;
    border: 1px solid rgba(255,255,255,.72);
    pointer-events: none;
  }}

  /* ── Section header ── */
  .section-header {{
    position: relative;
    z-index: 2;
    display: flex; align-items: center; justify-content: space-between;
    margin-bottom: 20px;
  }}
  .section-title {{
    font-size: 1.6rem; font-weight: 900; color: #0A1F44; letter-spacing: -0.03em;
  }}
  .section-tag {{
    font-size: 0.68rem; font-weight: 800; color: #FF5200;
    text-transform: uppercase; letter-spacing: 0.15em;
    background: #FFF4EF; padding: 4px 12px; border-radius: 999px;
    border: 1px solid #FFD5BF;
  }}

  /* ── Cinematic player shell ── */
  .player-shell {{
    position: relative;
    width: 100%;
    aspect-ratio: 21 / 9;
    border-radius: 24px;
    overflow: hidden;
    background: #000;
    box-shadow: 0 30px 74px rgba(10,31,68,.30);
    cursor: pointer;
    transform: perspective(1200px) rotateX(1.2deg);
    transform-origin: center top;
    z-index: 2;
  }}
  .player-shell:hover .ctrl-bar {{ opacity: 1; transform: translateY(0); }}
  .player-shell:hover .unmute-pill {{ opacity: 1; }}

  /* ── Actual video element ── */
  #mainVid {{
    width: 100%; height: 100%;
    object-fit: cover; display: block;
  }}

  /* ── Gradient scrim ── */
  .scrim {{
    position: absolute; inset: 0; pointer-events: none;
    background: linear-gradient(
      180deg,
      rgba(0,0,0,.0)   0%,
      rgba(0,0,0,.0)  55%,
      rgba(0,0,0,.55) 85%,
      rgba(0,0,0,.72) 100%
    );
  }}

  /* ── Big centre play/pause icon (shows briefly on state change) ── */
  .centre-icon {{
    position: absolute; top: 50%; left: 50%;
    transform: translate(-50%,-50%) scale(0);
    width: 72px; height: 72px; border-radius: 50%;
    background: rgba(255,255,255,.18); backdrop-filter: blur(8px);
    display: flex; align-items: center; justify-content: center;
    color: #fff; font-size: 28px;
    transition: transform .15s ease, opacity .3s ease;
    pointer-events: none; opacity: 0;
  }}
  .centre-icon.pop {{
    transform: translate(-50%,-50%) scale(1);
    opacity: 1;
  }}

  /* ── Unmute pill ── */
  .unmute-pill {{
    position: absolute; top: 20px; right: 20px;
    background: rgba(0,0,0,.55); backdrop-filter: blur(10px);
    color: #fff; border-radius: 999px;
    padding: 8px 16px; font-size: .8rem; font-weight: 700;
    display: flex; align-items: center; gap: 8px;
    cursor: pointer; transition: opacity .3s ease, background .2s ease;
    opacity: 0.92; border: 1px solid rgba(255,255,255,.18);
    z-index: 10;
  }}
  .unmute-pill:hover {{ background: rgba(255,82,0,.85); }}
  .unmute-pill svg {{ flex-shrink: 0; }}

  /* ── Control bar ── */
  .ctrl-bar {{
    position: absolute; bottom: 0; left: 0; right: 0;
    padding: 16px 20px 18px 20px;
    display: flex; flex-direction: column; gap: 10px;
    opacity: 0; transform: translateY(6px);
    transition: opacity .3s ease, transform .3s ease;
    z-index: 10;
  }}

  /* Progress track */
  .progress-track {{
    position: relative; width: 100%; height: 4px;
    background: rgba(255,255,255,.25); border-radius: 99px;
    cursor: pointer; transition: height .2s ease;
  }}
  .progress-track:hover {{ height: 6px; }}
  .progress-fill {{
    height: 100%; background: #FF5200; border-radius: 99px;
    width: 0%; pointer-events: none; transition: width .1s linear;
    position: relative;
  }}
  .progress-fill::after {{
    content: ''; position: absolute; right: -5px; top: 50%;
    transform: translateY(-50%);
    width: 12px; height: 12px; border-radius: 50%;
    background: #fff;
    box-shadow: 0 0 4px rgba(0,0,0,.4);
    opacity: 0; transition: opacity .2s ease;
  }}
  .progress-track:hover .progress-fill::after {{ opacity: 1; }}

  /* Bottom row */
  .ctrl-row {{
    display: flex; align-items: center; gap: 14px;
  }}
  .ctrl-btn {{
    background: none; border: none; color: #fff; cursor: pointer;
    padding: 4px; display: flex; align-items: center; justify-content: center;
    opacity: .9; transition: opacity .2s ease, transform .15s ease;
    flex-shrink: 0;
  }}
  .ctrl-btn:hover {{ opacity: 1; transform: scale(1.15); }}

  .time-display {{
    font-size: .78rem; font-weight: 600; color: rgba(255,255,255,.85);
    letter-spacing: .02em; white-space: nowrap;
  }}
  .spacer {{ flex: 1; }}

  /* Volume slider */
  .vol-wrap {{ display: flex; align-items: center; gap: 8px; }}
  .vol-slider {{
    -webkit-appearance: none; appearance: none;
    width: 72px; height: 3px; border-radius: 99px;
    background: rgba(255,255,255,.3); cursor: pointer; outline: none;
  }}
  .vol-slider::-webkit-slider-thumb {{
    -webkit-appearance: none; width: 12px; height: 12px;
    border-radius: 50%; background: #fff; cursor: pointer;
  }}

  /* ── Playlist dock BELOW player ── */
  .dock {{
    position: relative;
    z-index: 3;
    margin-top: 24px;
    display: grid;
    grid-template-columns: repeat(5, 1fr);
    gap: 16px;
    padding-bottom: 4px;
  }}
  @media (max-width: 820px) {{
    .dock {{ grid-template-columns: repeat(3, 1fr); }}
  }}

  .dock-card {{
    position: relative;
    width: 100%;
    aspect-ratio: 16 / 10;
    border-radius: 16px;
    overflow: hidden;
    cursor: pointer;
    background: #0F172A;
    border: 1px solid rgba(255,255,255,.75);
    box-shadow: 0 14px 30px rgba(10,31,68,.12);
    transition: transform .3s cubic-bezier(.4,0,.2,1), box-shadow .3s ease, border-color .3s ease;
  }}
  .dock-card:hover {{
    transform: perspective(900px) translateY(-7px) rotateX(4deg);
    box-shadow: 0 12px 28px rgba(10,31,68,.25);
  }}
  .dock-card-active {{
    border-color: #FF5200;
    box-shadow: 0 0 0 3px rgba(255,82,0,.18), 0 16px 34px rgba(255,82,0,.22);
  }}
  .dock-video {{
    width: 100%; height: 100%; object-fit: cover; display: block;
    filter: brightness(.7);
    transition: filter .35s ease, transform .35s ease;
  }}
  .dock-card:hover .dock-video,
  .dock-card-active .dock-video {{
    filter: brightness(1);
    transform: scale(1.05);
  }}
  .dock-card-scrim {{
    position: absolute; inset: 0; pointer-events: none;
    background: linear-gradient(180deg, transparent 30%, rgba(0,0,0,.85) 100%);
  }}
  .dock-card-title {{
    position: absolute; left: 10px; right: 10px; bottom: 10px;
    font-size: .72rem; font-weight: 700; color: #fff;
    line-height: 1.3;
    text-shadow: 0 1px 4px rgba(0,0,0,.8);
    pointer-events: none;
  }}
  /* Now-playing equalizer bars (active card only) */
  .dock-eq {{
    position: absolute; top: 10px; left: 10px;
    display: none; align-items: flex-end; gap: 2px;
    height: 14px; z-index: 2;
  }}
  .dock-card-active .dock-eq {{ display: flex; }}
  .dock-eq span {{
    width: 3px; background: #FF5200; border-radius: 2px;
    animation: eq 0.9s ease-in-out infinite;
  }}
  .dock-eq span:nth-child(1) {{ height: 6px;  animation-delay: 0s;   }}
  .dock-eq span:nth-child(2) {{ height: 14px; animation-delay: .25s; }}
  .dock-eq span:nth-child(3) {{ height: 9px;  animation-delay: .5s;  }}
  @keyframes eq {{
    0%,100% {{ transform: scaleY(.4); }}
    50%     {{ transform: scaleY(1); }}
  }}

  @media (max-width: 900px) {{
    .video-stage {{ padding: 20px; }}
    .player-shell {{ aspect-ratio: 16 / 9; }}
    .dock {{ grid-template-columns: repeat(2, 1fr); }}
  }}
</style>
</head>
<body>

<div class="video-stage">
<!-- Section header -->
<div class="section-header">
  <span class="section-title">EES 2026 — Highlight Reel</span>
  <span class="section-tag">Video</span>
</div>

<!-- Cinematic player -->
<div class="player-shell" id="playerShell">
  <video id="mainVid" autoplay muted loop playsinline preload="auto">
    <source src="{main_video_url}" type="video/mp4">
  </video>
  <div class="scrim"></div>

  <!-- Unmute pill -->
  <div class="unmute-pill" id="unmutePill" title="Bật / tắt âm thanh">
    <svg id="muteSvg" viewBox="0 0 24 24" fill="white" width="16" height="16">
      <path d="M16.5 12A4.5 4.5 0 0014 7.97v2.21l2.45 2.45c.03-.2.05-.41.05-.63zm2.5 0c0 .94-.2 1.82-.54 2.64l1.51 1.51A8.796 8.796 0 0021 12c0-4.28-2.99-7.86-7-8.77v2.06c2.89.86 5 3.54 5 6.71zM4.27 3L3 4.27 7.73 9H3v6h4l5 5v-6.73l4.25 4.25c-.67.52-1.42.93-2.25 1.18v2.06A8.99 8.99 0 0017.73 18l1.98 2 1.27-1.27L4.27 3zM12 4L9.91 6.09 12 8.18V4z"/>
    </svg>
    <span id="muteLabel">Bật tiếng</span>
  </div>

  <!-- Centre pop icon -->
  <div class="centre-icon" id="centreIcon">
    <svg viewBox="0 0 24 24" fill="white" width="32" height="32" id="centreIconSvg">
      <path d="M8 5v14l11-7z"/>
    </svg>
  </div>

  <!-- Controls -->
  <div class="ctrl-bar" id="ctrlBar">
    <div class="progress-track" id="progressTrack">
      <div class="progress-fill" id="progressFill"></div>
    </div>
    <div class="ctrl-row">
      <!-- Play/Pause -->
      <button class="ctrl-btn" id="playBtn" title="Play / Pause">
        <svg id="playIcon" viewBox="0 0 24 24" fill="white" width="22" height="22">
          <path d="M6 19h4V5H6v14zm8-14v14h4V5h-4z"/>
        </svg>
      </button>
      <!-- Time -->
      <span class="time-display" id="timeDisp">0:00 / 0:00</span>
      <div class="spacer"></div>
      <!-- Volume -->
      <div class="vol-wrap">
        <button class="ctrl-btn" id="volBtn" title="Mute / Unmute">
          <svg id="volIcon" viewBox="0 0 24 24" fill="white" width="20" height="20">
            <path d="M3 9v6h4l5 5V4L7 9H3zm13.5 3A4.5 4.5 0 0014 7.97v8.05c1.48-.73 2.5-2.25 2.5-3.02z"/>
          </svg>
        </button>
        <input type="range" class="vol-slider" id="volSlider" min="0" max="1" step="0.05" value="0.8">
      </div>
      <!-- Fullscreen -->
      <button class="ctrl-btn" id="fsBtn" title="Toàn màn hình">
        <svg viewBox="0 0 24 24" fill="white" width="20" height="20">
          <path d="M7 14H5v5h5v-2H7v-3zm-2-4h2V7h3V5H5v5zm12 7h-3v2h5v-5h-2v3zM14 5v2h3v3h2V5h-5z"/>
        </svg>
      </button>
    </div>
  </div>
</div>

<!-- Playlist dock BELOW player -->
<div class="dock" id="dock">
  {dock_cards}
</div>
</div>

<script>
(function() {{
  const vid     = document.getElementById('mainVid');
  const fill    = document.getElementById('progressFill');
  const track   = document.getElementById('progressTrack');
  const timeD   = document.getElementById('timeDisp');
  const playBtn = document.getElementById('playBtn');
  const playIco = document.getElementById('playIcon');
  const volBtn  = document.getElementById('volBtn');
  const volIco  = document.getElementById('volIcon');
  const volSl   = document.getElementById('volSlider');
  const fsBtn   = document.getElementById('fsBtn');
  const shell   = document.getElementById('playerShell');
  const pill    = document.getElementById('unmutePill');
  const pillLbl = document.getElementById('muteLabel');
  const muteSvg = document.getElementById('muteSvg');
  const centre  = document.getElementById('centreIcon');
  const centreSvg = document.getElementById('centreIconSvg');

  const MUTE_PATH   = "M16.5 12A4.5 4.5 0 0014 7.97v2.21l2.45 2.45c.03-.2.05-.41.05-.63zm2.5 0c0 .94-.2 1.82-.54 2.64l1.51 1.51A8.796 8.796 0 0021 12c0-4.28-2.99-7.86-7-8.77v2.06c2.89.86 5 3.54 5 6.71zM4.27 3L3 4.27 7.73 9H3v6h4l5 5v-6.73l4.25 4.25c-.67.52-1.42.93-2.25 1.18v2.06A8.99 8.99 0 0017.73 18l1.98 2 1.27-1.27L4.27 3zM12 4L9.91 6.09 12 8.18V4z";
  const UNMUTE_PATH = "M3 9v6h4l5 5V4L7 9H3zm13.5 3A4.5 4.5 0 0014 7.97v8.05c1.48-.73 2.5-2.25 2.5-3.02zM18.5 12c0-2.77-1.5-5.18-4-6.32v12.61c2.5-1.13 4-3.54 4-6.29z";

  function fmt(s) {{
    if (isNaN(s)) return '0:00';
    const m = Math.floor(s / 60), sec = Math.floor(s % 60);
    return m + ':' + (sec < 10 ? '0' : '') + sec;
  }}

  function updatePlayIcon(paused) {{
    playIco.querySelector('path').setAttribute('d',
      paused ? 'M8 5v14l11-7z' : 'M6 19h4V5H6v14zm8-14v14h4V5h-4z');
  }}

  function popCentre(paused) {{
    centreSvg.querySelector('path').setAttribute('d',
      paused ? 'M8 5v14l11-7z' : 'M6 19h4V5H6v14zm8-14v14h4V5h-4z');
    centre.classList.add('pop');
    setTimeout(() => centre.classList.remove('pop'), 700);
  }}

  function updateMuteUI(muted) {{
    muteSvg.querySelector('path').setAttribute('d', muted ? MUTE_PATH : UNMUTE_PATH);
    pillLbl.textContent = muted ? 'Bật tiếng' : 'Tắt tiếng';
    volIco.querySelector('path').setAttribute('d', muted ? MUTE_PATH : UNMUTE_PATH);
    volSl.value = muted ? 0 : (vid.volume || 0.8);
  }}

  // Tick
  vid.addEventListener('timeupdate', () => {{
    if (!vid.duration) return;
    const pct = (vid.currentTime / vid.duration) * 100;
    fill.style.width = pct + '%';
    timeD.textContent = fmt(vid.currentTime) + ' / ' + fmt(vid.duration);
  }});

  vid.addEventListener('play',  () => updatePlayIcon(false));
  vid.addEventListener('pause', () => updatePlayIcon(true));

  // Click shell = toggle play
  shell.addEventListener('click', (e) => {{
    if (e.target.closest('.ctrl-bar') || e.target.closest('.unmute-pill')) return;
    if (vid.paused) {{ vid.play().catch(()=>{{}}); popCentre(false); }}
    else            {{ vid.pause(); popCentre(true); }}
  }});

  // Play button
  playBtn.addEventListener('click', (e) => {{
    e.stopPropagation();
    if (vid.paused) vid.play().catch(()=>{{}});
    else vid.pause();
  }});

  // Progress scrub
  track.addEventListener('click', (e) => {{
    const rect = track.getBoundingClientRect();
    const pct = (e.clientX - rect.left) / rect.width;
    vid.currentTime = pct * vid.duration;
  }});

  // Unmute pill
  pill.addEventListener('click', (e) => {{
    e.stopPropagation();
    vid.muted = !vid.muted;
    if (!vid.muted) vid.volume = volSl.value > 0 ? +volSl.value : 0.8;
    updateMuteUI(vid.muted);
  }});

  // Vol button
  volBtn.addEventListener('click', (e) => {{
    e.stopPropagation();
    vid.muted = !vid.muted;
    if (!vid.muted) vid.volume = +volSl.value || 0.8;
    updateMuteUI(vid.muted);
  }});

  // Vol slider
  volSl.addEventListener('input', (e) => {{
    e.stopPropagation();
    vid.volume = +volSl.value;
    vid.muted  = (+volSl.value === 0);
    updateMuteUI(vid.muted);
  }});

  // Fullscreen
  fsBtn.addEventListener('click', (e) => {{
    e.stopPropagation();
    if (document.fullscreenElement) document.exitFullscreen();
    else shell.requestFullscreen().catch(()=>{{}});
  }});

  // Init volume
  vid.volume = 0.8;
  updateMuteUI(true); // starts muted (autoplay requirement)

  // ── Playlist dock ──
  document.querySelectorAll('.dock-card').forEach(card => {{
    const sv = card.querySelector('video');

    // Hover preview (only for non-active cards)
    card.addEventListener('mouseenter', () => {{
      if (!card.classList.contains('dock-card-active')) sv.play().catch(()=>{{}});
    }});
    card.addEventListener('mouseleave', () => {{
      if (!card.classList.contains('dock-card-active')) {{ sv.pause(); sv.currentTime = 0; }}
    }});

    card.addEventListener('click', () => {{
      const newSrc = card.dataset.src;
      const src = vid.querySelector('source');
      if (src && newSrc && src.getAttribute('src') !== newSrc) {{
        const wasMuted = vid.muted;
        vid.pause();
        src.setAttribute('src', newSrc);
        vid.load();
        vid.muted = wasMuted;
        vid.volume = +volSl.value || 0.8;
        vid.play().catch(()=>{{}});
        updateMuteUI(wasMuted);
      }}
      // Reset preview state on all cards, mark this active
      document.querySelectorAll('.dock-card').forEach(c => {{
        c.classList.remove('dock-card-active');
        const v = c.querySelector('video');
        v.pause(); v.currentTime = 0;
      }});
      card.classList.add('dock-card-active');
    }});
  }});
}})();
</script>
</body>
</html>
"""

    import streamlit.components.v1 as components
    components.html(video_html, height=920, scrolling=False)

    # ── 3. GALLERY ───────────────────────────────────────────────────────────
    gallery_images = [
        ("https://res.cloudinary.com/dd7gti2kn/image/upload/v1780541184/LOGO%20GHN/EES_2026_-_Thie%CC%A3%CC%82p_ca%CC%89m_o%CC%9Bn_Final_1_kiihrk.png",        "Thư cảm ơn"),

        ("https://res.cloudinary.com/dd7gti2kn/image/upload/v1780392695/LOGO%20GHN/IMG_1493_ldeq70.jpg",        "Khoảnh khắc hậu trường"),
        (img1,  "Truyền thông EES 2026 — CPO gửi thông điệp"),
        ("https://res.cloudinary.com/dd7gti2kn/image/upload/v1780392212/LOGO%20GHN/EES_GDV_A_Doanh_jj76dm.png", "GDV anh Doanh"),
        (img2,  "CPO Kick-off — Khởi động chiến dịch"),
        (img3,  "Giám đốc vùng — GDV anh Vũ"),
        ("https://res.cloudinary.com/dd7gti2kn/image/upload/v1781173209/LOGO%20GHN/photo_2026-06-11_17-19-05_olthvk.jpg",        "Quà tặng gửi đến các bạn NVPTTT"),
        ("https://res.cloudinary.com/dd7gti2kn/image/upload/v1781173209/LOGO%20GHN/photo_2026-06-11_17-19-11_fqee8q.jpg",        "Tổng kết quà tặng"),

        ("https://res.cloudinary.com/dd7gti2kn/image/upload/v1780392653/LOGO%20GHN/IMG_1490_mky43b.jpg",        "Team tại sự kiện"),
        (img4,  "Giám đốc vùng — Mr. Nguyễn Văn Tân"),
    ]

    # Build carousel (no duplication)
    import json as _json
    _items_data = _json.dumps([{"url": u, "cap": c} for u, c in gallery_images])

    gallery_html = (
        '<!DOCTYPE html><html><head><meta charset="utf-8">'
        '<link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@400;600;700;800;900&display=swap" rel="stylesheet">'
        '<style>'
        '* { box-sizing:border-box; margin:0; padding:0; }'
        "body { font-family:'Montserrat',sans-serif; background:transparent; overflow:hidden; }"
        '.gc-shell { padding:0 4px 8px; }'
        '.gc-header { display:flex; align-items:baseline; justify-content:space-between; margin-bottom:20px; padding:0 2px; }'
        '.gc-title { font-size:2rem; font-weight:900; letter-spacing:-0.03em; color:#0A1F44; }'
        '.gc-tag { font-size:0.72rem; font-weight:800; color:#FF5200; text-transform:uppercase; letter-spacing:0.15em;'
        '  background:#FFF4EF; padding:4px 12px; border-radius:999px; border:1px solid #FFD5BF; }'
        '.gc-stage { position:relative; border-radius:24px;'
        '  background: radial-gradient(circle at 16% 0%,rgba(255,82,0,.10),transparent 28%),'
        '    linear-gradient(135deg,rgba(255,255,255,.95),rgba(248,250,252,.92));'
        '  border:1px solid rgba(226,232,240,.9); box-shadow:0 22px 58px rgba(10,31,68,.10);'
        '  padding:28px 72px; overflow:hidden; }'
        '.gc-viewport { overflow:hidden; width:100%; }'
        '.gc-track { display:flex; gap:20px; transition:transform 0.45s cubic-bezier(0.25,0.8,0.25,1); }'
        '.gc-item { flex:0 0 auto; width:calc((100% - 40px)/3); height:420px; position:relative;'
        '  border-radius:18px; overflow:hidden; cursor:zoom-in;'
        '  box-shadow:0 8px 28px -8px rgba(10,31,68,.22);'
        '  transition:transform 0.35s ease,box-shadow 0.35s ease; }'
        '.gc-item:hover { transform:translateY(-6px) scale(1.012); box-shadow:0 22px 48px -12px rgba(10,31,68,.28); }'
        '.gc-img { width:100%; height:100%; object-fit:cover; display:block; }'
        '.gc-caption { position:absolute; bottom:0; left:0; right:0;'
        '  background:linear-gradient(transparent,rgba(10,31,68,.82));'
        '  color:#fff; padding:32px 16px 14px; font-size:0.82rem; font-weight:600;'
        '  opacity:0; transform:translateY(6px); transition:opacity 0.35s ease,transform 0.35s ease; }'
        '.gc-item:hover .gc-caption { opacity:1; transform:translateY(0); }'
        '.gc-btn { position:absolute; top:50%; transform:translateY(-50%);'
        '  width:48px; height:48px; background:rgba(255,255,255,.95);'
        '  border:1.5px solid rgba(226,232,240,.9); border-radius:50%;'
        '  cursor:pointer; font-size:1.3rem; font-weight:700; color:#0A1F44;'
        '  box-shadow:0 4px 16px rgba(10,31,68,.14);'
        '  transition:background 0.2s,box-shadow 0.2s,transform 0.2s;'
        '  display:flex; align-items:center; justify-content:center; z-index:10; }'
        '.gc-btn:hover { background:#FF5200; color:#fff; box-shadow:0 6px 20px rgba(255,82,0,.35);'
        '  transform:translateY(-50%) scale(1.08); }'
        '.gc-btn.dis { opacity:0.3; pointer-events:none; }'
        '.gc-prev { left:14px; } .gc-next { right:14px; }'
        '.gc-dots { display:flex; justify-content:center; gap:8px; margin-top:16px; }'
        '.gc-dot { width:8px; height:8px; border-radius:50%; background:#CBD5E1;'
        '  cursor:pointer; transition:background 0.25s,transform 0.25s; border:none; }'
        '.gc-dot.on { background:#FF5200; transform:scale(1.35); }'
        '.gc-ctr { text-align:center; margin-top:8px; font-size:0.72rem; font-weight:700; color:#94A3B8; letter-spacing:0.12em; }'
        '.lb { display:none; position:fixed; inset:0; background:rgba(0,0,0,0.93); z-index:9999;'
        '  align-items:center; justify-content:center; flex-direction:column; }'
        '.lb.open { display:flex; }'
        '.lb-inner { position:relative; display:flex; align-items:center; justify-content:center;'
        '  max-width:92vw; max-height:82vh; }'
        '.lb-img { max-width:100%; max-height:82vh; object-fit:contain; border-radius:10px;'
        '  box-shadow:0 32px 80px rgba(0,0,0,0.6); display:block; }'
        '.lb-cap { color:rgba(255,255,255,0.85); font-size:0.88rem; font-weight:600;'
        '  margin-top:16px; text-align:center; max-width:80vw; }'
        '.lb-x { position:fixed; top:20px; right:24px; width:44px; height:44px;'
        '  background:rgba(255,255,255,0.12); border:1.5px solid rgba(255,255,255,0.2);'
        '  border-radius:50%; color:white; font-size:1.4rem; cursor:pointer;'
        '  display:flex; align-items:center; justify-content:center;'
        '  transition:background 0.2s; z-index:10000; }'
        '.lb-x:hover { background:rgba(255,82,0,0.85); }'
        '.lb-arr { position:fixed; top:50%; transform:translateY(-50%);'
        '  width:52px; height:52px; background:rgba(255,255,255,0.12);'
        '  border:1.5px solid rgba(255,255,255,0.2); border-radius:50%;'
        '  color:white; font-size:1.5rem; cursor:pointer;'
        '  display:flex; align-items:center; justify-content:center;'
        '  transition:background 0.2s; z-index:10000; }'
        '.lb-arr:hover { background:rgba(255,82,0,0.85); }'
        '.lb-lft { left:20px; } .lb-rgt { right:20px; }'
        '.lb-counter { position:fixed; bottom:20px; left:50%; transform:translateX(-50%);'
        '  color:rgba(255,255,255,0.55); font-size:0.72rem; font-weight:700; letter-spacing:0.15em; }'
        '</style></head><body>'
        '<div class="gc-shell">'
        '<div class="gc-header">'
        '<span class="gc-title">G\u00f3c nh\u00ecn h\u1eadu tr\u01b0\u1eddng</span>'
        '<span class="gc-tag">\u1ea2nh th\u1ef1c t\u1ebf</span>'
        '</div>'
        '<div class="gc-stage">'
        '<button class="gc-btn gc-prev dis" id="gP" onclick="gM(-1)">&#8592;</button>'
        '<div class="gc-viewport"><div class="gc-track" id="gT"></div></div>'
        '<button class="gc-btn gc-next" id="gN" onclick="gM(1)">&#8594;</button>'
        '</div>'
        '<div class="gc-dots" id="gD"></div>'
        '<div class="gc-ctr" id="gC"></div>'
        '</div>'
        '<div class="lb" id="lb" onclick="lbBg(event)">'
        '  <button class="lb-x" onclick="lbClose()">&#215;</button>'
        '  <button class="lb-arr lb-lft" onclick="lbNav(-1);event.stopPropagation()">&#8592;</button>'
        '  <div class="lb-inner">'
        '    <img class="lb-img" id="lbImg" src="" alt="">'
        '  </div>'
        '  <button class="lb-arr lb-rgt" onclick="lbNav(1);event.stopPropagation()">&#8594;</button>'
        '  <div class="lb-cap" id="lbCap"></div>'
        '  <div class="lb-counter" id="lbN"></div>'
        '</div>'
        '<script>'
        f'var D={_items_data},PER=3,cur=0,lbI=0;'
        'var n=D.length,pages=Math.max(1,n-PER+1);'
        'var T=document.getElementById("gT");'
        'var dEl=document.getElementById("gD");'
        'var cEl=document.getElementById("gC");'
        'var bP=document.getElementById("gP"),bN=document.getElementById("gN");'
        'D.forEach(function(it,idx){'
        '  var el=document.createElement("div"); el.className="gc-item";'
        '  el.innerHTML="<img class=\'gc-img\' src=\'"+(it.url)+"\' loading=\'lazy\'>'
        '    <div class=\'gc-caption\'>"+it.cap+"</div>";'
        '  (function(i){el.onclick=function(){lbOpen(i);};})(idx);'
        '  T.appendChild(el);'
        '});'
        'for(var i=0;i<pages;i++){'
        '  var d=document.createElement("button"); d.className="gc-dot"+(i===0?" on":"");'
        '  d.setAttribute("data-i",i); d.onclick=function(){gTo(+this.getAttribute("data-i"));};'
        '  dEl.appendChild(d);'
        '}'
        'function gTo(idx){'
        '  cur=Math.max(0,Math.min(idx,pages-1));'
        '  var iw=T.children.length>0?T.children[0].getBoundingClientRect().width+20:0;'
        '  T.style.transform="translateX(-"+(cur*iw)+"px)";'
        '  [].forEach.call(dEl.children,function(d,i){d.className="gc-dot"+(i===cur?" on":"");});'
        '  bP.className="gc-btn gc-prev"+(cur===0?" dis":"");'
        '  bN.className="gc-btn gc-next"+(cur>=pages-1?" dis":"");'
        '  cEl.textContent=(Math.min(cur+PER,n))+\" / \"+n+\" ảnh\";'
        '}'
        'function gM(d){gTo(cur+d);}'
        'function lbOpen(i){'
        '  lbI=i; var it=D[i];'
        '  document.getElementById("lbImg").src=it.url;'
        '  document.getElementById("lbCap").textContent=it.cap;'
        '  document.getElementById(\"lbN\").textContent=(i+1)+\" / \"+n;'
        '  document.getElementById("lb").className="lb open";'
        '}'
        'function lbClose(){'
        '  document.getElementById("lb").className="lb";'
        '}'
        'function lbBg(e){'
        '  if(e.target===document.getElementById("lb"))lbClose();'
        '}'
        'function lbNav(dir){'
        '  lbOpen((lbI+dir+n)%n);'
        '}'
        'document.addEventListener("keydown",function(e){'
        '  var o=document.getElementById("lb");'
        '  if(!o.classList.contains("open"))return;'
        '  if(e.key==="Escape")lbClose();'
        '  if(e.key==="ArrowLeft")lbNav(-1);'
        '  if(e.key==="ArrowRight")lbNav(1);'
        '});'
        'gTo(0);'
        '</script></body></html>'
    )
    components.html(gallery_html, height=600, scrolling=False)



    # ── 4. TIMELINE ──────────────────────────────────────────────────────────
    st.markdown("<hr style='border:none;border-top:2px solid #F1F5F9;margin:8px 0 0 0;'>", unsafe_allow_html=True)
    journey_html = """
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@400;600;700;800;900&display=swap" rel="stylesheet">
<style>
* { box-sizing: border-box; margin: 0; padding: 0; }
body { font-family: 'Montserrat', sans-serif; background: transparent; }

.jt-shell {
    border-radius: 28px;
    padding: 34px;
    background:
        radial-gradient(circle at 8% 0%, rgba(255,82,0,.12), transparent 30%),
        radial-gradient(circle at 92% 12%, rgba(0,82,204,.10), transparent 34%),
        linear-gradient(135deg, #FFFFFF 0%, #F8FAFC 56%, #EEF6FF 100%);
    border: 1px solid rgba(226,232,240,.95);
    box-shadow: 0 24px 64px rgba(10,31,68,.11), inset 0 1px 0 rgba(255,255,255,.98);
    overflow: hidden;
}
.jt-section {
    display: grid;
    grid-template-columns: minmax(0, 1fr) minmax(0, 1.08fr);
    gap: 44px;
    padding: 4px 4px 16px 4px;
    align-items: start;
}

/* ── LEFT: Title + stat cards ── */
.jt-left {}
.jt-kicker {
    font-size: 0.7rem; font-weight: 800; letter-spacing: 0.18em;
    text-transform: uppercase; color: #FF5200; margin-bottom: 14px; display: inline-flex;
    background: #FFF4EF; border: 1px solid #FFD5BF; border-radius: 999px;
    padding: 7px 12px;
}
.jt-heading {
    font-size: 3rem; font-weight: 900; line-height: 1.08;
    letter-spacing: -0.04em; color: #0A1F44; margin-bottom: 18px;
}
.jt-sub {
    color: #64748B; font-size: 0.95rem; line-height: 1.75;
    font-weight: 500; margin-bottom: 36px;
}

/* 2×2 stat grid */
.jt-stats {
    display: grid;
    grid-template-columns: 1fr 1fr;
    grid-auto-rows: 1fr;
    gap: 16px;
}
.jt-stat {
    background: rgba(255,255,255,.82);
    backdrop-filter: blur(14px);
    border: 1px solid #E2E8F0;
    border-radius: 20px;
    padding: 24px 22px 20px;
    position: relative;
    overflow: hidden;
    transition: box-shadow 0.3s ease, transform 0.3s ease;
    display: flex;
    flex-direction: column;
    justify-content: flex-start;
}
.jt-stat:hover {
    box-shadow: 0 12px 32px rgba(10,31,68,0.10);
    transform: translateY(-3px);
}
.jt-stat::before {
    content: '';
    position: absolute; top: 0; left: 0; right: 0; height: 3px;
    background: linear-gradient(90deg, #FF5200, #FF8C42);
    border-radius: 18px 18px 0 0;
}
.jt-stat-num {
    font-size: 2.6rem; font-weight: 900; color: #FF5200;
    line-height: 1; letter-spacing: -0.04em; margin-bottom: 8px;
}
.jt-stat-label {
    font-size: 0.8rem; font-weight: 700; color: #0A1F44; margin-bottom: 4px;
}
.jt-stat-desc {
    font-size: 0.75rem; color: #94A3B8; line-height: 1.5; font-weight: 500;
}

/* ── RIGHT: Timeline milestones ── */
.jt-right {
    display: flex;
    flex-direction: column;
    gap: 0;
    padding-top: 8px;
    position: relative;
    padding-left: 0;
}
/* Vertical line */
.jt-right::before {
    content: '';
    position: absolute;
    left: 22px;
    top: 8px;
    bottom: 8px;
    width: 2px;
    background: linear-gradient(180deg, rgba(255,213,191,.35) 0%, #FF5200 45%, rgba(29,78,216,.72) 100%);
    border-radius: 2px;
}

.jt-node {
    display: flex;
    gap: 18px;
    align-items: flex-start;
    padding: 0 0 32px 0;
    position: relative;
}
.jt-node:last-child { padding-bottom: 0; }

/* Dot on the line */
.jt-dot {
    width: 44px;
    height: 44px;
    flex-shrink: 0;
    border-radius: 50%;
    background: linear-gradient(145deg, #FFFFFF, #FFF4EF);
    border: 1px solid rgba(255,82,0,.22);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1rem;
    position: relative;
    z-index: 1;
    box-shadow: 0 0 0 6px rgba(255,82,0,0.10), 0 12px 24px rgba(10,31,68,.10);
    transition: transform 0.3s ease, box-shadow 0.3s ease;
}
.jt-node:hover .jt-dot { transform: scale(1.08); box-shadow: 0 0 0 7px rgba(255,82,0,0.14), 0 16px 28px rgba(10,31,68,.14); }
.jt-dot svg {
    width: 18px;
    height: 18px;
    stroke: #FF5200;
    stroke-width: 2.2;
    fill: none;
}

.jt-body {
    background: rgba(255,255,255,.86);
    backdrop-filter: blur(12px);
    border: 1px solid #E2E8F0;
    border-radius: 20px;
    padding: 18px 22px;
    flex: 1;
    transition: box-shadow 0.3s ease, transform 0.3s ease, border-color 0.3s ease;
    box-shadow: 0 14px 30px rgba(10,31,68,.07);
}
.jt-node:hover .jt-body {
    box-shadow: 0 20px 40px rgba(10,31,68,0.11);
    transform: translateY(-3px);
    border-color: rgba(255,82,0,.22);
}
.jt-milestone {
    font-size: 1.7rem; font-weight: 900; color: #FF5200;
    line-height: 1; letter-spacing: -0.03em; margin-bottom: 8px;
}
.jt-title {
    font-size: 0.92rem; font-weight: 800; color: #0A1F44; margin-bottom: 6px;
}
.jt-desc {
    font-size: 0.84rem; color: #64748B; line-height: 1.65; font-weight: 500;
}

/* ── 3D Data Journey polish ── */
.jt-section {
    perspective: 1300px;
}
.jt-left {
    transform: translateZ(26px);
}
.jt-stat {
    box-shadow: 0 16px 34px rgba(10,31,68,0.08);
    transform-style: preserve-3d;
}
.jt-stat:hover {
    transform: translateY(-7px) translateZ(36px) rotateX(3deg);
    box-shadow: 0 22px 44px rgba(10,31,68,0.14);
}
.jt-right {
    transform: none;
    transform-origin: left center;
}
.jt-right::before {
    width: 4px;
    left: 22px;
    background: linear-gradient(180deg, rgba(255,213,191,.25) 0%, #FF5200 45%, rgba(0,82,204,.72) 100%);
    box-shadow: 0 0 24px rgba(255,82,0,.28);
}
.jt-dot {
    background: linear-gradient(145deg, #FFFFFF, #FFF4EF);
    box-shadow: 0 0 0 6px rgba(255,82,0,0.10), 0 14px 28px rgba(10,31,68,.14);
}
.jt-body {
    background: linear-gradient(145deg, #FFFFFF, #F8FAFC);
    box-shadow: 0 18px 36px rgba(10,31,68,.08);
    transform-style: preserve-3d;
}
.jt-node:hover .jt-body {
    transform: translateY(-6px) translateZ(32px);
    box-shadow: 0 24px 48px rgba(10,31,68,0.14);
    border-color: rgba(255,82,0,.28);
}
.jt-node:hover .jt-milestone {
    text-shadow: 0 12px 28px rgba(255,82,0,.24);
}

@media (max-width: 900px) {
    .jt-section {
        grid-template-columns: 1fr;
        gap: 34px;
    }
    .jt-right {
        transform: none;
        padding-left: 0;
    }
    .jt-right::before { left: 22px; }
}
</style>
<script>
  // Auto-resize iframe to fit content height
  window.addEventListener('load', function() {
    const h = document.body.scrollHeight;
    window.parent.postMessage({type: 'streamlit:setFrameHeight', height: h}, '*');
  });
</script>
</head>
<body>
    <div class="jt-shell">
<div class="jt-section">

  <!-- LEFT -->
  <div class="jt-left">
    <span class="jt-kicker">EES 2026 · Hành trình</span>
    <h2 class="jt-heading">Nhìn lại<br>Hành trình</h2>
    <p class="jt-sub">Những con số và dấu mốc đại diện cho khối lượng công việc khổng lồ mà Team đã thực hiện để biến dữ liệu thô thành các nhóm hành động chiến lược.</p>

    <div class="jt-stats">
      <div class="jt-stat">
        <div class="jt-stat-num">19</div>
        <div class="jt-stat-label">Ngày Khảo Sát</div>
        <div class="jt-stat-desc">Thu thập hơn 20,000 phản hồi hợp lệ trên toàn quốc</div>
      </div>
      <div class="jt-stat">
        <div class="jt-stat-num">20k+</div>
        <div class="jt-stat-label">Nhân Viên Lên Tiếng</div>
        <div class="jt-stat-desc">Tỷ lệ tham gia kỷ lục 93.7% — cao nhất lịch sử GHN</div>
      </div>
      <div class="jt-stat">
        <div class="jt-stat-num">5</div>
        <div class="jt-stat-label">Trụ Cột Phân Tích</div>
        <div class="jt-stat-desc">Niềm tin lãnh đạo · Quản lý trực tiếp · Công việc &amp; phát triển · Thu nhập &amp; minh bạch · Môi trường &amp; phát triển</div>
      </div>
      <div class="jt-stat">
        <div class="jt-stat-num">01</div>
        <div class="jt-stat-label">Dashboard Hợp Nhất</div>
        <div class="jt-stat-desc">Toàn bộ báo cáo & phân tích chéo trong một nền tảng duy nhất</div>
      </div>
    </div>
  </div>

  <!-- RIGHT: Timeline -->
    <div class="jt-right">

    <div class="jt-node">
      <div class="jt-dot">{_jt_icon("kickoff")}</div>
      <div class="jt-body">
        <div style="font-size:.68rem;font-weight:800;letter-spacing:.14em;text-transform:uppercase;color:#FF5200;margin-bottom:8px;">Mốc 01</div>
        <div class="jt-milestone">Kick-off</div>
        <div class="jt-title">Phát Động Chiến Dịch</div>
        <div class="jt-desc">CPO trực tiếp gửi thông điệp đến toàn bộ nhân sự GHN. Các Giám đốc Vùng tiếp lửa và dẫn dắt team tham gia khảo sát đồng loạt.</div>
      </div>
    </div>

    <div class="jt-node">
      <div class="jt-dot">{_jt_icon("scan")}</div>
      <div class="jt-body">
        <div style="font-size:.68rem;font-weight:800;letter-spacing:.14em;text-transform:uppercase;color:#FF5200;margin-bottom:8px;">Mốc 02</div>
        <div class="jt-milestone">19 ngày</div>
        <div class="jt-title">Thu Thập Thần Tốc</div>
        <div class="jt-desc">Phối hợp với các khối Vận hành trên toàn quốc, đạt 20,005 phản hồi thu thập và 19,221 mẫu phân tích sau làm sạch — vượt mọi kỳ vọng ban đầu về quy mô lẫn tốc độ.</div>
      </div>
    </div>

    <div class="jt-node">
      <div class="jt-dot">{_jt_icon("gear")}</div>
      <div class="jt-body">
        <div style="font-size:.68rem;font-weight:800;letter-spacing:.14em;text-transform:uppercase;color:#FF5200;margin-bottom:8px;">Mốc 03</div>
        <div class="jt-milestone">Data Processing</div>
        <div class="jt-title">Xử Lý & Làm Sạch Dữ Liệu</div>
        <div class="jt-desc">Chuẩn hóa dữ liệu thô qua nhiều vòng kiểm tra, map với HRIS và thiết lập cấu trúc phân nhóm Division/Section chính xác tuyệt đối.</div>
      </div>
    </div>

    <div class="jt-node">
      <div class="jt-dot">{_jt_icon("report")}</div>
      <div class="jt-body">
        <div style="font-size:.68rem;font-weight:800;letter-spacing:.14em;text-transform:uppercase;color:#FF5200;margin-bottom:8px;">Mốc 04</div>
        <div class="jt-milestone">Now</div>
        <div class="jt-title">Dashboard & Executive Report</div>
        <div class="jt-desc">Hội tụ toàn bộ báo cáo, phân tích chéo và câu chuyện dữ liệu vào một giao diện thông minh — sẵn sàng cho cuộc họp điều hành.</div>
      </div>
    </div>

  </div>
</div>
</div>
</body>
</html>
"""
    journey_html = (
        journey_html
        .replace('{_jt_icon("kickoff")}', _jt_icon("kickoff"))
        .replace('{_jt_icon("scan")}', _jt_icon("scan"))
        .replace('{_jt_icon("gear")}', _jt_icon("gear"))
        .replace('{_jt_icon("report")}', _jt_icon("report"))
    )
    components.html(journey_html, height=1020, scrolling=False)

    # ── Vietnam Map (standalone, full-width) ─────────────────────────────────
    # st.plotly_chart(create_vietnam_map(), use_container_width=True)





    # ── 4.5. NEXT STEPS TIMELINE ─────────────────────────────────────────────
    timeline_html = """
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Montserrat:ital,wght@0,400;0,600;0,800;0,900;1,400;1,600;1,800;1,900&display=swap" rel="stylesheet">
<style>
  body {
    margin: 0; padding: 0;
    font-family: "Montserrat", sans-serif;

    background: transparent;
  }
/* ── VERTICAL TIMELINE ── */
.vt-container {
    max-width: 1080px;
    margin: 28px auto 42px auto;
    padding: 34px;
    border-radius: 28px;
    background:
      radial-gradient(circle at 85% 0%, rgba(255,82,0,.14), transparent 32%),
      linear-gradient(135deg, #FFFFFF 0%, #F8FAFC 58%, #EEF6FF 100%);
    border: 1px solid rgba(226,232,240,.95);
    box-shadow: 0 24px 64px rgba(10,31,68,.11), inset 0 1px 0 rgba(255,255,255,.96);
}
.vt-header {
    text-align: center;
    margin-bottom: 54px;
}
.vt-title {
    color: #0A1F44;
    font-size: 2.35rem;
    font-weight: 900;
    text-transform: uppercase;
    letter-spacing: -0.03em;
    margin: 0;
}
.vt-kicker {
    display: inline-flex;
    color: #FF5200;
    font-size: .72rem;
    font-weight: 800;
    letter-spacing: .16em;
    text-transform: uppercase;
    background: #FFF4EF;
    border: 1px solid #FFD5BF;
    border-radius: 999px;
    padding: 7px 12px;
    margin-bottom: 14px;
}
.vt-timeline {
    position: relative;
    max-width: 1000px;
    margin: 0 auto;
    perspective: 1300px;
}
/* The central line */
.vt-timeline::after {
    content: '';
    position: absolute;
    width: 4px;
    background: linear-gradient(180deg, rgba(255,213,191,.5), #FF5200 45%, rgba(0,82,204,.6));
    top: 0;
    bottom: 0;
    left: 50%;
    margin-left: -2px;
    border-radius: 4px;
}

/* Container for each timeline item */
.vt-item {
    padding: 10px 40px;
    position: relative;
    background-color: transparent;
    width: 50%;
    box-sizing: border-box;
}

/* Position left and right */
.vt-left {
    left: 0;
}
.vt-right {
    left: 50%;
}

/* The circles on the line */
.vt-item::after {
    content: '';
    position: absolute;
    width: 20px;
    height: 20px;
    right: -10px;
    background-color: #fff;
    border: 4px solid #0052CC;
    top: 30px;
    border-radius: 50%;
    z-index: 1;
    box-sizing: border-box;
    box-shadow: 0 0 0 4px rgba(0,82,204,0.1);
}
.vt-right::after {
    left: -10px;
}

/* The actual content card */
.vt-content {
    padding: 24px 30px;
    background: rgba(255,255,255,.88);
    backdrop-filter: blur(14px);
    position: relative;
    border-radius: 20px;
    box-shadow: 0 18px 38px rgba(10,31,68,0.09);
    border: 1px solid #E2E8F0;
    transition: transform 0.3s ease, box-shadow 0.3s ease;
    transform-style: preserve-3d;
}
.vt-content:hover {
    transform: translateY(-7px) translateZ(34px) rotateX(2deg);
    box-shadow: 0 15px 40px rgba(0,82,204,0.15);
    border-color: #0052CC;
}

/* Arrows pointing to the line */
.vt-left .vt-content::after {
    content: " ";
    position: absolute;
    top: 30px;
    right: -12px;
    border-width: 12px 0 12px 12px;
    border-style: solid;
    border-color: transparent transparent transparent #fff;
}
.vt-right .vt-content::after {
    content: " ";
    position: absolute;
    top: 30px;
    left: -12px;
    border-width: 12px 12px 12px 0;
    border-style: solid;
    border-color: transparent #fff transparent transparent;
}

/* Typography inside card */
.vt-date {
    display: flex;
    align-items: center;
    color: #0052CC;
    font-size: 0.9rem;
    font-weight: 800;
    margin-bottom: 12px;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}
.vt-date svg {
    margin-right: 6px;
}
.vt-step-title {
    font-size: 1.3rem;
    font-weight: 900;
    color: #0A1F44;
    margin: 0 0 16px 0;
    line-height: 1.3;
    text-transform: uppercase;
}
.vt-list {
    list-style: none;
    padding: 0;
    margin: 0;
}
.vt-list li {
    position: relative;
    padding-left: 20px;
    margin-bottom: 12px;
    font-size: 0.95rem;
    color: #475569;
    line-height: 1.5;
}
.vt-list li::before {
    content: '❯';
    position: absolute;
    left: 0;
    color: #0052CC;
    font-size: 0.8rem;
    top: 2px;
}

/* Make Step 2 stand out like in the image (but vertical style) */
.vt-item.vt-highlight::after {
    border-color: #FF5200;
    box-shadow: 0 0 0 4px rgba(255,82,0,0.15);
}
.vt-item.vt-highlight .vt-content {
    background: #FF5200;
    color: #fff;
    border-color: #FF5200;
    box-shadow: 0 18px 46px rgba(255,82,0,0.24);
}
.vt-item.vt-highlight:hover .vt-content {
    box-shadow: 0 15px 40px rgba(255,82,0,0.25);
}
.vt-item.vt-highlight .vt-left .vt-content::after {
    border-color: transparent transparent transparent #FF5200;
}
.vt-item.vt-highlight.vt-right .vt-content::after {
    border-color: transparent #FF5200 transparent transparent;
}
.vt-item.vt-highlight .vt-date,
.vt-item.vt-highlight .vt-step-title,
.vt-item.vt-highlight .vt-list li {
    color: #fff;
}
.vt-item.vt-highlight .vt-list li::before {
    color: #FFD5BF;
}

/* Responsive styles */
@media screen and (max-width: 768px) {
    .vt-timeline::after {
        left: 24px;
    }
    .vt-item {
        width: 100%;
        padding-left: 60px;
        padding-right: 0;
    }
    .vt-left, .vt-right {
        left: 0;
    }
    .vt-left::after, .vt-right::after {
        left: 14px;
    }
    .vt-left .vt-content::after, .vt-right .vt-content::after {
        left: -12px;
        right: auto;
        border-width: 12px 12px 12px 0;
        border-color: transparent #fff transparent transparent;
    }
    .vt-item.vt-highlight.vt-left .vt-content::after,
    .vt-item.vt-highlight.vt-right .vt-content::after {
        border-color: transparent #FF5200 transparent transparent;
    }
}
</style>
</head>
<body>
<div class="vt-container">
    <div class="vt-header">
        <span class="vt-kicker">Action Roadmap</span>
        <h2 class="vt-title">SAU KHẢO SÁT GHN SẼ LÀM GÌ</h2>
    </div>
    
    <div class="vt-timeline">
        <!-- Step 1 (Left) -->
        <div class="vt-item vt-left">
            <div class="vt-content">
                <div class="vt-date">
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><polyline points="12 6 12 12 16 14"></polyline></svg>
                    20/05/2026
                </div>
                <h3 class="vt-step-title">Đóng khảo sát</h3>
                <ul class="vt-list">
                    <li>Thông báo cảm ơn toàn công ty</li>
                    <li>Công bố kết quả EES Race (cá nhân, tập thể)</li>
                    <li>Trao giải</li>
                </ul>
            </div>
        </div>

        <!-- Step 2 (Right, Highlighted) -->
        <div class="vt-item vt-right vt-highlight">
            <div class="vt-content">
                <div class="vt-date">
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><polyline points="12 6 12 12 16 14"></polyline></svg>
                    THÁNG 6/2026
                </div>
                <h3 class="vt-step-title">Phân tích &amp; Báo cáo</h3>
                <ul class="vt-list">
                    <li>Tính các chỉ số gắn kết</li>
                    <li>Phân loại và phân tích theo nhóm chủ đề</li>
                    <li>Báo cáo kết quả theo Khối, phòng ban</li>
                    <li>Kế hoạch và hành động cụ thể</li>
                </ul>
            </div>
        </div>

        <!-- Step 3 (Left) -->
        <div class="vt-item vt-left">
            <div class="vt-content">
                <div class="vt-date">
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><polyline points="12 6 12 12 16 14"></polyline></svg>
                    THÁNG 7/2026
                </div>
                <h3 class="vt-step-title">Chia sẻ toàn công ty</h3>
                <ul class="vt-list">
                    <li>Công bố kết quả tổng quan</li>
                    <li>Những điểm mà GHN đang làm tốt</li>
                    <li>Các hành động dự kiến cải tiến từ GHN</li>
                    <li>Trao đổi cụ thể đối với từng Khối/Phòng ban</li>
                </ul>
            </div>
        </div>

        <!-- Step 4 (Right) -->
        <div class="vt-item vt-right">
            <div class="vt-content">
                <div class="vt-date">
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><polyline points="12 6 12 12 16 14"></polyline></svg>
                    T8 - T9/2026
                </div>
                <h3 class="vt-step-title">Theo dõi và Đo lường</h3>
                <ul class="vt-list">
                    <li>Triển khai kế hoạch hành động</li>
                    <li>Báo cáo tiến độ cải tiến hàng tháng</li>
                    <li>Đo lường tiến độ cải tiến</li>
                </ul>
            </div>
        </div>
    </div>
</div>
</body>
</html>
"""
    components.html(timeline_html, height=1750, scrolling=False)
    # ── 5. TEAM ───────────────────────────────────────────────────────────────
    st.html("""
    <div class="ed-container">
        <div class="ed-team-section">
            <div class="ed-section-header">
                <h2 class="ed-section-title">Đội ngũ thực hiện</h2>
                <span class="ed-section-tag">Những người đứng sau</span>
            </div>
            <div class="ed-team-grid">
                <div class="ed-team-card">
                    <div class="ed-team-avatar">EX</div>
                    <div class="ed-team-role">Project Lead</div>
                    <div class="ed-team-name">EX</div>
                    <div class="ed-team-desc">Thiết kế nội dung khảo sát, điều phối triển khai và theo dõi tiến độ thực hiện trên toàn GHN.</div>
                </div>
                <div class="ed-team-card">
                    <div class="ed-team-avatar">HR</div>
                    <div class="ed-team-role">Truyền thông &amp; Kết nối</div>
                    <div class="ed-team-name">HRBP các khối / phòng ban</div>
                    <div class="ed-team-desc">Phối hợp truyền thông, kết nối các phòng ban và thúc đẩy sự tham gia của nhân viên trong chương trình khảo sát.</div>
                </div>
                <div class="ed-team-card">
                    <div class="ed-team-avatar">IT</div>
                    <div class="ed-team-role">Hạ tầng &amp; Hệ thống</div>
                    <div class="ed-team-name">Team IT, Product, L&amp;D</div>
                    <div class="ed-team-desc">Đồng hành hỗ trợ về hệ thống, kỹ thuật và các công cụ trong suốt chương trình khảo sát.</div>
                </div>
                <div class="ed-team-card">
                    <div class="ed-team-avatar">CPO</div>
                    <div class="ed-team-role">Project Sponsor</div>
                    <div class="ed-team-name">CPO</div>
                    <div class="ed-team-desc">Định hướng mục tiêu, hỗ trợ nguồn lực và đồng hành cùng chương trình trong suốt quá trình triển khai.</div>
                </div>
            </div>
        </div>
    </div>
    
    <style>
    /* Footer */
    .ed-footer-wrapper {
        margin-top: 32px;
        background: #FAFAFA;
        border-top: 4px solid #FF5200;
        padding: 48px 0;
        margin-left: -1rem;
        margin-right: -1rem;
    }
    .ed-footer {
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        flex-wrap: wrap;
        gap: 40px;
        padding: 0 1rem;
    }
    .ed-footer-left { max-width: 480px; }
    .ed-footer-logo {
        font-size: 1.4rem;
        font-weight: 900;
        margin-bottom: 12px;
    }
    .ed-footer-logo .ghn { color: #FF5200; }
    .ed-footer-logo .ees { color: #0052CC; }
    .ed-footer-desc {
        font-size: 0.95rem;
        color: #475569;
        line-height: 1.6;
        margin-bottom: 24px;
        font-weight: 500;
    }
    .ed-footer-right {
        display: flex;
        flex-direction: column;
        gap: 6px;
    }
    .ed-footer-title {
        color: #FF5200;
        font-size: 0.85rem;
        font-weight: 800;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        margin-bottom: 10px;
    }
    .ed-footer-item {
        font-size: 0.85rem;
        color: #64748B;
        font-weight: 600;
        text-transform: uppercase;
    }
    .ed-footer-highlight-dark {
        color: #0A1F44;
        font-weight: 700;
        margin-bottom: 10px;
        text-transform: none;
        font-size: 0.95rem;
    }
    .ed-footer-highlight-orange {
        color: #FF5200;
        font-weight: 700;
        text-transform: none;
        font-size: 0.95rem;
    }
    @media (max-width: 768px) {
        .ed-footer { flex-direction: column; }
    }
    </style>

    <div class="ed-footer-wrapper">
        <div class="ed-container ed-footer">
            <div class="ed-footer-left">
                <div class="ed-footer-logo">
                    <span class="ghn">GHN</span> <span style="color:#94A3B8; font-weight:400; margin:0 4px;">×</span> <span class="ees">EES 2026</span>
                </div>
                <div class="ed-footer-desc">
                    Khảo sát gắn kết nhân viên thường niên của GiaoHangNhanh.<br>
                    Cùng với tiếng nói của 20.000+ xây dựng môi trường và<br>
                    trải nghiệm nhân viên cho Công ty.
                </div>
            </div>
            <div class="ed-footer-right">
                <div class="ed-footer-title">LIÊN HỆ HỖ TRỢ</div>
                <div class="ed-footer-item">HRBP - BỘ PHẬN ĐỐI TÁC NHÂN SỰ</div>
                <div class="ed-footer-item">BAN TỔ CHỨC EES 2026</div>
                <div class="ed-footer-highlight-dark">people@ghn.vn</div>
                <div class="ed-footer-item">ỨNG DỤNG GTALK</div>
                <div class="ed-footer-highlight-orange">gtalk.ghn.vn</div>
            </div>
        </div>
    </div>
    """)
