import streamlit as st
import plotly.express as px
import pandas as pd
from utils.data_loader import compute_kpis, PILLAR_LABELS
from shared.plotly_theme import COLORS, apply_theme, fig_card
from utils.ai_generator import render_ai_insight_card

def render(df, cfg):
    apply_theme()

    level = st.radio("Cấp độ", ['Division', 'Department', 'Section'], horizontal=True)
    col_map = {'Division': 'division', 'Department': 'department', 'Section': 'section'}
    grp_col = col_map[level]

    metrics = []
    for name, g in df.groupby(grp_col):
        kpi = compute_kpis(g)
        kpi['name'] = name
        metrics.append(kpi)
    df_met = pd.DataFrame(metrics).sort_values('ei_mean', ascending=False)

    tab1, tab2 = st.tabs(["Bảng tổng hợp", "Heatmap"])

    with tab1:
        metric = st.selectbox("Chỉ số", ['EI (%)', 'eNPS', 'MEI (%)', '% Muốn nghỉ', '% Burnout'])
        metric_map = {'EI (%)': 'ei_mean', 'eNPS': 'enps_score', 'MEI (%)': 'mei_avg',
                      '% Muốn nghỉ': 'intent_pct_low', '% Burnout': 'burnout_pct'}
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
            prompt = f"So sánh sự phân hóa giữa đơn vị dẫn đầu ({top_unit}) và đơn vị yếu kém nhất ({bot_unit}) theo chỉ số {metric}. Cảnh báo rủi ro cho đơn vị yếu kém."
            render_ai_insight_card("AI Drilldown Insight", ai_data, prompt, custom_style="margin-top: 16px; margin-bottom: 24px;")

        fig = px.bar(df_met_sorted, x='name', y=m_col, color=m_col,
                     color_continuous_scale='RdYlGn_r' if is_negative_metric else 'RdYlGn',
                     range_color=[max(0, df_met_sorted[m_col].min() - 5), df_met_sorted[m_col].max() + 5],
                     text=df_met_sorted[m_col].apply(lambda v: f'{v:.1f}'),
                     hover_data={'n': True})
        fig = fig_card(fig, f'{metric} theo {level}', f'Biểu đồ so sánh {metric} giữa các {level}')
        fig.update_traces(textposition='outside')
        fig.update_layout(height=500, xaxis_tickangle=-45, xaxis_title=level, yaxis_title=metric, showlegend=False, coloraxis_showscale=False)
        st.plotly_chart(fig, use_container_width=True)

        df_display = df_met[['name', 'n', 'ei_mean', 'enps_score', 'mei_avg', 'intent_pct_low', 'burnout_pct']].rename(
            columns={'name': level, 'n': 'N', 'ei_mean': 'EI (%)', 'enps_score': 'eNPS',
                     'mei_avg': 'MEI (%)', 'intent_pct_low': '% Muốn nghỉ', 'burnout_pct': '% Burnout'})
        
        styled_met = df_display.style.background_gradient(
            cmap='RdYlGn', subset=['EI (%)', 'eNPS', 'MEI (%)'], vmin=50, vmax=90
        ).format(precision=1)

        col_config = {
            level: st.column_config.TextColumn(level, help=f"Tên {level}", width="medium"),
            'N': st.column_config.NumberColumn('Mẫu (N)', format="%d", width="small"),
            'EI (%)': st.column_config.NumberColumn('EI (%)', format="%.1f%%", width="small"),
            'eNPS': st.column_config.NumberColumn('eNPS', format="%+d", width="small"),
            'MEI (%)': st.column_config.NumberColumn('MEI (%)', format="%.1f%%", width="small"),
            '% Muốn nghỉ': st.column_config.NumberColumn('% Muốn nghỉ', format="%.1f%%", width="small"),
            '% Burnout': st.column_config.NumberColumn('% Burnout', format="%.1f%%", width="small")
        }

        st.dataframe(styled_met, use_container_width=True, hide_index=True, column_config=col_config)

        import io
        buffer1 = io.BytesIO()
        with pd.ExcelWriter(buffer1, engine='xlsxwriter') as writer:
            df_display.to_excel(writer, index=False, sheet_name='Summary')
        
        st.download_button(
            label="📥 Tải báo cáo Bảng tổng hợp (Excel)",
            data=buffer1.getvalue(),
            file_name=f"EES_Drilldown_{level}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            key=f"export_tab1_{level}"
        )

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
            st.plotly_chart(fig, use_container_width=True)
            
            buffer2 = io.BytesIO()
            with pd.ExcelWriter(buffer2, engine='xlsxwriter') as writer:
                df_heat.reset_index().to_excel(writer, index=False, sheet_name='Heatmap')
            
            st.download_button(
                label="📥 Tải báo cáo Heatmap (Excel)",
                data=buffer2.getvalue(),
                file_name=f"EES_Heatmap_Section.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                key="export_tab2"
            )

