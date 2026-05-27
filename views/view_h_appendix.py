import streamlit as st


_APPENDIX_CSS = """
<style>
.apx-page-header {
    margin-bottom: 32px;
    padding-bottom: 24px;
    border-bottom: 1px solid #E2E8F0;
}
.apx-page-eyebrow {
    font-size: 0.63rem;
    font-weight: 700;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: #94A3B8;
    margin: 0 0 6px;
}
.apx-page-title {
    font-size: 1.55rem;
    font-weight: 800;
    color: #0A1F44;
    margin: 0 0 6px;
    letter-spacing: -0.025em;
    line-height: 1.25;
}
.apx-page-desc {
    font-size: 0.88rem;
    color: #64748B;
    margin: 0;
    font-weight: 500;
    line-height: 1.6;
}
.apx-context-box {
    background: #F8FAFC;
    border: 1px solid #E2E8F0;
    border-left: 3px solid #FF5200;
    border-radius: 10px;
    padding: 20px 24px;
    margin-bottom: 28px;
}
.apx-context-title {
    font-size: 0.92rem;
    font-weight: 700;
    color: #0A1F44;
    margin: 0 0 8px;
}
.apx-context-body {
    font-size: 0.85rem;
    color: #475569;
    line-height: 1.7;
    margin: 0;
}
.apx-sec-header {
    margin: 8px 0 20px;
    padding-bottom: 12px;
    border-bottom: 1px solid #F1F5F9;
}
.apx-sec-title {
    font-size: 1.05rem;
    font-weight: 700;
    color: #0A1F44;
    margin: 0 0 4px;
    display: flex;
    align-items: center;
    gap: 8px;
}
.apx-sec-accent {
    width: 3px;
    height: 16px;
    background: #FF5200;
    border-radius: 2px;
    display: inline-block;
    flex-shrink: 0;
}
.apx-sec-desc {
    font-size: 0.82rem;
    color: #64748B;
    margin: 0;
    font-weight: 500;
}
.apx-card {
    background: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 12px;
    padding: 0;
    margin-bottom: 16px;
    overflow: hidden;
    transition: border-color 0.15s ease, box-shadow 0.15s ease;
}
.apx-card:hover {
    border-color: #CBD5E1;
    box-shadow: 0 2px 8px rgba(0,0,0,0.04);
}
.apx-card-accent {
    height: 3px;
    width: 100%;
}
.apx-card-body {
    padding: 22px 24px;
}
.apx-card-title {
    font-size: 1rem;
    font-weight: 700;
    color: #0A1F44;
    margin: 0 0 2px;
    letter-spacing: -0.01em;
}
.apx-card-subtitle {
    font-size: 0.78rem;
    color: #94A3B8;
    font-weight: 500;
    margin: 0 0 16px;
}
.apx-label {
    font-size: 0.68rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: #94A3B8;
    margin: 0 0 6px;
}
.apx-desc {
    font-size: 0.85rem;
    color: #334155;
    line-height: 1.65;
    margin: 0 0 16px;
}
.apx-formula-box {
    background: #F8FAFC;
    border: 1px solid #E2E8F0;
    border-left: 3px solid #3B82F6;
    border-radius: 8px;
    padding: 14px 16px;
    margin-bottom: 14px;
    font-family: 'Consolas', 'SF Mono', 'Courier New', monospace;
    font-size: 0.82rem;
    color: #1E293B;
    line-height: 1.7;
}
.apx-note {
    font-size: 0.82rem;
    color: #475569;
    line-height: 1.6;
    margin: 0 0 14px;
}
.apx-meta-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 10px;
    margin-bottom: 14px;
}
.apx-meta-item {
    background: #F8FAFC;
    border: 1px solid #F1F5F9;
    border-radius: 8px;
    padding: 10px 12px;
}
.apx-meta-label {
    font-size: 0.65rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: #94A3B8;
    margin: 0 0 3px;
}
.apx-meta-value {
    font-size: 0.8rem;
    color: #334155;
    font-weight: 600;
    margin: 0;
}
.apx-cls-bar {
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
    margin-top: 4px;
}
.apx-pill {
    display: inline-flex;
    align-items: center;
    gap: 4px;
    padding: 3px 10px;
    border-radius: 20px;
    font-size: 0.72rem;
    font-weight: 600;
    white-space: nowrap;
}
.apx-pill-green  { background: #F0FDF4; color: #15803D; border: 1px solid #BBF7D0; }
.apx-pill-yellow { background: #FEFCE8; color: #A16207; border: 1px solid #FDE68A; }
.apx-pill-orange { background: #FFF7ED; color: #C2410C; border: 1px solid #FED7AA; }
.apx-pill-red    { background: #FEF2F2; color: #DC2626; border: 1px solid #FECACA; }
.apx-pill-blue   { background: #EFF6FF; color: #1D4ED8; border: 1px solid #BFDBFE; }
.apx-pill-gray   { background: #F8FAFC; color: #475569; border: 1px solid #E2E8F0; }
.apx-pill-purple { background: #FAF5FF; color: #7C3AED; border: 1px solid #DDD6FE; }
</style>
"""


def render(**kwargs):
    st.markdown(_APPENDIX_CSS, unsafe_allow_html=True)

    st.markdown("""
    <div class="apx-page-header">
        <p class="apx-page-eyebrow">Tham chiếu</p>
        <h1 class="apx-page-title">Phụ lục & Giải thích Chỉ số</h1>
        <p class="apx-page-desc">
            Tài liệu tham khảo chi tiết về ý nghĩa và công thức tính toán của tất cả các chỉ số được sử dụng trong Dashboard EES 2026.
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="apx-context-box">
        <p class="apx-context-title">Tại sao cần các chỉ số này?</p>
        <p class="apx-context-body">
            Các chỉ số EES không chỉ đơn thuần là điểm trung bình của khảo sát. Chúng được thiết kế dựa trên các mô hình 
            tâm lý học tổ chức (như <i>Job Demands-Resources Model</i>) để đo lường không chỉ <b>mức độ hài lòng</b> 
            mà còn cả <b>sự gắn kết sâu sắc</b>, <b>mức độ kiệt sức</b> và <b>rủi ro biến động nhân sự</b>.
        </p>
    </div>
    """, unsafe_allow_html=True)

    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "Chỉ số Cốt lõi",
        "Rủi ro & Gắn kết",
        "Phân tích Chuyên sâu",
        "Mô phỏng & Dự báo",
        "NLP & Văn bản",
        "HRIS & Thu nhập"
    ])

    with tab1:
        _render_core_metrics()
    with tab2:
        _render_risk_engagement()
    with tab3:
        _render_deep_analysis()
    with tab4:
        _render_simulation()
    with tab5:
        _render_nlp()
    with tab6:
        _render_hris()


def _section_header(title: str, desc: str) -> str:
    return f"""
    <div class="apx-sec-header">
        <p class="apx-sec-title"><span class="apx-sec-accent"></span>{title}</p>
        <p class="apx-sec-desc">{desc}</p>
    </div>
    """


def _card(accent_color: str, title: str, subtitle: str,
          description: str, formula: str, formula_note: str, questions: str,
          scale: str = "", classification_pills: list = None) -> str:
    pills_html = ""
    if classification_pills:
        pills = "".join(
            f'<span class="apx-pill {p.get("cls", "apx-pill-gray")}">{p["label"]}</span>'
            for p in classification_pills
        )
        pills_html = f"""
        <div style="margin-top: 2px;">
            <p class="apx-label">Phân loại</p>
            <div class="apx-cls-bar">{pills}</div>
        </div>
        """

    scale_html = ""
    if scale:
        scale_html = f"""
        <div class="apx-meta-item">
            <p class="apx-meta-label">Thang đo</p>
            <p class="apx-meta-value">{scale}</p>
        </div>
        """

    questions_html = f"""
    <div class="apx-meta-item">
        <p class="apx-meta-label">Câu hỏi sử dụng</p>
        <p class="apx-meta-value">{questions}</p>
    </div>
    """

    meta_html = f"""
    <div class="apx-meta-grid">
        {questions_html}
        {scale_html}
    </div>
    """

    return f"""
    <div class="apx-card">
        <div class="apx-card-accent" style="background: {accent_color};"></div>
        <div class="apx-card-body">
            <p class="apx-card-title">{title}</p>
            <p class="apx-card-subtitle">{subtitle}</p>
            <p class="apx-label">Ý nghĩa</p>
            <p class="apx-desc">{description}</p>
            <p class="apx-label">Công thức</p>
            <div class="apx-formula-box">{formula}</div>
            <p class="apx-note">{formula_note}</p>
            {meta_html}
            {pills_html}
        </div>
    </div>
    """


def _render_core_metrics():
    st.markdown(_section_header(
        "Các chỉ số Nền tảng",
        "Những chỉ số tổng hợp quan trọng nhất, phản ánh sức khỏe tổ chức toàn diện."
    ), unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(_card(
            accent_color="#4F46E5",
            title="Engagement Index", subtitle="Chỉ số Gắn kết Tổ chức",
            description="Thước đo tổng thể về mức độ gắn kết của nhân viên với công ty, được tổng hợp từ 5 trụ cột cốt lõi: <i>Niềm tin & Định hướng, Quản lý trực tiếp, Môi trường & Công cụ, Đãi ngộ & Công bằng, Văn hóa & Tự hào.</i>",
            formula="EI = &Sigma;(Tỷ lệ tích cực<sub>i</sub> &times; Trọng số<sub>i</sub>)",
            formula_note="<b>Trong đó:</b> Tỷ lệ tích cực = (mean(Q trong trụ cột) - 1) / 4 &times; 100%. Trọng số: TC1=15%, TC2=25%, TC3=20%, TC4=20%, TC5=20%.",
            questions="Q9-Q29 (21 câu Likert 5 điểm)",
            scale="0-100%",
            classification_pills=[
                {"label": "Xuất sắc >= 80%", "cls": "apx-pill-green"},
                {"label": "Khỏe mạnh 65-79%", "cls": "apx-pill-blue"},
                {"label": "Cần theo dõi 50-64%", "cls": "apx-pill-yellow"},
                {"label": "Nghiêm trọng < 50%", "cls": "apx-pill-red"},
            ]
        ), unsafe_allow_html=True)

        st.markdown(_card(
            accent_color="#DB2777",
            title="Manager Effectiveness Index", subtitle="Chỉ số Năng lực Quản lý",
            description="Đánh giá mức độ hiệu quả, sự hỗ trợ và năng lực lãnh đạo của Quản lý trực tiếp từ góc nhìn của nhân viên cấp dưới. Gồm các khía cạnh: Ghi nhận năng lực, Đối xử công bằng, Hỗ trợ khi gặp khó khăn, và Lắng nghe ý kiến.",
            formula="MEI = Count(Q >= 4) / Count(Q hợp lệ) &times; 100%",
            formula_note="Tính % câu hỏi được trả lời mức 4 (Đồng ý) hoặc 5 (Hoàn toàn đồng ý) trong nhóm câu hỏi về quản lý trực tiếp.",
            questions="Q11, Q12, Q14, Q15",
            scale="0-100%",
            classification_pills=[
                {"label": "Shield: MEI > 4.2/5.0 (~84%)", "cls": "apx-pill-purple"},
                {"label": "Giảm đáng kể tỷ lệ nghỉ việc", "cls": "apx-pill-green"},
            ]
        ), unsafe_allow_html=True)

    with col2:
        st.markdown(_card(
            accent_color="#16A34A",
            title="Employee Net Promoter Score", subtitle="Chỉ số Sẵn sàng Giới thiệu",
            description="Đo lường mức độ trung thành của nhân viên. Dựa trên câu hỏi duy nhất: <i>\"Bạn có sẵn sàng giới thiệu GHN là một nơi làm việc tốt cho bạn bè/người thân không?\"</i> (Thang 0-10).",
            formula="eNPS = % Promoter (9-10) - % Detractor (0-6)",
            formula_note="<b>Promoter (Đại sứ):</b> Điểm 9-10. <b>Passive (Thụ động):</b> Điểm 7-8 (không đưa vào công thức). <b>Detractor (Bất mãn):</b> Điểm 0-6.",
            questions="Q31 (thang 0-10)",
            scale="-100 đến +100",
            classification_pills=[
                {"label": "Xuất sắc >= +30", "cls": "apx-pill-green"},
                {"label": "Tích cực >= 0", "cls": "apx-pill-blue"},
                {"label": "Tiêu cực < 0", "cls": "apx-pill-red"},
            ]
        ), unsafe_allow_html=True)

        st.markdown(_card(
            accent_color="#D97706",
            title="Pillar Scores (TC1-TC5)", subtitle="Điểm 5 Trụ cột Gắn kết",
            description="Điểm riêng biệt cho từng trụ cột, cho phép xác định chính xác lĩnh vực nào đang mạnh/yếu trong tổ chức.",
            formula="TC_pct = (mean(các Q trong trụ cột) - 1) / 4 &times; 100%",
            formula_note="<b>TC1</b> (Niềm tin & Định hướng): Q9, Q10 &middot; <b>TC2</b> (Quản lý trực tiếp): Q11-Q15 &middot; <b>TC3</b> (Môi trường & Công cụ): Q16-Q20 &middot; <b>TC4</b> (Đãi ngộ & Công bằng): Q21-Q25 &middot; <b>TC5</b> (Văn hóa & Tự hào): Q26-Q29",
            questions="Q9-Q29 (phân nhóm theo trụ cột)",
            scale="0-100% cho mỗi trụ cột",
            classification_pills=[
                {"label": "Xuất sắc >= 80%", "cls": "apx-pill-green"},
                {"label": "Khỏe mạnh 65-79%", "cls": "apx-pill-blue"},
                {"label": "Cần theo dõi 50-64%", "cls": "apx-pill-yellow"},
                {"label": "Nghiêm trọng < 50%", "cls": "apx-pill-red"},
            ]
        ), unsafe_allow_html=True)


def _render_risk_engagement():
    st.markdown(_section_header(
        "Chỉ số Rủi ro & Gắn kết",
        "Các chỉ số đo lường nguy cơ nghỉ việc, kiệt sức và mức độ gắn bó của nhân viên."
    ), unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(_card(
            accent_color="#DC2626",
            title="Turnover Intent / Flight Risk", subtitle="Tỷ lệ Muốn nghỉ việc",
            description="Đo lường tỷ lệ nhân viên có ý định rời tổ chức trong vòng 6 tháng tới, dựa trên câu hỏi về ý định gắn bó.",
            formula="% Muốn nghỉ = Count(Q30 <= 2) / Count(Q30 hợp lệ) &times; 100%",
            formula_note="Phân nhóm: <b>Muốn nghỉ</b> (điểm 1-2) &middot; <b>Phân vân</b> (điểm 3) &middot; <b>Gắn bó</b> (điểm 4-5)",
            questions="Q30 (Ý định ở lại 3 tháng, Likert 1-5)",
            scale="0-100%",
            classification_pills=[
                {"label": "Thấp <= 10%", "cls": "apx-pill-green"},
                {"label": "Trung bình <= 20%", "cls": "apx-pill-yellow"},
                {"label": "Cao > 20%", "cls": "apx-pill-red"},
            ]
        ), unsafe_allow_html=True)

        st.markdown(_card(
            accent_color="#15803D",
            title="Intent Retention Rate", subtitle="Tỷ lệ Nhân viên Gắn bó",
            description="Tỷ lệ nhân viên có ý định gắn bó lâu dài với tổ chức, là chỉ số đối nghịch với Flight Risk.",
            formula="% Gắn bó = Count(Q30 >= 4) / Count(Q30 hợp lệ) &times; 100%",
            formula_note="Nhóm này có xu hướng ở lại tổ chức, cần duy trì và phát huy.",
            questions="Q30 (Ý định ở lại 3 tháng, Likert 1-5)",
            scale="0-100%",
            classification_pills=[
                {"label": "Tốt >= 70%", "cls": "apx-pill-green"},
                {"label": "Trung bình 50-69%", "cls": "apx-pill-yellow"},
                {"label": "Thấp < 50%", "cls": "apx-pill-red"},
            ]
        ), unsafe_allow_html=True)

        st.markdown(_card(
            accent_color="#7C3AED",
            title="Stay Intention Score", subtitle="Điểm Ý định Ở lại",
            description="Điểm trung bình của câu hỏi về ý định gắn bó, phản ánh mức độ cam kết ở lại trung bình của toàn bộ nhân viên.",
            formula="Stay Score = mean(Q22)",
            formula_note="Điểm trung bình trên thang Likert 1-5 của câu hỏi về thu nhập phản ánh công sức (proxy cho stay intention).",
            questions="Q22",
            scale="1-5",
            classification_pills=[
                {"label": "Tốt >= 4.0", "cls": "apx-pill-green"},
                {"label": "Trung bình >= 3.0", "cls": "apx-pill-yellow"},
                {"label": "Nguy hiểm < 3.0", "cls": "apx-pill-red"},
            ]
        ), unsafe_allow_html=True)

    with col2:
        st.markdown(_card(
            accent_color="#EF4444",
            title="Burnout Risk Score", subtitle="Điểm Rủi ro Kiệt sức",
            description="Dựa trên mô hình JD-R (Job Demands-Resources). Nếu Áp lực liên tục lớn hơn Nguồn lực, nhân viên sẽ rơi vào trạng thái kiệt quệ.",
            formula="Burnout = mean(Q18, Q29) - mean(Q11, Q16)",
            formula_note="<b>Áp lực (Demands):</b> Q18 (Cường độ/An toàn LĐ), Q29 (Áp lực/Tôn trọng). <b>Nguồn lực (Resources):</b> Q11 (Hỗ trợ kịp thời), Q16 (App/Xe an toàn). Burnout > 0 = Áp lực > Nguồn lực.",
            questions="Q11, Q16, Q18, Q29",
            scale="0-100%",
            classification_pills=[
                {"label": "An toàn <= 15%", "cls": "apx-pill-green"},
                {"label": "Cần chú ý <= 30%", "cls": "apx-pill-yellow"},
                {"label": "Nguy hiểm > 30%", "cls": "apx-pill-red"},
            ]
        ), unsafe_allow_html=True)

        st.markdown(_card(
            accent_color="#EA580C",
            title="Stay Risk Segmentation", subtitle="Phân nhóm Rủi ro Ở lại",
            description="Phân loại nhân viên thành 3 nhóm rủi ro dựa trên điểm ý định gắn bó, giúp xác định đối tượng cần can thiệp giữ chân.",
            formula="Flight Risk: Q22 <= 2 &ensp;|&ensp; At Risk: Q22 = 3 &ensp;|&ensp; Stable: Q22 >= 4",
            formula_note="Mỗi nhóm được tính % trên tổng số nhân viên hợp lệ.",
            questions="Q22",
            scale="0-100% cho mỗi nhóm",
            classification_pills=[
                {"label": "Flight Risk: Nguy cơ rời đi cao", "cls": "apx-pill-red"},
                {"label": "At Risk: Đang cân nhắc", "cls": "apx-pill-orange"},
                {"label": "Stable: Ổn định", "cls": "apx-pill-green"},
            ]
        ), unsafe_allow_html=True)

        st.markdown(_card(
            accent_color="#059669",
            title="eNPS Segment Distribution", subtitle="Phân bố Đại sứ / Thụ động / Bất mãn",
            description="Phân bố chi tiết nhân viên theo 3 nhóm trung thành, giúp hiểu cấu trúc của điểm eNPS tổng thể.",
            formula="Promoter: Q31 >= 9 &ensp;|&ensp; Passive: Q31 &isin; {7, 8} &ensp;|&ensp; Detractor: Q31 <= 6",
            formula_note="<b>Promoter:</b> Trung thành, nhiệt huyết. <b>Passive:</b> Hài lòng nhưng dễ bị thu hút bởi offer khác. <b>Detractor:</b> Không hài lòng, có khả năng lan truyền tiêu cực.",
            questions="Q31 (thang 0-10)",
            scale="% cho mỗi nhóm",
            classification_pills=[
                {"label": "Promoter > 50% là tốt", "cls": "apx-pill-green"},
                {"label": "Detractor > 30% cần báo động", "cls": "apx-pill-red"},
            ]
        ), unsafe_allow_html=True)


def _render_deep_analysis():
    st.markdown(_section_header(
        "Chỉ số Phân tích Chuyên sâu",
        "Các phương pháp thống kê và phân tích nâng cao để tìm ra nguyên nhân và ưu tiên hành động."
    ), unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(_card(
            accent_color="#2563EB",
            title="Spearman Rank Correlation", subtitle="Hệ số Tương quan Hạng Spearman với EI",
            description="Đo lường mức độ ảnh hưởng của từng câu hỏi đến chỉ số gắn kết tổng thể (EI). Câu hỏi có tương quan cao hơn = ảnh hưởng nhiều hơn đến sự gắn kết.",
            formula="&rho; = spearmanr(Q_score, EI)",
            formula_note="Tính riêng cho từng câu hỏi Likert (Q9-Q29) so với EI. Giá trị &rho; > 0 = câu hỏi đồng biến với EI (điểm cao hơn &rarr; EI cao hơn).",
            questions="Q9-Q29 (từng câu) so với EI",
            scale="-1.0 đến +1.0",
            classification_pills=[
                {"label": "|&rho;| > 0.5: Mạnh", "cls": "apx-pill-green"},
                {"label": "0.3-0.5: Trung bình", "cls": "apx-pill-yellow"},
                {"label": "< 0.3: Yếu", "cls": "apx-pill-gray"},
            ]
        ), unsafe_allow_html=True)

        st.markdown(_card(
            accent_color="#CA8A04",
            title="Root Cause Gap Score", subtitle="Chênh lệch Điểm: Nhóm Muốn nghỉ vs. Gắn bó",
            description="So sánh điểm trung bình từng câu hỏi giữa nhóm muốn nghỉ và nhóm gắn bó, giúp xác định nguyên nhân gốc rễ khiến nhân viên muốn rời đi.",
            formula="Gap = mean(Q | intent >= 4) - mean(Q | intent <= 2)",
            formula_note="Gap lớn = câu hỏi đó là nguyên nhân chính khiến nhân viên muốn nghỉ. Top 10 gap lớn nhất được xếp hạng ưu tiên.",
            questions="Q9-Q29 (so sánh theo nhóm Q30)",
            scale="Điểm chênh lệch (Likert 1-5)",
            classification_pills=[
                {"label": "Gap > 1.0: Rất nghiêm trọng", "cls": "apx-pill-red"},
                {"label": "0.5-1.0: Đáng kể", "cls": "apx-pill-orange"},
                {"label": "< 0.5: Nhỏ", "cls": "apx-pill-gray"},
            ]
        ), unsafe_allow_html=True)

    with col2:
        st.markdown(_card(
            accent_color="#9333EA",
            title="Impact-Effort Priority Matrix", subtitle="Ma trận Ưu tiên Hành động",
            description="Phân loại từng câu hỏi vào 4 nhóm ưu tiên dựa trên tương quan với EI (Impact) và điểm hiện tại (Effort cần thiết), giúp tập trung nguồn lực hiệu quả.",
            formula="4 góc phần tư dựa trên Median(&rho;) và Median(Score)",
            formula_note="<b>Ưu tiên cao</b> (Impact cao + Điểm thấp): Cần hành động ngay. <b>Duy trì</b> (Impact cao + Điểm cao): Giữ vững. <b>Theo dõi</b> (Impact thấp + Điểm thấp): Quan sát. <b>Không ưu tiên</b> (Impact thấp + Điểm cao): Ít quan trọng.",
            questions="Q9-Q29",
            scale="Phân loại 4 nhóm",
            classification_pills=[
                {"label": "Ưu tiên cao", "cls": "apx-pill-red"},
                {"label": "Duy trì", "cls": "apx-pill-green"},
                {"label": "Theo dõi", "cls": "apx-pill-yellow"},
                {"label": "Không ưu tiên", "cls": "apx-pill-gray"},
            ]
        ), unsafe_allow_html=True)

        st.markdown(_card(
            accent_color="#475569",
            title="Survey Response Rate", subtitle="Tỷ lệ Phản hồi Khảo sát",
            description="Tỷ lệ nhân viên tham gia khảo sát so với tổng số nhân viên, phản ánh mức độ đại diện của dữ liệu.",
            formula="Response Rate = Số người tham gia / Tổng headcount &times; 100%",
            formula_note="Dựa trên dữ liệu headcount từ HRIS so với số lượng phản hồi thực tế.",
            questions="Không áp dụng (dữ liệu HRIS)",
            scale="0-100%",
            classification_pills=[
                {"label": "Tốt >= 70%", "cls": "apx-pill-green"},
                {"label": "Chấp nhận >= 50%", "cls": "apx-pill-yellow"},
                {"label": "Thấp < 50%", "cls": "apx-pill-red"},
            ]
        ), unsafe_allow_html=True)

        st.markdown(_card(
            accent_color="#059669",
            title="Year-over-Year Delta", subtitle="Thay đổi Chỉ số so với Năm trước",
            description="So sánh các chỉ số chính (EI, eNPS) giữa năm hiện tại và năm trước, giúp đánh giá xu hướng cải thiện hoặc suy giảm.",
            formula="&Delta; = Giá trị 2026 - Benchmark 2025",
            formula_note="Benchmark 2025: EI = 80.2%, eNPS = +33.6, Response Rate = 75.9%. Giá trị dương = cải thiện, âm = suy giảm.",
            questions="Không áp dụng (chỉ số tổng hợp)",
            scale="Điểm phần trăm",
            classification_pills=[
                {"label": "&Delta; > 0: Cải thiện", "cls": "apx-pill-green"},
                {"label": "&Delta; = 0: Duy trì", "cls": "apx-pill-gray"},
                {"label": "&Delta; < 0: Suy giảm", "cls": "apx-pill-red"},
            ]
        ), unsafe_allow_html=True)


def _render_simulation():
    st.markdown(_section_header(
        "Chỉ số Mô phỏng & Dự báo",
        "Các công cụ mô phỏng giúp dự đoán tác động của các can thiệp và ước tính ROI."
    ), unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(_card(
            accent_color="#2563EB",
            title="KPI Impact Simulator", subtitle="Mô phỏng Tác động KPI đến eNPS",
            description="Dự báo mức tăng eNPS và số người giữ lại được khi cải thiện các trụ cột cụ thể, từ đó ước tính chi phí tiết kiệm được.",
            formula="""enps_increase = improvement &times; weight &times; 100<br>
new_enps = current_enps + enps_increase<br>
retention_gain = (enps_increase / 10) &times; 0.05<br>
people_saved = N &times; retention_gain<br>
money_saved = people_saved &times; cost_per_hire""",
            formula_note="<b>Trọng số theo nhóm:</b> Shipper: MEI 34%, Thu nhập 28%, Hỗ trợ sự cố 18%, App 12%, Văn hóa 8%. Tài xế: Điều phối 32%, An toàn 26%, Thu nhập 20%, Thiết bị 14%, Tinh thần 8%.",
            questions="EI, eNPS, MEI và các trụ cột",
            scale="eNPS pts, số người, VND",
            classification_pills=[
                {"label": "ROI dương = Can thiệp có lợi", "cls": "apx-pill-green"},
            ]
        ), unsafe_allow_html=True)

        st.markdown(_card(
            accent_color="#DC2626",
            title="Micro Risk Simulator", subtitle="Trình Giả lập Rủi ro Nghỉ việc (Cá nhân)",
            description="Ước tính xác suất nghỉ việc của một nhân viên cụ thể dựa trên các yếu tố cá nhân (thâm niên, thu nhập, MEI, v.v.).",
            formula="""risk = base + tenure_penalty + salary_penalty + ... - mei_shield<br>
(clamped to [min, max])""",
            formula_note="<b>Shipper/Driver:</b> base(30) + tenure(0-25) + salary(0-20) + COD(0-15) - MEI(0-30), clamp [10, 95]. <b>Ops 2A/2B:</b> base(28) + tenure(0-20) + shift(0-18) + equip(0-15) - MEI(0-25), clamp [8, 95]. <b>Office 3A/3B:</b> base(22) + tenure(0-18) + workload(0-22) - recognition(0-20), clamp [5, 92].",
            questions="MEI, thâm niên, thu nhập, ca làm, thiết bị",
            scale="0-100% (xác suất)",
            classification_pills=[
                {"label": "Thấp <= 20%", "cls": "apx-pill-green"},
                {"label": "Trung bình <= 50%", "cls": "apx-pill-yellow"},
                {"label": "Cao > 50%", "cls": "apx-pill-red"},
            ]
        ), unsafe_allow_html=True)

    with col2:
        st.markdown(_card(
            accent_color="#CA8A04",
            title="Macro Risk Simulator", subtitle="Giả lập Tác động Tổ chức (Vĩ mô)",
            description="Dự báo tỷ lệ nghỉ việc toàn tổ chức khi thay đổi các yếu tố vĩ mô như lương thưởng, năng lực quản lý, và mức phạt.",
            formula="""impact_salary = salary_change% &times; 0.35<br>
impact_mei = mei_change% &times; 0.5<br>
impact_cod = cod_reduction% &times; 0.08<br>
new_risk = current_risk - (impact_salary + impact_mei + impact_cod)""",
            formula_note="Baseline là tỷ lệ muốn nghỉ hiện tại (intent_pct_low). Kết quả được clamp trong khoảng [2%, 80%].",
            questions="Turnover Intent (Q30), MEI, thu nhập",
            scale="0-100% (tỷ lệ dự báo)",
            classification_pills=[
                {"label": "Clamp: [2%, 80%]", "cls": "apx-pill-gray"},
            ]
        ), unsafe_allow_html=True)

        st.markdown(_card(
            accent_color="#64748B",
            title="Data Quality Flags", subtitle="Cờ Chất lượng Dữ liệu",
            description="Phát hiện các phản hồi không hợp lệ: trả lời thẳng hàng (straightline) hoặc bỏ trống quá nhiều, đảm bảo độ tin cậy của phân tích.",
            formula="""Straightline: SD(Q9..Q29) = 0 AND >= 10 câu hợp lệ<br>
Missing: > 80% câu Likert bị bỏ trống""",
            formula_note="Straightline = tất cả câu trả lời giống nhau (có thể trả lời ngẫu nhiên). Missing = không trả lời phần lớn câu hỏi.",
            questions="Q9-Q29 (tất cả câu Likert)",
            scale="Boolean (Có/Không)",
            classification_pills=[
                {"label": "Straightline: Loại (2A, 2B, 3A) / Giữ (1A, 1B, 3B)", "cls": "apx-pill-orange"},
                {"label": "Missing: Luôn loại", "cls": "apx-pill-red"},
            ]
        ), unsafe_allow_html=True)


def _render_nlp():
    st.markdown(_section_header(
        "Chỉ số NLP & Phân tích Văn bản",
        "Các chỉ số được trích xuất từ phản hồi mở (open-text) bằng kỹ thuật xử lý ngôn ngữ tự nhiên."
    ), unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(_card(
            accent_color="#DC2626",
            title="NLP Warning Signals", subtitle="Tín hiệu Cảnh báo từ Phản hồi Mở",
            description="Phát hiện tự động các tín hiệu tiêu cực từ phản hồi văn bản mở, giúp nhận diện sớm các vấn đề nghiêm trọng.",
            formula="Rule-based keyword detection + AI validation",
            formula_note="<b>5 loại tín hiệu:</b> Ý định nghỉ việc, Kiệt sức, Bất công, Mất niềm tin, Xung đột QL. Sau khi phát hiện bằng keyword, AI được dùng để lọc false positive.",
            questions="Q32, Q33, Q34 (phản hồi mở)",
            scale="Số tín hiệu / Tổng phản hồi",
            classification_pills=[
                {"label": "Mỗi tín hiệu được AI xác thực", "cls": "apx-pill-blue"},
            ]
        ), unsafe_allow_html=True)

        st.markdown(_card(
            accent_color="#7C3AED",
            title="Topic Distribution with Sentiment", subtitle="Phân bố Chủ đề & Giọng điệu",
            description="Phân loại phản hồi mở thành các chủ đề và đánh giá giọng điệu (tích cực/trung lập/tiêu cực) cho mỗi chủ đề.",
            formula="Topic% = Số đề cập / Tổng phản hồi &times; 100",
            formula_note="Mỗi chủ đề có phân bố: positive%, neutral%, negative%. Giúp hiểu vấn đề nào được quan tâm nhiều nhất và cảm xúc đi kèm.",
            questions="Q32, Q33, Q34 (phản hồi mở)",
            scale="% cho mỗi chủ đề",
            classification_pills=[
                {"label": "Chủ đề > 20% = Nổi bật", "cls": "apx-pill-blue"},
                {"label": "Negative > 50% = Cần chú ý", "cls": "apx-pill-red"},
            ]
        ), unsafe_allow_html=True)

    with col2:
        st.markdown(_card(
            accent_color="#2563EB",
            title="EVP Keyword Frequency", subtitle="Từ khóa EVP Nổi bật",
            description="Đếm tần suất từ khóa trong phản hồi mở, phân nhóm theo 4 yếu tố EVP (Employer Value Proposition) để hiểu nhân viên quan tâm đến điều gì nhất.",
            formula="Word frequency &rarr; bucketed into 4 EVP factors",
            formula_note="<b>4 nhóm EVP:</b> Lương thưởng & Phụ cấp, Công việc & Môi trường, Quản lý & Hỗ trợ, Công nghệ & Quy trình. Tần suất cao = mối quan tâm lớn.",
            questions="Q32, Q33, Q34 (phản hồi mở)",
            scale="Số lần xuất hiện / Tổng phản hồi",
            classification_pills=[
                {"label": "Top keywords trong mỗi nhóm EVP", "cls": "apx-pill-purple"},
            ]
        ), unsafe_allow_html=True)


def _render_hris():
    st.markdown(_section_header(
        "Chỉ số HRIS & Thu nhập",
        "Các chỉ số kết hợp dữ liệu khảo sát với dữ liệu HRIS (nhân sự) để tìm mối tương quan sâu hơn."
    ), unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(_card(
            accent_color="#16A34A",
            title="Income x Engagement", subtitle="Tương quan Thu nhập & Gắn kết",
            description="Phân tích mức độ gắn kết (EI) và eNPS theo từng nhóm thu nhập, giúp xác định thu nhập có phải yếu tố quyết định gắn kết hay không.",
            formula="mean(EI) và eNPS theo nhóm thu nhập",
            formula_note="<b>Nhóm thu nhập:</b> &lt;5tr, 5-7tr, 7-10tr, 10-15tr, &gt;15tr. Cho phép so sánh EI và eNPS giữa các nhóm.",
            questions="EI, eNPS + HRIS (thu nhập)",
            scale="EI: 0-100% | eNPS: -100 đến +100",
            classification_pills=[
                {"label": "Chênh lệch EI > 15% = Đáng kể", "cls": "apx-pill-orange"},
            ]
        ), unsafe_allow_html=True)

        st.markdown(_card(
            accent_color="#DC2626",
            title="Penalty x Engagement", subtitle="Tương quan Mức phạt & Gắn kết",
            description="Phân tích tác động của mức phạt (phạt + truy thu COD) đến sự gắn kết, giúp đánh giá chính sách phạt có ảnh hưởng tiêu cực hay không.",
            formula="mean(EI) theo nhóm mức phạt",
            formula_note="<b>Nhóm phạt:</b> Không phạt, &lt;500K, 500K-1tr, 1-3tr, &gt;3tr. tong_phat = Phạt + Truy thu COD.",
            questions="EI + HRIS (phạt, truy thu COD)",
            scale="EI: 0-100%",
            classification_pills=[
                {"label": "EI giảm > 10% = Tác động tiêu cực", "cls": "apx-pill-red"},
            ]
        ), unsafe_allow_html=True)

        st.markdown(_card(
            accent_color="#CA8A04",
            title="Turnover Risk Heatmap", subtitle="Bản đồ Rủi ro: Thu nhập x Mức phạt",
            description="Heatmap 2 chiều thể hiện tỷ lệ muốn nghỉ việc theo từng kết hợp (nhóm thu nhập, nhóm phạt), giúp xác định nhóm nhân viên có rủi ro cao nhất.",
            formula="Risk% = Count(Muốn nghỉ) / Tổng trong ô &times; 100%",
            formula_note="Chỉ hiển thị các ô có N >= 10 để đảm bảo ý nghĩa thống kê. Kết hợp Q30 (ý định) + HRIS (thu nhập, phạt).",
            questions="Q30 + HRIS (thu nhập, phạt)",
            scale="0-100% cho mỗi ô",
            classification_pills=[
                {"label": "> 30%: Nguy hiểm", "cls": "apx-pill-red"},
                {"label": "15-30%: Cần chú ý", "cls": "apx-pill-yellow"},
                {"label": "< 15%: An toàn", "cls": "apx-pill-green"},
            ]
        ), unsafe_allow_html=True)

    with col2:
        st.markdown(_card(
            accent_color="#9333EA",
            title="Warrior Classification x Engagement", subtitle="Phân loại Chiến binh & Gắn kết",
            description="Phân tích mức độ gắn kết theo phân loại chiến binh (từ HRIS), giúp hiểu nhóm chiến binh nào đang gắn kết tốt/yếu.",
            formula="mean(EI) và mean(thu nhập) theo phân loại Chiến binh",
            formula_note="Dựa trên trường 'Phân loại Chiến binh' trong HRIS. Cho phép so sánh EI và thu nhập trung bình giữa các nhóm.",
            questions="EI + HRIS (Phân loại Chiến binh)",
            scale="EI: 0-100%",
            classification_pills=[
                {"label": "So sánh EI giữa các nhóm chiến binh", "cls": "apx-pill-purple"},
            ]
        ), unsafe_allow_html=True)

        st.markdown(_card(
            accent_color="#059669",
            title="Income Structure Breakdown", subtitle="Cơ cấu Thu nhập Trung bình",
            description="Phân tích cơ cấu thu nhập trung bình theo từng thành phần, giúp hiểu tỷ trọng lương, thưởng, phụ cấp trong tổng thu nhập.",
            formula="Mean của từng thành phần thu nhập",
            formula_note="<b>Các thành phần:</b> Lương đơn hàng, Thưởng/Phạt GTC và LTC, Phụ cấp, Thưởng Doanh Thu. Hiển thị dưới dạng biểu đồ tròn %.",
            questions="HRIS (cơ cấu thu nhập)",
            scale="VND và %",
            classification_pills=[
                {"label": "Phân tích cơ cấu, không phân loại", "cls": "apx-pill-gray"},
            ]
        ), unsafe_allow_html=True)
