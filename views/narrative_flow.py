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


def render_narrative(df, cfg, group_id):
    """Render toàn bộ narrative flow cho một nhóm."""
    group_name = cfg.get('label', group_id)
    short_name = cfg.get('short', group_id)

    from utils.data_loader import compute_kpis
    kpis = compute_kpis(df)

    # ── ACT 1: BỨC TRANH TỔNG THỂ ──
    st.markdown(section_header(
        "Act 1 — Bức tranh tổng thể",
        f"Các chỉ số cốt lõi của {group_name}"
    ))

    _render_kpi_row(kpis)

    # Pillar overview chart
    _render_pillar_overview(df, group_id)

    # ── ACT 2: PHÁT HIỆN MÂU THUẪN ──
    st.markdown(section_header(
        "Act 2 — Những nghịch lý dữ liệu",
        "Các mâu thuẫn đáng chú ý cần lãnh đạo quan tâm"
    ))

    contradictions = detect_contradictions(df, group_id, cfg)

    if not contradictions:
        st.info("Không phát hiện mâu thuẫn dữ liệu đáng kể. Các chỉ số đều nhất quán.")
    else:
        _render_contradiction_cards(contradictions)

    # ── ACT 3: DEEP DIVE VÀO MÂU THUẪN ──
    top_contradictions = get_top_contradictions(contradictions, n=3)
    if top_contradictions:
        st.markdown(section_header(
            "Act 3 — Đi sâu vào nghịch lý",
            "Phân tích chi tiết các mâu thuẫn có impact cao nhất"
        ))

        for i, contradiction in enumerate(top_contradictions, 1):
            _render_deep_dive(df, contradiction, group_id, i)

    # ── ACT 4: HÀNH ĐỘNG ──
    st.markdown(section_header(
        "Act 4 — Hành động ưu tiên",
        "Đề xuất hành động dựa trên dữ liệu"
    ))

    _render_action_priorities(df, group_id, contradictions)


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
    st.plotly_chart(fig, width='stretch')


def _render_contradiction_cards(contradictions):
    """Render các contradiction cards."""
    critical = [c for c in contradictions if c['severity'] == 'critical']
    warning = [c for c in contradictions if c['severity'] == 'warning']

    # Summary banner
    total = len(contradictions)
    st.markdown(f"""
    <div style="background:#F8FAFC;border:1px solid #E2E8F0;border-radius:12px;padding:16px 20px;margin-bottom:20px;">
        <div style="font-size:0.82rem;color:#64748B;margin-bottom:8px;">
            Phát hiện <strong>{total} mâu thuẫn</strong> trong dữ liệu
        </div>
        <div style="display:flex;gap:16px;flex-wrap:wrap;">
            {'<span style="background:#FEF2F2;color:#DC2626;padding:4px 12px;border-radius:20px;font-size:0.78rem;font-weight:700;">' + str(len(critical)) + ' Nghiêm trọng</span>' if critical else ''}
            {'<span style="background:#FFFBEB;color:#D97706;padding:4px 12px;border-radius:20px;font-size:0.78rem;font-weight:700;">' + str(len(warning)) + ' Cảnh báo</span>' if warning else ''}
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
    st.plotly_chart(fig, width='stretch')


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
    st.plotly_chart(fig, width='stretch')


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
    st.plotly_chart(fig, width='stretch')


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
    st.plotly_chart(fig, width='stretch')


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
    st.plotly_chart(fig, width='stretch')


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
