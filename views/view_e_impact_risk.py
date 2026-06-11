import streamlit as st
import plotly.express as px
import pandas as pd
from shared.nlp_utils import detect_warning_signals
from utils.ai_generator import render_ai_insight_card, validate_warning_signals_with_ai

@st.fragment
def render(df, cfg, pillar_filter=None):
    codebook = cfg.get('codebook', {})
    open_cols = [q for q, info in codebook.items() if info['loại'] == 'open']

    from shared.plotly_theme import section_header
    st.markdown(section_header("Trình Giả Lập Rủi Ro Nghỉ Việc", "Thử kịch bản What-If: Thay đổi điều kiện làm việc → Rủi ro nghỉ thay đổi như thế nào?"), unsafe_allow_html=True)

    # Non-DA user explanation
    group_short = cfg.get('short', '')
    st.markdown(f"""
    <div style="background:#FFF7ED;border:1px solid #FED7AA;border-radius:12px;padding:14px 18px;margin-bottom:20px;display:flex;gap:12px;align-items:flex-start;">
        <div style="font-size:1.4rem;flex-shrink:0;"></div>
        <div>
            <div style="font-size:0.82rem;font-weight:700;color:#C2410C;margin-bottom:4px;">Công cụ mô phỏng rủi ro — Dành cho nhóm {cfg.get('label','')}</div>
            <div style="font-size:0.8rem;color:#475569;line-height:1.55;">
                Kéo các thanh trượt để <strong>thay đổi điều kiện làm việc giả định</strong> và xem ngay xác suất nghỉ việc thay đổi như thế nào.
                Đây là công cụ hữu ích để trả lời câu hỏi: <em>"Nếu tăng lương thêm X triệu, rủi ro giảm bao nhiêu %?"</em>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    sim_tab1, sim_tab2 = st.tabs(["Cấp độ Cá nhân (Micro)", "Cấp độ Tổ chức (Macro)"])

    with sim_tab1:
        sim_col1, sim_col2 = st.columns([1, 1.1])

        # ── GROUP-SPECIFIC SIMULATOR ────────────────────────────────────────
        with sim_col1:

            if group_short in ('Shipper', 'Tài xế'):
                # ── 1A / 1B: Frontline field staff ──
                st.markdown("<p style='font-weight:700;color:#0A1F44;margin-bottom:8px;margin-top:16px;'> Điều kiện làm việc nhân viên:</p>", unsafe_allow_html=True)
                sel_tenure = st.selectbox(
                    "Thâm niên hiện tại:",
                    ["Dưới 2 tháng — Giai đoạn thử thách (rủi ro cao nhất)",
                     "Từ 2–6 tháng — Giai đoạn làm quen",
                     "Từ 6 tháng – 2 năm",
                     "Trên 2 năm — Thâm niên vững vàng"]
                )
                sel_salary = st.slider(
                    "Thu nhập thực nhận tháng gần nhất (Triệu VND):",
                    min_value=5.0, max_value=15.0, value=8.0, step=0.5,
                    help="Thu nhập thấp trong tháng đầu là nguyên nhân chính khiến nhân viên mới nghỉ."
                )
                label_factor3 = "Khoản phạt & truy thu COD (Triệu VND):" if group_short == 'Shipper' else "Sự cố dọc tuyến tháng qua (lần):"
                sel_cod = st.slider(label_factor3, min_value=0.0, max_value=1.5, value=0.2, step=0.1)
                sel_mei = st.slider(
                    "Chất lượng quản lý trực tiếp (điểm 1–5):",
                    min_value=1.0, max_value=5.0, value=3.8, step=0.1,
                    help="Điểm 4.2+ là ngưỡng 'Tấm khiên' giúp giảm mạnh rủi ro nghỉ việc."
                )
                # Calculate
                base_risk = 30
                tenure_penalty = 25 if "Dưới 2 tháng" in sel_tenure else (10 if "2–6 tháng" in sel_tenure else 0)
                salary_penalty = 20 if sel_salary < 5.5 else (10 if sel_salary < 7.0 else 0)
                cod_penalty = 15 if sel_cod > 0.5 else 0
                mei_shield = 30 if sel_mei > 4.2 else (10 if sel_mei >= 3.5 else 0)
                bullets = []
                if tenure_penalty > 0:
                    bullets.append(f"<li style='color:#EF4444;margin-bottom:4px;'> <strong>Thâm niên ngắn (+{tenure_penalty}%):</strong> Chưa quen việc, thu nhập thấp hơn mức kỳ vọng trong tháng đầu.</li>")
                else:
                    bullets.append("<li style='color:#10B981;margin-bottom:4px;'> <strong>Thâm niên ổn định (+0%):</strong> Đã quen việc và có thu nhập dự đoán được.</li>")
                if salary_penalty > 0:
                    bullets.append(f"<li style='color:#EF4444;margin-bottom:4px;'> <strong>Thu nhập thấp (+{salary_penalty}%):</strong> Không đủ trang trải → mất động lực tiếp tục.</li>")
                else:
                    bullets.append("<li style='color:#10B981;margin-bottom:4px;'> <strong>Thu nhập ổn (+0%):</strong> Mức lương đủ đáp ứng nhu cầu sinh hoạt cơ bản.</li>")
                if cod_penalty > 0:
                    bullets.append(f"<li style='color:#EF4444;margin-bottom:4px;'> <strong>Phạt/Sự cố cao (+{cod_penalty}%):</strong> Tạo bức xúc tài chính và cảm giác bất công.</li>")
                else:
                    bullets.append("<li style='color:#10B981;margin-bottom:4px;'> <strong>Ít phạt/sự cố (+0%):</strong> Không bị áp lực tài chính và tâm lý không đáng có.</li>")
                if mei_shield > 0:
                    bullets.append(f"<li style='color:#10B981;margin-bottom:4px;'><strong>Quản lý tốt (−{mei_shield}%):</strong> Tấm khiên hấp thụ áp lực, giúp nhân viên vượt qua giai đoạn đầu khó khăn.</li>")
                else:
                    bullets.append("<li style='color:#EF4444;margin-bottom:4px;'> <strong>Quản lý yếu (+0%):</strong> Không có hỗ trợ → nhân viên mới dễ bỏ cuộc.</li>")
                risk_pct = max(10, min(95, base_risk + tenure_penalty + salary_penalty + cod_penalty - mei_shield))

            elif group_short in ('Kho 2A', 'BC 2B'):
                # ── 2A / 2B: Operations staff ──
                st.markdown("<p style='font-weight:700;color:#0A1F44;margin-bottom:8px;margin-top:16px;'> Điều kiện làm việc nhân viên:</p>", unsafe_allow_html=True)
                sel_tenure = st.selectbox(
                    "Thâm niên hiện tại:",
                    ["Dưới 3 tháng — Giai đoạn thử thách",
                     "Từ 3–9 tháng — Giai đoạn làm quen",
                     "Từ 9 tháng – 2 năm",
                     "Trên 2 năm — Nhân viên cốt lõi"]
                )
                ca_label = "Ca làm việc thường xuyên:" if group_short == 'Kho 2A' else "Cường độ làm việc:"
                sel_shift = st.selectbox(
                    ca_label,
                    ["Ca đêm liên tục (>3 đêm/tuần) — Rủi ro cao",
                     "Ca xoay (ngày + đêm)",
                     "Ca ngày ổn định"] if group_short == 'Kho 2A'
                    else ["Giờ cao điểm nhiều (>8h/ngày liên tục)",
                          "Tải trọng bình thường",
                          "Tải trọng thấp"]
                )
                sel_equip = st.select_slider(
                    "Thiết bị & Điều kiện làm việc:",
                    options=["Rất kém", "Kém", "Trung bình", "Tốt", "Rất tốt"],
                    value="Trung bình"
                )
                sel_career = st.select_slider(
                    "Lộ trình thăng tiến rõ ràng không?",
                    options=["Hoàn toàn mờ nhạt", "Không rõ", "Có nhưng khó", "Khá rõ", "Rất rõ ràng"],
                    value="Không rõ"
                )
                sel_mei = st.slider(
                    "Chất lượng quản lý trực tiếp (điểm 1–5):",
                    min_value=1.0, max_value=5.0, value=3.5, step=0.1
                )
                # Calculate
                base_risk = 28
                tenure_penalty  = 20 if "Dưới 3 tháng" in sel_tenure else (8 if "3–9 tháng" in sel_tenure else 0)
                shift_penalty   = 18 if "Ca đêm liên tục" in sel_shift or "nhiều" in sel_shift else (8 if "xoay" in sel_shift or "bình thường" in sel_shift else 0)
                equip_penalty   = 15 if sel_equip in ("Rất kém","Kém") else (5 if sel_equip == "Trung bình" else 0)
                career_penalty  = 12 if "mờ nhạt" in sel_career or "Không rõ" in sel_career else (5 if "khó" in sel_career else 0)
                mei_shield      = 25 if sel_mei > 4.0 else (10 if sel_mei >= 3.2 else 0)
                bullets = []
                if tenure_penalty: bullets.append(f"<li style='color:#EF4444;margin-bottom:4px;'> <strong>Thâm niên ngắn (+{tenure_penalty}%):</strong> Chưa thích nghi môi trường, dễ rời bỏ khi gặp khó khăn đầu tiên.</li>")
                else: bullets.append("<li style='color:#10B981;margin-bottom:4px;'> <strong>Nhân viên có kinh nghiệm (+0%):</strong> Đã quen việc và có sự gắn bó nhất định.</li>")
                if shift_penalty: bullets.append(f"<li style='color:#EF4444;margin-bottom:4px;'> <strong>Ca làm việc nặng (+{shift_penalty}%):</strong> Kiệt sức thể chất và ảnh hưởng cuộc sống cá nhân là nguyên nhân chính bỏ việc.</li>")
                else: bullets.append("<li style='color:#10B981;margin-bottom:4px;'> <strong>Ca kíp hợp lý (+0%):</strong> Cân bằng được công việc và cuộc sống.</li>")
                if equip_penalty: bullets.append(f"<li style='color:#EF4444;margin-bottom:4px;'> <strong>Thiết bị kém (+{equip_penalty}%):</strong> Làm việc khó khăn → năng suất thấp → thu nhập thấp → bực bội.</li>")
                else: bullets.append("<li style='color:#10B981;margin-bottom:4px;'> <strong>Thiết bị đủ dùng (+0%):</strong> Không bị cản trở bởi điều kiện vật chất.</li>")
                if career_penalty: bullets.append(f"<li style='color:#EF4444;margin-bottom:4px;'> <strong>Thăng tiến mờ nhạt (+{career_penalty}%):</strong> Không thấy tương lai → âm thầm tìm việc khác.</li>")
                else: bullets.append("<li style='color:#10B981;margin-bottom:4px;'> <strong>Lộ trình rõ ràng (+0%):</strong> Có động lực phấn đấu và gắn bó dài hạn.</li>")
                if mei_shield: bullets.append(f"<li style='color:#10B981;margin-bottom:4px;'><strong>Quản lý tốt (−{mei_shield}%):</strong> Hỗ trợ kịp thời và tạo môi trường làm việc tích cực.</li>")
                else: bullets.append("<li style='color:#EF4444;margin-bottom:4px;'> <strong>Quản lý thiếu sót (+0%):</strong> Nhân viên thiếu định hướng và dễ cảm thấy bị bỏ mặc.</li>")
                risk_pct = max(8, min(95, base_risk + tenure_penalty + shift_penalty + equip_penalty + career_penalty - mei_shield))

            else:
                # ── 3A / 3B: Office & Management staff ──
                st.markdown("<p style='font-weight:700;color:#0A1F44;margin-bottom:8px;margin-top:16px;'> Điều kiện làm việc nhân viên:</p>", unsafe_allow_html=True)
                sel_tenure = st.selectbox(
                    "Thâm niên hiện tại:",
                    ["Dưới 6 tháng — Giai đoạn hòa nhập",
                     "Từ 6 tháng – 1 năm",
                     "Từ 1–3 năm",
                     "Trên 3 năm — Nhân sự cốt lõi"]
                )
                sel_workload = st.select_slider(
                    "Khối lượng công việc hiện tại:",
                    options=["Quá tải nghiêm trọng", "Khá nhiều", "Vừa phải", "Ổn định"],
                    value="Khá nhiều"
                )
                sel_strategy = st.select_slider(
                    "Mức độ rõ ràng của chiến lược & định hướng từ lãnh đạo:",
                    options=["Rất mơ hồ", "Không rõ", "Tương đối rõ", "Rất rõ ràng"],
                    value="Không rõ"
                )
                sel_career = st.select_slider(
                    "Cơ hội phát triển & thăng tiến:",
                    options=["Không có", "Rất ít", "Có nhưng khó tiếp cận", "Tốt"],
                    value="Rất ít"
                )
                sel_recognition = st.select_slider(
                    "Mức độ ghi nhận đóng góp từ cấp trên:",
                    options=["Gần như không có", "Hiếm khi", "Đôi khi", "Thường xuyên"],
                    value="Hiếm khi"
                )
                # Calculate
                base_risk = 22
                tenure_penalty  = 18 if "Dưới 6 tháng" in sel_tenure else (8 if "6 tháng" in sel_tenure else 0)
                wl_penalty      = 22 if "nghiêm trọng" in sel_workload else (10 if "Khá nhiều" in sel_workload else 0)
                strategy_penalty= 18 if "Rất mơ hồ" in sel_strategy else (10 if "Không rõ" in sel_strategy else 0)
                career_penalty  = 12 if "Không có" in sel_career else (8 if "Rất ít" in sel_career else 0)
                recog_shield    = 20 if "Thường xuyên" in sel_recognition else (8 if "Đôi khi" in sel_recognition else 0)
                bullets = []
                if tenure_penalty: bullets.append(f"<li style='color:#EF4444;margin-bottom:4px;'> <strong>Mới vào (+{tenure_penalty}%):</strong> Kỳ vọng chưa được đáp ứng, văn hóa chưa thích nghi.</li>")
                else: bullets.append("<li style='color:#10B981;margin-bottom:4px;'> <strong>Đã ổn định (+0%):</strong> Hiểu rõ công ty và tìm được lý do để ở lại.</li>")
                if wl_penalty: bullets.append(f"<li style='color:#EF4444;margin-bottom:4px;'> <strong>Quá tải (+{wl_penalty}%):</strong> Làm việc quá nhiều mà không thấy kết quả tương xứng → kiệt sức.</li>")
                else: bullets.append("<li style='color:#10B981;margin-bottom:4px;'> <strong>Khối lượng vừa phải (+0%):</strong> Có thể làm tốt và vẫn còn năng lượng.</li>")
                if strategy_penalty: bullets.append(f"<li style='color:#EF4444;margin-bottom:4px;'> <strong>Chiến lược mơ hồ (+{strategy_penalty}%):</strong> Không biết mình đang làm vì mục tiêu gì → mất ý nghĩa công việc.</li>")
                else: bullets.append("<li style='color:#10B981;margin-bottom:4px;'> <strong>Định hướng rõ ràng (+0%):</strong> Hiểu vai trò của mình trong bức tranh lớn.</li>")
                if career_penalty: bullets.append(f"<li style='color:#EF4444;margin-bottom:4px;'> <strong>Ít cơ hội phát triển (+{career_penalty}%):</strong> Cảm thấy bị tran thuy tinh → tìm nơi khác có nhiều cơ hội hơn.</li>")
                else: bullets.append("<li style='color:#10B981;margin-bottom:4px;'> <strong>Có cơ hội phát triển (+0%):</strong> Thấy tương lai rõ ràng và có động lực phấn đấu.</li>")
                if recog_shield: bullets.append(f"<li style='color:#10B981;margin-bottom:4px;'><strong>Được ghi nhận (−{recog_shield}%):</strong> Cảm thấy công sức được trân trọng → tiếp tục cống hiến.</li>")
                else: bullets.append("<li style='color:#EF4444;margin-bottom:4px;'> <strong>Thiếu ghi nhận (+0%):</strong> Lam nhieu ma khong ai biet → dần mất động lực.</li>")
                risk_pct = max(5, min(92, base_risk + tenure_penalty + wl_penalty + strategy_penalty + career_penalty - recog_shield))

        with sim_col2:
            st.write("") # Alignment spacer
            risk_color = "rgba(16, 185, 129, 0.08)"
            border_color = "rgba(16, 185, 129, 0.3)"
            text_color = "#10B981"
            risk_label = "AN TOÀN (Nguy cơ thấp)"
            
            if risk_pct > 60:
                risk_color = "rgba(239, 68, 68, 0.08)"
                border_color = "rgba(239, 68, 68, 0.3)"
                text_color = "#EF4444"
                risk_label = "NGUY HIỂM (Nguy cơ rất cao)"
            elif risk_pct >= 25:
                risk_color = "rgba(245, 158, 11, 0.08)"
                border_color = "rgba(245, 158, 11, 0.3)"
                text_color = "#F59E0B"
                risk_label = "CẢNH BÁO (Trung bình)"

            st.markdown(f"""
            <div class="sim-gauge-container" style="background: {risk_color}; border: 1px solid {border_color}; margin-top: 15px;">
                <p style="margin: 0; font-size: 0.82rem; color: {text_color}; font-weight: 800; letter-spacing: 0.08em; text-transform: uppercase;">
                    XÁC SUẤT NGHỈ VIỆC DỰ BÁO
                </p>
                <p class="sim-risk-value" style="color: {text_color}; margin: 15px 0;">{risk_pct:.0f}%</p>
                <div style="font-weight: 800; font-size: 1.15rem; color: {text_color}; margin-top: -5px; margin-bottom: 15px;">
                    {risk_label}
                </div>
                <div class="sim-risk-meter">
                    <div class="sim-risk-bar" style="width: {risk_pct}%; background-color: {text_color};"></div>
                </div>
                <div style="text-align: left; margin-top: 20px; background: rgba(255, 255, 255, 0.75); padding: 16px 20px; border-radius: 16px; border: 1px solid rgba(0,0,0,0.04);">
                    <strong style="font-size: 0.88rem; color: #0A1F44; display: block; margin-bottom: 6px;"> Đóng góp nhân tố SHAP (Tác động thực tế):</strong>
                    <ul style="font-size: 0.82rem; color: #475569; margin: 0; padding-left: 16px; line-height: 1.6;">
                        {"".join(bullets)}
                    </ul>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
    with sim_tab2:
        st.markdown("""
        <div style="background:#F0F9FF;border:1px solid #BAE6FD;border-radius:10px;padding:12px 16px;margin:12px 0 16px;">
            <strong style="color:#0369A1;font-size:0.82rem;"> Cấp độ Tổ chức:</strong>
            <span style="font-size:0.8rem;color:#475569;"> Giả lập tác động của quyết sách nhân sự lên <strong>toàn bộ nhóm</strong> — không phải 1 người mà là tất cả mọi người cùng lúc.</span>
        </div>
        """, unsafe_allow_html=True)
        m_col1, m_col2 = st.columns([1, 1.1])
        with m_col1:
            st.markdown("<p style='font-weight: 700; color: #0A1F44; margin-bottom: 8px;'> Kịch bản điều chỉnh (So với hiện tại):</p>", unsafe_allow_html=True)
            macro_salary = st.slider("Tăng quỹ lương / thu nhập trung bình (%)", -10, 20, 0, step=1, key='macro_sal',
                                     help="10% = tăng lương trung bình 10% cho toàn nhóm")
            macro_mei    = st.slider("Cải thiện chất lượng Quản lý MEI (%)", 0, 20, 0, step=1, key='macro_mei',
                                     help="Đầu tư đào tạo quản lý → điểm MEI tăng lên")
            macro_cod    = st.slider(" Giảm áp lực phạt / sự cố / xung đột (%)", 0, 50, 0, step=5, key='macro_cod',
                                     help="Cải thiện quy trình, giảm lỗi hệ thống → nhân viên ít bị ảnh hưởng tiêu cực hơn")
        
        with m_col2:
            # Baseline is current actual risk
            from utils.data_loader import compute_kpis
            current_kpi = compute_kpis(df)
            current_risk = current_kpi.get('intent_pct_low', 25.0)
            
            # Linear heuristic impact model
            impact_salary = macro_salary * 0.35  # 10% salary increase drops risk by 3.5%
            impact_mei = macro_mei * 0.5         # 10% MEI increase drops risk by 5%
            impact_cod = macro_cod * 0.08        # 10% COD reduction drops risk by 0.8%
            
            total_reduction = impact_salary + impact_mei + impact_cod
            new_risk = max(2.0, min(80.0, current_risk - total_reduction))
            delta_risk = new_risk - current_risk
            
            from shared.plotly_theme import make_html_kpi
            delta_str = f"{delta_risk:+.1f}%" if delta_risk != 0 else "0.0%"
            color_theme = "green" if delta_risk < 0 else ("red" if delta_risk > 0 else "blue")
            
            st.markdown(make_html_kpi(
                "Tỷ lệ Rủi ro nghỉ việc dự phóng", 
                f"{new_risk:.1f}%", 
                delta=delta_str, 
                color=color_theme, 
                icon="", 
                progress_val=new_risk
            ), unsafe_allow_html=True)
            
            # Impact breakdown
            st.markdown(f"""
            <div style="margin-top: 16px; background: rgba(255, 255, 255, 0.75); padding: 16px; border-radius: 12px; border: 1px solid #E2E8F0; font-size: 0.85rem;">
                <strong style="color:#0A1F44;">Chi tiết tác động:</strong><br>
                <span style="color:#64748B;">Lương:</span> <span style="color:{'#10B981' if impact_salary>0 else '#EF4444'};">{-impact_salary:+.1f}%</span> |
                <span style="color:#64748B;">MEI:</span> <span style="color:#10B981;">{-impact_mei:+.1f}%</span> |
                <span style="color:#64748B;">Phạt:</span> <span style="color:#10B981;">{-impact_cod:+.1f}%</span>
            </div>
            """, unsafe_allow_html=True)
        
    st.write("")
    st.divider()
    st.write("")

    st.markdown(section_header("Phân Phối Tín Hiệu & Phản Hồi Mở (NLP)", "Phát hiện tín hiệu tiêu cực từ câu hỏi mở qua phân tích ngôn ngữ tự nhiên"), unsafe_allow_html=True)

    SIGNAL_LABELS = {
        'ý_định_nghỉ': 'Ý định nghỉ',
        'kiệt_sức': 'Kiệt sức',
        'bất_công': 'Bất công',
        'mất_niềm_tin': 'Mất niềm tin',
        'xung_đột_ql': 'Xung đột Quản lý'
    }

    all_signals = []
    for q in open_cols:
        cc = f'{q}_clean'
        if cc not in df.columns: continue
        for idx, text in df[cc].items():
            if text:
                for signal_type, phrase in detect_warning_signals(text):
                    # Trích xuất ngữ cảnh xung quanh cụm từ
                    text_lower = text.lower()
                    phrase_pos = text_lower.find(phrase.lower())
                    if phrase_pos >= 0:
                        ctx_start = max(0, phrase_pos - 30)
                        ctx_end = min(len(text), phrase_pos + len(phrase) + 30)
                        context_snippet = ('...' if ctx_start > 0 else '') + text[ctx_start:ctx_end] + ('...' if ctx_end < len(text) else '')
                    else:
                        context_snippet = text[:80]
                    
                    all_signals.append({
                        'Câu': q, 'Loại': SIGNAL_LABELS.get(signal_type, signal_type),
                        'Cụm từ': phrase,
                        'Ngữ cảnh': context_snippet,
                        'Section': df.loc[idx, 'section'] if 'section' in df.columns else '',
                        'eNPS': df.loc[idx, 'eNPS_group'] if 'eNPS_group' in df.columns else '',
                        'Phản hồi': text[:150],
                    })

    if not all_signals:
        st.info("Không phát hiện tín hiệu cảnh báo đáng lo ngại.")
        return

    # ── AI VALIDATION: Gọi LLM xác nhận lại từng tín hiệu ──
    n_before_ai = len(all_signals)
    
    # Chuẩn bị batch cho AI
    ai_batch = []
    for i, s in enumerate(all_signals):
        ai_batch.append({
            'index': i,
            'signal_type': s['Loại'],
            'phrase': s['Cụm từ'],
            'full_text': s['Phản hồi'],
        })
    
    # Gọi AI validator (batch 20 items mỗi lần)
    ai_results = {}
    with st.spinner(' AI đang xác nhận tín hiệu cảnh báo...'):
        for batch_start in range(0, len(ai_batch), 20):
            batch = ai_batch[batch_start:batch_start + 20]
            batch_result = validate_warning_signals_with_ai(batch)
            ai_results.update(batch_result)
    
    # Gắn kết quả AI vào từng signal
    for i, s in enumerate(all_signals):
        ai_r = ai_results.get(i, {'valid': True, 'reason': ''})
        s['AI_valid'] = ai_r['valid']
        s['AI_reason'] = ai_r['reason']
    
    # Lọc bỏ false positives
    confirmed_signals = [s for s in all_signals if s['AI_valid']]
    rejected_signals = [s for s in all_signals if not s['AI_valid']]
    n_after_ai = len(confirmed_signals)
    
    if not confirmed_signals:
        st.success(f" AI đã phân tích {n_before_ai} tín hiệu ban đầu và xác nhận tất cả đều **không đáng lo ngại** (false positive). Không có cảnh báo thực sự.")
        if rejected_signals:
            with st.expander(f" Xem {len(rejected_signals)} tín hiệu đã bị AI loại bỏ"):
                df_rej = pd.DataFrame(rejected_signals)[['Loại', 'Cụm từ', 'AI_reason', 'Phản hồi']]
                df_rej.columns = ['Loại', 'Cụm từ', 'Lý do loại bỏ', 'Phản hồi']
                st.dataframe(df_rej, width='stretch', hide_index=True)
        return
    
    df_sig = pd.DataFrame(confirmed_signals)
    
    from shared.plotly_theme import make_html_kpi, fig_card
    
    # KPI row
    kpi_c1, kpi_c2, kpi_c3 = st.columns(3)
    with kpi_c1:
        st.markdown(make_html_kpi("Tín hiệu đã xác nhận", f"{n_after_ai:,}", color="red", icon=""), unsafe_allow_html=True)
    with kpi_c2:
        st.markdown(make_html_kpi("False positive đã lọc", f"{n_before_ai - n_after_ai:,}", color="green", icon=""), unsafe_allow_html=True)
    with kpi_c3:
        accuracy_pct = (n_after_ai / n_before_ai * 100) if n_before_ai > 0 else 0
        st.markdown(make_html_kpi("Tỷ lệ cảnh báo thật", f"{accuracy_pct:.0f}%", color="blue", icon=""), unsafe_allow_html=True)

    sig_sum = df_sig['Loại'].value_counts()
    top_signal = sig_sum.index[0] if len(sig_sum) > 0 else "N/A"
    
    sig_sec = df_sig.groupby('Section')['Loại'].count().sort_values(ascending=False).head(10)
    top_section = sig_sec.index[0] if len(sig_sec) > 0 else "N/A"

    ai_data = {
        "Total_Warning_Signals": len(df_sig),
        "Top_Negative_Signal": top_signal,
        "Most_Affected_Section": top_section
    }
    prompt = (
        f"DỰA VÀO DỮ LIỆU THỰC TẾ SAU (KHÔNG bịa thêm):\n"
        f"- Tổng tín hiệu cảnh báo đã xác nhận: {ai_data['Total_Warning_Signals']}\n"
        f"- Tín hiệu nổi cộm nhất: {ai_data['Top_Negative_Signal']}\n"
        f"- Bộ phận bị ảnh hưởng nặng nhất: {ai_data['Most_Affected_Section']}\n\n"
        f"Đánh giá vấn đề và yêu cầu can thiệp từ HRBP. "
        f"CHỈ dùng 3 dữ kiện đã liệt kê."
    )
    render_ai_insight_card("AI NLP Insight", ai_data, prompt, custom_style="margin-top: 24px; margin-bottom: 24px;")

    c1, c2 = st.columns(2)
    with c1:
        fig1 = px.bar(x=sig_sum.index, y=sig_sum.values, color=sig_sum.values,
                     color_continuous_scale='OrRd', text=sig_sum.values)
        fig1 = fig_card(fig1, 'PHÂN LOẠI TÍN HIỆU', 'Nhóm rủi ro phát hiện qua NLP')
        fig1.update_traces(textposition='outside')
        fig1.update_layout(height=400, showlegend=False, xaxis_title="", yaxis_title="")
        st.plotly_chart(fig1, width='stretch', key="view_e_impact_risk_chart_401")
    with c2:
        fig2 = px.bar(x=sig_sec.values, y=sig_sec.index, orientation='h',
                     color=sig_sec.values, color_continuous_scale='OrRd', text=sig_sec.values)
        fig2 = fig_card(fig2, 'TOP 10 SECTION RỦI RO', 'Số lượng tín hiệu báo động theo bộ phận')
        fig2.update_traces(textposition='outside')
        fig2.update_layout(height=400, showlegend=False, xaxis_title="", yaxis_title="")
        st.plotly_chart(fig2, width='stretch', key="view_e_impact_risk_chart_408")

    st.markdown("#### Bảng Chi tiết")
    type_filter = st.multiselect("Lọc loại tín hiệu", df_sig['Loại'].unique(), default=list(df_sig['Loại'].unique()))
    df_warn_disp = df_sig[df_sig['Loại'].isin(type_filter)][['Loại', 'Section', 'eNPS', 'Cụm từ', 'Ngữ cảnh', 'Phản hồi']]
    
    col_config = {
        'Loại': st.column_config.TextColumn('Tín hiệu cảnh báo', width="medium"),
        'Section': st.column_config.TextColumn('Section / Bộ phận', width="medium"),
        'eNPS': st.column_config.TextColumn('Nhóm eNPS', width="small"),
        'Cụm từ': st.column_config.TextColumn('Cụm từ nhạy cảm', width="small"),
        'Ngữ cảnh': st.column_config.TextColumn('Ngữ cảnh', width="large", help="Đoạn văn bản xung quanh cụm từ nhạy cảm"),
        'Phản hồi': st.column_config.TextColumn('Nội dung phản hồi', width="large"),
    }
    
    st.dataframe(df_warn_disp, width='stretch', height=400, hide_index=True, column_config=col_config)
    
    # Hiển thị các tín hiệu bị AI loại bỏ
    if rejected_signals:
        with st.expander(f" Xem {len(rejected_signals)} tín hiệu đã bị AI loại bỏ (false positives)"):
            st.markdown("""
            <div style="background:#F0FDF4;border:1px solid #BBF7D0;border-radius:8px;padding:10px 14px;margin-bottom:12px;font-size:0.8rem;color:#166534;">
                <strong> Giải thích:</strong> Các tín hiệu dưới đây được hệ thống rule-based phát hiện, nhưng AI xác nhận rằng ngữ cảnh thực tế 
                <strong>không mang tính tiêu cực</strong> (VD: "vui vẻ bớt áp lực", "làm nhiều thu nhập cao"). Chúng đã được lọc bỏ để báo cáo chính xác hơn.
            </div>
            """, unsafe_allow_html=True)
            df_rej = pd.DataFrame(rejected_signals)
            df_rej_disp = df_rej[['Loại', 'Cụm từ', 'AI_reason', 'Ngữ cảnh', 'Phản hồi']]
            df_rej_disp.columns = ['Loại ban đầu', 'Cụm từ', 'Lý do AI loại bỏ', 'Ngữ cảnh', 'Phản hồi gốc']
            
            rej_col_config = {
                'Loại ban đầu': st.column_config.TextColumn('Loại ban đầu', width="small"),
                'Cụm từ': st.column_config.TextColumn('Cụm từ', width="small"),
                'Lý do AI loại bỏ': st.column_config.TextColumn('Lý do AI loại bỏ', width="large"),
                'Ngữ cảnh': st.column_config.TextColumn('Ngữ cảnh', width="large"),
                'Phản hồi gốc': st.column_config.TextColumn('Phản hồi', width="large"),
            }
            st.dataframe(df_rej_disp, width='stretch', hide_index=True, column_config=rej_col_config)
