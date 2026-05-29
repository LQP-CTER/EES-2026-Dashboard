import streamlit as st

from shared.plotly_theme import apply_theme


def render():
    apply_theme()

    st.markdown(
        """
        <style>
        .ees-overview-hero {
            position: relative;
            overflow: hidden;
            border-radius: 24px;
            background:
                radial-gradient(circle at top right, rgba(255, 82, 0, 0.18), transparent 30%),
                radial-gradient(circle at left center, rgba(29, 78, 216, 0.12), transparent 28%),
                linear-gradient(135deg, #07162f 0%, #0a1f44 55%, #111827 100%);
            border: 1px solid rgba(255,255,255,0.08);
            box-shadow: 0 18px 50px rgba(2, 6, 23, 0.18);
            padding: 34px;
            margin-bottom: 24px;
        }
        .ees-overview-hero::after {
            content: '';
            position: absolute;
            inset: 0;
            background: linear-gradient(120deg, rgba(255,255,255,0.06), transparent 38%, transparent 62%, rgba(255,255,255,0.04));
            pointer-events: none;
        }
        .ees-overview-kicker {
            display: inline-flex;
            align-items: center;
            gap: 8px;
            padding: 6px 12px;
            border-radius: 999px;
            background: rgba(255,255,255,0.08);
            color: #E2E8F0;
            font-size: 0.72rem;
            font-weight: 700;
            letter-spacing: 0.08em;
            text-transform: uppercase;
            margin-bottom: 16px;
        }
        .ees-overview-title {
            color: #FFFFFF;
            font-size: 2.1rem;
            font-weight: 900;
            letter-spacing: -0.04em;
            line-height: 1.12;
            margin: 0 0 12px;
            max-width: 820px;
        }
        .ees-overview-subtitle {
            color: #CBD5E1;
            font-size: 0.96rem;
            line-height: 1.7;
            max-width: 840px;
            margin-bottom: 24px;
        }
        .ees-overview-grid {
            display: grid;
            grid-template-columns: repeat(4, minmax(0, 1fr));
            gap: 14px;
        }
        .ees-overview-card {
            background: rgba(255,255,255,0.06);
            border: 1px solid rgba(255,255,255,0.09);
            border-radius: 18px;
            padding: 18px;
            backdrop-filter: blur(10px);
            min-height: 132px;
        }
        .ees-overview-card .label {
            color: #94A3B8;
            font-size: 0.68rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.12em;
            margin-bottom: 10px;
        }
        .ees-overview-card .value {
            color: #FFFFFF;
            font-size: 1.2rem;
            font-weight: 800;
            margin-bottom: 8px;
        }
        .ees-overview-card .desc {
            color: #CBD5E1;
            font-size: 0.84rem;
            line-height: 1.6;
        }
        .ees-section-shell {
            background: #FFFFFF;
            border: 1px solid #E2E8F0;
            border-radius: 18px;
            padding: 22px;
            box-shadow: 0 1px 3px rgba(15, 23, 42, 0.05);
            margin-bottom: 18px;
        }
        .ees-section-title {
            font-size: 0.92rem;
            font-weight: 800;
            color: #0A1F44;
            margin: 0 0 6px;
        }
        .ees-section-desc {
            color: #64748B;
            font-size: 0.84rem;
            line-height: 1.65;
            margin-bottom: 0;
        }
        .ees-placeholder-panel {
            border-radius: 16px;
            border: 1px dashed #CBD5E1;
            background: linear-gradient(180deg, #F8FAFC 0%, #FFFFFF 100%);
            padding: 18px;
            min-height: 160px;
        }
        .ees-placeholder-item {
            display: flex;
            gap: 12px;
            align-items: flex-start;
            padding: 14px 0;
            border-bottom: 1px solid #EEF2F7;
        }
        .ees-placeholder-item:last-child { border-bottom: none; }
        .ees-dot {
            width: 10px;
            height: 10px;
            margin-top: 6px;
            border-radius: 999px;
            background: linear-gradient(135deg, #FF5200, #F97316);
            box-shadow: 0 0 0 5px rgba(255, 82, 0, 0.08);
            flex: 0 0 auto;
        }
        .ees-placeholder-item strong {
            color: #0F172A;
            font-size: 0.88rem;
        }
        .ees-placeholder-item p {
            margin: 4px 0 0;
            color: #64748B;
            font-size: 0.84rem;
            line-height: 1.6;
        }
        .ees-mini-grid {
            display: grid;
            grid-template-columns: repeat(2, minmax(0, 1fr));
            gap: 12px;
            margin-top: 12px;
        }
        .ees-mini-item {
            border-radius: 16px;
            padding: 16px;
            border: 1px solid #E2E8F0;
            background: linear-gradient(180deg, #FFFFFF 0%, #F8FAFC 100%);
        }
        .ees-mini-item .tag {
            font-size: 0.68rem;
            letter-spacing: 0.1em;
            text-transform: uppercase;
            font-weight: 700;
            color: #64748B;
        }
        .ees-mini-item .title {
            font-size: 0.96rem;
            font-weight: 800;
            color: #0F172A;
            margin-top: 6px;
        }
        .ees-mini-item .body {
            color: #64748B;
            font-size: 0.84rem;
            line-height: 1.6;
            margin-top: 6px;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="ees-overview-hero">
            <div class="ees-overview-kicker">Overview EES 2026 · Executive Summary</div>
            <div class="ees-overview-title">Bức tranh tổng quan EES 2026</div>
            <div class="ees-overview-subtitle">
                Tab này dành riêng cho phần tóm tắt điều hành: team đã làm gì cho EES 2026, những trục phân tích chéo cần đọc cùng nhau,
                và các khoảng trống nội dung sẽ được bổ sung dần. Hiện tại đây là một sườn nền tảng sạch, sang, sẵn sàng để fill thông tin sau.
            </div>
            <div class="ees-overview-grid">
                <div class="ees-overview-card">
                    <div class="label">Nhân sự</div>
                    <div class="value">21,353</div>
                    <div class="desc">Quy mô toàn tổ chức</div>
                </div>
                <div class="ees-overview-card">
                    <div class="label">Phản hồi</div>
                    <div class="value">20,005</div>
                    <div class="desc">Mẫu khảo sát hợp lệ</div>
                </div>
                <div class="ees-overview-card">
                    <div class="label">Tỷ lệ phản hồi</div>
                    <div class="value">93.7%</div>
                    <div class="desc">So với benchmark 2025: +17.8%</div>
                </div>
                <div class="ees-overview-card">
                    <div class="label">Mức gắn kết</div>
                    <div class="value">72.3</div>
                    <div class="desc">EI tổng thể · -7.9 so với 2025</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    left, right = st.columns([1.05, 0.95])
    with left:
        st.markdown(
            """
            <div class="ees-section-shell">
                <div class="ees-section-title">Team đã làm gì cho EES 2026</div>
                <p class="ees-section-desc">
                    Đây là nơi gom các đầu việc chính của team: chuẩn hóa dữ liệu, xây dựng logic phân tích, tạo dashboard, thiết kế
                    các lớp so sánh chéo, và đóng gói các insight để leadership đọc nhanh hơn.
                </p>
                <div class="ees-mini-grid">
                    <div class="ees-mini-item">
                        <div class="tag">01 · Data foundation</div>
                        <div class="title">Chuẩn hóa & làm sạch dữ liệu</div>
                        <div class="body">Tạo nền dữ liệu tin cậy để chạy các phân tích theo nhóm, trụ cột và nhân khẩu học.</div>
                    </div>
                    <div class="ees-mini-item">
                        <div class="tag">02 · Cross analysis</div>
                        <div class="title">Phân tích chéo đa lớp</div>
                        <div class="body">Kết nối survey với division, department, section, tenure và các chỉ số phản hồi.</div>
                    </div>
                    <div class="ees-mini-item">
                        <div class="tag">03 · Storytelling</div>
                        <div class="title">Kể chuyện bằng insight</div>
                        <div class="body">Biến dữ liệu thành narrative điều hành, giúp nhìn ra ưu tiên và rủi ro nhanh hơn.</div>
                    </div>
                    <div class="ees-mini-item">
                        <div class="tag">04 · Actionability</div>
                        <div class="title">Định hướng hành động</div>
                        <div class="body">Chuyển insight thành các nhóm can thiệp và đề xuất hành động cụ thể.</div>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with right:
        st.markdown(
            """
            <div class="ees-section-shell">
                <div class="ees-section-title">Khung nội dung để fill sau</div>
                <p class="ees-section-desc">
                    Khi có nội dung chính thức, bạn chỉ cần thay phần placeholder này bằng timeline, KPI, ảnh chiến dịch hoặc thông điệp từ team.
                </p>
                <div style="height:14px"></div>
                <div class="ees-placeholder-panel">
                    <div class="ees-placeholder-item">
                        <span class="ees-dot"></span>
                        <div>
                            <strong>Timeline triển khai</strong>
                            <p>Giai đoạn khảo sát, xử lý dữ liệu, phân tích, và hoàn thiện dashboard.</p>
                        </div>
                    </div>
                    <div class="ees-placeholder-item">
                        <span class="ees-dot"></span>
                        <div>
                            <strong>Deliverables chính</strong>
                            <p>Dashboard, báo cáo narrative, phần giải thích chỉ số, và đề xuất hành động.</p>
                        </div>
                    </div>
                    <div class="ees-placeholder-item">
                        <span class="ees-dot"></span>
                        <div>
                            <strong>Điểm nhấn chiến lược</strong>
                            <p>Những phát hiện cross-analysis nổi bật, các vùng rủi ro và cơ hội can thiệp.</p>
                        </div>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
