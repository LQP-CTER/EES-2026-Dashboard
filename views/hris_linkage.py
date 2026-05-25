import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
from utils.data_loader import load_hris, merge_survey_hris
from shared.plotly_theme import COLORS, PAL_CATEGORY, color_by_score
from utils.ai_generator import render_ai_insight_card
def render(df_clean, cfg, sel_group):
    from shared.plotly_theme import section_header

    if sel_group != '1A':
        st.info("💡 Tính năng phân tích liên kết HRIS hiện tại chỉ hỗ trợ cho nhóm 1A.")
        return

    df_hris, month_label = load_hris()
    if df_hris is None:
        st.info(f"Nhóm {sel_group} hiện chưa có dữ liệu HRIS.")
        return

    df_m = merge_survey_hris(df_clean, df_hris)
    n_matched = df_m['Lương thực nhận'].notna().sum() if 'Lương thực nhận' in df_m.columns else 0
    st.success(f"Khớp HRIS: {n_matched:,} / {len(df_m):,} | Dữ liệu tháng: {month_label}")
    if n_matched < 50:
        st.warning("Không đủ mẫu để phân tích.")
        return

    tab1, tab2, tab3, tab4 = st.tabs(["Thu nhập × EI", "Phạt × EI", "Chiến binh", "Cấu trúc Thu nhập"])

    with tab1:
        if 'income_group' in df_m.columns:
            inc_stats = df_m.groupby('income_group', observed=True).agg(
                N=('EI', 'count'), EI=('EI', 'mean'),
                eNPS=('eNPS', lambda x: ((x>=9).sum()-(x<=6).sum())/x.notna().sum()*100 if x.notna().sum()>0 else 0),
            ).round(1)
            fig = make_subplots(specs=[[{'secondary_y': True}]])
            fig.add_trace(go.Bar(x=inc_stats.index.astype(str), y=inc_stats['EI'],
                marker_color=[color_by_score(v) for v in inc_stats['EI']],
                text=[f'{v:.1f}%' for v in inc_stats['EI']], textposition='outside', name='EI'), secondary_y=False)
            fig.add_trace(go.Scatter(x=inc_stats.index.astype(str), y=inc_stats['eNPS'],
                mode='lines+markers+text', marker=dict(size=10, color=COLORS['orange']),
                text=[f'{v:+.0f}' for v in inc_stats['eNPS']], textposition='top center',
                name='eNPS', line=dict(width=3)), secondary_y=True)
            fig.update_yaxes(title_text='EI (%)', secondary_y=False)
            fig.update_yaxes(title_text='eNPS', secondary_y=True)
            fig.update_layout(height=450, title='THU NHẬP × GẮN KẾT')
            st.plotly_chart(fig, width='stretch')
            st.dataframe(inc_stats, use_container_width=True)

    with tab2:
        if 'tong_phat' in df_m.columns:
            df_m['phat_group'] = pd.cut(df_m['tong_phat'], bins=[-1, 0, 0.5, 1, 3, 200],
                labels=['Không phạt', '< 500K', '500K-1tr', '1-3tr', '> 3tr'])
            phat_stats = df_m.groupby('phat_group', observed=True).agg(N=('EI','count'), EI=('EI','mean')).round(1)
            fig = go.Figure(go.Bar(x=phat_stats.index.astype(str), y=phat_stats['EI'],
                marker_color=[color_by_score(v) for v in phat_stats['EI']],
                text=[f'{v:.1f}%\n(n={n})' for v, n in zip(phat_stats['EI'], phat_stats['N'])],
                textposition='outside'))
            fig.update_layout(height=420, title='MỨC PHẠT × GẮN KẾT')
            st.plotly_chart(fig, width='stretch')

    with tab3:
        cb_col = 'Phân loại Chiến Binh '
        if cb_col in df_m.columns:
            cb_stats = df_m.groupby(cb_col, observed=True).agg(
                N=('EI','count'), EI=('EI','mean'), Income=('income_m','mean')).round(1)
            cb_stats = cb_stats[cb_stats['N'] >= 10].sort_values('EI', ascending=False)
            if len(cb_stats) > 0:
                fig = px.bar(cb_stats.reset_index(), x=cb_col, y='EI',
                    color='EI', color_continuous_scale='RdYlGn', range_color=[40, 90],
                    text='EI', hover_data={'N': True, 'Income': ':.1f'},
                    title='CHIẾN BINH × GẮN KẾT')
                fig.update_traces(textposition='outside', texttemplate='%{text:.1f}%')
                fig.update_layout(height=420)
                st.plotly_chart(fig, width='stretch')

    with tab4:
        structure_cols = {'Lương đơn hàng': 'Đơn hàng', 'Thưởng/ Phạt GTC và LTC': 'Thưởng GTC/LTC',
                          'Phụ cấp': 'Phụ cấp', 'Thưởng Doanh Thu': 'Thưởng DT'}
        avg_struct = {}
        for col, label in structure_cols.items():
            if col in df_m.columns:
                v = df_m[col].dropna().mean()
                if v > 0: avg_struct[label] = v / 1_000_000
        if avg_struct:
            total = sum(avg_struct.values())
            fig = go.Figure(go.Pie(labels=list(avg_struct.keys()), values=list(avg_struct.values()),
                hole=0.45, textinfo='label+percent', marker=dict(colors=PAL_CATEGORY[:len(avg_struct)])))
            fig.update_layout(height=400, title=f'CẤU TRÚC THU NHẬP TB ({total:.1f} triệu/tháng)',
                annotations=[dict(text=f'{total:.1f}tr', x=0.5, y=0.5, font_size=18, showarrow=False)])
            st.plotly_chart(fig, width='stretch')

    # --- AI Insight for HRIS ---
    hris_ai_data = {
        "N_matched": int(n_matched),
        "Total_Sample": len(df_m)
    }
    if 'income_group' in df_m.columns:
        try:
            hris_ai_data['Income_vs_EI'] = df_m.groupby('income_group', observed=True)['EI'].mean().to_dict()
        except:
            pass
    if 'phat_group' in df_m.columns:
        try:
            hris_ai_data['Penalty_vs_EI'] = df_m.groupby('phat_group', observed=True)['EI'].mean().to_dict()
        except:
            pass

    prompt = "Phân tích mối tương quan giữa thu nhập thực nhận (HRIS) và mức độ gắn kết (EI), cũng như ảnh hưởng của các khoản phạt đến tâm lý nhân viên. Đề xuất góc nhìn về chính sách đãi ngộ Total Rewards."
    render_ai_insight_card("AI HRIS & Thu nhập Insight", hris_ai_data, prompt, custom_style="margin-top: 32px; margin-bottom: 24px;")
