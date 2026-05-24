import streamlit as st
import plotly.express as px
import pandas as pd
from shared.plotly_theme import COLORS, apply_theme, fig_card
from utils.ai_generator import render_ai_insight_card

def render(df, cfg):
    apply_theme()
    codebook = cfg.get('codebook', {})
    likert_cols = [q for q, info in codebook.items() if info['loại'] == 'likert']

    st.markdown(f'<h3 style="color: #0A1F44; font-weight: 800; margin-bottom: 24px;">⚡ Ma trận Ưu tiên Hành động — {cfg.get("label", "")}</h3>', unsafe_allow_html=True)

    from scipy import stats as scipy_stats

    correlations = []
    for q in likert_cols:
        if q not in df.columns: continue
        valid = df[[q, 'EI']].dropna()
        if len(valid) < 30: continue
        corr, _ = scipy_stats.spearmanr(valid[q], valid['EI'])
        correlations.append({
            'Câu': q, 'Tên': codebook[q]['tên'], 'Trụ cột': codebook[q]['trụ_cột'],
            'Tương quan': round(corr, 3), 'Điểm TB': round(df[q].mean(), 2),
        })

    if not correlations:
        st.warning("Không đủ dữ liệu tương quan.")
        return

    df_corr = pd.DataFrame(correlations).sort_values('Tương quan', ascending=False)
    med_corr = df_corr['Tương quan'].median()
    med_score = df_corr['Điểm TB'].median()

    def _quadrant(row):
        if row['Tương quan'] >= med_corr and row['Điểm TB'] < med_score: return 'Ưu tiên cao'
        if row['Tương quan'] >= med_corr: return 'Duy trì'
        if row['Điểm TB'] < med_score: return 'Theo dõi'
        return 'Không ưu tiên'

    df_corr['Nhóm'] = df_corr.apply(_quadrant, axis=1)
    df_high_priority = df_corr[df_corr['Nhóm'] == 'Ưu tiên cao']
    
    ai_data = {
        "High_Priority_Items": df_high_priority.head(3)[['Câu', 'Tên', 'Trụ cột', 'Điểm TB', 'Tương quan']].to_dict(orient='records') if not df_high_priority.empty else "Không có yếu tố nào",
        "Total_High_Priority_Count": len(df_high_priority)
    }
    
    prompt = "Phân tích 3 yếu tố rơi vào nhóm Ưu tiên cao (High Priority). Giải thích nhanh tại sao đây là những hành động cấp bách (vì điểm trung bình thấp nhưng tương quan cực mạnh với EI) và đề xuất hướng giải quyết ngắn gọn."
    render_ai_insight_card("AI Action Priorities", ai_data, prompt, custom_style="margin-bottom: 24px;")

    color_map = {'Ưu tiên cao': COLORS['red'], 'Duy trì': COLORS['green'],
                 'Theo dõi': COLORS['gold'], 'Không ưu tiên': COLORS['grey']}

    c1, c2 = st.columns([2.5, 1])
    with c1:
        fig = px.scatter(df_corr, x='Điểm TB', y='Tương quan', color='Nhóm',
                         hover_data={'Câu': True, 'Tên': True, 'Trụ cột': True,
                                     'Điểm TB': ':.2f', 'Tương quan': ':.3f'},
                         text='Câu', size_max=15, color_discrete_map=color_map)
        fig = fig_card(fig, 'MA TRẬN TÁC ĐỘNG – NỖ LỰC', 'Tương quan Spearman vs Điểm trung bình (1-5)')
        fig.add_hline(y=med_corr, line_dash='dash', line_color='grey', opacity=0.4)
        fig.add_vline(x=med_score, line_dash='dash', line_color='grey', opacity=0.4)
        fig.update_traces(textposition='top center', textfont_size=10, marker=dict(size=12))
        fig.update_layout(height=550, xaxis_title='Điểm trung bình (1-5)',
                          yaxis_title='Tương quan Spearman với EI',
                          xaxis=dict(tickformat='.1f', showgrid=True), yaxis=dict(tickformat='.2f', showgrid=True))
        st.plotly_chart(fig, use_container_width=True)
    
    with c2:
        st.markdown("""
        <div style="background: white; padding: 20px; border-radius: 16px; border: 1px solid rgba(0,0,0,0.05); height: 100%; box-shadow: 0 4px 12px rgba(10,31,68,0.02);">
            <h4 style="color: #0A1F44; font-size: 1rem; margin-top: 0; font-weight: 700; border-bottom: 2px solid #E8EAF0; padding-bottom: 12px; margin-bottom: 16px;">Hướng dẫn đọc</h4>
            
            <div style="margin-bottom: 16px;">
                <div style="display: flex; align-items: center; gap: 8px; font-weight: 700; color: #C0392B; font-size: 0.95rem;">
                    <span style="width: 12px; height: 12px; border-radius: 50%; background: #C0392B; display: inline-block;"></span>
                    Ưu tiên cao
                </div>
                <div style="font-size: 0.85rem; color: #64748B; margin-left: 20px; margin-top: 4px;">Tác động lớn, nhưng điểm đang thấp. Cần dồn lực cải thiện ngay.</div>
            </div>
            
            <div style="margin-bottom: 16px;">
                <div style="display: flex; align-items: center; gap: 8px; font-weight: 700; color: #0D6E3A; font-size: 0.95rem;">
                    <span style="width: 12px; height: 12px; border-radius: 50%; background: #0D6E3A; display: inline-block;"></span>
                    Duy trì
                </div>
                <div style="font-size: 0.85rem; color: #64748B; margin-left: 20px; margin-top: 4px;">Thế mạnh của công ty. Tiếp tục phát huy.</div>
            </div>
            
            <div style="margin-bottom: 16px;">
                <div style="display: flex; align-items: center; gap: 8px; font-weight: 700; color: #FFA726; font-size: 0.95rem;">
                    <span style="width: 12px; height: 12px; border-radius: 50%; background: #FFA726; display: inline-block;"></span>
                    Theo dõi
                </div>
                <div style="font-size: 0.85rem; color: #64748B; margin-left: 20px; margin-top: 4px;">Điểm thấp nhưng tác động chưa lớn.</div>
            </div>
            
            <div>
                <div style="display: flex; align-items: center; gap: 8px; font-weight: 700; color: #78909C; font-size: 0.95rem;">
                    <span style="width: 12px; height: 12px; border-radius: 50%; background: #78909C; display: inline-block;"></span>
                    Không ưu tiên
                </div>
                <div style="font-size: 0.85rem; color: #64748B; margin-left: 20px; margin-top: 4px;">Điểm cao sẵn và ít tác động trực tiếp đến sự hài lòng chung.</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("#### Chi tiết")
    df_priorities = df_corr[['Nhóm', 'Câu', 'Tên', 'Trụ cột', 'Điểm TB', 'Tương quan']].sort_values(
        ['Nhóm', 'Tương quan'], ascending=[True, False])
        
    styled_priorities = df_priorities.style.background_gradient(
        cmap='RdYlGn', subset=['Điểm TB'], vmin=2.5, vmax=4.5
    ).background_gradient(
        cmap='Purples', subset=['Tương quan'], vmin=0.1, vmax=0.7
    ).format({'Điểm TB': '{:.2f}', 'Tương quan': '{:.3f}'})

    col_config = {
        'Nhóm': st.column_config.TextColumn('Nhóm phân loại', help="Phân nhóm ma trận ưu tiên", width="medium"),
        'Câu': st.column_config.TextColumn('Mã câu', width="small"),
        'Tên': st.column_config.TextColumn('Nội dung câu hỏi', width="large"),
        'Trụ cột': st.column_config.TextColumn('Trụ cột', width="medium"),
        'Điểm TB': st.column_config.NumberColumn('Điểm trung bình', format="%.2f", width="small"),
        'Tương quan': st.column_config.NumberColumn('Hệ số tương quan', format="%.3f", width="small"),
    }

    st.dataframe(styled_priorities, use_container_width=True, hide_index=True, column_config=col_config)

    import io
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
        df_priorities.to_excel(writer, index=False, sheet_name='Action_Priorities')
    
    st.download_button(
        label="📥 Tải báo cáo Ma trận Ưu tiên (Excel)",
        data=buffer.getvalue(),
        file_name=f"EES_Action_Priorities.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        key="export_priorities"
    )
