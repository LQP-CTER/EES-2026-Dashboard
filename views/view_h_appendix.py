import streamlit as st


def render(**kwargs):
    st.markdown("""
    <div style="margin-bottom: 24px;">
        <h2 style="color: #0A1F44; font-size: 1.8rem; margin-bottom: 8px;">Phụ lục & Giải thích Chỉ số</h2>
        <p style="color: #475569; font-size: 1.05rem;">
            Tài liệu tham khảo chi tiết về ý nghĩa và công thức tính toán của tất cả các chỉ số được sử dụng trong Dashboard EES 2026.
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div style="background-color: #FFF3EE; border-left: 4px solid #FF5200; padding: 20px; border-radius: 8px; margin-bottom: 30px;">
        <h3 style="color: #FF5200; font-size: 1.2rem; margin-top: 0;">Tại sao cần các chỉ số này?</h3>
        <p style="color: #334155; margin-bottom: 0; line-height: 1.6;">
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


def _metric_card(icon: str, icon_bg: str, icon_color: str, title: str, subtitle: str,
                 description: str, formula: str, formula_note: str, questions: str,
                 scale: str = "", classification: str = ""):
    cls_html = ""
    if classification:
        cls_html = f'<p style="color: #475569; font-size: 0.88rem; margin-bottom: 0;"><b>Phân loại:</b> {classification}</p>'
    scale_html = ""
    if scale:
        scale_html = f'<p style="color: #64748B; font-size: 0.85rem; margin-bottom: 8px;"><b>Thang đo:</b> {scale}</p>'
    return f"""
    <div style="background: white; border: 1px solid #E2E8F0; border-radius: 12px; padding: 24px; margin-bottom: 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.05);">
        <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 16px;">
            <div style="background: {icon_bg}; color: {icon_color}; width: 42px; height: 42px; border-radius: 8px; display: flex; align-items: center; justify-content: center; font-weight: bold; font-size: 0.85rem; flex-shrink: 0;">{icon}</div>
            <h3 style="margin: 0; color: #0A1F44; font-size: 1.05rem;">{title}<br><span style="font-size: 0.85rem; color: #64748B; font-weight: 400;">{subtitle}</span></h3>
        </div>
        <p style="color: #334155; font-size: 0.9rem; line-height: 1.6;"><b>Ý nghĩa:</b> {description}</p>
        <p style="color: #334155; font-size: 0.9rem; margin-bottom: 8px;"><b>Công thức:</b></p>
        <div style="background: #F8FAFC; padding: 12px; border-radius: 6px; font-family: 'Consolas', 'Courier New', monospace; font-size: 0.85rem; margin-bottom: 10px; border: 1px solid #E2E8F0;">
            {formula}
        </div>
        <p style="color: #475569; font-size: 0.85rem; margin-bottom: 8px;">{formula_note}</p>
        <p style="color: #64748B; font-size: 0.85rem; margin-bottom: 8px;"><b>Câu hỏi sử dụng:</b> {questions}</p>
        {scale_html}
        {cls_html}
    </div>
    """


def _render_core_metrics():
    st.markdown("### Các chỉ số Nền tảng")
    st.markdown("Những chỉ số tổng hợp quan trọng nhất, phản ánh sức khỏe tổ chức toàn diện.")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(_metric_card(
            icon="EI", icon_bg="#E0E7FF", icon_color="#4F46E5",
            title="Engagement Index", subtitle="Chỉ số Gắn kết Tổ chức",
            description="Thước đo tổng thể về mức độ gắn kết của nhân viên với công ty, được tổng hợp từ 5 trụ cột cốt lõi: <i>Niềm tin & Định hướng, Quản lý trực tiếp, Môi trường & Công cụ, Đãi ngộ & Công bằng, Văn hóa & Tự hào.</i>",
            formula="EI = &Sigma;(Tỷ lệ tích cực<sub>i</sub> &times; Trọng số<sub>i</sub>)",
            formula_note="<b>Trong đó:</b> Tỷ lệ tích cực = (mean(Q trong trụ cột) - 1) / 4 &times; 100%. Trọng số: TC1=15%, TC2=25%, TC3=20%, TC4=20%, TC5=20%.",
            questions="Q9-Q29 (21 câu Likert 5 điểm)",
            scale="0-100%",
            classification="Xuất sắc &ge; 80% | Khỏe mạnh 65-79% | Cần theo dõi 50-64% | Nghiêm trọng &lt; 50%"
        ), unsafe_allow_html=True)

        st.markdown(_metric_card(
            icon="MEI", icon_bg="#FCE7F3", icon_color="#DB2777",
            title="Manager Effectiveness Index", subtitle="Chỉ số Năng lực Quản lý",
            description="Đánh giá mức độ hiệu quả, sự hỗ trợ và năng lực lãnh đạo của Quản lý trực tiếp từ góc nhìn của nhân viên cấp dưới. Gồm các khía cạnh: Ghi nhận năng lực, Đối xử công bằng, Hỗ trợ khi gặp khó khăn, và Lắng nghe ý kiến.",
            formula="MEI = Count(Q &ge; 4) / Count(Q hợp lệ) &times; 100%",
            formula_note="Tính % câu hỏi được trả lời mức 4 (Đồng ý) hoặc 5 (Hoàn toàn đồng ý) trong nhóm câu hỏi về quản lý trực tiếp.",
            questions="Q11, Q12, Q14, Q15",
            scale="0-100%",
            classification="Ngưỡng khiên (Shield): MEI &gt; 4.2/5.0 (~84%) giảm đáng kể tỷ lệ nghỉ việc"
        ), unsafe_allow_html=True)

    with col2:
        st.markdown(_metric_card(
            icon="eNPS", icon_bg="#DCFCE7", icon_color="#16A34A",
            title="Employee Net Promoter Score", subtitle="Chỉ số Sẵn sàng Giới thiệu",
            description="Đo lường mức độ trung thành của nhân viên. Dựa trên câu hỏi duy nhất: <i>\"Bạn có sẵn sàng giới thiệu GHN là một nơi làm việc tốt cho bạn bè/người thân không?\"</i> (Thang 0-10).",
            formula="eNPS = % Promoter (9-10) - % Detractor (0-6)",
            formula_note="<b>Promoter (Đại sứ):</b> Điểm 9-10. <b>Passive (Thụ động):</b> Điểm 7-8 (không đưa vào công thức). <b>Detractor (Bất mãn):</b> Điểm 0-6.",
            questions="Q31 (thang 0-10)",
            scale="-100 đến +100",
            classification="Xuất sắc &ge; +30 | Tích cực &ge; 0 | Tiêu cực &lt; 0"
        ), unsafe_allow_html=True)

        st.markdown(_metric_card(
            icon="TC", icon_bg="#FEF3C7", icon_color="#D97706",
            title="Pillar Scores (TC1-TC5)", subtitle="Điểm 5 Trụ cột Gắn kết",
            description="Điểm riêng biệt cho từng trụ cột, cho phép xác định chính xác lĩnh vực nào đang mạnh/yếu trong tổ chức.",
            formula="TC_pct = (mean(các Q trong trụ cột) - 1) / 4 &times; 100%",
            formula_note="<b>TC1</b> (Niềm tin & Định hướng): Q9, Q10 | <b>TC2</b> (Quản lý trực tiếp): Q11-Q15 | <b>TC3</b> (Môi trường & Công cụ): Q16-Q20 | <b>TC4</b> (Đãi ngộ & Công bằng): Q21-Q25 | <b>TC5</b> (Văn hóa & Tự hào): Q26-Q29",
            questions="Q9-Q29 (phân nhóm theo trụ cột)",
            scale="0-100% cho mỗi trụ cột",
            classification="Xuất sắc &ge; 80% | Khỏe mạnh 65-79% | Cần theo dõi 50-64% | Nghiêm trọng &lt; 50%"
        ), unsafe_allow_html=True)


def _render_risk_engagement():
    st.markdown("### Chỉ số Rủi ro & Gắn kết")
    st.markdown("Các chỉ số đo lường nguy cơ nghỉ việc, kiệt sức và mức độ gắn bó của nhân viên.")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(_metric_card(
            icon="TR", icon_bg="#FEF2F2", icon_color="#DC2626",
            title="Turnover Intent / Flight Risk", subtitle="Tỷ lệ Muốn nghỉ việc",
            description="Đo lường tỷ lệ nhân viên có ý định rời tổ chức trong vòng 6 tháng tới, dựa trên câu hỏi về ý định gắn bó.",
            formula="% Muốn nghỉ = Count(Q30 &le; 2) / Count(Q30 hợp lệ) &times; 100%",
            formula_note="Phân nhóm: <b>Muốn nghỉ</b> (điểm 1-2) | <b>Phân vân</b> (điểm 3) | <b>Gắn bó</b> (điểm 4-5)",
            questions="Q30 (Ý định ở lại 3 tháng, Likert 1-5)",
            scale="0-100%",
            classification="Thấp &le; 10% | Trung bình &le; 20% | Cao &gt; 20%"
        ), unsafe_allow_html=True)

        st.markdown(_metric_card(
            icon="IR", icon_bg="#F0FDF4", icon_color="#15803D",
            title="Intent Retention Rate", subtitle="Tỷ lệ Nhân viên Gắn bó",
            description="Tỷ lệ nhân viên có ý định gắn bó lâu dài với tổ chức, là chỉ số đối nghịch với Flight Risk.",
            formula="% Gắn bó = Count(Q30 &ge; 4) / Count(Q30 hợp lệ) &times; 100%",
            formula_note="Nhóm này có xu hướng ở lại tổ chức, cần duy trì và phát huy.",
            questions="Q30 (Ý định ở lại 3 tháng, Likert 1-5)",
            scale="0-100%",
            classification="Tốt &ge; 70% | Trung bình 50-69% | Thấp &lt; 50%"
        ), unsafe_allow_html=True)

        st.markdown(_metric_card(
            icon="SI", icon_bg="#EDE9FE", icon_color="#7C3AED",
            title="Stay Intention Score", subtitle="Điểm Ý định Ở lại",
            description="Điểm trung bình của câu hỏi về ý định gắn bó, phản ánh mức độ cam kết ở lại trung bình của toàn bộ nhân viên.",
            formula="Stay Score = mean(Q22)",
            formula_note="Điểm trung bình trên thang Likert 1-5 của câu hỏi về thu nhập phản ánh công sức (proxy cho stay intention).",
            questions="Q22",
            scale="1-5",
            classification="Tốt &ge; 4.0 | Trung bình &ge; 3.0 | Nguy hiểm &lt; 3.0"
        ), unsafe_allow_html=True)

    with col2:
        st.markdown(_metric_card(
            icon="BR", icon_bg="#FEF2F2", icon_color="#DC2626",
            title="Burnout Risk Score", subtitle="Điểm Rủi ro Kiệt sức",
            description="Dựa trên mô hình JD-R (Job Demands-Resources). Nếu Áp lực liên tục lớn hơn Nguồn lực, nhân viên sẽ rơi vào trạng thái kiệt quệ.",
            formula="Burnout = mean(Q18, Q29) - mean(Q11, Q16)",
            formula_note="<b>Áp lực (Demands):</b> Q18 (Cường độ/An toàn LĐ), Q29 (Áp lực/Tôn trọng). <b>Nguồn lực (Resources):</b> Q11 (Hỗ trợ kịp thời), Q16 (App/Xe an toàn). Burnout &gt; 0 = Áp lực &gt; Nguồn lực.",
            questions="Q11, Q16, Q18, Q29",
            scale="0-100% (% người có Áp lực &gt; Nguồn lực)",
            classification="An toàn &le; 15% | Cần chú ý &le; 30% | Nguy hiểm &gt; 30%"
        ), unsafe_allow_html=True)

        st.markdown(_metric_card(
            icon="SR", icon_bg="#FFF7ED", icon_color="#EA580C",
            title="Stay Risk Segmentation", subtitle="Phân nhóm Rủi ro Ở lại",
            description="Phân loại nhân viên thành 3 nhóm rủi ro dựa trên điểm ý định gắn bó, giúp xác định đối tượng cần can thiệp giữ chân.",
            formula="Flight Risk: Q22 &le; 2 | At Risk: Q22 = 3 | Stable: Q22 &ge; 4",
            formula_note="Mỗi nhóm được tính % trên tổng số nhân viên hợp lệ.",
            questions="Q22",
            scale="0-100% cho mỗi nhóm",
            classification="Flight Risk: Nguy cơ rời đi cao | At Risk: Đang cân nhắc | Stable: Ổn định"
        ), unsafe_allow_html=True)

        st.markdown(_metric_card(
            icon="eN", icon_bg="#ECFDF5", icon_color="#059669",
            title="eNPS Segment Distribution", subtitle="Phân bố Đại sứ / Thụ động / Bất mãn",
            description="Phân bố chi tiết nhân viên theo 3 nhóm trung thành, giúp hiểu cấu trúc của điểm eNPS tổng thể.",
            formula="Promoter: Q31 &ge; 9 | Passive: Q31 &isin; {7, 8} | Detractor: Q31 &le; 6",
            formula_note="<b>Promoter:</b> Trung thành, nhiệt huyết. <b>Passive:</b> Hài lòng nhưng dễ bị thu hút bởi offer khác. <b>Detractor:</b> Không hài lòng, có khả năng lan truyền tiêu cực.",
            questions="Q31 (thang 0-10)",
            scale="% cho mỗi nhóm",
            classification="Promoter &gt; 50% là tốt | Detractor &gt; 30% cần báo động"
        ), unsafe_allow_html=True)


def _render_deep_analysis():
    st.markdown("### Chỉ số Phân tích Chuyên sâu")
    st.markdown("Các phương pháp thống kê và phân tích nâng cao để tìm ra nguyên nhân và ưu tiên hành động.")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(_metric_card(
            icon="&rho;", icon_bg="#DBEAFE", icon_color="#2563EB",
            title="Spearman Rank Correlation", subtitle="Hệ số Tương quan Hạng Spearman với EI",
            description="Đo lường mức độ ảnh hưởng của từng câu hỏi đến chỉ số gắn kết tổng thể (EI). Câu hỏi có tương quan cao hơn = ảnh hưởng nhiều hơn đến sự gắn kết.",
            formula="&rho; = spearmanr(Q_score, EI)",
            formula_note="Tính riêng cho từng câu hỏi Likert (Q9-Q29) so với EI. Giá trị &rho; &gt; 0 = câu hỏi đồng biến với EI (điểm cao hơn &rarr; EI cao hơn).",
            questions="Q9-Q29 (từng câu riêng biệt) so với EI",
            scale="-1.0 đến +1.0",
            classification="|&rho;| &gt; 0.5: Tương quan mạnh | 0.3-0.5: Trung bình | &lt; 0.3: Yếu"
        ), unsafe_allow_html=True)

        st.markdown(_metric_card(
            icon="RC", icon_bg="#FEF9C3", icon_color="#CA8A04",
            title="Root Cause Gap Score", subtitle="Chênh lệch Điểm: Nhóm Muốn nghỉ vs. Gắn bó",
            description="So sánh điểm trung bình từng câu hỏi giữa nhóm muốn nghỉ và nhóm gắn bó, giúp xác định nguyên nhân gốc rễ khiến nhân viên muốn rời đi.",
            formula="Gap = mean(Q | intent &ge; 4) - mean(Q | intent &le; 2)",
            formula_note="Gap lớn = câu hỏi đó là nguyên nhân chính khiến nhân viên muốn nghỉ. Top 10 gap lớn nhất được xếp hạng ưu tiên.",
            questions="Q9-Q29 (so sánh theo nhóm Q30)",
            scale="Điểm chênh lệch (Likert 1-5)",
            classification="Gap &gt; 1.0: Rất nghiêm trọng | 0.5-1.0: Đáng kể | &lt; 0.5: Nhỏ"
        ), unsafe_allow_html=True)

    with col2:
        st.markdown(_metric_card(
            icon="PM", icon_bg="#F3E8FF", icon_color="#9333EA",
            title="Impact-Effort Priority Matrix", subtitle="Ma trận Ưu tiên Hành động",
            description="Phân loại từng câu hỏi vào 4 nhóm ưu tiên dựa trên tương quan với EI (Impact) và điểm hiện tại (Effort cần thiết), giúp tập trung nguồn lực hiệu quả.",
            formula="4 góc phần tư dựa trên Median(&rho;) và Median(Score)",
            formula_note="<b>Ưu tiên cao</b> (Impact cao + Điểm thấp): Cần hành động ngay. <b>Duy trì</b> (Impact cao + Điểm cao): Giữ vững. <b>Theo dõi</b> (Impact thấp + Điểm thấp): Quan sát. <b>Không ưu tiên</b> (Impact thấp + Điểm cao): Ít quan trọng.",
            questions="Q9-Q29",
            scale="Phân loại 4 nhóm",
            classification="Ưu tiên cao | Duy trì | Theo dõi | Không ưu tiên"
        ), unsafe_allow_html=True)

        st.markdown(_metric_card(
            icon="RR", icon_bg="#F1F5F9", icon_color="#475569",
            title="Survey Response Rate", subtitle="Tỷ lệ Phản hồi Khảo sát",
            description="Tỷ lệ nhân viên tham gia khảo sát so với tổng số nhân viên, phản ánh mức độ đại diện của dữ liệu.",
            formula="Response Rate = Số người tham gia / Tổng headcount &times; 100%",
            formula_note="Dựa trên dữ liệu headcount từ HRIS so với số lượng phản hồi thực tế.",
            questions="Không áp dụng (dữ liệu HRIS)",
            scale="0-100%",
            classification="Tốt &ge; 70% | Chấp nhận &ge; 50% | Thấp &lt; 50%"
        ), unsafe_allow_html=True)

        st.markdown(_metric_card(
            icon="YoY", icon_bg="#ECFDF5", icon_color="#059669",
            title="Year-over-Year Delta", subtitle="Thay đổi Chỉ số so với Năm trước",
            description="So sánh các chỉ số chính (EI, eNPS) giữa năm hiện tại và năm trước, giúp đánh giá xu hướng cải thiện hoặc suy giảm.",
            formula="&Delta; = Giá trị 2026 - Benchmark 2025",
            formula_note="Benchmark 2025: EI = 80.2%, eNPS = +33.6, Response Rate = 75.9%. Giá trị dương = cải thiện, âm = suy giảm.",
            questions="Không áp dụng (so sánh chỉ số tổng hợp)",
            scale="Điểm phần trăm",
            classification="&Delta; &gt; 0: Cải thiện | &Delta; = 0: Duy trì | &Delta; &lt; 0: Suy giảm"
        ), unsafe_allow_html=True)


def _render_simulation():
    st.markdown("### Chỉ số Mô phỏng & Dự báo")
    st.markdown("Các công cụ mô phỏng giúp dự đoán tác động của các can thiệp và ước tính ROI.")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(_metric_card(
            icon="KPI", icon_bg="#DBEAFE", icon_color="#2563EB",
            title="KPI Impact Simulator", subtitle="Mô phỏng Tác động KPI đến eNPS",
            description="Dự báo mức tăng eNPS và số người giữ lại được khi cải thiện các trụ cột cụ thể, từ đó ước tính chi phí tiết kiệm được.",
            formula="""
            enps_increase = improvement &times; weight &times; 100<br>
            new_enps = current_enps + enps_increase<br>
            retention_gain = (enps_increase / 10) &times; 0.05<br>
            people_saved = N &times; retention_gain<br>
            money_saved = people_saved &times; cost_per_hire
            """,
            formula_note="<b>Trọng số theo nhóm:</b> Shipper: MEI 34%, Thu nhập 28%, Hỗ trợ sự cố 18%, App 12%, Văn hóa 8%. Tài xế: Điều phối 32%, An toàn 26%, Thu nhập 20%, Thiết bị 14%, Tinh thần 8%.",
            questions="Dựa trên EI, eNPS, MEI và các trụ cột",
            scale="eNPS points, số người, VND",
            classification="ROI dương = Can thiệp có lợi"
        ), unsafe_allow_html=True)

        st.markdown(_metric_card(
            icon="Mi", icon_bg="#FEF2F2", icon_color="#DC2626",
            title="Micro Risk Simulator", subtitle="Trình Giả lập Rủi ro Nghỉ việc (Cá nhân)",
            description="Ước tính xác suất nghỉ việc của một nhân viên cụ thể dựa trên các yếu tố cá nhân (thâm niên, thu nhập, MEI, v.v.).",
            formula="""
            risk = base + tenure_penalty + salary_penalty + ... - mei_shield<br>
            (clamped to [min, max])
            """,
            formula_note="<b>Shipper/Driver:</b> base(30) + tenure(0-25) + salary(0-20) + COD(0-15) - MEI(0-30), clamp [10, 95]. <b>Ops 2A/2B:</b> base(28) + tenure(0-20) + shift(0-18) + equip(0-15) - MEI(0-25), clamp [8, 95]. <b>Office 3A/3B:</b> base(22) + tenure(0-18) + workload(0-22) - recognition(0-20), clamp [5, 92].",
            questions="MEI, thâm niên, thu nhập, ca làm, thiết bị, v.v.",
            scale="0-100% (xác suất)",
            classification="Thấp &le; 20% | Trung bình &le; 50% | Cao &gt; 50%"
        ), unsafe_allow_html=True)

    with col2:
        st.markdown(_metric_card(
            icon="Ma", icon_bg="#FEF9C3", icon_color="#CA8A04",
            title="Macro Risk Simulator", subtitle="Giả lập Tác động Tổ chức (Vĩ mô)",
            description="Dự báo tỷ lệ nghỉ việc toàn tổ chức khi thay đổi các yếu tố vĩ mô như lương thưởng, năng lực quản lý, và mức phạt.",
            formula="""
            impact_salary = salary_change% &times; 0.35<br>
            impact_mei = mei_change% &times; 0.5<br>
            impact_cod = cod_reduction% &times; 0.08<br>
            new_risk = current_risk - (impact_salary + impact_mei + impact_cod)
            """,
            formula_note="Baseline là tỷ lệ muốn nghỉ hiện tại (intent_pct_low). Kết quả được clamp trong khoảng [2%, 80%].",
            questions="Dựa trên Turnover Intent (Q30), MEI, thu nhập",
            scale="0-100% (tỷ lệ nghỉ việc dự báo)",
            classification="Clamp: [2%, 80%]"
        ), unsafe_allow_html=True)

        st.markdown(_metric_card(
            icon="QF", icon_bg="#F1F5F9", icon_color="#64748B",
            title="Data Quality Flags", subtitle="Cờ Chất lượng Dữ liệu",
            description="Phát hiện các phản hồi không hợp lệ: trả lời thẳng hàng (straightline) hoặc bỏ trống quá nhiều, đảm bảo độ tin cậy của phân tích.",
            formula="""
            Straightline: SD(Q9..Q29) = 0 AND &ge; 10 câu hợp lệ<br>
            Missing: &gt; 80% câu Likert bị bỏ trống
            """,
            formula_note="Straightline = tất cả câu trả lời giống nhau (có thể trả lời ngẫu nhiên). Missing = không trả lời phần lớn câu hỏi.",
            questions="Q9-Q29 (tất cả câu Likert)",
            scale="Boolean (Có/Không)",
            classification="Straightline: Loại (2A, 2B, 3A) hoặc Giữ (1A, 1B, 3B) | Missing: Luôn loại"
        ), unsafe_allow_html=True)


def _render_nlp():
    st.markdown("### Chỉ số NLP & Phân tích Văn bản")
    st.markdown("Các chỉ số được trích xuất từ phản hồi mở (open-text) bằng kỹ thuật xử lý ngôn ngữ tự nhiên.")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(_metric_card(
            icon="NW", icon_bg="#FEF2F2", icon_color="#DC2626",
            title="NLP Warning Signals", subtitle="Tín hiệu Cảnh báo từ Phản hồi Mở",
            description="Phát hiện tự động các tín hiệu tiêu cực từ phản hồi văn bản mở, giúp nhận diện sớm các vấn đề nghiêm trọng.",
            formula="Rule-based keyword detection + AI validation",
            formula_note="<b>5 loại tín hiệu:</b> Ý định nghỉ việc (resignation intent), Kiệt sức (burnout), Bất công (injustice), Mất niềm tin (lost trust), Xung đột QL (management conflict). Sau khi phát hiện bằng keyword, AI được dùng để lọc false positive.",
            questions="Q32, Q33, Q34 (phản hồi mở)",
            scale="Số lượng tín hiệu / Tổng phản hồi",
            classification="Mỗi tín hiệu được xác thực bởi AI để giảm false positive"
        ), unsafe_allow_html=True)

        st.markdown(_metric_card(
            icon="TP", icon_bg="#EDE9FE", icon_color="#7C3AED",
            title="Topic Distribution with Sentiment", subtitle="Phân bố Chủ đề & Giọng điệu",
            description="Phân loại phản hồi mở thành các chủ đề và đánh giá giọng điệu (tích cực/trung lập/tiêu cực) cho mỗi chủ đề.",
            formula="Topic% = Số đề cập / Tổng phản hồi &times; 100",
            formula_note="Mỗi chủ đề có phân bố: positive%, neutral%, negative%. Giúp hiểu vấn đề nào được quan tâm nhiều nhất và cảm xúc đi kèm.",
            questions="Q32, Q33, Q34 (phản hồi mở)",
            scale="% cho mỗi chủ đề và giọng điệu",
            classification="Chủ đề &gt; 20% = Nổi bật | Negative &gt; 50% = Cần chú ý"
        ), unsafe_allow_html=True)

    with col2:
        st.markdown(_metric_card(
            icon="EVP", icon_bg="#DBEAFE", icon_color="#2563EB",
            title="EVP Keyword Frequency", subtitle="Từ khóa EVP Nổi bật",
            description="Đếm tần suất từ khóa trong phản hồi mở, phân nhóm theo 4 yếu tố EVP (Employer Value Proposition) để hiểu nhân viên quan tâm đến điều gì nhất.",
            formula="Word frequency &rarr; bucketed into 4 EVP factors",
            formula_note="<b>4 nhóm EVP:</b> Lương thưởng & Phụ cấp, Công việc & Môi trường, Quản lý & Hỗ trợ, Công nghệ & Quy trình. Tần suất cao = mối quan tâm lớn.",
            questions="Q32, Q33, Q34 (phản hồi mở)",
            scale="Số lần xuất hiện / Tổng phản hồi",
            classification="Top keywords trong mỗi nhóm EVP"
        ), unsafe_allow_html=True)


def _render_hris():
    st.markdown("### Chỉ số HRIS & Thu nhập")
    st.markdown("Các chỉ số kết hợp dữ liệu khảo sát với dữ liệu HRIS (nhân sự) để tìm mối tương quan sâu hơn.")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(_metric_card(
            icon="IxE", icon_bg="#DCFCE7", icon_color="#16A34A",
            title="Income x Engagement", subtitle="Tương quan Thu nhập & Gắn kết",
            description="Phân tích mức độ gắn kết (EI) và eNPS theo từng nhóm thu nhập, giúp xác định thu nhập có phải yếu tố quyết định gắn kết hay không.",
            formula="mean(EI) và eNPS theo nhóm thu nhập",
            formula_note="<b>Nhóm thu nhập:</b> &lt;5tr, 5-7tr, 7-10tr, 10-15tr, &gt;15tr. Cho phép so sánh EI và eNPS giữa các nhóm.",
            questions="EI, eNPS + dữ liệu HRIS (thu nhập)",
            scale="EI: 0-100% | eNPS: -100 đến +100",
            classification="Chênh lệch EI giữa nhóm cao nhất và thấp nhất &gt; 15% = Đáng kể"
        ), unsafe_allow_html=True)

        st.markdown(_metric_card(
            icon="PxE", icon_bg="#FEF2F2", icon_color="#DC2626",
            title="Penalty x Engagement", subtitle="Tương quan Mức phạt & Gắn kết",
            description="Phân tích tác động của mức phạt (phạt + truy thu COD) đến sự gắn kết, giúp đánh giá chính sách phạt có ảnh hưởng tiêu cực hay không.",
            formula="mean(EI) theo nhóm mức phạt",
            formula_note="<b>Nhóm phạt:</b> Không phạt, &lt;500K, 500K-1tr, 1-3tr, &gt;3tr. tong_phat = Phạt + Truy thu COD.",
            questions="EI + dữ liệu HRIS (phạt, truy thu COD)",
            scale="EI: 0-100%",
            classification="EI giảm &gt; 10% ở nhóm bị phạt nhiều = Tác động tiêu cực rõ rệt"
        ), unsafe_allow_html=True)

        st.markdown(_metric_card(
            icon="RM", icon_bg="#FEF9C3", icon_color="#CA8A04",
            title="Turnover Risk Heatmap", subtitle="Bản đồ Rủi ro: Thu nhập x Mức phạt",
            description="Heatmap 2 chiều thể hiện tỷ lệ muốn nghỉ việc theo từng kết hợp (nhóm thu nhập, nhóm phạt), giúp xác định nhóm nhân viên có rủi ro cao nhất.",
            formula="Risk% = Count(Muốn nghỉ) / Tổng trong ô &times; 100%",
            formula_note="Chỉ hiển thị các ô có N &ge; 10 để đảm bảo ý nghĩa thống kê. Kết hợp Q30 (ý định) + HRIS (thu nhập, phạt).",
            questions="Q30 + dữ liệu HRIS (thu nhập, phạt)",
            scale="0-100% cho mỗi ô",
            classification="Risk &gt; 30%: Ô nguy hiểm | 15-30%: Cần chú ý | &lt; 15%: An toàn"
        ), unsafe_allow_html=True)

    with col2:
        st.markdown(_metric_card(
            icon="CB", icon_bg="#F3E8FF", icon_color="#9333EA",
            title="Warrior Classification x Engagement", subtitle="Phân loại Chiến binh & Gắn kết",
            description="Phân tích mức độ gắn kết theo phân loại chiến binh (từ HRIS), giúp hiểu nhóm chiến binh nào đang gắn kết tốt/yếu.",
            formula="mean(EI) và mean(thu nhập) theo phân loại Chiến binh",
            formula_note="Dựa trên trường 'Phân loại Chiến binh' trong HRIS. Cho phép so sánh EI và thu nhập trung bình giữa các nhóm.",
            questions="EI + dữ liệu HRIS (Phân loại Chiến binh)",
            scale="EI: 0-100%",
            classification="So sánh EI giữa các nhóm chiến binh"
        ), unsafe_allow_html=True)

        st.markdown(_metric_card(
            icon="IS", icon_bg="#ECFDF5", icon_color="#059669",
            title="Income Structure Breakdown", subtitle="Cơ cấu Thu nhập Trung bình",
            description="Phân tích cơ cấu thu nhập trung bình theo từng thành phần, giúp hiểu tỷ trọng lương, thưởng, phụ cấp trong tổng thu nhập.",
            formula="Mean của từng thành phần thu nhập",
            formula_note="<b>Các thành phần:</b> Lương đơn hàng, Thưởng/Phạt GTC và LTC, Phụ cấp, Thưởng Doanh Thu. Hiển thị dưới dạng biểu đồ tròn %.",
            questions="Dữ liệu HRIS (cơ cấu thu nhập)",
            scale="VND và %",
            classification="Phân tích cơ cấu, không phân loại"
        ), unsafe_allow_html=True)
