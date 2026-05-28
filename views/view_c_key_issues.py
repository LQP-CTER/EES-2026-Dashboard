import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from shared.plotly_theme import COLORS, fig_card
from shared.nlp_utils import (
    extract_topic_stats, extract_topic_stats_with_tone,
    extract_representative_quotes, TOPIC_SHORT_LABELS, TOPIC_SUB_LABELS,
    extract_sub_topic_stats, classify_topics, classify_sub_topics,
    compute_sentiment_intensity
)
from utils.ai_generator import render_ai_insight_card


def render(df, cfg, pillar_filter=None):
    codebook = cfg.get('codebook', {})
    open_cols = [q for q, info in codebook.items() if info['loại'] == 'open']

    q_options = {q: codebook[q]['tên'] for q in open_cols if q in df.columns}
    if not q_options:
        st.info("Nhóm này không có câu hỏi mở.")
        return

    st.markdown("""
    <div style="background:#FFF7ED;border:1px solid #FED7AA;border-radius:12px;padding:16px 20px;margin-bottom:16px;">
        <div>
            <div style="font-size:0.82rem;font-weight:700;color:#C2410C;margin-bottom:4px;">Lắng nghe tiếng nói nhân viên — Họ thực sự nói gì?</div>
            <div style="font-size:0.8rem;color:#475569;line-height:1.55;">
                Hệ thống tự động phân tích <strong>toàn bộ câu trả lời tự luận</strong> và nhóm chúng thành các chủ đề.
                Chủ đề nào được nhắc nhiều nhất = vấn đề đang "nóng nhất" trong đầu nhân viên.
                Bạn cũng có thể xem nhân viên gắn bó nhất (<em>Promoter</em>) và bất mãn nhất (<em>Detractor</em>) đang nói về điều gì khác nhau.
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    sel_q = st.selectbox("Chọn câu hỏi mở để phân tích:", list(q_options.keys()),
                         format_func=lambda q: f"{q}: {q_options[q]}")
    cc = f'{sel_q}_clean'

    if cc not in df.columns or df[cc].notna().sum() < 30:
        st.warning("Không đủ phản hồi hợp lệ.")
        return

    texts = df[cc].dropna().tolist()
    n_texts = len(texts)

    from shared.plotly_theme import make_html_kpi
    st.markdown(make_html_kpi("Tổng số ý kiến tự luận", f"{n_texts:,}", color="blue", icon=""), unsafe_allow_html=True)

    # ══════════════════════════════════════════════════════════════
    # PHẦN 1: TỔNG QUAN CHỦ ĐỀ & GIỌNG ĐIỆU
    # ══════════════════════════════════════════════════════════════
    st.markdown("### 1. Tổng quan Chủ đề & Giọng điệu")
    st.markdown("Phân bổ các chủ đề được nhắc đến và giọng điệu (tích cực/trung lập/tiêu cực) của từng chủ đề.")

    topic_tone_data = extract_topic_stats_with_tone(texts)

    if not topic_tone_data:
        st.info("Không đủ dữ liệu để phân tích chủ đề.")
        return

    rows = []
    for topic, counts in sorted(topic_tone_data.items(), key=lambda x: -x[1]['total']):
        short = TOPIC_SHORT_LABELS.get(topic, topic).replace('', '').strip()
        if not short:
            continue
        total = counts['total']
        rows.append({
            'Chủ đề': short,
            'Chủ đề đầy đủ': topic,
            'Tích cực': counts['positive'],
            'Trung lập': counts['neutral'],
            'Tiêu cực': counts['negative'],
            'Total': total,
        })

    df_raw = pd.DataFrame(rows)

    if df_raw.empty:
        st.info("Không có chủ đề nào được phát hiện.")
        return

    df_topic = df_raw.groupby('Chủ đề', as_index=False).agg({
        'Chủ đề đầy đủ': 'first',
        'Tích cực': 'sum',
        'Trung lập': 'sum',
        'Tiêu cực': 'sum',
        'Total': 'sum',
    })

    df_topic['Pct'] = df_topic['Total'] / n_texts * 100
    df_topic['Neg_Pct'] = df_topic['Tiêu cực'] / df_topic['Total'] * 100
    df_topic['Tích cực'] = df_topic['Tích cực'] / df_topic['Total'] * 100
    df_topic['Trung lập'] = df_topic['Trung lập'] / df_topic['Total'] * 100
    df_topic['Tiêu cực'] = df_topic['Tiêu cực'] / df_topic['Total'] * 100

    df_topic = df_topic.sort_values('Total', ascending=False).reset_index(drop=True)

    top_topic = df_topic.iloc[0]
    ai_data = {
        "Total_Feedback": n_texts,
        "Top_Topic": top_topic['Chủ đề'],
        "Top_Topic_Percentage": round(top_topic['Pct'], 1),
        "Top_Topic_Negative_Pct": round(top_topic['Neg_Pct'], 1),
        "Group_Name": cfg.get('label', '')
    }
    prompt = (
        f"Dựa trên dữ liệu: {ai_data['Total_Feedback']} nhân viên đã chia sẻ ý kiến tự luận. "
        f"Chủ đề được nhắc nhiều nhất là '{ai_data['Top_Topic']}' ({ai_data['Top_Topic_Percentage']}% nhân viên đề cập), "
        f"trong đó {ai_data['Top_Topic_Negative_Pct']}% mang giọng điệu tiêu cực. "
        f"Hãy giải thích bằng ngôn ngữ thông thường cho một Giám đốc không chuyên về data: "
        f"(1) Tỷ lệ tiêu cực này có đáng lo không? "
        f"(2) Tại sao đây lại là điều họ muốn nói nhất? "
        f"(3) Lãnh đạo cần chú ý điều gì từ tín hiệu này?"
    )
    render_ai_insight_card("AI Topic Insight", ai_data, prompt, custom_style="margin-top: 16px; margin-bottom: 24px;")

    df_plot = df_topic.sort_values('Total', ascending=True)

    fig = go.Figure()
    for tone, color in [('Tiêu cực', '#EF4444'), ('Trung lập', '#94A3B8'), ('Tích cực', '#10B981')]:
        fig.add_trace(go.Bar(
            y=df_plot['Chủ đề'],
            x=df_plot[tone],
            name=tone,
            orientation='h',
            marker_color=color,
            text=[f'{v:.0f}%' if v > 8 else '' for v in df_plot[tone]],
            textposition='inside',
            textfont=dict(color='white', size=11),
        ))

    fig = fig_card(fig, f'PHÂN BỔ CHỦ ĐỀ & GIỌNG ĐIỆU — {sel_q}',
                   'Mỗi thanh = 1 chủ đề. Màu đỏ = tiêu cực, Xanh = tích cực, Xám = trung lập')
    fig.update_layout(
        barmode='stack',
        height=max(450, len(df_plot) * 45),
        xaxis_title='% Giọng điệu',
        yaxis_title='',
        margin=dict(l=120),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    st.plotly_chart(fig, use_container_width=True)

    anno = df_topic.sort_values('Neg_Pct', ascending=False).head(3)
    anno_html = " · ".join([f"<strong>{r['Chủ đề']}</strong> ({r['Neg_Pct']:.0f}% tiêu cực)" for _, r in anno.iterrows()])
    st.markdown(f"""
    <div style="background: #FEF2F2; border-left: 4px solid #DC2626; padding: 10px 14px; border-radius: 6px; font-size: 0.82rem; color: #7F1D1D;">
        <strong>Top chủ đề tiêu cực nhất:</strong> {anno_html}
    </div>
    """, unsafe_allow_html=True)

    # ══════════════════════════════════════════════════════════════
    # PHẦN 2: BẢNG CHI TIẾT HIERARCHICAL (LABEL CHA + LABEL CON)
    # ══════════════════════════════════════════════════════════════
    st.markdown("---")
    st.markdown("### 2. Phân tích Chi tiết theo Chủ đề")
    st.markdown("Bảng dưới đây hiển thị từng chủ đề (label cha) và các nguyên nhân chi tiết (label con) bên trong.")

    hierarchical_rows = []
    seen_parents = set()

    for _, row in df_topic.iterrows():
        parent_short = row['Chủ đề']
        parent_full = row['Chủ đề đầy đủ']
        parent_total = row['Total']
        parent_pct = row['Pct']
        parent_neg = row['Neg_Pct']

        if parent_short in seen_parents:
            continue
        seen_parents.add(parent_short)

        hierarchical_rows.append({
            'Cấp': 'Cha',
            'Chủ đề': parent_short,
            'Nhãn con': '',
            'Số lượng': parent_total,
            '% trên tổng': parent_pct,
            '% Tiêu cực': parent_neg,
            'parent_full': parent_full,
        })

        if parent_full in TOPIC_SUB_LABELS:
            sub_counts = extract_sub_topic_stats(texts, parent_full)
            if sub_counts:
                seen_subs = set()
                for sub_label, sub_count in sorted(sub_counts.items(), key=lambda x: -x[1]):
                    if sub_label in seen_subs:
                        continue
                    seen_subs.add(sub_label)
                    sub_pct = sub_count / n_texts * 100
                    hierarchical_rows.append({
                        'Cấp': 'Con',
                        'Chủ đề': '',
                        'Nhãn con': f"  └ {sub_label}",
                        'Số lượng': sub_count,
                        '% trên tổng': sub_pct,
                        '% Tiêu cực': None,
                        'parent_full': parent_full,
                    })

    df_hierarchical = pd.DataFrame(hierarchical_rows)

    def style_hierarchical(val):
        if val == 'Cha':
            return 'background-color: #F1F5F9; font-weight: 700;'
        else:
            return 'background-color: #FFFFFF; padding-left: 20px;'

    styled_df = df_hierarchical[['Cấp', 'Chủ đề', 'Nhãn con', 'Số lượng', '% trên tổng', '% Tiêu cực']].copy()
    styled_df = styled_df.style.apply(lambda row: [style_hierarchical(row['Cấp'])] * len(row), axis=1)

    st.dataframe(styled_df, width='stretch', hide_index=True, height=600)

    st.markdown("""
    <div style="background:#F8FAFC;border:1px solid #E2E8F0;border-radius:8px;padding:12px 16px;margin-top:12px;">
        <div style="font-size:0.78rem;color:#475569;line-height:1.6;">
            <strong>Ghi chú:</strong> Dòng màu xám = Chủ đề chính (label cha). Dòng trắng thụt vào = Nguyên nhân chi tiết (label con). 
            Một chủ đề có thể có nhiều nguyên nhân con khác nhau.
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ══════════════════════════════════════════════════════════════
    # PHẦN 3: SO SÁNH PROMOTER VS DETRACTOR
    # ══════════════════════════════════════════════════════════════
    if 'eNPS_group' in df.columns:
        st.markdown("---")
        st.markdown("### 3. So sánh Promoter vs Detractor")
        st.markdown("Nhân viên gắn bó (Promoter) và bất mãn (Detractor) đang nói về điều gì khác nhau?")

        col1, col2 = st.columns(2)

        with col1:
            promoter_texts = df[df['eNPS_group'] == 'Promoter'][cc].dropna().tolist()
            if len(promoter_texts) > 20:
                promoter_topics = extract_topic_stats(promoter_texts)
                n_promoter = len(promoter_texts)
                rows_promoter = [(TOPIC_SHORT_LABELS.get(t, t).replace('', '').strip(), c / n_promoter * 100)
                                 for t, c in sorted(promoter_topics.items(), key=lambda x: -x[1])]
                rows_promoter = [r for r in rows_promoter if r[0]]
                if rows_promoter:
                    st.markdown(f"**Promoter** (n={n_promoter:,})")
                    df_promoter = pd.DataFrame(rows_promoter, columns=['Chủ đề', '%'])
                    fig_promoter = px.bar(df_promoter, y='Chủ đề', x='%', orientation='h',
                                          color_discrete_sequence=[COLORS['green']], text='%',
                                          title='Promoter — Họ nói gì?')
                    fig_promoter.update_traces(texttemplate='%{text:.0f}%', textposition='outside')
                    fig_promoter.update_layout(height=400, margin=dict(l=180))
                    st.plotly_chart(fig_promoter, use_container_width=True)

        with col2:
            detractor_texts = df[df['eNPS_group'] == 'Detractor'][cc].dropna().tolist()
            if len(detractor_texts) > 20:
                detractor_topics = extract_topic_stats(detractor_texts)
                n_detractor = len(detractor_texts)
                rows_detractor = [(TOPIC_SHORT_LABELS.get(t, t).replace('', '').strip(), c / n_detractor * 100)
                                  for t, c in sorted(detractor_topics.items(), key=lambda x: -x[1])]
                rows_detractor = [r for r in rows_detractor if r[0]]
                if rows_detractor:
                    st.markdown(f"**Detractor** (n={n_detractor:,})")
                    df_detractor = pd.DataFrame(rows_detractor, columns=['Chủ đề', '%'])
                    fig_detractor = px.bar(df_detractor, y='Chủ đề', x='%', orientation='h',
                                           color_discrete_sequence=[COLORS['red']], text='%',
                                           title='Detractor — Họ nói gì?')
                    fig_detractor.update_traces(texttemplate='%{text:.0f}%', textposition='outside')
                    fig_detractor.update_layout(height=400, margin=dict(l=180))
                    st.plotly_chart(fig_detractor, use_container_width=True)

        ai_data_diff = {"Survey_Question": sel_q}
        prompt_diff = f"Chỉ dựa vào sự khác biệt tự nhiên trong hành vi: Phân tích ngắn gọn về sự khác nhau cơ bản trong cách Promoter (người gắn bó) và Detractor (người bất mãn) phản hồi về vấn đề này. Tại sao lãnh đạo cần quan tâm cả 2 luồng ý kiến?"
        render_ai_insight_card("AI Sentiment Comparison", ai_data_diff, prompt_diff,
                               custom_style="margin-top: 16px; margin-bottom: 24px;")

    # ══════════════════════════════════════════════════════════════
    # PHẦN 4: TRÍCH DẪN TIÊU BIỂU
    # ══════════════════════════════════════════════════════════════
    st.markdown("---")
    st.markdown("### 4. Trích dẫn Tiêu biểu")
    st.markdown("Chọn một chủ đề để xem các câu phản hồi thực tế từ nhân viên.")

    topic_options = [row['Chủ đề'] for _, row in df_topic.iterrows()]
    sel_topic_short = st.selectbox("Chọn chủ đề để xem trích dẫn:", topic_options)

    full_name = next(
        (k for k, v in TOPIC_SHORT_LABELS.items()
         if v.replace('', '').strip() == sel_topic_short),
        sel_topic_short
    )

    if full_name in TOPIC_SUB_LABELS:
        sub_counts = extract_sub_topic_stats(texts, full_name)
        if sub_counts:
            st.markdown(f"""
            <div style="background:#F8FAFC;border:1px solid #E2E8F0;border-radius:12px;
                        padding:14px 18px;margin-bottom:16px;">
                <div style="font-size:0.7rem;font-weight:700;color:#94A3B8;
                            text-transform:uppercase;letter-spacing:0.09em;margin-bottom:10px;">
                    Phân tích chi tiết nhãn con — {sel_topic_short}
                </div>
                <div style="display:flex;flex-wrap:wrap;gap:8px;">
            """, unsafe_allow_html=True)

            color_pool = ['#FF5200', '#F59E0B', '#10B981', '#3B82F6',
                          '#8B5CF6', '#EF4444', '#06B6D4', '#EC4899']
            for i, (sub_label, count) in enumerate(sorted(sub_counts.items(), key=lambda x: -x[1])):
                pct = count / len(texts) * 100
                col_hex = color_pool[i % len(color_pool)]
                st.markdown(f"""
                <span style="background:{col_hex}18;color:{col_hex};
                             border:1px solid {col_hex}44;
                             padding:4px 12px;border-radius:20px;
                             font-size:0.78rem;font-weight:600;display:inline-block;">
                    {sub_label} &nbsp;·&nbsp; {count} ({pct:.1f}%)
                </span>
                """, unsafe_allow_html=True)

            st.markdown("</div></div>", unsafe_allow_html=True)

            df_sub = pd.DataFrame(
                [(k, v, v / len(texts) * 100) for k, v in sub_counts.items()],
                columns=['Nhãn con', 'Số lượng', '%']
            ).sort_values('Số lượng', ascending=True)

            fig_sub = px.bar(
                df_sub, y='Nhãn con', x='Số lượng', orientation='h',
                text='Số lượng', color='%',
                color_continuous_scale='Oranges'
            )
            fig_sub = fig_card(
                fig_sub,
                f'Phân tách nhãn con — {sel_topic_short}',
                f'Nhân viên đề cập đến nguyên nhân chi tiết nào nhiều nhất?'
            )
            fig_sub.update_traces(textposition='outside')
            fig_sub.update_layout(
                height=max(300, len(df_sub) * 50 + 80),
                coloraxis_showscale=False,
                margin=dict(l=160)
            )
            st.plotly_chart(fig_sub, use_container_width=True)

    st.markdown(f"**Trích dẫn tiêu biểu — {sel_topic_short}**")
    quotes = extract_representative_quotes(df, cc, full_name, n=10)
    if quotes:
        for i, q in enumerate(quotes, 1):
            st.markdown(f"> {i}. *\"{q[:200]}\"*")
    else:
        st.info("Không tìm thấy trích dẫn.")

