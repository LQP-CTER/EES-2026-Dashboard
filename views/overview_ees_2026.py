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
            grid-template-columns: repeat(3, minmax(0, 1fr));
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
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="ees-overview-hero">
            <div class="ees-overview-kicker">Overview EES 2026</div>
            <div class="ees-overview-title">Bức tranh tổng quan về hành trình EES 2026 của team</div>
            <div class="ees-overview-subtitle">
                Tab này được đặt trước <strong>Tổng quan GHN</strong> để làm trang mở đầu chiến lược: thể hiện team đã làm gì cho EES 2026,
                các mảng đã hoàn thiện, các điểm cần theo dõi, và khung nội dung để bạn bổ sung thông tin sau này.
            </div>
            <div class="ees-overview-grid">
                <div class="ees-overview-card">
                    <div class="label">Mục tiêu</div>
                    <div class="value">One-page executive intro</div>
                    <div class="desc">Trình bày nhanh bối cảnh, định hướng, và giá trị mà dashboard mang lại cho lãnh đạo.</div>
                </div>
                <div class="ees-overview-card">
                    <div class="label">Trạng thái</div>
                    <div class="value">Background sẵn sàng</div>
                    <div class="desc">Hiện ưu tiên phần nền trực quan, tạo khung chuẩn để chèn nội dung chiến dịch sau.</div>
                </div>
                <div class="ees-overview-card">
                    <div class="label">Vai trò tab</div>
                    <div class="value">Team delivery snapshot</div>
                    <div class="desc">Tóm lược những hạng mục team đã làm, các phân tích đã hoàn thiện và roadmap tiếp theo.</div>
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
                <div class="ees-section-title">Khung nội dung đề xuất</div>
                <p class="ees-section-desc">
                    Bạn có thể dùng tab này như trang landing tổng hợp của chiến dịch EES 2026: giới thiệu mục tiêu khảo sát,
                    phạm vi triển khai, các mốc xử lý dữ liệu, các layer phân tích, và những gì team đã đóng góp.
                </p>
                <div style="height:14px"></div>
                <div class="ees-placeholder-panel">
                    <div class="ees-placeholder-item">
                        <span class="ees-dot"></span>
                        <div>
                            <strong>Tổng quan chiến dịch EES 2026</strong>
                            <p>Tóm tắt mục tiêu, phạm vi, đơn vị tham gia và tinh thần của chương trình.</p>
                        </div>
                    </div>
                    <div class="ees-placeholder-item">
                        <span class="ees-dot"></span>
                        <div>
                            <strong>Team đã làm gì</strong>
                            <p>Mô tả các đầu việc: làm sạch dữ liệu, xây dựng dashboard, phân tích chéo, và phát hiện rủi ro.</p>
                        </div>
                    </div>
                    <div class="ees-placeholder-item">
                        <span class="ees-dot"></span>
                        <div>
                            <strong>Kết quả nổi bật</strong>
                            <p>Khi có dữ liệu, chèn các con số, insight, tác động và các nhóm cần ưu tiên hành động.</p>
                        </div>
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
                <div class="ees-section-title">Không gian cho nội dung sau này</div>
                <p class="ees-section-desc">
                    Đây là layout nền tối giản nhưng cao cấp, phù hợp để bạn bổ sung timeline, ảnh, biểu đồ, quote từ lãnh đạo hoặc các mốc triển khai.
                </p>
                <div style="height:14px"></div>
                <div style="display:grid;gap:12px;">
                    <div style="padding:16px;border-radius:16px;background:#0A1F44;color:#FFFFFF;box-shadow:0 10px 24px rgba(10,31,68,0.12);">
                        <div style="font-size:0.68rem;font-weight:700;letter-spacing:0.12em;text-transform:uppercase;color:#94A3B8;">Deliverables</div>
                        <div style="font-size:1.05rem;font-weight:800;margin-top:6px;">Dashboard · Narrative · Action Plan</div>
                        <div style="font-size:0.84rem;color:#CBD5E1;line-height:1.6;margin-top:8px;">Khung tổng hợp các đầu ra chính của team cho EES 2026.</div>
                    </div>
                    <div style="padding:16px;border-radius:16px;background:#FFF7ED;border:1px solid #FED7AA;">
                        <div style="font-size:0.68rem;font-weight:700;letter-spacing:0.12em;text-transform:uppercase;color:#9A3412;">Status</div>
                        <div style="font-size:1.05rem;font-weight:800;margin-top:6px;color:#9A3412;">Sẵn sàng fill dữ liệu</div>
                        <div style="font-size:0.84rem;color:#7C2D12;line-height:1.6;margin-top:8px;">Phần nền đã hoàn thiện, chỉ cần điền nội dung thực tế theo thời gian.</div>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
