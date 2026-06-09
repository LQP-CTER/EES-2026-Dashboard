import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from textwrap import dedent
from utils.data_loader import compute_kpis, PILLAR_LABELS
from shared.plotly_theme import fig_card, apply_theme, COLORS
from utils.benchmark_2025 import get_company_benchmark_2025
from utils.ai_generator import render_ai_insight_card

MIN_DEPARTMENT_N = 1
MIN_ORG_SEGMENT_N = 5
UNKNOWN_ORG_VALUE = "Chưa xác định"


def _normalize_org_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Normalize org columns so GHN overview does not silently drop blank units."""
    df = df.copy()
    fallback_map = {
        "division": ["division", "Khối", "Khoi", "Division", "Khối/Phòng ban", "Khối / Phòng ban"],
        "department": ["department", "Phòng ban", "Phong ban", "Department", "Bộ phận", "Bo phan"],
        "section": ["section", "Section", "Vùng", "Vung", "Khu vực", "Khu vuc"],
    }
    for target, candidates in fallback_map.items():
        if target not in df.columns:
            source = next((c for c in candidates if c in df.columns), None)
            if source is not None:
                df[target] = df[source]
        if target in df.columns:
            clean = df[target].astype("string").str.replace(r"\s+", " ", regex=True).str.strip()
            df[target] = clean.mask(clean.isna() | clean.eq("") | clean.str.lower().isin({"nan", "none", "null"}), UNKNOWN_ORG_VALUE)
    return df


def render(all_data, available_groups):
    if not all_data:
        st.error("Không tìm thấy dữ liệu nào.")
        return

    apply_theme()

    all_dfs = []
    total_n_before = 0
    for group_id, (df, n_before) in all_data.items():
        df_group = df.copy()
        df_group["_survey_group"] = group_id
        all_dfs.append(df_group)
        total_n_before += n_before

    df_total = _normalize_org_columns(pd.concat(all_dfs, ignore_index=True))
    total_kpis = compute_kpis(df_total)
    total_n = total_kpis['n']
    total_ei = total_kpis['ei_mean']
    total_enps = total_kpis['enps_score']
    total_intent = total_kpis['intent_pct_low']
    total_mei = total_kpis.get('mei_mean', 0.0)

    try:
        from shared.workforce_mapper import load_workforce_and_mapping
        df_wf, _, _ = load_workforce_and_mapping()
        total_headcount = len(df_wf) if df_wf is not None and not df_wf.empty else 21353
    except Exception:
        total_headcount = 21353

    # total_n_before = raw submissions (tham gia khảo sát)
    # total_n        = sau lọc memo (mẫu phân tích hợp lệ)
    total_participants = total_n_before  # raw count cho tỷ lệ tham gia
    total_cleaned = total_n              # mẫu sau lọc dùng cho phân tích
    total_rr = round((total_participants / total_headcount) * 100, 1) if total_headcount > 0 else 0
    cleaned_rr = round((total_cleaned / total_headcount) * 100, 1) if total_headcount > 0 else 0
    bm = get_company_benchmark_2025()
    ei_delta = total_ei - bm['ei_mean']
    enps_delta = total_enps - bm['enps_score']
    rr_delta = total_rr - bm['response_rate']

    st.markdown('''
    <style>
    .ghn-shell {
        border-radius:28px;
        padding:32px;
        margin:20px 0 28px;
        background:
            radial-gradient(circle at 8% 0%, rgba(255,82,0,.12), transparent 28%),
            radial-gradient(circle at 92% 12%, rgba(29,78,216,.10), transparent 30%),
            linear-gradient(135deg, #FFFFFF 0%, #F8FAFC 54%, #EEF6FF 100%);
        border:1px solid rgba(226,232,240,.95);
        box-shadow:0 24px 64px rgba(10,31,68,.11), inset 0 1px 0 rgba(255,255,255,.96);
        overflow:hidden;
    }
    .ghn-hero {
        display:grid;
        grid-template-columns:minmax(0,1.15fr) minmax(340px,.85fr);
        gap:26px;
        align-items:stretch;
    }
    .ghn-kicker {
        display:inline-flex;
        align-items:center;
        gap:8px;
        padding:7px 12px;
        border-radius:999px;
        background:#FFF4EF;
        border:1px solid #FFD5BF;
        color:#FF5200;
        font-size:.72rem;
        font-weight:850;
        letter-spacing:.15em;
        text-transform:uppercase;
        margin-bottom:14px;
    }
    .ghn-kicker::before {
        content:'';
        width:8px;
        height:8px;
        border-radius:50%;
        background:#10B981;
        box-shadow:0 0 0 5px rgba(16,185,129,.14);
    }
    .ghn-title {
        font-size:clamp(2.25rem,3.45vw,3.65rem);
        line-height:1.03;
        letter-spacing:-.04em;
        font-weight:950;
        color:#0A1F44;
        margin:0 0 14px;
    }
    .ghn-subtitle {
        color:#475569;
        font-size:1rem;
        line-height:1.72;
        font-weight:550;
        margin:0;
        max-width:760px;
    }
    .ghn-command {
        position:relative;
        min-height:285px;
        border-radius:24px;
        padding:24px;
        overflow:hidden;
        color:#fff;
        background:
            linear-gradient(rgba(255,255,255,.08) 1px, transparent 1px),
            linear-gradient(90deg, rgba(255,255,255,.07) 1px, transparent 1px),
            linear-gradient(145deg, rgba(10,31,68,.98), rgba(29,78,216,.88));
        background-size:34px 34px,34px 34px,auto;
        box-shadow:0 24px 54px rgba(10,31,68,.24);
        transform:perspective(1200px) rotateY(-3deg) rotateX(1deg);
    }
    .ghn-command::after {
        content:'';
        position:absolute;
        width:210px;
        height:210px;
        right:-72px;
        bottom:-86px;
        background:radial-gradient(circle, rgba(255,82,0,.44), transparent 66%);
        pointer-events:none;
    }
    .ghn-command-label {
        position:relative;
        z-index:1;
        font-size:.72rem;
        font-weight:850;
        letter-spacing:.17em;
        text-transform:uppercase;
        color:#FFDBCC;
    }
    .ghn-command-score {
        position:relative;
        z-index:1;
        margin-top:18px;
        font-size:clamp(3rem,5.3vw,5rem);
        line-height:.9;
        font-weight:950;
        letter-spacing:-.06em;
    }
    .ghn-command-sub {
        position:relative;
        z-index:1;
        color:rgba(255,255,255,.82);
        font-size:.86rem;
        line-height:1.55;
        margin-top:10px;
    }
    .ghn-mini-grid {
        position:relative;
        z-index:1;
        display:grid;
        grid-template-columns:repeat(2,minmax(0,1fr));
        gap:10px;
        margin-top:28px;
    }
    .ghn-mini {
        border-radius:14px;
        padding:12px 13px;
        background:rgba(255,255,255,.12);
        border:1px solid rgba(255,255,255,.18);
        backdrop-filter:blur(10px);
    }
    .ghn-mini span { display:block; font-size:.66rem; font-weight:800; letter-spacing:.1em; text-transform:uppercase; color:#BFDBFE; margin-bottom:6px; }
    .ghn-mini strong { display:block; font-size:1.2rem; line-height:1; font-weight:900; color:#fff; }
    .ghn-metrics {
        display:grid;
        grid-template-columns:repeat(4,minmax(0,1fr));
        gap:16px;
        margin-top:22px;
    }
    .ghn-metric {
        position:relative;
        overflow:hidden;
        min-width:0;
        border-radius:18px;
        padding:18px 18px 20px;
        background:rgba(255,255,255,.86);
        border:1px solid rgba(226,232,240,.95);
        box-shadow:0 16px 30px rgba(10,31,68,.08);
    }
    .ghn-metric::before {
        content:'';
        position:absolute;
        top:0;
        left:0;
        right:0;
        height:4px;
        background:linear-gradient(90deg,var(--accent),#FFB38B);
    }
    .ghn-metric-label {
        color:var(--accent);
        font-size:.68rem;
        font-weight:850;
        text-transform:uppercase;
        letter-spacing:.11em;
        margin-bottom:10px;
    }
    .ghn-metric-value {
        font-size:clamp(1.7rem,2.35vw,2.55rem);
        font-weight:950;
        line-height:.95;
        color:#0A1F44;
        letter-spacing:-.04em;
        font-variant-numeric:tabular-nums;
        white-space:nowrap;
    }
    .ghn-metric-sub {
        font-size:.78rem;
        color:#64748B;
        line-height:1.45;
        margin-top:8px;
        font-weight:550;
    }
    .ghn-context {
        display:grid;
        grid-template-columns:repeat(4,minmax(0,1fr));
        gap:14px;
        margin-top:20px;
    }
    .ghn-context-card {
        background:#fff;
        border:1px solid #E2E8F0;
        border-radius:16px;
        padding:16px 17px;
        box-shadow:0 14px 30px rgba(10,31,68,.06);
        min-height:130px;
    }
    .ghn-context-chip {
        display:inline-flex;
        align-items:center;
        padding:5px 10px;
        border-radius:999px;
        background:#FFF4EF;
        border:1px solid #FFD5BF;
        color:#FF5200;
        font-size:.68rem;
        font-weight:850;
        letter-spacing:.08em;
        text-transform:uppercase;
        margin-bottom:10px;
    }
    .ghn-context-card h4 { margin:0 0 7px; font-size:.94rem; color:#0A1F44; font-weight:850; letter-spacing:-.01em; }
    .ghn-context-card p { margin:0; color:#64748B; font-size:.82rem; line-height:1.6; font-weight:520; }
    .ghn-band {
        border-radius:22px;
        padding:20px;
        margin:0 0 26px;
        background:#fff;
        border:1px solid #E2E8F0;
        box-shadow:0 18px 42px rgba(10,31,68,.08);
    }
    @media (max-width:1080px) {
        .ghn-hero { grid-template-columns:1fr; }
        .ghn-command { transform:none; }
        .ghn-metrics, .ghn-context { grid-template-columns:repeat(2,minmax(0,1fr)); }
    }
    @media (max-width:720px) {
        .ghn-shell { padding:20px; border-radius:22px; }
        .ghn-metrics, .ghn-context, .ghn-mini-grid { grid-template-columns:1fr; }
    }
    </style>
    ''', unsafe_allow_html=True)

    hero_html = dedent(f'''
    <div class="ghn-shell">
        <div class="ghn-hero">
            <div>
                <span class="ghn-kicker">GHN · Tổng quan tổ chức</span>
                <h1 class="ghn-title">Tổng quan GHN<br/>trên nền dữ liệu EES 2026</h1>
                <p class="ghn-subtitle">
                    Một lớp điều hành tổng hợp cho thấy quy mô tham gia, sức khỏe gắn kết,
                    khoảng cách giữa các đơn vị và các điểm cần ưu tiên trước khi đi sâu vào từng nhóm khảo sát.
                </p>
            </div>
            <div class="ghn-command">
                <div class="ghn-command-label">Trung tâm điều hành gắn kết</div>
                <div class="ghn-command-score">{total_ei:.1f}</div>
                <div class="ghn-command-sub">EI tổng thể · eNPS {total_enps:+.0f} · Rủi ro nghỉ việc {total_intent:.1f}%</div>
                <div class="ghn-mini-grid">
                    <div class="ghn-mini"><span>Tỷ lệ phản hồi</span><strong>{total_rr:.1f}%</strong></div>
                    <div class="ghn-mini"><span>EI so với 2025</span><strong>{ei_delta:+.1f}</strong></div>
                    <div class="ghn-mini"><span>Mẫu hợp lệ</span><strong>{total_cleaned:,}</strong></div>
                    <div class="ghn-mini"><span>Độ phủ dữ liệu</span><strong>{cleaned_rr:.1f}%</strong></div>
                </div>
            </div>
        </div>

        <div class="ghn-metrics">
            <div class="ghn-metric" style="--accent:#0A1F44"><div class="ghn-metric-label">Tổng nhân sự</div><div class="ghn-metric-value">{total_headcount:,}</div><div class="ghn-metric-sub">Headcount toàn tổ chức GHN</div></div>
            <div class="ghn-metric" style="--accent:#1D4ED8"><div class="ghn-metric-label">Đã tham gia</div><div class="ghn-metric-value">{total_participants:,}</div><div class="ghn-metric-sub">{total_rr:.1f}% tỷ lệ phản hồi</div></div>
            <div class="ghn-metric" style="--accent:#10B981"><div class="ghn-metric-label">Mẫu phân tích</div><div class="ghn-metric-value">{total_cleaned:,}</div><div class="ghn-metric-sub">{cleaned_rr:.1f}% / headcount sau lọc memo</div></div>
            <div class="ghn-metric" style="--accent:#64748B"><div class="ghn-metric-label">Chưa tham gia</div><div class="ghn-metric-value">{max(total_headcount - total_participants, 0):,}</div><div class="ghn-metric-sub">{max(round((1 - total_participants / total_headcount) * 100, 1), 0):.1f}% chưa phản hồi</div></div>
        </div>


    </div>
    ''')
    st.html(hero_html)

    # Executive company overview section
    from shared.plotly_theme import make_html_kpi
    st.html(dedent("""
    <div class="ghn-band">
        <div style="display:flex;align-items:flex-end;justify-content:space-between;gap:16px;flex-wrap:wrap;margin-bottom:14px;">
            <div>
                <div style="font-size:.72rem;font-weight:850;color:#FF5200;text-transform:uppercase;letter-spacing:.14em;margin-bottom:6px;">TỔNG QUAN GIAO HÀNG NHANH</div>
                <div style="font-size:1.35rem;font-weight:900;color:#0A1F44;letter-spacing:-.02em;">Bốn chỉ số chiến lược</div>
            </div>
            <div style="font-size:.82rem;color:#64748B;font-weight:550;">So sánh với baseline 2025 và trạng thái hiện tại của toàn tổ chức.</div>
        </div>
    </div>
    """))
    kpi_c1, kpi_c2, kpi_c3, kpi_c4 = st.columns(4)
    with kpi_c1:
        st.markdown(make_html_kpi("EI - Chỉ số gắn kết", f"{total_ei:.1f}", delta=f"{ei_delta:+.1f}", color="blue", icon="", progress_val=total_ei), unsafe_allow_html=True)
    with kpi_c2:
        st.markdown(make_html_kpi("eNPS - Mức sẵn sàng giới thiệu", f"{total_enps:+.0f}", delta=f"{enps_delta:+.0f}", color="orange", icon="", progress_val=(total_enps+100)/2), unsafe_allow_html=True)
    with kpi_c3:
        st.markdown(make_html_kpi("Attrition Risk - Rủi ro nghỉ việc", f"{total_intent:.1f}%", delta="N/A", color="red", icon="", progress_val=total_intent), unsafe_allow_html=True)
    with kpi_c4:
        st.markdown(make_html_kpi("MEI - Quản lý trực tiếp", f"{total_mei:.1f}", delta="N/A", color="green", icon="", progress_val=total_mei), unsafe_allow_html=True)

    try:
        from views.analyst_intelligence import render_company_analyst_intelligence
        render_company_analyst_intelligence(all_data)
    except Exception as _analyst_err:
        st.caption(f"Phân tích chuyên sâu từ tài liệu analyst không khả dụng: {_analyst_err}")

    # Calculate dynamic insights across divisions
    div_stats = []
    for div, df_div in df_total.groupby('division', dropna=False):
        if len(df_div) < MIN_ORG_SEGMENT_N:
            continue
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
            for div, df_div in df_total.groupby('division', dropna=False):
                if len(df_div) < MIN_ORG_SEGMENT_N:
                    continue
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
    # SECTION 2b: DRILLDOWN – PHÒNG BAN & SECTION
    # ══════════════════════════════════════════════════════════════
    st.markdown(section_header("Phân Tích Chi Tiết — Phòng Ban & Section",
                               "So sánh EI, eNPS và 5 trụ cột theo từng phòng ban / section"), unsafe_allow_html=True)

    def _build_drilldown_table(df_src, group_col, label, min_n=MIN_ORG_SEGMENT_N):
        rows = []
        for grp_val, grp_df in df_src.groupby(group_col, dropna=False):
            if len(grp_df) < min_n:
                continue
            kpis = compute_kpis(grp_df)
            row = {
                label: grp_val,
                'N': kpis['n'],
                'EI (%)': round(kpis['ei_mean'], 1),
                'eNPS': round(kpis['enps_score'], 0),
                'Rủi ro nghỉ việc (%)': round(kpis['intent_pct_low'], 1),
            }
            for p, plabel in PILLAR_LABELS.items():
                col = f'{p}_pct'
                if col in grp_df.columns:
                    row[plabel] = round(grp_df[col].mean(), 1)
            rows.append(row)
        if not rows:
            return pd.DataFrame()
        tbl = pd.DataFrame(rows).sort_values('EI (%)', ascending=False).reset_index(drop=True)
        return tbl

    def _color_ei(v):
        try:
            v = float(v)
            c = '#10B981' if v >= 75 else '#F59E0B' if v >= 65 else '#EF4444'
            return f'color:{c};font-weight:700'
        except Exception:
            return ''

    def _color_enps(v):
        try:
            v = float(v)
            c = '#10B981' if v >= 20 else '#F59E0B' if v >= 0 else '#EF4444'
            return f'color:{c};font-weight:700'
        except Exception:
            return ''

    def _heatmap_pillar(v):
        try:
            v = float(v)
            if v >= 78:   return 'background-color:#D1FAE5;color:#065F46'
            elif v >= 72: return 'background-color:#FEF3C7;color:#92400E'
            else:          return 'background-color:#FEE2E2;color:#991B1B'
        except Exception:
            return ''

    pillar_cols = [lbl for lbl in PILLAR_LABELS.values()]

    tab_dept, tab_section = st.tabs(["Theo Phòng Ban (Department)", "Theo Section"])

    with tab_dept:
        if 'department' in df_total.columns:
            tbl_dept = _build_drilldown_table(df_total, 'department', 'Phòng Ban', min_n=MIN_DEPARTMENT_N)
            if not tbl_dept.empty:
                # Summary KPI row
                kd1, kd2, kd3 = st.columns(3)
                kd1.metric("Số phòng ban phân tích", len(tbl_dept))
                kd2.metric("EI cao nhất", f"{tbl_dept['EI (%)'].max():.1f}%", delta=tbl_dept.iloc[0]['Phòng Ban'])
                kd3.metric("EI thấp nhất", f"{tbl_dept['EI (%)'].iloc[-1]:.1f}%", delta=tbl_dept.iloc[-1]['Phòng Ban'], delta_color="inverse")

                # Bar chart EI by department
                fig_dept = go.Figure(go.Bar(
                    y=tbl_dept['Phòng Ban'], x=tbl_dept['EI (%)'],
                    orientation='h',
                    marker=dict(
                        color=[
                            '#10B981' if v >= 75 else '#F59E0B' if v >= 65 else '#EF4444'
                            for v in tbl_dept['EI (%)']
                        ],
                        cornerradius=4,
                    ),
                    text=[f"{v:.1f}%" for v in tbl_dept['EI (%)']],
                    textposition='outside',
                ))
                fig_dept.add_vline(x=75, line_dash='dot', line_color='#10B981', line_width=1.5,
                                   annotation_text='75% target', annotation_position='top right')
                fig_dept = fig_card(fig_dept, 'EI theo Phòng Ban', 'Mức độ gắn kết trung bình')
                fig_dept.update_layout(
                    height=max(300, len(tbl_dept) * 28 + 80),
                    xaxis=dict(range=[0, 100]),
                    yaxis=dict(autorange='reversed'),
                )
                st.plotly_chart(fig_dept, width='stretch', key="dept_ei_bar")

                # Detailed table with pillar heatmap
                st.markdown("##### Bảng chi tiết — EI, eNPS & 5 Trụ Cột theo Phòng Ban")
                avail_pillar_cols = [c for c in pillar_cols if c in tbl_dept.columns]

                # Format numbers into strings before styling
                tbl_dept_fmt = tbl_dept.copy()
                for c in ['EI (%)', 'Rủi ro nghỉ việc (%)'] + avail_pillar_cols:
                    if c in tbl_dept_fmt.columns:
                        tbl_dept_fmt[c] = tbl_dept_fmt[c].apply(lambda v: f"{v:.1f}")
                if 'eNPS' in tbl_dept_fmt.columns:
                    tbl_dept_fmt['eNPS'] = tbl_dept_fmt['eNPS'].apply(lambda v: f"{v:+.0f}")

                # Re-use raw numeric cols for coloring via the original tbl_dept
                def _style_dept_row(row_idx, col, raw_df, fmt_df):
                    pass  # not used

                # Build style using original numeric tbl for color logic, display fmt df
                def _make_styler(fmt_df, raw_df, ei_col, enps_col, pillar_col_list):
                    def _ei_style(col_series):
                        return [_color_ei(raw_df.loc[i, ei_col]) for i in raw_df.index]
                    def _enps_style(col_series):
                        return [_color_enps(raw_df.loc[i, enps_col]) for i in raw_df.index]
                    def _pillar_style(col_series, col_name):
                        return [_heatmap_pillar(raw_df.loc[i, col_name]) for i in raw_df.index]

                    s = fmt_df.style.set_table_styles([
                        {'selector': 'th', 'props': [('background-color', '#F8FAFC'), ('color', '#475569'),
                                                      ('font-size', '0.73rem'), ('font-weight', '700'),
                                                      ('text-align', 'center')]},
                        {'selector': 'td', 'props': [('font-size', '0.78rem'), ('text-align', 'center')]},
                        {'selector': 'td:first-child', 'props': [('text-align', 'left')]},
                    ])
                    s = s.apply(_ei_style, subset=[ei_col], axis=0)
                    s = s.apply(_enps_style, subset=[enps_col], axis=0)
                    for pc in pillar_col_list:
                        if pc in fmt_df.columns:
                            s = s.apply(lambda col, _pc=pc: _pillar_style(col, _pc), subset=[pc], axis=0)
                    return s

                styled_dept = _make_styler(tbl_dept_fmt, tbl_dept.reset_index(drop=True),
                                           'EI (%)', 'eNPS', avail_pillar_cols)
                st.dataframe(styled_dept, width='stretch', hide_index=True)
            else:
                st.info("Không có dữ liệu theo phòng ban.")
        else:
            st.info("Dữ liệu chưa có cột 'department'.")

    with tab_section:
        if 'section' in df_total.columns:
            tbl_section = _build_drilldown_table(df_total, 'section', 'Section')
            if not tbl_section.empty:
                ks1, ks2, ks3 = st.columns(3)
                ks1.metric("Số section phân tích", len(tbl_section))
                ks2.metric("EI cao nhất", f"{tbl_section['EI (%)'].max():.1f}%", delta=tbl_section.iloc[0]['Section'])
                ks3.metric("EI thấp nhất", f"{tbl_section['EI (%)'].iloc[-1]:.1f}%", delta=tbl_section.iloc[-1]['Section'], delta_color="inverse")

                # Bar chart – paginated nếu nhiều section
                max_section_show = min(len(tbl_section), 60)
                if max_section_show <= 10:
                    n_show = max_section_show
                else:
                    n_show = st.slider(
                        "Số section hiển thị (sắp xếp theo EI)",
                        min_value=10,
                        max_value=max_section_show,
                        value=min(30, max_section_show),
                        step=5,
                        key="section_slider",
                    )
                tbl_section_show = pd.concat([
                    tbl_section.head(n_show // 2),
                    tbl_section.tail(n_show - n_show // 2)
                ]).drop_duplicates()

                fig_sec = go.Figure(go.Bar(
                    y=tbl_section_show['Section'], x=tbl_section_show['EI (%)'],
                    orientation='h',
                    marker=dict(
                        color=[
                            '#10B981' if v >= 75 else '#F59E0B' if v >= 65 else '#EF4444'
                            for v in tbl_section_show['EI (%)']
                        ],
                        cornerradius=4,
                    ),
                    text=[f"{v:.1f}%" for v in tbl_section_show['EI (%)']],
                    textposition='outside',
                ))
                fig_sec.add_vline(x=75, line_dash='dot', line_color='#10B981', line_width=1.5)
                fig_sec = fig_card(fig_sec, 'EI theo Section', f'Top & Bottom {n_show} section')
                fig_sec.update_layout(
                    height=max(350, len(tbl_section_show) * 26 + 80),
                    xaxis=dict(range=[0, 100]),
                    yaxis=dict(autorange='reversed'),
                )
                st.plotly_chart(fig_sec, width='stretch', key="section_ei_bar")

                st.markdown("##### Bảng đầy đủ — EI, eNPS & 5 Trụ Cột theo Section")
                avail_pillar_cols_s = [c for c in pillar_cols if c in tbl_section.columns]

                tbl_section_fmt = tbl_section.copy()
                for c in ['EI (%)', 'Rủi ro nghỉ việc (%)'] + avail_pillar_cols_s:
                    if c in tbl_section_fmt.columns:
                        tbl_section_fmt[c] = tbl_section_fmt[c].apply(lambda v: f"{v:.1f}")
                if 'eNPS' in tbl_section_fmt.columns:
                    tbl_section_fmt['eNPS'] = tbl_section_fmt['eNPS'].apply(lambda v: f"{v:+.0f}")

                styled_section = _make_styler(tbl_section_fmt, tbl_section.reset_index(drop=True),
                                              'EI (%)', 'eNPS', avail_pillar_cols_s)
                st.dataframe(styled_section, width='stretch', hide_index=True)
            else:
                st.info(f"Không đủ mẫu theo section (tối thiểu {MIN_ORG_SEGMENT_N} người / section).")
        else:
            st.info("Dữ liệu chưa có cột 'section'.")

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
        
        # Define some key EVP buckets manually for GHN context based on NLP Expert Report
        evp_buckets = {
            'Phạt & Truy thu (INCOME_Penalty)': ['phạt', 'trừ', 'truy thu', 'đền', 'bắt đền', 'đơn giá', 'sai địa chỉ'],
            'Minh bạch thu nhập (INCOME_Transparency)': ['minh bạch', 'cách tính', 'không rõ', 'chưa rõ', 'thắc mắc lương'],
            'Lương & Phụ cấp cơ bản (INCOME_Base)': ['lương', 'thưởng', 'thu nhập', 'phụ cấp', 'xăng', 'tiền', 'chế độ'],
            'Quá tải công việc (BURNOUT_Overload)': ['quá tải', 'mệt', 'nhiều việc', 'áp lực', 'báo cáo', 'đuối'],
            'Thiếu ngày nghỉ (BURNOUT_NoRest)': ['ngày nghỉ', 'nghỉ phép', 'không được nghỉ', 'làm suốt', 'nghỉ ngơi', 'chủ nhật'],
            'Hỗ trợ từ quản lý (MGR_Support)': ['quản lý', 'sếp', 'hỗ trợ', 'tận tâm', 'giúp đỡ', 'tbc', 'am', 'lãnh đạo'],
            'Lộ trình phát triển (CAREER_Path)': ['thăng tiến', 'phát triển', 'lộ trình', 'tương lai', 'học hỏi', 'đào tạo'],
            'Quy trình & Công cụ (OPS_Process)': ['quy trình', 'thủ tục', 'rườm rà', 'hệ thống', 'app', 'lỗi', 'pda', 'chậm', 'thao tác'],
            'Đồng nghiệp & Môi trường (ENV_Team)': ['môi trường', 'đồng nghiệp', 'anh em', 'hòa đồng', 'vui vẻ', 'thân thiện', 'tập thể'],
            'Tự chủ thời gian (POS_Flexibility)': ['chủ động', 'thời gian', 'tự do', 'không gò bó', 'thoải mái', 'linh hoạt']
        }
        
        evp_counts = {k: 0 for k in evp_buckets.keys()}
        for k, keywords in evp_buckets.items():
            for kw in keywords:
                # Use simple count for the keyword in the entire text
                # We add a simple space padding check or regex word boundary
                pattern = r'\b' + re.escape(kw) + r'\b'
                evp_counts[k] += len(re.findall(pattern, all_text))
                    
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


