import streamlit as st
from shared.plotly_theme import apply_theme

def render():
    apply_theme()

    import textwrap
    st.markdown(textwrap.dedent(
        """
        <style>
        /* Base Typography Reset */
        .ed-container { 
            font-family: 'Inter', sans-serif; 
            color: #0A1F44; 
            padding-bottom: 100px;
        }

        /* 1. Slim Hero Section */
        .ed-hero { margin-bottom: 60px; }
        .ed-kicker { 
            font-size: 0.75rem; 
            font-weight: 800; 
            letter-spacing: 0.15em; 
            text-transform: uppercase; 
            color: #FF5200; 
            margin-bottom: 16px; 
            display: block; 
        }
        .ed-headline { 
            font-size: 4rem; 
            font-weight: 900; 
            letter-spacing: -0.04em; 
            line-height: 1.05; 
            margin: 0 0 40px; 
            color: #0A1F44; 
            max-width: 1000px;
        }
        .ed-metrics-grid { 
            display: grid; 
            grid-template-columns: repeat(4, 1fr); 
            gap: 24px; 
            padding-top: 32px; 
            border-top: 2px solid #E2E8F0; 
        }
        .ed-metric-item { display: flex; flex-direction: column; }
        .ed-metric-label { 
            font-size: 0.75rem; 
            font-weight: 700; 
            text-transform: uppercase; 
            letter-spacing: 0.1em; 
            color: #64748B; 
            margin-bottom: 10px; 
        }
        .ed-metric-val { 
            font-size: 2.6rem; 
            font-weight: 900; 
            color: #0A1F44; 
            letter-spacing: -0.03em; 
            line-height: 1; 
        }
        .ed-metric-sub {
            font-size: 0.85rem;
            color: #94A3B8;
            margin-top: 8px;
            font-weight: 500;
        }

        /* 2. Video Player Placeholder */
        .ed-video-section { margin-bottom: 80px; }
        .ed-video-wrapper { 
            position: relative; 
            width: 100%; 
            aspect-ratio: 21 / 9; 
            background: #0F172A; 
            border-radius: 24px; 
            overflow: hidden; 
            box-shadow: 0 40px 80px rgba(10,31,68,0.15); 
            display: flex; 
            align-items: center; 
            justify-content: center; 
            flex-direction: column; 
            background-image: url('https://images.unsplash.com/photo-1540317580384-e5d43616b9aa?auto=format&fit=crop&w=2000&q=80');
            background-size: cover;
            background-position: center;
        }
        .ed-video-wrapper::before { 
            content: ''; 
            position: absolute; 
            inset: 0; 
            background: linear-gradient(to top, rgba(10,31,68,0.9) 0%, rgba(10,31,68,0.2) 100%); 
            pointer-events: none; 
        }
        .ed-play-btn { 
            width: 90px; 
            height: 90px; 
            background: rgba(255,255,255,0.1); 
            backdrop-filter: blur(12px); 
            border-radius: 999px; 
            display: flex; 
            align-items: center; 
            justify-content: center; 
            border: 1px solid rgba(255,255,255,0.3); 
            transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1); 
            cursor: pointer; 
            z-index: 2;
        }
        .ed-play-btn:hover { 
            transform: scale(1.1); 
            background: rgba(255,255,255,0.25); 
            border-color: #FFFFFF;
        }
        .ed-play-triangle { 
            width: 0; 
            height: 0; 
            border-top: 14px solid transparent; 
            border-bottom: 14px solid transparent; 
            border-left: 24px solid #FFFFFF; 
            margin-left: 8px; 
        }
        .ed-video-caption { 
            position: absolute; 
            bottom: 40px; 
            left: 50px; 
            color: #FFFFFF; 
            z-index: 2;
        }
        .ed-video-caption h3 { 
            font-size: 2rem; 
            font-weight: 800; 
            margin: 0 0 10px; 
            letter-spacing: -0.02em;
        }
        .ed-video-caption p { 
            font-size: 1.05rem; 
            color: rgba(255,255,255,0.8); 
            margin: 0; 
            font-weight: 500;
        }

        /* 3. Masonry Gallery */
        .ed-gallery-section { margin-bottom: 80px; }
        .ed-section-title { 
            font-size: 2.4rem; 
            font-weight: 900; 
            letter-spacing: -0.04em; 
            color: #0A1F44; 
            margin: 0 0 32px; 
            display: flex;
            align-items: baseline;
            justify-content: space-between;
        }
        .ed-section-title span {
            font-size: 1rem;
            font-weight: 700;
            color: #FF5200;
            text-transform: uppercase;
            letter-spacing: 0.1em;
        }
        .ed-masonry { 
            display: grid; 
            grid-template-columns: repeat(4, 1fr); 
            grid-auto-rows: 220px; 
            gap: 20px; 
        }
        .ed-masonry-item { 
            border-radius: 20px; 
            overflow: hidden; 
            position: relative; 
            background: #F8FAFC; 
        }
        .ed-masonry-item img { 
            width: 100%; 
            height: 100%; 
            object-fit: cover; 
            transition: transform 0.8s cubic-bezier(0.4, 0, 0.2, 1); 
        }
        .ed-masonry-item:hover img { transform: scale(1.08); }
        .ed-masonry-item::after { 
            content: ''; 
            position: absolute; 
            inset: 0; 
            background: linear-gradient(to top, rgba(10,31,68,0.8) 0%, transparent 50%); 
            opacity: 0; 
            transition: opacity 0.4s ease; 
        }
        .ed-masonry-item:hover::after { opacity: 1; }
        .ed-masonry-item-large { grid-column: span 2; grid-row: span 2; }
        .ed-masonry-item-tall { grid-row: span 2; }
        .ed-masonry-item-wide { grid-column: span 2; }
        .ed-masonry-caption { 
            position: absolute; 
            bottom: 24px; 
            left: 24px; 
            z-index: 2; 
            color: #FFFFFF; 
            font-weight: 800; 
            font-size: 1.2rem; 
            opacity: 0; 
            transform: translateY(15px); 
            transition: all 0.4s ease; 
        }
        .ed-masonry-item:hover .ed-masonry-caption { opacity: 1; transform: translateY(0); }

        /* 4. Typography Timeline */
        .ed-timeline-section { 
            display: grid; 
            grid-template-columns: 1fr 2fr; 
            gap: 80px; 
            padding: 80px 0; 
            border-top: 2px solid #F1F5F9; 
        }
        .ed-timeline-left h2 { 
            font-size: 3.5rem; 
            font-weight: 900; 
            line-height: 1.05; 
            margin: 0 0 24px; 
            letter-spacing: -0.04em; 
            color: #0A1F44;
        }
        .ed-timeline-left p { 
            color: #64748B; 
            font-size: 1.15rem; 
            line-height: 1.7; 
            font-weight: 500;
        }
        .ed-timeline-right { 
            display: flex; 
            flex-direction: column; 
            gap: 50px; 
            padding-top: 10px;
        }
        .ed-timeline-node { 
            display: flex; 
            gap: 40px; 
        }
        .ed-timeline-big-num { 
            font-size: 5rem; 
            font-weight: 900; 
            color: #FF5200; 
            line-height: 0.8; 
            letter-spacing: -0.05em; 
            min-width: 140px; 
            text-align: right;
        }
        .ed-timeline-content h4 { 
            font-size: 1.6rem; 
            font-weight: 800; 
            margin: 0 0 12px; 
            color: #0A1F44; 
            letter-spacing: -0.02em;
        }
        .ed-timeline-content p { 
            font-size: 1.05rem; 
            color: #64748B; 
            line-height: 1.65; 
            margin: 0; 
        }
        </style>
        """),
        unsafe_allow_html=True,
    )

    import textwrap
    st.markdown(textwrap.dedent(
        """
        <div class="ed-container">
            <!-- HERO SECTION -->
            <div class="ed-hero">
                <span class="ed-kicker">Employee Engagement Survey 2026</span>
                <h1 class="ed-headline">Dấu ấn hành trình EES 2026 & Những nỗ lực từ phía sau</h1>
                
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
                        <span class="ed-metric-sub">+17.8% so với 2025</span>
                    </div>
                    <div class="ed-metric-item">
                        <span class="ed-metric-label">Mức gắn kết</span>
                        <span class="ed-metric-val">72.3</span>
                        <span class="ed-metric-sub">Điểm EI tổng thể</span>
                    </div>
                </div>
            </div>

            <!-- VIDEO HIGHLIGHT -->
            <div class="ed-video-section">
                <div class="ed-video-wrapper">
                    <div class="ed-play-btn">
                        <div class="ed-play-triangle"></div>
                    </div>
                    <div class="ed-video-caption">
                        <h3>EES 2026 Highlight Reel</h3>
                        <p>Xem lại những khoảnh khắc đáng nhớ trong chuỗi ngày triển khai khảo sát.</p>
                    </div>
                </div>
            </div>

            <!-- MASONRY GALLERY -->
            <div class="ed-gallery-section">
                <h2 class="ed-section-title">
                    Góc nhìn hậu trường
                    <span>Team EX Showcase</span>
                </h2>
                <div class="ed-masonry">
                    <div class="ed-masonry-item ed-masonry-item-large">
                        <img src="https://images.unsplash.com/photo-1515169067868-5387ec356754?auto=format&fit=crop&w=800&q=80" alt="Behind the scenes">
                        <div class="ed-masonry-caption">Thảo luận chiến lược</div>
                    </div>
                    <div class="ed-masonry-item">
                        <img src="https://images.unsplash.com/photo-1542744173-8e7e53415bb0?auto=format&fit=crop&w=600&q=80" alt="Data analysis">
                        <div class="ed-masonry-caption">Xử lý Data</div>
                    </div>
                    <div class="ed-masonry-item ed-masonry-item-tall">
                        <img src="https://images.unsplash.com/photo-1552664730-d307ca884978?auto=format&fit=crop&w=600&q=80" alt="Team meeting">
                        <div class="ed-masonry-caption">Kick-off Sự kiện</div>
                    </div>
                    <div class="ed-masonry-item ed-masonry-item-wide">
                        <img src="https://images.unsplash.com/photo-1551434678-e076c223a692?auto=format&fit=crop&w=800&q=80" alt="Workshop">
                        <div class="ed-masonry-caption">Workshop Điều phối</div>
                    </div>
                </div>
            </div>

            <!-- TYPOGRAPHY TIMELINE -->
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
                            <h4>Giờ Xử Lý & Làm Sạch Data</h4>
                            <p>Chuẩn hóa dữ liệu thô, map với hệ thống HRIS và thiết lập cấu trúc phân nhóm (Division/Section) không tì vết.</p>
                        </div>
                    </div>
                    <div class="ed-timeline-node">
                        <div class="ed-timeline-big-num">01</div>
                        <div class="ed-timeline-content">
                            <h4>Nền Tảng Dashboard Duy Nhất</h4>
                            <p>Hội tụ toàn bộ báo cáo, phân tích chéo và câu chuyện dữ liệu (Storytelling) vào chung một giao diện thông minh.</p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        """),
        unsafe_allow_html=True,
    )
