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
    border-left: 4px solid #FF5200;
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
    margin: 8px 0 24px;
    padding-bottom: 12px;
    border-bottom: 1px solid #F1F5F9;
}
.apx-sec-title {
    font-size: 1.1rem;
    font-weight: 700;
    color: #0A1F44;
    margin: 0 0 4px;
    display: flex;
    align-items: center;
    gap: 10px;
}
.apx-sec-accent {
    width: 4px;
    height: 18px;
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
    border-left: 4px solid #CBD5E1;
    border-radius: 12px;
    padding: 0;
    margin-bottom: 20px;
    overflow: hidden;
    transition: border-color 0.15s ease, box-shadow 0.15s ease;
}
.apx-card:hover {
    border-color: #94A3B8;
    box-shadow: 0 4px 12px rgba(0,0,0,0.06);
}
.apx-card-body {
    padding: 28px 32px;
}
.apx-card-header {
    display: flex;
    align-items: flex-start;
    gap: 16px;
    margin-bottom: 20px;
    padding-bottom: 16px;
    border-bottom: 1px solid #F1F5F9;
}
.apx-card-number {
    font-size: 1.8rem;
    font-weight: 800;
    line-height: 1;
    letter-spacing: -0.03em;
    flex-shrink: 0;
    opacity: 0.15;
}
.apx-card-titles {
    flex: 1;
}
.apx-card-title {
    font-size: 1.15rem;
    font-weight: 700;
    color: #0A1F44;
    margin: 0 0 4px;
    letter-spacing: -0.01em;
}
.apx-card-subtitle {
    font-size: 0.82rem;
    color: #64748B;
    font-weight: 500;
    margin: 0;
}
.apx-section-label {
    font-size: 0.68rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: #94A3B8;
    margin: 0 0 8px;
}
.apx-desc {
    font-size: 0.88rem;
    color: #334155;
    line-height: 1.7;
    margin: 0 0 20px;
}
.apx-formula-box {
    background: #F8FAFC;
    border: 1px solid #E2E8F0;
    border-left: 4px solid #3B82F6;
    border-radius: 8px;
    padding: 16px 20px;
    margin-bottom: 12px;
    font-family: 'Consolas', 'SF Mono', 'Courier New', monospace;
    font-size: 0.85rem;
    color: #1E293B;
    line-height: 1.8;
}
.apx-note {
    font-size: 0.85rem;
    color: #475569;
    line-height: 1.65;
    margin: 0 0 20px;
}
.apx-meta-row {
    display: flex;
    gap: 12px;
    margin-bottom: 20px;
    flex-wrap: wrap;
}
.apx-meta-tag {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: #F1F5F9;
    border: 1px solid #E2E8F0;
    border-radius: 6px;
    padding: 6px 12px;
    font-size: 0.78rem;
    font-weight: 600;
    color: #475569;
}
.apx-meta-tag-label {
    color: #94A3B8;
    font-weight: 700;
    text-transform: uppercase;
    font-size: 0.68rem;
    letter-spacing: 0.05em;
}
.apx-threshold-bar {
    margin-top: 8px;
}
.apx-threshold-label {
    font-size: 0.68rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: #94A3B8;
    margin: 0 0 10px;
}
.apx-threshold-track {
    display: flex;
    gap: 2px;
    height: 32px;
    border-radius: 6px;
    overflow: hidden;
    margin-bottom: 8px;
}
.apx-threshold-segment {
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 0.72rem;
    font-weight: 700;
    color: white;
    text-shadow: 0 1px 2px rgba(0,0,0,0.2);
}
.apx-threshold-legend {
    display: flex;
    gap: 16px;
    flex-wrap: wrap;
}
.apx-threshold-item {
    display: flex;
    align-items: center;
    gap: 6px;
    font-size: 0.75rem;
    color: #475569;
}
.apx-threshold-dot {
    width: 10px;
    height: 10px;
    border-radius: 3px;
    flex-shrink: 0;
}
.apx-quick-ref {
    background: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 10px;
    padding: 20px;
    margin-bottom: 28px;
    overflow-x: auto;
}
.apx-quick-ref-title {
    font-size: 0.82rem;
    font-weight: 700;
    color: #0A1F44;
    margin: 0 0 12px;
    display: flex;
    align-items: center;
    gap: 8px;
}
.apx-quick-ref-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 0.78rem;
}
.apx-quick-ref-table th {
    background: #F8FAFC;
    padding: 10px 12px;
    text-align: left;
    font-weight: 700;
    color: #64748B;
    text-transform: uppercase;
    font-size: 0.68rem;
    letter-spacing: 0.08em;
    border-bottom: 2px solid #E2E8F0;
}
.apx-quick-ref-table td {
    padding: 10px 12px;
    border-bottom: 1px solid #F1F5F9;
    color: #334155;
}
.apx-quick-ref-table tr:last-child td {
    border-bottom: none;
}
.apx-quick-ref-table tr:hover {
    background: #F8FAFC;
}
.apx-quick-ref-num {
    font-weight: 800;
    color: #94A3B8;
    font-size: 0.72rem;
}
.apx-quick-ref-name {
    font-weight: 600;
    color: #0A1F44;
}
.apx-quick-ref-formula {
    font-family: 'Consolas', monospace;
    font-size: 0.75rem;
    color: #3B82F6;
}
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
    return f"""<div class="apx-sec-header">
<p class="apx-sec-title"><span class="apx-sec-accent"></span>{title}</p>
<p class="apx-sec-desc">{desc}</p>
</div>"""


def _quick_reference_table(items: list) -> str:
    rows = ""
    for i, item in enumerate(items, 1):
        rows += f"""<tr>
<td class="apx-quick-ref-num">{i:02d}</td>
<td class="apx-quick-ref-name">{item['name']}</td>
<td class="apx-quick-ref-formula">{item['formula']}</td>
<td>{item['questions']}</td>
</tr>"""
    return f"""<div class="apx-quick-ref">
<p class="apx-quick-ref-title">Tham chiếu nhanh</p>
<table class="apx-quick-ref-table">
<thead><tr><th style="width:40px">#</th><th>Chỉ số</th><th>Công thức</th><th>Câu hỏi</th></tr></thead>
<tbody>{rows}</tbody>
</table>
</div>"""


def _card(number: int, accent_color: str, title: str, subtitle: str,
          description: str, formula: str, formula_note: str, questions: str,
          scale: str = "", thresholds: list = None) -> str:
    meta_tags = f'<div class="apx-meta-tag"><span class="apx-meta-tag-label">Câu hỏi</span>{questions}</div>'
    if scale:
        meta_tags += f'<div class="apx-meta-tag"><span class="apx-meta-tag-label">Thang đo</span>{scale}</div>'

    threshold_html = ""
    if thresholds:
        segments = ""
        legend_items = ""
        for t in thresholds:
            segments += f'<div class="apx-threshold-segment" style="flex:{t["weight"]};background:{t["color"]};">{t["label"]}</div>'
            legend_items += f'<div class="apx-threshold-item"><div class="apx-threshold-dot" style="background:{t["color"]};"></div>{t["desc"]}</div>'
        threshold_html = f"""<div class="apx-threshold-bar">
<p class="apx-threshold-label">Phân loại</p>
<div class="apx-threshold-track">{segments}</div>
<div class="apx-threshold-legend">{legend_items}</div>
</div>"""

    return f"""<div class="apx-card" style="border-left-color: {accent_color};">
<div class="apx-card-body">
<div class="apx-card-header">
<div class="apx-card-number" style="color: {accent_color};">{number:02d}</div>
<div class="apx-card-titles">
<p class="apx-card-title">{title}</p>
<p class="apx-card-subtitle">{subtitle}</p>
</div>
</div>
<p class="apx-section-label">Ý nghĩa</p>
<p class="apx-desc">{description}</p>
<p class="apx-section-label">Công thức</p>
<div class="apx-formula-box">{formula}</div>
<p class="apx-note">{formula_note}</p>
<div class="apx-meta-row">{meta_tags}</div>
{threshold_html}
</div>
</div>"""


def _render_core_metrics():
    st.markdown(_section_header(
        "Các chỉ số Nền tảng",
        "Những chỉ số tổng hợp quan trọng nhất, phản ánh sức khỏe tổ chức toàn diện."
    ), unsafe_allow_html=True)

    st.markdown(_quick_reference_table([
        {"name": "Engagement Index", "formula": "EI = Σ(Tỷ lệ tích cực × Trọng số)", "questions": "Q9-Q29"},
        {"name": "Manager Effectiveness", "formula": "MEI = Count(Q≥4) / Count(Q) × 100%", "questions": "Q11, Q12, Q14, Q15"},
        {"name": "eNPS", "formula": "%Promoter - %Detractor", "questions": "Q31"},
        {"name": "Pillar Scores", "formula": "(mean - 1) / 4 × 100%", "questions": "Q9-Q29"},
    ]), unsafe_allow_html=True)

    st.markdown(_card(
        number=1,
        accent_color="#4F46E5",
        title="Engagement Index", subtitle="Chỉ số Gắn kết Tổ chức",
        description="Thước đo tổng thể về mức độ gắn kết của nhân viên với công ty, được tổng hợp từ 5 trụ cột cốt lõi: <i>Niềm tin & Định hướng, Quản lý trực tiếp, Môi trường & Công cụ, Đãi ngộ & Công bằng, Văn hóa & Tự hào.</i>",
        formula="EI = &Sigma;(Tỷ lệ tích cực<sub>i</sub> &times; Trọng số<sub>i</sub>)",
        formula_note="<b>Trong đó:</b> Tỷ lệ tích cực = (mean(Q trong trụ cột) - 1) / 4 &times; 100%. Trọng số: TC1=15%, TC2=25%, TC3=20%, TC4=20%, TC5=20%.",
        questions="Q9-Q29 (21 câu Likert 5 điểm)",
        scale="0-100%",
        thresholds=[
            {"label": "Nghiêm trọng", "weight": 50, "color": "#DC2626", "desc": "< 50%"},
            {"label": "Cần theo dõi", "weight": 15, "color": "#F59E0B", "desc": "50-64%"},
            {"label": "Khỏe mạnh", "weight": 15, "color": "#3B82F6", "desc": "65-79%"},
            {"label": "Xuất sắc", "weight": 20, "color": "#10B981", "desc": "≥ 80%"},
        ]
    ), unsafe_allow_html=True)

    st.markdown(_card(
        number=2,
        accent_color="#DB2777",
        title="Manager Effectiveness Index", subtitle="Chỉ số Năng lực Quản lý",
        description="Đánh giá mức độ hiệu quả, sự hỗ trợ và năng lực lãnh đạo của Quản lý trực tiếp từ góc nhìn của nhân viên cấp dưới. Gồm các khía cạnh: Ghi nhận năng lực, Đối xử công bằng, Hỗ trợ khi gặp khó khăn, và Lắng nghe ý kiến.",
        formula="MEI = Count(Q &ge; 4) / Count(Q hợp lệ) &times; 100%",
        formula_note="Tính % câu hỏi được trả lời mức 4 (Đồng ý) hoặc 5 (Hoàn toàn đồng ý) trong nhóm câu hỏi về quản lý trực tiếp. <b>Ngưỡng khiên (Shield):</b> MEI > 4.2/5.0 (~84%) giảm đáng kể tỷ lệ nghỉ việc.",
        questions="Q11, Q12, Q14, Q15",
        scale="0-100%",
        thresholds=[
            {"label": "Yếu", "weight": 50, "color": "#DC2626", "desc": "< 50%"},
            {"label": "Trung bình", "weight": 34, "color": "#F59E0B", "desc": "50-83%"},
            {"label": "Shield Zone", "weight": 16, "color": "#10B981", "desc": "≥ 84%"},
        ]
    ), unsafe_allow_html=True)

    st.markdown(_card(
        number=3,
        accent_color="#16A34A",
        title="Employee Net Promoter Score", subtitle="Chỉ số Sẵn sàng Giới thiệu",
        description="Đo lường mức độ trung thành của nhân viên. Dựa trên câu hỏi duy nhất: <i>\"Bạn có sẵn sàng giới thiệu GHN là một nơi làm việc tốt cho bạn bè/người thân không?\"</i> (Thang 0-10).",
        formula="eNPS = % Promoter (9-10) - % Detractor (0-6)",
        formula_note="<b>Promoter (Đại sứ):</b> Điểm 9-10. <b>Passive (Thụ động):</b> Điểm 7-8 (không đưa vào công thức). <b>Detractor (Bất mãn):</b> Điểm 0-6.",
        questions="Q31 (thang 0-10)",
        scale="-100 đến +100",
        thresholds=[
            {"label": "Tiêu cực", "weight": 50, "color": "#DC2626", "desc": "< 0"},
            {"label": "Tích cực", "weight": 30, "color": "#3B82F6", "desc": "0 đến +29"},
            {"label": "Xuất sắc", "weight": 20, "color": "#10B981", "desc": "≥ +30"},
        ]
    ), unsafe_allow_html=True)

    st.markdown(_card(
        number=4,
        accent_color="#D97706",
        title="Pillar Scores (TC1-TC5)", subtitle="Điểm 5 Trụ cột Gắn kết",
        description="Điểm riêng biệt cho từng trụ cột, cho phép xác định chính xác lĩnh vực nào đang mạnh/yếu trong tổ chức.",
        formula="TC_pct = (mean(các Q trong trụ cột) - 1) / 4 &times; 100%",
        formula_note="<b>TC1</b> (Niềm tin & Định hướng): Q9, Q10 &middot; <b>TC2</b> (Quản lý trực tiếp): Q11-Q15 &middot; <b>TC3</b> (Môi trường & Công cụ): Q16-Q20 &middot; <b>TC4</b> (Đãi ngộ & Công bằng): Q21-Q25 &middot; <b>TC5</b> (Văn hóa & Tự hào): Q26-Q29",
        questions="Q9-Q29 (phân nhóm theo trụ cột)",
        scale="0-100% cho mỗi trụ cột",
        thresholds=[
            {"label": "Nghiêm trọng", "weight": 50, "color": "#DC2626", "desc": "< 50%"},
            {"label": "Cần theo dõi", "weight": 15, "color": "#F59E0B", "desc": "50-64%"},
            {"label": "Khỏe mạnh", "weight": 15, "color": "#3B82F6", "desc": "65-79%"},
            {"label": "Xuất sắc", "weight": 20, "color": "#10B981", "desc": "≥ 80%"},
        ]
    ), unsafe_allow_html=True)


def _render_risk_engagement():
    st.markdown(_section_header(
        "Chỉ số Rủi ro & Gắn kết",
        "Các chỉ số đo lường nguy cơ nghỉ việc, kiệt sức và mức độ gắn bó của nhân viên."
    ), unsafe_allow_html=True)

    st.markdown(_quick_reference_table([
        {"name": "Turnover Intent", "formula": "Count(Q30≤2) / Count(Q30) × 100%", "questions": "Q30"},
        {"name": "Intent Retention", "formula": "Count(Q30≥4) / Count(Q30) × 100%", "questions": "Q30"},
        {"name": "Stay Intention", "formula": "mean(Q22)", "questions": "Q22"},
        {"name": "Burnout Risk", "formula": "mean(Q18,Q29) - mean(Q11,Q16)", "questions": "Q11, Q16, Q18, Q29"},
        {"name": "Stay Risk Segmentation", "formula": "Q22≤2 | Q22=3 | Q22≥4", "questions": "Q22"},
        {"name": "eNPS Segments", "formula": "Promoter | Passive | Detractor", "questions": "Q31"},
    ]), unsafe_allow_html=True)

    st.markdown(_card(
        number=5,
        accent_color="#DC2626",
        title="Turnover Intent / Flight Risk", subtitle="Tỷ lệ Muốn nghỉ việc",
        description="Đo lường tỷ lệ nhân viên có ý định rời tổ chức trong vòng 6 tháng tới, dựa trên câu hỏi về ý định gắn bó.",
        formula="% Muốn nghỉ = Count(Q30 &le; 2) / Count(Q30 hợp lệ) &times; 100%",
        formula_note="Phân nhóm: <b>Muốn nghỉ</b> (điểm 1-2) &middot; <b>Phân vân</b> (điểm 3) &middot; <b>Gắn bó</b> (điểm 4-5)",
        questions="Q30 (Ý định ở lại 3 tháng, Likert 1-5)",
        scale="0-100%",
        thresholds=[
            {"label": "Thấp", "weight": 10, "color": "#10B981", "desc": "≤ 10%"},
            {"label": "Trung bình", "weight": 10, "color": "#F59E0B", "desc": "11-20%"},
            {"label": "Cao", "weight": 80, "color": "#DC2626", "desc": "> 20%"},
        ]
    ), unsafe_allow_html=True)

    st.markdown(_card(
        number=6,
        accent_color="#15803D",
        title="Intent Retention Rate", subtitle="Tỷ lệ Nhân viên Gắn bó",
        description="Tỷ lệ nhân viên có ý định gắn bó lâu dài với tổ chức, là chỉ số đối nghịch với Flight Risk.",
        formula="% Gắn bó = Count(Q30 &ge; 4) / Count(Q30 hợp lệ) &times; 100%",
        formula_note="Nhóm này có xu hướng ở lại tổ chức, cần duy trì và phát huy.",
        questions="Q30 (Ý định ở lại 3 tháng, Likert 1-5)",
        scale="0-100%",
        thresholds=[
            {"label": "Thấp", "weight": 50, "color": "#DC2626", "desc": "< 50%"},
            {"label": "Trung bình", "weight": 20, "color": "#F59E0B", "desc": "50-69%"},
            {"label": "Tốt", "weight": 30, "color": "#10B981", "desc": "≥ 70%"},
        ]
    ), unsafe_allow_html=True)

    st.markdown(_card(
        number=7,
        accent_color="#7C3AED",
        title="Stay Intention Score", subtitle="Điểm Ý định Ở lại",
        description="Điểm trung bình của câu hỏi về ý định gắn bó, phản ánh mức độ cam kết ở lại trung bình của toàn bộ nhân viên.",
        formula="Stay Score = mean(Q22)",
        formula_note="Điểm trung bình trên thang Likert 1-5 của câu hỏi về thu nhập phản ánh công sức (proxy cho stay intention).",
        questions="Q22",
        scale="1-5",
        thresholds=[
            {"label": "Nguy hiểm", "weight": 40, "color": "#DC2626", "desc": "< 3.0"},
            {"label": "Trung bình", "weight": 20, "color": "#F59E0B", "desc": "3.0-3.9"},
            {"label": "Tốt", "weight": 40, "color": "#10B981", "desc": "≥ 4.0"},
        ]
    ), unsafe_allow_html=True)

    st.markdown(_card(
        number=8,
        accent_color="#EF4444",
        title="Burnout Risk Score", subtitle="Điểm Rủi ro Kiệt sức",
        description="Dựa trên mô hình JD-R (Job Demands-Resources). Nếu Áp lực liên tục lớn hơn Nguồn lực, nhân viên sẽ rơi vào trạng thái kiệt quệ.",
        formula="Burnout = mean(Q18, Q29) - mean(Q11, Q16)",
        formula_note="<b>Áp lực (Demands):</b> Q18 (Cường độ/An toàn LĐ), Q29 (Áp lực/Tôn trọng). <b>Nguồn lực (Resources):</b> Q11 (Hỗ trợ kịp thời), Q16 (App/Xe an toàn). Burnout > 0 = Áp lực > Nguồn lực.",
        questions="Q11, Q16, Q18, Q29",
        scale="0-100%",
        thresholds=[
            {"label": "An toàn", "weight": 15, "color": "#10B981", "desc": "≤ 15%"},
            {"label": "Cần chú ý", "weight": 15, "color": "#F59E0B", "desc": "16-30%"},
            {"label": "Nguy hiểm", "weight": 70, "color": "#DC2626", "desc": "> 30%"},
        ]
    ), unsafe_allow_html=True)

    st.markdown(_card(
        number=9,
        accent_color="#EA580C",
        title="Stay Risk Segmentation", subtitle="Phân nhóm Rủi ro Ở lại",
        description="Phân loại nhân viên thành 3 nhóm rủi ro dựa trên điểm ý định gắn bó, giúp xác định đối tượng cần can thiệp giữ chân.",
        formula="Flight Risk: Q22 &le; 2 &ensp;|&ensp; At Risk: Q22 = 3 &ensp;|&ensp; Stable: Q22 &ge; 4",
        formula_note="Mỗi nhóm được tính % trên tổng số nhân viên hợp lệ.",
        questions="Q22",
        scale="0-100% cho mỗi nhóm",
        thresholds=[
            {"label": "Flight Risk", "weight": 33, "color": "#DC2626", "desc": "Q22 ≤ 2: Nguy cơ rời đi cao"},
            {"label": "At Risk", "weight": 33, "color": "#F59E0B", "desc": "Q22 = 3: Đang cân nhắc"},
            {"label": "Stable", "weight": 34, "color": "#10B981", "desc": "Q22 ≥ 4: Ổn định"},
        ]
    ), unsafe_allow_html=True)

    st.markdown(_card(
        number=10,
        accent_color="#059669",
        title="eNPS Segment Distribution", subtitle="Phân bố Đại sứ / Thụ động / Bất mãn",
        description="Phân bố chi tiết nhân viên theo 3 nhóm trung thành, giúp hiểu cấu trúc của điểm eNPS tổng thể.",
        formula="Promoter: Q31 &ge; 9 &ensp;|&ensp; Passive: Q31 &isin; {7, 8} &ensp;|&ensp; Detractor: Q31 &le; 6",
        formula_note="<b>Promoter:</b> Trung thành, nhiệt huyết. <b>Passive:</b> Hài lòng nhưng dễ bị thu hút bởi offer khác. <b>Detractor:</b> Không hài lòng, có khả năng lan truyền tiêu cực.",
        questions="Q31 (thang 0-10)",
        scale="% cho mỗi nhóm",
        thresholds=[
            {"label": "Detractor", "weight": 33, "color": "#DC2626", "desc": "Q31 ≤ 6: Bất mãn"},
            {"label": "Passive", "weight": 33, "color": "#F59E0B", "desc": "Q31 = 7-8: Thụ động"},
            {"label": "Promoter", "weight": 34, "color": "#10B981", "desc": "Q31 ≥ 9: Đại sứ"},
        ]
    ), unsafe_allow_html=True)


def _render_deep_analysis():
    st.markdown(_section_header(
        "Chỉ số Phân tích Chuyên sâu",
        "Các phương pháp thống kê và phân tích nâng cao để tìm ra nguyên nhân và ưu tiên hành động."
    ), unsafe_allow_html=True)

    st.markdown(_quick_reference_table([
        {"name": "Spearman Correlation", "formula": "ρ = spearmanr(Q, EI)", "questions": "Q9-Q29 vs EI"},
        {"name": "Root Cause Gap", "formula": "mean(Q|intent≥4) - mean(Q|intent≤2)", "questions": "Q9-Q29 vs Q30"},
        {"name": "Priority Matrix", "formula": "Median(ρ) × Median(Score)", "questions": "Q9-Q29"},
        {"name": "Response Rate", "formula": "Participants / Headcount × 100%", "questions": "HRIS"},
        {"name": "YoY Delta", "formula": "Value_2026 - Benchmark_2025", "questions": "Tổng hợp"},
    ]), unsafe_allow_html=True)

    st.markdown(_card(
        number=11,
        accent_color="#2563EB",
        title="Spearman Rank Correlation", subtitle="Hệ số Tương quan Hạng Spearman với EI",
        description="Đo lường mức độ ảnh hưởng của từng câu hỏi đến chỉ số gắn kết tổng thể (EI). Câu hỏi có tương quan cao hơn = ảnh hưởng nhiều hơn đến sự gắn kết.",
        formula="&rho; = spearmanr(Q_score, EI)",
        formula_note="Tính riêng cho từng câu hỏi Likert (Q9-Q29) so với EI. Giá trị &rho; > 0 = câu hỏi đồng biến với EI (điểm cao hơn &rarr; EI cao hơn).",
        questions="Q9-Q29 (từng câu) so với EI",
        scale="-1.0 đến +1.0",
        thresholds=[
            {"label": "Yếu", "weight": 30, "color": "#94A3B8", "desc": "|ρ| < 0.3"},
            {"label": "Trung bình", "weight": 20, "color": "#F59E0B", "desc": "0.3-0.5"},
            {"label": "Mạnh", "weight": 50, "color": "#10B981", "desc": "> 0.5"},
        ]
    ), unsafe_allow_html=True)

    st.markdown(_card(
        number=12,
        accent_color="#CA8A04",
        title="Root Cause Gap Score", subtitle="Chênh lệch Điểm: Nhóm Muốn nghỉ vs. Gắn bó",
        description="So sánh điểm trung bình từng câu hỏi giữa nhóm muốn nghỉ và nhóm gắn bó, giúp xác định nguyên nhân gốc rễ khiến nhân viên muốn rời đi.",
        formula="Gap = mean(Q | intent &ge; 4) - mean(Q | intent &le; 2)",
        formula_note="Gap lớn = câu hỏi đó là nguyên nhân chính khiến nhân viên muốn nghỉ. Top 10 gap lớn nhất được xếp hạng ưu tiên.",
        questions="Q9-Q29 (so sánh theo nhóm Q30)",
        scale="Điểm chênh lệch (Likert 1-5)",
        thresholds=[
            {"label": "Nhỏ", "weight": 50, "color": "#94A3B8", "desc": "< 0.5"},
            {"label": "Đáng kể", "weight": 25, "color": "#F59E0B", "desc": "0.5-1.0"},
            {"label": "Rất nghiêm trọng", "weight": 25, "color": "#DC2626", "desc": "> 1.0"},
        ]
    ), unsafe_allow_html=True)

    st.markdown(_card(
        number=13,
        accent_color="#9333EA",
        title="Impact-Effort Priority Matrix", subtitle="Ma trận Ưu tiên Hành động",
        description="Phân loại từng câu hỏi vào 4 nhóm ưu tiên dựa trên tương quan với EI (Impact) và điểm hiện tại (Effort cần thiết), giúp tập trung nguồn lực hiệu quả.",
        formula="4 góc phần tư dựa trên Median(&rho;) và Median(Score)",
        formula_note="<b>Ưu tiên cao</b> (Impact cao + Điểm thấp): Cần hành động ngay. <b>Duy trì</b> (Impact cao + Điểm cao): Giữ vững. <b>Theo dõi</b> (Impact thấp + Điểm thấp): Quan sát. <b>Không ưu tiên</b> (Impact thấp + Điểm cao): Ít quan trọng.",
        questions="Q9-Q29",
        scale="Phân loại 4 nhóm",
        thresholds=[
            {"label": "Ưu tiên cao", "weight": 25, "color": "#DC2626", "desc": "Hành động ngay"},
            {"label": "Duy trì", "weight": 25, "color": "#10B981", "desc": "Giữ vững"},
            {"label": "Theo dõi", "weight": 25, "color": "#F59E0B", "desc": "Quan sát"},
            {"label": "Không ưu tiên", "weight": 25, "color": "#94A3B8", "desc": "Ít quan trọng"},
        ]
    ), unsafe_allow_html=True)

    st.markdown(_card(
        number=14,
        accent_color="#475569",
        title="Survey Response Rate", subtitle="Tỷ lệ Phản hồi Khảo sát",
        description="Tỷ lệ nhân viên tham gia khảo sát so với tổng số nhân viên, phản ánh mức độ đại diện của dữ liệu.",
        formula="Response Rate = Số người tham gia / Tổng headcount &times; 100%",
        formula_note="Dựa trên dữ liệu headcount từ HRIS so với số lượng phản hồi thực tế.",
        questions="Không áp dụng (dữ liệu HRIS)",
        scale="0-100%",
        thresholds=[
            {"label": "Thấp", "weight": 50, "color": "#DC2626", "desc": "< 50%"},
            {"label": "Chấp nhận", "weight": 20, "color": "#F59E0B", "desc": "50-69%"},
            {"label": "Tốt", "weight": 30, "color": "#10B981", "desc": "≥ 70%"},
        ]
    ), unsafe_allow_html=True)

    st.markdown(_card(
        number=15,
        accent_color="#059669",
        title="Year-over-Year Delta", subtitle="Thay đổi Chỉ số so với Năm trước",
        description="So sánh các chỉ số chính (EI, eNPS) giữa năm hiện tại và năm trước, giúp đánh giá xu hướng cải thiện hoặc suy giảm.",
        formula="&Delta; = Giá trị 2026 - Benchmark 2025",
        formula_note="Benchmark 2025: EI = 80.2%, eNPS = +33.6, Response Rate = 75.9%. Giá trị dương = cải thiện, âm = suy giảm.",
        questions="Không áp dụng (chỉ số tổng hợp)",
        scale="Điểm phần trăm",
        thresholds=[
            {"label": "Suy giảm", "weight": 33, "color": "#DC2626", "desc": "Δ < 0"},
            {"label": "Duy trì", "weight": 33, "color": "#94A3B8", "desc": "Δ = 0"},
            {"label": "Cải thiện", "weight": 34, "color": "#10B981", "desc": "Δ > 0"},
        ]
    ), unsafe_allow_html=True)


def _render_simulation():
    st.markdown(_section_header(
        "Chỉ số Mô phỏng & Dự báo",
        "Các công cụ mô phỏng giúp dự đoán tác động của các can thiệp và ước tính ROI."
    ), unsafe_allow_html=True)

    st.markdown(_quick_reference_table([
        {"name": "KPI Simulator", "formula": "improvement × weight × 100 → ROI", "questions": "EI, eNPS, MEI"},
        {"name": "Micro Risk", "formula": "base + penalties - shields", "questions": "Nhiều yếu tố"},
        {"name": "Macro Risk", "formula": "salary×0.35 + mei×0.5 + cod×0.08", "questions": "Q30, MEI, thu nhập"},
        {"name": "Quality Flags", "formula": "SD=0 | Missing>80%", "questions": "Q9-Q29"},
    ]), unsafe_allow_html=True)

    st.markdown(_card(
        number=16,
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
        thresholds=[
            {"label": "ROI dương = Can thiệp có lợi", "weight": 100, "color": "#10B981", "desc": "Tiết kiệm chi phí tuyển dụng"},
        ]
    ), unsafe_allow_html=True)

    st.markdown(_card(
        number=17,
        accent_color="#DC2626",
        title="Micro Risk Simulator", subtitle="Trình Giả lập Rủi ro Nghỉ việc (Cá nhân)",
        description="Ước tính xác suất nghỉ việc của một nhân viên cụ thể dựa trên các yếu tố cá nhân (thâm niên, thu nhập, MEI, v.v.).",
        formula="""risk = base + tenure_penalty + salary_penalty + ... - mei_shield<br>
(clamped to [min, max])""",
        formula_note="<b>Shipper/Driver:</b> base(30) + tenure(0-25) + salary(0-20) + COD(0-15) - MEI(0-30), clamp [10, 95]. <b>Ops 2A/2B:</b> base(28) + tenure(0-20) + shift(0-18) + equip(0-15) - MEI(0-25), clamp [8, 95]. <b>Office 3A/3B:</b> base(22) + tenure(0-18) + workload(0-22) - recognition(0-20), clamp [5, 92].",
        questions="MEI, thâm niên, thu nhập, ca làm, thiết bị",
        scale="0-100% (xác suất)",
        thresholds=[
            {"label": "Thấp", "weight": 20, "color": "#10B981", "desc": "≤ 20%"},
            {"label": "Trung bình", "weight": 30, "color": "#F59E0B", "desc": "21-50%"},
            {"label": "Cao", "weight": 50, "color": "#DC2626", "desc": "> 50%"},
        ]
    ), unsafe_allow_html=True)

    st.markdown(_card(
        number=18,
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
        thresholds=[
            {"label": "Clamp: [2%, 80%]", "weight": 100, "color": "#94A3B8", "desc": "Giới hạn dự báo"},
        ]
    ), unsafe_allow_html=True)

    st.markdown(_card(
        number=19,
        accent_color="#64748B",
        title="Data Quality Flags", subtitle="Cờ Chất lượng Dữ liệu",
        description="Phát hiện các phản hồi không hợp lệ: trả lời thẳng hàng (straightline) hoặc bỏ trống quá nhiều, đảm bảo độ tin cậy của phân tích.",
        formula="""Straightline: SD(Q9..Q29) = 0 AND &ge; 10 câu hợp lệ<br>
Missing: &gt; 80% câu Likert bị bỏ trống""",
        formula_note="Straightline = tất cả câu trả lời giống nhau (có thể trả lời ngẫu nhiên). Missing = không trả lời phần lớn câu hỏi.",
        questions="Q9-Q29 (tất cả câu Likert)",
        scale="Boolean (Có/Không)",
        thresholds=[
            {"label": "Straightline", "weight": 50, "color": "#F59E0B", "desc": "Loại (2A, 2B, 3A) / Giữ (1A, 1B, 3B)"},
            {"label": "Missing", "weight": 50, "color": "#DC2626", "desc": "Luôn loại"},
        ]
    ), unsafe_allow_html=True)


def _render_nlp():
    st.markdown(_section_header(
        "Chỉ số NLP & Phân tích Văn bản",
        "Các chỉ số được trích xuất từ phản hồi mở (open-text) bằng kỹ thuật xử lý ngôn ngữ tự nhiên."
    ), unsafe_allow_html=True)

    st.markdown(_quick_reference_table([
        {"name": "Warning Signals", "formula": "Keyword + AI validation", "questions": "Q32-Q34"},
        {"name": "Topic Distribution", "formula": "Mentions / Total × 100%", "questions": "Q32-Q34"},
        {"name": "EVP Keywords", "formula": "Word frequency → 4 buckets", "questions": "Q32-Q34"},
    ]), unsafe_allow_html=True)

    st.markdown(_card(
        number=20,
        accent_color="#DC2626",
        title="NLP Warning Signals", subtitle="Tín hiệu Cảnh báo từ Phản hồi Mở",
        description="Phát hiện tự động các tín hiệu tiêu cực từ phản hồi văn bản mở, giúp nhận diện sớm các vấn đề nghiêm trọng.",
        formula="Rule-based keyword detection + AI validation",
        formula_note="<b>5 loại tín hiệu:</b> Ý định nghỉ việc, Kiệt sức, Bất công, Mất niềm tin, Xung đột QL. Sau khi phát hiện bằng keyword, AI được dùng để lọc false positive.",
        questions="Q32, Q33, Q34 (phản hồi mở)",
        scale="Số tín hiệu / Tổng phản hồi",
        thresholds=[
            {"label": "Mỗi tín hiệu được AI xác thực", "weight": 100, "color": "#3B82F6", "desc": "Giảm false positive"},
        ]
    ), unsafe_allow_html=True)

    st.markdown(_card(
        number=21,
        accent_color="#7C3AED",
        title="Topic Distribution with Sentiment", subtitle="Phân bố Chủ đề & Giọng điệu",
        description="Phân loại phản hồi mở thành các chủ đề và đánh giá giọng điệu (tích cực/trung lập/tiêu cực) cho mỗi chủ đề.",
        formula="Topic% = Số đề cập / Tổng phản hồi &times; 100",
        formula_note="Mỗi chủ đề có phân bố: positive%, neutral%, negative%. Giúp hiểu vấn đề nào được quan tâm nhiều nhất và cảm xúc đi kèm.",
        questions="Q32, Q33, Q34 (phản hồi mở)",
        scale="% cho mỗi chủ đề",
        thresholds=[
            {"label": "Nổi bật", "weight": 20, "color": "#3B82F6", "desc": "> 20%"},
            {"label": "Cần chú ý", "weight": 50, "color": "#DC2626", "desc": "Negative > 50%"},
            {"label": "Bình thường", "weight": 30, "color": "#94A3B8", "desc": "Còn lại"},
        ]
    ), unsafe_allow_html=True)

    st.markdown(_card(
        number=22,
        accent_color="#2563EB",
        title="EVP Keyword Frequency", subtitle="Từ khóa EVP Nổi bật",
        description="Đếm tần suất từ khóa trong phản hồi mở, phân nhóm theo 4 yếu tố EVP (Employer Value Proposition) để hiểu nhân viên quan tâm đến điều gì nhất.",
        formula="Word frequency &rarr; bucketed into 4 EVP factors",
        formula_note="<b>4 nhóm EVP:</b> Lương thưởng & Phụ cấp, Công việc & Môi trường, Quản lý & Hỗ trợ, Công nghệ & Quy trình. Tần suất cao = mối quan tâm lớn.",
        questions="Q32, Q33, Q34 (phản hồi mở)",
        scale="Số lần xuất hiện / Tổng phản hồi",
        thresholds=[
            {"label": "Top keywords trong mỗi nhóm EVP", "weight": 100, "color": "#9333EA", "desc": "4 buckets"},
        ]
    ), unsafe_allow_html=True)


def _render_hris():
    st.markdown(_section_header(
        "Chỉ số HRIS & Thu nhập",
        "Các chỉ số kết hợp dữ liệu khảo sát với dữ liệu HRIS (nhân sự) để tìm mối tương quan sâu hơn."
    ), unsafe_allow_html=True)

    st.markdown(_quick_reference_table([
        {"name": "Income × EI", "formula": "mean(EI) by income bracket", "questions": "EI + HRIS"},
        {"name": "Penalty × EI", "formula": "mean(EI) by penalty bracket", "questions": "EI + HRIS"},
        {"name": "Risk Heatmap", "formula": "Risk% = Count(Muốn nghỉ) / N × 100%", "questions": "Q30 + HRIS"},
        {"name": "Warrior × EI", "formula": "mean(EI) by warrior class", "questions": "EI + HRIS"},
        {"name": "Income Structure", "formula": "Mean of components", "questions": "HRIS"},
    ]), unsafe_allow_html=True)

    st.markdown(_card(
        number=23,
        accent_color="#16A34A",
        title="Income x Engagement", subtitle="Tương quan Thu nhập & Gắn kết",
        description="Phân tích mức độ gắn kết (EI) và eNPS theo từng nhóm thu nhập, giúp xác định thu nhập có phải yếu tố quyết định gắn kết hay không.",
        formula="mean(EI) và eNPS theo nhóm thu nhập",
        formula_note="<b>Nhóm thu nhập:</b> &lt;5tr, 5-7tr, 7-10tr, 10-15tr, &gt;15tr. Cho phép so sánh EI và eNPS giữa các nhóm.",
        questions="EI, eNPS + HRIS (thu nhập)",
        scale="EI: 0-100% | eNPS: -100 đến +100",
        thresholds=[
            {"label": "Chênh lệch EI > 15% = Đáng kể", "weight": 100, "color": "#F59E0B", "desc": "So sánh nhóm cao nhất vs thấp nhất"},
        ]
    ), unsafe_allow_html=True)

    st.markdown(_card(
        number=24,
        accent_color="#DC2626",
        title="Penalty x Engagement", subtitle="Tương quan Mức phạt & Gắn kết",
        description="Phân tích tác động của mức phạt (phạt + truy thu COD) đến sự gắn kết, giúp đánh giá chính sách phạt có ảnh hưởng tiêu cực hay không.",
        formula="mean(EI) theo nhóm mức phạt",
        formula_note="<b>Nhóm phạt:</b> Không phạt, &lt;500K, 500K-1tr, 1-3tr, &gt;3tr. tong_phat = Phạt + Truy thu COD.",
        questions="EI + HRIS (phạt, truy thu COD)",
        scale="EI: 0-100%",
        thresholds=[
            {"label": "EI giảm > 10% = Tác động tiêu cực", "weight": 100, "color": "#DC2626", "desc": "Ở nhóm bị phạt nhiều"},
        ]
    ), unsafe_allow_html=True)

    st.markdown(_card(
        number=25,
        accent_color="#CA8A04",
        title="Turnover Risk Heatmap", subtitle="Bản đồ Rủi ro: Thu nhập x Mức phạt",
        description="Heatmap 2 chiều thể hiện tỷ lệ muốn nghỉ việc theo từng kết hợp (nhóm thu nhập, nhóm phạt), giúp xác định nhóm nhân viên có rủi ro cao nhất.",
        formula="Risk% = Count(Muốn nghỉ) / Tổng trong ô &times; 100%",
        formula_note="Chỉ hiển thị các ô có N &ge; 10 để đảm bảo ý nghĩa thống kê. Kết hợp Q30 (ý định) + HRIS (thu nhập, phạt).",
        questions="Q30 + HRIS (thu nhập, phạt)",
        scale="0-100% cho mỗi ô",
        thresholds=[
            {"label": "An toàn", "weight": 15, "color": "#10B981", "desc": "< 15%"},
            {"label": "Cần chú ý", "weight": 15, "color": "#F59E0B", "desc": "15-30%"},
            {"label": "Nguy hiểm", "weight": 70, "color": "#DC2626", "desc": "> 30%"},
        ]
    ), unsafe_allow_html=True)

    st.markdown(_card(
        number=26,
        accent_color="#9333EA",
        title="Warrior Classification x Engagement", subtitle="Phân loại Chiến binh & Gắn kết",
        description="Phân tích mức độ gắn kết theo phân loại chiến binh (từ HRIS), giúp hiểu nhóm chiến binh nào đang gắn kết tốt/yếu.",
        formula="mean(EI) và mean(thu nhập) theo phân loại Chiến binh",
        formula_note="Dựa trên trường 'Phân loại Chiến binh' trong HRIS. Cho phép so sánh EI và thu nhập trung bình giữa các nhóm.",
        questions="EI + HRIS (Phân loại Chiến binh)",
        scale="EI: 0-100%",
        thresholds=[
            {"label": "So sánh EI giữa các nhóm chiến binh", "weight": 100, "color": "#9333EA", "desc": "Phân tích tương quan"},
        ]
    ), unsafe_allow_html=True)

    st.markdown(_card(
        number=27,
        accent_color="#059669",
        title="Income Structure Breakdown", subtitle="Cơ cấu Thu nhập Trung bình",
        description="Phân tích cơ cấu thu nhập trung bình theo từng thành phần, giúp hiểu tỷ trọng lương, thưởng, phụ cấp trong tổng thu nhập.",
        formula="Mean của từng thành phần thu nhập",
        formula_note="<b>Các thành phần:</b> Lương đơn hàng, Thưởng/Phạt GTC và LTC, Phụ cấp, Thưởng Doanh Thu. Hiển thị dưới dạng biểu đồ tròn %.",
        questions="HRIS (cơ cấu thu nhập)",
        scale="VND và %",
        thresholds=[
            {"label": "Phân tích cơ cấu, không phân loại", "weight": 100, "color": "#94A3B8", "desc": "Biểu đồ tròn %"},
        ]
    ), unsafe_allow_html=True)
