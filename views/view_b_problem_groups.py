import streamlit as st
import plotly.express as px
import pandas as pd
from utils.data_loader import compute_kpis, PILLAR_LABELS
from shared.plotly_theme import COLORS, apply_theme, fig_card
from utils.ai_generator import render_ai_insight_card

def render(df, cfg, pillar_filter=None):
    apply_theme()

    from utils.anomaly_detector import detect_cross_pillar
    from views.anomaly_cards import render_anomaly_tab
    
    cross_anomalies = detect_cross_pillar(df, cfg.get('short', ''))
    if cross_anomalies:
        st.markdown("<h4 style='color: #0A1F44; margin-top: 10px;'>Phân tích Mẫu Nguy hiểm (Cross-Pillar)</h4>", unsafe_allow_html=True)
        render_anomaly_tab(cross_anomalies, pillar_id=None, show_cross=True)
        st.markdown("<hr style='border: 1px dashed rgba(0,0,0,0.1); margin: 24px 0;'>", unsafe_allow_html=True)

    st.markdown("""
    <div style="background:#EFF6FF;border:1px solid #BFDBFE;border-radius:12px;padding:16px 20px;margin-bottom:18px;">
        <div>
            <div style="font-size:0.82rem;font-weight:700;color:#1D4ED8;margin-bottom:4px;">Xác định đơn vị nào đang gặp vấn đề</div>
            <div style="font-size:0.8rem;color:#475569;line-height:1.55;">
                Chọn cấp độ <strong>Division → Department → Section</strong> để thu hẹp dần vào đơn vị cụ thể.
                Màu <span style="color:#DC2626;font-weight:700;">đỏ/cam</span> = điểm thấp, cần chú ý.
                Màu <span style="color:#15803D;font-weight:700;">xanh</span> = điểm tốt.
                Dùng biểu đồ này để trả lời: <em>"Vấn đề là toàn hệ thống hay chỉ ở một bộ phận cụ thể?"</em>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    level = st.radio("Cấp độ phân tích", ['Division', 'Department', 'Section'], horizontal=True)
    col_map = {'Division': 'division', 'Department': 'department', 'Section': 'section'}
    grp_col = col_map[level]

    metrics = []
    for name, g in df.groupby(grp_col):
        kpi = compute_kpis(g)
        kpi['name'] = name
        if pillar_filter and f"{pillar_filter}_pct" in g.columns:
            kpi[f'{pillar_filter} (%)'] = g[f"{pillar_filter}_pct"].mean()
        metrics.append(kpi)
    df_met = pd.DataFrame(metrics).sort_values('ei_mean', ascending=False)

    tab1, tab2 = st.tabs(["Bảng tổng hợp", "Heatmap"])

    with tab1:
        metric_opts = ['EI (%)', 'eNPS', 'MEI (%)', '% Muốn nghỉ', '% Burnout']
        metric_map = {'EI (%)': 'ei_mean', 'eNPS': 'enps_score', 'MEI (%)': 'mei_avg',
                      '% Muốn nghỉ': 'intent_pct_low', '% Burnout': 'burnout_pct'}
                      
        default_index = 0
        if pillar_filter and f'{pillar_filter} (%)' in df_met.columns:
            pillar_met_name = f'Điểm {pillar_filter} (%)'
            metric_opts.insert(0, pillar_met_name)
            metric_map[pillar_met_name] = f'{pillar_filter} (%)'

        metric = st.selectbox("Chỉ số", metric_opts, index=default_index)
        m_col = metric_map[metric]
        
        # Sort based on selected metric for correct insight
        is_negative_metric = metric in ['% Muốn nghỉ', '% Burnout']
        df_met_sorted = df_met.sort_values(m_col, ascending=is_negative_metric)

        if not df_met_sorted.empty:
            top_unit = df_met_sorted.iloc[0]['name']
            top_score = df_met_sorted.iloc[0][m_col]
            bot_unit = df_met_sorted.iloc[-1]['name']
            bot_score = df_met_sorted.iloc[-1][m_col]
            
            ai_data = {
                "Level": level,
                "Metric": metric,
                "Top_Unit": top_unit,
                "Top_Score": round(top_score, 1),
                "Bottom_Unit": bot_unit,
                "Bottom_Score": round(bot_score, 1)
            }
            prompt = (
                f"So sánh sự phân hóa DỰA VÀO DỮ LIỆU SAU (KHÔNG bịa thêm):\n"
                f"- Đơn vị dẫn đầu: {top_unit} ({metric} = {top_score:.1f})\n"
                f"- Đơn vị yếu nhất: {bot_unit} ({metric} = {bot_score:.1f})\n"
                f"Phân tích: (1) Khoảng cách này có ý nghĩa gì? (2) Rủi ro cho đơn vị yếu kém. "
                f"CHỈ dùng 2 con số đã cho."
            )
            render_ai_insight_card("AI Drilldown Insight", ai_data, prompt, custom_style="margin-top: 16px; margin-bottom: 24px;")

        fig = px.bar(df_met_sorted, x='name', y=m_col, color=m_col,
                     color_continuous_scale='RdYlGn_r' if is_negative_metric else 'RdYlGn',
                     range_color=[max(0, df_met_sorted[m_col].min() - 5), df_met_sorted[m_col].max() + 5],
                     text=df_met_sorted[m_col].apply(lambda v: f'{v:.1f}'),
                     hover_data={'n': True})
        fig = fig_card(fig, f'{metric} theo {level}', f'Biểu đồ so sánh {metric} giữa các {level}')
        fig.update_traces(textposition='outside')
        fig.update_layout(height=500, xaxis_tickangle=-45, xaxis_title=level, yaxis_title=metric, showlegend=False, coloraxis_showscale=False)
        st.plotly_chart(fig, width='stretch', key="view_b_problem_groups_chart_91")

        df_display_cols = ['name', 'n', 'ei_mean', 'enps_score', 'mei_avg', 'intent_pct_low', 'burnout_pct']
        rename_dict = {'name': level, 'n': 'N', 'ei_mean': 'EI (%)', 'enps_score': 'eNPS',
                     'mei_avg': 'MEI (%)', 'intent_pct_low': '% Muốn nghỉ', 'burnout_pct': '% Burnout'}
        
        if pillar_filter and f'{pillar_filter} (%)' in df_met.columns:
            df_display_cols.insert(2, f'{pillar_filter} (%)')

        df_display = df_met[df_display_cols].rename(columns=rename_dict)
        
        styled_met = (
            df_display.style
            .background_gradient(cmap='RdYlGn', subset=['EI (%)', 'MEI (%)'], vmin=50, vmax=90)
            .background_gradient(cmap='RdYlGn', subset=['eNPS'], vmin=-50, vmax=50)
            .background_gradient(cmap='RdYlGn_r', subset=['% Muốn nghỉ', '% Burnout'], vmin=0, vmax=30)
            .format(precision=1)
        )

        col_config = {
            level: st.column_config.TextColumn(level, help=f"Tên {level}", width="medium"),
            'N': st.column_config.NumberColumn('Mẫu (N)', format="%d", width="small"),
            'EI (%)': st.column_config.NumberColumn('EI (%)', format="%.1f%%", width="small"),
            'eNPS': st.column_config.NumberColumn('eNPS', format="%+d", width="small"),
            'MEI (%)': st.column_config.NumberColumn('MEI (%)', format="%.1f%%", width="small"),
            '% Muốn nghỉ': st.column_config.NumberColumn('% Muốn nghỉ', format="%.1f%%", width="small"),
            '% Burnout': st.column_config.NumberColumn('% Burnout', format="%.1f%%", width="small")
        }
        
        if pillar_filter:
            col_config[f'{pillar_filter} (%)'] = st.column_config.NumberColumn(f'Điểm {pillar_filter}', format="%.1f%%", width="small")

        st.dataframe(styled_met, width='stretch', hide_index=True, column_config=col_config)



    with tab2:
        heat_data = []
        for sec, g in df.groupby('section'):
            row = {'Section': sec}
            for p, label in PILLAR_LABELS.items():
                col = f'{p}_pct'
                if col in g.columns:
                    row[label] = round(g[col].mean(), 1)
            heat_data.append(row)
        df_heat = pd.DataFrame(heat_data).set_index('Section')
        if len(df_heat) > 0:
            fig = px.imshow(df_heat, color_continuous_scale='RdYlGn', aspect='auto', text_auto='.1f')
            fig = fig_card(fig, 'HEATMAP: Section × Trụ cột EI', 'Đánh giá điểm mạnh/yếu của từng đơn vị')
            fig.update_layout(height=max(400, len(df_heat) * 25 + 150))
            st.plotly_chart(fig, width='stretch', key="view_b_problem_groups_chart_141")
            
            ai_data_heat = {
                "Dimensions": list(df_heat.columns),
                "Sample_Count": len(df_heat)
            }
            prompt_heat = (
                f"DỰA VÀO Heatmap với {ai_data_heat['Sample_Count']} đơn vị và các khía cạnh: "
                f"{ai_data_heat['Dimensions']} (KHÔNG bịa thêm dữ liệu):\n"
                f"Phân tích: (1) Rủi ro khi một đơn vị có điểm thấp ở nhiều cột liên tiếp. "
                f"(2) Khuyến nghị hành động cho quản lý cấp cao."
            )
            render_ai_insight_card("AI Heatmap Analysis", ai_data_heat, prompt_heat, custom_style="margin-top: 16px; margin-bottom: 24px;")
            
