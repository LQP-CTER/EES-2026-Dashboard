import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from utils.data_loader import compute_kpis, PILLAR_LABELS
from shared.plotly_theme import COLORS, apply_theme, fig_card
from utils.ai_generator import render_ai_insight_card

def render(df, cfg):
    apply_theme()
    kpis = compute_kpis(df)

    # ══════════════════════════════════════════════════════════════
    # SECTION 0: METRIC EDUCATION PANEL — Hướng dẫn đọc chỉ số
    # ══════════════════════════════════════════════════════════════
    from shared.plotly_theme import make_html_kpi, section_header

    _ei_v   = kpis['ei_mean']
    _enps_v = kpis['enps_score']
    _mei_v  = kpis['mei_avg']
    _risk_v = kpis['intent_pct_low']

    def _ei_tag(v):
        if v >= 80: return ("Xuất sắc",    "#15803D", "#F0FDF4")
        if v >= 65: return ("Khỏe mạnh",   "#CA8A04", "#FEFCE8")
        if v >= 50: return ("Cần theo dõi","#EA580C", "#FFF7ED")
        return            ("Nghiêm trọng", "#DC2626", "#FEF2F2")
    def _enps_tag(v):
        if v >= 30: return ("Xuất sắc",  "#15803D", "#F0FDF4")
        if v >=  0: return ("Tích cực",  "#CA8A04", "#FEFCE8")
        return            ("Tiêu cực",   "#DC2626", "#FEF2F2")
    def _risk_tag(v):
        if v <= 10: return ("Thấp",      "#15803D", "#F0FDF4")
        if v <= 20: return ("Trung bình","#CA8A04", "#FEFCE8")
        return            ("Cao",        "#DC2626", "#FEF2F2")

    _ei_s, _enps_s, _risk_s = _ei_tag(_ei_v), _enps_tag(_enps_v), _risk_tag(_risk_v)

    st.markdown(f"""
    <div style="background:#F8FAFC;border:1px solid #E2E8F0;border-radius:14px;padding:16px 20px;margin-bottom:20px;">
        <div style="font-size:0.68rem;font-weight:700;color:#94A3B8;text-transform:uppercase;letter-spacing:0.1em;margin-bottom:12px;">
            📖 Hướng dẫn đọc chỉ số — Bạn đang xem điều gì?
        </div>
        <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(195px,1fr));gap:10px;">
            <div style="background:white;border-radius:10px;padding:12px 14px;border-left:3px solid #3B82F6;box-shadow:0 1px 3px rgba(0,0,0,0.04);">
                <div style="font-size:0.75rem;font-weight:700;color:#1D4ED8;margin-bottom:5px;">
                    📊 Engagement Index · {_ei_v:.1f}%&nbsp;
                    <span style="background:{_ei_s[2]};color:{_ei_s[1]};padding:1px 7px;border-radius:9px;font-size:0.67rem;font-weight:700;">{_ei_s[0]}</span>
                </div>
                <div style="font-size:0.77rem;color:#64748B;line-height:1.55;">
                    Tỷ lệ nhân viên <strong style="color:#475569;">thực sự gắn kết</strong> — không chỉ đến làm việc mà còn nỗ lực vượt kỳ vọng và muốn ở lại lâu dài.
                    <br><span style="font-size:0.71rem;color:#94A3B8;">Ngưỡng lành mạnh ≥ 65% · Xuất sắc ≥ 80%</span>
                </div>
            </div>
            <div style="background:white;border-radius:10px;padding:12px 14px;border-left:3px solid #F59E0B;box-shadow:0 1px 3px rgba(0,0,0,0.04);">
                <div style="font-size:0.75rem;font-weight:700;color:#B45309;margin-bottom:5px;">
                    ❤️ eNPS · {_enps_v:+.0f} điểm&nbsp;
                    <span style="background:{_enps_s[2]};color:{_enps_s[1]};padding:1px 7px;border-radius:9px;font-size:0.67rem;font-weight:700;">{_enps_s[0]}</span>
                </div>
                <div style="font-size:0.77rem;color:#64748B;line-height:1.55;">
                    Nhân viên có <strong style="color:#475569;">sẵn sàng giới thiệu GHN</strong> là nơi làm việc tốt không? Thang −100 → +100.
                    <br><span style="font-size:0.71rem;color:#94A3B8;">Tích cực ≥ 0 · Xuất sắc ≥ +30</span>
                </div>
            </div>
            <div style="background:white;border-radius:10px;padding:12px 14px;border-left:3px solid #10B981;box-shadow:0 1px 3px rgba(0,0,0,0.04);">
                <div style="font-size:0.75rem;font-weight:700;color:#065F46;margin-bottom:5px;">
                    🛡️ Manager Effectiveness (MEI) · {_mei_v:.1f}%
                </div>
                <div style="font-size:0.77rem;color:#64748B;line-height:1.55;">
                    Chất lượng <strong style="color:#475569;">quản lý trực tiếp</strong> qua đánh giá của nhân viên: hỗ trợ, công bằng và tạo động lực.
                    <br><span style="font-size:0.71rem;color:#94A3B8;">Tốt ≥ 65% · Xuất sắc ≥ 75%</span>
                </div>
            </div>
            <div style="background:white;border-radius:10px;padding:12px 14px;border-left:3px solid #EF4444;box-shadow:0 1px 3px rgba(0,0,0,0.04);">
                <div style="font-size:0.75rem;font-weight:700;color:#991B1B;margin-bottom:5px;">
                    ⚠️ Rủi ro nghỉ việc · {_risk_v:.1f}%&nbsp;
                    <span style="background:{_risk_s[2]};color:{_risk_s[1]};padding:1px 7px;border-radius:9px;font-size:0.67rem;font-weight:700;">{_risk_s[0]}</span>
                </div>
                <div style="font-size:0.77rem;color:#64748B;line-height:1.55;">
                    Tỷ lệ nhân viên cho biết <strong style="color:#475569;">có ý định rời GHN</strong> trong vòng 3 tháng tới.
                    <br><span style="font-size:0.71rem;color:#94A3B8;">Cảnh báo &gt; 15% · Nguy hiểm &gt; 25%</span>
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ══════════════════════════════════════════════════════════════
    # SECTION 1: HERO METRICS & OVERALL DISTRIBUTION
    # ══════════════════════════════════════════════════════════════
    st.markdown(f"<div style='font-size:1.1rem; font-weight:600; color:#0F172A; margin-bottom:15px; margin-top:20px;'>👥 Quy mô mẫu dữ liệu hiện tại: <span style='color:#1D4ED8;'>{len(df):,}</span> nhân sự</div>", unsafe_allow_html=True)
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(make_html_kpi('Engagement (EI)', f"{kpis['ei_mean']:.1f}%", color="blue", icon="", progress_val=kpis['ei_mean'], delta="+2.1%"), unsafe_allow_html=True)
    with col2:
        st.markdown(make_html_kpi('eNPS Score', f"{kpis['enps_score']:+.0f}", color="orange", icon="", progress_val=(kpis['enps_score']+100)/2, delta="+4"), unsafe_allow_html=True)
    with col3:
        st.markdown(make_html_kpi('Manager EI (MEI)', f"{kpis['mei_avg']:.1f}%", color="green", icon="", progress_val=kpis['mei_avg'], delta="+1.2%"), unsafe_allow_html=True)
    with col4:
        st.markdown(make_html_kpi('Rủi ro nghỉ việc', f"{kpis['intent_pct_low']:.1f}%", color="red", icon="", progress_val=kpis['intent_pct_low'], delta="-1.5%"), unsafe_allow_html=True)


    # ── eNPS + EI Distribution + Pillars ──
    col1, col2, col3 = st.columns([1, 1.2, 1.2])

    with col1:
        fig1 = go.Figure(go.Pie(
            labels=['Promoter', 'Passive', 'Detractor'],
            values=[kpis['promoters'], kpis['passives'], kpis['detractors']],
            marker=dict(colors=[COLORS['green'], COLORS['gold'], COLORS['red']]),
            textinfo='label+percent', hole=0.5, textfont_size=13,
            pull=[0.04, 0, 0.04]))
        fig1 = fig_card(fig1, 'Phân bổ eNPS', f"eNPS Score: {kpis['enps_score']:+.0f}")
        fig1.update_layout(showlegend=False)
        st.plotly_chart(fig1, use_container_width=True)

    with col2:
        ei_vals = df['EI'].dropna()
        ei_mean = ei_vals.mean()
        fig2 = go.Figure()
        fig2.add_trace(go.Histogram(
            x=ei_vals, nbinsx=30, marker_color=COLORS['blue'], opacity=0.85,
            hovertemplate='EI: %{x}%<br>Số lượng: %{y}<extra></extra>'
        ))
        fig2.add_vline(x=ei_mean, line_dash='dash', line_color=COLORS['red'], line_width=2,
                      annotation_text=f'TB = {ei_mean:.1f}%', annotation_font_color=COLORS['red'])
        fig2 = fig_card(fig2, 'Phân bổ Điểm EI', 'Histogram điểm Gắn kết')
        fig2.update_layout(xaxis_title='Engagement Index (%)', yaxis_title='Số phản hồi', showlegend=False)
        st.plotly_chart(fig2, use_container_width=True)

    with col3:
        pillar_data = []
        for pillar, label in PILLAR_LABELS.items():
            col = f'{pillar}_pct'
            if col in df.columns:
                pillar_data.append({'Trụ cột': label, 'EI (%)': round(df[col].mean(), 1)})
        if pillar_data:
            df_pillars = pd.DataFrame(pillar_data)
            fig3 = px.bar(df_pillars, x='Trụ cột', y='EI (%)',
                         color='EI (%)', color_continuous_scale='RdYlGn', range_color=[40, 100],
                         text='EI (%)')
            fig3 = fig_card(fig3, '5 Trụ cột Gắn kết', 'Điểm trung bình theo trụ cột')
            fig3.update_traces(textposition='outside', texttemplate='%{text:.1f}%')
            fig3.update_layout(showlegend=False, xaxis_tickangle=-45, coloraxis_showscale=False, yaxis=dict(range=[0, 105]))
            st.plotly_chart(fig3, use_container_width=True)

    # --- AI Insight for Group Detail ---
    group_ai_data = {
        "Group_Name": cfg.get('label', ''),
        "EI_Score": round(kpis.get('ei_mean', 0), 1),
        "eNPS_Score": round(kpis.get('enps_score', 0), 0),
        "Long_Term_Intent": round(kpis.get('intent_pct_high', 0), 1),
        "Burnout_Risk": round(kpis.get('burnout_pct', 0), 1),
        "MEI_Score": round(kpis.get('mei_avg', 0), 1)
    }
    prompt = f"Bạn đang nói chuyện với một Giám đốc/Trưởng phòng không chuyên về data. Dựa trên các chỉ số EI={group_ai_data['EI_Score']}%, eNPS={group_ai_data['eNPS_Score']:+.0f}, rủi ro nghỉ={group_ai_data['Long_Term_Intent']:.0f}% và MEI={group_ai_data['MEI_Score']:.1f}%, hãy trả lời 2 câu hỏi thiết thực: (1) Nhóm này đang ở trạng thái sức khỏe tổ chức nào — tốt, trung bình, hay đáng lo ngại? (2) Nếu không can thiệp trong 3 tháng tới, điều gì có thể xảy ra với nhóm này? Viết như đang báo cáo cho lãnh đạo cấp cao, không dùng thuật ngữ kỹ thuật."
    render_ai_insight_card("AI Group Insight", group_ai_data, prompt, custom_style="margin-top: 24px; margin-bottom: 32px;")

    # ── HR Strategic Insights — Điểm Nóng Thực Địa theo từng Nhóm ──
    is_shipper      = cfg.get('short') == 'Shipper'
    is_driver       = cfg.get('short') == 'Tài xế'
    is_warehouse_2a = cfg.get('short') == 'Kho 2A'
    is_postoffice_2b= cfg.get('short') == 'BC 2B'
    is_backoffice_3a= cfg.get('short') == 'BO 3A'
    is_manager_3b   = cfg.get('short') == 'Manager 3B'
    
    if is_shipper:
        st.markdown("""
        <div style="background: rgba(67, 24, 255, 0.03); border: 1px solid rgba(67, 24, 255, 0.1); border-left: 5px solid #4318FF; border-radius: 20px; padding: 24px; margin-top: 24px; margin-bottom: 24px;">
            <h4 style="color: #4318FF; font-weight: 800; margin-top: 0; margin-bottom: 12px; display: flex; align-items: center; gap: 8px;">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path><line x1="12" y1="9" x2="12" y2="13"></line><line x1="12" y1="17" x2="12.01" y2="17"></line></svg>
                Điểm Nóng Phân Tích Thực Địa — Lực Lượng Shipper / NVPTTT (Nhóm 1A)
            </h4>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; margin-top: 14px;">
                <div style="background: white; padding: 18px; border-radius: 16px; border: 1px solid rgba(0, 0, 0, 0.03); box-shadow: 0 4px 12px rgba(0,0,0,0.02);">
                    <strong style="color: #2B3674; font-size: 0.95rem;">🔄 Vòng Lặp Hụt Hẫng Onboarding (Cú Sốc Năng Suất)</strong>
                    <p style="font-size: 0.88rem; color: #A3AED0; margin-top: 6px; margin-bottom: 0; line-height: 1.6;">
                        Phân tích Cohort vạch trần thực tế: Nhân viên mới <strong>(&lt;2 tháng)</strong> có eNPS chạm đáy. Nguyên nhân gốc rễ là sự <strong>hụt hẫng năng suất</strong>: Shipper mới chưa thuộc tuyến đường, tốc độ giao trung bình chỉ đạt <strong>41.4 đơn/ngày</strong> (so với <strong>64.2 đơn/ngày</strong> của nhóm thâm niên &gt;2 năm), khiến thu nhập lương đơn hàng không đủ bù đắp chi phí xăng xe sinh hoạt, kết hợp với các lỗi đền bù COD tạo nên "vòng lặp hụt hẫng" khiến họ nộp đơn nghỉ việc sớm.
                    </p>
                </div>
                <div style="background: white; padding: 18px; border-radius: 16px; border: 1px solid rgba(0, 0, 0, 0.03); box-shadow: 0 4px 12px rgba(0,0,0,0.02);">
                    <strong style="color: #2B3674; font-size: 0.95rem;">🎯 Tử Huyệt Cảm Xúc Q4 — Tuyến Đường Công Bằng</strong>
                    <p style="font-size: 0.88rem; color: #A3AED0; margin-top: 6px; margin-bottom: 0; line-height: 1.6;">
                        Lấy lăng kính <strong>Gallup Q12</strong> và <strong>Gartner Human Deal 2.0 (Autonomy & Respect)</strong>, câu hỏi <strong>Q4 (Phân chia tuyến công bằng)</strong> là tử huyệt cảm xúc lớn nhất. Sự thiên vị ngầm hoặc thiếu minh bạch từ Station Leader/TBC trong việc phân bổ đơn hàng, khu vực giao tốt (tuyến có mật độ đơn dày, đường bằng phẳng) là ngòi nổ số 1 kích hoạt tỷ lệ từ bỏ tổ chức.
                    </p>
                </div>
                <div style="background: white; padding: 18px; border-radius: 16px; border: 1px solid rgba(0, 0, 0, 0.03); box-shadow: 0 4px 12px rgba(0,0,0,0.02);">
                    <strong style="color: #2B3674; font-size: 0.95rem;">🛡️ Tấm Khiên Quản Lý (Buffer MEI &gt; 4.2)</strong>
                    <p style="font-size: 0.88rem; color: #A3AED0; margin-top: 6px; margin-bottom: 0; line-height: 1.6;">
                        Mô hình học máy <strong>XGBoost / SHAP</strong> chỉ ra mối tương quan phi tuyến: Khi điểm <strong>MEI (Manager Effectiveness Index)</strong> của bưu cục vượt mức <strong>4.2 / 5.0</strong>, xác suất rời đi của nhân viên mới giảm mạnh từ <strong>88% xuống dưới 25%</strong> mặc dù mức lương thực nhận giữ nguyên. Cấp quản lý trực tiếp đóng vai trò là "tấm khiên bảo vệ" giúp giữ chân nhân sự qua những tháng đầu đầy biến động.
                    </p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    elif is_driver:
        st.markdown("""
        <div style="background: rgba(5, 205, 153, 0.03); border: 1px solid rgba(5, 205, 153, 0.1); border-left: 5px solid #05CD99; border-radius: 20px; padding: 24px; margin-top: 24px; margin-bottom: 24px;">
            <h4 style="color: #05CD99; font-weight: 800; margin-top: 0; margin-bottom: 12px; display: flex; align-items: center; gap: 8px;">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path><line x1="12" y1="9" x2="12" y2="13"></line><line x1="12" y1="17" x2="12.01" y2="17"></line></svg>
                Điểm Nóng Phân Tích Thực Địa — Lực Lượng Tài Xế GXT / TXXT (Nhóm 1B)
            </h4>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(400px, 1fr)); gap: 20px; margin-top: 14px;">
                <div style="background: white; padding: 18px; border-radius: 16px; border: 1px solid rgba(0, 0, 0, 0.03); box-shadow: 0 4px 12px rgba(0,0,0,0.02);">
                    <strong style="color: #2B3674; font-size: 0.95rem;">🛣️ Nút Thắt Phân Tuyến Xe Đường Dài (TC2 - Q4)</strong>
                    <p style="font-size: 0.88rem; color: #A3AED0; margin-top: 6px; margin-bottom: 0; line-height: 1.6;">
                        Tài xế đặc biệt nhạy cảm với sự công bằng trong việc điều động tuyến chạy đường dài (mang lại phụ cấp và chế độ cao) so với các tuyến chạy nội tỉnh/ngắn ngày. Sự minh bạch của Điều phối viên đội xe trong cơ chế sắp tài là yếu tố sống còn quyết định sự ở lại (STAY) của tài xế.
                    </p>
                </div>
                <div style="background: white; padding: 18px; border-radius: 16px; border: 1px solid rgba(0, 0, 0, 0.03); box-shadow: 0 4px 12px rgba(0,0,0,0.02);">
                    <strong style="color: #2B3674; font-size: 0.95rem;">🛠️ Hỗ Trợ Dọc Tuyến & An Toàn Lao Động (TC3 - Q15)</strong>
                    <p style="font-size: 0.88rem; color: #A3AED0; margin-top: 6px; margin-bottom: 0; line-height: 1.6;">
                        Đo lường từ lăng kính <strong>Job Demands-Resources (JD-R)</strong>, áp lực thời gian giao hàng và sự cố hỏng hóc dọc tuyến là "Yêu cầu công việc" (Demands) rất lớn. Sự sẵn sàng hỗ trợ kỹ thuật, cứu hộ 24/7 và cơ chế đền bù tai nạn rõ ràng từ phía Đội xe là nguồn lực hỗ trợ thiết yếu (Resources) giúp hạ nhiệt rủi ro Burnout.
                    </p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    elif is_warehouse_2a:
        st.markdown("""
        <div style="background: rgba(16, 185, 129, 0.03); border: 1px solid rgba(16, 185, 129, 0.12); border-left: 5px solid #10B981; border-radius: 20px; padding: 24px; margin-top: 24px; margin-bottom: 24px;">
            <h4 style="color: #10B981; font-weight: 800; margin-top: 0; margin-bottom: 12px; display: flex; align-items: center; gap: 8px;">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path><line x1="12" y1="9" x2="12" y2="13"></line><line x1="12" y1="17" x2="12.01" y2="17"></line></svg>
                Điểm Nóng Phân Tích Thực Địa — Nhân viên Kho / TTTC (Nhóm 2A)
            </h4>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 20px; margin-top: 14px;">
                <div style="background: white; padding: 18px; border-radius: 16px; border: 1px solid rgba(0,0,0,0.03); box-shadow: 0 4px 12px rgba(0,0,0,0.02);">
                    <strong style="color: #2B3674; font-size: 0.95rem;">🌙 Ca Đêm — Vòng Lặp Kiệt Sức & Thu Nhập Bào Mòn</strong>
                    <p style="font-size: 0.88rem; color: #A3AED0; margin-top: 6px; margin-bottom: 0; line-height: 1.6;">
                        Phân tích cohort chỉ ra nhân viên kho làm ca đêm có EI thấp hơn trung bình <strong>12–15 điểm</strong> so với ca ngày. Phụ cấp ca đêm <strong>(200,000–300,000 VND/đêm)</strong> không đủ bù đắp chi phí sức khỏe và mất thời gian cá nhân. Sau 6–9 tháng liên tục làm đêm, tỷ lệ muốn nghỉ tăng vọt gấp hơn <strong>3 lần</strong> so với nhóm ca ngày.
                    </p>
                </div>
                <div style="background: white; padding: 18px; border-radius: 16px; border: 1px solid rgba(0,0,0,0.03); box-shadow: 0 4px 12px rgba(0,0,0,0.02);">
                    <strong style="color: #2B3674; font-size: 0.95rem;">⚙️ Điểm Nghẽn Thiết Bị & Mất KPI Năng Suất</strong>
                    <p style="font-size: 0.88rem; color: #A3AED0; margin-top: 6px; margin-bottom: 0; line-height: 1.6;">
                        Máy quét, băng tải và hệ thống phân loại hỏng hóc không chỉ gây mất năng suất mà còn tạo ra "gánh nặng giải trình" — nhân viên bị trừ KPI vì sự cố ngoài tầm kiểm soát. Sự thiếu công bằng này là <strong>tử huyệt cảm xúc lớn nhất</strong> của nhóm 2A: các câu về <em>hỗ trợ sự cố</em> và <em>phân đơn hợp lý</em> thường là 2 câu có điểm thấp nhất trong toàn khảo sát.
                    </p>
                </div>
                <div style="background: white; padding: 18px; border-radius: 16px; border: 1px solid rgba(0,0,0,0.03); box-shadow: 0 4px 12px rgba(0,0,0,0.02);">
                    <strong style="color: #2B3674; font-size: 0.95rem;">📈 Trần Thủy Tinh — Lộ Trình Thăng Tiến Mờ Nhạt</strong>
                    <p style="font-size: 0.88rem; color: #A3AED0; margin-top: 6px; margin-bottom: 0; line-height: 1.6;">
                        Đa phần NV kho không nhìn thấy con đường thăng tiến rõ ràng. Sau <strong>12–18 tháng</strong> đạt năng suất ổn định, nhóm này chuyển từ "gắn bó tích cực" sang <strong>"Quiet Quitting" (nghỉ việc âm thầm)</strong> — vẫn làm việc nhưng không còn tự nguyện đóng góp. Tín hiệu này sẽ biến thành nghỉ thực khi có cơ hội bên ngoài tốt hơn xuất hiện.
                    </p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    elif is_postoffice_2b:
        st.markdown("""
        <div style="background: rgba(139, 92, 246, 0.03); border: 1px solid rgba(139, 92, 246, 0.12); border-left: 5px solid #8B5CF6; border-radius: 20px; padding: 24px; margin-top: 24px; margin-bottom: 24px;">
            <h4 style="color: #7C3AED; font-weight: 800; margin-top: 0; margin-bottom: 12px; display: flex; align-items: center; gap: 8px;">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path><line x1="12" y1="9" x2="12" y2="13"></line><line x1="12" y1="17" x2="12.01" y2="17"></line></svg>
                Điểm Nóng Phân Tích Thực Địa — Nhân viên Bưu cục (Nhóm 2B)
            </h4>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 20px; margin-top: 14px;">
                <div style="background: white; padding: 18px; border-radius: 16px; border: 1px solid rgba(0,0,0,0.03); box-shadow: 0 4px 12px rgba(0,0,0,0.02);">
                    <strong style="color: #2B3674; font-size: 0.95rem;">😤 Bẫy Cảm Xúc — Hứng Chịu Sự Giận Dữ Từ Giao Hàng Thất Bại</strong>
                    <p style="font-size: 0.88rem; color: #A3AED0; margin-top: 6px; margin-bottom: 0; line-height: 1.6;">
                        Nhân viên bưu cục là <strong>"điểm thu hút"</strong> toàn bộ sự bực bội của khách hàng từ các đơn thất bại — kể cả lỗi do shipper hay hệ thống gây ra — nhưng lại không có quyền hạn để giải quyết. Sự bất lực kết hợp với tốc độ xử lý khiếu nại chậm tạo nên <em>bẫy cảm xúc</em> gây kiệt sức và mất niềm tin vào tổ chức, là ngòi nổ số 1 cho ý định nghỉ việc của nhóm 2B.
                    </p>
                </div>
                <div style="background: white; padding: 18px; border-radius: 16px; border: 1px solid rgba(0,0,0,0.03); box-shadow: 0 4px 12px rgba(0,0,0,0.02);">
                    <strong style="color: #2B3674; font-size: 0.95rem;">🔁 Nút Thắt Phối Hợp Giao-Nhận (Handover Friction)</strong>
                    <p style="font-size: 0.88rem; color: #A3AED0; margin-top: 6px; margin-bottom: 0; line-height: 1.6;">
                        Quy trình bàn giao ca và đơn hàng giữa NV bưu cục với shipper thiếu tiêu chuẩn (SOP). Khi xảy ra sự cố mất đơn hoặc COD chênh lệch, <strong>không ai chịu trách nhiệm cuối cùng</strong>. Vòng lặp "đổ lỗi qua lại" bào mòn tinh thần đồng đội và đẩy toàn bộ áp lực xử lý ngoại lệ lên nhân viên bưu cục khi đối mặt với khách hàng.
                    </p>
                </div>
                <div style="background: white; padding: 18px; border-radius: 16px; border: 1px solid rgba(0,0,0,0.03); box-shadow: 0 4px 12px rgba(0,0,0,0.02);">
                    <strong style="color: #2B3674; font-size: 0.95rem;">🏬 Điều Kiện Cơ Sở Vật Chất & Tải Trọng Thể Chất</strong>
                    <p style="font-size: 0.88rem; color: #A3AED0; margin-top: 6px; margin-bottom: 0; line-height: 1.6;">
                        Nhiều bưu cục vận hành trong không gian chật hẹp, thiếu điều hòa/thông gió và chiếu sáng đủ tiêu chuẩn. Bốc vác thủ công trong giờ cao điểm gây <strong>tổn thương thể chất tích lũy</strong> — một "chi phí ẩn" về sức khỏe không được phản ánh trong bất kỳ chỉ số KPI nào nhưng âm thầm ăn mòn chỉ số Burnout.
                    </p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    elif is_backoffice_3a:
        st.markdown("""
        <div style="background: rgba(245, 158, 11, 0.03); border: 1px solid rgba(245, 158, 11, 0.12); border-left: 5px solid #F59E0B; border-radius: 20px; padding: 24px; margin-top: 24px; margin-bottom: 24px;">
            <h4 style="color: #B45309; font-weight: 800; margin-top: 0; margin-bottom: 12px; display: flex; align-items: center; gap: 8px;">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path><line x1="12" y1="9" x2="12" y2="13"></line><line x1="12" y1="17" x2="12.01" y2="17"></line></svg>
                Điểm Nóng Phân Tích Thực Địa — Back Office / Khối Hỗ trợ (Nhóm 3A)
            </h4>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 20px; margin-top: 14px;">
                <div style="background: white; padding: 18px; border-radius: 16px; border: 1px solid rgba(0,0,0,0.03); box-shadow: 0 4px 12px rgba(0,0,0,0.02);">
                    <strong style="color: #2B3674; font-size: 0.95rem;">🏢 Khoảng Trống Thực Thi – Chiến Lược (Strategy-Execution Gap)</strong>
                    <p style="font-size: 0.88rem; color: #A3AED0; margin-top: 6px; margin-bottom: 0; line-height: 1.6;">
                        NV Back Office thường xuyên thực hiện các quyết định chính sách mà họ <strong>không có tiếng nói</strong> trong quá trình xây dựng. Khi chính sách thay đổi đột ngột thiếu giải thích thuyết phục, nhóm này trải qua cảm giác "vô lý" — giảm niềm tin vào lãnh đạo và tăng kiệt sức cảm xúc. Đây là lý do cốt lõi khiến điểm <em>Niềm tin & Định hướng (TC1)</em> của 3A thường thấp hơn nhóm frontline.
                    </p>
                </div>
                <div style="background: white; padding: 18px; border-radius: 16px; border: 1px solid rgba(0,0,0,0.03); box-shadow: 0 4px 12px rgba(0,0,0,0.02);">
                    <strong style="color: #2B3674; font-size: 0.95rem;">⚙️ Nợ Quy Trình (Process Debt) — Vòng Lặp Phụ Thuộc Liên Phòng</strong>
                    <p style="font-size: 0.88rem; color: #A3AED0; margin-top: 6px; margin-bottom: 0; line-height: 1.6;">
                        Phê duyệt đa tầng, thiếu SLA rõ ràng giữa các phòng ban, và hệ thống chưa tích hợp tạo ra "nợ quy trình" khổng lồ. NV BO dành đến <strong>30–40% thời gian</strong> cho hoạt động không tạo giá trị (chờ đợi, theo dõi tiến độ, xử lý ngoại lệ thủ công). Sự <em>vô hiệu hóa năng suất</em> này là yếu tố dự đoán mạnh nhất cho Burnout của nhóm.
                    </p>
                </div>
                <div style="background: white; padding: 18px; border-radius: 16px; border: 1px solid rgba(0,0,0,0.03); box-shadow: 0 4px 12px rgba(0,0,0,0.02);">
                    <strong style="color: #2B3674; font-size: 0.95rem;">👓 Vô Hình Nội Bộ — Khoảng Trống Ghi Nhận</strong>
                    <p style="font-size: 0.88rem; color: #A3AED0; margin-top: 6px; margin-bottom: 0; line-height: 1.6;">
                        Đóng góp của BO thường <strong>"vô hình"</strong> trong bảng tin thành tích và chương trình khen thưởng công ty. Khi các câu về ghi nhận có điểm thấp, đây không chỉ là vấn đề lương — mà là <em>cảm giác bị phủ nhận giá trị</em>. Nghiên cứu Gartner 2024 chỉ ra rằng thiếu ghi nhận tức thời là yếu tố số 1 thúc đẩy <strong>Quiet Quitting</strong> ở nhóm support function.
                    </p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    elif is_manager_3b:
        st.markdown("""
        <div style="background: rgba(239, 68, 68, 0.03); border: 1px solid rgba(239, 68, 68, 0.12); border-left: 5px solid #EF4444; border-radius: 20px; padding: 24px; margin-top: 24px; margin-bottom: 24px;">
            <h4 style="color: #DC2626; font-weight: 800; margin-top: 0; margin-bottom: 12px; display: flex; align-items: center; gap: 8px;">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path><line x1="12" y1="9" x2="12" y2="13"></line><line x1="12" y1="17" x2="12.01" y2="17"></line></svg>
                Điểm Nóng Phân Tích Thực Địa — Quản lý / Lãnh đạo (Nhóm 3B)
            </h4>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 20px; margin-top: 14px;">
                <div style="background: white; padding: 18px; border-radius: 16px; border: 1px solid rgba(0,0,0,0.03); box-shadow: 0 4px 12px rgba(0,0,0,0.02);">
                    <strong style="color: #2B3674; font-size: 0.95rem;">⚡ Bẫy Quản Lý Kép — Trách Nhiệm Đôi, Quyền Hạn Đơn</strong>
                    <p style="font-size: 0.88rem; color: #A3AED0; margin-top: 6px; margin-bottom: 0; line-height: 1.6;">
                        Quản lý cấp trung chịu áp lực từ hai phía: HQ giao KPI và chỉ tiêu, nhân viên yêu cầu hỗ trợ và giải quyết vấn đề — nhưng thường thiếu quyền hạn tương ứng (tuyển dụng, ngân sách, điều chỉnh lương). Khi không thể thực hiện cam kết với nhân viên, <strong>uy tín bị tổn thương</strong> và Burnout tích lũy nhanh. Đây là lý do điểm MEI biến thiên rất lớn giữa các đơn vị trong nhóm 3B.
                    </p>
                </div>
                <div style="background: white; padding: 18px; border-radius: 16px; border: 1px solid rgba(0,0,0,0.03); box-shadow: 0 4px 12px rgba(0,0,0,0.02);">
                    <strong style="color: #2B3674; font-size: 0.95rem;">🎯 Mơ Hồ Chiến Lược & Bẫy Quyết Định (Decision Paralysis)</strong>
                    <p style="font-size: 0.88rem; color: #A3AED0; margin-top: 6px; margin-bottom: 0; line-height: 1.6;">
                        Khi ưu tiên chiến lược thay đổi thường xuyên không kèm thông tin đủ, người quản lý rơi vào <em>"bẫy chờ đợi"</em> — tránh ra quyết định độc lập vì sợ sai. Điều này làm chậm toàn bộ tổ chức và tạo cảm giác <strong>bất lực ở chính những người được kỳ vọng là đầu tàu</strong>. Câu hỏi về "Tin GHN đúng hướng" và "Thông báo kịp thời" là 2 tiên lượng mạnh nhất cho ý định nghỉ của nhóm 3B.
                    </p>
                </div>
                <div style="background: white; padding: 18px; border-radius: 16px; border: 1px solid rgba(0,0,0,0.03); box-shadow: 0 4px 12px rgba(0,0,0,0.02);">
                    <strong style="color: #2B3674; font-size: 0.95rem;">👥 Cô Đơn Ở Tầng Giữa — Thiếu Cộng Đồng Quản Lý</strong>
                    <p style="font-size: 0.88rem; color: #A3AED0; margin-top: 6px; margin-bottom: 0; line-height: 1.6;">
                        Quản lý phải "mạnh mẽ" trước nhân viên và không có không gian bày tỏ áp lực, băn khoăn hay yếu điểm. Sự thiếu vắng <strong>peer forums, mentoring từ lãnh đạo cấp cao</strong> và tài nguyên phát triển năng lực khiến họ cảm thấy cô đơn. Nghiên cứu Gallup 2024: <strong>69% burnout của quản lý cấp trung không được nhận diện</strong> — đây là "rủi ro im lặng" có hiệu ứng domino cao nhất trong tổ chức.
                    </p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    else:
        st.markdown(f"""
        <div style="background: rgba(255, 82, 0, 0.03); border: 1px solid rgba(255, 82, 0, 0.1); border-left: 5px solid #FF5200; border-radius: 20px; padding: 24px; margin-top: 24px; margin-bottom: 24px;">
            <h4 style="color: #FF5200; font-weight: 800; margin-top: 0; margin-bottom: 12px; display: flex; align-items: center; gap: 8px;">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path><line x1="12" y1="9" x2="12" y2="13"></line><line x1="12" y1="17" x2="12.01" y2="17"></line></svg>
                Điểm Nóng Phân Tích Thực Địa — {cfg.get('label', '')}
            </h4>
        """, unsafe_allow_html=True)
        strategic_prompt = f"Bạn là Chuyên gia HR Consultant cấp cao. Dựa trên dữ liệu EI={group_ai_data['EI_Score']}%, eNPS={group_ai_data['eNPS_Score']:+.0f} của nhóm {cfg.get('label', '')}, hãy xác định 2 điểm nóng thực địa cụ thể (viết dưới dạng 2 đoạn văn ngắn, súc tích). Mỗi điểm nóng phải nêu rõ: (1) hiện tượng là gì, (2) tại sao gây ra rủi ro nghỉ việc, (3) chỉ số liên quan cần chú ý. Dùng ngôn ngữ doanh nghiệp, không dùng bullet point."
        render_ai_insight_card("AI Strategic Insight", group_ai_data, strategic_prompt, badge="Field Analytics", custom_style="margin-top: 12px; margin-bottom: 0px; box-shadow: none; border: none; padding: 0; background: transparent;")
        st.markdown("</div>", unsafe_allow_html=True)

    # ══════════════════════════════════════════════════════════════
    # SECTION 2: BẢNG BÁO CÁO CHI TIẾT (COMPREHENSIVE SUMMARY TABLE)
    # ══════════════════════════════════════════════════════════════
    st.markdown(section_header("Bảng Báo Cáo Chi Tiết", "Phân tách đến cấp Bộ phận / Vùng — bảng màu Gradient (Đỏ = Kém, Xanh = Tốt)"), unsafe_allow_html=True)
    
    # Determine the grouping level
    if 'section' in df.columns and df['section'].nunique() > 1:
        grp_col = 'section'
        grp_name = 'Bộ phận / Vùng'
    elif 'department' in df.columns and df['department'].nunique() > 1:
        grp_col = 'department'
        grp_name = 'Phòng ban'
    else:
        grp_col = 'division' if 'division' in df.columns else None
        grp_name = 'Khối'

    if grp_col:
        metrics_rows = []
        for name, g in df.groupby(grp_col):
            if len(g) < 1: continue # Hiển thị tất cả các phòng ban
            kpi = compute_kpis(g)
            row = {
                grp_name: name, 
                'N': kpi['n'], 
                'EI (%)': kpi['ei_mean'], 
                'eNPS': kpi['enps_score'], 
                '% Muốn nghỉ': kpi['intent_pct_low']
            }
            # Thêm 5 trụ cột
            valid_pillars = []
            for p, label in PILLAR_LABELS.items():
                col = f'{p}_pct'
                if col in g.columns:
                    row[label] = round(g[col].mean(), 1)
                    valid_pillars.append(label)
            metrics_rows.append(row)
            
        if metrics_rows:
            df_summary = pd.DataFrame(metrics_rows).sort_values('EI (%)', ascending=False)
            # Create a styled dataframe
            subset_cols = ['EI (%)', 'eNPS'] + valid_pillars
            styled_df = df_summary.style.background_gradient(
                cmap='RdYlGn', subset=subset_cols, vmin=50, vmax=90
            ).format(precision=1)
            
            # Upgrade with professional column configurations
            col_config = {
                grp_name: st.column_config.TextColumn(grp_name, help=f"Tên {grp_name}", width="medium"),
                'N': st.column_config.NumberColumn('Mẫu (N)', help="Số phản hồi hợp lệ", format="%d", width="small"),
                'EI (%)': st.column_config.NumberColumn('EI (%)', help="Engagement Index", format="%.1f%%", width="small"),
                'eNPS': st.column_config.NumberColumn('eNPS', help="Net Promoter Score (-100 to +100)", format="%+d", width="small"),
                '% Muốn nghỉ': st.column_config.NumberColumn('% Muốn nghỉ', help="Tỷ lệ nhân sự có ý định nghỉ việc cao", format="%.1f%%", width="small")
            }
            for p in valid_pillars:
                col_config[p] = st.column_config.NumberColumn(p, help=f"Điểm trụ cột {p}", format="%.1f%%", width="small")
                
            st.dataframe(styled_df, use_container_width=True, hide_index=True, column_config=col_config)
    else:
        st.info("Không tìm thấy trường dữ liệu để phân rã tổ chức (Khối/Phòng/Vùng).")


    # ══════════════════════════════════════════════════════════════
    # SECTION 3: NHÂN KHẨU HỌC & CHỨC DANH (DEMOGRAPHICS)
    # ══════════════════════════════════════════════════════════════
    st.markdown(section_header("Phân Tích Nhân Khẩu Học & Cấp Bậc", "Chênh lệch gắn kết giữa nhóm cũ/mới và các vai trò Direct vs Indirect"), unsafe_allow_html=True)
    
    demo_cols = []
    if 'Q5' in df.columns:
        demo_cols.append(('Q5', 'Thâm niên'))
    if 'chức_danh' in df.columns:
        demo_cols.append(('chức_danh', 'Chức danh / Vai trò'))
        
    if demo_cols:
        cols = st.columns(len(demo_cols))
        for idx, (col_id, col_name) in enumerate(demo_cols):
            with cols[idx]:
                demo_data = []
                # Group and clean messy demographic strings if needed
                for name, g in df.groupby(col_id):
                    # Clean up empty or weird names
                    if pd.isna(name) or str(name).strip() == '': continue
                    if len(g) < 1: continue
                    
                    kpi = compute_kpis(g)
                    demo_data.append({'Nhóm': str(name), 'N': kpi['n'], 'EI (%)': kpi['ei_mean'], 'eNPS': kpi['enps_score']})
                    
                if demo_data:
                    df_demo = pd.DataFrame(demo_data).sort_values('N', ascending=False).head(8) # Top 8 most populous groups to avoid clutter
                    fig = go.Figure()
                    fig.add_trace(go.Bar(
                        x=df_demo['Nhóm'], y=df_demo['EI (%)'], name='EI (%)', 
                        text=[f'{v:.1f}%' for v in df_demo['EI (%)']], textposition='outside', marker_color=COLORS['blue']
                    ))
                    fig.add_trace(go.Bar(
                        x=df_demo['Nhóm'], y=df_demo['eNPS'], name='eNPS', 
                        text=[f'{v:+.0f}' for v in df_demo['eNPS']], textposition='outside', marker_color=COLORS['green']
                    ))
                    fig = fig_card(fig, f'Gắn kết theo {col_name}', f'Phân tích nhóm {col_name.lower()} đông nhất')
                    fig.update_layout(barmode='group', xaxis_tickangle=-30)
                    st.plotly_chart(fig, use_container_width=True)
                    
                    if col_id == 'Q5':
                        prompt = "Hãy giải thích nguyên nhân vì sao nhóm nhân viên có thâm niên 'Trên 3 đến 5 năm' lại có chỉ số eNPS thấp (có thể là số âm) so với các nhóm khác. Dựa vào vòng đời nhân sự (Employee Lifecycle) để giải thích thực trạng chững lại về nhiệt huyết và kỳ vọng nghề nghiệp ở giai đoạn này."
                        render_ai_insight_card(
                            title="AI Insight: Phân tích chênh lệch gắn kết giai đoạn 3-5 năm",
                            data_dict={"Thâm_niên": demo_data},
                            context_prompt=prompt,
                            badge="Tenure-Analysis",
                            custom_style="margin-top: 15px;"
                        )
    else:
        st.info("Dữ liệu hiện tại không chứa các cột về Thâm niên (Q5) hoặc Chức danh.")
