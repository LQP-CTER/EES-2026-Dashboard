import streamlit as st

_APPENDIX_CSS = """
<style>
.apx-page-header { margin-bottom: 32px; padding-bottom: 24px; border-bottom: 2px solid #F1F5F9; }
.apx-page-eyebrow { font-size: 0.63rem; font-weight: 700; letter-spacing: 0.14em; text-transform: uppercase; color: #FF5200; margin: 0 0 8px; }
.apx-page-title { font-size: 1.65rem; font-weight: 800; color: #0A1F44; margin: 0 0 8px; letter-spacing: -0.03em; line-height: 1.2; }
.apx-page-desc { font-size: 0.88rem; color: #64748B; margin: 0; font-weight: 400; line-height: 1.65; max-width: 700px; }
.apx-tip-box { background: linear-gradient(135deg, #FFF7F3 0%, #FFF1EB 100%); border: 1px solid #FECDB5; border-left: 5px solid #FF5200; border-radius: 12px; padding: 20px 24px; margin-bottom: 32px; display: flex; gap: 16px; align-items: flex-start; }
.apx-tip-title { font-size: 0.88rem; font-weight: 700; color: #9A3412; margin: 0 0 6px; }
.apx-tip-body { font-size: 0.84rem; color: #7C2D12; line-height: 1.7; margin: 0; }
.apx-sec-wrap { margin: 4px 0 24px; }
.apx-sec-title-row { display: flex; align-items: center; gap: 10px; margin-bottom: 6px; }
.apx-sec-accent { width: 4px; height: 22px; background: #FF5200; border-radius: 2px; flex-shrink: 0; }
.apx-sec-title { font-size: 1.05rem; font-weight: 800; color: #0A1F44; margin: 0; letter-spacing: -0.01em; }
.apx-sec-desc { font-size: 0.82rem; color: #64748B; margin: 0 0 0 14px; font-weight: 400; line-height: 1.5; }
.apx-quick-ref { background: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 12px; padding: 20px 24px; margin-bottom: 28px; overflow-x: auto; }
.apx-quick-ref-title { font-size: 0.8rem; font-weight: 700; color: #475569; margin: 0 0 14px; text-transform: uppercase; letter-spacing: 0.08em; }
.apx-quick-ref-table { width: 100%; border-collapse: collapse; font-size: 0.79rem; }
.apx-quick-ref-table th { background: #EEF2F7; padding: 9px 14px; text-align: left; font-weight: 700; color: #475569; text-transform: uppercase; font-size: 0.67rem; letter-spacing: 0.09em; border-bottom: 2px solid #D1D9E4; }
.apx-quick-ref-table td { padding: 10px 14px; border-bottom: 1px solid #EEF2F7; color: #334155; vertical-align: top; }
.apx-quick-ref-table tr:last-child td { border-bottom: none; }
.apx-quick-ref-table tr:hover { background: #F1F5F9; }
.apx-qr-num { font-weight: 800; color: #CBD5E1; font-size: 0.72rem; }
.apx-qr-name { font-weight: 700; color: #1E293B; }
.apx-qr-formula { font-family: 'Consolas', 'SF Mono', monospace; font-size: 0.74rem; color: #2563EB; }
.apx-card { background: #FFFFFF; border: 1px solid #E2E8F0; border-left: 5px solid #CBD5E1; border-radius: 14px; margin-bottom: 20px; overflow: hidden; box-shadow: 0 1px 4px rgba(0,0,0,0.04); transition: box-shadow 0.15s ease, transform 0.1s ease; }
.apx-card:hover { box-shadow: 0 6px 20px rgba(0,0,0,0.08); transform: translateY(-1px); }
.apx-card-body { padding: 28px 32px; }
.apx-card-header { display: flex; align-items: flex-start; gap: 18px; margin-bottom: 20px; padding-bottom: 18px; border-bottom: 1px solid #F1F5F9; }
.apx-card-num { font-size: 2rem; font-weight: 900; line-height: 1; flex-shrink: 0; opacity: 0.12; letter-spacing: -0.04em; }
.apx-card-titles { flex: 1; }
.apx-card-title { font-size: 1.15rem; font-weight: 800; color: #0A1F44; margin: 0 0 4px; letter-spacing: -0.015em; line-height: 1.3; }
.apx-card-sub { font-size: 0.82rem; color: #64748B; margin: 0; }
.apx-card-badge { display: inline-flex; align-items: center; background: #F1F5F9; border: 1px solid #E2E8F0; border-radius: 20px; padding: 4px 12px; font-size: 0.72rem; font-weight: 700; color: #475569; margin-left: auto; flex-shrink: 0; align-self: center; }
.apx-label { font-size: 0.67rem; font-weight: 800; text-transform: uppercase; letter-spacing: 0.1em; color: #94A3B8; margin: 0 0 8px; }
.apx-hr-box { background: linear-gradient(135deg, #EFF6FF 0%, #F0FDF4 100%); border: 1px solid #BFDBFE; border-left: 4px solid #3B82F6; border-radius: 10px; padding: 16px 20px; margin-bottom: 16px; font-size: 0.87rem; color: #1E3A5F; line-height: 1.7; }
.apx-hr-box b { color: #1D4ED8; }
.apx-formula-box { background: #F8FAFC; border: 1px solid #E2E8F0; border-left: 4px solid #8B5CF6; border-radius: 8px; padding: 14px 20px; margin-bottom: 10px; font-family: 'Consolas', 'SF Mono', 'Courier New', monospace; font-size: 0.84rem; color: #1E293B; line-height: 1.8; }
.apx-formula-note { font-size: 0.82rem; color: #64748B; line-height: 1.65; margin: 0 0 18px; }
.apx-meta-row { display: flex; gap: 10px; margin-bottom: 18px; flex-wrap: wrap; }
.apx-meta-tag { display: inline-flex; align-items: center; gap: 5px; background: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 6px; padding: 5px 10px; font-size: 0.77rem; font-weight: 600; color: #475569; }
.apx-meta-label { color: #94A3B8; font-weight: 800; text-transform: uppercase; font-size: 0.65rem; letter-spacing: 0.05em; }
.apx-thresh-wrap { margin-top: 4px; }
.apx-thresh-label { font-size: 0.67rem; font-weight: 800; text-transform: uppercase; letter-spacing: 0.1em; color: #94A3B8; margin: 0 0 10px; }
.apx-thresh-track { display: flex; gap: 2px; height: 30px; border-radius: 8px; overflow: hidden; margin-bottom: 10px; }
.apx-thresh-seg { display: flex; align-items: center; justify-content: center; font-size: 0.7rem; font-weight: 700; color: white; text-shadow: 0 1px 2px rgba(0,0,0,0.25); padding: 0 4px; text-align: center; white-space: nowrap; overflow: hidden; }
.apx-thresh-legend { display: flex; gap: 14px; flex-wrap: wrap; }
.apx-thresh-item { display: flex; align-items: center; gap: 6px; font-size: 0.75rem; color: #475569; font-weight: 500; }
.apx-thresh-dot { width: 10px; height: 10px; border-radius: 3px; flex-shrink: 0; }
.apx-new-badge { display: inline-block; background: #DCFCE7; color: #166534; font-size: 0.65rem; font-weight: 800; padding: 2px 8px; border-radius: 10px; letter-spacing: 0.05em; text-transform: uppercase; margin-left: 8px; vertical-align: middle; }
.apx-pillar-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 10px; margin-bottom: 20px; }
.apx-pillar-item { display: flex; align-items: center; gap: 10px; background: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 8px; padding: 10px 14px; }
.apx-pillar-dot { width: 12px; height: 12px; border-radius: 50%; flex-shrink: 0; }
.apx-pillar-name { font-size: 0.8rem; font-weight: 700; color: #1E293B; margin: 0; line-height: 1.2; }
.apx-pillar-weight { font-size: 0.72rem; color: #64748B; margin: 2px 0 0; }
</style>
"""


def render(**kwargs):
    st.markdown(_APPENDIX_CSS, unsafe_allow_html=True)

    st.markdown("""
    <div class="apx-page-header">
        <p class="apx-page-eyebrow">Từ điển Chỉ số / EES 2026</p>
        <h1 class="apx-page-title">Phụ lục &amp; Giải thích Chỉ số</h1>
        <p class="apx-page-desc">
            Tài liệu tham khảo về ý nghĩa thực tế, cách đọc kết quả, và công thức tính toán
            của tất cả chỉ số xuất hiện trong Dashboard EES 2026.
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="apx-tip-box">
        <div>
            <p class="apx-tip-title">Đọc chỉ số như thế nào cho đúng?</p>
            <p class="apx-tip-body">
                Các chỉ số EES không phải "điểm hài lòng" đơn thuần &mdash; chúng được thiết kế để
                <b>phát hiện rủi ro trước khi xảy ra</b>. Một chỉ số thấp không có nghĩa là "nhân viên
                không vui" &mdash; nó là tín hiệu để hỏi thêm và tìm nguyên nhân. Dùng phụ lục này
                như một cuốn từ điển: tra cứu khi cần, không cần ghi nhớ hết.
            </p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
        "Chỉ số Cốt lõi",
        "Rủi ro & Ý định",
        "Độ tin cậy Dữ liệu",
        "Phân tích Chuyên sâu",
        "AI & Văn bản mở",
        "HRIS & Năng suất",
        "Nguồn & Mô hình",
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
    with tab7:
        _render_sources_models()


# ── Helpers ──────────────────────────────────────────────────────────

def _sec(title, desc):
    st.markdown(f"""
<div class="apx-sec-wrap">
  <div class="apx-sec-title-row">
    <span class="apx-sec-accent"></span>
    <p class="apx-sec-title">{title}</p>
  </div>
  <p class="apx-sec-desc">{desc}</p>
</div>""", unsafe_allow_html=True)


def _quick_ref(items):
    rows = ""
    for i, it in enumerate(items, 1):
        new_tag = '<span class="apx-new-badge">Mới</span>' if it.get("new") else ""
        rows += f"""<tr>
<td class="apx-qr-num">{i:02d}</td>
<td><span class="apx-qr-name">{it["name"]}</span>{new_tag}</td>
<td class="apx-qr-formula">{it["formula"]}</td>
<td style="color:#64748B;font-size:0.77rem">{it["questions"]}</td>
</tr>"""
    st.markdown(f"""<div class="apx-quick-ref">
<p class="apx-quick-ref-title">Bảng tóm tắt nhanh</p>
<table class="apx-quick-ref-table">
<thead><tr>
  <th style="width:36px">#</th>
  <th>Tên chỉ số</th>
  <th>Công thức tóm tắt</th>
  <th>Nguồn dữ liệu</th>
</tr></thead>
<tbody>{rows}</tbody>
</table>
</div>""", unsafe_allow_html=True)


def _card(num, color, title, sub, badge,
          hr_meaning, formula, formula_note,
          source, scale="", thresholds=None, is_new=False):
    new_tag = '<span class="apx-new-badge">Mới</span>' if is_new else ""
    meta = f'<div class="apx-meta-tag"><span class="apx-meta-label">Nguồn</span>{source}</div>'
    if scale:
        meta += f'<div class="apx-meta-tag"><span class="apx-meta-label">Thang đo</span>{scale}</div>'

    thresh_html = ""
    if thresholds:
        segs = "".join(
            f'<div class="apx-thresh-seg" style="flex:{t["w"]};background:{t["color"]};">{t["label"]}</div>'
            for t in thresholds
        )
        legend = "".join(
            f'<div class="apx-thresh-item"><div class="apx-thresh-dot" style="background:{t["color"]};"></div>{t["desc"]}</div>'
            for t in thresholds
        )
        thresh_html = f"""<div class="apx-thresh-wrap">
<p class="apx-thresh-label">Ngưỡng &amp; Phân loại</p>
<div class="apx-thresh-track">{segs}</div>
<div class="apx-thresh-legend">{legend}</div>
</div>"""

    st.markdown(f"""
<div class="apx-card" style="border-left-color:{color};">
<div class="apx-card-body">
  <div class="apx-card-header">
    <div class="apx-card-num" style="color:{color};">{num:02d}</div>
    <div class="apx-card-titles">
      <p class="apx-card-title">{title}{new_tag}</p>
      <p class="apx-card-sub">{sub}</p>
    </div>
    <div class="apx-card-badge">{badge}</div>
  </div>
  <p class="apx-label">Ý nghĩa với HR</p>
  <div class="apx-hr-box">{hr_meaning}</div>
  <p class="apx-label">Cách tính</p>
  <div class="apx-formula-box">{formula}</div>
  <p class="apx-formula-note">{formula_note}</p>
  <div class="apx-meta-row">{meta}</div>
  {thresh_html}
</div>
</div>""", unsafe_allow_html=True)


# ── Tab 1: Chỉ số Cốt lõi ────────────────────────────────────────────

def _render_core_metrics():
    _sec("Chỉ số Cốt lõi", "Bốn chỉ số quan trọng nhất — đọc ngay để biết 'sức khỏe' tổng thể của đội ngũ.")

    _quick_ref([
        {"name": "Engagement Index (EI)", "formula": "Sum(Điểm trụ cột x Trọng số) %", "questions": "Q9-Q29"},
        {"name": "Manager Effectiveness Index (MEI)", "formula": "% câu >= 4 trong Trụ cột TC2", "questions": "Q11-Q15"},
        {"name": "Employee NPS (eNPS)", "formula": "%Promoter (9-10) - %Detractor (0-6)", "questions": "Q31"},
        {"name": "Điểm 5 Trụ cột (Pillar Scores)", "formula": "(Mean - 1) / 4 x 100%", "questions": "Q9-Q29 theo nhóm"},
        {"name": "Tỷ lệ Tham gia (Participation Rate)", "formula": "N đơn vị / N toàn nhóm x 100%", "questions": "Tự động", "new": True},
    ])

    _card(
        num=1, color="#4F46E5",
        title="Engagement Index (EI)", sub="Chỉ số Gắn kết Tổng thể",
        badge="Core KPI",
        hr_meaning="""
Đây là chỉ số quan trọng nhất của toàn khảo sát &mdash; đo lường mức độ nhân viên
<b>tâm huyết, cống hiến và gắn bó</b> với tổ chức.
<br><br>
Cách đọc đơn giản: <b>EI cao = nhân viên làm việc có nhiệt huyết, ít muốn nghỉ.</b>
EI thấp = đội ngũ đang mệt mỏi hoặc mất phương hướng &mdash; cần tìm hiểu nguyên nhân ngay,
trước khi thấy làn sóng nghỉ việc.
""",
        formula="EI = TC1x15% + TC2x25% + TC3x20% + TC4x20% + TC5x20%",
        formula_note="Mỗi trụ cột được chuẩn hóa từ thang 1-5 về thang %. Trọng số phản ánh mức độ ảnh hưởng thực tế đến ý định ở lại &mdash; TC2 (Quản lý trực tiếp) chiếm nhiều nhất vì quản lý là yếu tố giữ người hiệu quả nhất.",
        source="Q9-Q29 (21 câu Likert 1-5)",
        scale="0-100%",
        thresholds=[
            {"label": "Nguy hiểm", "w": 50, "color": "#DC2626", "desc": "< 50% &mdash; Cần hành động khẩn"},
            {"label": "Cảnh báo", "w": 15, "color": "#F59E0B", "desc": "50-64% &mdash; Theo dõi chặt"},
            {"label": "Ổn định", "w": 15, "color": "#3B82F6", "desc": "65-79% &mdash; Duy trì & cải thiện"},
            {"label": "Xuất sắc", "w": 20, "color": "#10B981", "desc": ">= 80% &mdash; Giữ vững"},
        ]
    )

    st.markdown("""
<div class="apx-pillar-grid">
  <div class="apx-pillar-item"><div class="apx-pillar-dot" style="background:#6366F1;"></div>
    <div><p class="apx-pillar-name">TC1 &mdash; Niềm tin Lãnh đạo</p><p class="apx-pillar-weight">Trọng số: 15%</p></div></div>
  <div class="apx-pillar-item"><div class="apx-pillar-dot" style="background:#0EA5E9;"></div>
    <div><p class="apx-pillar-name">TC2 &mdash; Quản lý Trực tiếp</p><p class="apx-pillar-weight">Trọng số: 25%</p></div></div>
  <div class="apx-pillar-item"><div class="apx-pillar-dot" style="background:#F59E0B;"></div>
    <div><p class="apx-pillar-name">TC3 &mdash; Môi trường &amp; Công cụ</p><p class="apx-pillar-weight">Trọng số: 20%</p></div></div>
  <div class="apx-pillar-item"><div class="apx-pillar-dot" style="background:#EF4444;"></div>
    <div><p class="apx-pillar-name">TC4 &mdash; Đãi ngộ &amp; Công bằng</p><p class="apx-pillar-weight">Trọng số: 20%</p></div></div>
  <div class="apx-pillar-item"><div class="apx-pillar-dot" style="background:#8B5CF6;"></div>
    <div><p class="apx-pillar-name">TC5 &mdash; Văn hóa &amp; Tự hào</p><p class="apx-pillar-weight">Trọng số: 20%</p></div></div>
</div>
""", unsafe_allow_html=True)

    _card(
        num=2, color="#DB2777",
        title="Manager Effectiveness Index (MEI)", sub="Chỉ số Năng lực Quản lý Trực tiếp",
        badge="Shield KPI",
        hr_meaning="""
MEI đo lường chất lượng của <b>Quản lý trực tiếp</b> (AM, TBC, Điều phối viên...) theo góc nhìn
của nhân viên &mdash; họ có được hỗ trợ đúng lúc không, có được đối xử công bằng không,
có nhận phản hồi thường xuyên không.
<br><br>
Khi MEI cao, nhân viên thường <b>ở lại kể cả khi thu nhập chưa phải tốt nhất</b> &mdash;
vì quản lý giỏi là "tấm khiên" giúp họ vượt qua áp lực ngày-qua-ngày.
""",
        formula="MEI = Số câu được chọn >= 4 / Tổng câu hợp lệ x 100%",
        formula_note="Tính từ nhóm câu hỏi Trụ cột TC2 (Q11-Q15). Người chọn mức 4 (Đồng ý) hoặc 5 (Rất đồng ý) được tính là 'Hài lòng với quản lý'. Phần còn lại là tín hiệu cần cải thiện.",
        source="Q11-Q15 (Trụ cột TC2)",
        scale="0-100%",
        thresholds=[
            {"label": "Yếu &mdash; Cần thay đổi", "w": 50, "color": "#DC2626", "desc": "< 50%"},
            {"label": "Trung bình", "w": 34, "color": "#F59E0B", "desc": "50-83%"},
            {"label": "Tốt &mdash; Vùng an toàn", "w": 16, "color": "#10B981", "desc": ">= 84%"},
        ]
    )

    _card(
        num=3, color="#16A34A",
        title="Employee Net Promoter Score (eNPS)", sub="Sẵn sàng Giới thiệu GHN cho người thân",
        badge="NPS",
        hr_meaning="""
eNPS hỏi một câu duy nhất: <i>"Trên thang 0-10, bạn có sẵn sàng giới thiệu GHN cho
người thân/bạn bè không?"</i>
<br><br>
Người cho <b>9-10 điểm</b> là Đại sứ (Promoter) &mdash; họ tự hào về chỗ làm. Người cho
<b>0-6 điểm</b> là Người bất mãn (Detractor). Nhóm <b>7-8 điểm</b> (Thụ động) không được tính.
<br><br>
eNPS dương (&gt; 0) đã là tốt. eNPS âm nghĩa là số người không hài lòng đang nhiều hơn người tự hào.
""",
        formula="eNPS = % Đại sứ (9-10 điểm) - % Người bất mãn (0-6 điểm)",
        formula_note="Thang điểm từ -100 đến +100. Xu hướng tăng/giảm qua các kỳ quan trọng hơn giá trị tuyệt đối.",
        source="Q31 (Thang điểm 0-10)",
        scale="-100 đến +100",
        thresholds=[
            {"label": "Tiêu cực", "w": 50, "color": "#DC2626", "desc": "< 0 &mdash; Nhiều người bất mãn hơn đại sứ"},
            {"label": "Tốt", "w": 30, "color": "#3B82F6", "desc": "0 đến +29"},
            {"label": "Rất tốt", "w": 20, "color": "#10B981", "desc": ">= +30 &mdash; Đội ngũ gắn kết cao"},
        ]
    )

    _card(
        num=4, color="#0EA5E9",
        title="Tỷ lệ Tham gia (Participation Rate)", sub="Độ phủ khảo sát của đơn vị so với toàn nhóm",
        badge="Mới",
        hr_meaning="""
Khi xem báo cáo của một đơn vị (Phòng ban, Section), tỷ lệ tham gia cho biết đơn vị đó chiếm
<b>bao nhiêu % tổng số người trả lời của toàn nhóm</b>.
<br><br>
Tỷ lệ thấp <b>không có nghĩa là nhân viên không hợp tác</b> &mdash; có thể đơn vị đó vốn dĩ nhỏ.
Nhưng nếu một đơn vị lớn mà tỷ lệ tham gia thấp bất thường, đáng hỏi thêm về lý do.
""",
        formula="Participation Rate = N (đơn vị) / N (toàn nhóm) x 100%",
        formula_note="Ví dụ: Section Vùng TBB có 35 phản hồi, toàn nhóm 1A có 800 phản hồi thì Participation Rate = 35/800 = 4.4%.",
        source="Tự động từ dữ liệu khảo sát",
        scale="%",
        is_new=True
    )


# ── Tab 2: Rủi ro & Ý định ────────────────────────────────────────────

def _render_risk_engagement():
    _sec("Rủi ro & Ý định ở lại", "Các tín hiệu cảnh báo sớm về nguy cơ nghỉ việc, kiệt sức và mất gắn kết.")

    _quick_ref([
        {"name": "Turnover Intent / Flight Risk", "formula": "% chọn Q30 <= 2", "questions": "Q30"},
        {"name": "Burnout Risk Score", "formula": "% điểm Áp lực cao + Nguồn lực thấp", "questions": "Q11, Q16, Q18, Q29"},
        {"name": "JSI &mdash; Job Satisfaction Index", "formula": "Điểm tổng hợp từ các câu hài lòng", "questions": "Nhóm câu hài lòng", "new": True},
        {"name": "EWS &mdash; Early Warning Score", "formula": "EI thấp + Q30 thấp + Silence cao", "questions": "Toàn khảo sát", "new": True},
        {"name": "Engagement Quadrant", "formula": "Ma trận EI x Ý định ở lại", "questions": "EI + Q30", "new": True},
        {"name": "Stay Intention", "formula": "Mean(Q30) — thang 1-5", "questions": "Q30"},
    ])

    _card(
        num=5, color="#DC2626",
        title="Turnover Intent (Flight Risk)", sub="Tỷ lệ Nhân viên có Ý định Nghỉ việc",
        badge="Rủi ro cao",
        hr_meaning="""
Chỉ số này đếm tỷ lệ nhân viên đang <b>nghiêng về phía muốn rời đi</b> &mdash; cụ thể là những người
chọn điểm 1 hoặc 2 ở câu hỏi về ý định ở lại.
<br><br>
Đây không phải dự đoán chắc chắn ai sẽ nghỉ &mdash; mà là <b>tín hiệu để ưu tiên giữ chân</b>.
Khi chỉ số vượt 20%, đội ngũ HR và quản lý cần hành động trực tiếp với nhóm này trước khi mất người.
""",
        formula="% Muốn nghỉ = Count(Q30 <= 2) / Count(Q30 hợp lệ) x 100%",
        formula_note="Flight Risk là chỉ số tổng hợp từ ý định nghỉ (Q30), eNPS cá nhân và thâm niên. Ở đơn vị mẫu nhỏ, gần như trùng với tỷ lệ Q30 <= 2. Q30: Điểm 1-2 = Muốn rời. Điểm 4-5 = Ổn định. Điểm 3 = Chưa rõ.",
        source="Q30 + eNPS cá nhân + Thâm niên",
        scale="0-100%",
        thresholds=[
            {"label": "An toàn", "w": 10, "color": "#10B981", "desc": "<= 10%"},
            {"label": "Cảnh giác", "w": 10, "color": "#F59E0B", "desc": "11-20% &mdash; Cần rà soát"},
            {"label": "Báo động đỏ", "w": 80, "color": "#DC2626", "desc": "> 20% &mdash; Hành động ngay"},
        ]
    )

    _card(
        num=6, color="#EF4444",
        title="Burnout Risk Score", sub="Tỷ lệ Nhân viên có nguy cơ Kiệt sức",
        badge="Burnout",
        hr_meaning="""
Nhân viên bị kiệt sức khi <b>áp lực công việc vượt quá sức chịu đựng</b> &mdash; cường độ làm việc cao
nhưng công cụ thiếu, sếp không hỗ trợ, và không thấy ý nghĩa trong công việc.
<br><br>
Khác với "bận rộn": người bận nhưng được hỗ trợ tốt thường <b>không bị burnout</b>.
Người bị kiệt sức thường là những người đang cố gắng nhất nhưng cảm thấy bị bỏ mặc.
""",
        formula="Burnout % = % nhân viên có (Điểm áp lực cao) VÀ (Điểm nguồn lực thấp)",
        formula_note="BRI = % nhân viên có điểm rủi ro kiệt sức vượt ngưỡng 0.5 (thang 0-1). Áp lực đến từ Q18 và Q29; nguồn lực từ Q11 và Q16. BRI <= 5% là thấp, đạt mức an toàn (GHN 2026: ~5.0%).",
        source="Q11, Q16, Q18, Q29",
        scale="0-100%",
        thresholds=[
            {"label": "Bình thường", "w": 15, "color": "#10B981", "desc": "<= 15%"},
            {"label": "Dấu hiệu mệt mỏi", "w": 15, "color": "#F59E0B", "desc": "16-30% &mdash; Theo dõi"},
            {"label": "Nguy cơ kiệt sức", "w": 70, "color": "#DC2626", "desc": "> 30% &mdash; Cần can thiệp"},
        ]
    )

    _card(
        num=7, color="#7C3AED",
        title="Job Satisfaction Index (JSI)", sub="Chỉ số Hài lòng Công việc tổng hợp",
        badge="JSI",
        hr_meaning="""
JSI tổng hợp mức độ hài lòng của nhân viên với <b>những yếu tố hàng ngày</b>: công việc có rõ ràng
không, công cụ có đủ không, đồng nghiệp có hỗ trợ không.
<br><br>
JSI <b>bổ sung cho EI</b>: EI đo gắn kết cảm xúc (tôi có muốn cống hiến không?), còn JSI đo sự
hài lòng thực tế (tôi có đang làm việc được thoải mái không?). Cả hai có thể di chuyển độc lập nhau.
""",
        formula="JSI = Điểm trung bình có trọng số của nhóm câu hỏi hài lòng công việc",
        formula_note="Dữ liệu JSI được tổng hợp từ cột JSI trong database (đã tính sẵn). Thang điểm 0-100, chuẩn hóa tương tự EI.",
        source="Cột JSI (pre-computed)",
        scale="0-100%",
        is_new=True,
        thresholds=[
            {"label": "Thấp", "w": 40, "color": "#DC2626", "desc": "< 60% &mdash; Nhiều rào cản hàng ngày"},
            {"label": "Trung bình", "w": 30, "color": "#F59E0B", "desc": "60-79%"},
            {"label": "Tốt", "w": 30, "color": "#10B981", "desc": ">= 80%"},
        ]
    )

    _card(
        num=8, color="#F97316",
        title="Early Warning Score (EWS)", sub="Điểm Cảnh báo Sớm Rủi ro Tổng thể",
        badge="EWS",
        hr_meaning="""
EWS là chỉ số tổng hợp giúp phát hiện những nhân viên <b>đang ở trạng thái nguy hiểm</b>
theo nhiều chiều cùng lúc: EI thấp, ý định ở lại thấp, bỏ trống câu hỏi mở (không muốn chia sẻ).
<br><br>
Khi EWS của một đơn vị cao, đó là tín hiệu cần ưu tiên theo dõi &mdash; không phải để "phán xét" ai,
mà để <b>chủ động hỏi thăm và tháo gỡ vướng mắc</b> trước khi họ quyết định rời đi.
""",
        formula="EWS >= 60 => Vùng đỏ | ews_red_pct = % nhân viên có EWS >= 60",
        formula_note="EWS được tính sẵn theo từng cá nhân dựa trên ma trận: điểm EI, điểm ý định ở lại (Q30), và trạng thái im lặng (bỏ trống câu mở). EWS >= 60/100 = vùng đỏ cần theo dõi.",
        source="Cột EWS (pre-computed)",
        scale="0-100 / % nhân viên vùng đỏ",
        is_new=True,
        thresholds=[
            {"label": "An toàn (< 60)", "w": 60, "color": "#10B981", "desc": "EWS < 60 &mdash; Bình thường"},
            {"label": "Vùng đỏ (>= 60)", "w": 40, "color": "#DC2626", "desc": "EWS >= 60 &mdash; Cần theo dõi sát"},
        ]
    )

    _card(
        num=9, color="#0891B2",
        title="Engagement Quadrant", sub="Ma trận phân loại Gắn kết x Ý định ở lại",
        badge="Quadrant",
        hr_meaning="""
Phân loại nhân viên vào <b>4 nhóm</b> dựa trên 2 trục: Mức độ Gắn kết (EI cao/thấp)
và Ý định Ở lại (Q30 cao/thấp):
<br><br>
&bull; <b>Champion (Gắn kết cao + Muốn ở)</b>: Nhóm nòng cốt &mdash; giữ chân và phát triển.<br>
&bull; <b>Loyal but Tired (Gắn kết thấp + Muốn ở)</b>: Đang cố bám trụ nhưng mệt mỏi &mdash; cần hỗ trợ kịp thời.<br>
&bull; <b>Risk (Gắn kết cao + Muốn đi)</b>: Năng lực tốt nhưng đang cân nhắc rời &mdash; nhóm nguy hiểm nhất vì mất người có giá trị.<br>
&bull; <b>Exit (Gắn kết thấp + Muốn đi)</b>: Đã quyết định về mặt tâm lý &mdash; can thiệp khó, cần tìm hiểu nguyên nhân gốc.
""",
        formula="Quadrant = f(EI > ngưỡng, Q30 >= 4)",
        formula_note="Ma trận này giúp HR và quản lý ưu tiên đúng nhóm cần can thiệp thay vì dàn đều nguồn lực. Tỷ lệ từng quadrant xuất hiện trong Dashboard phần phân tích chi tiết.",
        source="EI + Q30",
        scale="4 nhóm phân loại",
        is_new=True
    )

    _card(
        num=10, color="#0EA5E9",
        title="Stay Intention (Ý định Gắn bó)", sub="Điểm trung bình ý định ở lại trên thang 1-5",
        badge="Intent",
        hr_meaning="""
Stay Intention đo <b>điểm trung bình</b> ý định ở lại, khác với Flight Risk (đo tỷ lệ người ở vùng nguy hiểm).
Stay Intention cao (&ge; 4.0) cho thấy đội ngũ nhìn chung muốn gắn bó.
<br><br>
Hai chỉ số này bổ sung nhau: Stay Intention phản ánh <b>xu hướng chung</b>, còn Flight Risk phản ánh
<b>quy mô nhóm rủi ro cao</b>. GHN 2026: Stay Intention đạt <b>4,03/5</b>.
""",
        formula="Stay Intention = Mean(Q30) trên thang 1-5",
        formula_note="Q30 hỏi ý định gắn bó trong 6 tháng tới. Giá trị GHN 2026: 4,03/5. Đây là điểm trung bình toàn công ty; đơn vị có điểm dưới 3,5 cần theo dõi. (Xem thêm: Flight Risk = % có Q30 &le; 2).",
        source="Q30 (thang 1-5)",
        scale="1-5",
        thresholds=[
            {"label": "Rủi ro cao", "w": 35, "color": "#DC2626", "desc": "< 3.5 — Nhiều người đang cân nhắc rời"},
            {"label": "Trung lập", "w": 30, "color": "#F59E0B", "desc": "3.5-3.9"},
            {"label": "Ổn định", "w": 35, "color": "#10B981", "desc": ">= 4.0 — Phần lớn muốn ở lại"},
        ]
    )


# ── Tab 3: Độ tin cậy ─────────────────────────────────────────────────

def _render_data_trust():
    _sec("Độ tin cậy & Làm sạch Dữ liệu", "Bộ lọc tự động phát hiện phiếu trả lời không trung thực, đánh lùi, hoặc mâu thuẫn.")

    _quick_ref([
        {"name": "Effective N (Mẫu hiệu dụng)", "formula": "N nộp - N bị loại (Drop)", "questions": "Tất cả"},
        {"name": "Straightlining Rate", "formula": "% phiếu có SD(Q9-Q29) = 0", "questions": "Q9-Q29"},
        {"name": "Silence Rate", "formula": "% nhân viên bỏ trống toàn bộ câu mở", "questions": "Q32-Q34", "new": True},
        {"name": "Contradiction Flag", "formula": "Likert cao nhưng bình luận tiêu cực", "questions": "Q9-Q29 & Q32-Q34"},
        {"name": "Mahalanobis Outliers", "formula": "Khoảng cách thống kê đa chiều > ngưỡng", "questions": "Q9-Q29"},
    ])

    _card(
        num=10, color="#64748B",
        title="Effective N (Mẫu Hiệu dụng)", sub="Số phiếu thực sự dùng được để phân tích",
        badge="Sample",
        hr_meaning="""
Không phải mọi phiếu nộp vào đều được tính. Hệ thống tự động <b>loại hoặc giảm trọng số</b>
những phiếu có dấu hiệu không trung thực (đánh qua loa, toàn chọn 1 số, mâu thuẫn logic).
<br><br>
<b>Effective N</b> là số phiếu "sạch" dùng để tính kết quả. Tỷ lệ giữ lại cao (&gt; 80%) cho thấy
nhân viên điền khảo sát nghiêm túc &mdash; dữ liệu đáng tin.
""",
        formula="Effective N = N nộp - N Drop | Phiếu Downweight được tính x 0.5",
        formula_note="Phiếu bị Drop = bị loại hoàn toàn. Phiếu bị Downweight = vẫn tính nhưng sức ảnh hưởng chỉ bằng 50%. Tỷ lệ giữ = Effective N / N nộp x 100%.",
        source="Toàn bộ hệ thống",
        scale="Số lượng phiếu",
        thresholds=[
            {"label": "Chất lượng thấp", "w": 30, "color": "#DC2626", "desc": "Tỷ lệ giữ < 70% &mdash; Cần xem lại"},
            {"label": "Chất lượng tốt", "w": 70, "color": "#10B981", "desc": "Tỷ lệ giữ >= 80% &mdash; Đáng tin cậy"},
        ]
    )

    _card(
        num=11, color="#8B5CF6",
        title="Straightlining Rate", sub="Tỷ lệ Đánh thẳng hàng (Chọn cùng một số xuyên suốt)",
        badge="Quality",
        hr_meaning="""
Straightlining xảy ra khi ai đó chọn đúng một mức điểm (ví dụ: toàn chọn 3, hoặc toàn chọn 5)
cho <b>tất cả các câu</b> từ đầu đến cuối &mdash; thường là dấu hiệu điền qua loa, không đọc câu hỏi.
<br><br>
Tuy nhiên, <b>không phải lúc nào cũng là gian lận</b>: một số Shipper toàn chọn 5 vì thực sự
rất hài lòng. Hệ thống sẽ đối chiếu thêm với bình luận mở trước khi quyết định loại phiếu.
""",
        formula="Straightlining = Độ lệch chuẩn (SD) của tất cả câu Q9-Q29 = 0",
        formula_note="Nếu một người chọn đúng cùng một số cho tất cả 21 câu Likert thì SD = 0 và bị gán cờ Straightline. Hệ thống sau đó kiểm tra thêm câu mở để quyết định có loại hay chỉ giảm trọng số.",
        source="Q9-Q29",
        scale="0-100%"
    )

    _card(
        num=12, color="#F43F5E",
        title="Silence Rate", sub="Tỷ lệ Nhân viên không chia sẻ gì ở câu mở",
        badge="Silence",
        hr_meaning="""
Câu hỏi mở không bắt buộc &mdash; nhưng <b>tỷ lệ bỏ trống cao bất thường</b> là tín hiệu đáng chú ý.
<br><br>
Silence Rate cao có thể nghĩa là: nhân viên <b>không tin rằng ý kiến của họ được lắng nghe</b>,
hoặc lo sợ bị nhận diện. Đây là bài toán về văn hóa tâm lý an toàn, không chỉ là vấn đề khảo sát.
""",
        formula="Silence Rate = % nhân viên bỏ trống toàn bộ câu hỏi mở (Q32-Q34)",
        formula_note="Chỉ tính là im lặng khi bỏ trống TẤT CẢ câu mở, không phải chỉ một câu. Câu trả lời quá ngắn (< 3 chữ) cũng bị tính là im lặng thực tế.",
        source="Q32, Q33, Q34",
        scale="0-100%",
        is_new=True,
        thresholds=[
            {"label": "Tốt", "w": 30, "color": "#10B981", "desc": "< 30% &mdash; Nhân viên sẵn lòng chia sẻ"},
            {"label": "Cảnh giác", "w": 30, "color": "#F59E0B", "desc": "30-55%"},
            {"label": "Báo động", "w": 40, "color": "#DC2626", "desc": "> 55% &mdash; Cần xem lại văn hóa phản hồi"},
        ]
    )

    _card(
        num=13, color="#E11D48",
        title="Contradiction Flag & Mahalanobis", sub="Cờ Mâu thuẫn và Phát hiện Ngoại lệ Thống kê",
        badge="Flag",
        hr_meaning="""
Hai bộ lọc bổ sung cho nhau để phát hiện phiếu bất thường:
<br><br>
&bull; <b>Contradiction Flag</b>: Người đánh full 5 điểm nhưng lại viết bình luận mở rất tiêu cực &mdash; rõ ràng mâu thuẫn.<br>
&bull; <b>Mahalanobis</b>: Phép đo thống kê xem mẫu trả lời của ai đó có bất thường so với toàn bộ tập dữ liệu không &mdash; chỉ nhìn cấu trúc tổng thể.
""",
        formula="Flag khi: Mean(Likert) > 4.5 VÀ NLP Sentiment < 0",
        formula_note="Mahalanobis đo khoảng cách thống kê đa chiều. Khoảng cách > ngưỡng Chi-Square thì phiếu bị coi là bất thường. Hai cơ chế này kết hợp giúp giảm False Positive.",
        source="Q9-Q29 + Q32-Q34",
        scale="Số cờ / phiếu"
    )


# ── Tab 4: Phân tích Chuyên sâu ───────────────────────────────────────

def _render_deep_analysis():
    _sec("Phân tích Chuyên sâu", "Các phương pháp tìm nguyên nhân gốc rễ và đo mức độ ưu tiên để cải thiện.")

    _quick_ref([
        {"name": "Root Cause Gap Score", "formula": "Mean(Ở lại) - Mean(Muốn nghỉ) theo từng câu", "questions": "Q9-Q29 x Q30"},
        {"name": "Tenure Cohort Analysis", "formula": "Phân tích EI theo nhóm thâm niên", "questions": "EI + Thâm niên", "new": True},
        {"name": "KPI Impact Simulator", "formula": "Độ cải thiện x Trọng số => Lợi ích EI/eNPS", "questions": "Toàn hệ thống"},
    ])

    _card(
        num=14, color="#CA8A04",
        title="Root Cause Gap Score", sub="Tìm nguyên nhân gốc rễ qua chênh lệch hai nhóm",
        badge="Root Cause",
        hr_meaning="""
Tách nhân viên thành 2 nhóm: <b>Nhóm muốn ở lại</b> (Q30 >= 4) và <b>Nhóm có ý định rời đi</b>
(Q30 <= 2). Sau đó so sánh điểm của từng câu hỏi giữa 2 nhóm này.
<br><br>
<b>Câu nào có chênh lệch lớn nhất</b> = đó là yếu tố quan trọng nhất khiến người ta muốn rời đi.
Đây là kim chỉ nam để biết <b>nên ưu tiên cải thiện điều gì trước</b>.
""",
        formula="Gap(câu X) = Mean(câu X | Nhóm ở lại) - Mean(câu X | Nhóm muốn nghỉ)",
        formula_note="Gap > 1.0 điểm = yếu tố rất quan trọng, cần hành động ngay. Gap 0.5-1.0 = đáng chú ý. Gap < 0.5 = ít liên quan đến quyết định ở lại/ra đi.",
        source="Q9-Q29 (so sánh với Q30)",
        scale="Chênh lệch 0.0-5.0 điểm",
        thresholds=[
            {"label": "Ít liên quan", "w": 50, "color": "#CBD5E1", "desc": "Gap < 0.5"},
            {"label": "Đáng chú ý", "w": 25, "color": "#F59E0B", "desc": "Gap 0.5-1.0"},
            {"label": "Nguyên nhân chính", "w": 25, "color": "#DC2626", "desc": "Gap > 1.0 &mdash; Ưu tiên cao"},
        ]
    )

    _card(
        num=15, color="#0F766E",
        title="Tenure Cohort Analysis", sub="Phân tích Gắn kết theo Nhóm Thâm niên",
        badge="Cohort",
        hr_meaning="""
Chia nhân viên theo thâm niên và xem <b>EI thay đổi như thế nào</b> qua từng giai đoạn.
<br><br>
Phân tích này hay phát hiện điểm vỡ &mdash; thời điểm cụ thể mà gắn kết giảm mạnh. Ví dụ: nếu nhóm
1-3 tháng có EI thấp nhất, đó là dấu hiệu <b>trải nghiệm hội nhập ban đầu có vấn đề</b>,
không phải toàn bộ tổ chức có vấn đề.
""",
        formula="EI_cohort(t) = Mean(EI | thâm niên = t), chỉ tính nhóm N >= 5",
        formula_note="Chỉ hiển thị nhóm thâm niên có ít nhất 5 người (N >= 5) để đảm bảo kết quả có ý nghĩa. Điểm EWS_early được tính thêm cho nhóm thâm niên ngắn để phát hiện nguy cơ sớm.",
        source="Cột EI + Cột thâm niên (tenure)",
        scale="EI theo nhóm (%)",
        is_new=True
    )


# ── Tab 5: AI & Văn bản mở ────────────────────────────────────────────

def _render_nlp():
    _sec("AI & Phân tích Văn bản mở", "Dùng trí tuệ nhân tạo để đọc và hiểu phản hồi tự do của nhân viên.")

    _quick_ref([
        {"name": "Warning Signals", "formula": "Keyword Detection + AI xác nhận ngữ cảnh", "questions": "Q32-Q34"},
        {"name": "Topic Negative %", "formula": "Mentions tiêu cực / Tổng mentions x 100%", "questions": "Q32-Q34"},
        {"name": "EVP Analysis (NLP)", "formula": "Phân loại chủ đề tự động bằng AI", "questions": "Q32-Q34"},
    ])

    _card(
        num=16, color="#06B6D4",
        title="Warning Signals (Tín hiệu Cảnh báo)", sub="AI phát hiện các dấu hiệu nguy hiểm trong bình luận",
        badge="AI / NLP",
        hr_meaning="""
Hệ thống AI tự động quét hàng chục nghìn dòng bình luận để tìm các <b>tín hiệu nguy hiểm nghiêm trọng</b>:
đe dọa bạo lực, kiệt sức tột độ, mâu thuẫn gay gắt với quản lý, hoặc ý định gian lận.
<br><br>
Mục tiêu là giúp HR <b>không bỏ sót những tiếng kêu cứu quan trọng</b> trong hàng nghìn phản hồi &mdash;
công việc mà con người không thể làm thủ công hiệu quả với quy mô lớn.
""",
        formula="Dò từ khóa rủi ro => AI đọc ngữ cảnh => Xác nhận hoặc loại bỏ",
        formula_note="Bước 1: Dò từ khóa gắn cờ ban đầu. Bước 2: AI đọc lại toàn câu để phân định đây là phàn nàn bình thường hay tín hiệu thực sự đáng lo. Tránh báo động nhầm (False Positive).",
        source="Q32, Q33, Q34",
        scale="Số lượng tín hiệu"
    )


# ── Tab 6: HRIS & Năng suất ──────────────────────────────────────────

def _render_hris():
    _sec("Kết nối HRIS & Năng suất", "Liên kết dữ liệu khảo sát với hành vi thực tế: nghỉ việc, năng suất giao đơn.")

    _quick_ref([
        {"name": "Actual Turnover Rate", "formula": "Số người nghỉ thực / Tổng headcount x 100%", "questions": "Hệ thống HRIS"},
        {"name": "Productivity Groupings", "formula": "Phân nhóm theo số đơn giao/ngày", "questions": "Hệ thống ODS"},
        {"name": "EI x Productivity Correlation", "formula": "So sánh EI trung bình theo nhóm năng suất", "questions": "EI + ODS", "new": True},
    ])

    _card(
        num=17, color="#10B981",
        title="HRIS Linkage &mdash; Nghỉ việc & Năng suất", sub="Đối chiếu cảm xúc nhân viên với hành vi thực tế",
        badge="HRIS",
        hr_meaning="""
Dữ liệu khảo sát có giá trị hơn khi <b>kết nối với dữ liệu thực tế</b>: ai đã nghỉ việc sau khảo sát,
ai đang giao nhiều đơn nhất, ai đang có năng suất thấp bất thường?
<br><br>
Ví dụ: nếu nhóm giao &gt; 60 đơn/ngày (Năng suất cao) lại có EI thấp nhất &mdash; đó là dấu hiệu
của burnout ẩn ở người làm tốt nhất. Đây là rủi ro nghiêm trọng cần ưu tiên giải quyết.
""",
        formula="Nhóm Thấp: < 30 đơn/ngày | Trung bình: 30-60 | Cao: > 60 đơn/ngày",
        formula_note="Dữ liệu từ hệ thống vận hành (ODS/Data Warehouse) được kết nối vào dashboard qua NeonDB. Tính năng này chỉ khả dụng khi dữ liệu HRIS đã được đồng bộ.",
        source="HRIS + ODS + Khảo sát EES",
        scale="Đơn/ngày & % nghỉ việc"
    )


# ── Tab 7: Nguồn dữ liệu & Mô hình tham chiếu ──────────────────────────

def _render_sources_models():
    _sec("Nguồn dữ liệu & Mô hình tham chiếu",
         "Báo cáo hợp nhất EES 2026 được xây dựng từ nhiều nguồn phân tích độc lập — phần này giải thích nguồn gốc và nền tảng lý thuyết.")

    st.markdown("""
<div class="apx-quick-ref">
<p class="apx-quick-ref-title">10.2. Nguồn dữ liệu (Section 10.2 báo cáo chính thức)</p>
<table class="apx-quick-ref-table">
<thead><tr>
  <th>Nguồn phân tích</th>
  <th>Mô tả</th>
</tr></thead>
<tbody>
<tr>
  <td class="apx-qr-name">Phân tích sâu theo Khối và Phòng ban (BDA)</td>
  <td style="color:#334155;font-size:0.79rem">Phân tích chi tiết EI, eNPS, Flight Risk theo 11 Khối và các phòng ban trực thuộc</td>
</tr>
<tr>
  <td class="apx-qr-name">Kiểm định độ tin cậy &amp; Đối sánh thị trường (EX &amp; People Analytics)</td>
  <td style="color:#334155;font-size:0.79rem">Kiểm tra chất lượng dữ liệu, straight-line, silence; đối sánh benchmark ngành logistics 2025-2026</td>
</tr>
<tr>
  <td class="apx-qr-name">Phân tích trải nghiệm nhân viên</td>
  <td style="color:#334155;font-size:0.79rem">Phân tích hành trình nhân viên, EVP topics, open-text NLP theo 7 nhóm nhân sự</td>
</tr>
<tr>
  <td class="apx-qr-name">Phân tích 11 Khối với hệ chỉ số nâng cao</td>
  <td style="color:#334155;font-size:0.79rem">Bao gồm EWS, BRI, Engagement Quadrant và Root Cause Gap Score cho từng Khối</td>
</tr>
<tr>
  <td class="apx-qr-name">Tổng hợp phản hồi mở (7 nhóm)</td>
  <td style="color:#334155;font-size:0.79rem">Phân loại chủ đề tự động + xác nhận thủ công; Warning Signals AI screening</td>
</tr>
</tbody>
</table>
<p style="font-size:0.77rem;color:#94A3B8;margin:10px 0 0;">
Số liệu chi tiết theo từng Khối, phòng ban, khu vực và câu hỏi được lưu trong các file Excel kèm theo báo cáo.
</p>
</div>
""", unsafe_allow_html=True)

    st.markdown("""
<div class="apx-quick-ref" style="margin-top:20px;">
<p class="apx-quick-ref-title">Thông tin thu thập dữ liệu</p>
<table class="apx-quick-ref-table">
<thead><tr>
  <th>Hạng mục</th>
  <th>Chi tiết</th>
</tr></thead>
<tbody>
<tr>
  <td class="apx-qr-name">Thời gian khảo sát</td>
  <td style="color:#334155;font-size:0.79rem">19 ngày: 15/03 — 02/04/2026</td>
</tr>
<tr>
  <td class="apx-qr-name">Độ phủ (Coverage)</td>
  <td style="color:#334155;font-size:0.79rem">90% — 19.221 / 21.353 phiếu hợp lệ</td>
</tr>
<tr>
  <td class="apx-qr-name">Tỷ lệ tham gia (Participation)</td>
  <td style="color:#334155;font-size:0.79rem">93,7% trên tổng số nhân viên được mời</td>
</tr>
<tr>
  <td class="apx-qr-name">Trọng số độ tin cậy</td>
  <td style="color:#334155;font-size:0.79rem">
    Sạch (1.0) / Có vấn đề nhẹ — giảm trọng số (0.8) / Downweight (0.5) / Drop (loại)
  </td>
</tr>
<tr>
  <td class="apx-qr-name">Công thức quy đổi YoY (2025 vs 2026)</td>
  <td style="color:#334155;font-size:0.82rem;font-family:monospace;">
    EI_2025 (quy đổi) = Mean_Likert_2025 &times; 2 / 10 &times; 100
  </td>
</tr>
</tbody>
</table>
</div>
""", unsafe_allow_html=True)

    st.markdown("""
<div class="apx-quick-ref" style="margin-top:20px;">
<p class="apx-quick-ref-title">10.3. Mô hình tham chiếu (Section 10.3 báo cáo chính thức)</p>
<table class="apx-quick-ref-table">
<thead><tr>
  <th>Mô hình / Nguồn</th>
  <th>Ứng dụng trong EES 2026</th>
</tr></thead>
<tbody>
<tr>
  <td class="apx-qr-name">AON Hewitt Engagement Model</td>
  <td style="color:#334155;font-size:0.79rem">Nền tảng phân loại ngưỡng EI (Say / Stay / Strive) và khung 5 trụ cột</td>
</tr>
<tr>
  <td class="apx-qr-name">eNPS Framework (Bain &amp; Company)</td>
  <td style="color:#334155;font-size:0.79rem">Công thức Promoter - Detractor; ngưỡng phân loại Tiêu cực / Tốt / Rất tốt</td>
</tr>
<tr>
  <td class="apx-qr-name">Best Employer Research (Kincentric &amp; WTW)</td>
  <td style="color:#334155;font-size:0.79rem">Benchmark thị trường ngành Logistics Đông Nam Á; tham chiếu ngưỡng "Excellent Employer"</td>
</tr>
</tbody>
</table>
<p style="font-size:0.77rem;color:#94A3B8;margin:10px 0 0;">
Tất cả ngưỡng phân loại và cách tính chỉ số được điều chỉnh cho phù hợp đặc thù ngành logistics của GHN.
Benchmark thị trường chỉ mang tính tham khảo do khác biết thang đo, phương pháp và cơ cấu mẫu.
</p>
</div>
""", unsafe_allow_html=True)
