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

    # ══════════════════════════════════════════════════════════════
    # AGGREGATE DATA
    # ══════════════════════════════════════════════════════════════
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
    total_rr = round(total_n / total_n_before * 100, 1) if total_n_before > 0 else 0

    # Load 2025 Benchmark
    bm = get_company_benchmark_2025()
    ei_delta = total_ei - bm['ei_mean']
    enps_delta = total_enps - bm['enps_score']
    rr_delta = total_rr - bm['response_rate']

    def fmt_delta(val, is_pct=False):
        sign = "+" if val >= 0 else ""
        unit = "%" if is_pct else ""
        cls = "delta-positive" if val >= 0 else "delta-negative"
        return f'<span class="metric-delta {cls}">{sign}{val:.1f}{unit} YoY</span>'

    def fmt_sparkline(val, delta, color="#006FAD"):
        from shared.plotly_theme import generate_trend_data
        data = generate_trend_data(val, delta)
        if not data: return ""
        min_val, max_val = min(data), max(data)
        range_val = max_val - min_val if max_val != min_val else 1
        width, height = 120, 24
        points = []
        for i, v in enumerate(data):
            x = (i / (len(data) - 1)) * width
            y = height - ((v - min_val) / range_val) * height
            points.append(f"{x},{y}")
        pts_str = " ".join(points)
        return f"""<div style="margin-top: 12px; margin-bottom: -5px; width: 100%; height: {height+10}px;">
<svg width="100%" height="100%" viewBox="0 -5 {width} {height+10}" preserveAspectRatio="none">
<defs>
<linearGradient id="grad_{color.replace('#','')}" x1="0%" y1="0%" x2="0%" y2="100%">
<stop offset="0%" stop-color="{color}" stop-opacity="0.2" />
<stop offset="100%" stop-color="{color}" stop-opacity="0" />
</linearGradient>
</defs>
<polygon fill="url(#grad_{color.replace('#','')})" points="0,{height} {pts_str} {width},{height}" />
<polyline fill="none" stroke="{color}" stroke-width="2.5" points="{pts_str}" stroke-linecap="round" stroke-linejoin="round"/>
<circle cx="{points[-1].split(',')[0]}" cy="{points[-1].split(',')[1]}" r="3.5" fill="{color}" />
</svg>
</div>"""

    # ══════════════════════════════════════════════════════════════
    # SECTION 1: EXECUTIVE SUMMARY & DYNAMIC INSIGHTS
    # ══════════════════════════════════════════════════════════════
    st.markdown(f"""<div class="hero-card">
<p class="hero-title">
<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="12 2 2 7 12 12 22 7 12 2"></polygon><polyline points="2 17 12 22 22 17"></polyline><polyline points="2 12 12 17 22 12"></polyline></svg>
Executive Summary - GHN EES 2026
</p>
<p class="hero-subtitle">Báo cáo Mức độ Gắn kết Nhân viên Toàn Hệ thống • {total_n:,} respondents • Q1/2026</p>
<div class="hero-metrics">
<div class="hero-metric-box">
<span class="hero-metric-label">Engagement Index</span>
<span class="hero-metric-value">{total_ei:.1f}</span>
{fmt_sparkline(total_ei, ei_delta, color="#006FAD")}
{fmt_delta(ei_delta, is_pct=False)}
</div>
<div class="hero-metric-box">
<span class="hero-metric-label">eNPS</span>
<span class="hero-metric-value">{total_enps:+.0f}</span>
{fmt_sparkline(total_enps, enps_delta, color="#FF5200")}
{fmt_delta(enps_delta, is_pct=False)}
</div>
<div class="hero-metric-box">
<span class="hero-metric-label">Attrition Risk</span>
<span class="hero-metric-value">{total_intent:.1f}%</span>
{fmt_sparkline(total_intent, 0, color="#C0392B")}
<span class="metric-delta delta-neutral">N/A YoY</span>
</div>
<div class="hero-metric-box">
<span class="hero-metric-label">Response Rate</span>
<span class="hero-metric-value">{total_rr:.1f}%</span>
{fmt_sparkline(total_rr, rr_delta, color="#0D6E3A")}
{fmt_delta(rr_delta, is_pct=True)}
</div>
</div>
</div>""", unsafe_allow_html=True)

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
        
        prompt = "Hãy viết một đoạn Tóm tắt Điều hành (Executive Summary). Phân tích sự tăng giảm của EI và eNPS. Đánh giá nhóm (Division) xuất sắc nhất và nhóm yếu kém nhất. Đề xuất một chiến lược cải thiện cấp bách (Strategic Recommendation) dựa trên Gartner Human Deal cho nhóm yếu kém nhất."
        
        render_ai_insight_card("AI Executive Summary & Insight", ai_data, prompt)

    # ══════════════════════════════════════════════════════════════
    # SECTION 2: ORG DRILLDOWN (KHỐI / DIVISION)
    # ══════════════════════════════════════════════════════════════
    st.markdown('<h3 style="margin-top:2rem; font-weight:800; color:#0A1F44;">1. Phân Tích Cấp Tổ Chức (Division)</h3>', unsafe_allow_html=True)
    
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
            st.plotly_chart(fig_bar, use_container_width=True)
            
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
            st.plotly_chart(fig_hm, use_container_width=True)
            
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
            prompt = "Phân tích khoảng cách sức khỏe tổ chức giữa Khối dẫn đầu và Khối đứng chót. Phát đi cảnh báo 'Pillar Alert' cho trụ cột có điểm số thấp nhất toàn hệ thống, yêu cầu một chiến lược xuyên suốt thay vì giải quyết cục bộ."
            render_ai_insight_card("AI Organization Insight", org_ai_data, prompt, custom_style="margin-top: 24px; padding: 20px;")

    # ══════════════════════════════════════════════════════════════
    # SECTION 3: DEMOGRAPHICS (THÂM NIÊN & CẤP BẬC)
    # ══════════════════════════════════════════════════════════════
    st.markdown('<h3 style="margin-top:2rem; font-weight:800; color:#0A1F44;">2. Phân Tích Nhân Khẩu Học (Demographics)</h3>', unsafe_allow_html=True)
    
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
                        'Trên 2 đến 3 năm', 'Trên 3 đến 5 năm', 'Trên 5 năm', 'Chưa xác định'
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
                    marker_color=COLORS['navy'], text=[f'{v:.1f}%' for v in df_demo['ei_mean']], textposition='outside'
                ))
                fig_demo.add_trace(go.Bar(
                    y=df_demo['group'], x=df_demo['enps_score'], name='eNPS', orientation='h',
                    marker_color=COLORS['orange'], text=[f'{v:+.0f}' for v in df_demo['enps_score']], textposition='outside'
                ))
                fig_demo.update_layout(
                    barmode='group',
                    yaxis={'autorange': 'reversed'}
                )
                fig_demo = fig_card(fig_demo, f'EI & eNPS theo {title}', 'Phân mảnh sự gắn kết')
                
                st.plotly_chart(fig_demo, use_container_width=True)
                
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
                    prompt = "Dựa trên phân mảnh nhân khẩu học, hãy bình luận về nhóm có mức gắn kết cao nhất và thấp nhất. Đưa ra một 'Góc nhìn Chuyên gia (HR Insight)' liên quan đến Vòng đời Trải nghiệm Nhân viên (Employee Life-cycle), phân tích rủi ro 'kỳ vọng không được đáp ứng' (honeymoon phase) và cách can thiệp giữ chân (retention)."
                    render_ai_insight_card("AI Demographic Insight", demo_ai_data, prompt, custom_style="margin-top: 16px; padding: 20px;")

    else:
        st.info("Chưa có dữ liệu Nhân khẩu học trong các nhóm hiện tại.")

    # ══════════════════════════════════════════════════════════════
    # SECTION 4: EVP & NLP INSIGHTS
    # ══════════════════════════════════════════════════════════════
    st.markdown('<h3 style="margin-top:2rem; font-weight:800; color:#0A1F44;">3. EVP & Lắng Nghe Nhân Viên (NLP)</h3>', unsafe_allow_html=True)
    
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
                orientation='h', marker_color=COLORS['green'],
                text=df_evp['Mentions'], textposition='inside'
            ))
            fig_evp = fig_card(fig_evp, 'Từ khóa EVP nổi bật', 'Tần suất được nhắc đến trong câu hỏi mở')
            st.plotly_chart(fig_evp, use_container_width=True)
            
        with c_evp2:
            nlp_ai_data = {
                "EVP_Buckets_Frequencies": df_evp.set_index('EVP_Factor')['Mentions'].to_dict(),
                "Top_Bucket": df_evp.iloc[-1]['EVP_Factor'],
                "Bottom_Bucket": df_evp.iloc[0]['EVP_Factor']
            }
            prompt = "Phân tích dữ liệu đếm từ khóa từ các câu hỏi mở (Open-text) của nhân viên. Bóc tách những yếu tố ảnh hưởng mạnh nhất đến định vị thương hiệu tuyển dụng (EVP). Nêu rõ những điểm được đánh giá cao (như môi trường, thu nhập) và cảnh báo về những rủi ro bất mãn (ví dụ: công nghệ, tốc độ xử lý, truy thu... tùy theo dữ liệu đếm)."
            render_ai_insight_card("AI NLP Insight: Định Vị Thương Hiệu (EVP)", nlp_ai_data, prompt, badge="NLP Engine", custom_style="height: 100%; margin-bottom: 0; padding: 24px;")
    else:
        st.info("Chưa có dữ liệu câu hỏi mở (NLP) để phân tích EVP.")
