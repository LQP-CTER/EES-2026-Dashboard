import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from shared.plotly_theme import COLORS
from shared.nlp_utils import (
    extract_topic_stats, extract_topic_stats_with_tone,
    extract_representative_quotes, TOPIC_SHORT_LABELS,
    extract_ngrams, extract_action_suggestions, compute_sentiment_intensity
)
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
    
    from shared.plotly_theme import make_html_kpi, fig_card
    st.markdown(make_html_kpi("Tổng số ý kiến tự luận", f"{n_texts:,}", color="blue", icon=""), unsafe_allow_html=True)

    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "Chủ đề nổi bật", "Cụm từ khóa", "Đề xuất hành động", 
        "Promoter vs Detractor", "Trích dẫn tiêu biểu"
    ])

    # ── TAB 1: CHỦ ĐỀ NỔI BẬT (STACKED BAR VỚI TONE) ──
    with tab1:
        topic_tone_data = extract_topic_stats_with_tone(texts)
        
        if topic_tone_data:
            # Build stacked bar data
            rows = []
            for topic, counts in sorted(topic_tone_data.items(), key=lambda x: -x[1]['total']):
                short = TOPIC_SHORT_LABELS.get(topic, topic).replace('❓', '').strip()
                if not short:
                    continue
                total = counts['total']
                rows.append({
                    'Chủ đề': short,
                    'Tích cực': counts['positive'] / total * 100,
                    'Trung lập': counts['neutral'] / total * 100,
                    'Tiêu cực': counts['negative'] / total * 100,
                    'Total': total,
                    'Pct': total / n_texts * 100,
                    'Neg_Pct': counts['negative'] / total * 100,
                })
            
            df_topic = pd.DataFrame(rows)
            
            if not df_topic.empty:
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

                # Stacked bar chart
                df_plot = df_topic.sort_values('Total', ascending=True)
                
                fig = go.Figure()
                for tone, color, symbol in [
                    ('Tiêu cực', '#EF4444', '🔴'),
                    ('Trung lập', '#94A3B8', '⚪'),
                    ('Tích cực', '#10B981', '🟢'),
                ]:
                    fig.add_trace(go.Bar(
                        y=df_plot['Chủ đề'],
                        x=df_plot[tone],
                        name=f'{symbol} {tone}',
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
                    height=max(450, len(df_plot)*45),
                    xaxis_title='% Giọng điệu',
                    yaxis_title='',
                    margin=dict(l=120),
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
                )
                st.plotly_chart(fig, use_container_width=True)
                
                # Summary annotation
                anno = df_topic.sort_values('Neg_Pct', ascending=False).head(3)
                anno_html = " · ".join([f"<strong>{r['Chủ đề']}</strong> ({r['Neg_Pct']:.0f}% tiêu cực)" for _, r in anno.iterrows()])
                st.markdown(f"""
                <div style="background: #FEF2F2; border-left: 4px solid #DC2626; padding: 10px 14px; border-radius: 6px; font-size: 0.82rem; color: #7F1D1D;">
                    <strong>Top chủ đề tiêu cực nhất:</strong> {anno_html}
                </div>
                """, unsafe_allow_html=True)

        # Also store for Tab 5
        topics = extract_topic_stats(texts)
        topic_data = [(TOPIC_SHORT_LABELS.get(t, t).replace('❓', '').strip(), c, c/n_texts*100)
                      for t, c in sorted(topics.items(), key=lambda x: -x[1])]
        topic_data = [t for t in topic_data if t[0]]

    # ── TAB 2: CỤM TỪ KHÓA + TREEMAP ──
    with tab2:
        st.markdown("#### Top Cụm từ khóa được nhắc nhiều nhất")
        st.markdown("<span style='font-size:0.85rem; color:#64748B;'>Phân tích tần suất xuất hiện của các cụm từ (2-3 từ) để tìm ra từ khóa nóng nhất.</span>", unsafe_allow_html=True)
        
        ngrams_data = extract_ngrams(texts, n=2, top_k=15)
        if ngrams_data:
            df_ng = pd.DataFrame(ngrams_data, columns=['Cụm từ', 'Tần suất']).sort_values('Tần suất', ascending=True)
            
            # Horizontal bar chart
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
            
            # Treemap Word Cloud
            st.markdown("#### Bản đồ Từ khóa (Word Cloud)")
            df_tree = pd.DataFrame(ngrams_data, columns=['Cụm từ', 'Tần suất'])
            fig_tree = px.treemap(
                df_tree, path=['Cụm từ'], values='Tần suất',
                color='Tần suất', color_continuous_scale='Blues',
            )
            fig_tree.update_traces(
                textinfo='label+value',
                textfont=dict(size=14),
                hovertemplate='<b>%{label}</b><br>Số lần xuất hiện: %{value}<extra></extra>'
            )
            fig_tree.update_layout(
                height=400, margin=dict(t=30, l=10, r=10, b=10),
                coloraxis_showscale=False
            )
            st.plotly_chart(fig_tree, use_container_width=True)
        else:
            st.info("Chưa có đủ cụm từ khóa nổi bật.")

    # ── TAB 3: ĐỀ XUẤT HÀNH ĐỘNG ──
    with tab3:
        st.markdown("""
        <div style="background:#F0FDF4;border:1px solid #BBF7D0;border-radius:10px;padding:12px 16px;margin-bottom:16px;">
            <strong style="color:#166534;font-size:0.85rem;">Phát hiện đề xuất hành động:</strong>
            <span style="font-size:0.8rem;color:#475569;"> Hệ thống tự động lọc ra các câu mang tính <strong>đề xuất, kiến nghị, mong muốn</strong> từ nhân viên — những insight có giá trị hành động cao nhất.</span>
        </div>
        """, unsafe_allow_html=True)
        
        suggestions = extract_action_suggestions(texts)
        
        if suggestions:
            st.markdown(make_html_kpi("Số đề xuất phát hiện", f"{len(suggestions):,}", color="green", icon=""), unsafe_allow_html=True)
            
            # Group by topic
            df_sug = pd.DataFrame(suggestions)
            topic_counts = df_sug['topic'].value_counts()
            
            fig_sug = px.bar(
                x=topic_counts.values, y=topic_counts.index, orientation='h',
                text=topic_counts.values, color_discrete_sequence=[COLORS['green']]
            )
            fig_sug = fig_card(fig_sug, 'ĐỀ XUẤT HÀNH ĐỘNG THEO CHỦ ĐỀ', 'Nhân viên muốn cải thiện điều gì nhất?')
            fig_sug.update_traces(textposition='outside')
            fig_sug.update_layout(height=350, xaxis_title='Số đề xuất', yaxis_title='', margin=dict(l=150))
            st.plotly_chart(fig_sug, use_container_width=True)
            
            ai_data_sug = {
                "Total_Suggestions": len(suggestions),
                "Top_Topics": topic_counts.head(3).to_dict()
            }
            prompt_sug = f"Nhân viên đã đưa ra {ai_data_sug['Total_Suggestions']} đề xuất hành động cụ thể. Top 3 chủ đề được kiến nghị nhiều nhất: {ai_data_sug['Top_Topics']}. Hãy phân tích: (1) Đề xuất nào khả thi nhất có thể triển khai trong 30 ngày? (2) Điều gì cho thấy nhân viên vẫn đang quan tâm đến công ty (thay vì im lặng bỏ đi)?"
            render_ai_insight_card("AI Action Extraction", ai_data_sug, prompt_sug, custom_style="margin-top: 16px; margin-bottom: 24px;")
            
            # Detail table
            st.markdown("#### Chi tiết đề xuất")
            df_display = df_sug[['topic', 'tone', 'text']].copy()
            df_display.columns = ['Chủ đề', 'Giọng điệu', 'Nội dung đề xuất']
            
            # Map tone labels
            tone_map = {'tích_cực': '🟢 Tích cực', 'tiêu_cực': '🔴 Tiêu cực', 'trung_lập': '⚪ Trung lập'}
            df_display['Giọng điệu'] = df_display['Giọng điệu'].map(tone_map).fillna('⚪ Trung lập')
            
            # Short label for topic
            for full, short in TOPIC_SHORT_LABELS.items():
                df_display['Chủ đề'] = df_display['Chủ đề'].str.replace(full, short, regex=False)
            
            col_config = {
                'Chủ đề': st.column_config.TextColumn('Chủ đề', width="medium"),
                'Giọng điệu': st.column_config.TextColumn('Giọng điệu', width="small"),
                'Nội dung đề xuất': st.column_config.TextColumn('Nội dung', width="large"),
            }
            st.dataframe(df_display.head(50), use_container_width=True, hide_index=True, column_config=col_config, height=400)
        else:
            st.info("Không phát hiện đề xuất hành động cụ thể trong phản hồi.")

    # ── TAB 4: PROMOTER VS DETRACTOR ──
    with tab4:
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

    # ── TAB 5: TRÍCH DẪN TIÊU BIỂU + SUB-LABELS ──
    with tab5:
        from shared.nlp_utils import (
            TOPIC_SUB_LABELS, classify_sub_topics, extract_sub_topic_stats
        )
        if topic_data:
            sel_topic_short = st.selectbox("Chọn chủ đề", [l for l, _, _ in topic_data])
            # Reverse map short label → full name
            full_name = next(
                (k for k, v in TOPIC_SHORT_LABELS.items()
                 if v.replace('❓', '').strip() == sel_topic_short),
                sel_topic_short
            )

            # ── Sub-label breakdown (if this parent has children) ──
            if full_name in TOPIC_SUB_LABELS:
                sub_counts = extract_sub_topic_stats(texts, full_name)
                if sub_counts:
                    total_sub = sum(sub_counts.values())
                    st.markdown(f"""
                    <div style="background:#F8FAFC;border:1px solid #E2E8F0;border-radius:12px;
                                padding:14px 18px;margin-bottom:16px;">
                        <div style="font-size:0.7rem;font-weight:700;color:#94A3B8;
                                    text-transform:uppercase;letter-spacing:0.09em;margin-bottom:10px;">
                            Phân tích chi tiết nhãn con — {sel_topic_short}
                        </div>
                        <div style="display:flex;flex-wrap:wrap;gap:8px;">
                    """, unsafe_allow_html=True)

                    color_pool = [
                        '#FF5200', '#F59E0B', '#10B981', '#3B82F6',
                        '#8B5CF6', '#EF4444', '#06B6D4', '#EC4899'
                    ]
                    for i, (sub_label, count) in enumerate(
                        sorted(sub_counts.items(), key=lambda x: -x[1])
                    ):
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

                    # Bar chart of sub-labels
                    import plotly.express as px
                    from shared.plotly_theme import fig_card
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
                else:
                    st.info(f"Không tìm thấy đủ dữ liệu nhãn con cho chủ đề '{sel_topic_short}'. "
                            f"Hệ thống sẽ tiếp tục hiển thị trích dẫn gốc bên dưới.")
            else:
                st.info(f"Chủ đề '{sel_topic_short}' chưa có phân tích nhãn con.")

            st.markdown("---")
            st.markdown(f"**📝 Trích dẫn tiêu biểu — {sel_topic_short}**")
            quotes = extract_representative_quotes(df, cc, full_name, n=10)
            if quotes:
                for i, q in enumerate(quotes, 1):
                    st.markdown(f"> {i}. *\"{q[:200]}\"*")
            else:
                st.info("Không tìm thấy trích dẫn.")

