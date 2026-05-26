import streamlit as st
import plotly.express as px
import pandas as pd
from shared.plotly_theme import COLORS, apply_theme, fig_card
from utils.ai_generator import render_ai_insight_card

def render(df, cfg):
    apply_theme()
    codebook = cfg.get('codebook', {})
    likert_cols = [q for q, info in codebook.items() if info['loại'] == 'likert']

    from shared.plotly_theme import section_header

    # Non-DA user context banner
    st.markdown("""
    <div style="background:#EFF6FF;border:1px solid #BFDBFE;border-radius:12px;padding:14px 18px;margin-bottom:20px;display:flex;gap:12px;align-items:flex-start;">
        <div style="font-size:1.4rem;flex-shrink:0;">🗺️</div>
        <div>
            <div style="font-size:0.82rem;font-weight:700;color:#1D4ED8;margin-bottom:4px;">Ma trận Ưu tiên Hành động — Nên làm gì trước?</div>
            <div style="font-size:0.8rem;color:#475569;line-height:1.55;">
                Biểu đồ này giúp bạn <strong>xác định đúng trọng tâm</strong>: không phải mọi điểm thấp đều cần giải quyết ngay. Chỉ những yếu tố <strong style="color:#DC2626;">ảnh hưởng lớn đến gắn kết MÀ điểm hiện tại lại thấp</strong> mới là ưu tiên thực sự.
                Nhìn vào góc <span style="background:#FEF2F2;color:#DC2626;padding:1px 6px;border-radius:4px;font-weight:700;">đỏ trên-trái</span> trước tiên — đó là những nơi cần đầu tư nguồn lực ngay.
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

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
    
    prompt = "Bạn đang tư vấn cho một Giám đốc HR không chuyên về data analytics. Dựa trên danh sách các yếu tố 'Ưu tiên cao' (điểm thấp nhưng ảnh hưởng lớn đến sự gắn kết), hãy giải thích bằng ngôn ngữ thông thường: (1) Các yếu tố này thực tế nghĩa là gì — nhân viên đang gặp phải vấn đề gì trong ngày làm việc? (2) Nếu cải thiện những điểm này, điều gì sẽ thay đổi? (3) Bước đầu tiên cần làm ngay là gì — một hành động cụ thể có thể triển khai trong tháng tới?"
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
        import textwrap
        st.markdown(textwrap.dedent("""
        <div style="background: white; padding: 20px; border-radius: 16px; border: 1px solid rgba(0,0,0,0.05); height: 100%; box-shadow: 0 4px 12px rgba(10,31,68,0.02);">
            <h4 style="color: #0A1F44; font-size: 0.95rem; margin-top: 0; font-weight: 700; border-bottom: 2px solid #E8EAF0; padding-bottom: 10px; margin-bottom: 14px;">
                📋 Cách đọc biểu đồ này
            </h4>
            <p style="font-size: 0.78rem; color: #64748B; line-height: 1.55; margin-bottom: 14px; padding: 8px 10px; background: #F8FAFC; border-radius: 8px;">
                Mỗi chấm = một câu hỏi khảo sát.<br>
                <strong>Trục ngang (→)</strong>: điểm trung bình nhân viên cho câu đó (thấp = họ không hài lòng).<br>
                <strong>Trục dọc (↑)</strong>: câu đó ảnh hưởng nhiều/ít đến sự gắn kết tổng thể.
            </p>
            <div style="margin-bottom: 14px; padding: 10px 12px; background: #FEF2F2; border-radius: 10px; border-left: 3px solid #C0392B;">
                <div style="display: flex; align-items: center; gap: 8px; font-weight: 700; color: #C0392B; font-size: 0.85rem; margin-bottom: 4px;">
                    <span style="width: 10px; height: 10px; border-radius: 50%; background: #C0392B; display: inline-block; flex-shrink:0;"></span>
                    🔴 Ưu tiên cao — Hành động ngay
                </div>
                <div style="font-size: 0.78rem; color: #7F1D1D;">Điểm thấp <em>VÀ</em> ảnh hưởng lớn đến gắn kết. Đây là những điểm đau thực sự của nhân viên — nếu không cải thiện, rủi ro nghỉ việc tăng cao.</div>
            </div>
            <div style="margin-bottom: 14px; padding: 10px 12px; background: #F0FDF4; border-radius: 10px; border-left: 3px solid #0D6E3A;">
                <div style="display: flex; align-items: center; gap: 8px; font-weight: 700; color: #0D6E3A; font-size: 0.85rem; margin-bottom: 4px;">
                    <span style="width: 10px; height: 10px; border-radius: 50%; background: #0D6E3A; display: inline-block; flex-shrink:0;"></span>
                    🟢 Duy trì — Thế mạnh hiện tại
                </div>
                <div style="font-size: 0.78rem; color: #14532D;">Điểm cao <em>VÀ</em> ảnh hưởng lớn. Đây là lý do nhân viên chọn ở lại — cần bảo vệ và không để xuống cấp.</div>
            </div>
            <div style="margin-bottom: 14px; padding: 10px 12px; background: #FFFBEB; border-radius: 10px; border-left: 3px solid #FFA726;">
                <div style="display: flex; align-items: center; gap: 8px; font-weight: 700; color: #92400E; font-size: 0.85rem; margin-bottom: 4px;">
                    <span style="width: 10px; height: 10px; border-radius: 50%; background: #FFA726; display: inline-block; flex-shrink:0;"></span>
                    🟡 Theo dõi — Chưa cấp bách
                </div>
                <div style="font-size: 0.78rem; color: #78350F;">Điểm thấp nhưng ảnh hưởng chưa nhiều. Xếp sau khi đã giải quyết nhóm đỏ.</div>
            </div>
            <div style="padding: 10px 12px; background: #F8FAFC; border-radius: 10px; border-left: 3px solid #78909C;">
                <div style="display: flex; align-items: center; gap: 8px; font-weight: 700; color: #475569; font-size: 0.85rem; margin-bottom: 4px;">
                    <span style="width: 10px; height: 10px; border-radius: 50%; background: #78909C; display: inline-block; flex-shrink:0;"></span>
                    ⚪ Không ưu tiên — Ổn định
                </div>
                <div style="font-size: 0.78rem; color: #64748B;">Điểm đã cao và ít tác động trực tiếp. Không cần đầu tư thêm ở thời điểm này.</div>
            </div>
        </div>
        """), unsafe_allow_html=True)

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


