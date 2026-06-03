import streamlit as st
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
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');

    .ed-container { font-family:'Inter',sans-serif; color:#0A1F44; max-width:1200px; }

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
    .ed-team-section { padding-bottom:100px; }
    .ed-team-grid { display:grid; grid-template-columns:repeat(3,1fr); gap:20px; margin-top:28px; }
    .ed-team-card {
        background:#fff; border:1.5px solid #E2E8F0; border-radius:20px;
        padding:28px 28px 24px; transition:box-shadow .3s ease, transform .3s ease;
    }
    .ed-team-card:hover { box-shadow:0 12px 40px rgba(10,31,68,.1); transform:translateY(-4px); }
    .ed-team-role { font-size:.68rem; font-weight:800; text-transform:uppercase; letter-spacing:.14em; color:#FF5200; margin-bottom:8px; }
    .ed-team-name { font-size:1.25rem; font-weight:800; color:#0A1F44; letter-spacing:-.02em; margin-bottom:10px; }
    .ed-team-desc { font-size:.9rem; color:#64748B; line-height:1.6; }
    .ed-team-badge {
        display:inline-block; margin-top:14px; font-size:.72rem; font-weight:700;
        color:#0A1F44; background:#F1F5F9; padding:3px 10px; border-radius:999px;
    }
    </style>
    """, unsafe_allow_html=True)

    # ── 1. HERO (stats) ──────────────────────────────────────────────────────
    st.markdown("""
    <div class="ed-container">
        <div class="ed-hero">
            <span class="ed-kicker">Employee Engagement Survey 2026</span>
            <h1 class="ed-headline">Dấu ấn hành trình EES 2026<br>&amp; Những nỗ lực từ phía sau</h1>
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
    font-family: 'Inter', -apple-system, sans-serif;
    background: transparent;
    padding: 0;
  }}

  /* ── Section header ── */
  .section-header {{
    display: flex; align-items: center; justify-content: space-between;
    margin-bottom: 18px;
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
    aspect-ratio: 16 / 9;
    border-radius: 20px;
    overflow: hidden;
    background: #000;
    box-shadow: 0 24px 64px rgba(10,31,68,.28);
    cursor: pointer;
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
    margin-top: 20px;
    display: grid;
    grid-template-columns: repeat(5, 1fr);
    gap: 14px;
  }}
  @media (max-width: 820px) {{
    .dock {{ grid-template-columns: repeat(3, 1fr); }}
  }}

  .dock-card {{
    position: relative;
    width: 100%;
    aspect-ratio: 16 / 10;
    border-radius: 14px;
    overflow: hidden;
    cursor: pointer;
    background: #0F172A;
    border: 2px solid transparent;
    transition: transform .3s cubic-bezier(.4,0,.2,1), box-shadow .3s ease, border-color .3s ease;
  }}
  .dock-card:hover {{
    transform: translateY(-4px);
    box-shadow: 0 12px 28px rgba(10,31,68,.25);
  }}
  .dock-card-active {{
    border-color: #FF5200;
    box-shadow: 0 0 0 2px rgba(255,82,0,.35), 0 8px 20px rgba(255,82,0,.3);
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
</style>
</head>
<body>

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
    components.html(video_html, height=1050, scrolling=False)

    # ── 3. GALLERY ───────────────────────────────────────────────────────────
    gallery_images = [
        ("https://res.cloudinary.com/dd7gti2kn/image/upload/v1780392695/LOGO%20GHN/IMG_1493_ldeq70.jpg",        "Khoảnh khắc hậu trường"),
        (img1,  "Truyền thông EES 2026 — CPO gửi thông điệp"),
        ("https://res.cloudinary.com/dd7gti2kn/image/upload/v1780392212/LOGO%20GHN/EES_GDV_A_Doanh_jj76dm.png", "GDV anh Doanh"),
        (img2,  "CPO Kick-off — Khởi động chiến dịch"),
        (img3,  "Giám đốc vùng — GDV anh Vũ"),
        ("https://res.cloudinary.com/dd7gti2kn/image/upload/v1780392653/LOGO%20GHN/IMG_1490_mky43b.jpg",        "Team tại sự kiện"),
        (img4,  "Giám đốc vùng — Mr. Nguyễn Văn Tân"),
    ]

    gallery_items_html = ""
    for url, caption in gallery_images:
        gallery_items_html += f'''
        <div class="gl-item">
            <img class="gl-img" src="{url}" alt="{caption}" loading="lazy">
            <div class="gl-caption">{caption}</div>
        </div>'''

    gallery_html = f'''
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  body {{
    margin: 0; padding: 0;
    font-family: "Inter", "Helvetica Neue", sans-serif;
    background: transparent;
    overflow-x: hidden;
  }}
  /* ── Section header ── */
  .gl-header {{
    display: flex; align-items: baseline; justify-content: space-between;
    margin-bottom: 24px; padding: 0 12px;
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
  .gl-wrap {{
    display: flex;
    gap: 24px;
    overflow-x: auto;
    padding: 24px 12px 60px 12px;
    scroll-snap-type: x mandatory;
    scroll-behavior: smooth;
    -webkit-overflow-scrolling: touch;
    scrollbar-width: none; /* Firefox */
  }}
  .gl-wrap::-webkit-scrollbar {{
    display: none; /* Chrome/Safari */
  }}

  .gl-item {{
    position: relative;
    flex: 0 0 auto;
    height: 550px; /* Cố định chiều cao, chiều ngang tự giãn không giới hạn khung */
    scroll-snap-align: center;
    border-radius: 12px;
    transition: transform 0.5s cubic-bezier(0.2, 0.8, 0.2, 1), box-shadow 0.5s ease;
  }}
  .gl-item:hover {{
    transform: translateY(-8px);
    box-shadow: 0 30px 60px rgba(10,31,68,0.25);
    z-index: 10;
  }}
  
  .gl-img {{
    height: 100%;       /* Phủ kín chiều cao của khung gl-item */
    width: auto;        /* Tự động kéo ngang theo TỶ LỆ GỐC, KHÔNG CẮT HÌNH */
    display: block;
    border-radius: 12px;
    object-fit: contain; /* KHÔNG bao giờ bị khuất hình */
  }}

  /* Minimalist hover caption */
  .gl-caption {{
    position: absolute;
    bottom: 24px;
    left: 24px;
    background: rgba(255, 255, 255, 0.9);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    color: #0A1F44;
    padding: 10px 20px;
    border-radius: 8px;
    font-size: 0.95rem;
    font-weight: 700;
    opacity: 0;
    transform: translateY(15px);
    transition: all 0.4s ease;
    pointer-events: none;
    box-shadow: 0 10px 30px rgba(0,0,0,0.15);
    max-width: 85%;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }}
  .gl-item:hover .gl-caption {{
    opacity: 1;
    transform: translateY(0);
  }}

  /* ── Responsive ── */
  @media (max-width: 768px) {{
    .gl-item {{ height: 400px; }}
    .gl-wrap {{ gap: 16px; }}
  }}
  @media (max-width: 480px) {{
    .gl-item {{ height: 300px; }}
    .gl-wrap {{ gap: 12px; }}
    .gl-caption {{ bottom: 12px; left: 12px; font-size: 0.85rem; padding: 8px 16px; }}
  }}
</style>
</head>
<body>

<!-- Section header -->
<div class="gl-header">
  <span class="gl-title">Góc nhìn hậu trường</span>
  <span class="gl-tag">Team EX Showcase</span>
</div>

<!-- Horizontal scroll container -->
<div class="gl-wrap">
  {gallery_items_html}
</div>

</body>
</html>
'''
    components.html(gallery_html, height=750, scrolling=False)

    # ── 4. TIMELINE ──────────────────────────────────────────────────────────
    st.markdown("""
    <div class="ed-container">
        <div class="ed-timeline-section">
            <div class="ed-timeline-left">
                <h2>Nhìn lại<br>Hành trình</h2>
                <p>Những con số và dấu mốc đại diện cho khối lượng công việc khổng lồ mà Team đã thực hiện để biến dữ liệu thô thành các nhóm hành động chiến lược.</p>
            </div>
            <div class="ed-timeline-right">
                <div class="ed-timeline-node">
                    <div class="ed-timeline-big-num">19</div>
                    <div class="ed-timeline-content">
                        <h4>Ngày Khảo Sát Thần Tốc</h4>
                        <p>Phối hợp với các khối Vận hành trên toàn quốc để thu thập hơn 20,000 phản hồi hợp lệ trong thời gian kỷ lục.</p>
                    </div>
                </div>
                <div class="ed-timeline-node">
                    <div class="ed-timeline-big-num">20k+</div>
                    <div class="ed-timeline-content">
                        <h4>Nhân Viên Đã Lên Tiếng</h4>
                        <p>Hơn 20,000 nhân viên GHN đã chủ động nói lên tiếng nói của mình — mỗi phản hồi là một tín hiệu quan trọng để tổ chức lắng nghe và thay đổi.</p>
                    </div>
                </div>
                <div class="ed-timeline-node">
                    <div class="ed-timeline-big-num">∞</div>
                    <div class="ed-timeline-content">
                        <h4>Vòng Xử Lý &amp; Làm Sạch Dữ Liệu</h4>
                        <p>Chuẩn hóa dữ liệu thô qua nhiều vòng kiểm tra, map với hệ thống HRIS và thiết lập cấu trúc phân nhóm (Division/Section) chính xác tuyệt đối.</p>
                    </div>
                </div>
                <div class="ed-timeline-node">
                    <div class="ed-timeline-big-num">01</div>
                    <div class="ed-timeline-content">
                        <h4>Nền Tảng Dashboard Duy Nhất</h4>
                        <p>Hội tụ toàn bộ báo cáo, phân tích chéo và câu chuyện dữ liệu vào chung một giao diện thông minh.</p>
                    </div>
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

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
                    <div class="ed-team-role">Project Lead</div>
                    <div class="ed-team-name">Team EX &amp; L&amp;D</div>
                    <div class="ed-team-desc">Thiết kế bộ câu hỏi, phối hợp triển khai khảo sát và điều phối thu thập phản hồi toàn GHN.</div>
                    <span class="ed-team-badge">Survey Design &amp; Ops</span>
                </div>
                <div class="ed-team-card">
                    <div class="ed-team-role">Data &amp; Analytics</div>
                    <div class="ed-team-name">Team People Analytics</div>
                    <div class="ed-team-desc">Làm sạch, chuẩn hóa và phân tích toàn bộ tập dữ liệu 20,005 mẫu với mô hình NLP và phân nhóm theo EVP.</div>
                    <span class="ed-team-badge">NLP · HRIS Mapping</span>
                </div>
                <div class="ed-team-card">
                    <div class="ed-team-role">Truyền thông &amp; Lan tỏa</div>
                    <div class="ed-team-name">HRBP các vùng &amp; KTC</div>
                    <div class="ed-team-desc">Hỗ trợ truyền thông nội bộ, thúc đẩy nhân viên tham gia khảo sát và đảm bảo tỉ lệ phản hồi đạt mức cao nhất tại từng khu vực.</div>
                    <span class="ed-team-badge">Internal Comms · Engagement Push</span>
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── 6. ĐỘ TIN CẬY DỮ LIỆU (subsection mở rộng) ────────────────────────
    from views import overview_data_reliability
    overview_data_reliability.render()
