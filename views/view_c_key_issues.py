import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from shared.plotly_theme import COLORS
from shared.nlp_utils import extract_topic_stats, extract_representative_quotes, TOPIC_SHORT_LABELS
from utils.ai_generator import render_ai_insight_card

def render(df, cfg):
    codebook = cfg.get('codebook', {})
    open_cols = [q for q, info in codebook.items() if info['loại'] == 'open']

    q_options = {q: codebook[q]['tên'] for q in open_cols if q in df.columns}
    if not q_options:
        st.info("Nhóm này không có câu hỏi mở.")
        return

    sel_q = st.selectbox("Chọn câu hỏi mở", list(q_options.keys()),
                         format_func=lambda q: f"{q}: {q_options[q]}")
    cc = f'{sel_q}_clean'

    if cc not in df.columns or df[cc].notna().sum() < 30:
        st.warning("Không đủ phản hồi hợp lệ.")
        return

    texts = df[cc].dropna().tolist()
    n_texts = len(texts)
    
    from shared.plotly_theme import make_html_kpi, fig_card
    st.markdown(make_html_kpi("Tổng số ý kiến tự luận", f"{n_texts:,}", color="blue", icon="💬"), unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["Chủ đề nổi bật", "Promoter vs Detractor", "Trích dẫn tiêu biểu"])

    with tab1:
        topics = extract_topic_stats(texts)
        topic_data = [(TOPIC_SHORT_LABELS.get(t, t).replace('❓', '').strip(), c, c/n_texts*100)
                      for t, c in sorted(topics.items(), key=lambda x: -x[1])]
        topic_data = [t for t in topic_data if t[0]]
        
        if topic_data:
            top_topic = topic_data[0]
            ai_data = {
                "Total_Feedback": n_texts,
                "Top_Topic": top_topic[0],
                "Top_Topic_Percentage": round(top_topic[2], 1),
                "Group_Name": cfg.get('label', '')
            }
            prompt = "Phân tích cụm chủ đề (Topic) nổi bật nhất từ các phản hồi tự luận (Open-text). Đánh giá tầm quan trọng của chủ đề này và kết luận nó phản ánh 'tiếng lòng' gì của nhân viên."
            render_ai_insight_card("AI Topic Insight", ai_data, prompt, custom_style="margin-top: 16px; margin-bottom: 24px;")

            labels, counts, pcts = zip(*topic_data)
            fig = go.Figure(go.Bar(
                y=list(labels)[::-1], x=list(pcts)[::-1], orientation='h',
                marker_color=COLORS['orange'],
                text=[f'{p:.0f}% ({c:,})' for c, p in zip(list(counts)[::-1], list(pcts)[::-1])],
                textposition='outside'))
            fig = fig_card(fig, f'PHÂN BỔ CHỦ ĐỀ — {sel_q}', 'Tỷ lệ % phản hồi nhắc đến từng chủ đề')
            fig.update_layout(height=max(450, len(labels)*40), xaxis_title='', yaxis_title='', margin=dict(l=150))
            st.plotly_chart(fig, use_container_width=True)

    with tab2:
        if 'eNPS_group' in df.columns:
            for group, label, color in [('Promoter', 'Promoter', COLORS['green']),
                                         ('Detractor', 'Detractor', COLORS['red'])]:
                grp_texts = df[df['eNPS_group'] == group][cc].dropna().tolist()
                if len(grp_texts) > 20:
                    grp_topics = extract_topic_stats(grp_texts)
                    n_grp = len(grp_texts)
                    rows = [(TOPIC_SHORT_LABELS.get(t, t).replace('❓', '').strip(), c/n_grp*100)
                            for t, c in sorted(grp_topics.items(), key=lambda x: -x[1])]
                    rows = [r for r in rows if r[0]]
                    if rows:
                        st.markdown(f"**{label}** (n={n_grp:,})")
                        df_grp = pd.DataFrame(rows, columns=['Chủ đề', '%'])
                        fig = px.bar(df_grp, y='Chủ đề', x='%', orientation='h',
                                     color_discrete_sequence=[color], text='%', title=f'{label} — {sel_q}')
                        fig.update_traces(texttemplate='%{text:.0f}%', textposition='outside')
                        fig.update_layout(height=350, margin=dict(l=180))
                        st.plotly_chart(fig, width='stretch')

    with tab3:
        if topic_data:
            sel_topic = st.selectbox("Chọn chủ đề", [l for l, _, _ in topic_data])
            # Reverse map short label to full name
            full_name = next((k for k, v in TOPIC_SHORT_LABELS.items() if v.replace('❓', '').strip() == sel_topic), sel_topic)
            quotes = extract_representative_quotes(df, cc, full_name, n=10)
            if quotes:
                for i, q in enumerate(quotes, 1):
                    st.markdown(f"> {i}. *\"{q[:200]}\"*")
            else:
                st.info("Không tìm thấy trích dẫn.")
