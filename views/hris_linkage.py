import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
from utils.data_loader import load_hris, merge_survey_hris
from shared.plotly_theme import COLORS, PAL_CATEGORY, color_by_score
from utils.ai_generator import render_ai_insight_card
def render(df_clean, cfg, sel_group, pillar_filter=None, **kwargs):
    from shared.plotly_theme import section_header

    if sel_group != '1A':
        st.info(" Tính năng phân tích liên kết HRIS hiện tại chỉ hỗ trợ cho nhóm 1A.")
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

    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "Thu nhập × EI", "Phạt × EI", "Chiến binh", "Cấu trúc Thu nhập",
        " Năng suất × Nghỉ việc"
    ])

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
            st.plotly_chart(fig, width='stretch', key="hris_linkage_chart_49")
            st.dataframe(inc_stats, width='stretch')

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
            st.plotly_chart(fig, width='stretch', key="hris_linkage_chart_62")

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
                st.plotly_chart(fig, width='stretch', key="hris_linkage_chart_77")

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
            st.plotly_chart(fig, width='stretch', key="hris_linkage_chart_93")

    with tab5:
        _render_productivity_analysis(df_m, cfg)

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


def _render_productivity_analysis(df_m, cfg):
    """Phân tích Năng suất × Ý định Nghỉ việc (5 bước)."""
    import numpy as np
    from shared.plotly_theme import COLORS, make_html_kpi, color_by_score

    ns_giao_col = 'Năng suất Giao'
    ns_lay_col = 'Năng suất Lấy'
    ns_group_col = 'Phân loại Nhóm Năng Suất Giao'
    cb_col = 'Phân loại Chiến Binh'

    has_ns = ns_giao_col in df_m.columns and df_m[ns_giao_col].notna().sum() > 50
    if not has_ns:
        st.info("Không đủ dữ liệu năng suất từ HRIS.")
        return

    df = df_m[df_m[ns_giao_col].notna()].copy()
    cross = []   # will be populated in Bước 2
    hyp_data = []  # will be populated in Bước 3

    # Chuẩn hóa nhóm NS
    ns_order = ['1. <30 đơn - NS Giao Thấp',
                '2. Từ 30 đơn - 60 đơn - NS Giao Trung Bình',
                '3. Từ 60 đơn - 90 đơn - NS Giao Cao',
                '4. Từ 90 đơn trở lên - NS Giao Siêu Cao']
    ns_short = {'1. <30 đơn - NS Giao Thấp': '< 30 đơn\n(Thấp)',
                '2. Từ 30 đơn - 60 đơn - NS Giao Trung Bình': '30-60 đơn\n(TB)',
                '3. Từ 60 đơn - 90 đơn - NS Giao Cao': '60-90 đơn\n(Cao)',
                '4. Từ 90 đơn trở lên - NS Giao Siêu Cao': '≥ 90 đơn\n(Siêu Cao)'}
    ns_colors = {'< 30 đơn\n(Thấp)': '#EF4444', '30-60 đơn\n(TB)': '#F59E0B',
                 '60-90 đơn\n(Cao)': '#3B82F6', '≥ 90 đơn\n(Siêu Cao)': '#10B981'}

    if ns_group_col in df.columns:
        df['_ns_label'] = df[ns_group_col].map(ns_short).fillna('Khác')
    else:
        df['_ns_label'] = pd.cut(df[ns_giao_col], bins=[-1, 30, 60, 90, 999],
            labels=['< 30 đơn\n(Thấp)', '30-60 đơn\n(TB)', '60-90 đơn\n(Cao)', '≥ 90 đơn\n(Siêu Cao)'])

    ns_label_order = ['< 30 đơn\n(Thấp)', '30-60 đơn\n(TB)', '60-90 đơn\n(Cao)', '≥ 90 đơn\n(Siêu Cao)']

    # ════════════════════════════════════════════════════════════
    # BƯỚC 1: TỔNG QUAN NĂNG SUẤT
    # ════════════════════════════════════════════════════════════
    st.markdown("####  Bước 1: Tổng quan Năng suất")
    st.markdown("Phân bố năng suất giao hàng trung bình/ngày và phân loại Chiến Binh của toàn bộ nhân viên.")

    # KPI cards
    avg_giao = df[ns_giao_col].mean()
    avg_lay = df[ns_lay_col].mean() if ns_lay_col in df.columns else 0
    total_gl = df['Số đơn GL'].mean() if 'Số đơn GL' in df.columns else 0

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(make_html_kpi("NS Giao TB", f"{avg_giao:.0f} đơn/ngày", color="blue", icon=""), unsafe_allow_html=True)
    with c2:
        st.markdown(make_html_kpi("NS Lấy TB", f"{avg_lay:.0f} đơn/ngày", color="green", icon=""), unsafe_allow_html=True)
    with c3:
        st.markdown(make_html_kpi("Tổng đơn GL/tháng", f"{total_gl:,.0f}", color="orange", icon=""), unsafe_allow_html=True)

    col_hist, col_pie = st.columns([3, 2])

    with col_hist:
        fig_hist = go.Figure()
        fig_hist.add_trace(go.Histogram(
            x=df[ns_giao_col], nbinsx=40,
            marker_color='rgba(59, 130, 246, 0.7)',
            name='Năng suất Giao'
        ))
        # Add vertical lines for group boundaries
        for bnd, lbl in [(30, '<30: Thấp'), (60, '30-60: TB'), (90, '60-90: Cao')]:
            fig_hist.add_vline(x=bnd, line_dash='dash', line_color='#94A3B8',
                annotation_text=lbl, annotation_position='top')
        fig_hist.update_layout(
            height=360, title='Phân bố Năng suất Giao (đơn/ngày)',
            xaxis_title='Đơn/ngày', yaxis_title='Số NV',
            margin=dict(t=50, b=40)
        )
        st.plotly_chart(fig_hist, width='stretch', key="hris_linkage_chart_194")

    with col_pie:
        if cb_col in df.columns:
            cb_counts = df[cb_col].value_counts()
            fig_pie = go.Figure(go.Pie(
                labels=cb_counts.index, values=cb_counts.values,
                hole=0.4, textinfo='label+percent',
                marker=dict(colors=['#3B82F6', '#F59E0B', '#10B981']),
            ))
            fig_pie.update_layout(height=360, title='Phân loại Chiến Binh',
                margin=dict(t=50, b=20))
            st.plotly_chart(fig_pie, width='stretch', key="hris_linkage_chart_206")

    # Stacked bar: 4 nhóm NS
    ns_dist = df['_ns_label'].value_counts().reindex(ns_label_order).fillna(0)
    ns_pct = (ns_dist / ns_dist.sum() * 100).round(1)
    fig_stack = go.Figure()
    for k in ns_label_order:
        v = ns_pct.get(k, 0)
        n = int(ns_dist.get(k, 0))
        short_lbl = k.split(chr(10))[1] if chr(10) in k else k
        fig_stack.add_trace(go.Bar(
            x=[v], y=['NVGN'], orientation='h',
            marker_color=ns_colors.get(k, '#94A3B8'),
            text=[f"{short_lbl}: {v:.1f}% ({n})"],
            textposition='inside', showlegend=False,
        ))
    fig_stack.update_layout(height=100, margin=dict(t=10, b=10, l=60, r=10),
        xaxis=dict(visible=False), yaxis=dict(visible=False), barmode='stack',
        showlegend=False)
    st.plotly_chart(fig_stack, width='stretch', key="hris_linkage_chart_225")

    # ════════════════════════════════════════════════════════════
    # BƯỚC 2: NĂNG SUẤT × Ý ĐỊNH NGHỈ VIỆC
    # ════════════════════════════════════════════════════════════
    st.markdown("---")
    st.markdown("####  Bước 2: Năng suất × Ý định Nghỉ việc")
    st.markdown("**Nhân viên năng suất thấp có muốn nghỉ việc nhiều hơn không?** So sánh tỷ lệ muốn nghỉ và các chỉ số gắn kết theo nhóm năng suất.")

    if 'intent_risk' not in df.columns or df['intent_risk'].notna().sum() < 30:
        st.info("Không đủ dữ liệu Ý định nghỉ (Q30).")
    else:
        # Cross-tab: % muốn nghỉ theo nhóm NS
        cross = []
        for lbl in ns_label_order:
            grp = df[df['_ns_label'] == lbl]
            n = len(grp)
            if n < 10:
                continue
            n_quit = grp['intent_risk'].astype(str).str.contains('Muốn nghỉ').sum()
            n_stay = grp['intent_risk'].astype(str).str.contains('Gắn bó').sum()
            n_mid = grp['intent_risk'].astype(str).str.contains('Phân vân').sum()
            ei = grp['EI'].mean()
            mei = grp['MEI'].mean() if 'MEI' in grp.columns else None
            cross.append({
                'Nhóm NS': lbl, 'N': n,
                '% Muốn nghỉ': round(n_quit / n * 100, 1),
                '% Phân vân': round(n_mid / n * 100, 1),
                '% Gắn bó': round(n_stay / n * 100, 1),
                'EI': round(ei, 1) if pd.notna(ei) else None,
                'MEI': round(mei, 1) if pd.notna(mei) else None,
            })

        if cross:
            df_cross = pd.DataFrame(cross)

            # Insight box
            low_row = df_cross[df_cross['Nhóm NS'].str.contains('Thấp')]
            high_row = df_cross[df_cross['Nhóm NS'].str.contains('Cao') & ~df_cross['Nhóm NS'].str.contains('Siêu')]
            if not low_row.empty and not high_row.empty:
                q_low = low_row.iloc[0]['% Muốn nghỉ']
                q_high = high_row.iloc[0]['% Muốn nghỉ']
                ratio = q_low / q_high if q_high > 0 else 0
                st.markdown(f"""
<div style="background:#FEF2F2;border:1px solid #FECACA;border-left:4px solid #DC2626;border-radius:10px;padding:14px 18px;margin-bottom:20px;">
<span style="font-size:1.3rem;"></span> <strong style="color:#DC2626;">Phát hiện quan trọng:</strong>
Nhóm năng suất <strong>Thấp (< 30 đơn/ngày)</strong> có tỷ lệ muốn nghỉ <strong>{q_low:.1f}%</strong>,
gấp <strong>{ratio:.1f}x</strong> so với nhóm năng suất Cao (<strong>{q_high:.1f}%</strong>).
</div>""", unsafe_allow_html=True)

            # Grouped bar: % quit by NS group
            fig_quit = go.Figure()
            for col, color, name in [
                ('% Muốn nghỉ', '#EF4444', 'Muốn nghỉ'),
                ('% Phân vân', '#F59E0B', 'Phân vân'),
                ('% Gắn bó', '#10B981', 'Gắn bó'),
            ]:
                fig_quit.add_trace(go.Bar(
                    x=df_cross['Nhóm NS'], y=df_cross[col],
                    name=name, marker_color=color,
                    text=[f'{v:.1f}%' for v in df_cross[col]],
                    textposition='outside'
                ))
            fig_quit.update_layout(
                barmode='group', height=420,
                title='Ý ĐỊNH Ở LẠI THEO NHÓM NĂNG SUẤT GIAO',
                yaxis_title='%', margin=dict(t=50, b=40),
                legend=dict(orientation='h', y=1.08, x=0.5, xanchor='center'),
            )
            st.plotly_chart(fig_quit, width='stretch', key="hris_linkage_chart_294")

            # EI + MEI comparison
            col_ei, col_mei = st.columns(2)
            with col_ei:
                fig_ei = go.Figure(go.Bar(
                    x=df_cross['Nhóm NS'], y=df_cross['EI'],
                    marker_color=[color_by_score(v) for v in df_cross['EI']],
                    text=[f'{v:.1f}%' for v in df_cross['EI']],
                    textposition='outside',
                ))
                fig_ei.update_layout(height=350, title='EI THEO NHÓM NĂNG SUẤT',
                    yaxis_title='EI (%)', margin=dict(t=50, b=40))
                st.plotly_chart(fig_ei, width='stretch', key="hris_linkage_chart_307")

            with col_mei:
                if df_cross['MEI'].notna().any():
                    fig_mei = go.Figure(go.Bar(
                        x=df_cross['Nhóm NS'], y=df_cross['MEI'],
                        marker_color=[color_by_score(v) for v in df_cross['MEI'].fillna(0)],
                        text=[f'{v:.1f}%' if pd.notna(v) else '' for v in df_cross['MEI']],
                        textposition='outside',
                    ))
                    fig_mei.update_layout(height=350, title='MEI THEO NHÓM NĂNG SUẤT',
                        yaxis_title='MEI (%)', margin=dict(t=50, b=40))
                    st.plotly_chart(fig_mei, width='stretch', key="hris_linkage_chart_319")

    # ════════════════════════════════════════════════════════════
    # BƯỚC 3: ROOT CAUSE NĂNG SUẤT THẤP
    # ════════════════════════════════════════════════════════════
    st.markdown("---")
    st.markdown("####  Bước 3: Nguyên nhân Năng suất Thấp")
    st.markdown("""
Phân tích **5 giả thuyết** về nguyên nhân gốc rễ: Gán đơn thấp? Quản lý phân không công bằng?
Nhân viên mới chưa quen? Phạt nặng mất động lực? Hay tuyến đường khó?
""")

    df_low = df[df['_ns_label'] == '< 30 đơn\n(Thấp)']
    df_high = df[df['_ns_label'].isin(['60-90 đơn\n(Cao)', '≥ 90 đơn\n(Siêu Cao)'])]

    if len(df_low) < 10 or len(df_high) < 10:
        st.info("Không đủ mẫu NS Thấp / Cao để so sánh.")
    else:
        hyp_data = []

        # 1. Gán đơn thấp
        don_giao_col = 'Tổng Đơn giao'
        if don_giao_col in df.columns:
            low_don = df_low[don_giao_col].mean()
            high_don = df_high[don_giao_col].mean()
            gap_pct = (high_don - low_don) / high_don * 100 if high_don > 0 else 0
            hyp_data.append({
                'Giả thuyết': ' Gán đơn thấp',
                'NS Thấp': f'{low_don:,.0f} đơn/th',
                'NS Cao': f'{high_don:,.0f} đơn/th',
                'Chênh lệch': f'{gap_pct:.0f}%',
                'Đánh giá': 'Nghiêm trọng' if gap_pct > 40 else ('Đáng kể' if gap_pct > 20 else 'Nhỏ'),
            })

        # 2. Quản lý phân không công bằng (Q12 + Q24)
        for q, q_name in [('Q12', 'Phân đơn công bằng'), ('Q24', 'Phân đơn khu vực hợp lý')]:
            if q in df.columns:
                low_score = df_low[q].mean()
                high_score = df_high[q].mean()
                gap = high_score - low_score
                hyp_data.append({
                    'Giả thuyết': f'{q_name} ({q})',
                    'NS Thấp': f'{low_score:.2f}/5',
                    'NS Cao': f'{high_score:.2f}/5',
                    'Chênh lệch': f'{gap:+.2f}',
                    'Đánh giá': 'Nghiêm trọng' if gap > 0.8 else ('Đáng kể' if gap > 0.4 else 'Nhỏ'),
                })

        # 3. Thâm niên
        tn_col = 'Thâm niên (Đơn vị tính là tháng)'
        if tn_col in df.columns:
            low_tn = df_low[tn_col].mean()
            high_tn = df_high[tn_col].mean()
            hyp_data.append({
                'Giả thuyết': 'Thâm niên thấp',
                'NS Thấp': f'{low_tn:.1f} tháng',
                'NS Cao': f'{high_tn:.1f} tháng',
                'Chênh lệch': f'{high_tn - low_tn:.1f} tháng',
                'Đánh giá': 'Nghiêm trọng' if low_tn < 3 else ('Đáng kể' if low_tn < 6 else 'Nhỏ'),
            })

        # 4. Phạt nặng mất động lực
        if 'tong_phat' in df.columns:
            low_phat = df_low['tong_phat'].mean()
            high_phat = df_high['tong_phat'].mean()
            hyp_data.append({
                'Giả thuyết': ' Phạt nặng mất động lực',
                'NS Thấp': f'{low_phat:.2f} tr',
                'NS Cao': f'{high_phat:.2f} tr',
                'Chênh lệch': f'{low_phat - high_phat:+.2f} tr',
                'Đánh giá': 'Nghiêm trọng' if low_phat > high_phat * 1.5 else ('Đáng kể' if low_phat > high_phat * 1.2 else 'Nhỏ'),
            })

        if hyp_data:
            df_hyp = pd.DataFrame(hyp_data)
            st.dataframe(df_hyp, width='stretch', hide_index=True)

        # Scatter: Thâm niên × Năng suất
        col_scatter, col_box = st.columns(2)

        with col_scatter:
            if tn_col in df.columns:
                df_scatter = df[[tn_col, ns_giao_col, 'intent_risk']].dropna()
                if len(df_scatter) > 50:
                    fig_sc = px.scatter(
                        df_scatter, x=tn_col, y=ns_giao_col,
                        color='intent_risk',
                        color_discrete_map={
                            'Muốn nghỉ (1-2)': '#EF4444',
                            ' Phân vân (3)': '#F59E0B',
                            'Gắn bó (4-5)': '#10B981',
                        },
                        opacity=0.5,
                        title='THÂM NIÊN × NĂNG SUẤT GIAO',
                        labels={tn_col: 'Thâm niên (tháng)', ns_giao_col: 'Đơn/ngày'},
                    )
                    fig_sc.update_layout(height=400, margin=dict(t=50, b=40),
                        legend=dict(orientation='h', y=-0.15, x=0.5, xanchor='center'))
                    # Add trendline
                    try:
                        z = np.polyfit(df_scatter[tn_col].values, df_scatter[ns_giao_col].values, 2)
                        p = np.poly1d(z)
                        x_line = np.linspace(df_scatter[tn_col].min(), min(df_scatter[tn_col].max(), 60), 100)
                        fig_sc.add_trace(go.Scatter(x=x_line, y=p(x_line),
                            mode='lines', line=dict(color='#475569', width=2, dash='dash'),
                            name='Xu hướng', showlegend=True))
                    except:
                        pass
                    st.plotly_chart(fig_sc, width='stretch', key="hris_linkage_chart_427")

        with col_box:
            # Box plot: Q12 (Phân đơn công bằng) theo nhóm NS
            if 'Q12' in df.columns:
                fig_box = go.Figure()
                for lbl in ns_label_order:
                    grp_data = df[df['_ns_label'] == lbl]['Q12'].dropna()
                    if len(grp_data) > 5:
                        fig_box.add_trace(go.Box(
                            y=grp_data, name=lbl.replace('\n', ' '),
                            marker_color=ns_colors.get(lbl, '#94A3B8'),
                            boxmean=True,
                        ))
                fig_box.update_layout(
                    height=400, title='Q12: PHÂN ĐƠN CÔNG BẰNG<br><sup>Theo nhóm Năng suất</sup>',
                    yaxis_title='Điểm (1-5)', margin=dict(t=70, b=40),
                    showlegend=False,
                )
                st.plotly_chart(fig_box, width='stretch', key="hris_linkage_chart_446")

    # ════════════════════════════════════════════════════════════
    # BƯỚC 4: TÁC ĐỘNG TÀI CHÍNH
    # ════════════════════════════════════════════════════════════
    st.markdown("---")
    st.markdown("#### Bước 4: Tác động Tài chính theo Năng suất")

    if 'income_m' in df.columns:
        fin_data = []
        for lbl in ns_label_order:
            grp = df[df['_ns_label'] == lbl]
            if len(grp) < 10:
                continue
            fin_data.append({
                'Nhóm NS': lbl,
                'N': len(grp),
                'Thu nhập TB (tr)': grp['income_m'].mean(),
                'Đơn giao/th': grp['Tổng Đơn giao'].mean() if 'Tổng Đơn giao' in grp.columns else 0,
                'Phạt TB (tr)': grp['tong_phat'].mean() if 'tong_phat' in grp.columns else 0,
            })

        if fin_data:
            df_fin = pd.DataFrame(fin_data)

            fig_fin = make_subplots(specs=[[{'secondary_y': True}]])
            fig_fin.add_trace(go.Bar(
                x=df_fin['Nhóm NS'], y=df_fin['Thu nhập TB (tr)'],
                marker_color=[ns_colors.get(k, '#94A3B8') for k in df_fin['Nhóm NS']],
                text=[f'{v:.1f}tr' for v in df_fin['Thu nhập TB (tr)']],
                textposition='outside', name='Thu nhập (tr)',
            ), secondary_y=False)

            if df_fin['Phạt TB (tr)'].sum() > 0:
                fig_fin.add_trace(go.Scatter(
                    x=df_fin['Nhóm NS'], y=df_fin['Phạt TB (tr)'],
                    mode='lines+markers+text',
                    marker=dict(size=10, color='#DC2626'),
                    text=[f'{v:.2f}tr' for v in df_fin['Phạt TB (tr)']],
                    textposition='top center', name='Phạt TB (tr)',
                    line=dict(width=2, dash='dot'),
                ), secondary_y=True)

            fig_fin.update_yaxes(title_text='Thu nhập (triệu)', secondary_y=False)
            fig_fin.update_yaxes(title_text='Phạt (triệu)', secondary_y=True)
            fig_fin.update_layout(
                height=420, title='THU NHẬP VÀ PHẠT THEO NHÓM NĂNG SUẤT',
                margin=dict(t=50, b=40),
                legend=dict(orientation='h', y=1.08, x=0.5, xanchor='center'),
            )
            st.plotly_chart(fig_fin, width='stretch', key="hris_linkage_chart_496")

    # ════════════════════════════════════════════════════════════
    # BƯỚC 5: AI DEEP DIVE INSIGHT
    # ════════════════════════════════════════════════════════════
    st.markdown("---")
    st.markdown("####  Bước 5: AI Deep Dive — Năng suất × Nghỉ việc")

    ai_data = {
        "Total_with_HRIS": len(df),
        "Avg_NS_Giao": round(avg_giao, 1),
    }
    # Add cross-tab to AI
    if cross:
        ai_data['NS_x_Intent'] = cross
    # Add hypothesis results
    if hyp_data:
        ai_data['Root_Cause_Hypotheses'] = hyp_data

    prompt = f"""Phân tích chuyên sâu mối quan hệ giữa năng suất giao hàng và ý định nghỉ việc của Shipper.
Dữ liệu cho thấy nhóm năng suất thấp (<30 đơn/ngày) có tỷ lệ muốn nghỉ cao hơn rõ rệt.
Hãy phân tích:
1. Đây là quan hệ nhân-quả hay tương quan? (Năng suất thấp → muốn nghỉ, hay muốn nghỉ → năng suất thấp?)
2. Vai trò của quản lý trực tiếp (Q12: Phân đơn công bằng) trong việc tạo ra sự bất bình đẳng năng suất.
3. Vòng xoáy tiêu cực: NS thấp → thu nhập thấp → mất động lực → NS càng thấp.
4. Khuyến nghị can thiệp cụ thể cho HR: ưu tiên hỗ trợ nhóm nào, hành động gì.
"""
    render_ai_insight_card("AI Productivity Deep Dive", ai_data, prompt,
        badge="Deep Analysis", custom_style="margin-top: 16px; margin-bottom: 24px;")

