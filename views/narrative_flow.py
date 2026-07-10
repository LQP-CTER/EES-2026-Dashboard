"""
Narrative Flow — EES 2026
Chế độ "Xem Báo Cáo" — mạch chuyện dữ liệu xuyên suốt.
Thay vì tab rời rạc, dẫn dắt lãnh đạo qua câu chuyện dữ liệu:
  Act 1: Bức tranh tổng thể (KPIs)
  Act 2: Những phát hiện mâu thuẫn (Contradictions)
  Act 3: Đi sâu vào矛盾 thuẫn (Deep Dive)
  Act 4: Hành động (Action)
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

from shared.codebook import PILLAR_META, PILLAR_ORDER, get_pillar_questions, get_question_label
from shared.plotly_theme import fig_card, COLORS, make_html_kpi, section_header
from utils.contradiction_engine import detect_contradictions, get_top_contradictions
from utils.ai_generator import (
    MASTER_REPORT_VOICE_VERSION,
    get_master_report_voice_prompt,
    render_ai_insight_card,
)


_AI_LOGO_B64 = ""


def _act_header(number: str, title: str, subtitle: str, color: str = "#FF5200") -> str:
    """Render a professional act/section header for the narrative report."""
    return f"""
    <div style="display:flex;align-items:flex-start;gap:16px;margin:32px 0 20px;
                padding-bottom:16px;border-bottom:2px solid #F1F5F9;">
        <div style="background:{color};color:white;border-radius:10px;padding:8px 14px;
                    font-size:0.72rem;font-weight:800;letter-spacing:0.06em;
                    text-transform:uppercase;white-space:nowrap;flex-shrink:0;margin-top:2px">
            {number}
        </div>
        <div>
            <div style="font-size:1.05rem;font-weight:800;color:#0A1F44;letter-spacing:-0.02em;line-height:1.25">
                {title}
            </div>
            <div style="font-size:0.82rem;color:#64748B;margin-top:4px;font-weight:500">
                {subtitle}
            </div>
        </div>
    </div>"""


def render_narrative(df, cfg, group_id, df_bench=None):
    """Render toàn bộ narrative flow cho một nhóm."""
    group_name = cfg.get('label', group_id)

    # ── Mode selector ────────────────────────────────────────────────
    mode = st.segmented_control(
        "Chế độ báo cáo",
        options=["Tổng quan nhóm", "Báo cáo đơn vị"],
        default="Tổng quan nhóm",
        key=f"narrative_mode_{group_id}",
    )
    if mode == "Báo cáo đơn vị":
        _render_unit_report(df, cfg, group_id, df_bench=df_bench)
        return

    from utils.data_loader import compute_kpis
    kpis = compute_kpis(df)

    # Compute contradictions once — shared across tabs
    contradictions = detect_contradictions(df, group_id, cfg)
    top_contradictions = get_top_contradictions(contradictions, n=3)

    # ── Report page header ──────────────────────────────────────────
    n_contradictions = len(contradictions)
    severity_label = "Có mâu thuẫn nghiêm trọng" if any(
        c['severity'] == 'critical' for c in contradictions
    ) else ("Có cảnh báo" if contradictions else "Dữ liệu nhất quán")
    severity_color = "#DC2626" if any(c['severity'] == 'critical' for c in contradictions) \
        else ("#D97706" if contradictions else "#15803D")
    severity_bg = "#FEF2F2" if any(c['severity'] == 'critical' for c in contradictions) \
        else ("#FFFBEB" if contradictions else "#F0FDF4")

    color = "#FF5200"
    st.markdown(f"""
    <div style="background:#FFFFFF;border:1px solid #E2E8F0;border-left:4px solid {color};
                border-radius:12px;padding:24px 28px;margin-bottom:28px;box-shadow: 0 4px 6px -1px rgba(0,0,0,0.02);">
        <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:14px;">
            <div>
                <div style="display:flex;align-items:center;gap:8px;margin-bottom:4px">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9.937 15.5A2 2 0 0 0 8.5 14.063l-6.135-1.582a.5.5 0 0 1 0-.962L8.5 9.936A2 2 0 0 0 9.937 8.5l1.582-6.135a.5.5 0 0 1 .963 0L14.063 8.5A2 2 0 0 0 15.5 9.937l6.135 1.581a.5.5 0 0 1 0 .964L15.5 14.063a2 2 0 0 0-1.437 1.437l-1.582 6.135a.5.5 0 0 1-.963 0z"/><path d="M20 3v4"/><path d="M22 5h-4"/><path d="M4 17v2"/><path d="M5 18H3"/></svg>
                    <span style="font-size:0.68rem;font-weight:700;letter-spacing:0.1em;text-transform:uppercase;color:{color};">
                        BÁO CÁO TRẢI NGHIỆM TỔNG THỂ
                    </span>
                </div>
                <span style="font-size:1.4rem;font-weight:800;color:#0A1F44;letter-spacing:-0.02em;">Nhóm {group_name}</span>
            </div>
        </div>
        <p style="font-size:0.83rem;color:#64748B;margin:0 0 18px;line-height:1.65;">
            Mạch dữ liệu xuyên suốt từ bức tranh tổng thể (KPIs) đến những mâu thuẫn ngầm ẩn và định hướng hành động chiến lược.
        </p>
        <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:14px;">
            <div style="background:#F8FAFC;padding:14px;border-radius:8px;border:1px solid #F1F5F9;">
                <span style="font-size:0.65rem;font-weight:700;color:#94A3B8;text-transform:uppercase;letter-spacing:0.08em;display:block;margin-bottom:5px;">EI Score</span>
                <div style="font-size:1.8rem;font-weight:900;color:{color};line-height:1;">{kpis['ei_mean']:.1f}%</div>
                <div style="font-size:0.7rem;color:#94A3B8;margin-top:3px;">Chỉ số Gắn kết</div>
            </div>
            <div style="background:#F8FAFC;padding:14px;border-radius:8px;border:1px solid #F1F5F9;">
                <span style="font-size:0.65rem;font-weight:700;color:#94A3B8;text-transform:uppercase;letter-spacing:0.08em;display:block;margin-bottom:5px;">eNPS</span>
                <div style="font-size:1.8rem;font-weight:900;color:#0A1F44;line-height:1;">{kpis['enps_score']:+.0f}</div>
                <div style="font-size:0.7rem;color:#94A3B8;margin-top:3px;">Net Promoter Score</div>
            </div>
            <div style="background:#F8FAFC;padding:14px;border-radius:8px;border:1px solid #F1F5F9;">
                <span style="font-size:0.65rem;font-weight:700;color:#94A3B8;text-transform:uppercase;letter-spacing:0.08em;display:block;margin-bottom:5px;">Rủi ro nghỉ</span>
                <div style="font-size:1.8rem;font-weight:900;color:#EF4444;line-height:1;">{kpis['intent_pct_low']:.1f}%</div>
                <div style="font-size:0.7rem;color:#94A3B8;margin-top:3px;">Tỷ lệ dự báo nghỉ việc</div>
            </div>
            <div style="background:#F8FAFC;padding:14px;border-radius:8px;border:1px solid #F1F5F9;">
                <span style="font-size:0.65rem;font-weight:700;color:#94A3B8;text-transform:uppercase;letter-spacing:0.08em;display:block;margin-bottom:5px;">Mâu thuẫn (Nghịch lý)</span>
                <div style="display:flex;align-items:center;gap:8px;">
                    <div style="font-size:1.8rem;font-weight:900;color:#0A1F44;line-height:1;">{n_contradictions}</div>
                    <span style="background:{severity_bg};color:{severity_color};padding:3px 8px;border-radius:12px;font-size:0.65rem;font-weight:700;line-height:1.2;white-space:normal;">{severity_label}</span>
                </div>
                <div style="font-size:0.7rem;color:#94A3B8;margin-top:3px;">Vấn đề ngầm phát hiện</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Tabs for each Act ───────────────────────────────────────────
    tab_names = [
        "Act 1 · Tổng thể",
        "Act 2 · Nghịch lý",
        "Act 3 · Đi sâu",
        "Act 4 · Hành động",
        "Act 5 · Tiếng nói NV",
    ]
    tabs = st.tabs(tab_names)
    tab_act1, tab_act2, tab_act3, tab_act4, tab_act5 = tabs

    # ── ACT 1 ──────────────────────────────────────────────────────
    with tab_act1:
        st.markdown(_act_header(
            "Act 1", "Bức tranh tổng thể",
            f"Các chỉ số cốt lõi và hiệu suất trụ cột của {group_name}"
        ), unsafe_allow_html=True)
        _render_kpi_row(kpis)
        
        st.markdown("<br>", unsafe_allow_html=True)
        col_chart, col_ai = st.columns([55, 45], gap="large")
        with col_chart:
            st.markdown("<div style='font-size:0.9rem;font-weight:700;color:#64748B;text-transform:uppercase;margin-bottom:10px;'>Hiệu suất 5 Trụ cột Trải nghiệm</div>", unsafe_allow_html=True)
            pdf = _render_pillar_overview(df, group_id)
        
        with col_ai:
            if pdf is not None:
                ai_prompt = (
                    f"Bạn là Giám đốc Nhân sự (CHRO) kiêm Senior Data Analyst. "
                    f"Phân tích bức tranh sức khỏe tổ chức của nhóm {group_name} DỰA CHÍNH XÁC VÀO DỮ LIỆU SAU "
                    f"(TUYỆT ĐỐI KHÔNG bịa thêm chỉ số nào):\n"
                    f"- EI Score = {kpis['ei_mean']:.1f}%\n"
                    f"- eNPS = {kpis['enps_score']:+.0f}\n"
                    f"- Rủi ro nghỉ việc = {kpis['intent_pct_low']:.1f}% (tỷ lệ muốn NGHỈ, intent ≤ 2/5)\n"
                    f"- Hiệu quả QL (MEI) = {kpis.get('mei_avg',0):.1f}%\n"
                    f"- Burnout = {kpis.get('burnout_pct',0):.1f}%\n"
                    f"- Điểm trụ cột (thang 5): {pdf[['Trụ cột', 'Điểm TB']].to_dict('records')}\n\n"
                    f"Yêu cầu:\n"
                    f"1. Đánh giá 'Sức khỏe tổng thể' đang ở mức nào — dẫn chứng bằng con số cụ thể.\n"
                    f"2. Đâu là tử huyệt (bottleneck) cản trở trải nghiệm nhân viên nhất?\n"
                    f"Viết 2 đoạn văn ngắn, sắc bén. CHỈ trích dẫn các con số đã liệt kê."
                )
                render_ai_insight_card("CHRO Strategic Summary", {"kpis": kpis, "pillars": pdf.to_dict('records')}, ai_prompt, badge="Act 1 Insight")

        # ── Supplementary charts row (radar + EI distribution) ──
        if pdf is not None:
            st.markdown("<br>", unsafe_allow_html=True)
            _r_col, _e_col = st.columns(2)
            with _r_col:
                _render_act1_radar_chart(pdf, group_name)
            with _e_col:
                _render_ei_distribution_chart(df, "_act1")

    # ── ACT 2 ──────────────────────────────────────────────────────
    with tab_act2:
        st.markdown(_act_header(
            "Act 2", "Những nghịch lý & Điểm mù",
            "Phân tích mâu thuẫn dữ liệu hoặc rủi ro tiềm ẩn",
            color="#DC2626"
        ), unsafe_allow_html=True)
        if not contradictions:
            _render_hidden_risks(df, group_id)
        else:
            _render_contradiction_cards(df, contradictions)

    # ── ACT 3 ──────────────────────────────────────────────────────
    with tab_act3:
        st.markdown(_act_header(
            "Act 3", "Đi sâu vào vấn đề cốt lõi",
            "Phân tích chi tiết nguyên nhân sâu xa (Root Cause)",
            color="#8B5CF6"
        ), unsafe_allow_html=True)
        if not top_contradictions:
            _render_weakness_deep_dive(df, group_id)
        else:
            for i, contradiction in enumerate(top_contradictions, 1):
                _render_deep_dive(df, contradiction, group_id, i)

    # ── ACT 4 ──────────────────────────────────────────────────────
    with tab_act4:
        st.markdown(_act_header(
            "Act 4", "Hành động ưu tiên",
            "Ma trận ưu tiên dựa trên tương quan với Engagement Index",
            color="#F59E0B"
        ), unsafe_allow_html=True)
        _render_action_priorities(df, group_id, contradictions)

    # ── ACT 5 ──────────────────────────────────────────────────────
    with tab_act5:
        st.markdown(_act_header(
            "Act 5", "Tiếng nói nhân viên",
            "Mong muốn thay đổi theo từng đơn vị — phân tích định tính bằng AI",
            color="#10B981"
        ), unsafe_allow_html=True)
        _render_employee_voice(df, group_id, cfg)


def _render_kpi_row(kpis):
    """Render hàng KPI cards."""
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(make_html_kpi(
            "Engagement Index", f"{kpis['ei_mean']:.1f}%",
            color="blue", progress_val=kpis['ei_mean']
        ), unsafe_allow_html=True)
    with c2:
        st.markdown(make_html_kpi(
            "eNPS Score", f"{kpis['enps_score']:+.0f}",
            color="orange", progress_val=(kpis['enps_score']+100)/2
        ), unsafe_allow_html=True)
    with c3:
        st.markdown(make_html_kpi(
            "Rủi ro nghỉ việc", f"{kpis['intent_pct_low']:.1f}%",
            color="red", progress_val=kpis['intent_pct_low']
        ), unsafe_allow_html=True)
    with c4:
        mei = kpis.get('mei_avg', 0)
        st.markdown(make_html_kpi(
            "Hiệu quả QL", f"{mei:.1f}%",
            color="green", progress_val=mei
        ), unsafe_allow_html=True)


def _render_pillar_overview(df, group_id):
    """Render biểu đồ tổng quan 5 trụ cột."""
    pillar_data = []
    for p in PILLAR_ORDER:
        qs = get_pillar_questions(group_id, p)
        q_cols = [q for q in qs if q in df.columns]
        if q_cols:
            score = df[q_cols].mean(numeric_only=True).mean()
            pillar_data.append({
                'Trụ cột': PILLAR_META[p]['name'],
                'Điểm TB': round(score, 2),
                'pillar_id': p,
            })

    if not pillar_data:
        return

    pdf = pd.DataFrame(pillar_data).sort_values('Điểm TB', ascending=True)

    colors = []
    for score in pdf['Điểm TB']:
        if score >= 4.0:
            colors.append('#10B981')
        elif score >= 3.7:
            colors.append('#F59E0B')
        else:
            colors.append('#EF4444')

    fig = go.Figure(go.Bar(
        y=pdf['Trụ cột'], x=pdf['Điểm TB'],
        orientation='h',
        marker=dict(color=colors, cornerradius=4),
        text=[f"{s:.2f}" for s in pdf['Điểm TB']],
        textposition='outside',
        textfont=dict(size=12, color='#0A1F44', family='Exo 2'),
    ))
    fig.add_vline(x=4.0, line_dash="dot", line_color="#10B981", line_width=1.5,
                  annotation_text="Ngưỡng Tốt (4.0)", annotation_position="top right",
                  annotation_font=dict(size=10, color="#10B981"))
    fig.update_layout(
        height=280,
        margin=dict(l=10, r=60, t=10, b=10),
        xaxis=dict(range=[1, 5.3], dtick=0.5, gridcolor='rgba(226,232,240,0.6)', zeroline=False),
        yaxis=dict(automargin=True),
        plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
        font=dict(family='Exo 2', size=12),
    )
    st.plotly_chart(fig, use_container_width=True, key="narrative_flow_chart_146")
    return pdf


def _render_contradiction_cards(df, contradictions):
    """Render các contradiction cards."""
    critical = [c for c in contradictions if c['severity'] == 'critical']
    warning = [c for c in contradictions if c['severity'] == 'warning']

    # Summary banner
    total = len(contradictions)
    
    badges = []
    if critical:
        badges.append(f'<span style="background:#FEF2F2;color:#DC2626;padding:4px 12px;border-radius:20px;font-size:0.78rem;font-weight:700;">{len(critical)} Nghiêm trọng</span>')
    if warning:
        badges.append(f'<span style="background:#FFFBEB;color:#D97706;padding:4px 12px;border-radius:20px;font-size:0.78rem;font-weight:700;">{len(warning)} Cảnh báo</span>')
    badges_html = " ".join(badges)

    st.markdown(f"""
    <div style="background:#F8FAFC;border:1px solid #E2E8F0;border-radius:12px;padding:16px 20px;margin-bottom:20px;">
        <div style="font-size:0.82rem;color:#64748B;margin-bottom:8px;">
            Phát hiện <strong>{total} mâu thuẫn</strong> trong dữ liệu
        </div>
        <div style="display:flex;gap:16px;flex-wrap:wrap;">
            {badges_html}
        </div>
    </div>
    """, unsafe_allow_html=True)

    # AI Systemic Risk Analysis
    if contradictions:
        prompt = (
            f"Bạn là Senior Data Analyst. Dưới đây là danh sách {total} nghịch lý/mâu thuẫn dữ liệu "
            f"ĐƯỢC PHÁT HIỆN TỪ DỮ LIỆU KHẢO SÁT THỰC TẾ:\n"
            f"{[c['title'] for c in contradictions]}\n\n"
            f"Thay vì phân tích rời rạc từng cái, hãy TỔNG HỢP và trả lời "
            f"(CHỈ dựa vào các nghịch lý được liệt kê, KHÔNG bịa thêm):\n"
            f"1. Có 'sợi dây liên kết ngầm' nào giữa các nghịch lý này không?\n"
            f"2. Rủi ro hệ thống (Systemic Risk) lớn nhất là gì nếu lãnh đạo phớt lờ chúng?\n"
            f"Viết 2 đoạn văn ngắn, súc tích, đậm chất chiến lược."
        )
        render_ai_insight_card("Phân tích Rủi ro Hệ thống (Systemic Risk)", {"contradictions": [c['title'] for c in contradictions]}, prompt, badge="Act 2 Insight")
        st.markdown("<br>", unsafe_allow_html=True)

    # Render top contradictions as cards
    for c in contradictions[:5]:
        border_color = '#DC2626' if c['severity'] == 'critical' else '#D97706'
        bg_color = '#FEF2F2' if c['severity'] == 'critical' else '#FFFBEB'
        type_label = {
            'paradox': 'Nghịch lý',
            'gap': 'Khoảng cách',
            'cliff': 'Vực thẳm',
            'blind_spot': 'Điểm mù',
        }.get(c['type'], 'Phát hiện')

        st.markdown(f"""
        <div style="background:{bg_color};border:1px solid {border_color}30;border-left:4px solid {border_color};
                    border-radius:12px;padding:16px 20px;margin-bottom:14px;">
            <div style="display:flex;align-items:center;gap:10px;margin-bottom:10px;">
                <span style="background:{border_color};color:white;padding:3px 10px;border-radius:20px;
                             font-size:0.72rem;font-weight:700;text-transform:uppercase;">
                    {type_label}
                </span>
                <span style="font-size:0.72rem;color:#64748B;">
                    Impact: {c['impact_score']:.0f}/100
                </span>
            </div>
            <div style="font-size:0.92rem;font-weight:700;color:#0A1F44;margin-bottom:8px;">
                {c['title']}
            </div>
            <div style="font-size:0.85rem;color:#475569;line-height:1.65;">
                {c['narrative']}
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        c_id = c['id']
        metrics = c['metrics']
        if c_id == 'TENURE_CLIFF':
            _render_tenure_cliff_chart(df, metrics)
        elif c_id in ('INFO_GAP', 'FAIRNESS_GAP'):
            _render_gap_chart(df, metrics, c_id)
        elif c_id in ('PRIDE_PARADOX', 'INCOME_PARADOX', 'SILENT_DISENGAGED', 'MEI_SHIELD_FAIL', 'BURNOUT_TRAP', 'LEADERSHIP_HALO'):
            _render_paradox_chart(df, metrics, c_id)
        elif c_id == 'BURNOUT_BLIND_SPOT':
            _render_burnout_blind_chart(df, metrics)
        elif c_id == 'GLASS_CEILING':
            _render_glass_ceiling_chart(df, metrics)


def _render_deep_dive(df, contradiction, group_id, index):
    """Render deep dive cho một contradiction."""
    c_id = contradiction['id']
    metrics = contradiction['metrics']

    st.markdown(f"""
    <div style="background:white;border:1px solid #E2E8F0;border-radius:12px;padding:20px 24px;margin-bottom:20px;">
        <div style="font-size:0.72rem;color:#64748B;text-transform:uppercase;letter-spacing:0.08em;margin-bottom:6px;">
            Nghịch lý #{index}
        </div>
        <div style="font-size:1.05rem;font-weight:700;color:#0A1F44;margin-bottom:12px;">
            {contradiction['title']}
        </div>
        <div style="font-size:0.88rem;color:#475569;line-height:1.7;margin-bottom:16px;">
            {contradiction['narrative']}
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Metric chart + EI distribution (always visible in Act 3)
    _ch_col, _ei_col = st.columns([55, 45])
    with _ch_col:
        _render_deep_dive_metric_chart(df, metrics, c_id, index)
    with _ei_col:
        _render_ei_distribution_chart(df, f"_{c_id}_{index}")

    # Regional breakdown (if sub-groups available)
    _render_regional_breakdown_chart(df, c_id)

    # AI deep dive
    _render_ai_deep_dive(contradiction, group_id)


def _render_regional_breakdown_chart(df, c_id):
    """Render regional breakdown chart cho Act 3."""
    group_col = None
    if 'tên_bc' in df.columns and df['tên_bc'].nunique() > 1:
        group_col = 'tên_bc'
    elif 'vùng' in df.columns and df['vùng'].nunique() > 1:
        group_col = 'vùng'
    elif 'phòng ban' in df.columns and df['phòng ban'].nunique() > 1:
        group_col = 'phòng ban'
        
    if not group_col:
        return
        
    q_cols = []
    labels = []
    
    if c_id == 'LEADERSHIP_HALO':
        q_cols = ['Q9', 'Q31']
        labels = ['Q9: Niềm tin LĐ', 'Q31: eNPS']
    elif c_id == 'BURNOUT_TRAP':
        q_cols = ['Q29', 'Q30', 'Q32', 'Q33']
        labels = ['Q29: Khối lượng CV', 'Q30: Áp lực', 'Q32: Kiệt sức', 'Q33: Muốn ở lại']
    elif c_id == 'PRIDE_PARADOX':
        q_cols = ['Q28', 'Q33']
        labels = ['Q28: Tự hào', 'Q33: Muốn ở lại']
    elif c_id == 'INCOME_PARADOX':
        q_cols = ['Q21', 'Q33']
        labels = ['Q21: Thu nhập', 'Q33: Muốn ở lại']
    elif c_id == 'SILENT_DISENGAGED':
        q_cols = ['Q28', 'Q31']
        labels = ['Q28: Hài lòng chung', 'Q31: eNPS']
    elif c_id == 'MEI_SHIELD_FAIL':
        q_cols = ['Q12', 'Q33']
        labels = ['Q12: Hỗ trợ', 'Q33: Muốn ở lại']

    q_cols = [c for c in q_cols if c in df.columns]
    if not q_cols: return
    
    data = []
    for g, grp in df.groupby(group_col):
        if len(grp) < 5: continue
        row = {'Nhóm': g}
        for q in q_cols:
            row[q] = grp[q].mean()
        data.append(row)
        
    if not data: return
    pdf = pd.DataFrame(data)
    
    fig = go.Figure()
    colors = ['#4318FF', '#EF4444', '#F59E0B', '#10B981']
    for idx, q in enumerate(q_cols):
        fig.add_trace(go.Bar(
            name=labels[idx],
            x=pdf['Nhóm'], y=pdf[q],
            marker_color=colors[idx % len(colors)],
            text=[f"{v:.1f}" for v in pdf[q]],
            textposition='outside',
            textfont=dict(size=11)
        ))
    
    fig.update_layout(
        barmode='group',
        title=f"Phân rã theo {group_col}",
        height=320, margin=dict(l=10, r=10, t=40, b=10),
        plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
        font=dict(family='Exo 2', size=12),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    st.plotly_chart(fig, use_container_width=True, key=f"regional_breakdown_{c_id}")


def _render_tenure_cliff_chart(df, metrics, key_suffix=''):
    """Render biểu đồ tenure cliff."""
    if 'Q5' not in df.columns:
        return

    tenure_order = [
        'Dưới 1 tháng', 'Trên 1 đến 3 tháng', 'Trên 3 đến 6 tháng',
        'Trên 6 đến 9 tháng', 'Trên 9 đến 12 tháng', 'Trên 1 đến 2 năm',
        'Trên 2 đến 3 năm', 'Trên 3 đến 5 năm', 'Trên 5 năm',
    ]
    tenure_data = []
    for t in tenure_order:
        subset = df[df['Q5'] == t]['EI']
        if len(subset) >= 10:
            tenure_data.append({'Thâm niên': t, 'EI': round(subset.mean(), 1), 'N': len(subset)})

    if len(tenure_data) < 3:
        return

    tdf = pd.DataFrame(tenure_data)
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=tdf['Thâm niên'], y=tdf['EI'],
        mode='lines+markers+text',
        marker=dict(size=12, color='#4318FF', line=dict(width=2, color='white')),
        line=dict(color='#4318FF', width=3),
        text=[f"{v:.1f}" for v in tdf['EI']],
        textposition='top center',
        textfont=dict(size=11, color='#0A1F44', family='Exo 2'),
    ))
    fig.add_hline(y=65, line_dash="dot", line_color="#10B981", line_width=1.5,
                  annotation_text="Ngưỡng Khỏe mạnh (65%)")
    fig.update_layout(
        height=320,
        margin=dict(l=10, r=10, t=20, b=80),
        xaxis=dict(tickangle=-25, gridcolor='rgba(226,232,240,0.3)'),
        yaxis=dict(range=[max(0, tdf['EI'].min()-10), min(100, tdf['EI'].max()+10)],
                   dtick=10, gridcolor='rgba(226,232,240,0.6)'),
        plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
        font=dict(family='Exo 2'),
    )
    st.plotly_chart(fig, use_container_width=True, key=f"narrative_flow_chart_tenure_cliff{key_suffix}")


def _render_gap_chart(df, metrics, c_id, key_suffix=''):
    """Render biểu đồ gap (info gap hoặc fairness gap)."""
    if c_id == 'INFO_GAP':
        labels = ['Q9: Tin BLĐ', 'Q10: Thông báo']
        values = [metrics.get('Q9_tin_BLD', 0), metrics.get('Q10_thong_bao', 0)]
        colors = ['#10B981', '#EF4444']
    else:
        labels = ['Q11: Hỗ trợ', 'Q12: Công bằng']
        values = [metrics.get('Q11_ho_tro', 0), metrics.get('Q12_cong_bang', 0)]
        colors = ['#10B981', '#EF4444']

    fig = go.Figure(go.Bar(
        x=labels, y=values,
        marker=dict(color=colors, cornerradius=4),
        text=[f"{v:.2f}" for v in values],
        textposition='outside',
        textfont=dict(size=13, color='#0A1F44', family='Exo 2'),
    ))
    fig.add_hline(y=4.0, line_dash="dot", line_color="#10B981", line_width=1.5)
    fig.update_layout(
        height=280,
        margin=dict(l=10, r=10, t=10, b=10),
        yaxis=dict(range=[1, 5.3], dtick=0.5, gridcolor='rgba(226,232,240,0.6)'),
        plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
        font=dict(family='Exo 2', size=12),
    )
    st.plotly_chart(fig, use_container_width=True, key=f"narrative_flow_chart_gap_{c_id}{key_suffix}")


def _render_paradox_chart(df, metrics, c_id, key_suffix=''):
    """Render biểu đồ paradox."""
    if c_id == 'PRIDE_PARADOX':
        labels = ['Q28: Tự hào', 'Ý định nghỉ (%)']
        values = [metrics.get('Q28_tu_hao', 0), metrics.get('intent_low_pct', 0)]
        y_ranges = [[1, 5.3], [0, 100]]
    elif c_id == 'INCOME_PARADOX':
        labels = ['Q21: Thu nhập', 'Ý định nghỉ (%)']
        values = [metrics.get('Q21_thu_nhap', 0), metrics.get('intent_low_pct', 0)]
        y_ranges = [[1, 5.3], [0, 100]]
    elif c_id == 'MEI_SHIELD_FAIL':
        labels = ['MEI: Hiệu quả QL', 'Ý định nghỉ (%)']
        values = [metrics.get('MEI', 0), metrics.get('intent_low_pct', 0)]
        y_ranges = [[0, 100], [0, 100]]
    elif c_id == 'BURNOUT_TRAP':
        labels = ['Burnout (%)', 'Ý định nghỉ (%)']
        values = [metrics.get('burnout_pct', 0), metrics.get('intent_low_pct', 0)]
        y_ranges = [[0, 100], [0, 100]]
    elif c_id == 'LEADERSHIP_HALO':
        labels = ['Q9: Niềm tin LĐ', 'eNPS']
        values = [metrics.get('Q9_tin_BLD', 0), metrics.get('eNPS', 0)]
        y_ranges = [[1, 5.3], [-100, 100]]
    else:
        labels = ['EI', 'Ý định nghỉ (%)']
        values = [metrics.get('EI', 0), metrics.get('intent_low_pct', 0)]
        y_ranges = [[0, 100], [0, 100]]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=labels, y=values,
        marker=dict(color=['#10B981', '#EF4444'], cornerradius=4),
        text=[f"{v:.1f}" for v in values],
        textposition='outside',
        textfont=dict(size=13, color='#0A1F44', family='Exo 2'),
    ))
    fig.update_layout(
        height=280,
        margin=dict(l=10, r=10, t=10, b=10),
        plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
        font=dict(family='Exo 2', size=12),
    )
    st.plotly_chart(fig, use_container_width=True, key=f"narrative_flow_chart_paradox_{c_id}{key_suffix}")


def _render_burnout_blind_chart(df, metrics, key_suffix=''):
    """Render biểu đồ burnout blind spot."""
    labels = ['Q29: Nói ổn', 'Burnout thực tế (%)']
    values = [metrics.get('Q29_ap_luc', 0), metrics.get('burnout_pct', 0)]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=labels, y=values,
        marker=dict(color=['#10B981', '#EF4444'], cornerradius=4),
        text=[f"{v:.1f}" for v in values],
        textposition='outside',
        textfont=dict(size=13, color='#0A1F44', family='Exo 2'),
    ))
    fig.update_layout(
        height=280,
        margin=dict(l=10, r=10, t=10, b=10),
        plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
        font=dict(family='Exo 2', size=12),
    )
    st.plotly_chart(fig, use_container_width=True, key=f"narrative_flow_chart_burnout_blind{key_suffix}")


def _render_glass_ceiling_chart(df, metrics, key_suffix=''):
    """Render biểu đồ glass ceiling."""
    labels = ['NV mới (< 1 năm)', 'NV cũ (> 2 năm)']
    values = [metrics.get('junior_Q19', 0), metrics.get('senior_Q19', 0)]

    fig = go.Figure(go.Bar(
        x=labels, y=values,
        marker=dict(color=['#10B981', '#EF4444'], cornerradius=4),
        text=[f"{v:.2f}" for v in values],
        textposition='outside',
        textfont=dict(size=13, color='#0A1F44', family='Exo 2'),
    ))
    fig.add_hline(y=3.5, line_dash="dot", line_color="#F59E0B", line_width=1.5,
                  annotation_text="Ngưỡng Cảnh báo (3.5)")
    fig.update_layout(
        height=280,
        margin=dict(l=10, r=10, t=10, b=10),
        yaxis=dict(range=[1, 5.3], dtick=0.5, gridcolor='rgba(226,232,240,0.6)'),
        plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
        font=dict(family='Exo 2', size=12),
    )
    st.plotly_chart(fig, use_container_width=True, key=f"narrative_flow_chart_glass_ceiling{key_suffix}")


def _render_ai_deep_dive(contradiction, group_id):
    """Render AI deep dive cho một contradiction."""
    c_id = contradiction['id']
    metrics = contradiction['metrics']

    prompt = (
        f"Bạn là Senior Data Analyst. Áp dụng framework 5 Whys để phân tích nghịch lý sau "
        f"(DỰA VÀO DỮ LIỆU THỰC TẾ BÊN DƯỚI, KHÔNG BỊA THÊM):\n\n"
        f"Nghịch lý: {contradiction['title']}\n\n"
        f"Mô tả: {contradiction['narrative']}\n\n"
        f"Dữ liệu thực tế: {metrics}\n\n"
        f"Trả lời (CHỈ dùng dữ liệu đã cung cấp):\n"
        f"1. Nguyên nhân gốc rễ (Root Cause) theo 5 Whys là gì?\n"
        f"2. Đánh giá rủi ro nếu vấn đề tiếp diễn — dẫn chứng bằng con số từ dữ liệu.\n"
        f"3. Đề xuất 1 hành động can thiệp trúng đích nhất.\n"
        f"Viết ngắn gọn, sắc bén. KHÔNG tự suy diễn con số ngoài dữ liệu."
    )

    render_ai_insight_card(
        f"AI Deep Dive: {contradiction['title']}",
        metrics,
        prompt,
        badge="Deep Dive"
    )


def _render_action_priorities(df, group_id, contradictions):
    """Render action priorities dựa trên contradictions và correlation."""
    from scipy.stats import spearmanr

    from shared.codebook import get_codebook
    codebook = get_codebook(group_id)
    likert_qs = [q for q, info in codebook.items() if info['loại'] == 'likert' and q in df.columns]

    if not likert_qs or 'EI' not in df.columns:
        st.info("Không đủ dữ liệu để tính priority.")
        return

    results = []
    for q in likert_qs:
        valid = df[[q, 'EI']].dropna()
        if len(valid) < 10:
            continue
        corr, _ = spearmanr(valid[q], valid['EI'])
        mean_score = valid[q].mean()
        label = get_question_label(group_id, q)
        results.append({
            'Q': q,
            'Label': label,
            'Mean': round(mean_score, 2),
            'Correlation': round(corr, 3),
        })

    if not results:
        return

    rdf = pd.DataFrame(results)

    # Classify into quadrants
    def classify(row):
        high_impact = abs(row['Correlation']) > 0.3
        low_score = row['Mean'] < 3.7
        if low_score and high_impact:
            return 'Ưu tiên cao'
        elif not low_score and high_impact:
            return 'Duy trì'
        elif low_score and not high_impact:
            return 'Theo dõi'
        else:
            return 'Không ưu tiên'

    rdf['Priority'] = rdf.apply(classify, axis=1)
    rdf = rdf.sort_values('Correlation', ascending=False)

    # Render priority table
    priority_colors = {
        'Ưu tiên cao': '#DC2626',
        'Duy trì': '#10B981',
        'Theo dõi': '#F59E0B',
        'Không ưu tiên': '#94A3B8',
    }

    # Create Scatter Plot for Action Matrix
    fig = go.Figure()

    for priority, color in priority_colors.items():
        subset = rdf[rdf['Priority'] == priority]
        if not subset.empty:
            fig.add_trace(go.Scatter(
                x=subset['Mean'],
                y=subset['Correlation'],
                mode='markers+text',
                name=priority,
                marker=dict(size=14, color=color, line=dict(width=1.5, color='white')),
                text=subset['Q'],
                textposition="top center",
                textfont=dict(size=10, color='#475569', family='Exo 2'),
                hovertemplate="<b>%{text}</b><br>Điểm: %{x:.2f}<br>Tương quan: %{y:.3f}<extra></extra>"
            ))

    # Add Quadrant Lines
    fig.add_vline(x=3.7, line_dash="dot", line_color="#94A3B8", line_width=1.5)
    fig.add_hline(y=0.3, line_dash="dot", line_color="#94A3B8", line_width=1.5)

    # Quadrant annotations
    fig.add_annotation(x=1, y=0.9, text="Ưu tiên Cải thiện", showarrow=False, font=dict(color='#DC2626', size=14, weight='bold'), xref="paper", yref="paper")
    fig.add_annotation(x=1, y=0.1, text="Duy trì & Phát huy", showarrow=False, font=dict(color='#10B981', size=14, weight='bold'), xref="paper", yref="paper")

    fig.update_layout(
        height=450,
        margin=dict(l=20, r=20, t=40, b=40),
        xaxis_title="Hiệu suất (Điểm trung bình)",
        yaxis_title="Tác động (Tương quan với EI)",
        xaxis=dict(range=[1, 5.3], gridcolor='rgba(226,232,240,0.5)'),
        yaxis=dict(gridcolor='rgba(226,232,240,0.5)'),
        plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
        font=dict(family='Exo 2'),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    st.plotly_chart(fig, use_container_width=True, key="narrative_flow_chart_action_matrix")

    # Display list of Top Priorities
    top_priority = rdf[rdf['Priority'] == 'Ưu tiên cao'].head(5)
    if not top_priority.empty:
        st.markdown("<br>", unsafe_allow_html=True)
        # AI 90-Day Action Plan Insight
        prompt = (
            f"Bạn là Senior Data Analyst & HR Consultant. DỰA VÀO Ma trận Hành động của {group_id}, "
            f"đây là top các yếu tố 'Ưu tiên cao' (Điểm thấp nhưng Tương quan mạnh với EI) "
            f"— CHỈ phân tích từ dữ liệu này:\n"
            f"{top_priority[['Q', 'Label', 'Mean', 'Correlation']].to_dict('records')}\n\n"
            f"Yêu cầu:\n"
            f"1. Tại sao cải thiện các yếu tố này mang lại ROI cao nhất? Dẫn chứng bằng số tương quan và điểm.\n"
            f"2. Đề xuất Kế hoạch 90 ngày gồm 3 bước thực chiến.\n"
            f"Viết 2 đoạn văn ngắn. KHÔNG bịa thêm dữ liệu ngoài danh sách trên."
        )
        render_ai_insight_card("Kế hoạch Hành động 90 ngày (90-Day Action Plan)", {"top_priority": top_priority.to_dict('records')}, prompt, badge="Act 4 Insight")


def _render_hidden_risks(df, group_id):
    """Render phân tích rủi ro tiềm ẩn (khi không có mâu thuẫn)."""
    from shared.codebook import get_codebook, get_question_label
    codebook = get_codebook(group_id)
    likert_qs = [q for q, info in codebook.items() if info['loại'] == 'likert' and q in df.columns]
    
    if not likert_qs:
        st.info("Không có dữ liệu câu hỏi Likert để phân tích rủi ro.")
        return
        
    scores = []
    for q in likert_qs:
        mean_score = df[q].mean()
        if pd.notna(mean_score):
            scores.append({'Q': q, 'Label': get_question_label(group_id, q), 'Score': mean_score})
            
    if not scores:
        return
        
    sdf = pd.DataFrame(scores).sort_values('Score', ascending=True).head(5)
    
    st.markdown("""
    <div style="background:#F8FAFC;border:1px solid #E2E8F0;border-radius:12px;padding:16px 20px;margin-bottom:20px;">
        <div style="font-size:0.82rem;color:#64748B;margin-bottom:8px;">
            Không phát hiện mâu thuẫn dữ liệu lớn, nhưng đây là <strong>Top 5 rủi ro tiềm ẩn (Hidden Risks)</strong> dựa trên các yếu tố có điểm thấp nhất:
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Render Bar chart
    fig = go.Figure(go.Bar(
        x=sdf['Score'], y=sdf['Label'], orientation='h',
        marker=dict(color='#EF4444', cornerradius=4),
        text=[f"{v:.2f}" for v in sdf['Score']],
        textposition='outside',
        textfont=dict(size=12, color='#0A1F44', family='Exo 2')
    ))
    fig.update_layout(
        height=300, margin=dict(l=10, r=40, t=10, b=10),
        xaxis=dict(range=[1, 5.3], dtick=0.5, gridcolor='rgba(226,232,240,0.6)'),
        yaxis=dict(automargin=True, autorange="reversed"),
        plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
        font=dict(family='Exo 2')
    )
    st.plotly_chart(fig, use_container_width=True, key="narrative_flow_chart_hidden_risks")
    
    # Thêm Heatmap phân rã theo phòng ban / vùng
    group_col = None
    if 'tên_bc' in df.columns and df['tên_bc'].nunique() > 1:
        group_col = 'tên_bc'
    elif 'vùng' in df.columns and df['vùng'].nunique() > 1:
        group_col = 'vùng'
        
    if group_col:
        st.markdown(f"<div style='font-size:0.9rem;font-weight:700;color:#64748B;margin-top:20px;margin-bottom:10px;'>Phân rã Rủi ro theo {group_col.replace('_', ' ').title()}</div>", unsafe_allow_html=True)
        top_5_qs = sdf['Q'].tolist()
        heatmap_data = df.groupby(group_col)[top_5_qs].mean().round(2)
        
        fig_hm = go.Figure(data=go.Heatmap(
            z=heatmap_data.values,
            x=[get_question_label(group_id, q) for q in heatmap_data.columns],
            y=heatmap_data.index,
            colorscale='RdYlGn',
            zmin=1, zmax=5,
            text=heatmap_data.values,
            texttemplate="%{text:.2f}",
            showscale=False
        ))
        fig_hm.update_layout(
            height=max(250, len(heatmap_data) * 40),
            margin=dict(l=10, r=10, t=10, b=80),
            xaxis=dict(tickangle=30),
            yaxis=dict(autorange="reversed"),
            font=dict(family='Exo 2')
        )
        st.plotly_chart(fig_hm, use_container_width=True, key="narrative_flow_chart_hidden_risks_heatmap")
    
    # AI Insight
    prompt = (
        f"Bạn là Senior Data Analyst. Đơn vị này không có mâu thuẫn dữ liệu nghiêm trọng, "
        f"nhưng đây là 5 câu hỏi có điểm thấp nhất (thang 5) — DỰA CHÍNH XÁC VÀO DỮ LIỆU NÀY:\n"
        f"{sdf.to_dict('records')}\n\n"
        f"Phân tích (CHỈ dùng dữ liệu đã cung cấp, KHÔNG bịa thêm):\n"
        f"1. Những điểm yếu này phản ánh vấn đề gì về môi trường làm việc hay chính sách?\n"
        f"2. Nếu không cải thiện, rủi ro ngầm (Hidden Risk) lớn nhất là gì?\n"
        f"Viết 2 đoạn văn ngắn gọn, phân tích sâu."
    )
    render_ai_insight_card("Phân tích Rủi ro Tiềm ẩn (Hidden Risks)", {"bottom_scores": sdf.to_dict('records')}, prompt, badge="Act 2 Insight")


def _render_weakness_deep_dive(df, group_id):
    """Render deep dive vào điểm yếu lớn nhất (khi không có mâu thuẫn)."""
    from shared.codebook import get_codebook, get_question_label
    codebook = get_codebook(group_id)
    likert_qs = [q for q, info in codebook.items() if info['loại'] == 'likert' and q in df.columns]
    
    if not likert_qs:
        return
        
    # Lấy câu hỏi thấp nhất
    scores = [(q, df[q].mean()) for q in likert_qs if pd.notna(df[q].mean())]
    if not scores:
        return
        
    scores.sort(key=lambda x: x[1])
    worst_q, worst_score = scores[0]
    worst_label = get_question_label(group_id, worst_q)
    
    # Phân bố điểm của worst_q
    dist = df[worst_q].value_counts(normalize=True).sort_index() * 100
    dist_dict = {f"Điểm {k}": f"{v:.1f}%" for k, v in dist.items()}
    
    st.markdown(f"""
    <div style="background:white;border:1px solid #E2E8F0;border-radius:12px;padding:20px 24px;margin-bottom:20px;">
        <div style="font-size:0.72rem;color:#64748B;text-transform:uppercase;letter-spacing:0.08em;margin-bottom:6px;">
            Vấn đề cốt lõi (Bottom #1)
        </div>
        <div style="font-size:1.05rem;font-weight:700;color:#0A1F44;margin-bottom:12px;">
            {worst_q}: {worst_label} (Điểm: {worst_score:.2f}/5)
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # 1. Biểu đồ phân bố điểm
    fig_dist = go.Figure(go.Bar(
        x=[f"{int(k)} sao" for k in dist.index], y=dist.values,
        marker=dict(color='#8B5CF6', cornerradius=4),
        text=[f"{v:.1f}%" for v in dist.values],
        textposition='outside',
        textfont=dict(size=12, color='#0A1F44', family='Exo 2')
    ))
    fig_dist.update_layout(
        title=dict(text="Tỷ lệ phân bố điểm đánh giá", font=dict(size=14, color='#475569')),
        height=250, margin=dict(l=10, r=10, t=40, b=10),
        yaxis=dict(showgrid=True, gridcolor='rgba(226,232,240,0.6)', range=[0, max(dist.values)*1.2]),
        plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font=dict(family='Exo 2')
    )
    st.plotly_chart(fig_dist, use_container_width=True, key="narrative_flow_chart_weakness_dist")

    # 2. Phân rã theo vùng/phòng ban
    group_col = None
    if 'tên_bc' in df.columns and df['tên_bc'].nunique() > 1:
        group_col = 'tên_bc'
    elif 'vùng' in df.columns and df['vùng'].nunique() > 1:
        group_col = 'vùng'
        
    if group_col:
        region_scores = df.groupby(group_col)[worst_q].mean().dropna().sort_values()
        
        fig_brk = go.Figure(go.Bar(
            x=region_scores.values, y=region_scores.index, orientation='h',
            marker=dict(color='#EF4444', cornerradius=4),
            text=[f"{v:.2f}" for v in region_scores.values],
            textposition='outside',
            textfont=dict(size=12, color='#0A1F44', family='Exo 2')
        ))
        fig_brk.update_layout(
            title=dict(text=f"Điểm '{worst_q}' theo {group_col.replace('_', ' ').title()} (Vùng kéo dữ liệu xuống)", font=dict(size=14, color='#475569')),
            height=max(250, len(region_scores) * 35), margin=dict(l=10, r=40, t=40, b=10),
            xaxis=dict(range=[1, 5.3], dtick=0.5, gridcolor='rgba(226,232,240,0.6)'),
            yaxis=dict(automargin=True, autorange="reversed"),
            plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font=dict(family='Exo 2')
        )
        st.plotly_chart(fig_brk, use_container_width=True, key="narrative_flow_chart_weakness_breakdown")

    
    # AI Deep Dive
    prompt = (
        f"Bạn là Senior Data Analyst. DỰA VÀO DỮ LIỆU THỰC TẾ SAU "
        f"(KHÔNG BỊA THÊM):\n"
        f"Yếu tố yếu nhất: '{worst_q}: {worst_label}' — Điểm TB = {worst_score:.2f}/5.\n"
        f"Phân bố điểm: {dist_dict}\n\n"
        f"Áp dụng 5 Whys:\n"
        f"1. Nguyên nhân gốc rễ khiến nhân viên đánh giá thấp yếu tố này?\n"
        f"2. Đề xuất 1 hành động can thiệp cụ thể, khả thi trong ngắn hạn.\n"
        f"Viết ngắn gọn, sắc bén. CHỈ dùng dữ liệu đã cung cấp."
    )
    render_ai_insight_card(f"AI Deep Dive: Root Cause của {worst_q}", {"metric": worst_q, "score": worst_score}, prompt, badge="Deep Dive")


# ═══════════════════════════════════════════════════════════════
# ACT 5: EMPLOYEE VOICE — MONG MUỐN THEO ĐƠN VỊ
# ═══════════════════════════════════════════════════════════════

@st.fragment
def _render_employee_voice(df, group_id, cfg):
    """
    Phần "Tiếng nói nhân viên" — chọn đơn vị rồi AI phân tích
    các câu hỏi mở (Q34: Điều cần thay đổi/cải thiện) theo từng đơn vị.
    """
    _BAD_VALS = {None, 'nan', 'none', '', 'n/a', 'na'}

    # Tìm cột open-text cần cải thiện (Q34 ưu tiên, fallback Q33/Q32)
    open_col = None
    for cand in ['Q34', 'Q33', 'Q32']:
        if cand in df.columns:
            open_col = cand
            break

    if open_col is None:
        st.info("Không tìm thấy cột câu hỏi mở trong dữ liệu.")
        return

    # Kiểm tra có cột tổ chức không
    has_division   = 'division'   in df.columns
    has_department = 'department' in df.columns
    has_section    = 'section'    in df.columns

    if not (has_division or has_department or has_section):
        st.info("Đây là nhóm không có phân cấp đơn vị (phóng ban/vùng). Phân tích đang dùng toàn bộ nhóm.")
        _run_voice_analysis(df, open_col, group_id, "Đồng bộ toàn nhóm", cfg)
        return

    # ── BUILD DROPDOWN OPTIONS ──
    color = "#8B5CF6"
    st.markdown(f"""
    <div style="background:#FFFFFF;border:1px solid #E2E8F0;border-left:4px solid {color};
                border-radius:12px;padding:24px 28px;margin-bottom:20px;">
        <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:14px;">
            <div>
                <span style="font-size:0.68rem;font-weight:700;letter-spacing:0.1em;text-transform:uppercase;
                             color:{color};display:block;margin-bottom:4px;">ACT 5 · AI ANALYSIS</span>
                <span style="font-size:1.2rem;font-weight:800;color:#0A1F44;letter-spacing:-0.02em;">Tiếng Nói Nhân Viên (Employee Voice)</span>
            </div>
        </div>
        <p style="font-size:0.83rem;color:#64748B;margin:0 0 18px;line-height:1.65;">
            Phân tích chuyên sâu các phản hồi mở từ nhân viên bằng trí tuệ nhân tạo.
            Lắng nghe những mong muốn thầm kín và cảm xúc chân thật nhất đằng sau những con số khảo sát.
        </p>
        <div style="background:#F8FAFC;border:1px solid #F1F5F9;border-radius:8px;padding:12px 16px;">
            <div style="font-size:0.75rem;font-weight:700;color:#64748B;text-transform:uppercase;letter-spacing:0.05em;margin-bottom:2px;">Lọc theo Đơn vị hành chính</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    col_sel1, col_sel2, col_sel3 = st.columns([1, 1, 1])

    # Level 1: Division
    sel_div = None
    if has_division:
        divs = sorted([v for v in df['division'].dropna().unique()
                       if str(v).strip().lower() not in _BAD_VALS])
        divs_opts = ['— Tất cả (toàn nhóm) —'] + divs
        with col_sel1:
            sel_div = st.selectbox('Khối / Division',
                                   divs_opts, key=f'ev_div_{group_id}')
        if sel_div == '— Tất cả (toàn nhóm) —':
            sel_div = None

    # Filter theo division
    df_filt = df.copy()
    if sel_div and has_division:
        df_filt = df_filt[df_filt['division'] == sel_div]

    # Level 2: Department
    sel_dept = None
    if has_department and sel_div is not None:
        depts = sorted([v for v in df_filt['department'].dropna().unique()
                        if str(v).strip().lower() not in _BAD_VALS])
        if depts:
            depts_opts = ['— Tất cả —'] + depts
            with col_sel2:
                sel_dept = st.selectbox('Phòng ban / Department',
                                        depts_opts, key=f'ev_dept_{group_id}')
            if sel_dept == '— Tất cả —':
                sel_dept = None

    if sel_dept and has_department:
        df_filt = df_filt[df_filt['department'] == sel_dept]

    # Level 3: Section
    sel_sec = None
    if has_section and sel_dept is not None:
        secs = sorted([v for v in df_filt['section'].dropna().unique()
                       if str(v).strip().lower() not in _BAD_VALS])
        if secs:
            secs_opts = ['— Tất cả —'] + secs
            with col_sel3:
                sel_sec = st.selectbox('Vùng / Section',
                                       secs_opts, key=f'ev_sec_{group_id}')
            if sel_sec == '— Tất cả —':
                sel_sec = None

    if sel_sec and has_section:
        df_filt = df_filt[df_filt['section'] == sel_sec]

    # Determine unit label for display
    unit_label = sel_sec or sel_dept or sel_div or 'Đồng bộ toàn nhóm'

    # ── SUMMARY ROW ──
    n_total   = len(df_filt)
    valid_responses = df_filt[open_col].dropna().apply(
        lambda x: str(x).strip()
    ).loc[lambda s: (s.str.len() > 5) & (~s.str.lower().isin(_BAD_VALS))]
    n_responses = len(valid_responses)

    st.markdown(f"""
    <div style="display:flex;gap:16px;flex-wrap:wrap;margin-bottom:16px;">
        <div style="background:#F8FAFC;border:1px solid #E2E8F0;border-radius:10px;
                    padding:10px 18px;font-size:0.82rem;color:#475569;">
            <strong>{n_total:,}</strong> nhân viên tại <em>{unit_label}</em>
        </div>
        <div style="background:#EFF6FF;border:1px solid #BFDBFE;border-radius:10px;
                    padding:10px 18px;font-size:0.82rem;color:#1D4ED8;">
            <strong>{n_responses:,}</strong> phản hồi có nội dung về cải thiện
        </div>
    </div>
    """, unsafe_allow_html=True)

    if n_responses < 3:
        st.info(f"Không đủ dữ liệu (≥ 3 phản hồi) tại đơn vị này để phân tích.")
        return

    _run_voice_analysis(df_filt, open_col, group_id, unit_label, cfg)


def _run_voice_analysis(df_unit, open_col, group_id, unit_label, cfg):
    """
    Gọi Groq AI (llama-3.3-70b-versatile) phân tích các câu trả lời mở
    và trích xuất top mong muốn thay đổi của nhân viên tại đơn vị.
    """
    import json, hashlib
    from utils.ai_generator import get_groq_clients_all, format_ai_html

    _BAD_VALS = {None, 'nan', 'none', '', 'n/a', 'na'}

    responses = df_unit[open_col].dropna().apply(str).apply(str.strip)
    responses = responses[responses.str.len() > 5]
    responses = responses[~responses.str.lower().isin(_BAD_VALS)]

    if len(responses) == 0:
        st.info("Không có phản hồi đủ ý nghĩa.")
        return

    # Lấy tối đa 120 responses (giới hạn token)
    sample = responses.sample(min(120, len(responses)), random_state=42).tolist()
    responses_text = "\n".join([f"- {r}" for r in sample])

    group_name = cfg.get('label', group_id)
    prompt_key = hashlib.md5(
        (MASTER_REPORT_VOICE_VERSION + unit_label + responses_text[:200]).encode()
    ).hexdigest()
    cache_key  = f"ev_voice_{group_id}_{prompt_key}"

    # Theme frequency chart (no AI, always visible)
    _render_voice_theme_chart(responses, group_id, unit_label)

    # Các button phân tích theo loại
    col_b1, col_b2, col_b3 = st.columns(3)
    with col_b1:
        run_desires = st.button(f"Phân tích Mong muốn",
                                key=f"btn_desires_{group_id}_{unit_label[:20]}")
    with col_b2:
        run_sentiment = st.button(f"Phân tích Cảm xúc",
                                  key=f"btn_sentiment_{group_id}_{unit_label[:20]}")
    with col_b3:
        if cache_key in st.session_state:
            if st.button("Phân tích lại", key=f"btn_rerun_{group_id}_{unit_label[:20]}"):
                del st.session_state[cache_key]
                st.rerun()

    # Xác định loại phân tích
    if run_desires:
        st.session_state[f'ev_mode_{group_id}'] = 'desires'
        if cache_key in st.session_state:
            del st.session_state[cache_key]
    elif run_sentiment:
        st.session_state[f'ev_mode_{group_id}'] = 'sentiment'
        if cache_key in st.session_state:
            del st.session_state[cache_key]

    mode = st.session_state.get(f'ev_mode_{group_id}', 'desires')

    if mode == 'desires':
        ai_prompt = f"""Bạn đang viết theo văn phong của báo cáo GHN EES 2026 Deep Analyst.

Dưới đây là {len(sample)} phản hồi THỰC TẾ ẩn danh của nhân viên thuộc nhóm «{group_name}», đơn vị «{unit_label}», khi được hỏi: "Bạn mong muốn điều gì cần thay đổi hoặc cải thiện tại công ty?":

{responses_text}

NHIỆM VỤ:
Đọc kỹ các phản hồi này, gom nhóm các ý lặp lại nhiều nhất và viết phần nhận định giống mục "điểm cần đọc kỹ" trong báo cáo.
Mọi nhận định và dẫn chứng phải bám đúng tập phản hồi đang có. Không dùng dữ liệu của đơn vị khác và không tự bịa chi tiết.

Trình bày bằng tiếng Việt theo cấu trúc sau:

1. Bức tranh chung:
- Viết 2 đến 3 câu mở đầu, nêu nhận định chính về điều nhân viên đang nhắc nhiều nhất tại đơn vị này.
- Nếu dữ liệu phân tán hoặc chưa đủ chắc, phải nói rõ mức độ thận trọng khi diễn giải.

2. Các điểm nhân viên đang nhắc nhiều:
- Chọn 3 đến 5 ý quan trọng nhất theo tần suất và mức độ ảnh hưởng.
- Mỗi ý viết gọn theo nhịp:
  [Tên ý] -> điều nhân viên đang nói -> điều này cho thấy gì ở góc độ vận hành/quản trị -> 1 trích dẫn ngắn lấy nguyên văn từ dữ liệu.
- Không cần cố ước lượng phần trăm nếu không đếm được tương đối chắc từ tập phản hồi.

3. Điều cần lưu ý:
- Nêu 1 ý đáng chú ý nhất cần theo dõi thêm, theo giọng thận trọng của báo cáo nội bộ.

4. Hàm ý hành động:
- Đưa ra 1 đến 2 ưu tiên hành động ngắn, cụ thể.

YÊU CẦU TONE:
- Viết giống báo cáo phân tích nội bộ, không viết như chatbot.
- Câu ngắn, chắc, mạch lạc.
- Không dùng từ kịch tính, không đặt nhãn sáng tác cho vấn đề.
- Không có lời chào và không có kết luận dài dòng."""
    else:
        ai_prompt = f"""Bạn đang viết theo văn phong của báo cáo GHN EES 2026 Deep Analyst.

Dưới đây là {len(sample)} phản hồi ẩn danh THỰC TẾ của nhân viên thuộc nhóm «{group_name}», đơn vị «{unit_label}»:

{responses_text}

NHIỆM VỤ:
Đọc kỹ toàn bộ phản hồi để viết phần nhận định về sắc thái cảm xúc và các lớp lo ngại nổi bật. Báo cáo phải dựa hoàn toàn trên dữ liệu đang có.

Trình bày bằng tiếng Việt theo cấu trúc sau:

1. Bức tranh cảm xúc chung:
- Viết 2 đến 3 câu nêu sắc thái chủ đạo của tập phản hồi.
- Chỉ đưa ra tỷ lệ ước lượng nếu thật sự có thể đếm tương đối trực tiếp từ dữ liệu. Nếu không chắc, dùng mô tả định tính như "nghiêng về tiêu cực", "khá phân tán", "thiên về góp ý thực dụng".

2. Những lớp cảm xúc hoặc lo ngại nổi bật:
- Chọn 2 đến 4 ý quan trọng nhất.
- Mỗi ý cần gắn với bằng chứng cụ thể từ phản hồi và giải thích ngắn nó phản ánh điều gì trong trải nghiệm làm việc.
- Khi diễn giải, giữ giọng thận trọng như báo cáo: "điều này cho thấy", "có thể đến từ", "đáng chú ý là".

3. Điều cần lưu ý:
- Nêu 1 tín hiệu đáng quan tâm nhất, nhưng chỉ ở mức dữ liệu cho phép.
- Nếu chưa đủ chắc để coi là rủi ro hệ thống, phải nói rõ đây mới là tín hiệu cần theo dõi thêm.

4. Hàm ý hành động:
- Đưa ra 1 đến 2 hành động ưu tiên, ngắn và cụ thể.

YÊU CẦU TONE:
- Viết giống báo cáo phân tích nội bộ, không viết như chatbot hay bài tư vấn lên gân.
- Không dùng từ như "red flag", "khủng hoảng", "báo động" nếu dữ liệu không đủ mạnh.
- Không có lời chào hỏi, không kết luận sáo rỗng."""

    # SHOW RAW RESPONSES collapsible
    limit_key = f"ev_limit_{group_id}_{unit_label}"
    if limit_key not in st.session_state:
        st.session_state[limit_key] = 50

    is_expanded = st.session_state[limit_key] > 50

    with st.expander(f"Xem {len(responses)} phản hồi thực tế", expanded=is_expanded):
        current_limit = st.session_state[limit_key]
        import html
        
        html_str = '<div style="max-height: 400px; overflow-y: auto; padding-right: 8px;">'
        for i, r in enumerate(responses.iloc[:current_limit], 1):
            safe_r = html.escape(str(r))
            html_str += (
                f'<div style="background:#F8FAFC;border-left:3px solid #E2E8F0;padding:8px 12px;'
                f'margin-bottom:6px;border-radius:0 6px 6px 0;font-size:0.83rem;color:#475569;">'
                f'<span style="color:#94A3B8;font-size:0.72rem;">{i}.</span> {safe_r}'
                f'</div>'
            )
        html_str += "</div>"
        st.markdown(html_str, unsafe_allow_html=True)
        
        if current_limit < len(responses):
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button(f"Xem thêm 50 phản hồi (Đang hiện {current_limit}/{len(responses)})", key=f"btn_loadmore_{group_id}_{unit_label}"):
                st.session_state[limit_key] += 50
                st.rerun()

    # AI ANALYSIS
    st.markdown("")
    ai_container = st.empty()

    if cache_key in st.session_state:
        cached = st.session_state[cache_key]
        ai_container.markdown(f"""
        <div class="ai-insight-container">
            <div class="ai-header">
                <div class="ai-icon"><svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#FF5200" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9.937 15.5A2 2 0 0 0 8.5 14.063l-6.135-1.582a.5.5 0 0 1 0-.962L8.5 9.936A2 2 0 0 0 9.937 8.5l1.582-6.135a.5.5 0 0 1 .963 0L14.063 8.5A2 2 0 0 0 15.5 9.937l6.135 1.581a.5.5 0 0 1 0 .964L15.5 14.063a2 2 0 0 0-1.437 1.437l-1.582 6.135a.5.5 0 0 1-.963 0z"/><path d="M20 3v4"/><path d="M22 5h-4"/><path d="M4 17v2"/><path d="M5 18H3"/></svg></div>
                <h4 class="ai-title">AI Phân tích Tiếng nói Nhân viên — {unit_label}</h4>
                <div class="ai-badge">{'Mong muốn' if mode == 'desires' else 'Cảm xúc'}</div>
            </div>
            <div class="ai-content">{format_ai_html(cached)}</div>
        </div>
        """, unsafe_allow_html=True)
    elif run_desires or run_sentiment:
        # Gọi Groq streaming với llama-3.3-70b-versatile (tốt nhất cho phân tích định tính)
        VOICE_MODELS = ["llama-3.3-70b-versatile",
                        "llama-3.1-8b-instant",
                        "mixtral-8x7b-32768"]
        all_clients = get_groq_clients_all()
        full_text = ""
        success = False

        def _build_voice_html(content, typing=False):
            cursor = "<span style='border-right:2px solid #FF5200;margin-left:2px'></span>" if typing else ""
            return f"""
            <div class="ai-insight-container">
                <div class="ai-header">
                    <div class="ai-icon"><svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#FF5200" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9.937 15.5A2 2 0 0 0 8.5 14.063l-6.135-1.582a.5.5 0 0 1 0-.962L8.5 9.936A2 2 0 0 0 9.937 8.5l1.582-6.135a.5.5 0 0 1 .963 0L14.063 8.5A2 2 0 0 0 15.5 9.937l6.135 1.581a.5.5 0 0 1 0 .964L15.5 14.063a2 2 0 0 0-1.437 1.437l-1.582 6.135a.5.5 0 0 1-.963 0z"/><path d="M20 3v4"/><path d="M22 5h-4"/><path d="M4 17v2"/><path d="M5 18H3"/></svg></div>
                    <h4 class="ai-title">AI Phân tích Tiếng nói Nhân viên — {unit_label}</h4>
                    <div class="ai-badge">{'Mong muốn' if mode == 'desires' else 'Cảm xúc'}</div>
                </div>
                <div class="ai-content">{format_ai_html(content)}{cursor}</div>
            </div>"""

        with st.spinner("AI đang phân tích phản hồi..."):
            for client in all_clients:
                for model in VOICE_MODELS:
                    try:
                        stream = client.chat.completions.create(
                            messages=[
                                {
                                    "role": "system",
                                    "content": (
                                        "Bạn là chuyên gia phân tích định tính và cảm xúc trong lĩnh vực "
                                        "Quản trị Nhân lực. Luôn viết bằng tiếng Việt. Chỉ sử dụng dữ liệu "
                                        "và trích dẫn được cung cấp. Tỷ lệ ước lượng chỉ được đưa ra khi có "
                                        "thể đếm trực tiếp từ tập phản hồi và phải ghi rõ là ước lượng.\n\n"
                                        + get_master_report_voice_prompt()
                                    ),
                                },
                                {"role": "user", "content": ai_prompt}
                            ],
                            model=model,
                            temperature=0.2,
                            max_tokens=1200,
                            stream=True
                        )
                        for chunk in stream:
                            if chunk.choices[0].delta.content:
                                full_text += chunk.choices[0].delta.content
                                ai_container.markdown(
                                    _build_voice_html(full_text, typing=True),
                                    unsafe_allow_html=True
                                )
                        success = True
                        break
                    except Exception as e:
                        last_error = str(e)
                        continue # Try the next model/client regardless of error type
                if success:
                    break

        if success:
            st.session_state[cache_key] = full_text
            ai_container.markdown(_build_voice_html(full_text), unsafe_allow_html=True)
        else:
            err_msg = last_error if 'last_error' in locals() else 'Unknown error'
            ai_container.error(f"Không thể kết nối AI. Chi tiết lỗi: {err_msg}")
    else:
        st.info("Chọn đơn vị rồi bấm **Phân tích Mong muốn** hoặc **Phân tích Cảm xúc** để xem kết quả.")




# ═══════════════════════════════════════════════════════════════
# CHART HELPERS — GROUP OVERVIEW (enhancements for Acts 1–5)
# ═══════════════════════════════════════════════════════════════

def _render_deep_dive_metric_chart(df, metrics, c_id, index):
    """
    Act 3 — always-visible metric chart for each contradiction.
    Dispatches to existing chart functions with a unique key suffix
    so Act 2 and Act 3 can both render the same contradiction type.
    """
    ks = f"_act3_{index}"
    if c_id == 'TENURE_CLIFF':
        _render_tenure_cliff_chart(df, metrics, key_suffix=ks)
    elif c_id in ('INFO_GAP', 'FAIRNESS_GAP'):
        _render_gap_chart(df, metrics, c_id, key_suffix=ks)
    elif c_id in ('PRIDE_PARADOX', 'INCOME_PARADOX', 'SILENT_DISENGAGED',
                  'MEI_SHIELD_FAIL', 'BURNOUT_TRAP', 'LEADERSHIP_HALO'):
        _render_paradox_chart(df, metrics, c_id, key_suffix=ks)
    elif c_id == 'BURNOUT_BLIND_SPOT':
        _render_burnout_blind_chart(df, metrics, key_suffix=ks)
    elif c_id == 'GLASS_CEILING':
        _render_glass_ceiling_chart(df, metrics, key_suffix=ks)
    # Unknown type → EI distribution still shows in right column


def _render_ei_distribution_chart(df, key_suffix=""):
    """
    Phân phối Engagement Index — 3 nhóm: Không gắn kết / Trung lập / Gắn kết.
    Luôn hiển thị nếu có cột EI — không phụ thuộc sub-group hay region.
    """
    if 'EI' not in df.columns:
        return
    ei = df['EI'].dropna()
    if len(ei) < 5:
        return
    total = len(ei)
    d_pct = (ei < 50).sum() / total * 100
    n_pct = ((ei >= 50) & (ei < 75)).sum() / total * 100
    e_pct = (ei >= 75).sum() / total * 100
    avg_ei = ei.mean()

    fig = go.Figure(go.Bar(
        x=['Không gắn kết', 'Trung lập', 'Gắn kết'],
        y=[d_pct, n_pct, e_pct],
        marker=dict(color=['#EF4444', '#F59E0B', '#10B981'], cornerradius=6),
        text=[f"{v:.1f}%<br>({int(v / 100 * total)})" for v in [d_pct, n_pct, e_pct]],
        textposition='outside',
        textfont=dict(size=11, color='#0A1F44', family='Exo 2'),
        hovertemplate='<b>%{x}</b><br>%{y:.1f}%<extra></extra>',
    ))
    fig.update_layout(
        title=dict(text=f"Phân phối EI  (TB: {avg_ei:.1f}%)",
                   font=dict(size=13, color='#475569', family='Exo 2')),
        height=270,
        margin=dict(l=10, r=10, t=45, b=30),
        yaxis=dict(range=[0, max(d_pct, n_pct, e_pct) * 1.4],
                   ticksuffix='%', gridcolor='rgba(226,232,240,0.5)'),
        xaxis=dict(tickfont=dict(size=11, color='#475569')),
        plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
        font=dict(family='Exo 2', size=12),
    )
    st.plotly_chart(fig, use_container_width=True,
                    key=f"ei_dist_chart{key_suffix}")


def _render_act1_radar_chart(pdf, group_name):
    """
    Radar (spider) chart cho 5 trụ cột.
    Hiển thị 'hình dạng' cân bằng / mất cân bằng của trải nghiệm — bổ sung cho bar chart.
    """
    if pdf is None or len(pdf) < 3:
        return
    categories = pdf['Trụ cột'].tolist()
    values     = pdf['Điểm TB'].tolist()
    cats_c = categories + [categories[0]]
    vals_c = values     + [values[0]]

    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=vals_c, theta=cats_c,
        fill='toself',
        fillcolor='rgba(67,24,255,0.10)',
        line=dict(color='#4318FF', width=2.5),
        marker=dict(size=7, color='#4318FF'),
        name='Điểm TB',
    ))
    fig.add_trace(go.Scatterpolar(
        r=[4.0] * len(cats_c), theta=cats_c,
        fill='none',
        line=dict(color='#10B981', width=1.5, dash='dot'),
        name='Ngưỡng Tốt (4.0)',
        marker=dict(size=0),
    ))
    fig.update_layout(
        polar=dict(
            radialaxis=dict(range=[1, 5], dtick=1,
                            gridcolor='rgba(226,232,240,0.7)',
                            tickfont=dict(size=9)),
            angularaxis=dict(tickfont=dict(size=11, color='#475569', family='Exo 2')),
            bgcolor='rgba(0,0,0,0)',
        ),
        title=dict(text=f"Hình dạng trải nghiệm — {group_name}",
                   font=dict(size=13, color='#475569', family='Exo 2')),
        height=310,
        margin=dict(l=40, r=40, t=55, b=20),
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(family='Exo 2'),
        showlegend=True,
        legend=dict(orientation='h', yanchor='bottom', y=-0.12,
                    xanchor='center', x=0.5, font=dict(size=11)),
    )
    st.plotly_chart(fig, use_container_width=True, key="narrative_act1_radar_chart")


def _render_voice_theme_chart(responses, group_id, unit_label=""):
    """
    Theme-bucket frequency chart từ open-text — hiển thị ngay, không cần AI.
    Buckets 8 chủ đề HR cốt lõi bằng Vietnamese keyword matching.
    """
    import re

    THEMES = {
        'Lương & Phúc lợi':      ['lương', 'thưởng', 'thu nhập', 'tăng lương', 'phúc lợi', 'đãi ngộ', 'chế độ', 'trợ cấp'],
        'Quản lý & Lãnh đạo':    ['quản lý', 'sếp', 'lãnh đạo', 'quản lí', 'cấp trên', 'giám sát'],
        'Đào tạo & Phát triển':  ['đào tạo', 'học', 'phát triển', 'kỹ năng', 'thăng tiến', 'lộ trình', 'cơ hội'],
        'Khối lượng & Áp lực':   ['áp lực', 'quá tải', 'khối lượng', 'stress', 'mệt', 'kiệt sức', 'tăng ca'],
        'Môi trường làm việc':   ['môi trường', 'văn phòng', 'không khí', 'đồng nghiệp', 'đội nhóm', 'văn hóa', 'thiết bị'],
        'Thông tin & Minh bạch': ['thông tin', 'minh bạch', 'rõ ràng', 'thông báo', 'giao tiếp', 'truyền thông'],
        'Ghi nhận & Công nhận':  ['ghi nhận', 'công nhận', 'khen', 'đánh giá', 'kpi', 'đóng góp'],
        'Quy trình & Công cụ':   ['quy trình', 'hệ thống', 'công cụ', 'phần mềm', 'ứng dụng', 'bất hợp lý'],
    }

    if len(responses) < 3:
        return

    all_text = ' '.join(responses.tolist()).lower()
    all_text = re.sub(r'[^\w\s]', ' ', all_text)

    theme_counts = {t: sum(all_text.count(kw) for kw in kws)
                    for t, kws in THEMES.items()}
    theme_counts = {t: c for t, c in theme_counts.items() if c > 0}

    if not theme_counts:
        return

    sorted_t = sorted(theme_counts.items(), key=lambda x: x[1], reverse=True)
    labels  = [t[0] for t in sorted_t]
    counts  = [t[1] for t in sorted_t]
    max_c   = max(counts)
    colors  = ['#EF4444' if c / max_c >= 0.7 else '#F59E0B' if c / max_c >= 0.4 else '#6366F1'
               for c in counts]

    fig = go.Figure(go.Bar(
        x=counts, y=labels, orientation='h',
        marker=dict(color=colors, cornerradius=4),
        text=counts, textposition='outside',
        textfont=dict(size=11, color='#475569', family='Exo 2'),
    ))
    fig.update_layout(
        title=dict(text=f"Chủ đề nổi bật từ {len(responses)} phản hồi — {unit_label}",
                   font=dict(size=13, color='#475569', family='Exo 2')),
        height=max(280, len(sorted_t) * 38 + 60),
        margin=dict(l=10, r=50, t=45, b=10),
        xaxis=dict(title='Số lần đề cập (ước tính)', gridcolor='rgba(226,232,240,0.5)'),
        yaxis=dict(automargin=True, autorange='reversed'),
        plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
        font=dict(family='Exo 2', size=12),
    )
    # Use a stable key: group_id + first 20 chars of unit_label (spaces replaced)
    safe_label = unit_label[:20].replace(' ', '_').replace('/', '_')
    st.plotly_chart(fig, use_container_width=True,
                    key=f"voice_theme_chart_{group_id}_{safe_label}")


# ═══════════════════════════════════════════════════════════════════════
# UNIT REPORT MODE  —  7 phần báo cáo đơn vị (department / section)
# ═══════════════════════════════════════════════════════════════════════

def _render_unit_report(df, cfg, group_id, df_bench=None):
    """
    Entry point cho chế độ 'Báo cáo đơn vị'.
    Người dùng chọn Division → Department → Section → toàn bộ báo cáo
    lọc theo đơn vị đó, so sánh vs benchmark (toàn nhóm).
    """
    from utils.unit_report import (
        get_org_options, build_unit_df, get_unit_label, get_unit_level,
        pillar_scores_comparison, kpis_with_delta, get_open_col,
        get_participation_rate,
    )
    from utils.credibility import confidence_badge, triangulate_pillar

    # Use full group df as benchmark (or fall back to scoped df)
    if df_bench is None:
        df_bench = df

    org = get_org_options(df)
    has_div  = bool(org["division"])
    has_dept = bool(org["department"])
    has_sec  = bool(org["section"])

    if not has_div and not has_dept:
        st.info("Nhóm này không có phân cấp đơn vị. Vui lòng dùng chế độ 'Tổng quan nhóm'.")
        return

    # ── Scope detection for restricted users ─────────────────────────────
    _auth = st.session_state.get("user_authorization", {})
    from utils.authorization import resolve_data_scope as _rds
    _scope = _rds(_auth) if isinstance(_auth, dict) else {"unrestricted": True}
    _restricted = not _scope.get("unrestricted", True)
    _scope_level = (_scope.get("level") or "").upper()

    def _first_val(col):
        return (
            df[col].dropna().iloc[0]
            if col in df.columns and not df[col].dropna().empty else None
        )

    # ── Unit selector ──────────────────────────────────────────────────
    sel_div = sel_dept = sel_sec = None

    # SECTION-scoped: skip dropdowns, auto-lock to authorized section
    if _restricted and _scope_level == "SECTION" and len(df) > 0:
        sel_div  = _first_val("division")
        sel_dept = _first_val("department")
        sel_sec  = _first_val("section")
        _locked_label = sel_sec or sel_dept or sel_div or "đơn vị của bạn"
        st.markdown(
            f'<div style="background:#EFF6FF;border:1px solid #BFDBFE;border-radius:10px;'
            f'padding:10px 18px;margin-bottom:8px;font-size:0.83rem;color:#1D4ED8;">'
            f'Bao cao don vi: <strong>{_locked_label}</strong>'
            f'</div>',
            unsafe_allow_html=True,
        )

    # DEPARTMENT-scoped: auto-lock division+dept, allow section drill-down
    elif _restricted and _scope_level in ("DEPARTMENT", "PHONG_BAN") and len(df) > 0:
        sel_div  = _first_val("division")
        sel_dept = _first_val("department")
        df_after_dept = df[df["department"] == sel_dept] if sel_dept else df
        _, _, _c3 = st.columns(3)
        with _c3:
            if has_sec and sel_dept is not None:
                secs_avail = sorted([
                    v for v in df_after_dept["section"].dropna().unique()
                    if str(v).strip().lower() not in {"nan", "none", "", "n/a"}
                ])
                if secs_avail:
                    opt_sec = ["— Tất cả section —"] + secs_avail
                    sel_sec_raw = st.selectbox("Section / Vùng", opt_sec,
                                               key=f"ur_sec_{group_id}_{sel_dept or 'all'}")
                    if sel_sec_raw != "— Tất cả section —":
                        sel_sec = sel_sec_raw

    # DIVISION-scoped: auto-lock division, allow dept/section drill-down
    elif _restricted and _scope_level in ("DIVISION", "KHOI") and len(df) > 0:
        sel_div = _first_val("division")
        df_after_div = df[df["division"] == sel_div] if sel_div else df
        _c2, _c3 = st.columns([1, 1])
        with _c2:
            if has_dept:
                depts_avail = sorted([
                    v for v in df_after_div["department"].dropna().unique()
                    if str(v).strip().lower() not in {"nan", "none", "", "n/a"}
                ])
                opt_dept = ["— Tất cả phòng ban —"] + depts_avail
                sel_dept_raw = st.selectbox("Phòng ban", opt_dept,
                                            key=f"ur_dept_{group_id}_{sel_div or 'all'}")
                if sel_dept_raw != "— Tất cả phòng ban —":
                    sel_dept = sel_dept_raw
        df_after_dept = df_after_div.copy()
        if sel_dept and has_dept:
            df_after_dept = df_after_dept[df_after_dept["department"] == sel_dept]
        with _c3:
            if has_sec and sel_dept is not None:
                secs_avail = sorted([
                    v for v in df_after_dept["section"].dropna().unique()
                    if str(v).strip().lower() not in {"nan", "none", "", "n/a"}
                ])
                if secs_avail:
                    opt_sec = ["— Tất cả section —"] + secs_avail
                    sel_sec_raw = st.selectbox("Section / Vùng", opt_sec,
                                               key=(
                                                   f"ur_sec_{group_id}_"
                                                   f"{sel_div or 'all'}_{sel_dept or 'all'}"
                                               ))
                    if sel_sec_raw != "— Tất cả section —":
                        sel_sec = sel_sec_raw

    # UNRESTRICTED (Admin / ALL): full dropdown selectors
    else:
        col1, col2, col3 = st.columns(3)

        with col1:
            if has_div:
                opt_div = ["— Chọn khối —"] + org["division"]
                sel_div_raw = st.selectbox("Khối / Division", opt_div,
                                           key=f"ur_div_{group_id}")
                if sel_div_raw != "— Chọn khối —":
                    sel_div = sel_div_raw

        df_after_div = df[df["division"] == sel_div] if sel_div and has_div else df

        with col2:
            if has_dept and sel_div is not None:
                depts_avail = sorted([
                    v for v in df_after_div["department"].dropna().unique()
                    if str(v).strip().lower() not in {"nan","none","","n/a"}
                ])
                opt_dept = ["— Tất cả phòng ban —"] + depts_avail
                sel_dept_raw = st.selectbox("Phòng ban", opt_dept,
                                            key=f"ur_dept_{group_id}_{sel_div or 'all'}")
                if sel_dept_raw != "— Tất cả phòng ban —":
                    sel_dept = sel_dept_raw
            elif has_dept and not has_div:
                opt_dept = ["— Chọn phòng ban —"] + org["department"]
                sel_dept_raw = st.selectbox("Phòng ban", opt_dept,
                                            key=f"ur_dept_nodiv_{group_id}")
                if sel_dept_raw != "— Chọn phòng ban —":
                    sel_dept = sel_dept_raw

        df_after_dept = df_after_div.copy()
        if sel_dept and has_dept:
            df_after_dept = df_after_dept[df_after_dept["department"] == sel_dept]

        with col3:
            if has_sec and sel_dept is not None:
                secs_avail = sorted([
                    v for v in df_after_dept["section"].dropna().unique()
                    if str(v).strip().lower() not in {"nan","none","","n/a"}
                ])
                if secs_avail:
                    opt_sec = ["— Tất cả section —"] + secs_avail
                    sel_sec_raw = st.selectbox("Section / Vùng", opt_sec,
                                               key=(
                                                   f"ur_sec_{group_id}_"
                                                   f"{sel_div or 'all'}_{sel_dept or 'all'}"
                                               ))
                    if sel_sec_raw != "— Tất cả section —":
                        sel_sec = sel_sec_raw

        if sel_div is None and sel_dept is None:
            st.markdown(
                '<div style="background:#EFF6FF;border:1px solid #BFDBFE;border-radius:10px;'
                'padding:12px 18px;margin-top:10px;font-size:0.83rem;color:#1D4ED8;">'
                'Chọn ít nhất <strong>Khối</strong> hoặc <strong>Phòng ban</strong> để xem báo cáo đơn vị.'
                '</div>',
                unsafe_allow_html=True,
            )
            return

    # ── Build unit dataframe ───────────────────────────────────────────
    df_unit = build_unit_df(df, sel_div, sel_dept, sel_sec)
    unit_label = get_unit_label(sel_div, sel_dept, sel_sec)
    unit_level = get_unit_level(sel_div, sel_dept, sel_sec)
    n_unit = len(df_unit)

    if n_unit < 5:
        st.warning(
            f"Đơn vị **{unit_label}** chỉ có {n_unit} người tham gia khảo sát — "
            "không đủ mẫu để phân tích (cần ≥ 5). Vui lòng chọn đơn vị lớn hơn."
        )
        return

    part_rate = get_participation_rate(df_unit, df_bench)
    kpis_d    = kpis_with_delta(df_unit, df_bench)
    pillar_comp = pillar_scores_comparison(df_unit, df_bench, group_id)

    # ── Header banner ──────────────────────────────────────────────────
    badge_html = confidence_badge(n_unit, part_rate)
    st.markdown(
        f'<div style="background:#fff;border:1px solid #E2E8F0;border-left:4px solid #FF5200;'
        f'border-radius:12px;padding:18px 24px;margin-bottom:20px;">'
        f'<div style="font-size:.68rem;font-weight:700;letter-spacing:.1em;text-transform:uppercase;'
        f'color:#FF5200;margin-bottom:4px;">BÁO CÁO ĐƠN VỊ</div>'
        f'<div style="font-size:1.25rem;font-weight:800;color:#0A1F44;letter-spacing:-.02em;">'
        f'{unit_label}</div>'
        f'<div style="margin-top:8px;">{badge_html}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )

    # ── Render 7 phần ─────────────────────────────────────────────────
    _render_unit_p1_context(df_unit, df_bench, unit_label, kpis_d, n_unit)
    _render_unit_p2_radar(pillar_comp, unit_label, group_id)
    _render_unit_p3_pillars(df_unit, df_bench, group_id, cfg, pillar_comp)
    _render_unit_p4_risk(df_unit, df_bench, group_id, unit_level, sel_dept)
    _render_unit_p5_contradictions(df_unit, group_id, cfg)
    _render_unit_p6_voice(df_unit, group_id, cfg, unit_label)
    _render_unit_p7_actions(df_unit, df_bench, group_id, pillar_comp, unit_label)


# ── P1: Bối cảnh & Vị trí ────────────────────────────────────────────

def _render_unit_p1_context(df_unit, df_bench, unit_label, kpis_d, n_unit):
    """P1 — KPI strip với delta so sánh benchmark."""
    st.markdown(_part_header("P1", "Bối cảnh & Vị trí",
                             f"Đơn vị {unit_label} đang đứng ở đâu so với toàn nhóm?",
                             color="#2563EB"), unsafe_allow_html=True)

    def _delta_badge(val, reverse=False):
        """reverse=True: delta dương là xấu (flight risk, burnout)."""
        if val is None:
            return ""
        good = val > 0 if not reverse else val < 0
        color = "#15803D" if good else "#DC2626"
        bg    = "#F0FDF4" if good else "#FEF2F2"
        sign  = "▲" if val > 0 else "▼"
        return (
            f'<span style="background:{bg};color:{color};padding:2px 7px;'
            f'border-radius:5px;font-size:.72rem;font-weight:700;">'
            f'{sign}{abs(val):.1f}</span>'
        )

    metrics = [
        ("Engagement Index", f"{kpis_d['ei_mean']:.2f}%",
         kpis_d["delta_ei"], f"{kpis_d['bench_ei']:.2f}%", False, "#2563EB"),
        ("eNPS", f"{kpis_d['enps_score']:+.0f}",
         kpis_d["delta_enps"], f"{kpis_d['bench_enps']:+.0f}", False, "#7C3AED"),
        ("% Muốn nghỉ", f"{kpis_d['intent_pct_low']:.2f}%",
         kpis_d["delta_flight"], f"{kpis_d['bench_flight']:.2f}%", True, "#DC2626"),
        ("% Burnout", f"{kpis_d['burnout_pct']:.2f}%",
         kpis_d["delta_burnout"], f"{kpis_d['bench_burnout']:.2f}%", True, "#EA580C"),
        ("MEI (QL)", f"{kpis_d.get('mei_avg',0):.2f}%",
         kpis_d["delta_mei"], f"{kpis_d['bench_mei']:.2f}%", False, "#059669"),
    ]

    cols = st.columns(5)
    for col, (name, val_str, delta, bench, rev, accent) in zip(cols, metrics):
        delta_html = _delta_badge(delta, reverse=rev)
        with col:
            st.markdown(
                f'<div style="background:#fff;border:1px solid #E2E8F0;border-top:3px solid {accent};'
                f'border-radius:10px;padding:14px 12px;text-align:center;">'
                f'<div style="font-size:.67rem;font-weight:700;color:#94A3B8;text-transform:uppercase;'
                f'letter-spacing:.07em;margin-bottom:6px;">{name}</div>'
                f'<div style="font-size:1.7rem;font-weight:900;color:{accent};line-height:1.1;">{val_str}</div>'
                f'<div style="margin-top:5px;">{delta_html}</div>'
                f'<div style="font-size:.68rem;color:#CBD5E1;margin-top:3px;">nhóm: {bench}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )


# ── P2: Radar 5 Trụ cột ───────────────────────────────────────────────

def _render_unit_p2_radar(pillar_comp, unit_label, group_id):
    """P2 — Radar chart unit vs benchmark + top strengths/weaknesses."""
    import plotly.graph_objects as go

    st.markdown(_part_header("P2", "Sức khỏe 5 Trụ cột",
                             "So sánh trực quan unit vs toàn nhóm", color="#7C3AED"),
                unsafe_allow_html=True)

    if not pillar_comp:
        st.info("Không đủ dữ liệu để vẽ radar.")
        return

    names   = [r["name"] for r in pillar_comp]
    scores_u = [r["pct_unit"] for r in pillar_comp]
    scores_b = [r["pct_bench"] if r["pct_bench"] is not None else r["pct_unit"]
                for r in pillar_comp]

    # Close the polygon
    names_c    = names + [names[0]]
    scores_uc  = scores_u + [scores_u[0]]
    scores_bc  = scores_b + [scores_b[0]]

    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=scores_bc, theta=names_c,
        fill="toself", name="Benchmark nhóm",
        line=dict(color="#94A3B8", width=2, dash="dot"),
        fillcolor="rgba(148,163,184,0.12)",
    ))
    fig.add_trace(go.Scatterpolar(
        r=scores_uc, theta=names_c,
        fill="toself", name=unit_label[:30],
        line=dict(color="#FF5200", width=2.5),
        fillcolor="rgba(255,82,0,0.15)",
        marker=dict(size=7, color="#FF5200"),
    ))
    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 100], tickfont=dict(size=10)),
            angularaxis=dict(tickfont=dict(size=11, family="Exo 2")),
        ),
        legend=dict(orientation="h", yanchor="bottom", y=-0.15, xanchor="center", x=0.5),
        height=380,
        margin=dict(l=40, r=40, t=30, b=60),
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Exo 2"),
    )

    col_r, col_cards = st.columns([1.1, 0.9], gap="large")
    with col_r:
        st.plotly_chart(fig, use_container_width=True,
                        key=f"unit_radar_{group_id}_{unit_label[:15]}")

    with col_cards:
        sorted_p = sorted(
            [r for r in pillar_comp if r["delta"] is not None],
            key=lambda x: x["delta"],
        )
        weakest  = sorted_p[:2]
        strongest = sorted_p[-2:][::-1]

        st.markdown("**Thế mạnh cốt lõi**")
        for r in strongest:
            _delta = f"+{r['delta']:.2f}" if r["delta"] >= 0 else f"{r['delta']:.2f}"
            st.markdown(
                f'<div style="background:#F0FDF4;border-left:3px solid #15803D;'
                f'border-radius:7px;padding:8px 12px;margin-bottom:6px;">'
                f'<span style="font-size:.8rem;font-weight:700;color:#14532D;">{r["name"]}</span>'
                f'<span style="float:right;font-size:.78rem;color:#15803D;font-weight:700;">'
                f'{r["score_unit"]:.2f}/5 · {_delta}</span>'
                f'</div>',
                unsafe_allow_html=True,
            )

        st.markdown("**Điểm cần cải thiện**", unsafe_allow_html=False)
        for r in weakest:
            _delta = f"+{r['delta']:.2f}" if r["delta"] >= 0 else f"{r['delta']:.2f}"
            st.markdown(
                f'<div style="background:#FEF2F2;border-left:3px solid #DC2626;'
                f'border-radius:7px;padding:8px 12px;margin-bottom:6px;">'
                f'<span style="font-size:.8rem;font-weight:700;color:#7F1D1D;">{r["name"]}</span>'
                f'<span style="float:right;font-size:.78rem;color:#DC2626;font-weight:700;">'
                f'{r["score_unit"]:.2f}/5 · {_delta}</span>'
                f'</div>',
                unsafe_allow_html=True,
            )

        # AI summary
        if pillar_comp:
            from utils.ai_generator import render_ai_insight_card
            pillar_lines = "\n".join([
                f"  {r['name']}: {r['score_unit']:.2f}/5 (benchmark {r['score_bench'] or '?':.2f}, delta {r['delta'] or 0:+.2f})"
                for r in pillar_comp
            ])
            prompt = (
                f"Bạn là HR Business Partner phân tích đơn vị '{unit_label}'.\n"
                f"DỮ LIỆU THỰC TẾ (KHÔNG bịa thêm):\n{pillar_lines}\n\n"
                "Viết 2 đoạn ngắn bằng tiếng Việt:\n"
                "(1) Thế mạnh cốt lõi — dẫn chứng bằng số.\n"
                "(2) Điểm nghẽn chính và lý do quan trọng — dẫn chứng bằng số.\n"
                "Tối đa 80 từ mỗi đoạn. Chỉ dùng số đã cung cấp."
            )
            render_ai_insight_card(
                f"AI · Nhận định 5 Trụ cột — {unit_label[:25]}",
                {"pillars": pillar_comp}, prompt,
                custom_style="margin-top:12px;",
            )


# ── P3: Chi tiết từng Trụ cột ─────────────────────────────────────────

def _render_unit_p3_pillars(df_unit, df_bench, group_id, cfg, pillar_comp):
    """P3 — Expandable per-pillar detail: bar chart câu hỏi + bảng + triangulation."""
    import plotly.graph_objects as go
    from utils.credibility import confidence_badge, triangulate_pillar, render_triangulation_box
    from utils.unit_report import pillar_question_detail

    st.markdown(_part_header("P3", "Chi tiết từng Trụ cột tại đơn vị",
                             "Đi sâu đến từng câu hỏi, so sánh vs benchmark nhóm",
                             color="#EA580C"), unsafe_allow_html=True)

    for r in pillar_comp:
        pid   = r["pillar_id"]
        delta = r["delta"] if r["delta"] is not None else 0
        flag  = " [!]" if delta <= -0.2 else (" [+]" if delta >= 0.1 else "")
        delta_str = f"{delta:+.2f}" if r["delta"] is not None else "—"
        header_label = f"{r['name']}{flag}  ·  {r['score_unit']:.2f}/5  ({delta_str} vs nhóm)"

        with st.expander(header_label, expanded=(delta <= -0.2)):
            df_qs = pillar_question_detail(df_unit, df_bench, group_id, pid)
            if df_qs.empty:
                st.info("Không đủ dữ liệu câu hỏi.")
                continue

            # Bar chart: unit vs benchmark per question
            labels = [f"{row['Câu']}: {row['Nội dung'][:35]}…"
                      if len(row['Nội dung']) > 35 else f"{row['Câu']}: {row['Nội dung']}"
                      for _, row in df_qs.iterrows()]
            fig = go.Figure()
            fig.add_trace(go.Bar(
                name="Đơn vị", y=labels, x=df_qs["Điểm đơn vị"],
                orientation="h", marker_color="#FF5200",
                text=[f"{v:.2f}" for v in df_qs["Điểm đơn vị"]],
                textposition="outside", textfont=dict(size=10),
            ))
            if "Điểm nhóm" in df_qs.columns and df_qs["Điểm nhóm"].notna().any():
                fig.add_trace(go.Bar(
                    name="Benchmark nhóm", y=labels, x=df_qs["Điểm nhóm"],
                    orientation="h", marker_color="#94A3B8",
                    opacity=0.65,
                ))
            fig.update_layout(
                barmode="group", height=max(220, len(df_qs) * 50 + 60),
                margin=dict(l=10, r=50, t=20, b=10),
                xaxis=dict(range=[1, 5.5], title="Điểm TB (1–5)", gridcolor="rgba(226,232,240,0.5)"),
                yaxis=dict(autorange="reversed"),
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                font=dict(family="Exo 2", size=11),
            )
            st.plotly_chart(fig, use_container_width=True,
                            key=f"unit_p3_bar_{group_id}_{pid}")

            # Câu yếu nhất
            weakest_q = df_qs.iloc[0]
            st.markdown(
                f'<div style="background:#FEF2F2;border-left:3px solid #DC2626;'
                f'border-radius:8px;padding:10px 14px;margin:8px 0;">'
                f'<span style="font-size:.68rem;font-weight:800;color:#DC2626;'
                f'text-transform:uppercase;letter-spacing:.07em;">Câu yếu nhất</span><br>'
                f'<span style="font-size:.88rem;font-weight:700;color:#0A1F44;">'
                f'{weakest_q["Câu"]}: {weakest_q["Nội dung"]}</span><br>'
                f'<span style="font-size:.8rem;color:#64748B;">'
                f'Điểm {weakest_q["Điểm đơn vị"]:.2f}/5 · {weakest_q["% Tiêu cực"]:.1f}% tiêu cực · N={weakest_q["N"]:,}'
                f'</span></div>',
                unsafe_allow_html=True,
            )

            # Bảng chi tiết
            st.markdown("**Bảng chi tiết**")
            cols_show = ["Câu", "Nội dung", "Điểm đơn vị", "Điểm nhóm", "Delta", "% Tiêu cực", "N"]
            cols_show = [c for c in cols_show if c in df_qs.columns]
            st.dataframe(
                df_qs[cols_show].style.format({
                    "Điểm đơn vị": "{:.2f}",
                    "Điểm nhóm": "{:.2f}",
                    "Delta": "{:+.2f}",
                    "% Tiêu cực": "{:.1f}%",
                    "N": "{:,}",
                }, na_rep="—").background_gradient(
                    cmap="RdYlGn", subset=["Điểm đơn vị"], vmin=2, vmax=5
                ),
                use_container_width=True, hide_index=True,
            )

            # Triangulation
            tri = triangulate_pillar(df_unit, df_bench, pid, group_id)
            tbox = render_triangulation_box(tri)
            if tbox:
                st.markdown(tbox, unsafe_allow_html=True)

            # Confidence badge
            n_pid = int(df_qs["N"].max()) if not df_qs.empty else len(df_unit)
            st.markdown(confidence_badge(n_pid), unsafe_allow_html=True)


# ── P4: Nhóm rủi ro ───────────────────────────────────────────────────

def _render_unit_p4_risk(df_unit, df_bench, group_id, unit_level, sel_dept):
    """P4 — Flight risk, burnout, intent gap; heatmap sub-units."""
    import plotly.graph_objects as go
    import plotly.express as px
    from shared.codebook import PILLAR_META, PILLAR_ORDER, get_pillar_questions

    st.markdown(_part_header("P4", "Nhóm rủi ro trong đơn vị",
                             "Ai đang có nguy cơ cao nhất? Burnout, muốn nghỉ, khoảng cách ý định",
                             color="#9333EA"), unsafe_allow_html=True)

    n_unit = len(df_unit)

    # ── Mini KPIs rủi ro ──────────────────────────────────────────────
    if "intent" in df_unit.columns:
        n_quit = int((pd.to_numeric(df_unit["intent"], errors="coerce") <= 2).sum())
    else:
        n_quit = 0

    burnout_col = next((c for c in ["burnout_proxy", "burnout_risk"] if c in df_unit.columns), None)
    if burnout_col:
        n_burnout = int(pd.to_numeric(df_unit[burnout_col], errors="coerce")
                        .map({True: 1, False: 0, 1: 1, 0: 0}).fillna(0).sum())
    else:
        n_burnout = 0

    col1, col2, col3 = st.columns(3)
    for col, (label, val, total, accent) in zip(
        [col1, col2, col3],
        [
            ("Muốn nghỉ (intent 1–2)", n_quit, n_unit, "#DC2626"),
            ("Có dấu hiệu Burnout",    n_burnout, n_unit, "#EA580C"),
            ("Tổng khảo sát",          n_unit, n_unit, "#2563EB"),
        ],
    ):
        pct = round(val / total * 100, 1) if total > 0 else 0
        with col:
            st.markdown(
                f'<div style="background:#fff;border:1px solid #E2E8F0;border-top:3px solid {accent};'
                f'border-radius:10px;padding:14px;text-align:center;">'
                f'<div style="font-size:.68rem;font-weight:700;color:#94A3B8;text-transform:uppercase;'
                f'letter-spacing:.07em;margin-bottom:6px;">{label}</div>'
                f'<div style="font-size:1.6rem;font-weight:900;color:{accent};line-height:1.1;">{val:,}</div>'
                f'<div style="font-size:.78rem;color:#64748B;margin-top:3px;">{pct:.1f}% / {total:,} người</div>'
                f'</div>',
                unsafe_allow_html=True,
            )

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Intent gap per pillar ─────────────────────────────────────────
    # Tìm trụ cột yếu nhất để visualize intent gap
    from views.pillar_renderer import _render_pillar_intent_gap
    from utils.unit_report import pillar_scores_comparison as _psc

    pcomp = _psc(df_unit, df_bench, group_id)
    if pcomp:
        weakest_pid = min(
            [r for r in pcomp if r["delta"] is not None],
            key=lambda x: x["delta"],
            default=None,
        )
        if weakest_pid:
            st.markdown(
                f'<div style="font-size:.78rem;font-weight:700;color:#64748B;'
                f'text-transform:uppercase;letter-spacing:.07em;margin-bottom:8px;">'
                f'Khoảng cách ý định — {weakest_pid["name"]} (trụ cột yếu nhất)</div>',
                unsafe_allow_html=True,
            )
            # cfg mock để pass
            _render_pillar_intent_gap(df_unit, {}, group_id, weakest_pid["pillar_id"])

    # ── Heatmap sub-units (adaptive) ──────────────────────────────────
    if unit_level == "division" and "department" in df_unit.columns:
        sub_col, sub_label = "department", "Phòng ban"
    elif unit_level == "department" and "section" in df_unit.columns:
        sub_col, sub_label = "section", "Section"
    else:
        sub_col, sub_label = None, None

    if sub_col:
        subs = [
            v for v in df_unit[sub_col].dropna().unique()
            if str(v).strip().lower() not in {"nan","none","","n/a"}
        ]
        if len(subs) >= 2:
            st.markdown(
                f'<div style="font-size:.78rem;font-weight:700;color:#64748B;'
                f'text-transform:uppercase;letter-spacing:.07em;margin:14px 0 8px;">'
                f'So sánh {sub_label} trong đơn vị</div>',
                unsafe_allow_html=True,
            )
            heatmap_rows = []
            for sv in sorted(subs):
                sub_df = df_unit[df_unit[sub_col] == sv]
                if len(sub_df) < 5:
                    continue
                row = {sub_label: sv, "N": len(sub_df)}
                ei_vals = pd.to_numeric(sub_df.get("EI", pd.Series(dtype=float)), errors="coerce")
                row["EI (%)"] = round(float(ei_vals.mean()), 1) if ei_vals.notna().sum() >= 3 else None
                if "intent" in sub_df.columns:
                    row["% Muốn nghỉ"] = round(
                        (pd.to_numeric(sub_df["intent"], errors="coerce") <= 2).mean() * 100, 1
                    )
                for p in PILLAR_ORDER:
                    qs = [q for q in get_pillar_questions(group_id, p) if q in sub_df.columns]
                    if qs:
                        vals = sub_df[qs].apply(pd.to_numeric, errors="coerce").mean(axis=1).dropna()
                        if len(vals) >= 3:
                            row[PILLAR_META[p]["name"]] = round(float(vals.mean()), 2)
                heatmap_rows.append(row)

            if heatmap_rows:
                hmdf = pd.DataFrame(heatmap_rows).set_index(sub_label)
                num_cols = [c for c in hmdf.columns if c != "N" and hmdf[c].dtype in [float, "float64"]]
                if num_cols:
                    styled = hmdf[num_cols].style.background_gradient(
                        cmap="RdYlGn", axis=None, vmin=2.5, vmax=5.0
                    ).format("{:.2f}", na_rep="—")
                    st.dataframe(styled, use_container_width=True)


# ── P5: Nghịch lý & Điểm mù ──────────────────────────────────────────

def _render_unit_p5_contradictions(df_unit, group_id, cfg):
    """P5 — Contradictions tại unit level."""
    from utils.contradiction_engine import detect_contradictions

    st.markdown(_part_header("P5", "Nghịch lý & Điểm mù",
                             "Những gì dữ liệu 'trái chiều' tại đơn vị này",
                             color="#DC2626"), unsafe_allow_html=True)

    if len(df_unit) < 20:
        st.info(f"Cần ít nhất 20 người tham gia để phát hiện nghịch lý (đơn vị hiện có {len(df_unit):,}).")
        return

    try:
        contradictions = detect_contradictions(df_unit, group_id, cfg)
    except Exception:
        contradictions = []

    if not contradictions:
        st.success("Không phát hiện mâu thuẫn dữ liệu nghiêm trọng tại đơn vị này.")
        return

    for c in contradictions[:4]:
        border = "#DC2626" if c["severity"] == "critical" else "#D97706"
        bg     = "#FEF2F2" if c["severity"] == "critical" else "#FFFBEB"
        st.markdown(
            f'<div style="background:{bg};border-left:4px solid {border};'
            f'border:1px solid {border}30;border-left:4px solid {border};'
            f'border-radius:10px;padding:14px 18px;margin-bottom:12px;">'
            f'<div style="font-size:.88rem;font-weight:700;color:#0A1F44;margin-bottom:5px;">'
            f'{c["title"]}</div>'
            f'<div style="font-size:.8rem;color:#475569;line-height:1.6;">{c["narrative"]}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )


# ── P6: Tiếng nói nhân viên (tái dùng) ───────────────────────────────

def _render_unit_p6_voice(df_unit, group_id, cfg, unit_label):
    """P6 — Open text đã filter sẵn theo unit."""
    st.markdown(_part_header("P6", "Tiếng nói nhân viên",
                             "Phản hồi mở đã được lọc theo đơn vị này",
                             color="#059669"), unsafe_allow_html=True)

    open_col = None
    for cand in ["Q34", "Q33", "Q32"]:
        if cand in df_unit.columns:
            open_col = cand
            break

    if open_col is None:
        st.info("Không tìm thấy câu hỏi mở trong dữ liệu.")
        return

    _run_voice_analysis(df_unit, open_col, group_id, unit_label, cfg)


# ── P7: Kế hoạch hành động 30 ngày ───────────────────────────────────

def _render_unit_p7_actions(df_unit, df_bench, group_id, pillar_comp, unit_label):
    """P7 — Top 3 actions có evidence chain traceable từ dữ liệu unit."""
    from utils.pillar_analysis import build_action_evidence
    from utils.ai_generator import render_ai_insight_card

    st.markdown(_part_header("P7", "Kế hoạch hành động 30 ngày",
                             "Ưu tiên từ dữ liệu thực tế của đơn vị này",
                             color="#D97706"), unsafe_allow_html=True)

    # Lấy 2–3 trụ cột yếu nhất
    weak_pillars = sorted(
        [r for r in pillar_comp if r["delta"] is not None and r["delta"] < 0],
        key=lambda x: x["delta"],
    )[:3]

    if not weak_pillars:
        weak_pillars = sorted(pillar_comp, key=lambda x: x["score_unit"])[:2]

    if not weak_pillars:
        st.info("Không đủ dữ liệu để gợi ý hành động.")
        return

    action_items = []
    for r in weak_pillars:
        pid = r["pillar_id"]
        try:
            ev = build_action_evidence(df_unit, group_id, pid)
        except Exception:
            ev = {"enabled": False, "profile": {"actions": {}}}

        if ev.get("enabled"):
            weakest = ev.get("weakest", {})
            owner   = ev.get("owner", "Pillar Owner")
            action  = ev.get("action", "Xem xét dữ liệu và can thiệp.")
            evidence_parts = [
                f"{r['name']} = {r['score_unit']:.2f}/5 "
                f"(thấp hơn nhóm {abs(r['delta']):.2f} điểm)",
            ]
            if weakest:
                evidence_parts.append(
                    f"Tín hiệu yếu nhất: {weakest.get('Tín hiệu','')} "
                    f"({weakest.get('Điểm TB',0):.2f}/5, {weakest.get('% Tiêu cực',0):.1f}% tiêu cực)"
                )
            # flight risk
            if "intent" in df_unit.columns:
                fr = (pd.to_numeric(df_unit["intent"], errors="coerce") <= 2).mean() * 100
                evidence_parts.append(f"Flight risk tại đơn vị: {fr:.1f}%")

            action_items.append({
                "pillar": r["name"],
                "action": action,
                "owner": owner,
                "evidence": " · ".join(evidence_parts),
                "score": r["score_unit"],
                "delta": r["delta"],
            })

    if not action_items:
        st.info("Không đủ dữ liệu để xây dựng kế hoạch hành động cụ thể.")
        return

    for i, item in enumerate(action_items, 1):
        accent = ["#DC2626", "#EA580C", "#D97706"][i - 1]
        st.markdown(
            f'<div style="background:#fff;border:1px solid #E2E8F0;'
            f'border-left:4px solid {accent};border-radius:10px;padding:16px 18px;margin-bottom:12px;">'
            f'<div style="display:flex;align-items:center;gap:10px;margin-bottom:8px;">'
            f'<span style="background:{accent};color:white;border-radius:6px;'
            f'padding:3px 10px;font-size:.72rem;font-weight:800;">Ưu tiên {i}</span>'
            f'<span style="font-size:.88rem;font-weight:700;color:#0A1F44;">{item["pillar"]}</span>'
            f'</div>'
            f'<div style="font-size:.84rem;color:#334155;line-height:1.65;margin-bottom:8px;">'
            f'{item["action"]}</div>'
            f'<div style="font-size:.75rem;color:#64748B;margin-bottom:6px;">'
            f'<strong>Owner đề xuất:</strong> {item["owner"]}</div>'
            f'<div style="background:#F8FAFC;border-radius:6px;padding:8px 10px;'
            f'font-size:.72rem;color:#475569;line-height:1.6;">'
            f'<strong>Bang chung:</strong> {item["evidence"]}'
            f'</div></div>',
            unsafe_allow_html=True,
        )

    # AI tổng hợp
    action_summary = "\n".join([
        f"{i}. [{it['pillar']}] {it['action']} (Owner: {it['owner']})"
        for i, it in enumerate(action_items, 1)
    ])
    evidence_summary = "\n".join([
        f"  • {it['pillar']}: score={it['score']:.2f}, delta={it['delta']:.2f}"
        for it in action_items
    ])
    prompt = (
        f"Bạn là HRBP đang chuẩn bị brief cho trưởng phòng '{unit_label}'.\n"
        f"DỮ LIỆU THỰC TẾ:\n{evidence_summary}\n"
        f"Kế hoạch hành động đề xuất:\n{action_summary}\n\n"
        "Viết 1 đoạn tóm tắt ngắn (tối đa 100 từ) bằng tiếng Việt:\n"
        "Giải thích TẠI SAO 3 hành động này là ưu tiên đúng — liên kết với dữ liệu, "
        "và điều gì sẽ xảy ra nếu không làm trong 30 ngày tới.\n"
        "Chỉ dùng số đã cung cấp. Không chung chung."
    )
    render_ai_insight_card(
        f"AI · Tóm tắt kế hoạch — {unit_label[:30]}",
        {"actions": action_items}, prompt,
        custom_style="margin-top:12px;",
    )


# ── Shared UI helper ──────────────────────────────────────────────────

def _part_header(number: str, title: str, subtitle: str, color: str = "#FF5200") -> str:
    return (
        f'<div style="display:flex;align-items:flex-start;gap:14px;'
        f'margin:28px 0 16px;padding-bottom:12px;border-bottom:2px solid #F1F5F9;">'
        f'<div style="background:{color};color:white;border-radius:8px;'
        f'padding:5px 12px;font-size:.7rem;font-weight:800;letter-spacing:.07em;'
        f'text-transform:uppercase;white-space:nowrap;flex-shrink:0;margin-top:3px;">{number}</div>'
        f'<div>'
        f'<div style="font-size:1rem;font-weight:800;color:#0A1F44;letter-spacing:-.02em;">{title}</div>'
        f'<div style="font-size:.8rem;color:#64748B;margin-top:3px;">{subtitle}</div>'
        f'</div></div>'
    )
