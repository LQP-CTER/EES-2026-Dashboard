import streamlit as st
import plotly.express as px
import pandas as pd
from utils.data_loader import compute_kpis, PILLAR_LABELS
from utils.segment_risk import MIN_SEGMENT_N, build_segment_driver_profile, scan_risk_segments
from shared.plotly_theme import COLORS, apply_theme, fig_card
from utils.ai_generator import render_ai_insight_card

@st.fragment
def render(df, cfg, group_id=None, pillar_filter=None):
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

    st.markdown("#### Segment Risk Scan")
    risk_df = scan_risk_segments(df, pillar_filter=pillar_filter, min_n=MIN_SEGMENT_N, top_n=20)
    if risk_df.empty:
        st.info("Chưa có segment nào đủ mẫu để scan rủi ro. Dashboard chỉ ẩn segment có N < 5.")
    else:
        st.caption("Chỉ ẩn segment có N < 5. Segment nhỏ từ 5-29 nên đọc như tín hiệu định hướng, không kết luận tuyệt đối.")
        risk_cols = [
            'Segment Type', 'Segment', 'N', 'Risk Level', 'Risk Score',
            'EI (%)', '% Muốn nghỉ', '% Burnout', 'eNPS', 'Primary Driver'
        ]
        if pillar_filter and f'Điểm {pillar_filter} (%)' in risk_df.columns:
            risk_cols.insert(6, f'Điểm {pillar_filter} (%)')
        risk_cols = [c for c in risk_cols if c in risk_df.columns]

        def _risk_style(row):
            level = row.get('Risk Level')
            if level == 'Critical':
                bg = '#FEF2F2'
                color = '#B91C1C'
            elif level == 'Warning':
                bg = '#FFF7ED'
                color = '#C2410C'
            else:
                bg = '#F8FAFC'
                color = '#475569'
            return [f'background-color:{bg};color:{color};font-weight:700' if c == 'Risk Level' else '' for c in row.index]

        st.dataframe(
            risk_df[risk_cols].style.apply(_risk_style, axis=1).format(precision=1),
            width='stretch',
            hide_index=True,
            column_config={
                'Segment Type': st.column_config.TextColumn('Loại segment', width='small'),
                'Segment': st.column_config.TextColumn('Segment', width='medium'),
                'N': st.column_config.NumberColumn('N', format='%d', width='small'),
                'Risk Level': st.column_config.TextColumn('Mức rủi ro', width='small'),
                'Risk Score': st.column_config.NumberColumn('Risk Score', format='%.1f', width='small'),
                'EI (%)': st.column_config.NumberColumn('EI (%)', format='%.1f%%', width='small'),
                '% Muốn nghỉ': st.column_config.NumberColumn('% Muốn nghỉ', format='%.1f%%', width='small'),
                '% Burnout': st.column_config.NumberColumn('% Burnout', format='%.1f%%', width='small'),
                'eNPS': st.column_config.NumberColumn('eNPS', format='%+d', width='small'),
                'Primary Driver': st.column_config.TextColumn('Driver chính', width='medium'),
            }
        )

        group_id = group_id or cfg.get('group_id') or cfg.get('id') or '1A'
        option_map = {
            f"{row['Segment Type']} · {row['Segment']} · {row['Risk Level']} · N={int(row['N'])}": idx
            for idx, row in risk_df.iterrows()
        }
        selected_label = st.selectbox(
            "Chọn segment để xem driver",
            list(option_map.keys()),
            index=0,
            key=f"segment_driver_{pillar_filter or 'all'}",
        )
        selected = risk_df.iloc[option_map[selected_label]]
        profile = build_segment_driver_profile(
            df,
            group_id,
            selected['_segment_col'],
            selected['_segment_value'],
            min_n=MIN_SEGMENT_N,
        )
        if profile.get("enabled"):
            pillar_df = profile.get("pillar_df", pd.DataFrame())
            question_df = profile.get("question_df", pd.DataFrame())
            lowest_pillar = pillar_df.iloc[0] if not pillar_df.empty else None
            weakest_q = question_df.iloc[0] if not question_df.empty else None

            c1, c2, c3 = st.columns(3)
            with c1:
                st.metric("Segment đang xem", selected['Segment'], f"N={int(selected['N'])}")
            with c2:
                st.metric(
                    "Trụ cột yếu nhất",
                    lowest_pillar['Trụ cột'] if lowest_pillar is not None else "N/A",
                    f"{lowest_pillar['Điểm segment']:.1f}%" if lowest_pillar is not None else None,
                )
            with c3:
                st.metric(
                    "Câu yếu nhất",
                    weakest_q['Câu hỏi'] if weakest_q is not None else "N/A",
                    f"{weakest_q['Điểm TB']:.2f}/5" if weakest_q is not None else None,
                )

            left, right = st.columns([1.05, 1.25])
            with left:
                if not pillar_df.empty:
                    fig_driver = px.bar(
                        pillar_df.sort_values("Điểm segment", ascending=True),
                        x="Điểm segment",
                        y="Trụ cột",
                        orientation="h",
                        color="Điểm segment",
                        color_continuous_scale="RdYlGn",
                        range_color=[40, 90],
                        text="Điểm segment",
                        hover_data=["Điểm toàn nhóm", "Chênh lệch"],
                    )
                    fig_driver = fig_card(
                        fig_driver,
                        "Driver theo trụ cột",
                        "Trụ cột thấp nhất là nơi nên đào sâu trước",
                    )
                    fig_driver.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
                    fig_driver.update_layout(height=320, xaxis_title="Điểm (%)", yaxis_title=None, coloraxis_showscale=False)
                    st.plotly_chart(fig_driver, width='stretch', key=f"segment_driver_pillar_{pillar_filter or 'all'}")
            with right:
                if not question_df.empty:
                    q_show = question_df.head(8)[[
                        "Trụ cột", "Câu hỏi", "Nhãn", "Điểm TB", "% Tích cực", "% Tiêu cực", "Chênh toàn nhóm", "N"
                    ]]
                    st.dataframe(
                        q_show.style.format({
                            "Điểm TB": "{:.2f}",
                            "% Tích cực": "{:.1f}%",
                            "% Tiêu cực": "{:.1f}%",
                            "Chênh toàn nhóm": "{:+.2f}",
                            "N": "{:,}",
                        }),
                        width='stretch',
                        hide_index=True,
                        height=320,
                    )
            voice = profile.get("voice_signals", {})
            if voice.get("enabled"):
                st.markdown("##### Tín hiệu open-text của segment")
                v1, v2, v3 = st.columns(3)
                with v1:
                    st.metric("Phản hồi mở có nội dung", f"{voice.get('text_n', 0):,}")
                with v2:
                    st.metric("NLP tiêu cực", f"{voice.get('negative_pct', 0):.1f}%", f"{voice.get('negative_n', 0):,} phản hồi")
                with v3:
                    st.metric("Warning signals", f"{voice.get('warning_n', 0):,}")

                topic_rows = []
                for label, count in (voice.get("top_topics") or {}).items():
                    topic_rows.append({"Loại": "Topic", "Tín hiệu": label, "Số lần": count})
                for label, count in (voice.get("top_warnings") or {}).items():
                    topic_rows.append({"Loại": "Warning", "Tín hiệu": label, "Số lần": count})
                if topic_rows:
                    st.dataframe(
                        pd.DataFrame(topic_rows),
                        width='stretch',
                        hide_index=True,
                        height=210,
                    )

            driver = selected.get("Primary Driver", "")
            action_map = {
                "Muốn nghỉ cao": "Ưu tiên phỏng vấn giữ chân nhóm mẫu 10-15 người trong segment này; hỏi rõ điểm nghẽn trong 30 ngày gần nhất và owner xử lý.",
                "Burnout cao": "Kiểm tra tải công việc, lịch/ca và hỗ trợ trực tiếp; giảm áp lực vận hành ngắn hạn trước khi mở chương trình dài hạn.",
                "eNPS âm": "Dùng phản hồi mở để gom 3 nguyên nhân bất mãn chính; tránh truyền thông rộng trước khi xử lý vấn đề cụ thể.",
                "Điểm trụ cột thấp": "Đi thẳng vào trụ cột yếu nhất và top câu hỏi yếu; chọn 1 hành động cấp quản lý có thể hoàn tất trong 2-4 tuần.",
                "EI thấp": "Chạy pulse check ngắn theo segment này, sau đó so sánh với nhóm cùng cấp để xác định đây là vấn đề cục bộ hay hệ thống.",
            }
            st.markdown(f"""
            <div style="background:#F8FAFC;border:1px solid #E2E8F0;border-left:4px solid #0A1F44;border-radius:12px;padding:14px 16px;margin-top:14px;">
                <div style="font-size:.72rem;font-weight:900;color:#64748B;text-transform:uppercase;letter-spacing:.09em;margin-bottom:6px;">Next action</div>
                <div style="font-size:.9rem;color:#0A1F44;font-weight:800;margin-bottom:4px;">Driver chính: {driver}</div>
                <div style="font-size:.82rem;color:#475569;line-height:1.65;">{action_map.get(driver, action_map["EI thấp"])}</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.info("Segment được chọn không đủ N >= 5 để dựng driver profile.")

    st.markdown("<hr style='border:1px dashed rgba(0,0,0,0.08);margin:22px 0;'>", unsafe_allow_html=True)

    level = st.radio("Cấp độ phân tích", ['Division', 'Department', 'Section'], horizontal=True)
    col_map = {'Division': 'division', 'Department': 'department', 'Section': 'section'}
    grp_col = col_map[level]

    metrics = []
    for name, g in df.groupby(grp_col):
        if len(g) < MIN_SEGMENT_N:
            continue
        kpi = compute_kpis(g)
        kpi['name'] = name
        if pillar_filter and f"{pillar_filter}_pct" in g.columns:
            kpi[f'{pillar_filter} (%)'] = g[f"{pillar_filter}_pct"].mean()
        metrics.append(kpi)
    df_met = pd.DataFrame(metrics).sort_values('ei_mean', ascending=False) if metrics else pd.DataFrame()

    tab1, tab2 = st.tabs(["Bảng tổng hợp", "Heatmap"])

    with tab1:
        if df_met.empty:
            st.info("Không có nhóm nào đủ N >= 5 để phân tích ở cấp độ này.")
            return

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
        st.plotly_chart(fig, width='stretch', key=f"view_b_seg_bar_{group_id or 'all'}_{pillar_filter or 'all'}")

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
            if len(g) < MIN_SEGMENT_N:
                continue
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
            st.plotly_chart(fig, width='stretch', key=f"view_b_heatmap_{group_id or 'all'}_{pillar_filter or 'all'}")
            
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
            render_ai_insight_card("AI Heatmap Analysis", ai_data_heat, prompt_heat)
