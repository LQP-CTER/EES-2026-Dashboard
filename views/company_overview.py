import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from utils.data_loader import compute_kpis, PILLAR_LABELS
from shared.plotly_theme import fig_card, apply_theme, COLORS
from utils.benchmark_2025 import get_company_benchmark_2025
from utils.ai_generator import render_ai_insight_card

def render(all_data, available_groups):
    if not all_data:
        st.error("Không tìm thấy dữ liệu nào.")
        return

    apply_theme()

    all_dfs = []
    total_n_before = 0
    for df, n_before in all_data.values():
        all_dfs.append(df)
        total_n_before += n_before

    df_total = pd.concat(all_dfs, ignore_index=True)
    total_kpis = compute_kpis(df_total)
    total_n = total_kpis['n']
    total_ei = total_kpis['ei_mean']
    total_enps = total_kpis['enps_score']
    total_intent = total_kpis['intent_pct_low']

    try:
        from shared.workforce_mapper import load_workforce_and_mapping
        df_wf, _, _ = load_workforce_and_mapping()
        total_headcount = len(df_wf) if not df_wf.empty else 21353
    except Exception:
        total_headcount = 21353

    # Tổng số phản hồi hợp lệ sau làm sạch ở cấp công ty
    total_participants = total_n
    total_rr = round((total_participants / total_headcount) * 100, 1) if total_headcount > 0 else 0
    bm = get_company_benchmark_2025()
    ei_delta = total_ei - bm['ei_mean']
    enps_delta = total_enps - bm['enps_score']
    rr_delta = total_rr - bm['response_rate']

    st.markdown('''
    <style>
    .overview-hero {
        background: linear-gradient(135deg, #0A1F44 0%, #14345E 55%, #1B4A7A 100%);
        color: white;
        border-radius: 20px;
        padding: 28px 30px;
        margin-bottom: 24px;
        position: relative;
        overflow: hidden;
        box-shadow: 0 18px 40px rgba(10,31,68,0.16);
    }
    .overview-hero::after {
        content: '';
        position: absolute;
        inset: auto -120px -140px auto;
        width: 320px;
        height: 320px;
        border-radius: 50%;
        background: radial-gradient(circle, rgba(255,82,0,0.3) 0%, transparent 70%);
        filter: blur(18px);
        pointer-events: none;
    }
    .overview-kpi-grid {
        display: grid;
        grid-template-columns: repeat(4, minmax(0, 1fr));
        gap: 14px;
        margin-top: 18px;
    }
    .overview-kpi {
        background: rgba(255,255,255,0.08);
        border: 1px solid rgba(255,255,255,0.12);
        border-radius: 14px;
        padding: 16px 18px;
        backdrop-filter: blur(8px);
    }
    .overview-kpi .label { font-size: 0.7rem; text-transform: uppercase; letter-spacing: .08em; color: #BFDBFE; font-weight: 700; }
    .overview-kpi .value { font-size: 2rem; font-weight: 900; line-height: 1; margin-top: 10px; }
    .overview-kpi .sub { font-size: 0.8rem; color: #DBEAFE; margin-top: 8px; }
    .overview-section { margin-top: 24px; }
    .background-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
        gap: 14px;
    }
    .bg-card {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 16px;
        padding: 18px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.04);
        min-height: 140px;
    }
    .bg-card h4 { margin: 0 0 8px; font-size: 0.92rem; color: #0A1F44; }
    .bg-card p { margin: 0; color: #64748B; font-size: 0.84rem; line-height: 1.7; }
    .bg-chip {
        display:inline-flex;align-items:center;padding:4px 10px;border-radius:999px;
        background:#FFF3EE;color:#FF5200;font-size:0.72rem;font-weight:700;margin-bottom:10px;
    }
    .cov-container { display:flex; gap:0; background:#FFFFFF; border:1px solid #E2E8F0; border-radius:14px; box-shadow:0 1px 3px rgba(0,0,0,0.04); margin-bottom:28px; overflow:hidden; }
    .cov-card { flex:1; padding:24px 28px; position:relative; }
    .cov-card + .cov-card { border-left:1px solid #F1F5F9; }
    .cov-label { font-size:0.68rem; font-weight:700; text-transform:uppercase; letter-spacing:0.1em; color:#94A3B8; margin-bottom:10px; }
    .cov-value { font-size:2.4rem; font-weight:800; line-height:1; letter-spacing:-0.03em; margin-bottom:8px; }
    .cov-sub { font-size:0.8rem; color:#64748B; font-weight:500; line-height:1.5; }
    .cov-progress-track { width:100%; height:6px; background:#F1F5F9; border-radius:3px; margin-top:12px; overflow:hidden; }
    .cov-progress-fill { height:100%; border-radius:3px; transition:width 0.5s ease; }
    .cov-badge { display:inline-flex; align-items:center; gap:5px; padding:3px 10px; border-radius:20px; font-size:0.72rem; font-weight:700; }
    .cov-badge-dot { width:6px; height:6px; border-radius:50%; display:inline-block; }
    </style>
    ''', unsafe_allow_html=True)

    st.markdown(f'''
    <div class="overview-hero">
        <div style="position:relative; z-index:2;">
            <div style="font-size:0.72rem; letter-spacing:0.16em; text-transform:uppercase; color:#BFDBFE; font-weight:800;">EES 2026 · Executive Overview</div>
            <h2 style="margin:10px 0 8px; font-size:2rem; line-height:1.15; font-weight:900; color:white;">Bức tranh tổng quan EES 2026</h2>
            <p style="margin:0; max-width:860px; color:#DBEAFE; line-height:1.75; font-size:0.92rem;">
                Trang này là một mặt phẳng truyền thông nội bộ dành cho team EX: kể lại team đã làm gì cho EES 2026,
                cách team biến dữ liệu thành câu chuyện điều hành, và các lớp phân tích chéo đã được dựng lên cho toàn công ty.
            </p>
            <div class="overview-kpi-grid">
                <div class="overview-kpi"><div class="label">Nhân sự</div><div class="value">{total_headcount:,}</div><div class="sub">Quy mô toàn tổ chức</div></div>
                <div class="overview-kpi"><div class="label">Phản hồi</div><div class="value">{total_participants:,}</div><div class="sub">Mẫu khảo sát hợp lệ</div></div>
                <div class="overview-kpi"><div class="label">Tỷ lệ phản hồi</div><div class="value">{total_rr:.1f}%</div><div class="sub">Phản hồi hợp lệ / Headcount</div></div>
                <div class="overview-kpi"><div class="label">Mức gắn kết</div><div class="value">{total_ei:.1f}</div><div class="sub">EI tổng thể · {ei_delta:+.1f} so với 2025</div></div>
            </div>
        </div>
    </div>

    <div class="overview-section">
        <div class="background-grid">
            <div class="bg-card"><div class="bg-chip">Phân tích chéo</div><h4>Cross-check theo nhiều lớp</h4><p>Đọc đồng thời theo phòng ban, thâm niên, khối, và trụ cột để tránh kết luận từ một lát cắt đơn lẻ.</p></div>
            <div class="bg-card"><div class="bg-chip">Chiến lược</div><h4>Executive narrative</h4><p>Không chỉ hiển thị số liệu, mà còn gom thành câu chuyện điều hành: tín hiệu chính, rủi ro và ưu tiên hành động.</p></div>
            <div class="bg-card"><div class="bg-chip">Nội dung sắp fill</div><h4>Roadmap & team contributions</h4><p>Khu vực này sẽ dùng để ghi lại team đã làm gì cho EES 2026, ai phụ trách phần nào và các deliverable quan trọng.</p></div>
            <div class="bg-card"><div class="bg-chip">Tối ưu</div><h4>Nhanh hơn & gọn hơn</h4><p>Dữ liệu đang được cache theo nhóm để giảm thời gian tải và giúp dashboard phản hồi nhanh hơn.</p></div>
        </div>
    </div>
    ''', unsafe_allow_html=True)

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    st.markdown(f'''
    <div class="cov-container">
        <div class="cov-card"><div class="cov-label">Tổng nhân sự</div><div class="cov-value" style="color:#0A1F44;">{total_headcount:,}</div><div class="cov-sub">Headcount toàn tổ chức GHN</div></div>
        <div class="cov-card"><div class="cov-label">Đã tham gia khảo sát</div><div class="cov-value" style="color:#006FAD;">{total_participants:,}</div><div class="cov-sub"><span class="cov-badge" style="background:#EFF6FF;color:#1D4ED8;border:1px solid #BFDBFE;"><span class="cov-badge-dot" style="background:#3B82F6;"></span>{total_rr}% tỷ lệ phản hồi</span></div><div class="cov-progress-track"><div class="cov-progress-fill" style="width: {min(total_rr, 100):.1f}%; background: linear-gradient(90deg, #3B82F6, #006FAD);"></div></div></div>
        <div class="cov-card"><div class="cov-label">Chưa tham gia</div><div class="cov-value" style="color:#94A3B8;">{max(total_headcount - total_participants, 0):,}</div><div class="cov-sub"><span class="cov-badge" style="background:#F8FAFC;color:#64748B;border:1px solid #E2E8F0;"><span class="cov-badge-dot" style="background:#CBD5E1;"></span>{max(round((1 - total_participants / total_headcount) * 100, 1), 0):.1f}% chưa phản hồi</span></div><div class="cov-progress-track"><div class="cov-progress-fill" style="width: {min(max(round((1 - total_participants / total_headcount) * 100, 1), 0), 100):.1f}%; background: #E2E8F0;"></div></div></div>
    </div>
    ''', unsafe_allow_html=True)

    # Executive company overview section
    from shared.plotly_theme import make_html_kpi
    kpi_c1, kpi_c2, kpi_c3, kpi_c4 = st.columns(4)
    with kpi_c1:
        st.markdown(make_html_kpi("Engagement Index", f"{total_ei:.1f}", delta=f"{ei_delta:+.1f}", color="blue", icon="", progress_val=total_ei), unsafe_allow_html=True)
    with kpi_c2:
        st.markdown(make_html_kpi("eNPS Score", f"{total_enps:+.0f}", delta=f"{enps_delta:+.0f}", color="orange", icon="", progress_val=(total_enps+100)/2), unsafe_allow_html=True)
    with kpi_c3:
        st.markdown(make_html_kpi("Attrition Risk", f"{total_intent:.1f}%", delta="N/A", color="red", icon="", progress_val=total_intent), unsafe_allow_html=True)
    with kpi_c4:
        st.markdown(make_html_kpi("Response Rate", f"{total_rr:.1f}%", delta=f"{rr_delta:+.1f}%", color="green", icon="", progress_val=total_rr), unsafe_allow_html=True)

    # Calculate dynamic insights across divisions
    div_stats = []
    for div, df_div in df_total.groupby('division'):
        if len(df_div) < 10: continue
        kpis = compute_kpis(df_div)
        kpis['division'] = div
        div_stats.append(kpis)
    df_div_stats = pd.DataFrame(div_stats)

    if not df_div_stats.empty:
        top_div = df_div_stats.loc[df_div_stats['ei_mean'].idxmax()]
        bot_div = df_div_stats.loc[df_div_stats['ei_mean'].idxmin()]
        
        pillar_scores = {p: df_total[f'{p}_pct'].mean() for p in PILLAR_LABELS.keys() if f'{p}_pct' in df_total.columns}
        if pillar_scores:
            top_pillar_key = max(pillar_scores, key=pillar_scores.get)
            bot_pillar_key = min(pillar_scores, key=pillar_scores.get)
            top_pillar_name = PILLAR_LABELS[top_pillar_key]
            bot_pillar_name = PILLAR_LABELS[bot_pillar_key]
        else:
            top_pillar_name = bot_pillar_name = "N/A"

        ai_data = {
            "Total_EI": round(total_ei, 1),
            "Total_eNPS": round(total_enps, 0),
            "EI_Delta_YoY": round(ei_delta, 1),
            "Top_Division": top_div['division'],
            "Top_Division_EI": round(top_div['ei_mean'], 1),
            "Top_Pillar": top_pillar_name,
            "Bottom_Division": bot_div['division'],
            "Bottom_Division_EI": round(bot_div['ei_mean'], 1),
            "Bottom_Pillar": bot_pillar_name,
            "Total_Attrition_Risk": round(total_intent, 1)
        }
        
        prompt = (
            f"Viết một đoạn Tóm tắt Điều hành (Executive Summary) DỰA CHÍNH XÁC vào các chỉ số sau "
            f"(KHÔNG bịa thêm chỉ số nào khác):\n"
            f"- EI tổng = {ai_data['Total_EI']}% (thay đổi {ai_data['EI_Delta_YoY']:+.1f} so với 2025)\n"
            f"- eNPS tổng = {ai_data['Total_eNPS']:+.0f}\n"
            f"- Rủi ro nghỉ việc (Attrition Risk) = {ai_data['Total_Attrition_Risk']:.1f}%\n"
            f"- Division xuất sắc nhất: {ai_data['Top_Division']} (EI {ai_data['Top_Division_EI']:.1f}%)\n"
            f"- Division yếu nhất: {ai_data['Bottom_Division']} (EI {ai_data['Bottom_Division_EI']:.1f}%)\n"
            f"- Trụ cột mạnh nhất hệ thống: {ai_data['Top_Pillar']}\n"
            f"- Trụ cột yếu nhất hệ thống: {ai_data['Bottom_Pillar']}\n\n"
            f"Yêu cầu: (1) Phân tích ý nghĩa của sự thay đổi EI/eNPS. "
            f"(2) Đánh giá khoảng cách giữa Division dẫn đầu và Division chót bảng. "
            f"(3) Đề xuất 1 chiến lược cải thiện cấp bách dựa trên Gartner Human Deal cho Division yếu nhất. "
            f"CHỈ dùng đúng các con số đã liệt kê, KHÔNG tự suy diễn thêm."
        )
        
        render_ai_insight_card("AI Executive Summary & Insight", ai_data, prompt)

    # ══════════════════════════════════════════════════════════════
    # SECTION 2: ORG DRILLDOWN (KHỐI / DIVISION)
    # ══════════════════════════════════════════════════════════════
    from shared.plotly_theme import section_header
    st.markdown(section_header("Phân Tích Cấp Tổ Chức", "Mức độ gắn kết và sức khỏe tổ chức theo Khối / Division"), unsafe_allow_html=True)
    
    if not df_div_stats.empty:
        df_div_stats = df_div_stats.sort_values('ei_mean', ascending=True)
        
        c1, c2 = st.columns([1, 1])
        with c1:
            fig_bar = go.Figure(go.Bar(
                y=df_div_stats['division'], x=df_div_stats['ei_mean'],
                orientation='h', marker_color=COLORS['blue'],
                text=[f'{v:.1f}%' for v in df_div_stats['ei_mean']],
                textposition='inside'
            ))
            fig_bar = fig_card(fig_bar, 'EI theo Khối / Division', 'Mức độ gắn kết trung bình')
            fig_bar.update_layout(xaxis=dict(range=[0, 100], showgrid=True))
            st.plotly_chart(fig_bar, width='stretch', key="company_overview_chart_250")
            
        with c2:
            # Heatmap of pillars by division
            hm_data = []
            for div, df_div in df_total.groupby('division'):
                if len(df_div) < 10: continue
                row = {'division': div}
                for p, plabel in PILLAR_LABELS.items():
                    col = f'{p}_pct'
                    if col in df_div.columns:
                        row[plabel] = df_div[col].mean()
                hm_data.append(row)
            df_hm = pd.DataFrame(hm_data).set_index('division')
            
            fig_hm = go.Figure(data=go.Heatmap(
                z=df_hm.values,
                x=df_hm.columns,
                y=df_hm.index,
                colorscale='RdYlGn',
                zmin=50, zmax=90,
                text=df_hm.round(1).values,
                texttemplate="%{text}",
                showscale=False
            ))
            fig_hm = fig_card(fig_hm, 'Heatmap 5 Trụ Cột theo Khối', 'Phân bổ sức khỏe tổ chức')
            st.plotly_chart(fig_hm, width='stretch', key="company_overview_chart_276")
            
        # --- AI Insight for Division ---
        if len(df_div_stats) > 1:
            top_div = df_div_stats.iloc[-1]['division']
            bot_div = df_div_stats.iloc[0]['division']
            lowest_pillar = df_hm.mean().idxmin()
            
            org_ai_data = {
                "Top_Division": top_div,
                "Top_EI": round(df_div_stats.iloc[-1]['ei_mean'], 1),
                "Bottom_Division": bot_div,
                "Bottom_EI": round(df_div_stats.iloc[0]['ei_mean'], 1),
                "Lowest_System_Pillar": lowest_pillar
            }
            prompt = (
                f"Phân tích khoảng cách sức khỏe tổ chức DỰA VÀO CÁC CON SỐ SAU "
                f"(KHÔNG đề cập đến chỉ số nào khác):\n"
                f"- Khối dẫn đầu: {org_ai_data['Top_Division']} (EI = {org_ai_data['Top_EI']:.1f}%)\n"
                f"- Khối đứng chót: {org_ai_data['Bottom_Division']} (EI = {org_ai_data['Bottom_EI']:.1f}%)\n"
                f"- Trụ cột thấp nhất toàn hệ thống: {org_ai_data['Lowest_System_Pillar']}\n\n"
                f"Yêu cầu: (1) Lượng hóa khoảng cách EI giữa 2 khối. "
                f"(2) Phát cảnh báo 'Pillar Alert' cho trụ cột yếu nhất, giải thích TẠI SAO nó thấp. "
                f"(3) Đề xuất chiến lược xuyên suốt thay vì giải quyết cục bộ. "
                f"CHỈ dùng đúng 3 dữ kiện trên."
            )
            render_ai_insight_card("AI Organization Insight", org_ai_data, prompt, custom_style="margin-top: 24px; padding: 20px;")

    # ══════════════════════════════════════════════════════════════
    # SECTION 3: DEMOGRAPHICS (THÂM NIÊN & CẤP BẬC)
    # ══════════════════════════════════════════════════════════════
    st.markdown(section_header("Phân Tích Nhân Khẩu Học", "Phân mảnh mức độ gắn kết theo Thâm niên và Cấp bậc"), unsafe_allow_html=True)
    
    # Define demographic groups from Q5 if 'Q5' exists
    demographics_cols = []
    if 'Q5' in df_total.columns:
        demographics_cols.append(('Q5', 'Thâm niên'))
    
    if demographics_cols:
        for idx, (col, title) in enumerate(demographics_cols):
            # Compute stats by this col
            demo_stats = []
            for val, df_sub in df_total.groupby(col):
                if len(df_sub) < 5: continue
                kpis = compute_kpis(df_sub)
                kpis['group'] = val
                demo_stats.append(kpis)
            
            if demo_stats:
                df_demo = pd.DataFrame(demo_stats)
                if col == 'Q5':
                    order = [
                        'Dưới 1 tháng', 'Trên 1 đến 3 tháng', 'Trên 3 đến 6 tháng',
                        'Trên 6 đến 9 tháng', 'Trên 9 đến 12 tháng', 'Trên 1 đến 2 năm',
                        'Trên 2 đến 3 năm', 'Trên 3 đến 5 năm', 'Trên 5 năm', 'Khác'
                    ]
                    # Append any unknown J or other categories to the end
                    existing = df_demo['group'].tolist()
                    for g in existing:
                        if g not in order: order.append(g)
                    df_demo['group_cat'] = pd.Categorical(df_demo['group'], categories=order, ordered=True)
                    df_demo = df_demo.sort_values('group_cat')
                else:
                    df_demo = df_demo.sort_values('n', ascending=False)
                    
                fig_demo = go.Figure()
                fig_demo.add_trace(go.Bar(
                    y=df_demo['group'], x=df_demo['ei_mean'], name='EI', orientation='h',
                    marker_color=COLORS['blue'], text=[f'{v:.1f}%' for v in df_demo['ei_mean']], textposition='outside'
                ))
                fig_demo.add_trace(go.Bar(
                    y=df_demo['group'], x=df_demo['enps_score'], name='eNPS', orientation='h',
                    marker_color=COLORS['green'], text=[f'{v:+.0f}' for v in df_demo['enps_score']], textposition='outside'
                ))
                fig_demo.update_layout(
                    barmode='group',
                    yaxis={'autorange': 'reversed'}
                )
                fig_demo = fig_card(fig_demo, f'EI & eNPS theo {title}', 'Phân mảnh sự gắn kết')
                
                st.plotly_chart(fig_demo, width='stretch', key="company_overview_chart_346")
                
                # --- AI Insight for Demographics ---
                if len(df_demo) > 1:
                    top_group = df_demo.iloc[0]['group']
                    bot_group = df_demo.iloc[-1]['group']
                    demo_ai_data = {
                        "Highest_Engagement_Group": top_group,
                        "Top_EI": round(df_demo.iloc[0]['ei_mean'], 1),
                        "Lowest_Engagement_Group": bot_group,
                        "Bottom_EI": round(df_demo.iloc[-1]['ei_mean'], 1)
                    }
                    prompt = (
                        f"Dựa trên phân mảnh nhân khẩu học, phân tích DỰA VÀO CÁC CON SỐ SAU "
                        f"(KHÔNG bịa thêm chỉ số):\n"
                        f"- Nhóm gắn kết CAO nhất: {demo_ai_data['Highest_Engagement_Group']} (EI = {demo_ai_data['Top_EI']:.1f}%)\n"
                        f"- Nhóm gắn kết THẤP nhất: {demo_ai_data['Lowest_Engagement_Group']} (EI = {demo_ai_data['Bottom_EI']:.1f}%)\n\n"
                        f"Yêu cầu: (1) Giải thích khoảng cách EI giữa 2 nhóm. "
                        f"(2) Đưa ra góc nhìn Employee Life-cycle: tại sao nhóm thấp lại ở giai đoạn 'kỳ vọng không được đáp ứng' (honeymoon phase)? "
                        f"(3) Đề xuất 1 cách can thiệp giữ chân cụ thể. "
                        f"CHỈ phân tích từ 2 con số EI đã cho."
                    )
                    render_ai_insight_card("AI Demographic Insight", demo_ai_data, prompt, custom_style="margin-top: 16px; padding: 20px;")

    else:
        st.info("Chưa có dữ liệu Nhân khẩu học trong các nhóm hiện tại.")

    # ══════════════════════════════════════════════════════════════
    # SECTION 4: EVP & NLP INSIGHTS
    # ══════════════════════════════════════════════════════════════
    st.markdown(section_header("EVP & Lắng Nghe Nhân Viên (NLP)", "Phân tích từ khóa từ câu hỏi mở — định vị Thương hiệu Tuyển dụng"), unsafe_allow_html=True)
    
    # Collect all NLP clean responses
    open_responses = []
    for c in df_total.columns:
        if c.endswith('_clean') and 'Q' in c:
            open_responses.extend(df_total[c].dropna().tolist())
            
    if open_responses:
        # Simple extraction of common words (simulating EVP model)
        from collections import Counter
        import re
        all_text = " ".join(open_responses).lower()
        words = re.findall(r'\b[a-z_àáãạảăẵẳâầấậẫẩđèéẹẻẽêềếệểễìíịỉĩòóọỏõôồốộổỗơờớợởỡùúụủũưừứựửữỳýỵỷỹ]{3,}\b', all_text)
        
        # Define some key EVP buckets manually for GHN context
        evp_buckets = {
            'Lương thưởng & Phụ cấp': ['lương', 'thưởng', 'thu nhập', 'phụ cấp', 'xăng', 'tiền', 'đơn giá', 'truy thu'],
            'Công việc & Môi trường': ['công việc', 'ổn định', 'môi trường', 'thoải mái', 'áp lực', 'bụi', 'thời gian'],
            'Quản lý & Hỗ trợ': ['quản lý', 'sếp', 'hỗ trợ', 'tbc', 'tận tâm', 'giúp đỡ', 'hoà đồng'],
            'Công nghệ & Quy trình': ['app', 'ứng dụng', 'lỗi', 'quy trình', 'chậm', 'thao tác', 'điện thoại']
        }
        
        evp_counts = {k: 0 for k in evp_buckets.keys()}
        for w in words:
            for k, keywords in evp_buckets.items():
                if w in keywords:
                    evp_counts[k] += 1
                    
        df_evp = pd.DataFrame(list(evp_counts.items()), columns=['EVP_Factor', 'Mentions']).sort_values('Mentions', ascending=True)
        
        c_evp1, c_evp2 = st.columns([1, 1.2])
        with c_evp1:
            fig_evp = go.Figure(go.Bar(
                y=df_evp['EVP_Factor'], x=df_evp['Mentions'],
                orientation='h', marker_color=COLORS['blue'],
                text=df_evp['Mentions'], textposition='inside'
            ))
            fig_evp = fig_card(fig_evp, 'Từ khóa EVP nổi bật', 'Tần suất được nhắc đến trong câu hỏi mở')
            st.plotly_chart(fig_evp, width='stretch', key="company_overview_chart_406")
            
        with c_evp2:
            df_evp_ai = df_evp[df_evp['Mentions'] > 0]
            if df_evp_ai.empty:
                st.info("Chưa có đủ từ khóa để phân tích sâu.")
            else:
                nlp_ai_data = {
                    "EVP_Buckets_Frequencies": df_evp_ai.set_index('EVP_Factor')['Mentions'].to_dict(),
                    "Top_Bucket": df_evp_ai.iloc[-1]['EVP_Factor'],
                    "Bottom_Bucket_with_mentions": df_evp_ai.iloc[0]['EVP_Factor']
                }
                prompt = (
                    f"Phân tích dữ liệu đếm từ khóa EVP từ câu hỏi mở của nhân viên. "
                    f"Dữ liệu thực tế:\n"
                    f"{nlp_ai_data['EVP_Buckets_Frequencies']}\n\n"
                    f"YÊU CẦU NGHIÊM NGẶT:\n"
                    f"- CHỈ phân tích các yếu tố CÓ mentions > 0 trong dữ liệu trên.\n"
                    f"- TUYỆT ĐỐI KHÔNG nhắc đến, ám chỉ, hoặc suy diễn về các yếu tố có 0 mentions.\n"
                    f"- Nêu bật yếu tố được nhắc nhiều nhất (điểm mạnh EVP) và yếu tố ít được nhắc nhất (rủi ro tiềm ẩn).\n"
                    f"- Mọi con số trích dẫn PHẢI khớp với dữ liệu đã cho."
                )
                render_ai_insight_card("AI NLP Insight: Định Vị Thương Hiệu (EVP)", nlp_ai_data, prompt, badge="NLP Engine", custom_style="height: 100%; margin-bottom: 0; padding: 24px;")
    else:
        st.info("Chưa có dữ liệu câu hỏi mở (NLP) để phân tích EVP.")


