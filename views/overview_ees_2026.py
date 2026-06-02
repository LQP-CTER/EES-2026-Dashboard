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
    except Exception as e:
        return ""

def render():
    apply_theme()

    # Cloudinary URLs for masonry layout
    img1 = "https://res.cloudinary.com/dd7gti2kn/image/upload/v1780393860/LOGO%20GHN/EES_2026_-_CPO_ngang_ayvreb.png"
    img2 = "https://res.cloudinary.com/dd7gti2kn/image/upload/v1780393847/LOGO%20GHN/CPO_kick-off_1_edlqb4.png"
    img3 = "https://res.cloudinary.com/dd7gti2kn/image/upload/v1780393855/LOGO%20GHN/EES_2026_-_GDV_a_Vu%CC%83_ew1dix.png"
    img4 = "https://res.cloudinary.com/dd7gti2kn/image/upload/v1780392210/LOGO%20GHN/Mr_Nguye%CC%82%CC%83n_Va%CC%82n_Ta%CC%82n_Regional_Director_Gia%CC%81m_%C4%90o%CC%82%CC%81c_Vu%CC%80ng_rbzjr3.png"

    # Base CSS
    css = """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');

    .ed-container {
        font-family: 'Inter', sans-serif;
        color: #0A1F44;
        max-width: 1200px;
        margin: 0 auto;
    }

    .ed-hero { margin-bottom: 56px; }
    .ed-kicker {
        font-size: 0.72rem;
        font-weight: 800;
        letter-spacing: 0.18em;
        text-transform: uppercase;
        color: #FF5200;
        margin-bottom: 14px;
        display: block;
    }
    .ed-headline {
        font-size: 3.4rem;
        font-weight: 900;
        letter-spacing: -0.03em;
        line-height: 1.08;
        margin: 0 0 36px;
        color: #0A1F44;
    }

    .ed-metrics-grid {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 16px;
        padding-top: 36px;
        border-top: 2px solid #E2E8F0;
    }
    .ed-metric-item {
        background: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 16px;
        padding: 20px 24px 22px;
        display: flex;
        flex-direction: column;
        position: relative;
        overflow: hidden;
    }
    .ed-metric-item::before {
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 3px;
        background: linear-gradient(90deg, #FF5200, #FF8C42);
        border-radius: 16px 16px 0 0;
    }
    .ed-metric-label {
        font-size: 0.7rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        color: #94A3B8;
        margin-bottom: 10px;
    }
    .ed-metric-val {
        font-size: 2.4rem;
        font-weight: 900;
        color: #0A1F44;
        letter-spacing: -0.03em;
        line-height: 1;
    }
    .ed-metric-sub {
        font-size: 0.78rem;
        color: #64748B;
        margin-top: 8px;
        font-weight: 600;
    }
    .ed-metric-sub.positive { color: #10B981; }

    .ed-section-header {
        display: flex;
        align-items: baseline;
        justify-content: space-between;
        margin-bottom: 28px;
        margin-top: 56px;
    }
    .ed-section-title {
        font-size: 2rem;
        font-weight: 900;
        letter-spacing: -0.03em;
        color: #0A1F44;
        margin: 0;
    }
    .ed-section-tag {
        font-size: 0.72rem;
        font-weight: 800;
        color: #FF5200;
        text-transform: uppercase;
        letter-spacing: 0.15em;
        background: #FFF4EF;
        padding: 4px 12px;
        border-radius: 999px;
        border: 1px solid #FFD5BF;
    }

    .ed-masonry {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        grid-auto-rows: 210px;
        gap: 16px;
        margin-bottom: 72px;
    }
    .ed-masonry-item {
        border-radius: 16px;
        overflow: hidden;
        position: relative;
        background: #F1F5F9;
    }
    .ed-masonry-item img {
        width: 100%;
        height: 100%;
        object-fit: cover;
        transition: transform 0.7s cubic-bezier(0.4,0,0.2,1);
    }
    .ed-masonry-item:hover img { transform: scale(1.06); }
    .ed-masonry-overlay {
        position: absolute;
        inset: 0;
        background: linear-gradient(to top, rgba(10,31,68,0.75) 0%, transparent 55%);
        opacity: 0;
        transition: opacity 0.4s ease;
    }
    .ed-masonry-item:hover .ed-masonry-overlay { opacity: 1; }
    .ed-masonry-caption {
        position: absolute;
        bottom: 18px;
        left: 18px;
        z-index: 2;
        color: #FFFFFF;
        font-weight: 700;
        font-size: 1rem;
        opacity: 0;
        transform: translateY(10px);
        transition: all 0.4s ease;
    }
    .ed-masonry-item:hover .ed-masonry-caption { opacity: 1; transform: translateY(0); }
    .ed-masonry-item-large { grid-column: span 2; grid-row: span 2; }
    .ed-masonry-item-tall  { grid-row: span 2; }
    .ed-masonry-item-wide  { grid-column: span 2; }

    .ed-timeline-section {
        display: grid;
        grid-template-columns: 1fr 2fr;
        gap: 72px;
        padding: 72px 0;
        border-top: 2px solid #F1F5F9;
        margin-bottom: 72px;
    }
    .ed-timeline-left h2 {
        font-size: 3rem;
        font-weight: 900;
        line-height: 1.08;
        margin: 0 0 20px;
        letter-spacing: -0.04em;
        color: #0A1F44;
    }
    .ed-timeline-left p {
        color: #64748B;
        font-size: 1.05rem;
        line-height: 1.7;
        font-weight: 500;
        margin: 0;
    }
    .ed-timeline-right {
        display: flex;
        flex-direction: column;
        gap: 44px;
        padding-top: 8px;
    }
    .ed-timeline-node {
        display: flex;
        gap: 32px;
        align-items: flex-start;
    }
    .ed-timeline-big-num {
        font-size: 4.5rem;
        font-weight: 900;
        color: #FF5200;
        line-height: 0.85;
        letter-spacing: -0.05em;
        min-width: 130px;
        text-align: right;
        flex-shrink: 0;
    }
    .ed-timeline-content h4 {
        font-size: 1.4rem;
        font-weight: 800;
        margin: 0 0 10px;
        color: #0A1F44;
        letter-spacing: -0.02em;
    }
    .ed-timeline-content p {
        font-size: 1rem;
        color: #64748B;
        line-height: 1.65;
        margin: 0;
    }

    .ed-team-section { padding-bottom: 100px; }
    .ed-team-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 20px;
        margin-top: 28px;
    }
    .ed-team-card {
        background: #FFFFFF;
        border: 1.5px solid #E2E8F0;
        border-radius: 20px;
        padding: 28px 28px 24px;
        transition: box-shadow 0.3s ease, transform 0.3s ease;
    }
    .ed-team-card:hover {
        box-shadow: 0 12px 40px rgba(10,31,68,0.1);
        transform: translateY(-4px);
    }
    .ed-team-role {
        font-size: 0.68rem;
        font-weight: 800;
        text-transform: uppercase;
        letter-spacing: 0.14em;
        color: #FF5200;
        margin-bottom: 8px;
    }
    .ed-team-name {
        font-size: 1.25rem;
        font-weight: 800;
        color: #0A1F44;
        letter-spacing: -0.02em;
        margin-bottom: 10px;
    }
    .ed-team-desc {
        font-size: 0.9rem;
        color: #64748B;
        line-height: 1.6;
    }
    .ed-team-badge {
        display: inline-block;
        margin-top: 14px;
        font-size: 0.72rem;
        font-weight: 700;
        color: #0A1F44;
        background: #F1F5F9;
        padding: 3px 10px;
        border-radius: 999px;
    }
    
    /* Video Container Styling */
    .video-container-wrapper {
        border-radius: 16px;
        overflow: hidden;
        box-shadow: 0 10px 30px rgba(10,31,68,0.15);
        margin-bottom: 24px;
        border: 2px solid #E2E8F0;
        background: #0F172A;
    }
    .video-container-horizontal {
        border-radius: 12px;
        overflow: hidden;
        box-shadow: 0 4px 15px rgba(10,31,68,0.1);
        border: 1px solid #E2E8F0;
        background: #0F172A;
    }

    /* HERO VIDEO - màn hình lớn ở đầu trang */
    .hero-video-wrapper {
        position: relative;
        width: 100%;
        aspect-ratio: 21 / 9;
        border-radius: 20px;
        overflow: hidden;
        background: linear-gradient(135deg, #0A1F44 0%, #14345E 100%);
        box-shadow: 0 20px 50px rgba(10,31,68,0.25);
        border: 1px solid rgba(255,255,255,0.08);
    }
    .hero-video {
        width: 100%;
        height: 100%;
        object-fit: cover;
        display: block;
    }
    .hero-video-overlay {
        position: absolute;
        inset: 0;
        background: linear-gradient(180deg, rgba(10,31,68,0.0) 0%, rgba(10,31,68,0.0) 40%, rgba(10,31,68,0.75) 100%);
        display: flex;
        flex-direction: column;
        justify-content: flex-end;
        align-items: flex-start;
        padding: 32px 40px;
        pointer-events: none;
    }
    .hero-play-icon {
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        width: 90px;
        height: 90px;
        border-radius: 50%;
        background: rgba(255,82,0,0.92);
        color: #fff;
        font-size: 32px;
        display: flex;
        align-items: center;
        justify-content: center;
        padding-left: 8px;
        box-shadow: 0 8px 24px rgba(255,82,0,0.5);
        opacity: 0.85;
        transition: all 0.3s ease;
    }
    .hero-video-wrapper:hover .hero-play-icon {
        transform: translate(-50%, -50%) scale(1.08);
        opacity: 1;
    }
    .hero-video-caption {
        display: flex;
        flex-direction: column;
        gap: 6px;
    }
    .hero-video-kicker {
        font-size: 0.72rem;
        font-weight: 800;
        letter-spacing: 0.18em;
        text-transform: uppercase;
        color: #FF8C42;
    }
    .hero-video-title {
        font-size: 1.8rem;
        font-weight: 900;
        color: #fff;
        letter-spacing: -0.02em;
        line-height: 1.1;
    }

    /* SHORTS ROW - 4 video ngang */
    .shorts-row {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 14px;
        margin-bottom: 24px;
    }
    @media (max-width: 900px) {
        .shorts-row { grid-template-columns: repeat(2, 1fr); }
    }
    .short-card {
        position: relative;
        aspect-ratio: 9 / 16;
        border-radius: 14px;
        overflow: hidden;
        background: #0F172A;
        box-shadow: 0 6px 18px rgba(10,31,68,0.15);
        cursor: pointer;
        transition: transform 0.35s ease, box-shadow 0.35s ease;
    }
    .short-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 14px 32px rgba(10,31,68,0.25);
    }
    .short-video {
        width: 100%;
        height: 100%;
        object-fit: cover;
        display: block;
    }
    .short-overlay {
        position: absolute;
        inset: 0;
        background: linear-gradient(180deg, rgba(0,0,0,0.0) 50%, rgba(0,0,0,0.65) 100%);
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        align-items: center;
        padding: 14px 10px;
        pointer-events: none;
    }
    .short-play {
        width: 44px;
        height: 44px;
        border-radius: 50%;
        background: rgba(255,255,255,0.92);
        color: #0A1F44;
        font-size: 16px;
        display: flex;
        align-items: center;
        justify-content: center;
        padding-left: 3px;
        margin-top: auto;
        opacity: 0.9;
        transition: all 0.3s ease;
    }
    .short-card:hover .short-play {
        background: #FF5200;
        color: #fff;
        transform: scale(1.1);
    }
    .short-label {
        font-size: 0.78rem;
        font-weight: 700;
        color: #fff;
        text-align: center;
        text-shadow: 0 1px 4px rgba(0,0,0,0.6);
    }
    </style>
    """

    st.markdown(css, unsafe_allow_html=True)

    # 1. HERO SECTION
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

    # 2. MAIN VIDEO SECTION
    st.markdown("""
    <div class="ed-container">
        <div class="ed-section-header" style="margin-top: 0; margin-bottom: 20px;">
            <h2 class="ed-section-title">EES 2026 — Highlight Reel</h2>
            <span class="ed-section-tag">Main Video</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    main_video_url = "https://res.cloudinary.com/dd7gti2kn/video/upload/v1780389451/LOGO%20GHN/Action_video_dgq3f7.mp4"

    # 2. HERO VIDEO SECTION (màn hình lớn với autoplay + overlay)
    st.markdown(f"""
    <div class="ed-container">
        <div class="ed-section-header" style="margin-top: 20px; margin-bottom: 20px;">
            <h2 class="ed-section-title">EES 2026 — Highlight Reel</h2>
            <span class="ed-section-tag">Main Video</span>
        </div>
        <div class="hero-video-wrapper">
            <video class="hero-video" autoplay muted loop playsinline poster="">
                <source src="{main_video_url}" type="video/mp4">
                Trình duyệt không hỗ trợ video.
            </video>
            <div class="hero-video-overlay">
                <div class="hero-play-icon">▶</div>
                <div class="hero-video-caption">
                    <span class="hero-video-kicker">EES 2026</span>
                    <span class="hero-video-title">Hành trình gắn kết toàn GHN</span>
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 3. HORIZONTAL SHORTS VIDEOS
    st.markdown("""
    <div class="ed-container">
        <div class="ed-section-header" style="margin-top: 40px; margin-bottom: 20px;">
            <h2 class="ed-section-title" style="font-size: 1.5rem;">Khoảnh khắc đáng nhớ</h2>
            <span class="ed-section-tag">Shorts</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    v1_url = "https://res.cloudinary.com/dd7gti2kn/video/upload/v1780395113/LOGO%20GHN/IMG_0734_nhqt02.mp4"
    v2_url = "https://res.cloudinary.com/dd7gti2kn/video/upload/v1780393976/LOGO%20GHN/IMG_1233_wgzajm.mp4"
    v3_url = "https://res.cloudinary.com/dd7gti2kn/video/upload/v1780393954/LOGO%20GHN/IMG_1232_ykz6pz.mp4"
    v4_url = "https://res.cloudinary.com/dd7gti2kn/video/upload/v1780393907/LOGO%20GHN/IMG_1723_gdh1gs.mp4"

    shorts_html = f"""
    <div class="ed-container">
        <div class="shorts-row">
            <div class="short-card">
                <video class="short-video" muted loop playsinline preload="metadata">
                    <source src="{v1_url}" type="video/mp4">
                </video>
                <div class="short-overlay">
                    <div class="short-play">▶</div>
                    <div class="short-label">Khoảnh khắc 1</div>
                </div>
            </div>
            <div class="short-card">
                <video class="short-video" muted loop playsinline preload="metadata">
                    <source src="{v2_url}" type="video/mp4">
                </video>
                <div class="short-overlay">
                    <div class="short-play">▶</div>
                    <div class="short-label">Khoảnh khắc 2</div>
                </div>
            </div>
            <div class="short-card">
                <video class="short-video" muted loop playsinline preload="metadata">
                    <source src="{v3_url}" type="video/mp4">
                </video>
                <div class="short-overlay">
                    <div class="short-play">▶</div>
                    <div class="short-label">Khoảnh khắc 3</div>
                </div>
            </div>
            <div class="short-card">
                <video class="short-video" muted loop playsinline preload="metadata">
                    <source src="{v4_url}" type="video/mp4">
                </video>
                <div class="short-overlay">
                    <div class="short-play">▶</div>
                    <div class="short-label">Khoảnh khắc 4</div>
                </div>
            </div>
        </div>
    </div>
    <script>
    document.querySelectorAll('.short-card').forEach(card => {{
        const video = card.querySelector('video');
        card.addEventListener('mouseenter', () => video.play().catch(() => {{}}));
        card.addEventListener('mouseleave', () => {{ video.pause(); video.currentTime = 0; }});
    }});
    </script>
    """
    st.markdown(shorts_html, unsafe_allow_html=True)

    # 4. GALLERY & REMAINDER OF PAGE
    st.markdown(f"""
    <div class="ed-container">
        <div class="ed-section-header">
            <h2 class="ed-section-title">Góc nhìn hậu trường</h2>
            <span class="ed-section-tag">Team EX Showcase</span>
        </div>
        <div class="ed-masonry">
            <div class="ed-masonry-item ed-masonry-item-large">
                <img src="{img1}" alt="CPO ngang">
                <div class="ed-masonry-overlay"></div>
                <div class="ed-masonry-caption">Thảo luận chiến lược (CPO Kick-off)</div>
            </div>
            <div class="ed-masonry-item">
                <img src="{img2}" alt="Không khí làm việc">
                <div class="ed-masonry-overlay"></div>
                <div class="ed-masonry-caption">Không khí làm việc</div>
            </div>
            <div class="ed-masonry-item ed-masonry-item-tall">
                <img src="{img3}" alt="Giám đốc vùng">
                <div class="ed-masonry-overlay"></div>
                <div class="ed-masonry-caption">Chia sẻ từ Lãnh đạo</div>
            </div>
            <div class="ed-masonry-item ed-masonry-item-wide">
                <img src="{img4}" alt="Chiến dịch EES RACE">
                <div class="ed-masonry-overlay"></div>
                <div class="ed-masonry-caption">Chiến dịch EES RACE</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 5. TIMELINE SECTION
    st.markdown("""
    <div class="ed-container">
        <div class="ed-timeline-section">
            <div class="ed-timeline-left">
                <h2>Nhìn lại<br>Hành trình</h2>
                <p>Những con số và dấu mốc đại diện cho khối lượng công việc khổng lồ mà Team đã thực hiện để biến dữ liệu thô thành các nhóm hành động chiến lược.</p>
            </div>
            <div class="ed-timeline-right">
                <div class="ed-timeline-node">
                    <div class="ed-timeline-big-num">14</div>
                    <div class="ed-timeline-content">
                        <h4>Ngày Khảo Sát Thần Tốc</h4>
                        <p>Phối hợp với các khối Vận hành trên toàn quốc để thu thập hơn 20,000 mẫu trong thời gian kỷ lục.</p>
                    </div>
                </div>
                <div class="ed-timeline-node">
                    <div class="ed-timeline-big-num">300+</div>
                    <div class="ed-timeline-content">
                        <h4>Giờ Xử Lý &amp; Làm Sạch Data</h4>
                        <p>Chuẩn hóa dữ liệu thô, map với hệ thống HRIS và thiết lập cấu trúc phân nhóm (Division/Section) không tì vết.</p>
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

    # 6. TEAM SECTION
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
                    <div class="ed-team-name">Team EX / C&amp;B</div>
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
                    <div class="ed-team-role">Dashboard &amp; Storytelling</div>
                    <div class="ed-team-name">Team Data Visualization</div>
                    <div class="ed-team-desc">Xây dựng nền tảng dashboard tương tác, trực quan hóa insight và truyền tải câu chuyện dữ liệu đến ban lãnh đạo.</div>
                    <span class="ed-team-badge">Streamlit · Plotly</span>
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

