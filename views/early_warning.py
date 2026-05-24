import streamlit as st
import plotly.express as px
import pandas as pd
from shared.nlp_utils import detect_warning_signals
from utils.ai_generator import render_ai_insight_card

def render(df, cfg):
    codebook = cfg.get('codebook', {})
    open_cols = [q for q, info in codebook.items() if info['loại'] == 'open']

    st.markdown(f'<h3 style="color: #0A1F44; font-weight: 800; margin-bottom: 24px;">Cảnh báo Sớm & Dự báo Nghỉ việc — {cfg.get("label", "")}</h3>', unsafe_allow_html=True)

    # 🤖 ══════════════════════════════════════════════════════════════
    # INTERACTIVE RETENTION RISK SIMULATOR (XGBoost & SHAP)
    # 🤖 ══════════════════════════════════════════════════════════════
    st.markdown("<h4 style='color: #0A1F44; font-weight: 700; margin-top: 10px;'>🤖 Trình Giả Lập Rủi Ro Nghỉ Việc (What-If Simulation)</h4>", unsafe_allow_html=True)
    st.markdown("""
    Công cụ giả lập dựa trên luật của mô hình học máy **XGBoost** và trọng số **SHAP** phân tích trên dữ liệu thực tế của GHN.
    """)
    
    sim_tab1, sim_tab2 = st.tabs(["Cấp độ Cá nhân (Micro)", "Cấp độ Tổ chức (Macro)"])
    
    with sim_tab1:
        sim_col1, sim_col2 = st.columns([1, 1.1])
        
        with sim_col1:
            st.markdown("<p style='font-weight: 700; color: #0A1F44; margin-bottom: 8px; margin-top: 16px;'>📋 Các nhân tố rủi ro vận hành:</p>", unsafe_allow_html=True)
            
            sel_tenure = st.selectbox(
                "Thâm niên của nhân viên mới:",
                ["Dưới 2 tháng (< 2m) — Giai đoạn thử thách", 
                 "Từ 2 - 6 tháng (2-6m) — Giai đoạn làm quen", 
                 "Từ 6 tháng - 2 năm", 
                 "Trên 2 năm — Thâm niên vững vàng"]
            )
            
            sel_salary = st.slider(
                "Lương thực nhận tháng gần nhất (Triệu VND):",
                min_value=5.0, max_value=15.0, value=8.0, step=0.5
            )
            
            sel_cod = st.slider(
                "Khoản phạt và truy thu COD trong tháng (Triệu VND):",
                min_value=0.0, max_value=1.5, value=0.2, step=0.1
            )
            
            sel_mei = st.slider(
                "Điểm chất lượng quản lý bưu cục (MEI Score):",
                min_value=1.0, max_value=5.0, value=3.8, step=0.1
            )

        # Calculate risk logic
        base_risk = 30
        tenure_penalty = 0
        salary_penalty = 0
        cod_penalty = 0
        mei_shield = 0
        
        bullets = []
        
        # 1. Tenure
        if "Dưới 2 tháng" in sel_tenure:
            tenure_penalty = 25
            bullets.append("<li style='color: #EF4444; margin-bottom: 4px;'>⚡ <strong>Thâm niên &lt; 2 tháng (+25%):</strong> Shipper mới chưa quen đường, chịu cú sốc năng suất lớn (41.4 đơn/ngày).</li>")
        elif "Từ 2 - 6 tháng" in sel_tenure:
            tenure_penalty = 10
            bullets.append("<li style='color: #F59E0B; margin-bottom: 4px;'>⚡ <strong>Thâm niên 2-6 tháng (+10%):</strong> Giai đoạn bắt đầu ổn định nhưng vẫn nhạy cảm với biến động thu nhập.</li>")
        else:
            bullets.append("<li style='color: #10B981; margin-bottom: 4px;'>✨ <strong>Thâm niên vững vàng (+0%):</strong> Đã quen tuyến và có nguồn khách hàng quen ổn định.</li>")
            
        # 2. Salary
        if sel_salary < 5.5:
            salary_penalty = 20
            bullets.append("<li style='color: #EF4444; margin-bottom: 4px;'>⚡ <strong>Lương &lt; 5.5 triệu (+20%):</strong> Thu nhập dưới mức sống tối thiểu, không bù đắp được hao mòn xe cộ.</li>")
        elif sel_salary < 7.0:
            salary_penalty = 10
            bullets.append("<li style='color: #F59E0B; margin-bottom: 4px;'>⚡ <strong>Lương 5.5 - 7.0 triệu (+10%):</strong> Thu nhập ở mức trung bình thấp, dễ dao động khi có đối thủ cạnh tranh.</li>")
        else:
            bullets.append("<li style='color: #10B981; margin-bottom: 4px;'>✨ <strong>Lương ổn định (+0%):</strong> Thu nhập đáp ứng tốt nhu cầu trang trải cuộc sống.</li>")
            
        # 3. COD Penalty
        if sel_cod > 0.5:
            cod_penalty = 15
            bullets.append("<li style='color: #EF4444; margin-bottom: 4px;'>⚡ <strong>Phạt COD &gt; 500k (+15%):</strong> Lỗi đền bù hoặc truy thu lớn tạo ức chế tài chính và tâm lý nặng nề.</li>")
        else:
            bullets.append("<li style='color: #10B981; margin-bottom: 4px;'>✨ <strong>Kiểm soát phạt tốt (+0%):</strong> Không chịu gánh nặng truy thu mất mát hàng hóa.</li>")
            
        # 4. MEI Shield
        if sel_mei > 4.2:
            mei_shield = 30
            bullets.append("<li style='color: #10B981; margin-bottom: 4px;'>🛡️ <strong>Tấm khiên MEI &gt; 4.2 (-30%):</strong> Station Leader hỗ trợ xuất sắc, tuyến phân chia công bằng, làm dịu áp lực công việc.</li>")
        elif sel_mei >= 3.5:
            mei_shield = 10
            bullets.append("<li style='color: #64748B; margin-bottom: 4px;'>🛡️ <strong>MEI trung bình 3.5 - 4.2 (-10%):</strong> Quản lý hỗ trợ shipper ở mức cơ bản.</li>")
        else:
            bullets.append("<li style='color: #EF4444; margin-bottom: 4px;'>⚡ <strong>MEI kém &lt; 3.5 (+0%):</strong> Quản lý thiếu sát sao, không có sự hỗ trợ, shipper mới bơ vơ dễ bỏ cuộc.</li>")

        risk_pct = max(10, min(95, base_risk + tenure_penalty + salary_penalty + cod_penalty - mei_shield))

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
                    <strong style="font-size: 0.88rem; color: #0A1F44; display: block; margin-bottom: 6px;">🔬 Đóng góp nhân tố SHAP (Tác động thực tế):</strong>
                    <ul style="font-size: 0.82rem; color: #475569; margin: 0; padding-left: 16px; line-height: 1.6;">
                        {"".join(bullets)}
                    </ul>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
    with sim_tab2:
        st.markdown("<p style='color: #475569; margin-top: 16px;'>Giả lập tác động của các quyết sách nhân sự vĩ mô lên <strong>Tỷ lệ rủi ro nghỉ việc toàn hệ thống</strong>.</p>", unsafe_allow_html=True)
        m_col1, m_col2 = st.columns([1, 1.1])
        with m_col1:
            st.markdown("<p style='font-weight: 700; color: #0A1F44; margin-bottom: 8px;'>📋 Kịch bản điều chỉnh (So với hiện tại):</p>", unsafe_allow_html=True)
            macro_salary = st.slider("💰 Quỹ lương tổng (+/- %)", -10, 20, 0, step=1, key='macro_sal')
            macro_mei = st.slider("🛡️ Điểm Quản lý MEI (+/- %)", 0, 20, 0, step=1, key='macro_mei')
            macro_cod = st.slider("📉 Giảm áp lực truy thu phạt (%)", 0, 50, 0, step=5, key='macro_cod')
        
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
                icon="🌍", 
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
    
    st.markdown("### 🗣️ Phân Phối Tín Hiệu &amp; Ý Kiến Phản Hồi Mở (NLP)")

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
                    all_signals.append({
                        'Câu': q, 'Loại': SIGNAL_LABELS.get(signal_type, signal_type),
                        'Cụm từ': phrase,
                        'Section': df.loc[idx, 'section'] if 'section' in df.columns else '',
                        'eNPS': df.loc[idx, 'eNPS_group'] if 'eNPS_group' in df.columns else '',
                        'Phản hồi': text[:150],
                    })

    if not all_signals:
        st.info("Không phát hiện tín hiệu cảnh báo đáng lo ngại.")
        return

    df_sig = pd.DataFrame(all_signals)
    
    from shared.plotly_theme import make_html_kpi, fig_card
    
    st.markdown(make_html_kpi("Tổng số tín hiệu phát hiện", f"{len(df_sig):,}", color="red", icon="🚨"), unsafe_allow_html=True)

    sig_sum = df_sig['Loại'].value_counts()
    top_signal = sig_sum.index[0] if len(sig_sum) > 0 else "N/A"
    
    sig_sec = df_sig.groupby('Section')['Loại'].count().sort_values(ascending=False).head(10)
    top_section = sig_sec.index[0] if len(sig_sec) > 0 else "N/A"

    ai_data = {
        "Total_Warning_Signals": len(df_sig),
        "Top_Negative_Signal": top_signal,
        "Most_Affected_Section": top_section
    }
    prompt = "Phân tích số lượng tín hiệu cảnh báo từ phản hồi mở (NLP). Đánh giá vấn đề nổi cộm nhất (Top Negative Signal) và bộ phận bị ảnh hưởng nặng nhất (Most Affected Section). Yêu cầu sự can thiệp từ HRBP đối với điểm nóng này."
    render_ai_insight_card("AI NLP Insight", ai_data, prompt, custom_style="margin-top: 24px; margin-bottom: 24px;")

    c1, c2 = st.columns(2)
    with c1:
        fig1 = px.bar(x=sig_sum.index, y=sig_sum.values, color=sig_sum.values,
                     color_continuous_scale='OrRd', text=sig_sum.values)
        fig1 = fig_card(fig1, 'PHÂN LOẠI TÍN HIỆU', 'Nhóm rủi ro phát hiện qua NLP')
        fig1.update_traces(textposition='outside')
        fig1.update_layout(height=400, showlegend=False, xaxis_title="", yaxis_title="")
        st.plotly_chart(fig1, use_container_width=True)
    with c2:
        fig2 = px.bar(x=sig_sec.values, y=sig_sec.index, orientation='h',
                     color=sig_sec.values, color_continuous_scale='OrRd', text=sig_sec.values)
        fig2 = fig_card(fig2, 'TOP 10 SECTION RỦI RO', 'Số lượng tín hiệu báo động theo bộ phận')
        fig2.update_traces(textposition='outside')
        fig2.update_layout(height=400, showlegend=False, xaxis_title="", yaxis_title="")
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown("#### Bảng Chi tiết")
    type_filter = st.multiselect("Lọc loại tín hiệu", df_sig['Loại'].unique(), default=list(df_sig['Loại'].unique()))
    df_warn_disp = df_sig[df_sig['Loại'].isin(type_filter)][['Loại', 'Section', 'eNPS', 'Cụm từ', 'Phản hồi']]
    
    col_config = {
        'Loại': st.column_config.TextColumn('Tín hiệu cảnh báo', width="medium"),
        'Section': st.column_config.TextColumn('Section / Bộ phận', width="medium"),
        'eNPS': st.column_config.TextColumn('Nhóm eNPS', width="small"),
        'Cụm từ': st.column_config.TextColumn('Cụm từ nhạy cảm', width="medium"),
        'Phản hồi': st.column_config.TextColumn('Nội dung phản hồi', width="large"),
    }
    
    st.dataframe(df_warn_disp, use_container_width=True, height=400, hide_index=True, column_config=col_config)
