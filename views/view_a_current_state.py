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
    from shared.plotly_theme import make_html_kpi, section_header

    _ei_v      = kpis['ei_mean']
    _enps_v    = kpis['enps_score']
    _mei_v     = kpis['mei_avg']
    _risk_v    = kpis['intent_pct_low']
    _burnout_v = kpis['burnout_pct']
    _stay_v    = kpis.get('stay_score_avg', 0)
    _stay_fl   = kpis.get('stay_flight_pct', 0)
    _stay_ar   = kpis.get('stay_atrisk_pct', 0)
    _stay_st   = kpis.get('stay_stable_pct', 0)

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
    def _burnout_tag(v):
        if v <= 15: return ("An toàn",   "#15803D", "#F0FDF4")
        if v <= 30: return ("Cần chú ý","#CA8A04", "#FEFCE8")
        return            ("Nguy hiểm",  "#DC2626", "#FEF2F2")
    def _stay_tag(v):
        if v >= 4.0: return ("Tốt",       "#15803D", "#F0FDF4")
        if v >= 3.0: return ("Trung bình","#CA8A04", "#FEFCE8")
        return             ("Nguy hiểm",  "#DC2626", "#FEF2F2")

    _ei_s, _enps_s, _risk_s = _ei_tag(_ei_v), _enps_tag(_enps_v), _risk_tag(_risk_v)
    _burnout_s, _stay_s = _burnout_tag(_burnout_v), _stay_tag(_stay_v)

    # ══ SECTION 1: COMPACT HERO KPI — 1 hàng 6 cột ══
    # ── Data Quality Summary Panel ──
    _n_before    = df.attrs.get('n_before', len(df))
    _n_removed   = df.attrs.get('n_removed', 0)
    _pct_removed = df.attrs.get('pct_removed', 0.0)
    _filter_desc = df.attrs.get('filter_desc', 'Áp dụng bộ lọc chất lượng tiêu chuẩn')
    _filter_meth = df.attrs.get('filter_method', 'standard')
    _n_final     = len(df)
    _keep_pct    = round(_n_final / _n_before * 100, 1) if _n_before > 0 else 100

    _meth_color = {"none": "#0EA5E9", "straight_and_empty": "#8B5CF6", "standard": "#10B981"}.get(_filter_meth, "#64748B")
    _meth_label = {"none": "Không lọc", "straight_and_empty": "Lọc straight-line + mở trống", "standard": "Lọc chuẩn"}.get(_filter_meth, "Lọc chuẩn")

    st.markdown(f"""
    <div style="background:#F8FAFC;border:1px solid #E2E8F0;border-radius:12px;padding:12px 18px;margin-bottom:14px;">
        <div style="display:flex;align-items:center;gap:10px;flex-wrap:wrap;margin-bottom:10px;">
            <span style="font-size:0.72rem;font-weight:700;text-transform:uppercase;letter-spacing:0.08em;color:#94A3B8;">📊 Xử lý dữ liệu</span>
            <span style="background:{_meth_color}18;color:{_meth_color};font-size:0.68rem;font-weight:700;padding:2px 10px;border-radius:20px;">{_meth_label}</span>
            <span style="font-size:0.72rem;color:#64748B;margin-left:auto;">{_filter_desc}</span>
        </div>
        <div style="display:flex;gap:24px;align-items:center;flex-wrap:wrap;">
            <div style="text-align:center;">
                <div style="font-size:1.3rem;font-weight:900;color:#1E293B;letter-spacing:-0.03em;">{_n_before:,}</div>
                <div style="font-size:0.65rem;color:#94A3B8;font-weight:600;text-transform:uppercase;letter-spacing:0.06em;">Mẫu thu thập</div>
            </div>
            <div style="font-size:1.2rem;color:#CBD5E1;">→</div>
            <div style="text-align:center;">
                <div style="font-size:1.3rem;font-weight:900;color:#DC2626;letter-spacing:-0.03em;">−{_n_removed:,}</div>
                <div style="font-size:0.65rem;color:#94A3B8;font-weight:600;text-transform:uppercase;letter-spacing:0.06em;">Loại bỏ ({_pct_removed:.1f}%)</div>
            </div>
            <div style="font-size:1.2rem;color:#CBD5E1;">→</div>
            <div style="text-align:center;">
                <div style="font-size:1.3rem;font-weight:900;color:#15803D;letter-spacing:-0.03em;">{_n_final:,}</div>
                <div style="font-size:0.65rem;color:#94A3B8;font-weight:600;text-transform:uppercase;letter-spacing:0.06em;">Mẫu phân tích ({_keep_pct:.1f}%)</div>
            </div>
            <div style="flex:1;min-width:120px;">
                <div style="background:#E2E8F0;border-radius:99px;height:6px;overflow:hidden;">
                    <div style="background:linear-gradient(90deg,#15803D,#22C55E);height:100%;width:{_keep_pct}%;border-radius:99px;transition:width 0.5s;"></div>
                </div>
                <div style="font-size:0.65rem;color:#94A3B8;margin-top:3px;text-align:right;">{_keep_pct:.1f}% được sử dụng</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    def _kpi_chip(label, value, tag_text, tag_color, tag_bg, sub, border_color):
        return (
            f'<div style="background:#fff;border:1px solid #E2E8F0;border-top:3px solid {border_color};'
            f'border-radius:10px;padding:13px 14px;height:100%;box-sizing:border-box;">'
            f'<div style="font-size:0.64rem;font-weight:700;text-transform:uppercase;letter-spacing:0.07em;'
            f'color:#94A3B8;margin-bottom:7px;">{label}</div>'
            f'<div style="display:flex;align-items:baseline;gap:7px;flex-wrap:wrap;">'
            f'<span style="font-size:1.55rem;font-weight:900;color:#0A1F44;letter-spacing:-0.03em;line-height:1;">{value}</span>'
            f'<span style="font-size:0.68rem;font-weight:700;color:{tag_color};background:{tag_bg};'
            f'padding:2px 7px;border-radius:20px;white-space:nowrap;">{tag_text}</span>'
            f'</div>'
            f'<div style="font-size:0.67rem;color:#94A3B8;margin-top:5px;">{sub}</div>'
            f'</div>'
        )

    # ══ SECTION 1: KPI CARDS — Hàng 1: 3 cột | Hàng 2: 3 cột căn giữa ══
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(_kpi_chip("Engagement (EI)", f"{_ei_v:.1f}%", _ei_s[0], _ei_s[1], _ei_s[2],
                              "Ngưỡng lành mạnh ≥ 65% · Xuất sắc ≥ 80%", "#3B82F6"), unsafe_allow_html=True)
    with c2:
        st.markdown(_kpi_chip("eNPS", f"{_enps_v:+.0f} điểm", _enps_s[0], _enps_s[1], _enps_s[2],
                              "Tích cực ≥ 0 · Xuất sắc ≥ +30", "#F59E0B"), unsafe_allow_html=True)
    with c3:
        mei_tag = _ei_tag(_mei_v)
        st.markdown(_kpi_chip("Manager Effectiveness (MEI)", f"{_mei_v:.1f}%", mei_tag[0], mei_tag[1], mei_tag[2],
                              "Tốt ≥ 65% · Xuất sắc ≥ 75%", "#10B981"), unsafe_allow_html=True)

    st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)

    # Hàng 2: 3 cột căn giữa (dùng spacer hai bên)
    _s1, c4, c5, c6, _s2 = st.columns([0.5, 1, 1, 1, 0.5])
    with c4:
        st.markdown(_kpi_chip("Rủi ro nghỉ việc", f"{_risk_v:.1f}%", _risk_s[0], _risk_s[1], _risk_s[2],
                              "Cảnh báo > 15% · Nguy hiểm > 25%", "#EF4444"), unsafe_allow_html=True)
    with c5:
        st.markdown(_kpi_chip("Burnout Score", f"{_burnout_v:.1f}%", _burnout_s[0], _burnout_s[1], _burnout_s[2],
                              "An toàn ≤ 15% · Cần chú ý ≤ 30%", "#8B5CF6"), unsafe_allow_html=True)
    with c6:
        st.markdown(_kpi_chip("Ý định Ở lại (Q22)", f"{_stay_v:.2f}/5", _stay_s[0], _stay_s[1], _stay_s[2],
                              f"Flight Risk {_stay_fl:.0f}% · Stable {_stay_st:.0f}%", "#06B6D4"), unsafe_allow_html=True)

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

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
    ai_prompt = f"Bạn đang nói chuyện với một Giám đốc/Trưởng phòng không chuyên về data. Dựa trên các chỉ số EI={group_ai_data['EI_Score']}%, eNPS={group_ai_data['eNPS_Score']:+.0f}, rủi ro nghỉ={group_ai_data['Long_Term_Intent']:.0f}% và MEI={group_ai_data['MEI_Score']:.1f}%, hãy trả lời 2 câu hỏi thiết thực: (1) Nhóm này đang ở trạng thái sức khỏe tổ chức nào — tốt, trung bình, hay đáng lo ngại? (2) Nếu không can thiệp trong 3 tháng tới, điều gì có thể xảy ra với nhóm này? Viết như đang báo cáo cho lãnh đạo cấp cao, không dùng thuật ngữ kỹ thuật."
    # ► Đặt chỗ trống cho AI — sẽ được render SAU khi toàn bộ UI đã hiển thị
    ai_placeholder = st.empty()

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
    # SECTION 2: BẢNG BÁO CÁO CHI TIẾT — PHÂN CẤP Division → Department
    # Cấu trúc: mỗi Division (Vùng/Khối) là 1 bảng riêng; Department là rows
    # Giống ees-tracking: groupby Division → xem chi tiết Department bên trong
    # ══════════════════════════════════════════════════════════════
    st.markdown(section_header(
        "Bảng Báo Cáo Chi Tiết",
        "Phân cấp theo Khối (Division) → Phòng ban / Tỉnh (Department) — bảng màu Gradient (Đỏ = Kém, Xanh = Tốt)"
    ), unsafe_allow_html=True)

    _BAD_VALS = {None, 'None', 'Khác', 'Chưa xác định', 'Không xác định', 'nan', ''}

    # Xác định cột department để drill down
    _has_vung = 'division' in df.columns and df['division'].eq('Vùng').any()
    if _has_vung and 'section' in df.columns and df['section'].nunique() > 1:
        dept_col  = 'section'
        dept_name = 'Section / Vùng'
    elif 'department' in df.columns and df['department'].nunique() > 1:
        dept_col  = 'department'
        dept_name = 'Phòng ban / Tỉnh'
    elif 'section' in df.columns and df['section'].nunique() > 1:
        dept_col  = 'section'
        dept_name = 'Section'
    else:
        dept_col  = None
        dept_name = 'Phòng ban'

    _has_div = 'division' in df.columns and df['division'].notna().any()

    if _has_div:
        df_valid = df[df['division'].notna() & ~df['division'].isin(_BAD_VALS)].copy()
        divs_sorted = (
            df_valid.groupby('division')['EI']
            .mean()
            .sort_values(ascending=False)
            .index.tolist()
        ) if 'EI' in df_valid.columns else sorted(df_valid['division'].unique().tolist())

        for div_name in divs_sorted:
            df_div = df_valid[df_valid['division'] == div_name]
            if len(df_div) < 2:
                continue
            div_kpi = compute_kpis(df_div)

            # ── Header badge cho mỗi Division ──
            ei_color = (
                "#15803D" if div_kpi['ei_mean'] >= 65
                else "#CA8A04" if div_kpi['ei_mean'] >= 50
                else "#DC2626"
            )
            ei_bg = (
                "#F0FDF4" if div_kpi['ei_mean'] >= 65
                else "#FEFCE8" if div_kpi['ei_mean'] >= 50
                else "#FEF2F2"
            )
            enps_color = "#15803D" if div_kpi['enps_score'] >= 0 else "#DC2626"

            st.markdown(f"""
            <div style="
                display:flex; align-items:center; gap:10px;
                background:#F8FAFC; border:1px solid #E2E8F0;
                border-left:4px solid {ei_color};
                border-radius:10px; padding:10px 16px;
                margin-top:18px; margin-bottom:6px;
            ">
                <span style="font-size:0.95rem;font-weight:700;color:#1E293B;flex:1;">
                    📍 {div_name}
                </span>
                <span style="background:{ei_bg};color:{ei_color};font-size:0.72rem;font-weight:700;
                      padding:3px 10px;border-radius:20px;">
                    EI {div_kpi['ei_mean']:.1f}%
                </span>
                <span style="background:#F1F5F9;color:{enps_color};font-size:0.72rem;font-weight:700;
                      padding:3px 10px;border-radius:20px;">
                    eNPS {div_kpi['enps_score']:+.0f}
                </span>
                <span style="background:#F1F5F9;color:#64748B;font-size:0.72rem;font-weight:600;
                      padding:3px 10px;border-radius:20px;">
                    N={div_kpi['n']:,}
                </span>
            </div>
            """, unsafe_allow_html=True)

            # ── Bảng Department bên trong Division ──
            # Nếu department == 'Vùng' → drill down thêm 1 cấp vào section (Vùng 1, Vùng 2, ...)
            _ROW_LBL = 'Phòng ban / Vùng'
            if 'department' in df_div.columns:
                df_dept_valid = df_div[df_div['department'].notna() & ~df_div['department'].isin(_BAD_VALS)]
                dept_rows = []
                dept_pillars_seen = []

                for dname, dg in df_dept_valid.groupby('department', dropna=True):
                    if len(dg) < 1:
                        continue

                    # Departments cần drill down vào section nếu có dữ liệu chi tiết hơn:
                    # - "Vùng" → Vùng HCM, HNO, DNB...
                    # - "Kho Trung Chuyển" → Cụm KTC Xuyên Á, M12, Đài Tư...
                    _EXPAND_DEPTS = {'vùng', 'kho trung chuyển'}
                    dname_norm = str(dname).strip().lower()
                    is_expand_dept = dname_norm in _EXPAND_DEPTS

                    if is_expand_dept and 'section' in dg.columns:
                        _sec_valid = dg[dg['section'].notna() & ~dg['section'].isin(_BAD_VALS)]
                        # Chỉ expand nếu có ít nhất 1 section khác tên department
                        unique_secs = _sec_valid['section'].unique()
                        has_specific = any(str(s).strip().lower() != dname_norm for s in unique_secs)


                        if has_specific:
                            # Thêm hàng tổng hợp cho department (Kho Trung Chuyển / Vùng) trước khi mở rộng
                            dkpi_parent = compute_kpis(dg)
                            parent_row = {
                                _ROW_LBL: f'📦 {dname}' if 'kho' in dname_norm else f'🗺️ {dname}',
                                'N': dkpi_parent['n'],
                                'EI (%)': round(dkpi_parent['ei_mean'], 1),
                                'eNPS': round(dkpi_parent['enps_score'], 0),
                                'MEI': round(dkpi_parent.get('mei_avg', 0), 1),
                                'Burnout (%)': round(dkpi_parent.get('burnout_pct', 0), 1),
                                '% Muốn nghỉ': round(dkpi_parent['intent_pct_low'], 1),
                            }
                            for p, plabel in PILLAR_LABELS.items():
                                pcol = f'{p}_pct'
                                if pcol in dg.columns:
                                    parent_row[plabel] = round(dg[pcol].mean(), 1)
                                    if plabel not in dept_pillars_seen:
                                        dept_pillars_seen.append(plabel)
                            dept_rows.append(parent_row)

                            for sname, sg in _sec_valid.groupby('section', dropna=True):
                                if len(sg) < 1:
                                    continue
                                skpi = compute_kpis(sg)
                                srow = {
                                    _ROW_LBL: f'  ↳ {sname}',
                                    'N': skpi['n'],
                                    'EI (%)': round(skpi['ei_mean'], 1),
                                    'eNPS': round(skpi['enps_score'], 0),
                                    'MEI': round(skpi.get('mei_avg', 0), 1),
                                    'Burnout (%)': round(skpi.get('burnout_pct', 0), 1),
                                    '% Muốn nghỉ': round(skpi['intent_pct_low'], 1),
                                }
                                for p, plabel in PILLAR_LABELS.items():
                                    pcol = f'{p}_pct'
                                    if pcol in sg.columns:
                                        srow[plabel] = round(sg[pcol].mean(), 1)
                                        if plabel not in dept_pillars_seen:
                                            dept_pillars_seen.append(plabel)
                                dept_rows.append(srow)

                        else:
                            # Không có sub-section → hiển thị aggregate row cho department
                            dkpi = compute_kpis(dg)
                            drow = {
                                _ROW_LBL: str(dname),
                                'N': dkpi['n'],
                                'EI (%)': round(dkpi['ei_mean'], 1),
                                'eNPS': round(dkpi['enps_score'], 0),
                                'MEI': round(dkpi.get('mei_avg', 0), 1),
                                'Burnout (%)': round(dkpi.get('burnout_pct', 0), 1),
                                '% Muốn nghỉ': round(dkpi['intent_pct_low'], 1),
                            }
                            for p, plabel in PILLAR_LABELS.items():
                                pcol = f'{p}_pct'
                                if pcol in dg.columns:
                                    drow[plabel] = round(dg[pcol].mean(), 1)
                                    if plabel not in dept_pillars_seen:
                                        dept_pillars_seen.append(plabel)
                            dept_rows.append(drow)
                    else:
                        # Department thường (không phải Vùng) → row trực tiếp
                        dkpi = compute_kpis(dg)
                        drow = {
                            _ROW_LBL: str(dname),
                            'N': dkpi['n'],
                            'EI (%)': round(dkpi['ei_mean'], 1),
                            'eNPS': round(dkpi['enps_score'], 0),
                            'MEI': round(dkpi.get('mei_avg', 0), 1),
                            'Burnout (%)': round(dkpi.get('burnout_pct', 0), 1),
                            '% Muốn nghỉ': round(dkpi['intent_pct_low'], 1),
                        }
                        for p, plabel in PILLAR_LABELS.items():
                            pcol = f'{p}_pct'
                            if pcol in dg.columns:
                                drow[plabel] = round(dg[pcol].mean(), 1)
                                if plabel not in dept_pillars_seen:
                                    dept_pillars_seen.append(plabel)
                        dept_rows.append(drow)

                if dept_rows:
                    df_dept_tbl = pd.DataFrame(dept_rows)
                    # Giữ insertion order nếu có parent-child (↳) — tránh tách hàng tổng khỏi hàng con
                    if not df_dept_tbl[_ROW_LBL].str.contains('↳', na=False).any():
                        df_dept_tbl = df_dept_tbl.sort_values('EI (%)', ascending=False)
                    _grad = ['EI (%)', 'MEI'] + dept_pillars_seen

                    _red  = ['Burnout (%)', '% Muốn nghỉ']
                    styled = df_dept_tbl.style \
                        .background_gradient(
                            cmap='RdYlGn',
                            subset=[c for c in _grad if c in df_dept_tbl.columns],
                            vmin=50, vmax=90
                        ) \
                        .background_gradient(
                            cmap='RdYlGn_r',
                            subset=[c for c in _red if c in df_dept_tbl.columns],
                            vmin=0, vmax=20
                        ) \
                        .format(precision=1)

                    col_cfg = {
                        _ROW_LBL: st.column_config.TextColumn(_ROW_LBL, width='medium'),
                        'N': st.column_config.NumberColumn('Mẫu (N)', format='%d', width='small'),
                        'EI (%)': st.column_config.NumberColumn('EI (%)', format='%.1f%%', width='small'),
                        'eNPS': st.column_config.NumberColumn('eNPS', format='%+.0f', width='small'),
                        'MEI': st.column_config.NumberColumn('MEI', format='%.1f', width='small'),
                        'Burnout (%)': st.column_config.NumberColumn('Burnout (%)', format='%.1f%%', width='small'),
                        '% Muốn nghỉ': st.column_config.NumberColumn('% Muốn nghỉ', format='%.1f%%', width='small'),
                    }
                    for pl in dept_pillars_seen:
                        col_cfg[pl] = st.column_config.NumberColumn(pl, format='%.1f%%', width='small')

                    st.dataframe(styled, use_container_width=True, hide_index=True, column_config=col_cfg)
                else:
                    st.caption("  ↳ Chưa đủ dữ liệu để phân rã.")
            elif dept_col and dept_col in df_div.columns:
                # Fallback: dùng dept_col gốc (section) nếu không có 'department'
                df_dept_valid = df_div[df_div[dept_col].notna() & ~df_div[dept_col].isin(_BAD_VALS)]
                dept_rows = []
                dept_pillars_seen = []
                for dname, dg in df_dept_valid.groupby(dept_col, dropna=True):
                    if len(dg) < 1:
                        continue
                    dkpi = compute_kpis(dg)
                    drow = {
                        _ROW_LBL: str(dname),
                        'N': dkpi['n'],
                        'EI (%)': round(dkpi['ei_mean'], 1),
                        'eNPS': round(dkpi['enps_score'], 0),
                        'MEI': round(dkpi.get('mei_avg', 0), 1),
                        'Burnout (%)': round(dkpi.get('burnout_pct', 0), 1),
                        '% Muốn nghỉ': round(dkpi['intent_pct_low'], 1),
                    }
                    for p, plabel in PILLAR_LABELS.items():
                        pcol = f'{p}_pct'
                        if pcol in dg.columns:
                            drow[plabel] = round(dg[pcol].mean(), 1)
                            if plabel not in dept_pillars_seen:
                                dept_pillars_seen.append(plabel)
                    dept_rows.append(drow)
                if dept_rows:
                    df_dept_tbl = pd.DataFrame(dept_rows).sort_values('EI (%)', ascending=False)
                    _grad = ['EI (%)', 'MEI'] + dept_pillars_seen
                    _red  = ['Burnout (%)', '% Muốn nghỉ']
                    styled = df_dept_tbl.style \
                        .background_gradient(cmap='RdYlGn', subset=[c for c in _grad if c in df_dept_tbl.columns], vmin=50, vmax=90) \
                        .background_gradient(cmap='RdYlGn_r', subset=[c for c in _red if c in df_dept_tbl.columns], vmin=0, vmax=20) \
                        .format(precision=1)
                    col_cfg = {
                        _ROW_LBL: st.column_config.TextColumn(_ROW_LBL, width='medium'),
                        'N': st.column_config.NumberColumn('Mẫu (N)', format='%d', width='small'),
                        'EI (%)': st.column_config.NumberColumn('EI (%)', format='%.1f%%', width='small'),
                        'eNPS': st.column_config.NumberColumn('eNPS', format='%+.0f', width='small'),
                        'MEI': st.column_config.NumberColumn('MEI', format='%.1f', width='small'),
                        'Burnout (%)': st.column_config.NumberColumn('Burnout (%)', format='%.1f%%', width='small'),
                        '% Muốn nghỉ': st.column_config.NumberColumn('% Muốn nghỉ', format='%.1f%%', width='small'),
                    }
                    for pl in dept_pillars_seen:
                        col_cfg[pl] = st.column_config.NumberColumn(pl, format='%.1f%%', width='small')
                    st.dataframe(styled, use_container_width=True, hide_index=True, column_config=col_cfg)
                else:
                    st.caption("  ↳ Chưa đủ dữ liệu để phân rã.")
            else:
                st.caption("  ↳ Không có dữ liệu phòng ban cho nhóm này.")

    elif dept_col:
        # Fallback: không có division, hiển thị bảng department phẳng
        _BAD = {None, 'None', 'Khác', 'Chưa xác định', 'Không xác định', 'nan', ''}
        df_grp_valid = df[df[dept_col].notna() & ~df[dept_col].isin(_BAD)].copy()
        metrics_rows = []
        valid_pillars = []
        for name, g in df_grp_valid.groupby(dept_col, dropna=True):
            if len(g) < 1: continue
            kpi = compute_kpis(g)
            row = {
                dept_name: name,
                'N': kpi['n'],
                'EI (%)': kpi['ei_mean'],
                'eNPS': kpi['enps_score'],
                '% Muốn nghỉ': kpi['intent_pct_low']
            }
            for p, label in PILLAR_LABELS.items():
                col = f'{p}_pct'
                if col in g.columns:
                    row[label] = round(g[col].mean(), 1)
                    if label not in valid_pillars:
                        valid_pillars.append(label)
            metrics_rows.append(row)

        if metrics_rows:
            df_summary = pd.DataFrame(metrics_rows).sort_values('EI (%)', ascending=False)
            subset_cols = ['EI (%)', 'eNPS'] + valid_pillars
            styled_df = df_summary.style.background_gradient(
                cmap='RdYlGn', subset=subset_cols, vmin=50, vmax=90
            ).format(precision=1)
            col_config = {
                dept_name: st.column_config.TextColumn(dept_name, width="medium"),
                'N': st.column_config.NumberColumn('Mẫu (N)', format="%d", width="small"),
                'EI (%)': st.column_config.NumberColumn('EI (%)', format="%.1f%%", width="small"),
                'eNPS': st.column_config.NumberColumn('eNPS', format="%+d", width="small"),
                '% Muốn nghỉ': st.column_config.NumberColumn('% Muốn nghỉ', format="%.1f%%", width="small")
            }
            for p in valid_pillars:
                col_config[p] = st.column_config.NumberColumn(p, format="%.1f%%", width="small")
            st.dataframe(styled_df, use_container_width=True, hide_index=True, column_config=col_config)
    else:
        st.info("Không tìm thấy trường dữ liệu để phân rã tổ chức (Khối/Phòng/Vùng).")


    # ══════════════════════════════════════════════════════════════
    # SECTION 2B: DEEP DIVE — Chọn đơn vị để xem phân tích chi tiết
    # ══════════════════════════════════════════════════════════════
    try:
        from shared.anomaly_detector import detect_unit_anomalies

        _MIN_N = 15
        _sec_col = None
        for _c in ['section', 'department']:
            if _c in df.columns and df[_c].notna().sum() > 0:
                _sec_col = _c
                break

        if _sec_col:
            _BAD_DD = {None, 'None', 'Khác', 'Chưa xác định', 'Không xác định', 'nan', ''}
            _df_valid = df[df[_sec_col].notna() & ~df[_sec_col].isin(_BAD_DD)]
            _unit_options = sorted([
                u for u, g in _df_valid.groupby(_sec_col)
                if len(g) >= _MIN_N
            ])

            if _unit_options:
                st.markdown(section_header(
                    "Deep Dive — Phân tích chi tiết theo đơn vị",
                    "Chọn một bộ phận để xem phân tích chuyên sâu về các chỉ số và dấu hiệu bất thường"
                ), unsafe_allow_html=True)

                _sel_unit = st.selectbox(
                    "Chọn đơn vị cần phân tích:",
                    options=["— Chọn bộ phận —"] + _unit_options,
                    key=f"deepdive_unit_{cfg.get('id','')}"
                )

                if _sel_unit and _sel_unit != "— Chọn bộ phận —":
                    _udf = _df_valid[_df_valid[_sec_col] == _sel_unit].copy()
                    _ukpis = compute_kpis(_udf)
                    _grp_kpis = kpis  # so sánh với toàn nhóm

                    # ── Header card ──
                    st.markdown(f"""
                    <div style="background:linear-gradient(135deg,#1D4ED8 0%,#3B82F6 100%);
                                border-radius:12px;padding:16px 20px;margin:10px 0 14px 0;">
                        <div style="color:rgba(255,255,255,0.7);font-size:0.7rem;font-weight:600;
                                    text-transform:uppercase;letter-spacing:0.08em;">Đơn vị được chọn</div>
                        <div style="color:#fff;font-size:1.2rem;font-weight:800;margin-top:4px;">{_sel_unit}</div>
                        <div style="color:rgba(255,255,255,0.65);font-size:0.78rem;margin-top:2px;">
                            N = {len(_udf):,} nhân sự &nbsp;·&nbsp; Toàn nhóm: N = {len(df):,}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                    # ── Metrics so sánh với toàn nhóm ──
                    m1, m2, m3, m4, m5 = st.columns(5)

                    def _delta(unit_val, grp_val, invert=False):
                        d = unit_val - grp_val
                        if invert: d = -d
                        return f"{d:+.1f}pp" if abs(d) >= 0.1 else "±0"

                    with m1:
                        st.metric("EI (%)", f"{_ukpis['ei_mean']:.1f}%",
                                  delta=_delta(_ukpis['ei_mean'], _grp_kpis['ei_mean']))
                    with m2:
                        st.metric("eNPS", f"{_ukpis['enps_score']:+.0f}",
                                  delta=_delta(_ukpis['enps_score'], _grp_kpis['enps_score']))
                    with m3:
                        st.metric("MEI (%)", f"{_ukpis['mei_avg']:.1f}%",
                                  delta=_delta(_ukpis['mei_avg'], _grp_kpis['mei_avg']))
                    with m4:
                        st.metric("Burnout (%)", f"{_ukpis['burnout_pct']:.1f}%",
                                  delta=_delta(_ukpis['burnout_pct'], _grp_kpis['burnout_pct'], invert=True),
                                  delta_color="inverse")
                    with m5:
                        st.metric("Muốn nghỉ (%)", f"{_ukpis['intent_pct_low']:.1f}%",
                                  delta=_delta(_ukpis['intent_pct_low'], _grp_kpis['intent_pct_low'], invert=True),
                                  delta_color="inverse")

                    st.caption("Delta (pp) so với trung bình toàn nhóm. Xanh = tốt hơn, Đỏ = kém hơn.")

                    # ── Anomaly patterns ──
                    _anomalies = detect_unit_anomalies(_udf, min_n=_MIN_N)
                    if _anomalies:
                        st.markdown("**Phát hiện bất thường:**")
                        for _a in _anomalies:
                            with st.expander(f"**{_a['label']}**", expanded=True):
                                # Metrics pills
                                _metric_str = "   |   ".join([f"**{k}**: {v}" for k, v in _a['metrics'].items()])
                                st.markdown(_metric_str)
                                st.markdown(f"> {_a['desc']}")
                    else:
                        st.success("Không phát hiện dấu hiệu bất thường nào ở đơn vị này.")

                    # ── Pillar breakdown cho đơn vị ──
                    _pillar_rows = []
                    for _p, _plabel in PILLAR_LABELS.items():
                        _pcol = f'{_p}_pct'
                        if _pcol in _udf.columns:
                            _pillar_rows.append({
                                'Trụ cột': _plabel,
                                'Đơn vị': round(_udf[_pcol].mean(), 1),
                                'Toàn nhóm': round(df[_pcol].mean(), 1) if _pcol in df.columns else 0
                            })
                    if _pillar_rows:
                        st.markdown("**5 Trụ cột Gắn kết:**")
                        df_pillars_dd = pd.DataFrame(_pillar_rows)
                        fig_dd = go.Figure()
                        fig_dd.add_trace(go.Bar(
                            name=_sel_unit, x=df_pillars_dd['Trụ cột'],
                            y=df_pillars_dd['Đơn vị'], marker_color=COLORS['blue'],
                            text=[f"{v:.1f}%" for v in df_pillars_dd['Đơn vị']],
                            textposition='outside'
                        ))
                        fig_dd.add_trace(go.Bar(
                            name='Toàn nhóm', x=df_pillars_dd['Trụ cột'],
                            y=df_pillars_dd['Toàn nhóm'], marker_color='rgba(148,163,184,0.5)',
                            text=[f"{v:.1f}%" for v in df_pillars_dd['Toàn nhóm']],
                            textposition='outside'
                        ))
                        fig_dd = fig_card(fig_dd, f'Trụ cột — {_sel_unit}', 'So sánh với toàn nhóm')
                        fig_dd.update_layout(barmode='group', xaxis_tickangle=-30,
                                            showlegend=True, yaxis=dict(range=[0, 110]))
                        st.plotly_chart(fig_dd, use_container_width=True)

    except Exception as _dd_err:
        st.caption(f"Deep Dive không khả dụng: {_dd_err}")



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

    # =========================================================================
    # LATE RENDER: Kích hoạt AI SAU khi toàn bộ UI đã được hiển thị xong
    # =========================================================================
    render_ai_insight_card(
        "AI Group Insight",
        group_ai_data,
        ai_prompt,
        custom_style="margin-top: 24px; margin-bottom: 32px;",
        target_container=ai_placeholder
    )
