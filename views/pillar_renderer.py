"""
PILLAR RENDERER — EES 2026 Dashboard  (v2 — Restructured)
Renders unified multi-tab view for each of the 5 Experience Pillars.

Tab 1: Chẩn đoán Nhanh  — Câu yếu nhất + Breakdown thâm niên + AI insight theo form báo cáo
Tab 2: Chi tiết từng câu  — Phân bố phản hồi + NLP open-text
Tab 3: Nhóm rủi ro       — Breakdown Division/Dept/Section + cross-pillar pattern at unit level
Tab 4: Nguyên nhân & Hành động — Root cause + action priority
Tab 5: Bất thường        — Anomaly detection per pillar + cross-pillar + AI synthesis
Tab 6: HRIS (TC3/TC4/TC5 only)
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px

from shared.codebook import (
    PILLAR_META, PILLAR_ORDER, get_pillar_description,
    get_codebook, get_pillar_questions, get_question_label, PILLAR_WEIGHTS,
)
from shared.plotly_theme import fig_card, COLORS
from shared.loading import TerminalLoader
from utils.anomaly_detector import detect_pillar_anomalies, detect_cross_pillar, run_full_anomaly_scan
from utils.action_queue import build_priority_action_queue
from utils.executive_brief import build_executive_brief
from utils.lifecycle_analysis import build_lifecycle_risk
from utils.pillar_interaction import build_cross_pillar_priority
from views.anomaly_cards import render_anomaly_tab
from utils.ai_generator import render_ai_insight_card


# ─────────────────────────────────────────────────────────────
# TENURE HELPERS
# ─────────────────────────────────────────────────────────────

TENURE_ORDER = [
    'Dưới 1 tháng', 'Trên 1 đến 3 tháng', 'Trên 3 đến 6 tháng',
    'Trên 6 đến 9 tháng', 'Trên 9 đến 12 tháng', 'Trên 1 đến 2 năm',
    'Trên 2 đến 3 năm', 'Trên 3 đến 5 năm', 'Trên 5 năm',
]
TENURE_MONTHS = {
    'Dưới 1 tháng': 0.5, 'Trên 1 đến 3 tháng': 2, 'Trên 3 đến 6 tháng': 4.5,
    'Trên 6 đến 9 tháng': 7.5, 'Trên 9 đến 12 tháng': 10.5, 'Trên 1 đến 2 năm': 18,
    'Trên 2 đến 3 năm': 30, 'Trên 3 đến 5 năm': 48, 'Trên 5 năm': 72,
}


def _qmean(df, col):
    if col not in df.columns:
        return None
    vals = df[col].dropna()
    return vals.mean() if len(vals) >= 5 else None


def _render_aggregate_only_fallback(df, cfg, group_id, pillar_id, qs, context="quick"):
    """Render a useful aggregate view when raw question columns are absent."""
    meta = PILLAR_META[pillar_id]
    p_col = f"{pillar_id}_pct"
    missing_preview = ", ".join(qs[:8]) if qs else "không resolve được codebook"
    available_q = sorted([c for c in df.columns if str(c).upper().startswith("Q")])[:12]
    available_txt = ", ".join(available_q) if available_q else "không thấy cột Q nào"

    if p_col not in df.columns:
        st.info(
            "Không tìm thấy cột câu hỏi hoặc cột điểm tổng hợp cho trụ cột này trong dữ liệu đang load. "
            f"Codebook cần: {missing_preview}. Dữ liệu hiện có: {available_txt}."
        )
        return

    vals = pd.to_numeric(df[p_col], errors="coerce").dropna()
    if vals.empty:
        st.info(
            f"Cột tổng hợp {p_col} có trong dữ liệu nhưng không có giá trị hợp lệ. "
            f"Codebook cần raw questions: {missing_preview}."
        )
        return

    pillar_pct = float(vals.mean())
    pillar_mean = pillar_pct / 100 * 4 + 1
    ei_val = pd.to_numeric(df.get("EI", pd.Series(dtype=float)), errors="coerce").mean()
    enps_val = pd.to_numeric(df.get("eNPS", pd.Series(dtype=float)), errors="coerce").mean()

    st.markdown(f"""
    <div style="background:#FFF7ED;border:1px solid #FDBA7433;border-left:4px solid {meta['color']};
                border-radius:12px;padding:16px 18px;margin-bottom:16px;">
        <div style="font-size:.72rem;font-weight:900;color:#FF5200;text-transform:uppercase;letter-spacing:.09em;margin-bottom:6px;">Aggregate mode</div>
        <div style="font-size:.95rem;color:#0A1F44;font-weight:850;margin-bottom:6px;">DB hiện có điểm tổng hợp <code>{p_col}</code>, nhưng thiếu raw question columns.</div>
        <div style="font-size:.82rem;color:#475569;line-height:1.65;">
            Dashboard vẫn đọc được điểm trụ cột tổng hợp, nhưng chưa thể xếp hạng từng câu hỏi.
            Cần bổ sung các cột raw trong table Neon: <strong>{missing_preview}</strong>.
            Cột Q hiện thấy: <strong>{available_txt}</strong>.
        </div>
    </div>
    """, unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Điểm trụ cột", f"{pillar_pct:.1f}%")
    c2.metric("Quy đổi thang 5", f"{pillar_mean:.2f}/5")
    c3.metric("EI nhóm", f"{ei_val:.1f}%" if not pd.isna(ei_val) else "N/A")
    c4.metric("eNPS TB", f"{enps_val:.1f}" if not pd.isna(enps_val) else "N/A")

    breakdown_col = next((c for c in ["department", "section", "division"] if c in df.columns), None)
    if breakdown_col:
        rows = []
        for unit, g in df.groupby(breakdown_col, dropna=False):
            scores = pd.to_numeric(g[p_col], errors="coerce").dropna()
            if len(scores) < 5:
                continue
            rows.append({
                "Đơn vị": unit,
                "N": len(scores),
                f"{pillar_id} (%)": round(float(scores.mean()), 1),
                "EI (%)": round(float(pd.to_numeric(g.get("EI", pd.Series(dtype=float)), errors="coerce").mean()), 1),
            })
        if rows:
            agg_df = pd.DataFrame(rows).sort_values(f"{pillar_id} (%)", ascending=True)
            fig = px.bar(
                agg_df.tail(20),
                x=f"{pillar_id} (%)",
                y="Đơn vị",
                orientation="h",
                color=f"{pillar_id} (%)",
                color_continuous_scale="RdYlGn",
                text=f"{pillar_id} (%)",
            )
            fig = fig_card(fig, f"{pillar_id} theo {breakdown_col}", "Fallback theo điểm tổng hợp từ database")
            fig.update_layout(height=max(320, min(len(agg_df), 20) * 26 + 90), coloraxis_showscale=False)
            st.plotly_chart(fig, width="stretch", key=f"aggregate_fallback_{context}_{pillar_id}")
            with st.expander("Bảng aggregate fallback", expanded=False):
                st.dataframe(agg_df.sort_values(f"{pillar_id} (%)", ascending=False), width="stretch", hide_index=True)


# ─────────────────────────────────────────────────────────────
# PILLAR HEADER
# ─────────────────────────────────────────────────────────────

def _render_pillar_header(pillar_id, df, cfg, group_id):
    meta = PILLAR_META[pillar_id]
    qs = get_pillar_questions(group_id, pillar_id)
    q_cols = [q for q in qs if q in df.columns]

    if q_cols:
        pillar_mean = df[q_cols].mean(numeric_only=True).mean()
        total_valid, pillar_fav = 0, 0
        for c in q_cols:
            vals = df[c].dropna()
            pillar_fav += (vals >= 4).sum()
            total_valid += len(vals)
        fav_pct = (pillar_fav / total_valid * 100) if total_valid > 0 else 0
    elif f"{pillar_id}_pct" in df.columns:
        pillar_pct = pd.to_numeric(df[f"{pillar_id}_pct"], errors="coerce").dropna()
        pillar_mean = (pillar_pct.mean() / 100 * 4 + 1) if not pillar_pct.empty else None
        fav_pct = float(pillar_pct.mean()) if not pillar_pct.empty else 0
    else:
        pillar_mean, fav_pct = None, 0

    color = meta['color']
    score_str = f"{pillar_mean:.2f}" if pillar_mean else "N/A"
    fav_str = f"{fav_pct:.1f}%"
    weight_str = f"{PILLAR_WEIGHTS.get(pillar_id, 0)*100:.0f}%"
    q_count_str = str(len(q_cols)) if q_cols else f"{len(qs)}*"
    q_count_note = "câu hỏi trong trụ cột" if q_cols else "theo codebook; DB thiếu raw Q"

    # Pillar score color
    if pillar_mean:
        score_color = '#10B981' if pillar_mean >= 4.0 else '#F59E0B' if pillar_mean >= 3.7 else '#EF4444'
    else:
        score_color = color

    st.markdown(f"""
    <div style="background:#FFFFFF;border:1px solid #E2E8F0;border-left:4px solid {color};
                border-radius:12px;padding:24px 28px;margin-bottom:20px;">
        <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:14px;">
            <div>
                <span style="font-size:0.68rem;font-weight:700;letter-spacing:0.1em;text-transform:uppercase;
                             color:{color};display:block;margin-bottom:4px;">{pillar_id} · Trọng số {weight_str}</span>
                <span style="font-size:1.2rem;font-weight:800;color:#0A1F44;letter-spacing:-0.02em;">{meta['name']}</span>
            </div>
        </div>
        <p style="font-size:0.83rem;color:#64748B;margin:0 0 18px;line-height:1.65;">{get_pillar_description(pillar_id, group_id)}</p>
        <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:14px;">
            <div style="background:#F8FAFC;padding:14px;border-radius:8px;border:1px solid #F1F5F9;">
                <span style="font-size:0.65rem;font-weight:700;color:#94A3B8;text-transform:uppercase;letter-spacing:0.08em;display:block;margin-bottom:5px;">Điểm trung bình</span>
                <div style="font-size:1.8rem;font-weight:900;color:{score_color};line-height:1;">{score_str}</div>
                <div style="font-size:0.7rem;color:#94A3B8;margin-top:3px;">trên thang 5.0</div>
            </div>
            <div style="background:#F8FAFC;padding:14px;border-radius:8px;border:1px solid #F1F5F9;">
                <span style="font-size:0.65rem;font-weight:700;color:#94A3B8;text-transform:uppercase;letter-spacing:0.08em;display:block;margin-bottom:5px;">Tỷ lệ tích cực</span>
                <div style="font-size:1.8rem;font-weight:900;color:#0A1F44;line-height:1;">{fav_str}</div>
                <div style="font-size:0.7rem;color:#94A3B8;margin-top:3px;">đồng ý hoặc rất đồng ý</div>
            </div>
            <div style="background:#F8FAFC;padding:14px;border-radius:8px;border:1px solid #F1F5F9;">
                <span style="font-size:0.65rem;font-weight:700;color:#94A3B8;text-transform:uppercase;letter-spacing:0.08em;display:block;margin-bottom:5px;">Số câu hỏi</span>
                <div style="font-size:1.8rem;font-weight:900;color:#0A1F44;line-height:1;">{q_count_str}</div>
                <div style="font-size:0.7rem;color:#94A3B8;margin-top:3px;">{q_count_note}</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Thêm Anomaly Banner ngay dưới header
    pillar_anomalies = detect_pillar_anomalies(df, group_id, pillar_id)
    if pillar_anomalies:
        from views.anomaly_cards import render_anomaly_summary_banner
        render_anomaly_summary_banner(pillar_anomalies)


# ─────────────────────────────────────────────────────────────
# TAB 1: CHẨN ĐOÁN NHANH (replaced old "Tổng quan")
# ─────────────────────────────────────────────────────────────

def _render_tab_quick_diagnosis(df, cfg, group_id, pillar_id):
    """Chẩn đoán nhanh: câu yếu nhất, breakdown thâm niên, AI insight."""
    meta = PILLAR_META[pillar_id]
    qs = get_pillar_questions(group_id, pillar_id)
    q_cols = [q for q in qs if q in df.columns]
    color = meta['color']

    if not q_cols:
        _render_aggregate_only_fallback(df, cfg, group_id, pillar_id, qs, context="quick")
        return

    cb = get_codebook(group_id)

    # ── Khối 1: Xếp hạng câu hỏi theo điểm ──────────────────
    st.markdown("#### Câu hỏi nào đang kéo trụ cột xuống?")
    q_data = []
    for q in q_cols:
        vals = df[q].dropna()
        if len(vals) < 5:
            continue
        mean_val = vals.mean()
        fav = (vals >= 4).sum() / len(vals) * 100
        neg = (vals <= 2).sum() / len(vals) * 100
        label = get_question_label(group_id, q)
        q_data.append({
            'Q': q, 'Label': f"{q}: {label}",
            'Mean': round(mean_val, 2), 'Favorable': round(fav, 1),
            'Negative': round(neg, 1), 'N': len(vals),
        })

    if not q_data:
        st.warning("Không đủ dữ liệu.")
        return

    q_df = pd.DataFrame(q_data).sort_values('Mean', ascending=True)

    # Color by threshold
    bar_colors = []
    for m in q_df['Mean']:
        if m >= 4.0:   bar_colors.append('#10B981')
        elif m >= 3.7: bar_colors.append('#F59E0B')
        elif m >= 3.5: bar_colors.append('#F97316')
        else:          bar_colors.append('#EF4444')

    fig = go.Figure(go.Bar(
        y=q_df['Label'], x=q_df['Mean'],
        orientation='h',
        marker=dict(color=bar_colors, cornerradius=4),
        text=[f"{m:.2f}" for m in q_df['Mean']],
        textposition='outside',
        textfont=dict(size=12, color='#0A1F44', family='Inter'),
        hovertemplate='%{y}<br>Điểm TB: %{x:.2f}<br>N=%{customdata}<extra></extra>',
        customdata=q_df['N'],
    ))
    fig.add_vline(x=4.0, line_dash="dot", line_color="#10B981", line_width=1.5,
                  annotation_text="Ngưỡng Tốt (4.0)", annotation_position="top right",
                  annotation_font=dict(size=10, color="#10B981"))
    fig.add_vline(x=3.5, line_dash="dot", line_color="#F59E0B", line_width=1,
                  annotation_text="Cảnh báo (3.5)", annotation_position="bottom right",
                  annotation_font=dict(size=9, color="#F59E0B"))
    fig.update_layout(
        height=max(250, len(q_df) * 55 + 80),
        margin=dict(l=10, r=60, t=10, b=10),
        xaxis=dict(range=[1, 5.3], dtick=0.5, gridcolor='rgba(226,232,240,0.6)', zeroline=False),
        yaxis=dict(automargin=True),
        plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
        font=dict(family='Inter', size=12),
    )
    st.plotly_chart(fig, width='stretch', key="diag_bar_chart")

    # Highlight câu yếu nhất & câu có tiềm năng cải thiện cao nhất
    weakest = q_df.iloc[0]
    strongest = q_df.iloc[-1]
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"""
        <div style="background:#FEF2F2;border:1px solid #FCA5A5;border-radius:8px;padding:12px 16px;">
            <div style="font-size:0.7rem;font-weight:700;color:#DC2626;text-transform:uppercase;letter-spacing:0.08em;margin-bottom:4px;">Câu yếu nhất — Ưu tiên cải thiện</div>
            <div style="font-size:0.9rem;font-weight:700;color:#111827;">{weakest['Label']}</div>
            <div style="font-size:1.3rem;font-weight:900;color:#DC2626;">{weakest['Mean']:.2f}/5</div>
            <div style="font-size:0.78rem;color:#6B7280;">{weakest['Negative']:.1f}% phản hồi tiêu cực</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div style="background:#F0FDF4;border:1px solid #86EFAC;border-radius:8px;padding:12px 16px;">
            <div style="font-size:0.7rem;font-weight:700;color:#16A34A;text-transform:uppercase;letter-spacing:0.08em;margin-bottom:4px;">Điểm mạnh nhất — Nhân rộng</div>
            <div style="font-size:0.9rem;font-weight:700;color:#111827;">{strongest['Label']}</div>
            <div style="font-size:1.3rem;font-weight:900;color:#16A34A;">{strongest['Mean']:.2f}/5</div>
            <div style="font-size:0.78rem;color:#6B7280;">{strongest['Favorable']:.1f}% phản hồi tích cực</div>
        </div>
        """, unsafe_allow_html=True)

    # ── Khối 2: Breakdown theo thâm niên ─────────────────────
    if 'Q5' in df.columns:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("#### Ai đang bị ảnh hưởng nhất? (Phân tích theo Thâm niên)")

        df_work = df.copy()
        df_work['_pillar_score'] = df_work[q_cols].mean(axis=1)

        tenure_data = []
        for t in TENURE_ORDER:
            mask = df_work['Q5'] == t
            subset = df_work.loc[mask, '_pillar_score'].dropna()
            if len(subset) >= 10:
                tenure_data.append({'Thâm niên': t, 'Điểm TB': round(subset.mean(), 2), 'N': len(subset)})

        if len(tenure_data) >= 2:
            t_df = pd.DataFrame(tenure_data)

            # Tìm "cliff" — điểm giảm đột ngột
            diffs = t_df['Điểm TB'].diff()
            cliff_idx = diffs.abs().idxmax()
            cliff_drop = diffs.loc[cliff_idx]

            fig2 = go.Figure()
            # Color points by score
            point_colors = ['#10B981' if v >= 4.0 else '#F59E0B' if v >= 3.7 else '#EF4444' for v in t_df['Điểm TB']]
            fig2.add_trace(go.Scatter(
                x=t_df['Thâm niên'], y=t_df['Điểm TB'],
                mode='lines+markers+text',
                marker=dict(size=12, color=point_colors, line=dict(width=2, color='white')),
                line=dict(color=color, width=3),
                text=[f"{v:.2f}" for v in t_df['Điểm TB']],
                textposition='top center',
                textfont=dict(size=11, color='#0A1F44', family='Inter'),
                hovertemplate='%{x}<br>Điểm: %{y:.2f}<br>N=%{customdata}<extra></extra>',
                customdata=t_df['N'],
            ))
            fig2.add_hline(y=4.0, line_dash="dot", line_color="#10B981", line_width=1.5)
            fig2.add_hline(y=3.5, line_dash="dot", line_color="#F59E0B", line_width=1)
            fig2.update_layout(
                height=320,
                margin=dict(l=10, r=10, t=20, b=80),
                xaxis=dict(tickangle=-25, gridcolor='rgba(226,232,240,0.3)'),
                yaxis=dict(range=[max(1, t_df['Điểm TB'].min()-0.3), min(5, t_df['Điểm TB'].max()+0.3)],
                           dtick=0.2, gridcolor='rgba(226,232,240,0.6)'),
                plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                font=dict(family='Inter'),
            )
            st.plotly_chart(fig2, width='stretch', key="tenure_cliff_chart")

            # Cliff alert
            if cliff_drop is not None and cliff_drop < -0.4:
                cliff_tenure = t_df.loc[cliff_idx, 'Thâm niên']
                st.markdown(f"""
                <div style="background:#FFFBEB;border-left:4px solid #D97706;border-radius:8px;padding:10px 16px;margin-top:8px;">
                    <span style="font-size:0.78rem;font-weight:700;color:#D97706;">TENURE CLIFF phát hiện tại mốc "{cliff_tenure}"</span>
                    <div style="font-size:0.8rem;color:#374151;margin-top:4px;">
                        Điểm giảm {abs(cliff_drop):.2f} điểm — kỳ vọng ban đầu đang gặp thực tế.
                        Cần "milestone intervention" ngay tại mốc này.
                    </div>
                </div>
                """, unsafe_allow_html=True)

    # ── Khối 3: AI Insight ────────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("#### AI Phân tích")

    p_mean = q_df['Mean'].mean()
    weakest_label = weakest['Label']
    p_name = meta['name']
    group_name = cfg.get('label', 'nhóm này')
    pillar_doc_desc = get_pillar_description(pillar_id, group_id)

    prompt = (
        f"Bạn là Chuyên gia People Analytics, phân tích trụ cột '{p_name}' cho {group_name}. "
        f"DỰA CHÍNH XÁC VÀO DỮ LIỆU SAU (KHÔNG bịa thêm chỉ số):\n"
        f"- Điểm TB trụ cột: {p_mean:.2f}/5\n"
        f"- Câu yếu nhất: {weakest_label} ({weakest['Mean']:.2f}/5, {weakest['Negative']:.1f}% tiêu cực)\n"
        f"- Câu mạnh nhất: {strongest['Label']} ({strongest['Mean']:.2f}/5)\n"
        f"- Định hướng: {pillar_doc_desc}\n\n"
        f"YÊU CẦU (CHỈ dùng dữ liệu đã cung cấp): "
        f"(1) Tại sao '{weakest['Label']}' yếu nhất? Liên kết với đặc thù {group_name}. "
        f"(2) Điều gì xảy ra trong 3-6 tháng nếu không can thiệp? "
        f"(3) Đề xuất 1 hành động CỤ THỂ trong 30 ngày. "
        f"Sắc bén, bám sát đặc thù, KHÔNG chung chung."
    )
    ai_data = {
        'Pillar': p_name, 'Group': group_name,
        'Pillar_Mean': round(p_mean, 2),
        'Weakest_Q': weakest['Label'], 'Weakest_Score': weakest['Mean'],
        'Strongest_Q': strongest['Label'], 'Strongest_Score': strongest['Mean'],
    }
    render_ai_insight_card("AI Chẩn đoán Trụ cột", ai_data, prompt)


# ─────────────────────────────────────────────────────────────
# TAB 2: CHI TIẾT TỪNG CÂU + NLP
# ─────────────────────────────────────────────────────────────

def _render_tab_detail(df, cfg, group_id, pillar_id):
    """Chi tiết phân bố từng câu + phân tích pillar-specific."""
    qs = get_pillar_questions(group_id, pillar_id)
    q_cols = [q for q in qs if q in df.columns]

    if not q_cols:
        _render_aggregate_only_fallback(df, cfg, group_id, pillar_id, qs, context="detail")
        return

    meta = PILLAR_META[pillar_id]
    color = meta['color']

    # ── So sánh tương quan (Nghịch lý) ──
    # Dùng "vai trò câu hỏi" (role) thay vì hard-code số câu → đúng cho cả 6 nhóm.
    # Mỗi cặp: (role_A, role_B, tiêu đề). Role được resolve về mã câu theo group_id.
    from shared.codebook import get_role_question
    role_pairs = {
        'TC1': [('info_trust', 'info_timely', 'Tin tưởng định hướng vs Nhận thông tin kịp thời')],
        'TC2': [('mgr_support', 'mgr_fairness', 'Quản lý hỗ trợ vs Phân công công bằng')],
        'TC3': [('change_guide', 'info_timely', 'Hướng dẫn thay đổi vs Thông báo thay đổi')],
        'TC4': [('income_fair', 'transparency', 'Thu nhập công bằng vs Minh bạch khấu trừ/phạt')],
        'TC5': [('pride', 'pressure', 'Tự hào về tổ chức vs Mức độ áp lực/Burnout')],
    }

    pairs = {}
    if pillar_id in role_pairs:
        resolved = []
        for roleA, roleB, title in role_pairs[pillar_id]:
            qA = get_role_question(group_id, roleA)
            qB = get_role_question(group_id, roleB)
            if qA and qB:
                resolved.append((qA, qB, title))
        if resolved:
            pairs[pillar_id] = resolved

    if pillar_id in pairs:
        for qA, qB, title in pairs[pillar_id]:
            if qA in q_cols and qB in q_cols:
                mA = _qmean(df, qA)
                mB = _qmean(df, qB)
                if mA and mB:
                    st.markdown(f"##### Phân tích Tương quan: {title}")
                    gap = abs(mA - mB)
                    
                    if gap >= 0.4:
                        st.markdown(f"""
                        <div style="background:#FFFBEB; border-left:4px solid #D97706; padding:12px; border-radius:6px; margin-bottom:12px;">
                            <span style="color:#D97706; font-weight:700;">Nghịch lý phát hiện:</span> 
                            Khoảng cách <strong>{gap:.2f} điểm</strong> giữa hai yếu tố này. Dù nhân viên đánh giá cao một mặt ({qA if mA > mB else qB}), nhưng lại rất bất mãn ở mặt kia ({qB if mA > mB else qA}). Sự chênh lệch này là nguyên nhân chính gây ức chế tâm lý.
                        </div>
                        """, unsafe_allow_html=True)
                        
                    labelA = get_question_label(group_id, qA)
                    labelB = get_question_label(group_id, qB)
                    
                    fig_comp = go.Figure()
                    fig_comp.add_trace(go.Bar(
                        x=[mA, mB],
                        y=[f"{qA} ", f"{qB} "],
                        orientation='h',
                        text=[f"{mA:.2f}", f"{mB:.2f}"],
                        textposition='inside',
                        marker_color=['#3B82F6', '#F59E0B'],
                        hovertemplate='%{x:.2f}<extra></extra>'
                    ))
                    fig_comp.update_layout(
                        height=160, margin=dict(l=10, r=20, t=10, b=10),
                        xaxis=dict(range=[1, 5], visible=False),
                        yaxis=dict(autorange="reversed"),
                        showlegend=False,
                        plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)'
                    )
                    
                    c1, c2 = st.columns([1, 2])
                    with c1:
                        st.markdown(f"<div style='font-size:0.8rem; color:#475569; margin-top:20px;'><strong>{qA}</strong>: {labelA}<br><br><strong>{qB}</strong>: {labelB}</div>", unsafe_allow_html=True)
                    with c2:
                        st.plotly_chart(fig_comp, width='stretch', key=f"comp_paradox_chart_{qA}_{qB}")
                        
                    if gap >= 0.4:
                        open_cols = df.attrs.get('open_cols', ['Q32', 'Q33', 'Q34', 'Q35', 'Q36'])
                        all_texts = []
                        for tc in open_cols:
                            clean_col = f"{tc}_clean"
                            target_col = clean_col if clean_col in df.columns else tc
                            if target_col in df.columns:
                                vals = df[target_col].dropna().astype(str)
                                vals = vals[vals.str.len() > 10]
                                all_texts.extend(vals.tolist())
                        
                        sample_texts = ""
                        if all_texts:
                            import random
                            sample_size = min(20, len(all_texts))
                            sampled = random.sample(all_texts, sample_size)
                            sample_texts = "\n- ".join(sampled)
                        
                        ai_data = {
                            "Title": title,
                            "Q_High": f"{qA if mA > mB else qB}: {labelA if mA > mB else labelB}",
                            "Score_High": round(max(mA, mB), 2),
                            "Q_Low": f"{qB if mA > mB else qA}: {labelB if mA > mB else labelA}",
                            "Score_Low": round(min(mA, mB), 2),
                            "Gap": round(gap, 2)
                        }
                        
                        prompt = (
                            f"Phân tích nghịch lý DỰA VÀO DỮ LIỆU THỰC TẾ SAU "
                            f"(TUYỆT ĐỐI KHÔNG bịa thêm):\n"
                            f"Nghịch lý: '{title}'\n"
                            f"- Yếu tố CAO: {ai_data['Q_High']} (Điểm: {ai_data['Score_High']}/5)\n"
                            f"- Yếu tố THẤP: {ai_data['Q_Low']} (Điểm: {ai_data['Score_Low']}/5)\n"
                            f"- Khoảng cách: {ai_data['Gap']} điểm\n\n"
                        )
                        if sample_texts:
                            prompt += f"Ý kiến thực tế của nhân viên:\n- {sample_texts}\n\n"
                        else:
                            prompt += "Không có dữ liệu câu hỏi mở.\n\n"
                            
                        prompt += (
                            "Yêu cầu (CHỈ dùng dữ liệu đã cung cấp):\n"
                            "1. Giải thích TẠI SAO xuất hiện nghịch lý này — mâu thuẫn cốt lõi là gì?\n"
                            "2. Đề xuất 1 hành động can thiệp để thu hẹp khoảng cách."
                        )
                        
                        render_ai_insight_card(f"Bằng chứng từ Dữ liệu & AI Phân tích", ai_data, prompt)

                    st.markdown("<hr style='margin:16px 0;border:none;border-top:1px dashed #E2E8F0;'>", unsafe_allow_html=True)

    st.markdown("##### Phân bố phản hồi từng câu hỏi")

    for i, q in enumerate(q_cols):
        if q not in df.columns:
            continue
        vals = df[q].dropna()
        if len(vals) == 0:
            continue
        label = get_question_label(group_id, q)
        mean_val = vals.mean()
        dist_pct = vals.value_counts().reindex([1, 2, 3, 4, 5], fill_value=0) / len(vals) * 100

        delta_color = "#10B981" if mean_val >= 4.0 else "#F59E0B" if mean_val >= 3.7 else "#EF4444"
        col1, col2 = st.columns([1, 3])
        with col1:
            st.markdown(f"""
            <div style="background:white;border:1px solid #E2E8F0;border-radius:10px;padding:16px;text-align:center;">
                <div style="font-size:0.72rem;color:#94A3B8;font-weight:700;text-transform:uppercase;letter-spacing:0.08em;">{q}</div>
                <div style="font-size:2rem;font-weight:900;color:{delta_color};margin:4px 0;">{mean_val:.2f}</div>
                <div style="font-size:0.76rem;color:#64748B;">{label}</div>
                <div style="font-size:0.72rem;color:#94A3B8;margin-top:6px;">N={len(vals):,}</div>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            c_map = ['#EF4444', '#F97316', '#94A3B8', '#22C55E', '#10B981']
            labels_map = ['1-Rất không ĐY', '2-Không ĐY', '3-Trung lập', '4-Đồng ý', '5-Rất đồng ý']
            fig = go.Figure(go.Bar(
                y=labels_map,
                x=[dist_pct.get(j, 0) for j in range(1, 6)],
                orientation='h',
                marker_color=c_map,
                text=[f"{dist_pct.get(j, 0):.1f}%" for j in range(1, 6)],
                textposition='outside',
            ))
            fig.update_layout(
                height=155, margin=dict(l=0, r=40, t=0, b=0),
                xaxis=dict(range=[0, 100], title=None, showgrid=False),
                yaxis=dict(title=None, automargin=True),
                plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                showlegend=False, font=dict(family='Inter', size=11),
            )
            st.plotly_chart(fig, width='stretch', key=f"dist_chart_{i}")

        # ── Breakdown table by segment ──────────────────────────
        seg_col = None
        seg_label = ""
        if group_id in ['1A', '1B', '2A']:
            for c in df.columns:
                if 'Vùng' in str(c) or 'vùng' in str(c):
                    seg_col = c
                    seg_label = 'Vùng'
                    break
        else:
            if 'department' in df.columns:
                seg_col = 'department'
                seg_label = 'Phòng ban'
        
        if not seg_col:
            seg_col = next((c for c in ['division', 'department'] if c in df.columns), None)
            if seg_col:
                seg_label = {'division': 'Khối', 'department': 'Phòng ban'}.get(seg_col, seg_col)

        if seg_col:
            with st.expander(f"Phân tích {q} theo {seg_label}", expanded=False):
                likert_labels = {
                    1: '1-Rất không ĐY',
                    2: '2-Không ĐY',
                    3: '3-Trung lập',
                    4: '4-Đồng ý',
                    5: '5-Rất đồng ý',
                }
                rows = []
                df_q = df[[seg_col, q]].dropna()
                for seg_val, grp in df_q.groupby(seg_col):
                    if len(grp) < 5:
                        continue
                    n = len(grp)
                    vcnt = grp[q].value_counts()
                    row = {seg_label: seg_val, 'N': n, 'TB': round(grp[q].mean(), 2)}
                    for k, lbl in likert_labels.items():
                        row[lbl] = f"{vcnt.get(k, 0) / n * 100:.1f}%"
                    rows.append(row)
                if rows:
                    import pandas as pd
                    tbl = pd.DataFrame(rows).sort_values('TB', ascending=False).reset_index(drop=True)
                    # color TB column
                    def _color_tb(s):
                        return [f'color:{"#10B981" if v >= 4.0 else "#F59E0B" if v >= 3.7 else "#EF4444"};font-weight:700' for v in s]
                    styled = (
                        tbl.style
                        .format({'TB': '{:.2f}', 'N': '{:,}'})
                        .apply(_color_tb, subset=['TB'])
                        .apply(lambda s: ['text-align: center'] * len(s), subset=tbl.columns[2:])
                        .set_table_styles([
                            {'selector': 'th', 'props': [('background-color', '#F8FAFC'), ('color', '#475569'), ('font-size', '0.75rem')]},
                            {'selector': 'td', 'props': [('font-size', '0.78rem')]},
                        ])
                    )
                    st.dataframe(styled, use_container_width=True, hide_index=True)
                else:
                    st.info("Không đủ mẫu để phân tách.")

        st.markdown("<hr style='margin:6px 0;border:none;border-top:1px solid #F1F5F9;'>", unsafe_allow_html=True)

    # NLP open-text
    st.markdown("---")
    from views import view_c_key_issues
    try:
        view_c_key_issues.render(df, cfg, pillar_filter=pillar_id)
    except TypeError:
        view_c_key_issues.render(df, cfg)


# ─────────────────────────────────────────────────────────────
# TAB 3: NHÓM RỦI RO
# ─────────────────────────────────────────────────────────────

def _render_tab_risk_groups(df, cfg, group_id, pillar_id):
    meta = PILLAR_META[pillar_id]
    qs = get_pillar_questions(group_id, pillar_id)
    q_cols = [q for q in qs if q in df.columns]

    if not q_cols:
        st.info("Không đủ dữ liệu phân nhóm.")
        return

    df_work = df.copy()
    df_work['_pillar_score'] = df_work[q_cols].mean(axis=1)

    lifecycle = build_lifecycle_risk(df, group_id, pillar_id=pillar_id)
    cross_priority = build_cross_pillar_priority(df, pillar_id)
    action_queue = build_priority_action_queue(
        df,
        group_id,
        pillar_id=pillar_id,
        lifecycle=lifecycle,
        cross_priority=cross_priority,
    )
    if not action_queue.empty:
        st.markdown("##### Priority Action Queue")
        q1, q2, q3 = st.columns(3)
        with q1:
            st.metric("Hành động ưu tiên", f"{len(action_queue):,}")
        with q2:
            immediate_n = int((action_queue['Ưu tiên'] == 'Immediate').sum())
            st.metric("Immediate", f"{immediate_n:,}")
        with q3:
            top_owner = action_queue['Owner gợi ý'].mode().iloc[0] if not action_queue['Owner gợi ý'].mode().empty else "N/A"
            st.metric("Owner xuất hiện nhiều", top_owner)

        show_queue_cols = [
            'Nguồn', 'Đối tượng', 'N', 'Risk Score', 'Ưu tiên',
            'Vấn đề chính', 'Owner gợi ý', 'Thời hạn'
        ]
        st.dataframe(
            action_queue[show_queue_cols].style.format({'Risk Score': '{:.1f}', 'N': '{:,}'}),
            width='stretch',
            hide_index=True,
            height=330,
        )
        source_summary = (
            action_queue.groupby('Nguồn')
            .agg(action_count=('Đối tượng', 'count'), avg_risk=('Risk Score', 'mean'))
            .reset_index()
            .sort_values('avg_risk', ascending=False)
        )
        fig_queue = px.bar(
            source_summary,
            x='Nguồn',
            y='avg_risk',
            color='action_count',
            color_continuous_scale='OrRd',
            text='action_count',
            hover_data=['avg_risk'],
        )
        fig_queue = fig_card(
            fig_queue,
            'Nguồn rủi ro cần hành động',
            'Risk trung bình theo nhóm phát hiện',
        )
        fig_queue.update_traces(textposition='outside')
        fig_queue.update_layout(height=260, xaxis_title=None, yaxis_title='Risk trung bình', coloraxis_showscale=False)
        st.plotly_chart(fig_queue, width='stretch', key=f"priority_action_queue_{pillar_id}")

        with st.expander("Chi tiết hành động đề xuất", expanded=False):
            st.dataframe(
                action_queue[['Nguồn', 'Đối tượng', 'Vấn đề chính', 'Hành động']],
                width='stretch',
                hide_index=True,
            )

        brief = build_executive_brief(action_queue, lifecycle, cross_priority)
        if brief.get('enabled'):
            with st.expander("Executive brief & 30-60-90 plan", expanded=False):
                st.markdown(f"**{brief.get('headline', '')}**")
                for bullet in brief.get('bullets', []):
                    st.markdown(f"- {bullet}")

                owner_summary = brief.get('owner_summary', pd.DataFrame())
                plan_df = brief.get('plan_df', pd.DataFrame())
                b1, b2 = st.columns([0.85, 1.25])
                with b1:
                    if not owner_summary.empty:
                        st.markdown("**Owner load**")
                        st.dataframe(
                            owner_summary.style.format({'avg_risk': '{:.1f}'}),
                            width='stretch',
                            hide_index=True,
                            height=220,
                        )
                with b2:
                    if not plan_df.empty:
                        st.markdown("**30-60-90 plan**")
                        st.dataframe(
                            plan_df.style.format({'Risk Score': '{:.1f}', 'N': '{:,}'}),
                            width='stretch',
                            hide_index=True,
                            height=260,
                        )
                        csv_data = plan_df.to_csv(index=False).encode('utf-8-sig')
                        st.download_button(
                            "Tải 30-60-90 plan CSV",
                            data=csv_data,
                            file_name=f"ees_2026_{group_id}_{pillar_id}_30_60_90_plan.csv",
                            mime="text/csv",
                            key=f"download_plan_{group_id}_{pillar_id}",
                        )

        st.markdown("<hr style='border:1px dashed rgba(0,0,0,0.08);margin:22px 0;'>", unsafe_allow_html=True)

    if lifecycle.get('enabled'):
        st.markdown("##### Lifecycle Risk theo thâm niên")
        worst = lifecycle.get('worst', {})
        c1, c2, c3 = st.columns(3)
        with c1:
            st.metric("Cohort rủi ro nhất", worst.get('Thâm niên', 'N/A'), f"N={worst.get('N', 0):,}")
        with c2:
            gap = lifecycle.get('early_gap')
            st.metric("Early gap", f"{gap:+.1f} điểm" if gap is not None and not pd.isna(gap) else "N/A", lifecycle.get('ews_window', ''))
        with c3:
            cliff = lifecycle.get('cliff')
            st.metric("Tenure cliff", cliff.get('label', 'Không phát hiện') if cliff else "Không phát hiện",
                      f"{cliff.get('drop'):+.1f} điểm" if cliff else None)

        cohort_df = lifecycle.get('cohort_df', pd.DataFrame())
        if not cohort_df.empty:
            y_col = f"Điểm {pillar_id} (%)" if f"Điểm {pillar_id} (%)" in cohort_df.columns else "EI (%)"
            fig_life = go.Figure()
            fig_life.add_trace(go.Scatter(
                x=cohort_df['Thâm niên'],
                y=cohort_df[y_col],
                mode='lines+markers+text',
                marker=dict(size=11, color=meta['color'], line=dict(width=2, color='white')),
                line=dict(color=meta['color'], width=3),
                text=[f"{v:.1f}" for v in cohort_df[y_col]],
                textposition='top center',
                customdata=cohort_df[['N', 'Risk Score']],
                hovertemplate='%{x}<br>Điểm: %{y:.1f}%<br>N=%{customdata[0]}<br>Risk=%{customdata[1]:.1f}<extra></extra>',
            ))
            fig_life.add_hline(y=65, line_dash="dot", line_color="#F59E0B", line_width=1)
            fig_life.update_layout(
                height=320,
                margin=dict(l=10, r=20, t=10, b=75),
                xaxis=dict(tickangle=-25, gridcolor='rgba(226,232,240,0.35)'),
                yaxis=dict(title=y_col, range=[max(0, cohort_df[y_col].min() - 8), min(100, cohort_df[y_col].max() + 10)],
                           gridcolor='rgba(226,232,240,0.6)'),
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(family='Inter'),
            )
            st.plotly_chart(fig_life, width='stretch', key=f"lifecycle_risk_{pillar_id}")

            table_cols = ['Thâm niên', 'N', y_col, 'EI (%)', '% Muốn nghỉ', '% Burnout', 'eNPS', 'Risk Score']
            for extra in ['Câu yếu nhất', 'Điểm câu yếu', '% tiêu cực câu yếu']:
                if extra in cohort_df.columns:
                    table_cols.append(extra)
            table_cols = [c for c in table_cols if c in cohort_df.columns]
            with st.expander("Bảng lifecycle diagnostics", expanded=False):
                st.dataframe(
                    cohort_df[table_cols].style.format(precision=1),
                    width='stretch',
                    hide_index=True,
                )

            playbook = lifecycle.get('playbook', {})
            if playbook:
                st.markdown(f"""
                <div style="background:#F8FAFC;border:1px solid #E2E8F0;border-left:4px solid {meta['color']};
                            border-radius:12px;padding:14px 16px;margin-top:12px;">
                    <div style="font-size:.72rem;font-weight:900;color:#64748B;text-transform:uppercase;letter-spacing:.09em;margin-bottom:6px;">Lifecycle playbook</div>
                    <div style="font-size:.92rem;color:#0A1F44;font-weight:850;margin-bottom:4px;">{playbook.get('label', 'Cohort rủi ro')} · {playbook.get('focus', '')}</div>
                    <div style="font-size:.82rem;color:#475569;line-height:1.65;">{playbook.get('action', '')}</div>
                </div>
                """, unsafe_allow_html=True)

            voice = lifecycle.get('voice_signals', {})
            if voice.get('enabled'):
                with st.expander("Tín hiệu open-text của cohort rủi ro nhất", expanded=False):
                    v1, v2, v3 = st.columns(3)
                    with v1:
                        st.metric("Phản hồi mở có nội dung", f"{voice.get('text_n', 0):,}")
                    with v2:
                        st.metric("NLP tiêu cực", f"{voice.get('negative_pct', 0):.1f}%", f"{voice.get('negative_n', 0):,} phản hồi")
                    with v3:
                        st.metric("Warning signals", f"{voice.get('warning_n', 0):,}")
                    signal_rows = []
                    for label, count in (voice.get('top_topics') or {}).items():
                        signal_rows.append({'Loại': 'Topic', 'Tín hiệu': label, 'Số lần': count})
                    for label, count in (voice.get('top_warnings') or {}).items():
                        signal_rows.append({'Loại': 'Warning', 'Tín hiệu': label, 'Số lần': count})
                    if signal_rows:
                        st.dataframe(pd.DataFrame(signal_rows), width='stretch', hide_index=True)

            hotspots = lifecycle.get('hotspots', pd.DataFrame())
            if isinstance(hotspots, pd.DataFrame) and not hotspots.empty:
                with st.expander("Hotspot đơn vị trong cohort rủi ro nhất", expanded=False):
                    st.caption("Chỉ hiện đơn vị có N >= 5 trong cohort thâm niên rủi ro nhất.")
                    st.dataframe(
                        hotspots.style.format(precision=1),
                        width='stretch',
                        hide_index=True,
                    )

        st.markdown("<hr style='border:1px dashed rgba(0,0,0,0.08);margin:22px 0;'>", unsafe_allow_html=True)

    if cross_priority.get('enabled'):
        st.markdown("##### Cross-Pillar Priority")
        top_cross = cross_priority.get('top', {})
        p1, p2, p3 = st.columns(3)
        with p1:
            st.metric("Hotspot liên trụ cột", top_cross.get('Đơn vị', 'N/A'), top_cross.get('Cấp', ''))
        with p2:
            st.metric("Trụ cột đi kèm", top_cross.get('Trụ cột đi kèm', 'N/A'), f"{top_cross.get('Điểm đi kèm', 0):.1f}%")
        with p3:
            st.metric("Risk score", f"{top_cross.get('Risk Score', 0):.1f}", f"{top_cross.get('Số trụ cột <65', 0)} trụ cột <65")

        companion_df = cross_priority.get('companion_df', pd.DataFrame())
        risk_df = cross_priority.get('risk_df', pd.DataFrame())
        c_left, c_right = st.columns([0.9, 1.35])
        with c_left:
            if not companion_df.empty:
                fig_pair = px.bar(
                    companion_df,
                    x='unit_count',
                    y='Tên trụ cột',
                    orientation='h',
                    color='avg_risk',
                    color_continuous_scale='OrRd',
                    text='unit_count',
                    hover_data=['Trụ cột đi kèm', 'avg_risk'],
                )
                fig_pair = fig_card(
                    fig_pair,
                    'Trụ cột đi kèm thường gặp',
                    'Các trụ cột thường đồng thời yếu với trụ cột đang xem',
                )
                fig_pair.update_traces(textposition='outside')
                fig_pair.update_layout(height=300, xaxis_title='Số đơn vị', yaxis_title=None, coloraxis_showscale=False)
                st.plotly_chart(fig_pair, width='stretch', key=f"cross_pillar_companion_{pillar_id}")
        with c_right:
            if not risk_df.empty:
                show_cols = [
                    'Cấp', 'Đơn vị', 'N', 'Điểm trụ cột', 'Trụ cột đi kèm',
                    'Điểm đi kèm', 'Số trụ cột <65', '% Muốn nghỉ', '% Burnout',
                    'Risk Score', 'Pattern'
                ]
                show_cols = [c for c in show_cols if c in risk_df.columns]
                st.dataframe(
                    risk_df[show_cols].style.format(precision=1),
                    width='stretch',
                    hide_index=True,
                    height=300,
                )

        top_action = top_cross.get('Next action')
        if top_action:
            st.markdown(f"""
            <div style="background:#FFF7ED;border:1px solid #FDBA7433;border-left:4px solid #FF5200;
                        border-radius:12px;padding:14px 16px;margin-top:12px;">
                <div style="font-size:.72rem;font-weight:900;color:#FF5200;text-transform:uppercase;letter-spacing:.09em;margin-bottom:6px;">Cross-pillar playbook</div>
                <div style="font-size:.92rem;color:#0A1F44;font-weight:850;margin-bottom:4px;">{top_cross.get('Pattern', 'Cross-pillar risk')}</div>
                <div style="font-size:.82rem;color:#475569;line-height:1.65;">{top_action}</div>
            </div>
            """, unsafe_allow_html=True)

        with st.expander("Chi tiết next action theo từng hotspot", expanded=False):
            action_cols = ['Cấp', 'Đơn vị', 'N', 'Pattern', 'Next action']
            action_cols = [c for c in action_cols if c in risk_df.columns]
            st.dataframe(risk_df[action_cols], width='stretch', hide_index=True)

        st.markdown("<hr style='border:1px dashed rgba(0,0,0,0.08);margin:22px 0;'>", unsafe_allow_html=True)

    # By Region
    if 'region' in df_work.columns:
        st.markdown("##### Điểm trụ cột theo Vùng vận hành")
        region_agg = df_work.groupby('region')['_pillar_score'].agg(['mean', 'count']).reset_index()
        region_agg = region_agg[region_agg['count'] >= 5].sort_values('mean', ascending=True)
        region_agg.columns = ['Vùng', 'Điểm TB', 'N']
        if not region_agg.empty:
            fig = go.Figure(go.Bar(
                y=region_agg['Vùng'], x=region_agg['Điểm TB'],
                orientation='h',
                marker=dict(
                    color=[meta['color'] if m >= 4.0 else '#F59E0B' if m >= 3.7 else '#EF4444'
                           for m in region_agg['Điểm TB']],
                    cornerradius=4,
                ),
                text=[f"{m:.2f}" for m in region_agg['Điểm TB']],
                textposition='outside',
            ))
            fig.add_vline(x=4.0, line_dash="dot", line_color="#10B981", line_width=1.5)
            fig.add_vline(x=3.5, line_dash="dot", line_color="#F59E0B", line_width=1)
            fig.update_layout(
                height=max(300, len(region_agg) * 30 + 80),
                margin=dict(l=10, r=60, t=10, b=10),
                xaxis=dict(range=[max(1, region_agg['Điểm TB'].min()-0.3), 5], gridcolor='rgba(226,232,240,0.6)'),
                yaxis=dict(automargin=True),
                plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                font=dict(family='Inter'),
            )
            st.plotly_chart(fig, width='stretch', key="region_risk_chart")

    st.markdown("---")

    # Division/Dept/Section breakdown
    from views import view_b_problem_groups
    try:
        view_b_problem_groups.render(df, cfg, group_id=group_id, pillar_filter=pillar_id)
    except TypeError:
        view_b_problem_groups.render(df, cfg)


# ─────────────────────────────────────────────────────────────
# TAB 4: NGUYÊN NHÂN & HÀNH ĐỘNG
# ─────────────────────────────────────────────────────────────

def _render_tab_root_cause(df, cfg, group_id, pillar_id):
    from views import view_d_root_cause, view_f_action_priority

    st.markdown("####  Phân tích nguyên nhân gốc rễ")
    try:
        view_d_root_cause.render(df, cfg, group_id, pillar_filter=pillar_id)
    except TypeError:
        view_d_root_cause.render(df, cfg, group_id)

    st.markdown("---")
    st.markdown("####  Ưu tiên hành động")
    try:
        view_f_action_priority.render(df, cfg, pillar_filter=pillar_id)
    except TypeError:
        view_f_action_priority.render(df, cfg)


# ─────────────────────────────────────────────────────────────
# TAB 5: BẤT THƯỜNG (Anomaly Detection)
# ─────────────────────────────────────────────────────────────

def _render_tab_anomaly(df, cfg, group_id, pillar_id):
    """Tab Bất thường — per-pillar anomalies + cross-pillar patterns."""
    scan = run_full_anomaly_scan(df, group_id)
    health = scan.get('health_score', {})
    priority_actions = scan.get('priority_actions', [])
    deep_dive = scan.get('deep_dive_plan', {})
    tenure = scan.get('tenure_cohorts', {})
    pillar_anomalies = scan.get('pillar_anomalies', {}).get(pillar_id, [])
    cross_anomalies = scan.get('cross_pillar_patterns', [])
    all_anomalies = pillar_anomalies + cross_anomalies

    st.markdown(f"""
    <div style="background:#F8FAFC;border:1px solid #E2E8F0;border-radius:12px;padding:14px 16px;margin-bottom:16px;">
        <div style="display:flex;gap:18px;align-items:center;flex-wrap:wrap;">
            <div>
                <div style="font-size:.68rem;font-weight:800;color:#64748B;text-transform:uppercase;letter-spacing:.08em;">Health snapshot</div>
                <div style="font-size:1.35rem;font-weight:900;color:#0A1F44;line-height:1.1;">{health.get('score', 'N/A')} · {health.get('label', 'N/A')}</div>
            </div>
            <div style="font-size:.8rem;color:#475569;line-height:1.55;">
                EI {health.get('EI', 'N/A')} · Burnout {health.get('burnout_score', 'N/A')} · Flight risk {health.get('flight_risk_pct', 'N/A')}%
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if deep_dive:
        trigger_txt = ", ".join(deep_dive.get('matched_triggers') or []) or "Chưa match trigger đặc thù"
        questions = deep_dive.get('questions') or []
        question_html = "".join([f"<li>{q}</li>" for q in questions[:3]])
        st.markdown(f"""
        <div style="background:#FFF7ED;border:1px solid #FDBA7433;border-left:4px solid #FF5200;border-radius:12px;padding:16px 18px;margin-bottom:16px;">
            <div style="font-size:.72rem;font-weight:900;color:#FF5200;text-transform:uppercase;letter-spacing:.09em;margin-bottom:6px;">Deep-dive trọng tâm · {deep_dive.get('urgency', 'LOW')}</div>
            <div style="font-size:1rem;font-weight:800;color:#0A1F44;margin-bottom:6px;">{deep_dive.get('focus', 'Đi sâu vào trụ cột thấp nhất')}</div>
            <div style="font-size:.82rem;color:#475569;line-height:1.6;margin-bottom:8px;">
                Trigger: <strong>{trigger_txt}</strong> · Trụ cột thấp nhất: <strong>{deep_dive.get('lowest_pillar', 'N/A')}</strong>
                ({deep_dive.get('lowest_pillar_score', 'N/A')}%)
            </div>
            <ul style="font-size:.82rem;color:#475569;line-height:1.65;margin:0 0 0 18px;">{question_html}</ul>
        </div>
        """, unsafe_allow_html=True)

    if tenure.get('enabled'):
        with st.expander("Tenure cohort diagnostics", expanded=False):
            cliff = tenure.get('cliff')
            early_gap = tenure.get('early_gap')
            st.caption(f"EWS window: {tenure.get('ews_window', 'N/A')} · Early gap: {early_gap if early_gap is not None else 'N/A'} điểm")
            if cliff:
                st.warning(f"Tenure cliff tại {cliff.get('label')}: EI giảm {cliff.get('drop')} điểm.")
            tenure_df = pd.DataFrame(tenure.get('records', []))
            if not tenure_df.empty:
                st.dataframe(tenure_df, width='stretch', hide_index=True)

    if priority_actions:
        st.markdown("#### Hành động ưu tiên từ full scan")
        for item in priority_actions[:3]:
            st.markdown(
                f"- **{item.get('id')} · {item.get('title')}**: {item.get('action')}"
            )
        st.markdown("---")

    render_anomaly_tab(all_anomalies, pillar_id=pillar_id, show_cross=True)


# ─────────────────────────────────────────────────────────────
# TAB 6: HRIS (TC3/TC4/TC5 only)
# ─────────────────────────────────────────────────────────────

def _render_tab_hris(df, cfg, group_id, pillar_id):
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
    """Main entry: lazily render only the selected pillar analysis section."""
    if df is None or df.empty:
        st.warning("Không có dữ liệu để hiển thị.")
        return

    _render_pillar_header(pillar_id, df, cfg, group_id)

    section_names = [
        "Chẩn đoán Nhanh",
        "Chi tiết Từng câu",
        "Nhóm Rủi ro",
        "Nguyên nhân & Hành động",
        "Bất thường",
    ]
    if pillar_id == 'TC4':
        section_names.append("HRIS & Rủi ro")
    elif pillar_id == 'TC3':
        section_names.append("HRIS & Năng suất")
    elif pillar_id == 'TC5':
        section_names.append("Rủi ro Gắn kết")

    selected_section = st.segmented_control(
        "Nội dung phân tích",
        options=section_names,
        default=section_names[0],
        selection_mode="single",
        key=f"pillar_section_{group_id}_{pillar_id}",
        label_visibility="collapsed",
        width="stretch",
    )
    selected_section = selected_section or section_names[0]

    renderers = {
        section_names[0]: _render_tab_quick_diagnosis,
        section_names[1]: _render_tab_detail,
        section_names[2]: _render_tab_risk_groups,
        section_names[3]: _render_tab_root_cause,
        section_names[4]: _render_tab_anomaly,
    }
    if len(section_names) > 5:
        renderers[section_names[5]] = _render_tab_hris

    loading_messages = {
        section_names[1]: "Đang tổng hợp chi tiết từng câu và phản hồi mở...",
        section_names[2]: "Đang xác định các nhóm, segment và lifecycle có rủi ro...",
        section_names[3]: "Đang phân tích driver, nguyên nhân và mức ưu tiên hành động...",
        section_names[4]: "Đang quét bất thường trong trụ cột và liên kết chéo...",
    }
    if len(section_names) > 5:
        loading_messages[section_names[5]] = "Đang đối chiếu dữ liệu HRIS và chỉ báo liên quan..."

    renderer = renderers[selected_section]
    loading_message = loading_messages.get(selected_section)
    if not loading_message:
        renderer(df, cfg, group_id, pillar_id)
        return

    loading_slot = st.empty()
    loader = TerminalLoader(loading_slot, f"Đang mở {selected_section}")
    loader.add(loading_message)
    try:
        renderer(df, cfg, group_id, pillar_id)
        loader.done(f"Đã hoàn tất {selected_section}.")
    finally:
        loader.clear()
