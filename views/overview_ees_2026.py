import streamlit as st
from shared.plotly_theme import apply_theme

def render():
    apply_theme()

    full_html = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');

.ed-container {
    font-family: 'Inter', sans-serif;
    color: #0A1F44;
    padding-bottom: 100px;
    max-width: 1200px;
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

.ed-video-section { margin-bottom: 72px; }
.ed-video-wrapper {
    position: relative;
    width: 100%;
    aspect-ratio: 21 / 8;
    background: #0F172A;
    border-radius: 20px;
    overflow: hidden;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-direction: column;
    background-image: url('https://images.unsplash.com/photo-1540317580384-e5d43616b9aa?auto=format&fit=crop&w=2000&q=80');
    background-size: cover;
    background-position: center;
}
.ed-video-overlay {
    position: absolute;
    inset: 0;
    background: linear-gradient(135deg, rgba(10,31,68,0.85) 0%, rgba(10,31,68,0.3) 100%);
}
.ed-video-content {
    position: relative;
    z-index: 2;
    display: flex;
    align-items: center;
    gap: 40px;
    padding: 40px;
}
.ed-play-btn {
    flex-shrink: 0;
    width: 80px;
    height: 80px;
    background: rgba(255,82,0,0.9);
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    border: 3px solid rgba(255,255,255,0.3);
    cursor: pointer;
}
.ed-play-triangle {
    width: 0;
    height: 0;
    border-top: 12px solid transparent;
    border-bottom: 12px solid transparent;
    border-left: 20px solid #FFFFFF;
    margin-left: 6px;
}
.ed-video-text h3 {
    font-size: 1.8rem;
    font-weight: 800;
    color: #FFFFFF;
    margin: 0 0 8px;
    letter-spacing: -0.02em;
}
.ed-video-text p {
    font-size: 1rem;
    color: rgba(255,255,255,0.75);
    margin: 0;
    font-weight: 500;
    max-width: 500px;
}

.ed-gallery-section { margin-bottom: 72px; }
.ed-section-header {
    display: flex;
    align-items: baseline;
    justify-content: space-between;
    margin-bottom: 28px;
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

.ed-team-section { padding-bottom: 40px; }
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
</style>

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

    <div class="ed-video-section">
        <div class="ed-video-wrapper">
            <div class="ed-video-overlay"></div>
            <div class="ed-video-content">
                <div class="ed-play-btn">
                    <div class="ed-play-triangle"></div>
                </div>
                <div class="ed-video-text">
                    <h3>EES 2026 — Highlight Reel</h3>
                    <p>Xem lại những khoảnh khắc đáng nhớ trong chuỗi ngày triển khai khảo sát toàn GHN.</p>
                </div>
            </div>
        </div>
    </div>

    <div class="ed-gallery-section">
        <div class="ed-section-header">
            <h2 class="ed-section-title">Góc nhìn hậu trường</h2>
            <span class="ed-section-tag">Team EX Showcase</span>
        </div>
        <div class="ed-masonry">
            <div class="ed-masonry-item ed-masonry-item-large">
                <img src="https://images.unsplash.com/photo-1515169067868-5387ec356754?auto=format&fit=crop&w=800&q=80" alt="Strategy">
                <div class="ed-masonry-overlay"></div>
                <div class="ed-masonry-caption">Thảo luận chiến lược</div>
            </div>
            <div class="ed-masonry-item">
                <img src="https://images.unsplash.com/photo-1542744173-8e7e53415bb0?auto=format&fit=crop&w=600&q=80" alt="Data">
                <div class="ed-masonry-overlay"></div>
                <div class="ed-masonry-caption">Xử lý Data</div>
            </div>
            <div class="ed-masonry-item ed-masonry-item-tall">
                <img src="https://images.unsplash.com/photo-1552664730-d307ca884978?auto=format&fit=crop&w=600&q=80" alt="Meeting">
                <div class="ed-masonry-overlay"></div>
                <div class="ed-masonry-caption">Kick-off Sự kiện</div>
            </div>
            <div class="ed-masonry-item ed-masonry-item-wide">
                <img src="https://images.unsplash.com/photo-1551434678-e076c223a692?auto=format&fit=crop&w=800&q=80" alt="Workshop">
                <div class="ed-masonry-overlay"></div>
                <div class="ed-masonry-caption">Workshop Điều phối</div>
            </div>
        </div>
    </div>

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
"""
    st.components.v1.html(full_html, height=2800, scrolling=True)
