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
        <p class="apx-page-eyebrow">Từ điển Chỉ số / Thư viện tham chiếu</p>
        <h1 class="apx-page-title">Phụ lục & Giải thích Chỉ số (EES 2026)</h1>
        <p class="apx-page-desc">
            Tài liệu tham khảo chi tiết về ý nghĩa, diễn giải thực tế và công thức tính toán của tất cả các chỉ số (Kpis) được sử dụng trong Dashboard.
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="apx-context-box">
        <p class="apx-context-title">Tại sao cần hiểu các chỉ số này?</p>
        <p class="apx-context-body">
            Các chỉ số EES không chỉ đơn thuần là "điểm hài lòng". Chúng được thiết kế dựa trên các mô hình 
            thống kê và tâm lý học để phát hiện các <b>rủi ro ngầm</b> (như tỷ lệ đánh lụi, mẫu giả), 
            cũng như dự báo <b>nguy cơ nghỉ việc</b> thực tế. Hiểu rõ từng chỉ số giúp bạn nắm bắt chính xác 
            "sức khỏe" của đội ngũ để đưa ra quyết định kịp thời.
        </p>
    </div>
    """, unsafe_allow_html=True)

    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "Cốt lõi (Core)",
        "Gắn kết (Risk)",
        "Độ tin cậy (Trust)",
        "Phân tích (Analysis)",
        "AI & NLP",
        "HRIS & Năng suất"
    ])

    with tab1:
        _render_core_metrics()
    with tab2:
        _render_risk_engagement()
    with tab3:
        _render_data_trust()
    with tab4:
        _render_deep_analysis()
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
<p class="apx-quick-ref-title">Bảng tóm tắt nhanh</p>
<table class="apx-quick-ref-table">
<thead><tr><th style="width:40px">#</th><th>Tên chỉ số</th><th>Công thức</th><th>Câu hỏi/Nguồn</th></tr></thead>
<tbody>{rows}</tbody>
</table>
</div>"""


def _card(number: int, accent_color: str, title: str, subtitle: str,
          description: str, formula: str, formula_note: str, questions: str,
          scale: str = "", thresholds: list = None) -> str:
    meta_tags = f'<div class="apx-meta-tag"><span class="apx-meta-tag-label">Nguồn/Câu hỏi</span>{questions}</div>'
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
<p class="apx-threshold-label">Phân loại & Ngưỡng báo động</p>
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
<p class="apx-section-label">Giải nghĩa thực tế</p>
<p class="apx-desc">{description}</p>
<p class="apx-section-label">Công thức toán học</p>
<div class="apx-formula-box">{formula}</div>
<p class="apx-note">{formula_note}</p>
<div class="apx-meta-row">{meta_tags}</div>
{threshold_html}
</div>
</div>"""


def _render_core_metrics():
    st.markdown(_section_header(
        "Nhóm Chỉ số Cốt lõi",
        "Những chỉ số tổng hợp quan trọng nhất, đóng vai trò như 'ống nghe nhịp tim' của tổ chức."
    ), unsafe_allow_html=True)

    st.markdown(_quick_reference_table([
        {"name": "Engagement Index", "formula": "EI = Σ(Tỷ lệ tích cực × Trọng số)", "questions": "Q9-Q29"},
        {"name": "Manager Effectiveness", "formula": "MEI = Count(Q≥4) / Count(Q) × 100%", "questions": "TC2 (Quản lý trực tiếp)"},
        {"name": "eNPS", "formula": "%Promoter - %Detractor", "questions": "Q31"},
        {"name": "Pillar Scores", "formula": "(mean - 1) / 4 × 100%", "questions": "Q9-Q29 (Theo nhóm)"},
    ]), unsafe_allow_html=True)

    st.markdown(_card(
        number=1,
        accent_color="#4F46E5",
        title="Engagement Index (EI)", subtitle="Chỉ số Gắn kết Tổ chức",
        description="Điểm số phản ánh mức độ hạnh phúc và cam kết cống hiến của nhân viên. Khi chỉ số này giảm, các vấn đề về thái độ làm việc, kỷ luật và tỷ lệ nghỉ việc thường sẽ tăng cao ngay sau đó.",
        formula="EI = &Sigma;(Tỷ lệ tích cực<sub>i</sub> &times; Trọng số<sub>i</sub>)",
        formula_note="<b>Tính toán:</b> Điểm trung bình của 5 trụ cột được chuẩn hóa sang % (từ thang 1-5). Trọng số: TC1=15%, TC2=25%, TC3=20%, TC4=20%, TC5=20%.",
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
        title="Manager Effectiveness Index (MEI)", subtitle="Chỉ số Năng lực Quản lý (MEI)",
        description="Chấm điểm trực tiếp Trưởng bưu cục/Điều phối viên/Quản lý trực tiếp. Nếu chỉ số này cao, nhân viên ít khi nghỉ việc kể cả khi lương thưởng không quá hấp dẫn (MEI hoạt động như một 'Chiếc khiên' bảo vệ nhân viên khỏi áp lực công việc).",
        formula="MEI = Count(Q &ge; 4) / Count(Q hợp lệ) &times; 100%",
        formula_note="Tính phần trăm (%) số câu trả lời 'Đồng ý' (mức 4) hoặc 'Rất đồng ý' (mức 5) trong Trụ cột số 2 (Quản lý trực tiếp).",
        questions="Các câu hỏi về Quản lý",
        scale="0-100%",
        thresholds=[
            {"label": "Yếu", "weight": 50, "color": "#DC2626", "desc": "< 50%"},
            {"label": "Trung bình", "weight": 34, "color": "#F59E0B", "desc": "50-83%"},
            {"label": "Shield Zone (Tốt)", "weight": 16, "color": "#10B981", "desc": "≥ 84%"},
        ]
    ), unsafe_allow_html=True)

    st.markdown(_card(
        number=3,
        accent_color="#16A34A",
        title="Employee Net Promoter Score (eNPS)", subtitle="Chỉ số Sẵn sàng Giới thiệu",
        description="Dựa trên 1 câu hỏi duy nhất: 'Bạn có sẵn sàng giới thiệu công ty cho bạn bè không?'. Nhân viên có xu hướng chỉ giới thiệu chỗ làm tốt cho người thân để giữ uy tín cá nhân.",
        formula="eNPS = % Đại sứ (Điểm 9-10) - % Kẻ bất mãn (Điểm 0-6)",
        formula_note="Người cho điểm 7-8 bị coi là 'Thụ động' (Passive) và không được tính vào công thức. Một chỉ số eNPS dương đã là dấu hiệu rất tốt.",
        questions="Q31 (Thang điểm 0-10)",
        scale="-100 đến +100",
        thresholds=[
            {"label": "Báo động đỏ", "weight": 50, "color": "#DC2626", "desc": "< 0 (Tiêu cực)"},
            {"label": "Tốt", "weight": 30, "color": "#3B82F6", "desc": "0 đến +29"},
            {"label": "Đỉnh cao", "weight": 20, "color": "#10B981", "desc": "≥ +30"},
        ]
    ), unsafe_allow_html=True)


def _render_risk_engagement():
    st.markdown(_section_header(
        "Nhóm Rủi ro & Ý định ở lại",
        "Các chỉ số cảnh báo sớm khả năng 'bỏ việc' (Turnover) hoặc 'kiệt sức' (Burnout) của nhân sự."
    ), unsafe_allow_html=True)

    st.markdown(_quick_reference_table([
        {"name": "Turnover Intent (Flight Risk)", "formula": "Count(Q30≤2) / Count(Q30) × 100%", "questions": "Q30"},
        {"name": "Intent Retention Rate", "formula": "Count(Q30≥4) / Count(Q30) × 100%", "questions": "Q30"},
        {"name": "Burnout Risk Score", "formula": "mean(Áp lực) - mean(Nguồn lực)", "questions": "Q11, Q16, Q18, Q29"},
    ]), unsafe_allow_html=True)

    st.markdown(_card(
        number=4,
        accent_color="#DC2626",
        title="Turnover Intent / Flight Risk", subtitle="Tỷ lệ Rủi ro Muốn nghỉ việc",
        description="Đo lường tỷ lệ nhân sự đang có ý định 'nhảy việc' trong vòng 3 đến 6 tháng tới. Nếu chỉ số này cao, công ty sắp đối mặt với làn sóng nghỉ việc (Attrition) lớn.",
        formula="% Muốn nghỉ = Count(Q30 &le; 2) / Count(Q30 hợp lệ) &times; 100%",
        formula_note="Được tính từ câu Q30: Nhóm chọn điểm 1 (Rất không đồng ý ở lại) và 2 (Không đồng ý ở lại).",
        questions="Q30 (Ý định ở lại)",
        scale="0-100%",
        thresholds=[
            {"label": "Thấp (An toàn)", "weight": 10, "color": "#10B981", "desc": "≤ 10%"},
            {"label": "Cảnh giác", "weight": 10, "color": "#F59E0B", "desc": "11-20%"},
            {"label": "Báo động đỏ", "weight": 80, "color": "#DC2626", "desc": "> 20%"},
        ]
    ), unsafe_allow_html=True)

    st.markdown(_card(
        number=5,
        accent_color="#EF4444",
        title="Burnout Risk Score", subtitle="Tỷ lệ Rủi ro Kiệt sức",
        description="Đo lường sự cạn kiệt năng lượng. Theo tâm lý học, khi mức độ Áp lực công việc (Cường độ cao) vượt quá Nguồn lực hỗ trợ (Công cụ kém, Sếp bỏ bê), nhân viên sẽ bị 'burnout' (kiệt sức tột độ).",
        formula="Burnout = Điểm trung bình (Áp lực) - Điểm trung bình (Nguồn lực)",
        formula_note="Áp lực (ví dụ: Q18, Q29). Nguồn lực hỗ trợ (ví dụ: Q11, Q16). Nếu kết quả > 0, nghĩa là Áp lực đang đè bẹp Nguồn lực.",
        questions="Q11, Q16, Q18, Q29",
        scale="0-100%",
        thresholds=[
            {"label": "Bình thường", "weight": 15, "color": "#10B981", "desc": "≤ 15%"},
            {"label": "Dấu hiệu mệt mỏi", "weight": 15, "color": "#F59E0B", "desc": "16-30%"},
            {"label": "Kiệt sức", "weight": 70, "color": "#DC2626", "desc": "> 30%"},
        ]
    ), unsafe_allow_html=True)


def _render_data_trust():
    st.markdown(_section_header(
        "Nhóm Độ tin cậy & Làm sạch Dữ liệu",
        "Bộ lọc AI phát hiện các bản ghi khảo sát rác, không trung thực hoặc đánh lụi để làm sạch dữ liệu."
    ), unsafe_allow_html=True)

    st.markdown(_quick_reference_table([
        {"name": "Effective N", "formula": "Khảo sát thô - (Mẫu bị loại trừ)", "questions": "Tất cả"},
        {"name": "Straightlining Rate", "formula": "SD(Q9-Q29) = 0", "questions": "Q9-Q29"},
        {"name": "Mahalanobis Outliers", "formula": "Khoảng cách đa chiều > Ngưỡng Chi-Square", "questions": "Q9-Q29"},
        {"name": "Contradiction Flag", "formula": "Likert cao nhưng NLP bình luận tiêu cực", "questions": "Q9-Q29 & Q32-34"},
    ]), unsafe_allow_html=True)

    st.markdown(_card(
        number=6,
        accent_color="#64748B",
        title="Effective N (Quy mô Mẫu Hiệu dụng)", subtitle="Số lượng bài test thực tế dùng được",
        description="Đây là lượng dữ liệu 'sạch' dùng để tính toán sau khi AI loại bỏ các bài test rác (đánh quá nhanh, bỏ trống, hoặc mâu thuẫn). Tỷ lệ giữ (Retention Rate) của dữ liệu cho biết chất lượng điền khảo sát.",
        formula="N Hiệu dụng = N Khảo sát nộp vào - N Bị phạt (Drop)",
        formula_note="Những bài bị giảm trọng số (Downweight) vẫn được tính nhưng sức ảnh hưởng chỉ bằng một nửa (0.5).",
        questions="Toàn bộ hệ thống",
        scale="Số lượng mẫu",
        thresholds=[
            {"label": "Tỷ lệ giữ < 70% (Rác nhiều)", "weight": 30, "color": "#DC2626", "desc": "Chất lượng khảo sát thấp"},
            {"label": "Tỷ lệ giữ > 80% (Dữ liệu tốt)", "weight": 70, "color": "#10B981", "desc": "Đáng tin cậy"},
        ]
    ), unsafe_allow_html=True)

    st.markdown(_card(
        number=7,
        accent_color="#8B5CF6",
        title="Straightlining Rate", subtitle="Tỷ lệ Đánh thẳng hàng (Đánh lụi)",
        description="Số phần trăm người làm khảo sát chọn đúng 1 mức điểm (Ví dụ: toàn chọn số 3 hoặc toàn chọn số 5) cho tất cả các câu từ đầu đến cuối.",
        formula="Độ lệch chuẩn (Standard Deviation) của nhóm câu Likert = 0",
        formula_note="Đôi khi đánh toàn 5 là do quá hài lòng thực sự (nhất là đối tượng Shipper), nên AI không luôn luôn xóa thẳng tay mà sẽ đối chiếu với bình luận mở.",
        questions="Câu hỏi trắc nghiệm Likert (Q9-Q29)",
        scale="0-100%",
        thresholds=[]
    ), unsafe_allow_html=True)
    
    st.markdown(_card(
        number=8,
        accent_color="#F43F5E",
        title="Contradiction Flags & Mahalanobis", subtitle="Cờ Mâu thuẫn Logic & Outliers",
        description="Cờ mâu thuẫn xuất hiện khi nhân sự đánh full 5 điểm (cực kỳ hài lòng) nhưng lại ghi bình luận 'Sếp tồi, tôi muốn nghỉ việc'. Mahalanobis đo độ bất thường về mặt toán học trong ma trận trả lời.",
        formula="NLP Sentiment < 0 AND Mean(Likert) > 4.5",
        formula_note="Những mẫu bị gắn nhiều cờ (Flag) sẽ bị AI hạ mức tín nhiệm (Downweight) hoặc loại bỏ hoàn toàn (Drop).",
        questions="Câu trắc nghiệm + Câu mở",
        scale="Số lượng cờ",
        thresholds=[]
    ), unsafe_allow_html=True)


def _render_deep_analysis():
    st.markdown(_section_header(
        "Nhóm Phân tích Chuyên sâu & Ước tính",
        "Dùng để tìm ra nguyên nhân gốc rễ và đo lường sự ưu tiên (Priority)."
    ), unsafe_allow_html=True)

    st.markdown(_quick_reference_table([
        {"name": "Root Cause Gap", "formula": "Mean(Người ở lại) - Mean(Người muốn nghỉ)", "questions": "Q9-Q29 vs Q30"},
        {"name": "KPI Impact Simulator", "formula": "Độ cải thiện × Trọng số → Lợi ích eNPS", "questions": "Toàn hệ thống"},
    ]), unsafe_allow_html=True)

    st.markdown(_card(
        number=9,
        accent_color="#CA8A04",
        title="Root Cause Gap Score", subtitle="Độ Chênh lệch Tìm Nguyên nhân Gốc rễ",
        description="Tách nhân sự ra làm 2 nhóm (Nhóm muốn nghỉ vs Nhóm trung thành). So sánh điểm từng câu hỏi của 2 nhóm. Chênh lệch càng lớn, câu hỏi đó càng là lý do chính khiến người ta rời đi.",
        formula="Gap = Mean(Câu hỏi X | Nhóm ở lại) - Mean(Câu hỏi X | Nhóm muốn nghỉ)",
        formula_note="Gap lớn (> 0.5 điểm) tức là vấn đề rất nhạy cảm. Đây là kim chỉ nam để biết phải ưu tiên sửa cái gì trước.",
        questions="So sánh Q9-Q29 với Q30",
        scale="Chênh lệch từ 0.0 - 5.0",
        thresholds=[
            {"label": "Chênh lệch nhỏ", "weight": 50, "color": "#94A3B8", "desc": "< 0.5"},
            {"label": "Lý do đáng kể", "weight": 25, "color": "#F59E0B", "desc": "0.5-1.0"},
            {"label": "Nguyên nhân gốc (Báo động)", "weight": 25, "color": "#DC2626", "desc": "> 1.0"},
        ]
    ), unsafe_allow_html=True)


def _render_nlp():
    st.markdown(_section_header(
        "Nhóm AI Text & Phân tích Ngôn ngữ tự nhiên",
        "Sử dụng trí tuệ nhân tạo (NLP) để 'đọc' và hiểu các đoạn phản hồi văn bản mở."
    ), unsafe_allow_html=True)

    st.markdown(_quick_reference_table([
        {"name": "Warning Signals", "formula": "Keyword Detection + AI Validation", "questions": "Q32-Q34"},
        {"name": "Topic Negative Pct", "formula": "Mentions (Tiêu cực) / Tổng Mentions × 100%", "questions": "Q32-Q34"},
    ]), unsafe_allow_html=True)

    st.markdown(_card(
        number=10,
        accent_color="#06B6D4",
        title="Warning Signals", subtitle="Tín hiệu Cảnh báo Nguy hiểm (AI)",
        description="Thuật toán AI tự động quét hàng chục nghìn đoạn bình luận để tìm ra các dấu hiệu báo động đỏ như: đe dọa bạo lực, kiệt sức tột độ, mâu thuẫn nảy lửa với sếp, hoặc ý định gian lận.",
        formula="Dò tìm Keyword + Dùng LLM/AI để lọc False Positive",
        formula_note="Sau khi dò từ khóa (ví dụ: 'đánh sếp', 'tự tử', 'nghỉ việc'), AI sẽ đọc lại ngữ cảnh để xác định đây là nói đùa hay nguy cơ thật.",
        questions="Phản hồi mở (Q32, Q33, Q34)",
        scale="Số lượng tín hiệu báo động",
        thresholds=[]
    ), unsafe_allow_html=True)


def _render_hris():
    st.markdown(_section_header(
        "Nhóm Nhân sự HRIS & Năng suất (Productivity)",
        "Liên kết dữ liệu khảo sát với hành vi thực tế trên hệ thống nhân sự (Số đơn, KPIs, Nghỉ việc)."
    ), unsafe_allow_html=True)

    st.markdown(_quick_reference_table([
        {"name": "Turnover Rate", "formula": "Số người nghỉ / Tổng Headcount", "questions": "Hệ thống HRIS"},
        {"name": "Productivity Groupings", "formula": "Phân chia lượng đơn giao: Cao, TB, Thấp", "questions": "Hệ thống ODS"},
    ]), unsafe_allow_html=True)

    st.markdown(_card(
        number=11,
        accent_color="#10B981",
        title="Turnover & Productivity", subtitle="Tỷ lệ Nghỉ việc & Phân nhóm Năng suất",
        description="Đối chiếu sự gắn kết (EI) với năng suất thực tế (số đơn giao/ngày) và hành vi nghỉ việc thực tế. Dashboard sẽ chỉ ra: liệu những người giao nhiều đơn nhất có đang muốn nghỉ việc nhiều nhất hay không.",
        formula="Nhóm Năng suất Thấp (<30 đơn), TB (30-60), Cao (>60 đơn)",
        formula_note="Dữ liệu này được kết nối trực tiếp từ Data Warehouse (NeonDB) để chứng minh mối quan hệ giữa Cảm xúc và Năng suất làm việc.",
        questions="Dữ liệu HRIS + Khảo sát EES",
        scale="Hiệu suất thực tế",
        thresholds=[]
    ), unsafe_allow_html=True)

