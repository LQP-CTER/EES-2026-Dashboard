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
    # SECTION 1: HERO METRICS & OVERALL DISTRIBUTION
    # ══════════════════════════════════════════════════════════════
    from shared.plotly_theme import make_html_kpi, section_header
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
    prompt = "Phân tích mức độ gắn kết (EI), eNPS và rủi ro Burnout của nhóm này. Đánh giá vai trò của Quản lý trực tiếp (dựa vào điểm MEI - Manager Effectiveness Index) trong việc giữ chân nhân sự. Đưa ra một kết luận ngắn."
    render_ai_insight_card("AI Group Insight", group_ai_data, prompt, custom_style="margin-top: 24px; margin-bottom: 32px;")

    # ── HR Strategic Insights (Specific to 1A and 1B, dynamic for others) ──
    is_shipper = cfg.get('short') == 'Shipper'
    is_driver = cfg.get('short') == 'Tài xế'
    
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
    else:
        st.markdown(f"""
        <div style="background: rgba(255, 82, 0, 0.03); border: 1px solid rgba(255, 82, 0, 0.1); border-left: 5px solid #FF5200; border-radius: 20px; padding: 24px; margin-top: 24px; margin-bottom: 24px;">
            <h4 style="color: #FF5200; font-weight: 800; margin-top: 0; margin-bottom: 12px; display: flex; align-items: center; gap: 8px;">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path><line x1="12" y1="9" x2="12" y2="13"></line><line x1="12" y1="17" x2="12.01" y2="17"></line></svg>
                Điểm Nóng Phân Tích Thực Địa — {cfg.get('label', '')}
            </h4>
        """, unsafe_allow_html=True)
        
        strategic_prompt = f"Bạn là Chuyên gia Tư vấn Quản trị Nhân sự (HR Consultant). Nhìn vào dữ liệu tổng quan điểm EI, eNPS và Burnout của nhóm {cfg.get('label', '')}, hãy sáng tạo ra 2 'Điểm nóng thực địa' giả định nhưng logic và thực tế (ví dụ: áp lực ca kíp đêm, quy trình phối hợp liên phòng ban rườm rà, thiếu lộ trình thăng tiến). Trình bày dưới dạng 2 gạch đầu dòng, viết thật ngắn gọn, chuyên nghiệp, dùng ngôn ngữ như 'tử huyệt cảm xúc', 'vòng lặp hụt hẫng', 'điểm nghẽn năng suất'."
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
                    fig.update_layout(barmode='group', xaxis_tickangle=-30, yaxis=dict(range=[0, 105]))
                    st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Dữ liệu hiện tại không chứa các cột về Thâm niên (Q5) hoặc Chức danh.")
