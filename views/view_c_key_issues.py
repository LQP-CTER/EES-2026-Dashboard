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

    # Non-DA user context
    st.markdown("""
    <div style="background:#FFF7ED;border:1px solid #FED7AA;border-radius:12px;padding:14px 18px;margin-bottom:16px;display:flex;gap:12px;align-items:flex-start;">
        <div style="font-size:1.4rem;flex-shrink:0;">💬</div>
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
    
    from shared.plotly_theme import make_html_kpi, fig_card
    st.markdown(make_html_kpi("Tổng số ý kiến tự luận", f"{n_texts:,}", color="blue", icon="💬"), unsafe_allow_html=True)

    tab1, tab2, tab3, tab4 = st.tabs(["Chủ đề nổi bật", "Cụm từ khóa", "Promoter vs Detractor", "Trích dẫn tiêu biểu"])

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
            prompt = f"Dựa trên dữ liệu: {ai_data['Total_Feedback']} nhân viên đã chia sẻ ý kiến tự luận, và chủ đề được nhắc nhiều nhất là '{ai_data['Top_Topic']}' ({ai_data['Top_Topic_Percentage']}% nhân viên đề cập). Hãy giải thích bằng ngôn ngữ thông thường cho một Giám đốc không chuyên về data: (1) Chủ đề này có nghĩa là gì trong thực tế công việc hàng ngày của nhân viên? (2) Tại sao đây lại là điều họ muốn nói nhất? (3) Lãnh đạo cần chú ý điều gì từ tín hiệu này?"
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
        from shared.nlp_utils import extract_ngrams
        st.markdown("#### Top Cụm từ khóa được nhắc nhiều nhất")
        st.markdown("<span style='font-size:0.85rem; color:#64748B;'>Phân tích tần suất xuất hiện của các cụm từ (2-3 từ) để tìm ra từ khóa nóng nhất.</span>", unsafe_allow_html=True)
        ngrams_data = extract_ngrams(texts, n=2, top_k=15)
        if ngrams_data:
            df_ng = pd.DataFrame(ngrams_data, columns=['Cụm từ', 'Tần suất']).sort_values('Tần suất', ascending=True)
            fig_ng = px.bar(df_ng, y='Cụm từ', x='Tần suất', orientation='h', text='Tần suất', color_discrete_sequence=[COLORS['blue']])
            fig_ng = fig_card(fig_ng, 'PHÂN BỔ TỪ KHÓA (N-GRAMS)', 'Cụm từ khóa lặp lại nhiều nhất')
            fig_ng.update_traces(textposition='outside')
            fig_ng.update_layout(height=450, xaxis_title='', yaxis_title='', margin=dict(l=120))
            
            ai_data_ng = {
                "Top_Ngrams": df_ng.tail(3).to_dict(orient='records')
            }
            prompt_ng = f"Dựa trên 3 cụm từ xuất hiện nhiều nhất: {ai_data_ng['Top_Ngrams']}. Hãy phân tích ngắn gọn: Những cụm từ này tiết lộ điều gì về trải nghiệm thực tế của nhân viên? Tại sao các từ khóa này lại đi cùng nhau?"
            render_ai_insight_card("AI N-Grams Insight", ai_data_ng, prompt_ng, custom_style="margin-bottom: 24px;")
            
            st.plotly_chart(fig_ng, use_container_width=True)
        else:
            st.info("Chưa có đủ cụm từ khóa nổi bật.")

    with tab3:
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
                        
            # Thêm AI Insight chung cho Promoter vs Detractor
            ai_data_diff = {
                "Survey_Question": sel_q
            }
            prompt_diff = f"Chỉ dựa vào sự khác biệt tự nhiên trong hành vi: Phân tích ngắn gọn về sự khác nhau cơ bản trong cách Promoter (người gắn bó) và Detractor (người bất mãn) phản hồi về vấn đề này. Tại sao lãnh đạo cần quan tâm cả 2 luồng ý kiến?"
            render_ai_insight_card("AI Sentiment Comparison", ai_data_diff, prompt_diff, custom_style="margin-top: 16px; margin-bottom: 24px;")

    with tab4:
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
                
