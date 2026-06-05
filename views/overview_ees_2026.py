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

    main_video_url  = "https://res.cloudinary.com/dd7gti2kn/video/upload/v1780389451/LOGO%20GHN/Action_video_dgq3f7.mp4"
    short_urls = [
        ("https://res.cloudinary.com/dd7gti2kn/video/upload/v1780395113/LOGO%20GHN/IMG_0734_nhqt02.mp4",   "Khoảnh khắc 1"),
        ("https://res.cloudinary.com/dd7gti2kn/video/upload/v1780393976/LOGO%20GHN/IMG_1233_wgzajm.mp4",   "Khoảnh khắc 2"),
        ("https://res.cloudinary.com/dd7gti2kn/video/upload/v1780393954/LOGO%20GHN/IMG_1232_ykz6pz.mp4",   "Khoảnh khắc 3"),
        ("https://res.cloudinary.com/dd7gti2kn/video/upload/v1780393907/LOGO%20GHN/IMG_1723_gdh1gs.mp4",   "Khoảnh khắc 4"),
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
    .ed-orbit {
        position:absolute;
        left:50%;
        bottom:28px;
        width:280px;
        height:190px;
        transform:translateX(-50%);
        transform-style:preserve-3d;
    }
    .ed-orbit-ring {
        position:absolute;
        inset:22px 12px 28px;
        border:1px solid rgba(255,255,255,.24);
        border-radius:50%;
        transform:rotateX(64deg);
    }
    .ed-orbit-ring:nth-child(2) {
        inset:44px 42px 48px;
        border-color:rgba(255,213,191,.42);
    }
    .ed-orbit-core {
        position:absolute;
        left:50%;
        top:48%;
        width:86px;
        height:86px;
        border-radius:50%;
        transform:translate(-50%,-50%) translateZ(42px);
        background:radial-gradient(circle at 35% 28%, #FFFFFF 0%, #FFD5BF 22%, #FF5200 66%, #B93800 100%);
        box-shadow:0 0 34px rgba(255,82,0,.62);
    }
    .ed-orbit-pill {
        position:absolute;
        padding:7px 10px;
        border-radius:999px;
        color:#fff;
        background:rgba(255,255,255,.12);
        border:1px solid rgba(255,255,255,.20);
        font-size:.68rem;
        font-weight:800;
        backdrop-filter:blur(10px);
        box-shadow:0 12px 22px rgba(0,0,0,.16);
    }
    .ed-orbit-pill.p1 { left:8px; top:28px; }
    .ed-orbit-pill.p2 { right:10px; top:22px; }
    .ed-orbit-pill.p3 { left:38px; bottom:20px; }
    .ed-orbit-pill.p4 { right:34px; bottom:18px; }
    .ed-orbit-pill.p5 { left:50%; top:0; transform:translateX(-50%); }
    .ed-command-bars {
        position:absolute;
        right:28px;
        bottom:28px;
        z-index:2;
        display:flex;
        align-items:end;
        gap:8px;
        height:94px;
    }
    .ed-command-bars span {
        width:16px;
        border-radius:999px 999px 4px 4px;
        background:linear-gradient(180deg,#FFFFFF,#FFD5BF 42%,#FF5200);
        opacity:.92;
        box-shadow:0 12px 18px rgba(0,0,0,.18);
    }
    .ed-command-bars span:nth-child(1) { height:38px; }
    .ed-command-bars span:nth-child(2) { height:64px; }
    .ed-command-bars span:nth-child(3) { height:48px; }
    .ed-command-bars span:nth-child(4) { height:82px; }

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

    # ── 1. HERO (stats) ──────────────────────────────────────────────────────
    st.markdown("""
    <div class="ed-container">
        <div class="ed-hero">
            <div class="ed-hero-shell">
                <div class="ed-hero-copy">
                    <span class="ed-kicker">Employee Engagement Survey 2026</span>
                    <h1 class="ed-headline">Dấu ấn hành trình EES 2026<br>&amp; những nỗ lực từ phía sau</h1>
                    <p class="ed-hero-sub">Một lớp tổng quan điều hành cho thấy quy mô tham gia, chất lượng dữ liệu và câu chuyện triển khai phía sau bộ báo cáo gắn kết toàn GHN.</p>
                </div>
                <div class="ed-command-panel">
                    <div class="ed-command-top">
                        <div>
                            <span class="ed-command-label">Engagement Intelligence</span>
                            <div class="ed-command-score">72.3</div>
                            <div class="ed-command-unit">EI score · Validated dataset</div>
                        </div>
                        <span class="ed-command-chip">Live Overview</span>
                    </div>
                    <div class="ed-orbit">
                        <div class="ed-orbit-ring"></div>
                        <div class="ed-orbit-ring"></div>
                        <div class="ed-orbit-core"></div>
                        <span class="ed-orbit-pill p1">Lãnh đạo</span>
                        <span class="ed-orbit-pill p2">MEI</span>
                        <span class="ed-orbit-pill p3">Công việc</span>
                        <span class="ed-orbit-pill p4">Thu nhập</span>
                        <span class="ed-orbit-pill p5">Môi trường</span>
                    </div>
                    <div class="ed-command-bars">
                        <span></span><span></span><span></span><span></span>
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
                        <span class="ed-metric-sub">Mẫu hợp lệ</span>
                    </div>
                    <div class="ed-metric-item">
                        <span class="ed-metric-label">Tỷ lệ tham gia</span>
                        <span class="ed-metric-val">93.7%</span>
                        <span class="ed-metric-sub positive">▲ +17.8% so với 2025</span>
                    </div>
                    <div class="ed-metric-item">
                        <span class="ed-metric-label">Mức gắn kết</span>
                        <span class="ed-metric-val">72.3</span>
                        <span class="ed-metric-sub">Điểm EI tổng thể</span>
                    </div>
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── 2. VIDEO SECTION ─────────────────────────────────────────────────────
    # Playlist = main highlight reel + 4 shorts. The main reel is the first item.
    playlist = [(main_video_url, "Highlight Reel")] + short_urls

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
        ("https://res.cloudinary.com/dd7gti2kn/image/upload/v1780541185/LOGO%20GHN/EES_2026_-_Thie%CC%A3%CC%82p_ca%CC%89m_o%CC%9Bn_Final_hzxztu.png",        "Thư cảm ơn"),
        ("https://res.cloudinary.com/dd7gti2kn/image/upload/v1780392695/LOGO%20GHN/IMG_1493_ldeq70.jpg",        "Khoảnh khắc hậu trường"),
        (img1,  "Truyền thông EES 2026 — CPO gửi thông điệp"),
        ("https://res.cloudinary.com/dd7gti2kn/image/upload/v1780392212/LOGO%20GHN/EES_GDV_A_Doanh_jj76dm.png", "GDV anh Doanh"),
        (img2,  "CPO Kick-off — Khởi động chiến dịch"),
        (img3,  "Giám đốc vùng — GDV anh Vũ"),
        ("https://res.cloudinary.com/dd7gti2kn/image/upload/v1780392653/LOGO%20GHN/IMG_1490_mky43b.jpg",        "Team tại sự kiện"),
        (img4,  "Giám đốc vùng — Mr. Nguyễn Văn Tân"),
    ]

    gallery_items_html = ""
    for url, caption in gallery_images * 2:
        gallery_items_html += f'''
<div class="gl-item">
<img class="gl-img" src="{url}" alt="{caption}" loading="lazy">
<div class="gl-caption">{caption}</div>
</div>'''

    gallery_html = f'''
<style>
  /* ── Section header ── */
  .gl-header {{
    display: flex; align-items: baseline; justify-content: space-between;
    margin-bottom: 24px; padding: 0 6px;
  }}
  .gl-title {{
    font-size: 2rem; font-weight: 900; letter-spacing: -0.03em; color: #0A1F44;
  }}
  .gl-tag {{
    font-size: 0.72rem; font-weight: 800; color: #FF5200;
    text-transform: uppercase; letter-spacing: 0.15em;
    background: #FFF4EF; padding: 4px 12px; border-radius: 999px;
    border: 1px solid #FFD5BF;
  }}

  /* ── Premium Horizontal Scroll Gallery ── */
  .gl-wrap-container {{
    overflow-x: hidden;
    width: 100%;
    margin-bottom: 36px;
    padding: 18px 0 8px;
    border-radius: 28px;
    background:
      radial-gradient(circle at 18% 0%, rgba(255,82,0,.12), transparent 30%),
      linear-gradient(135deg, rgba(255,255,255,.94), rgba(248,250,252,.92));
    border: 1px solid rgba(226,232,240,.9);
    box-shadow: inset 0 1px 0 rgba(255,255,255,.95), 0 22px 58px rgba(10,31,68,.10);
    perspective: 1400px;
  }}
  .gl-wrap {{
    display: flex;
    gap: 24px;
    padding: 24px 18px 62px 18px;
    width: max-content;
    animation: autoScroll 30s linear infinite;
  }}
  .gl-wrap:hover {{
    animation-play-state: paused;
  }}
  @keyframes autoScroll {{
    0% {{ transform: translateX(0); }}
    100% {{ transform: translateX(calc(-50% - 12px)); }}
  }}

  .gl-item {{
    position: relative;
    flex: 0 0 auto;
    height: 500px; 
    scroll-snap-align: center;
    border-radius: 20px;
    transform: rotateY(-7deg) translateZ(0);
    transform-style: preserve-3d;
    transition: transform 0.5s cubic-bezier(0.2, 0.8, 0.2, 1), box-shadow 0.5s ease, filter 0.5s ease;
  }}
  .gl-item:hover {{
    transform: scale(1.025) translateY(-12px) rotateY(0deg) translateZ(48px);
    box-shadow: 0 30px 60px -12px rgba(10, 31, 68, 0.25);
    z-index: 10;
  }}
  .gl-img {{
    width: auto;
    height: 100%;
    object-fit: cover;
    border-radius: 20px;
    box-shadow: 0 22px 44px -16px rgba(0,0,0,0.28);
    border: 1px solid rgba(255,255,255,0.55);
  }}
  .gl-item::after {{
    content: '';
    position: absolute;
    inset: auto 16px -18px;
    height: 28px;
    border-radius: 50%;
    background: rgba(10,31,68,.20);
    filter: blur(16px);
    z-index: -1;
  }}
  .gl-caption {{
    position: absolute;
    bottom: 24px; left: 24px;
    background: rgba(10, 31, 68, 0.78);
    backdrop-filter: blur(12px);
    color: white;
    padding: 12px 24px;
    border-radius: 14px;
    border: 1px solid rgba(255,255,255,.18);
    font-size: 0.95rem; font-weight: 600;
    opacity: 0;
    transform: translateY(10px);
    transition: all 0.4s ease;
    pointer-events: none;
    white-space: nowrap;
  }}
  .gl-item:hover .gl-caption {{
    opacity: 1;
    transform: translateY(0);
  }}
  @media (max-width: 768px) {{
    .gl-item {{ height: 400px; }}
    .gl-wrap {{ gap: 16px; padding-bottom: 40px; }}
    .gl-caption {{ bottom: 12px; left: 12px; font-size: 0.85rem; padding: 8px 16px; }}
  }}
</style>

<!-- Section header -->
<div class="gl-header">
  <span class="gl-title">Góc nhìn hậu trường</span>
  <span class="gl-tag">Team EX Showcase</span>
</div>

<!-- Horizontal scroll container -->
<div class="gl-wrap-container">
<div class="gl-wrap">
{gallery_items_html}
</div>
</div>
'''
    components.html(gallery_html, height=640, scrolling=False)

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
    grid-template-columns: 1fr 1fr;
    gap: 60px;
    padding: 4px 4px 10px 4px;
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
}
/* Vertical line */
.jt-right::before {
    content: '';
    position: absolute;
    left: 19px;
    top: 8px;
    bottom: 8px;
    width: 2px;
    background: linear-gradient(180deg, #FFD5BF 0%, #FF5200 50%, #FFD5BF 100%);
    border-radius: 2px;
}

.jt-node {
    display: flex;
    gap: 24px;
    align-items: flex-start;
    padding: 0 0 40px 0;
    position: relative;
}
.jt-node:last-child { padding-bottom: 0; }

/* Dot on the line */
.jt-dot {
    width: 40px;
    height: 40px;
    flex-shrink: 0;
    border-radius: 50%;
    background: white;
    border: 3px solid #FF5200;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1rem;
    position: relative;
    z-index: 1;
    box-shadow: 0 0 0 5px rgba(255,82,0,0.10);
    transition: transform 0.3s ease;
}
.jt-node:hover .jt-dot { transform: scale(1.15); }

.jt-body {
    background: rgba(255,255,255,.86);
    backdrop-filter: blur(12px);
    border: 1px solid #E2E8F0;
    border-radius: 18px;
    padding: 20px 22px;
    flex: 1;
    transition: box-shadow 0.3s ease;
}
.jt-node:hover .jt-body {
    box-shadow: 0 8px 24px rgba(10,31,68,0.09);
}
.jt-milestone {
    font-size: 2rem; font-weight: 900; color: #FF5200;
    line-height: 1; letter-spacing: -0.03em; margin-bottom: 8px;
}
.jt-title {
    font-size: 0.95rem; font-weight: 800; color: #0A1F44; margin-bottom: 6px;
}
.jt-desc {
    font-size: 0.82rem; color: #64748B; line-height: 1.65; font-weight: 500;
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
    padding-left: 6px;
    transform: rotateY(-3deg) translateZ(18px);
    transform-origin: left center;
}
.jt-right::before {
    width: 4px;
    left: 18px;
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
    }
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
        <div class="jt-stat-desc">Lãnh đạo · MEI · Công việc · Thu nhập · Môi trường</div>
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
      <div class="jt-dot">🚀</div>
      <div class="jt-body">
        <div class="jt-milestone">Kick-off</div>
        <div class="jt-title">Phát Động Chiến Dịch</div>
        <div class="jt-desc">CPO trực tiếp gửi thông điệp đến toàn bộ nhân sự GHN. Các Giám đốc Vùng tiếp lửa và dẫn dắt team tham gia khảo sát đồng loạt.</div>
      </div>
    </div>

    <div class="jt-node">
      <div class="jt-dot">📋</div>
      <div class="jt-body">
        <div class="jt-milestone">19 ngày</div>
        <div class="jt-title">Thu Thập Thần Tốc</div>
        <div class="jt-desc">Phối hợp với các khối Vận hành trên toàn quốc, đạt 20,005 phản hồi hợp lệ — vượt mọi kỳ vọng ban đầu về quy mô lẫn tốc độ.</div>
      </div>
    </div>

    <div class="jt-node">
      <div class="jt-dot">⚙️</div>
      <div class="jt-body">
        <div class="jt-milestone">∞ vòng</div>
        <div class="jt-title">Xử Lý & Làm Sạch Dữ Liệu</div>
        <div class="jt-desc">Chuẩn hóa dữ liệu thô qua nhiều vòng kiểm tra, map với HRIS và thiết lập cấu trúc phân nhóm Division/Section chính xác tuyệt đối.</div>
      </div>
    </div>

    <div class="jt-node">
      <div class="jt-dot">📊</div>
      <div class="jt-body">
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
    components.html(journey_html, height=860, scrolling=False)

    # ── Vietnam Map (standalone, full-width) ─────────────────────────────────
    st.plotly_chart(create_vietnam_map(), use_container_width=True)





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
    components.html(timeline_html, height=1300, scrolling=False)
    # ── 5. TEAM ───────────────────────────────────────────────────────────────
    st.markdown("""
    <div class="ed-container">
        <div class="ed-team-section">
            <div class="ed-section-header">
                <h2 class="ed-section-title">Đội ngũ thực hiện</h2>
                <span class="ed-section-tag">People Behind the Data</span>
            </div>
            <div class="ed-team-grid">
                <div class="ed-team-card">
                    <div class="ed-team-avatar">EX</div>
                    <div class="ed-team-role">Project Lead</div>
                    <div class="ed-team-name">Team EX &amp; L&amp;D</div>
                    <div class="ed-team-desc">Thiết kế bộ câu hỏi, phối hợp triển khai khảo sát và điều phối thu thập phản hồi toàn GHN.</div>
                    <span class="ed-team-badge">Survey Design &amp; Ops</span>
                </div>
                <div class="ed-team-card">
                    <div class="ed-team-avatar">HR</div>
                    <div class="ed-team-role">Truyền thông &amp; Lan tỏa</div>
                    <div class="ed-team-name">HRBP các vùng &amp; KTC</div>
                    <div class="ed-team-desc">Hỗ trợ truyền thông nội bộ, thúc đẩy nhân viên tham gia khảo sát và đảm bảo tỉ lệ phản hồi đạt mức cao nhất tại từng khu vực.</div>
                    <span class="ed-team-badge">Internal Comms · Engagement Push</span>
                </div>
                <div class="ed-team-card">
                    <div class="ed-team-avatar">IT</div>
                    <div class="ed-team-role">Hạ tầng &amp; Hệ thống</div>
                    <div class="ed-team-name">Team IT</div>
                    <div class="ed-team-desc">Đảm bảo hạ tầng server, băng thông mạng và hỗ trợ kỹ thuật liên tục trong suốt quá trình triển khai khảo sát.</div>
                    <span class="ed-team-badge">System & Infrastructure</span>
                </div>
                <div class="ed-team-card">
                    <div class="ed-team-avatar">BI</div>
                    <div class="ed-team-role">Kỹ thuật Dữ liệu</div>
                    <div class="ed-team-name">Team BI</div>
                    <div class="ed-team-desc">Xây dựng kiến trúc cơ sở dữ liệu, tối ưu hóa đường ống xử lý dữ liệu (data pipeline) và kết nối API.</div>
                    <span class="ed-team-badge">Data Engineering</span>
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

