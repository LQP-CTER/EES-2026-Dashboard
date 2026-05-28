"""
PILLAR RENDERER – EES 2026 Dashboard
Renders a unified multi-tab view for each of the 5 Experience Pillars.

Each pillar renders:
  Tab 1: Tổng quan     — KPI cards + phân bố điểm (from view_a)
  Tab 2: Chi tiết      — Deep-dive từng câu hỏi (from view_c)
  Tab 3: Nhóm rủi ro   — Thâm niên/thế hệ/vùng (from view_b)
  Tab 4: Nguyên nhân   — Root cause + action (from view_d + view_f)
  Tab 5: HRIS (TC3/TC4) — Thu nhập, năng suất (from hris_linkage)
"""

import streamlit as st
import pandas as pd
import numpy as np

from shared.codebook import (
    PILLAR_META, PILLAR_ORDER,
    get_codebook, get_pillar_questions, get_question_label, PILLAR_WEIGHTS,
)


# ─────────────────────────────────────────────────────────────
# PILLAR HEADER
# ─────────────────────────────────────────────────────────────

def _render_pillar_header(pillar_id, df, cfg, group_id):
    """Render the pillar header with KPI summary."""
    meta = PILLAR_META[pillar_id]
    qs = get_pillar_questions(group_id, pillar_id)
    q_cols = [q for q in qs if q in df.columns]

    if q_cols:
        pillar_mean = df[q_cols].mean(numeric_only=True).mean()
        pillar_fav = 0
        total_valid = 0
        for c in q_cols:
            vals = df[c].dropna()
            fav = (vals >= 4).sum()
            pillar_fav += fav
            total_valid += len(vals)
        fav_pct = (pillar_fav / total_valid * 100) if total_valid > 0 else 0
    else:
        pillar_mean = None
        fav_pct = 0

    # Render header card
    color = meta['color']
    score_str = f"{pillar_mean:.2f}" if pillar_mean else "N/A"
    fav_str = f"{fav_pct:.1f}%"
    weight_str = f"{PILLAR_WEIGHTS.get(pillar_id, 0)*100:.0f}%"

    st.markdown(f"""
    <div style="background: linear-gradient(135deg, {color}08 0%, {color}15 100%); 
                border: 1px solid {color}30; border-radius: 14px; padding: 24px 28px; margin-bottom: 24px;
                position: relative; overflow: hidden;">
        <div style="position: absolute; right: -20px; top: -20px; font-size: 4rem; opacity: 0.08;">{meta['icon']}</div>
        <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 12px;">
            <span style="font-size: 1.5rem;">{meta['icon']}</span>
            <div>
                <span style="font-size: 0.65rem; font-weight: 700; letter-spacing: 0.12em; text-transform: uppercase; 
                             color: {color}; display: block;">{pillar_id} · Trọng số {weight_str}</span>
                <span style="font-size: 1.1rem; font-weight: 800; color: #0A1F44; display: block; margin-top: 2px;">
                    {meta['name']}</span>
            </div>
        </div>
        <p style="font-size: 0.84rem; color: #64748B; margin: 0 0 16px; line-height: 1.5;">{meta['description']}</p>
        <div style="display: flex; gap: 24px; flex-wrap: wrap;">
            <div style="background: white; padding: 12px 18px; border-radius: 10px; border: 1px solid #E2E8F0; min-width: 120px;">
                <span style="font-size: 0.65rem; font-weight: 700; color: #94A3B8; text-transform: uppercase; letter-spacing: 0.08em;">Điểm TB</span>
                <div style="font-size: 1.6rem; font-weight: 900; color: {color}; margin-top: 2px;">{score_str}</div>
            </div>
            <div style="background: white; padding: 12px 18px; border-radius: 10px; border: 1px solid #E2E8F0; min-width: 120px;">
                <span style="font-size: 0.65rem; font-weight: 700; color: #94A3B8; text-transform: uppercase; letter-spacing: 0.08em;">% Tích cực</span>
                <div style="font-size: 1.6rem; font-weight: 900; color: #0A1F44; margin-top: 2px;">{fav_str}</div>
            </div>
            <div style="background: white; padding: 12px 18px; border-radius: 10px; border: 1px solid #E2E8F0; min-width: 120px;">
                <span style="font-size: 0.65rem; font-weight: 700; color: #94A3B8; text-transform: uppercase; letter-spacing: 0.08em;">Số câu hỏi</span>
                <div style="font-size: 1.6rem; font-weight: 900; color: #0A1F44; margin-top: 2px;">{len(q_cols)}</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────
# TAB 1: TỔNG QUAN
# ─────────────────────────────────────────────────────────────

def _render_tab_overview(df, cfg, group_id, pillar_id):
    """Tab Tổng quan: KPI + phân bố điểm cho câu hỏi trong trụ cột."""
    from views import view_a_current_state
    qs = get_pillar_questions(group_id, pillar_id)
    cb = get_codebook(group_id)

    if not qs:
        st.info("Không có câu hỏi nào trong trụ cột này.")
        return

    # Render overview using existing view_a function
    # But filter to only show pillar-relevant content
    try:
        view_a_current_state.render(df, cfg, pillar_filter=pillar_id)
    except TypeError:
        # Fallback: render manual summary if view_a doesn't support pillar_filter yet
        _render_manual_overview(df, cfg, group_id, pillar_id, qs, cb)


def _render_manual_overview(df, cfg, group_id, pillar_id, qs, cb):
    """Manual overview rendering when view_a doesn't support pillar_filter."""
    import plotly.graph_objects as go

    st.markdown("##### Điểm trung bình từng câu hỏi")

    q_data = []
    for q in qs:
        if q not in df.columns:
            continue
        vals = df[q].dropna()
        if len(vals) == 0:
            continue
        mean_val = vals.mean()
        fav = (vals >= 4).sum() / len(vals) * 100
        neg = (vals <= 2).sum() / len(vals) * 100
        label = get_question_label(group_id, q)
        q_data.append({
            'Q': q,
            'Label': f"{q}: {label}",
            'Mean': round(mean_val, 2),
            'Favorable': round(fav, 1),
            'Negative': round(neg, 1),
            'N': len(vals),
        })

    if not q_data:
        st.warning("Không đủ dữ liệu cho trụ cột này.")
        return

    q_df = pd.DataFrame(q_data).sort_values('Mean', ascending=True)

    meta = PILLAR_META[pillar_id]
    color = meta['color']

    fig = go.Figure()
    fig.add_trace(go.Bar(
        y=q_df['Label'],
        x=q_df['Mean'],
        orientation='h',
        marker=dict(
            color=[color if m >= 4.0 else '#F59E0B' if m >= 3.8 else '#EF4444' for m in q_df['Mean']],
            line=dict(width=0),
            cornerradius=4,
        ),
        text=[f"{m:.2f}" for m in q_df['Mean']],
        textposition='outside',
        textfont=dict(size=12, color='#0A1F44', family='Inter'),
        hovertemplate='%{y}<br>Điểm TB: %{x:.2f}<br>N=%{customdata}<extra></extra>',
        customdata=q_df['N'],
    ))

    fig.update_layout(
        height=max(250, len(q_df) * 55 + 80),
        margin=dict(l=10, r=60, t=10, b=10),
        xaxis=dict(range=[1, 5], dtick=0.5, gridcolor='rgba(226,232,240,0.6)', zeroline=False),
        yaxis=dict(automargin=True),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(family='Inter', size=12),
    )
    # Add benchmark line at 4.0
    fig.add_vline(x=4.0, line_dash="dot", line_color="#10B981", line_width=1,
                  annotation_text="Ngưỡng Tốt (4.0)", annotation_position="top right",
                  annotation_font=dict(size=10, color="#10B981"))

    st.plotly_chart(fig, width='stretch', key=f"pillar_overview_{pillar_id}")

    # Summary table
    st.markdown("##### Bảng tổng hợp")
    display_df = pd.DataFrame(q_data)[['Q', 'Label', 'Mean', 'Favorable', 'Negative', 'N']]
    display_df.columns = ['Mã', 'Câu hỏi', 'Điểm TB', '% Tích cực', '% Tiêu cực', 'N']
    display_df = display_df.sort_values('Điểm TB', ascending=True)
    st.dataframe(display_df, width='stretch', hide_index=True, key=f"pillar_table_{pillar_id}")


# ─────────────────────────────────────────────────────────────
# TAB 2: CHI TIẾT
# ─────────────────────────────────────────────────────────────

def _render_tab_detail(df, cfg, group_id, pillar_id):
    """Tab Chi tiết: Deep-dive analysis for each question in the pillar."""
    # First, render the pillar-specific distribution
    _render_manual_detail(df, cfg, group_id, pillar_id)
    
    st.markdown("---")
    
    # Then append the full NLP open-ended analysis from view_c
    from views import view_c_key_issues
    try:
        view_c_key_issues.render(df, cfg, pillar_filter=pillar_id)
    except TypeError:
        view_c_key_issues.render(df, cfg)


def _render_manual_detail(df, cfg, group_id, pillar_id):
    """Manual detail rendering — distribution of each question."""
    import plotly.express as px

    qs = get_pillar_questions(group_id, pillar_id)
    if not qs:
        st.info("Không có câu hỏi nào trong trụ cột này.")
        return

    st.markdown("##### Phân bố phản hồi từng câu hỏi")

    for q in qs:
        if q not in df.columns:
            continue
        vals = df[q].dropna()
        if len(vals) == 0:
            continue

        label = get_question_label(group_id, q)
        mean_val = vals.mean()

        dist = vals.value_counts().reindex([1, 2, 3, 4, 5], fill_value=0)
        dist_pct = dist / dist.sum() * 100

        col1, col2 = st.columns([1, 3])
        with col1:
            delta_color = "#10B981" if mean_val >= 4.0 else "#F59E0B" if mean_val >= 3.8 else "#EF4444"
            st.markdown(f"""
            <div style="background: white; border: 1px solid #E2E8F0; border-radius: 10px; padding: 16px; text-align: center;">
                <div style="font-size: 0.72rem; color: #94A3B8; font-weight: 700; text-transform: uppercase; letter-spacing: 0.08em;">{q}</div>
                <div style="font-size: 2rem; font-weight: 900; color: {delta_color}; margin: 4px 0;">{mean_val:.2f}</div>
                <div style="font-size: 0.78rem; color: #64748B;">{label}</div>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            colors = ['#EF4444', '#F97316', '#94A3B8', '#22C55E', '#10B981']
            labels = ['1-Rất không ĐY', '2-Không ĐY', '3-Trung lập', '4-Đồng ý', '5-Rất đồng ý']
            fig = px.bar(
                x=[dist_pct.get(i, 0) for i in range(1, 6)],
                y=labels,
                orientation='h',
                color_discrete_sequence=[colors[0]],
            )
            fig.update_traces(
                marker_color=colors,
                text=[f"{dist_pct.get(i, 0):.1f}%" for i in range(1, 6)],
                textposition='outside',
            )
            fig.update_layout(
                height=160, margin=dict(l=0, r=40, t=0, b=0),
                xaxis=dict(range=[0, 100], title=None, showgrid=False),
                yaxis=dict(title=None, automargin=True),
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                showlegend=False,
                font=dict(family='Inter', size=11),
            )
            st.plotly_chart(fig, width='stretch', key=f"dist_{pillar_id}_{q}")

        st.markdown("<hr style='margin: 8px 0; border: none; border-top: 1px solid #F1F5F9;'>", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────
# TAB 3: NHÓM RỦI RO
# ─────────────────────────────────────────────────────────────

def _render_tab_risk_groups(df, cfg, group_id, pillar_id):
    """Tab Nhóm rủi ro: breakdown by tenure/generation/region for this pillar."""
    # First, render the pillar-specific manual breakdown
    _render_manual_risk_groups(df, cfg, group_id, pillar_id)
    
    st.markdown("---")
    
    # Then append the full division/department heatmap from view_b
    from views import view_b_problem_groups
    try:
        view_b_problem_groups.render(df, cfg, pillar_filter=pillar_id)
    except TypeError:
        view_b_problem_groups.render(df, cfg)


def _render_manual_risk_groups(df, cfg, group_id, pillar_id):
    """Manual risk groups rendering — score by tenure/generation."""
    import plotly.graph_objects as go

    qs = get_pillar_questions(group_id, pillar_id)
    q_cols = [q for q in qs if q in df.columns]

    if not q_cols or 'Q5' not in df.columns:
        st.info("Không đủ dữ liệu phân nhóm.")
        return

    # Calculate pillar score per row
    df_work = df.copy()
    df_work['_pillar_score'] = df_work[q_cols].mean(axis=1)

    st.markdown("##### Điểm trụ cột theo Thâm niên")

    tenure_order = [
        'Dưới 1 tháng', 'Trên 1 đến 3 tháng', 'Trên 3 đến 6 tháng',
        'Trên 6 đến 9 tháng', 'Trên 9 đến 12 tháng', 'Trên 1 đến 2 năm',
        'Trên 2 đến 3 năm', 'Trên 3 đến 5 năm', 'Trên 5 năm'
    ]

    tenure_data = []
    for t in tenure_order:
        mask = df_work['Q5'] == t
        subset = df_work.loc[mask, '_pillar_score'].dropna()
        if len(subset) >= 10:
            tenure_data.append({
                'Thâm niên': t,
                'Điểm TB': round(subset.mean(), 2),
                'N': len(subset),
            })

    if tenure_data:
        t_df = pd.DataFrame(tenure_data)
        meta = PILLAR_META[pillar_id]

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=t_df['Thâm niên'], y=t_df['Điểm TB'],
            mode='lines+markers+text',
            marker=dict(size=10, color=meta['color'], line=dict(width=2, color='white')),
            line=dict(color=meta['color'], width=3),
            text=[f"{v:.2f}" for v in t_df['Điểm TB']],
            textposition='top center',
            textfont=dict(size=11, color='#0A1F44', family='Inter'),
            hovertemplate='%{x}<br>Điểm: %{y:.2f}<br>N=%{customdata}<extra></extra>',
            customdata=t_df['N'],
        ))
        fig.add_hline(y=4.0, line_dash="dot", line_color="#10B981", line_width=1)
        fig.update_layout(
            height=350,
            margin=dict(l=10, r=10, t=20, b=80),
            xaxis=dict(tickangle=-30, gridcolor='rgba(226,232,240,0.3)'),
            yaxis=dict(range=[3.5, 4.5], dtick=0.1, gridcolor='rgba(226,232,240,0.6)'),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(family='Inter'),
        )
        st.plotly_chart(fig, width='stretch', key=f"tenure_{pillar_id}")

    # By Region
    if 'region' in df_work.columns:
        st.markdown("##### Điểm trụ cột theo Vùng vận hành")
        region_agg = df_work.groupby('region')['_pillar_score'].agg(['mean', 'count']).reset_index()
        region_agg = region_agg[region_agg['count'] >= 10].sort_values('mean', ascending=True)
        region_agg.columns = ['Vùng', 'Điểm TB', 'N']

        if not region_agg.empty:
            fig2 = go.Figure()
            fig2.add_trace(go.Bar(
                y=region_agg['Vùng'], x=region_agg['Điểm TB'],
                orientation='h',
                marker=dict(
                    color=[PILLAR_META[pillar_id]['color'] if m >= 4.0 else '#F59E0B' if m >= 3.8 else '#EF4444'
                           for m in region_agg['Điểm TB']],
                    cornerradius=4,
                ),
                text=[f"{m:.2f}" for m in region_agg['Điểm TB']],
                textposition='outside',
            ))
            fig2.add_vline(x=4.0, line_dash="dot", line_color="#10B981", line_width=1)
            fig2.update_layout(
                height=max(300, len(region_agg) * 30 + 80),
                margin=dict(l=10, r=60, t=10, b=10),
                xaxis=dict(range=[3.0, 4.5], gridcolor='rgba(226,232,240,0.6)'),
                yaxis=dict(automargin=True),
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(family='Inter'),
            )
            st.plotly_chart(fig2, width='stretch', key=f"region_{pillar_id}")


# ─────────────────────────────────────────────────────────────
# TAB 4: NGUYÊN NHÂN & HÀNH ĐỘNG
# ─────────────────────────────────────────────────────────────

def _render_tab_root_cause(df, cfg, group_id, pillar_id):
    """Tab Nguyên nhân: root cause analysis + action priority."""
    from views import view_d_root_cause, view_f_action_priority

    # Root cause — only render for matching pillar
    st.markdown("####  Phân tích nguyên nhân gốc rễ")
    try:
        view_d_root_cause.render(df, cfg, group_id, pillar_filter=pillar_id)
    except TypeError:
        # Fallback: render full root cause (backward compat)
        view_d_root_cause.render(df, cfg, group_id)

    st.markdown("---")

    # Action priority
    st.markdown("####  Ưu tiên hành động")
    try:
        view_f_action_priority.render(df, cfg, pillar_filter=pillar_id)
    except TypeError:
        view_f_action_priority.render(df, cfg)


# ─────────────────────────────────────────────────────────────
# TAB 5: HRIS LINKAGE (TC3 & TC4 only)
# ─────────────────────────────────────────────────────────────

def _render_tab_hris(df, cfg, group_id, pillar_id):
    """Tab HRIS: only for TC3 (productivity) and TC4 (income)."""
    from views import hris_linkage, view_e_impact_risk

    if pillar_id == 'TC4':
        st.markdown("#### Phân tích HRIS: Thu nhập & Rủi ro nghỉ việc")
        try:
            hris_linkage.render(df, cfg, group_id, pillar_filter=pillar_id)
        except TypeError:
            hris_linkage.render(df, cfg, group_id)
        st.markdown("---")
        st.markdown("#### Mô phỏng rủi ro & chi phí thay thế")
        view_e_impact_risk.render(df, cfg)

    elif pillar_id == 'TC3':
        st.markdown("#### Phân tích HRIS: Năng suất & Vận hành")
        try:
            hris_linkage.render(df, cfg, group_id, pillar_filter=pillar_id)
        except TypeError:
            hris_linkage.render(df, cfg, group_id)

    elif pillar_id == 'TC5':
        st.markdown("####  Phân tích Rủi ro Gắn kết")
        view_e_impact_risk.render(df, cfg)


# ─────────────────────────────────────────────────────────────
# MAIN RENDER
# ─────────────────────────────────────────────────────────────

def render(df, cfg, group_id, pillar_id):
    """Main entry point: render pillar with tabs."""
    if df is None or df.empty:
        st.warning("Không có dữ liệu để hiển thị.")
        return

    meta = PILLAR_META[pillar_id]

    # Render pillar header
    _render_pillar_header(pillar_id, df, cfg, group_id)

    # Build tab list based on pillar
    tab_names = [" Tổng quan", " Chi tiết", " Nhóm rủi ro", " Nguyên nhân & Hành động"]

    # Add HRIS tab for TC3, TC4, TC5
    if pillar_id in ('TC3', 'TC4', 'TC5'):
        if pillar_id == 'TC4':
            tab_names.append("HRIS & Rủi ro")
        elif pillar_id == 'TC3':
            tab_names.append("HRIS & Năng suất")
        elif pillar_id == 'TC5':
            tab_names.append(" Rủi ro Gắn kết")

    tabs = st.tabs(tab_names)

    with tabs[0]:
        _render_tab_overview(df, cfg, group_id, pillar_id)

    with tabs[1]:
        _render_tab_detail(df, cfg, group_id, pillar_id)

    with tabs[2]:
        _render_tab_risk_groups(df, cfg, group_id, pillar_id)

    with tabs[3]:
        _render_tab_root_cause(df, cfg, group_id, pillar_id)

    if len(tabs) > 4:
        with tabs[4]:
            _render_tab_hris(df, cfg, group_id, pillar_id)
