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
from utils.ai_generator import render_ai_insight_card


_AI_LOGO_B64 = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAIAAAD8GO2jAAADT0lEQVR4nO1WTWwVVRT+zp15f33PlhojIivKAl0RiKgNCalhUV2ZEBODC+PPorpxQQIoG10TMLjDjQloSKORjUlTF6AYFdPUrjRFTU0auwBCAi/w/mbmns+cmVc0ffPo66I7Tu7M3HvPPd+558w5514hic0kt6noeKhgAAr7cnp/vnQfgOiNDMlYPdObHUVh/jTJZh3UdMu0N4FKVcKCMZMYrUZqTMoCIU6GRnKN6FFAQoTNuh7dJ3frCARJIkHAexGePSjHv7Ylpw/L3CWtlUQTBCE9WRsJTs1JdTQTH8ACQG4u40bsyuAQ4CHFgFcu8u1/bMvfX0Q5CG7VGUKaYBvceqcvztp/kFlw+7p+/Jrs3Me7N93laXjP0z9i7huGBfNHEuG5l+XIfoROXzgsw49zad4d+UJGt/VaYN7OoXZDo5Z2Wsn7BzgBf/adbDpemI1/nc36/uy7xjp+QDtNjdpsN3KR+iggqT45Ns4J6KGCX7lG9UziLiuJqd6vXNNDRU4gOfY8ve8Hk1eLfGKvKxdk4Spqjjt2u+27zPVBaHFFtQ7Ebd/FHbtRc7Lwi/5w4b7gGspTIOnk5XMoCCLF2B4bqu+yMm42HNvDSFEQfnfuP8F1FJBwjlELK4tSJBQYfTKN914iHt1mqVKkrCyaiHO9+d+nXEctiVtZIqF5Z7VCrLUUjXr6FUQta3nUoyCDKtdQGaYHSsD8DNUbirmF1tIhVTk/I2VIQlaGTeS++AMtMCAJi9y5Fx3hUAlLf/HzE3CBNQOQrK/nP5ClP1kpoSMytlfCYroDGfREk8kpCKEqtQDTJ/2ZN3T5NwvQJNbl3/XMmzJ9EtUAqlZaJ6f64uRXU1U450+9KjNf4rESkgT3PKoOT4wZ9/rf0lA8EjAI5VZHX3olOPpVJjKwAptM8/nDF2X+Z2wJEBaQRBKpMYvOHOJj3PZ8Zlw+mpVKzZyTV037nwdZUWo39NP38O1nEgPF1dqYQCKwAEy+JVOfSLmWU4LWV7CqA4Au/oRL5/nHVanfsNXDW/HUuBx83T29///LNq4gE05Tr5sTWeBXR7p4qgbdH33gI1O9qbEStEo+MVwL3HVog2cy08UP3PLAt4r8/cjG1j+82Q1Am367/hffvQmZc1fQbgAAAABJRU5ErkJggg=="


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


def render_narrative(df, cfg, group_id):
    """Render toàn bộ narrative flow cho một nhóm."""
    group_name = cfg.get('label', group_id)

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

    st.markdown(f"""
    <div style="background:#0A1F44;border-radius:16px;padding:28px 32px;
                margin-bottom:28px;position:relative;overflow:hidden;">
        <div style="position:absolute;top:-40%;right:-5%;width:300px;height:300px;
                    background:radial-gradient(circle,rgba(255,82,0,0.18) 0%,transparent 70%);
                    filter:blur(40px);pointer-events:none"></div>
        <div style="position:relative;z-index:1">
            <div style="display:flex;align-items:center;gap:8px;margin-bottom:10px">
                <img src="{_AI_LOGO_B64}" style="width:18px;height:18px">
                <span style="font-size:0.68rem;font-weight:700;color:#94A3B8;
                             text-transform:uppercase;letter-spacing:0.12em">
                    EES 2026 · Báo cáo tự động
                </span>
            </div>
            <div style="font-size:1.4rem;font-weight:900;color:#FFFFFF;
                        letter-spacing:-0.025em;margin-bottom:6px">
                Báo cáo Trải nghiệm Nhân viên — {group_name}
            </div>
            <div style="font-size:0.85rem;color:#94A3B8;margin-bottom:20px">
                Mạch dữ liệu xuyên suốt từ bức tranh tổng thể đến hành động cụ thể
            </div>
            <div style="display:flex;gap:12px;flex-wrap:wrap">
                <div style="background:rgba(255,255,255,0.06);border:1px solid rgba(255,255,255,0.1);
                            border-radius:10px;padding:12px 18px;min-width:100px">
                    <div style="font-size:0.65rem;color:#94A3B8;text-transform:uppercase;
                                letter-spacing:0.08em;margin-bottom:4px">EI Score</div>
                    <div style="font-size:1.6rem;font-weight:900;color:#FF5200;line-height:1">
                        {kpis['ei_mean']:.1f}%
                    </div>
                </div>
                <div style="background:rgba(255,255,255,0.06);border:1px solid rgba(255,255,255,0.1);
                            border-radius:10px;padding:12px 18px;min-width:100px">
                    <div style="font-size:0.65rem;color:#94A3B8;text-transform:uppercase;
                                letter-spacing:0.08em;margin-bottom:4px">eNPS</div>
                    <div style="font-size:1.6rem;font-weight:900;color:#FFFFFF;line-height:1">
                        {kpis['enps_score']:+.0f}
                    </div>
                </div>
                <div style="background:rgba(255,255,255,0.06);border:1px solid rgba(255,255,255,0.1);
                            border-radius:10px;padding:12px 18px;min-width:100px">
                    <div style="font-size:0.65rem;color:#94A3B8;text-transform:uppercase;
                                letter-spacing:0.08em;margin-bottom:4px">Rủi ro nghỉ</div>
                    <div style="font-size:1.6rem;font-weight:900;color:#FFFFFF;line-height:1">
                        {kpis['intent_pct_low']:.1f}%
                    </div>
                </div>
                <div style="background:rgba(255,255,255,0.06);border:1px solid rgba(255,255,255,0.1);
                            border-radius:10px;padding:12px 18px">
                    <div style="font-size:0.65rem;color:#94A3B8;text-transform:uppercase;
                                letter-spacing:0.08em;margin-bottom:4px">Nghịch lý</div>
                    <div style="display:flex;align-items:center;gap:8px;margin-top:4px">
                        <span style="font-size:1.6rem;font-weight:900;color:#FFFFFF;line-height:1">
                            {n_contradictions}
                        </span>
                        <span style="background:{severity_bg};color:{severity_color};padding:3px 10px;
                                     border-radius:20px;font-size:0.7rem;font-weight:700">
                            {severity_label}
                        </span>
                    </div>
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Tabs for each Act ───────────────────────────────────────────
    tab_act1, tab_act2, tab_act3, tab_act4, tab_act5 = st.tabs([
        "Act 1 · Tổng thể",
        "Act 2 · Nghịch lý",
        "Act 3 · Đi sâu",
        "Act 4 · Hành động",
        "Act 5 · Tiếng nói NV",
    ])

    # ── ACT 1 ──────────────────────────────────────────────────────
    with tab_act1:
        st.markdown(_act_header(
            "Act 1", "Bức tranh tổng thể",
            f"Các chỉ số cốt lõi và hiệu suất trụ cột của {group_name}"
        ), unsafe_allow_html=True)
        _render_kpi_row(kpis)
        _render_pillar_overview(df, group_id)

    # ── ACT 2 ──────────────────────────────────────────────────────
    with tab_act2:
        st.markdown(_act_header(
            "Act 2", "Những nghịch lý dữ liệu",
            "Mâu thuẫn đáng chú ý cần lãnh đạo quan tâm",
            color="#DC2626"
        ), unsafe_allow_html=True)
        if not contradictions:
            st.markdown("""
            <div style="background:#F0FDF4;border:1px solid #BBF7D0;border-radius:12px;
                        padding:20px 24px;text-align:center;color:#15803D;font-size:0.9rem;font-weight:600">
                Không phát hiện mâu thuẫn dữ liệu đáng kể. Các chỉ số đều nhất quán.
            </div>
            """, unsafe_allow_html=True)
        else:
            _render_contradiction_cards(contradictions)

    # ── ACT 3 ──────────────────────────────────────────────────────
    with tab_act3:
        st.markdown(_act_header(
            "Act 3", "Đi sâu vào nghịch lý",
            "Phân tích chi tiết các mâu thuẫn có impact cao nhất",
            color="#8B5CF6"
        ), unsafe_allow_html=True)
        if not top_contradictions:
            st.info("Không có mâu thuẫn nào đủ impact để phân tích sâu.")
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
        textfont=dict(size=12, color='#0A1F44', family='Inter'),
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
        font=dict(family='Inter', size=12),
    )
    st.plotly_chart(fig, width='stretch', key="narrative_flow_chart_146")


def _render_contradiction_cards(contradictions):
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

    # Render specific deep dive visualization based on contradiction type
    if c_id == 'TENURE_CLIFF':
        _render_tenure_cliff_chart(df, metrics)
    elif c_id in ('INFO_GAP', 'FAIRNESS_GAP'):
        _render_gap_chart(df, metrics, c_id)
    elif c_id in ('PRIDE_PARADOX', 'INCOME_PARADOX', 'SILENT_DISENGAGED', 'MEI_SHIELD_FAIL'):
        _render_paradox_chart(df, metrics, c_id)
    elif c_id == 'BURNOUT_BLIND':
        _render_burnout_blind_chart(df, metrics)
    elif c_id == 'GLASS_CEILING':
        _render_glass_ceiling_chart(df, metrics)

    # AI deep dive
    _render_ai_deep_dive(contradiction, group_id)


def _render_tenure_cliff_chart(df, metrics):
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
        textfont=dict(size=11, color='#0A1F44', family='Inter'),
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
        font=dict(family='Inter'),
    )
    st.plotly_chart(fig, width='stretch', key="narrative_flow_chart_277")


def _render_gap_chart(df, metrics, c_id):
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
        textfont=dict(size=13, color='#0A1F44', family='Inter'),
    ))
    fig.add_hline(y=4.0, line_dash="dot", line_color="#10B981", line_width=1.5)
    fig.update_layout(
        height=280,
        margin=dict(l=10, r=10, t=10, b=10),
        yaxis=dict(range=[1, 5.3], dtick=0.5, gridcolor='rgba(226,232,240,0.6)'),
        plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
        font=dict(family='Inter', size=12),
    )
    st.plotly_chart(fig, width='stretch', key="narrative_flow_chart_306")


def _render_paradox_chart(df, metrics, c_id):
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
        textfont=dict(size=13, color='#0A1F44', family='Inter'),
    ))
    fig.update_layout(
        height=280,
        margin=dict(l=10, r=10, t=10, b=10),
        plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
        font=dict(family='Inter', size=12),
    )
    st.plotly_chart(fig, width='stretch', key="narrative_flow_chart_342")


def _render_burnout_blind_chart(df, metrics):
    """Render biểu đồ burnout blind spot."""
    labels = ['Q29: Nói ổn', 'Burnout thực tế (%)']
    values = [metrics.get('Q29_ap_luc', 0), metrics.get('burnout_pct', 0)]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=labels, y=values,
        marker=dict(color=['#10B981', '#EF4444'], cornerradius=4),
        text=[f"{v:.1f}" for v in values],
        textposition='outside',
        textfont=dict(size=13, color='#0A1F44', family='Inter'),
    ))
    fig.update_layout(
        height=280,
        margin=dict(l=10, r=10, t=10, b=10),
        plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
        font=dict(family='Inter', size=12),
    )
    st.plotly_chart(fig, width='stretch', key="narrative_flow_chart_364")


def _render_glass_ceiling_chart(df, metrics):
    """Render biểu đồ glass ceiling."""
    labels = ['NV mới (< 1 năm)', 'NV cũ (> 2 năm)']
    values = [metrics.get('junior_Q19', 0), metrics.get('senior_Q19', 0)]

    fig = go.Figure(go.Bar(
        x=labels, y=values,
        marker=dict(color=['#10B981', '#EF4444'], cornerradius=4),
        text=[f"{v:.2f}" for v in values],
        textposition='outside',
        textfont=dict(size=13, color='#0A1F44', family='Inter'),
    ))
    fig.add_hline(y=3.5, line_dash="dot", line_color="#F59E0B", line_width=1.5,
                  annotation_text="Ngưỡng Cảnh báo (3.5)")
    fig.update_layout(
        height=280,
        margin=dict(l=10, r=10, t=10, b=10),
        yaxis=dict(range=[1, 5.3], dtick=0.5, gridcolor='rgba(226,232,240,0.6)'),
        plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
        font=dict(family='Inter', size=12),
    )
    st.plotly_chart(fig, width='stretch', key="narrative_flow_chart_388")


def _render_ai_deep_dive(contradiction, group_id):
    """Render AI deep dive cho một contradiction."""
    c_id = contradiction['id']
    metrics = contradiction['metrics']

    prompt = (
        f"Bạn là Chuyên gia People Analytics. Phân tích nghịch lý sau của {group_id}:\n\n"
        f"**{contradiction['title']}**\n\n"
        f"{contradiction['narrative']}\n\n"
        f"Dữ liệu: {metrics}\n\n"
        f"Hãy trả lời:\n"
        f"1. Nguyên nhân gốc rễ của nghịch lý này là gì?\n"
        f"2. Nếu không can thiệp, điều gì sẽ xảy ra trong 3-6 tháng?\n"
        f"3. Đề xuất 1 hành động cụ thể, khả thi trong 30 ngày.\n\n"
        f"Viết cho Giám đốc HR đọc — không dùng thuật ngữ kỹ thuật."
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

    st.markdown("""
    <div style="background:#F8FAFC;border:1px solid #E2E8F0;border-radius:12px;padding:16px 20px;margin-bottom:16px;">
        <div style="font-size:0.82rem;color:#64748B;margin-bottom:8px;">
            Ma trận Ưu tiên Hành động — dựa trên tương quan với EI
        </div>
        <div style="display:flex;gap:12px;flex-wrap:wrap;">
            <span style="background:#FEF2F2;color:#DC2626;padding:3px 10px;border-radius:20px;font-size:0.72rem;font-weight:700;">Ưu tiên cao: Điểm thấp + Ảnh hưởng lớn</span>
            <span style="background:#F0FDF4;color:#10B981;padding:3px 10px;border-radius:20px;font-size:0.72rem;font-weight:700;">Duy trì: Điểm cao + Ảnh hưởng lớn</span>
            <span style="background:#FFFBEB;color:#D97706;padding:3px 10px;border-radius:20px;font-size:0.72rem;font-weight:700;">Theo dõi: Điểm thấp + Ảnh hưởng nhỏ</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Display top priorities
    top_priority = rdf[rdf['Priority'] == 'Ưu tiên cao'].head(5)
    maintain = rdf[rdf['Priority'] == 'Duy trì'].head(3)

    if not top_priority.empty:
        st.markdown("**Top hành động ưu tiên:**")
        for _, row in top_priority.iterrows():
            st.markdown(f"""
            <div style="background:#FEF2F2;border:1px solid #FCA5A5;border-radius:10px;padding:12px 16px;margin-bottom:10px;">
                <div style="font-size:0.88rem;font-weight:700;color:#0A1F44;">
                    {row['Q']}: {row['Label']}
                </div>
                <div style="font-size:0.82rem;color:#475569;margin-top:4px;">
                    Điểm: {row['Mean']:.2f}/5 | Tương quan với EI: {row['Correlation']:.3f}
                </div>
            </div>
            """, unsafe_allow_html=True)

    if not maintain.empty:
        st.markdown("**Duy trì:**")
        maintain_labels = ', '.join([f"{row['Q']}: {row['Label']}" for _, row in maintain.iterrows()])
        st.markdown(f"""
        <div style="background:#F0FDF4;border:1px solid #86EFAC;border-radius:10px;padding:12px 16px;margin-bottom:10px;">
            <div style="font-size:0.85rem;color:#166534;">
                {maintain_labels} — đang tốt, tiếp tục phát huy.
            </div>
        </div>
        """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════
# ACT 5: EMPLOYEE VOICE — MONG MUỐN THEO ĐƠN VỊ
# ═══════════════════════════════════════════════════════════════

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
    st.markdown("""
    <div style="background:#F8FAFC;border:1px solid #E2E8F0;border-radius:12px;
                padding:16px 20px;margin-bottom:16px;">
        <div style="font-size:0.82rem;color:#64748B;margin-bottom:4px;">Chọn đơn vị cần phân tích</div>
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
    prompt_key = hashlib.md5((unit_label + responses_text[:200]).encode()).hexdigest()
    cache_key  = f"ev_voice_{group_id}_{prompt_key}"

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
        ai_prompt = f"""Bạn là Chuyên gia Tư vấn Quản trị & Phân tích Trải nghiệm Nhân viên. Dưới đây là {len(sample)} phản hồi THỰC TẾ ẩn danh của nhân viên thuộc nhóm «{group_name}», đơn vị «{unit_label}», khi được hỏi: "Bạn mong muốn điều gì cần thay đổi hoặc cải thiện tại công ty?":

{responses_text}

NHIỆM VỤ TỐI QUAN TRỌNG: 
Đọc kỹ {len(sample)} câu phản hồi trên. TỔNG HỢP và GOM NHÓM các ý kiến lặp lại nhiều nhất thành TOP 5 mong muốn/khiếu nại cốt lõi. 
Mọi phân tích, kết luận VÀ DẪN CHỨNG PHẢI ĐƯỢC LẤY CHÍNH XÁC TỪ DỮ LIỆU CUNG CẤP NÀY. TUYỆT ĐỐI KHÔNG BỊA ĐẶT (HALLUCINATE) HOẶC DÙNG DỮ LIỆU CỦA ĐƠN VỊ KHÁC.

Hãy trình bày báo cáo định tính (bằng tiếng Việt) theo đúng cấu trúc sau:

1. Top 5 Vấn Đề / Mong Muốn Cấp Bách Nhất (Sắp xếp theo tần suất xuất hiện):
- [Tên Vấn Đề 1]: (Chiếm khoảng XX% số phản hồi) Phân tích ngắn gọn bản chất vấn đề từ góc độ dữ liệu.
  + 📝 Trích dẫn thực tế: Trích chính xác 1-2 câu (hoặc cụm từ) BÊ NGUYÊN TỪ DỮ LIỆU BÊN TRÊN để làm bằng chứng. KHÔNG tự chế ra câu trích dẫn.
  + 💡 Khuyến nghị hành động: Đề xuất 1 hành động quản trị cụ thể, khả thi để giải quyết.
- [Tên Vấn Đề 2]: (Làm tương tự)
... (Đến Vấn Đề 5)

2. Đánh Giá Mức Độ Nghiêm Trọng (Severity Warning):
- Nhận diện 1 vấn đề mang tính hệ thống (systemic) nhất hoặc gây ức chế sâu sắc nhất dựa trên cách dùng từ của nhân viên (Giải thích trong 2 dòng).

TUYỆT ĐỐI: 
- Trình bày dạng bullet points, câu chữ tư vấn chuyên nghiệp.
- KHÔNG thêm lời chào, kết luận dài dòng hay bịa đặt dữ liệu."""
    else:
        ai_prompt = f"""Bạn là Chuyên gia Tâm lý học Tổ chức (Organizational Psychologist) & Phân tích Trải nghiệm Nhân viên cấp cao. Dưới đây là {len(sample)} phản hồi ẩn danh thực tế của nhân viên thuộc nhóm «{group_name}», đơn vị «{unit_label}»:

{responses_text}

Nhiệm vụ của bạn là đọc hiểu sâu sắc (deep reading) các phản hồi này để bóc tách những cảm xúc, trăn trở ngầm ẩn bên dưới. Hãy xuất báo cáo định tính (bằng tiếng Việt) theo đúng cấu trúc sau:

1. Bức Tranh Cảm Xúc Tổng Thể:
- Tỷ lệ ước lượng: XX% Tích cực / XX% Trung lập / XX% Tiêu cực.
- Tâm lý chủ đạo: [Ghi rõ trạng thái tâm lý đang chi phối tập thể này: VD Lạc quan, Kiệt sức, Hoang mang, Gắn kết...]. Giải thích ngắn gọn (1 câu) lý do gốc rễ.

2. Phân Tích Sâu Các Trọng Tâm Cảm Xúc (Deep Dive):
- [Vấn đề 1]: Phân tích sâu nguyên nhân gốc rễ (root cause) khiến nhân viên có cảm xúc này, dựa trên văn bản. Trích dẫn ngắn gọn 1-2 cụm từ điển hình từ dữ liệu để chứng minh.
- [Vấn đề 2]: (Làm tương tự nếu có)

3. Tín Hiệu Cảnh Báo Ngầm (Red Flags) (Nếu có):
- Chỉ ra những rủi ro ngầm có thể gây tỷ lệ nghỉ việc cao (turnover) hoặc giảm sút hiệu suất (VD: mâu thuẫn nội bộ, mất niềm tin quản lý, kiệt sức thầm lặng).

4. Tóm Tắt Khuyến Nghị Dành Cho Lãnh Đạo (CEO Summary):
- Đúc kết trong 2-3 câu sắc sảo nhất về tình trạng "sức khỏe tinh thần" của đơn vị này, và 1 định hướng ưu tiên cần giải quyết ngay.

TUYỆT ĐỐI: 
- Dùng bullet points rõ ràng, trình bày chuyên nghiệp, câu chữ mang tính tư vấn chiến lược.
- KHÔNG thêm lời chào, KHÔNG tự sáng tác ngoài dữ liệu."""

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
                <div class="ai-icon"><img src="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAIAAAD8GO2jAAADT0lEQVR4nO1WTWwVVRT+zp15f33PlhojIivKAl0RiKgNCalhUV2ZEBODC+PPorpxQQIoG10TMLjDjQloSKORjUlTF6AYFdPUrjRFTU0auwBCAi/w/mbmns+cmVc0ffPo66I7Tu7M3HvPPd+558w5514hic0kt6noeKhgAAr7cnp/vnQfgOiNDMlYPdObHUVh/jTJZh3UdMu0N4FKVcKCMZMYrUZqTMoCIU6GRnKN6FFAQoTNuh7dJ3frCARJIkHAexGePSjHv7Ylpw/L3CWtlUQTBCE9WRsJTs1JdTQTH8ACQG4u40bsyuAQ4CHFgFcu8u1/bMvfX0Q5CG7VGUKaYBvceqcvztp/kFlw+7p+/Jrs3Me7N93laXjP0z9i7huGBfNHEuG5l+XIfoROXzgsw49zad4d+UJGt/VaYN7OoXZDo5Z2Wsn7BzgBf/adbDpemI1/nc36/uy7xjp+QDtNjdpsN3KR+iggqT45Ns4J6KGCX7lG9UziLiuJqd6vXNNDRU4gOfY8ve8Hk1eLfGKvKxdk4Spqjjt2u+27zPVBaHFFtQ7Ebd/FHbtRc7Lwi/5w4b7gGspTIOnk5XMoCCLF2B4bqu+yMm42HNvDSFEQfnfuP8F1FJBwjlELK4tSJBQYfTKN914iHt1mqVKkrCyaiHO9+d+nXEctiVtZIqF5Z7VCrLUUjXr6FUQta3nUoyCDKtdQGaYHSsD8DNUbirmF1tIhVTk/I2VIQlaGTeS++AMtMCAJi9y5Fx3hUAlLf/HzE3CBNQOQrK/nP5ClP1kpoSMytlfCYroDGfREk8kpCKEqtQDTJ/2ZN3T5NwvQJNbl3/XMmzJ9EtUAqlZaJ6f64uRXU1U450+9KjNf4rESkgT3PKoOT4wZ9/rf0lA8EjAI5VZHX3olOPpVJjKwAptM8/nDF2X+Z2wJEBaQRBKpMYvOHOJj3PZ8Zlw+mpVKzZyTV037nwdZUWo39NP38O1nEgPF1dqYQCKwAEy+JVOfSLmWU4LWV7CqA4Au/oRL5/nHVanfsNXDW/HUuBx83T29///LNq4gE05Tr5sTWeBXR7p4qgbdH33gI1O9qbEStEo+MVwL3HVog2cy08UP3PLAt4r8/cjG1j+82Q1Am367/hffvQmZc1fQbgAAAABJRU5ErkJggg==" style="width: 16px; height: 16px;" alt="Ultramarines Logo" /></div>
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
                    <div class="ai-icon"><img src="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAIAAAD8GO2jAAADT0lEQVR4nO1WTWwVVRT+zp15f33PlhojIivKAl0RiKgNCalhUV2ZEBODC+PPorpxQQIoG10TMLjDjQloSKORjUlTF6AYFdPUrjRFTU0auwBCAi/w/mbmns+cmVc0ffPo66I7Tu7M3HvPPd+558w5514hic0kt6noeKhgAAr7cnp/vnQfgOiNDMlYPdObHUVh/jTJZh3UdMu0N4FKVcKCMZMYrUZqTMoCIU6GRnKN6FFAQoTNuh7dJ3frCARJIkHAexGePSjHv7Ylpw/L3CWtlUQTBCE9WRsJTs1JdTQTH8ACQG4u40bsyuAQ4CHFgFcu8u1/bMvfX0Q5CG7VGUKaYBvceqcvztp/kFlw+7p+/Jrs3Me7N93laXjP0z9i7huGBfNHEuG5l+XIfoROXzgsw49zad4d+UJGt/VaYN7OoXZDo5Z2Wsn7BzgBf/adbDpemI1/nc36/uy7xjp+QDtNjdpsN3KR+iggqT45Ns4J6KGCX7lG9UziLiuJqd6vXNNDRU4gOfY8ve8Hk1eLfGKvKxdk4Spqjjt2u+27zPVBaHFFtQ7Ebd/FHbtRc7Lwi/5w4b7gGspTIOnk5XMoCCLF2B4bqu+yMm42HNvDSFEQfnfuP8F1FJBwjlELK4tSJBQYfTKN914iHt1mqVKkrCyaiHO9+d+nXEctiVtZIqF5Z7VCrLUUjXr6FUQta3nUoyCDKtdQGaYHSsD8DNUbirmF1tIhVTk/I2VIQlaGTeS++AMtMCAJi9y5Fx3hUAlLf/HzE3CBNQOQrK/nP5ClP1kpoSMytlfCYroDGfREk8kpCKEqtQDTJ/2ZN3T5NwvQJNbl3/XMmzJ9EtUAqlZaJ6f64uRXU1U450+9KjNf4rESkgT3PKoOT4wZ9/rf0lA8EjAI5VZHX3olOPpVJjKwAptM8/nDF2X+Z2wJEBaQRBKpMYvOHOJj3PZ8Zlw+mpVKzZyTV037nwdZUWo39NP38O1nEgPF1dqYQCKwAEy+JVOfSLmWU4LWV7CqA4Au/oRL5/nHVanfsNXDW/HUuBx83T29///LNq4gE05Tr5sTWeBXR7p4qgbdH33gI1O9qbEStEo+MVwL3HVog2cy08UP3PLAt4r8/cjG1j+82Q1Am367/hffvQmZc1fQbgAAAABJRU5ErkJggg==" style="width: 16px; height: 16px;" alt="Ultramarines Logo" /></div>
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
                                {"role": "system", "content": "Bạn là chuyên gia phân tích định tính và cảm xúc trong lĩnh vực Quản trị Nhân lực. Phân tích súc tích, chính xác, luôn bằng tiếng Việt."},
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
