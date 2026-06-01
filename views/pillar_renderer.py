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
from utils.anomaly_detector import detect_pillar_anomalies, detect_cross_pillar
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
    else:
        pillar_mean, fav_pct = None, 0

    color = meta['color']
    score_str = f"{pillar_mean:.2f}" if pillar_mean else "N/A"
    fav_str = f"{fav_pct:.1f}%"
    weight_str = f"{PILLAR_WEIGHTS.get(pillar_id, 0)*100:.0f}%"

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
                <div style="font-size:1.8rem;font-weight:900;color:#0A1F44;line-height:1;">{len(q_cols)}</div>
                <div style="font-size:0.7rem;color:#94A3B8;margin-top:3px;">câu hỏi trong trụ cột</div>
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
        st.info("Không có câu hỏi nào trong trụ cột này.")
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
        st.info("Không có câu hỏi nào trong trụ cột này.")
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
                            <span style="color:#D97706; font-weight:700;">⚠️ Nghịch lý phát hiện:</span> 
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

    # By Region
    if 'region' in df_work.columns:
        st.markdown("##### Điểm trụ cột theo Vùng vận hành")
        region_agg = df_work.groupby('region')['_pillar_score'].agg(['mean', 'count']).reset_index()
        region_agg = region_agg[region_agg['count'] >= 10].sort_values('mean', ascending=True)
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
        view_b_problem_groups.render(df, cfg, pillar_filter=pillar_id)
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
    pillar_anomalies = detect_pillar_anomalies(df, group_id, pillar_id)
    cross_anomalies  = detect_cross_pillar(df, group_id)
    all_anomalies    = pillar_anomalies + cross_anomalies
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
    """Main entry: render pillar with 5–6 tabs."""
    if df is None or df.empty:
        st.warning("Không có dữ liệu để hiển thị.")
        return

    _render_pillar_header(pillar_id, df, cfg, group_id)

    # Build tabs
    tab_names = [
        "Chẩn đoán Nhanh",
        "Chi tiết Từng câu",
        "Nhóm Rủi ro",
        "Nguyên nhân & Hành động",
        "Bất thường",
    ]
    if pillar_id == 'TC4':
        tab_names.append("HRIS & Rủi ro")
    elif pillar_id == 'TC3':
        tab_names.append("HRIS & Năng suất")
    elif pillar_id == 'TC5':
        tab_names.append("Rủi ro Gắn kết")

    tabs = st.tabs(tab_names)

    with tabs[0]:
        _render_tab_quick_diagnosis(df, cfg, group_id, pillar_id)

    with tabs[1]:
        _render_tab_detail(df, cfg, group_id, pillar_id)

    with tabs[2]:
        _render_tab_risk_groups(df, cfg, group_id, pillar_id)

    with tabs[3]:
        _render_tab_root_cause(df, cfg, group_id, pillar_id)

    with tabs[4]:
        _render_tab_anomaly(df, cfg, group_id, pillar_id)

    if len(tabs) > 5:
        with tabs[5]:
            _render_tab_hris(df, cfg, group_id, pillar_id)
