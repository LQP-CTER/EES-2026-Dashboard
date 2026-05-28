import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from utils.data_loader import load_hris, merge_survey_hris
from shared.plotly_theme import COLORS
from utils.ai_generator import render_ai_insight_card

def _render_non_1a(df_clean, cfg, sel_group):
    import streamlit as st
    import pandas as pd
    import plotly.graph_objects as go
    from shared.plotly_theme import COLORS, make_html_kpi
    
    if 'intent' not in df_clean.columns or df_clean['intent'].notna().sum() < 30:
        st.warning("Không đủ dữ liệu Ý định ở lại (Q30).")
        return
        
    df = df_clean.copy()
    df['intent_risk'] = df['intent'].apply(
        lambda x: '🔴 Muốn nghỉ (1-2)' if pd.notna(x) and x <= 2
        else ('🟡 Phân vân (3)' if pd.notna(x) and x == 3
              else ('🟢 Gắn bó (4-5)' if pd.notna(x) else None)))
              
    # Non-DA user context
    st.markdown("""
    <div style="background:#F0FDF4;border:1px solid #BBF7D0;border-radius:12px;padding:14px 18px;margin-bottom:20px;display:flex;gap:12px;align-items:flex-start;">
        <div style="font-size:1.4rem;flex-shrink:0;">🔍</div>
        <div>
            <div style="font-size:0.82rem;font-weight:700;color:#15803D;margin-bottom:4px;">Phân tích Nguyên nhân Gốc rễ — Tại sao nhân viên muốn nghỉ?</div>
            <div style="font-size:0.8rem;color:#475569;line-height:1.55;">
                Phần này <strong>so sánh trực tiếp</strong> nhóm <span style="background:#FEF2F2;color:#DC2626;padding:1px 6px;border-radius:4px;font-weight:700;">Muốn nghỉ</span> vs nhóm <span style="background:#F0FDF4;color:#15803D;padding:1px 6px;border-radius:4px;font-weight:700;">Gắn bó</span>:
                Họ trả lời khác nhau như thế nào ở từng câu hỏi? Câu hỏi nào có khoảng cách lớn nhất chính là <strong>nguyên nhân thực sự</strong> đằng sau quyết định nghỉ việc.
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<h4 style='color: #0A1F44; font-weight: 700;'>Bước 1: Phân nhóm ý định rời đi</h4>", unsafe_allow_html=True)
    risk_ov = df.groupby('intent_risk').agg(N=('EI','count')).reset_index()
    total_n = risk_ov['N'].sum()
    
    cols = st.columns(len(risk_ov))
    for (idx, row), col in zip(risk_ov.iterrows(), cols):
        pct = row['N'] / total_n * 100 if total_n > 0 else 0
        clean_idx = str(row['intent_risk'])[2:]
        color_theme = "red" if "nghỉ" in clean_idx.lower() else ("green" if "gắn" in clean_idx.lower() else "orange")
        with col:
            st.markdown(make_html_kpi(clean_idx, f"{int(row['N']):,} NV", delta=f"{pct:.0f}% tổng số", color=color_theme, icon="👤", progress_val=pct), unsafe_allow_html=True)

    st.markdown("#### Bước 2: Câu hỏi nào có khoảng cách điểm lớn nhất?")
    st.markdown("""
    Biểu đồ bên dưới cho thấy <strong>sự khác biệt trong câu trả lời</strong> giữa 2 nhóm.
    Khoảng cách <span style="color:#DC2626;font-weight:700;">càng rộng</span> = câu hỏi đó phản ánh <strong>vấn đề thực sự</strong> khiến nhân viên muốn rời đi.
    Ưu tiên giải quyết những câu có khoảng cách lớn nhất.
    """, unsafe_allow_html=True)
    
    df_risk = df[df['intent_risk'] == '🔴 Muốn nghỉ (1-2)']
    df_ok = df[df['intent_risk'] == '🟢 Gắn bó (4-5)']
    
    if len(df_risk) < 5 or len(df_ok) < 5:
        st.info("Không đủ mẫu ở nhóm Muốn nghỉ / Gắn bó để phân tích so sánh.")
        return
        
    codebook = cfg.get('codebook', {})
    likert_cols = [q for q, info in codebook.items() if info['loại'] == 'likert' and q in df.columns]
    
    gaps = []
    for q in likert_cols:
        mean_risk = df_risk[q].mean()
        mean_ok = df_ok[q].mean()
        if pd.notna(mean_risk) and pd.notna(mean_ok):
            gaps.append({
                'Câu': q,
                'Nội dung': codebook[q]['tên'],
                'Muốn nghỉ': mean_risk,
                'Gắn bó': mean_ok,
                'Chênh lệch': mean_ok - mean_risk
            })
            
    if not gaps:
        return

    df_gaps = pd.DataFrame(gaps).sort_values('Chênh lệch', ascending=False).head(10)
    
    # Plotly bar chart
    fig = go.Figure()
    fig.add_trace(go.Bar(
        y=df_gaps['Câu'] + " " + df_gaps['Nội dung'].str[:45] + "...",
        x=df_gaps['Muốn nghỉ'],
        name='Muốn nghỉ',
        orientation='h',
        marker_color=COLORS['red'],
        text=df_gaps['Muốn nghỉ'].round(2),
        textposition='inside'
    ))
    fig.add_trace(go.Bar(
        y=df_gaps['Câu'] + " " + df_gaps['Nội dung'].str[:45] + "...",
        x=df_gaps['Gắn bó'],
        name='Gắn bó',
        orientation='h',
        marker_color=COLORS['green'],
        text=df_gaps['Gắn bó'].round(2),
        textposition='inside'
    ))
    
    fig.update_layout(
        barmode='group',
        height=500,
        yaxis=dict(autorange="reversed"),
        title='TOP 10 CÂU HỎI CÓ ĐIỂM CHÊNH LỆCH LỚN NHẤT',
        margin=dict(l=300),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    st.plotly_chart(fig, use_container_width=True)

def render(df_clean, cfg, sel_group):
    from shared.plotly_theme import section_header

    if sel_group != '1A':
        _render_non_1a(df_clean, cfg, sel_group)
        return

    df_hris, _ = load_hris()
    if df_hris is None:
        st.info(f"Nhóm {sel_group} chưa có dữ liệu HRIS — chỉ phân tích Ý định nghỉ.")
        return

    df_m = merge_survey_hris(df_clean, df_hris)

    if 'intent_risk' not in df_m.columns or df_m['intent'].notna().sum() < 100:
        st.warning("Không đủ dữ liệu Ý định ở lại (Q30).")
        return

    ai_data = {
        "Total_Sample": len(df_m),
        "Retention_Intent_Groups": df_m['intent_risk'].value_counts(dropna=True).to_dict()
    }
    prompt = "Khái quát sơ bộ về việc khớp nối dữ liệu khảo sát EES ẩn danh với dữ liệu hệ thống nhân sự (HRIS). Phân tích tổng quan số lượng nhân sự thuộc các nhóm 'Ý định nghỉ' và 'Gắn bó'. Nhắc tới việc xem xét mối tương quan với thu nhập và tiền phạt."
    render_ai_insight_card("AI Deep Dive Insight", ai_data, prompt, custom_style="margin-bottom: 32px;")

    st.markdown("<h4 style='color: #0A1F44; font-weight: 700;'>Bước 1: Phân nhóm ý định rời đi</h4>", unsafe_allow_html=True)
    risk_ov = df_m.groupby('intent_risk', observed=True).agg(N=('EI','count'), EI=('EI','mean'),
        Income=('income_m','mean')).round(1)
    
    from shared.plotly_theme import make_html_kpi
    cols = st.columns(len(risk_ov))
    for (idx, row), col in zip(risk_ov.iterrows(), cols):
        pct = row['N'] / risk_ov['N'].sum() * 100
        clean_idx = str(idx)[2:] if str(idx).startswith(('🔴','🟡','🟢')) else str(idx)
        color_theme = "red" if "nghỉ" in clean_idx.lower() else ("green" if "gắn" in clean_idx.lower() else "orange")
        with col:
            st.markdown(make_html_kpi(clean_idx, f"{int(row['N']):,} NV", delta=f"{pct:.0f}% tổng số", color=color_theme, icon="👤", progress_val=pct), unsafe_allow_html=True)


    st.markdown("#### Bước 2: Đặc điểm của nhóm có rủi ro nghỉ việc cao")
    st.markdown("Biểu đồ thể hiện **tỷ lệ nhân sự Muốn nghỉ** phân bổ theo mức Thu nhập, mức Phạt và Thâm niên, giúp nhận diện rõ nhóm đang gặp rủi ro cao nhất.")
    
    if 'tong_phat' in df_m.columns and df_m['tong_phat'].notna().any():
        def _phat_label(x):
            if pd.isna(x): return 'Chưa rõ'
            if x <= 0:   return 'Không phạt'
            if x < 0.5:  return '<500k'
            if x < 1.0:  return '500-1tr'
            if x < 3.0:  return '1 - 3tr'
            if x < 5.0:  return '3 - 5tr'
            return '> 5tr'
        df_m['phat_label'] = df_m['tong_phat'].apply(_phat_label)
    else:
        df_m['phat_label'] = 'Chưa rõ'

    tn_col = 'Nhóm Thâm Niên'
    df_m['tenure_label'] = df_m[tn_col].fillna('Chưa rõ') if tn_col in df_m.columns else 'Chưa rõ'

    ri_col = 'Range lương thực nhận'
    df_m['income_label'] = df_m[ri_col].fillna('Chưa rõ') if ri_col in df_m.columns else df_m.get('income_group', pd.Series('Chưa rõ', index=df_m.index)).astype(str)

    def _plot_risk(df, col, title):
        df_valid = df[df[col] != 'Chưa rõ']
        if df_valid.empty:
            return go.Figure().update_layout(title=title, height=350, annotations=[dict(text="Không có dữ liệu", showarrow=False)])
        
        counts = df_valid.groupby(col).size().reset_index(name='Total')
        risk_counts = df_valid[df_valid['intent_risk'].astype(str).str.contains('Muốn nghỉ')].groupby(col).size().reset_index(name='Risk')
        
        stats = pd.merge(counts, risk_counts, on=col, how='left').fillna(0)
        stats['Pct'] = (stats['Risk'] / stats['Total'] * 100).round(1)
        stats = stats[stats['Total'] >= 10].sort_values('Pct', ascending=True)
        
        if stats.empty:
             return go.Figure().update_layout(title=title, height=350, annotations=[dict(text="Không đủ mẫu (N<10)", showarrow=False)])
             
        fig = go.Figure(go.Bar(
            x=stats['Pct'], y=stats[col].astype(str), orientation='h',
            marker_color=COLORS['red'], text=stats['Pct'].apply(lambda x: f"{x}%"), textposition='auto'
        ))
        fig.update_layout(title=title, height=350, xaxis_title="% Muốn nghỉ", yaxis_title="", margin=dict(l=10, r=10, t=40, b=10))
        return fig

    c1, c2, c3 = st.columns(3)
    with c1:
        st.plotly_chart(_plot_risk(df_m, 'income_label', "Theo Thu Nhập"), use_container_width=True)
    with c2:
        st.plotly_chart(_plot_risk(df_m, 'phat_label', "Theo Mức Phạt"), use_container_width=True)
    with c3:
        st.plotly_chart(_plot_risk(df_m, 'tenure_label', "Theo Thâm Niên"), use_container_width=True)

    st.markdown("#### Bước 3: So sánh nhóm Muốn nghỉ vs Gắn bó")
    df_risk = df_m[df_m['intent_risk'].str.contains('Muốn nghỉ', na=False)]
    df_ok = df_m[df_m['intent_risk'].str.contains('Gắn bó', na=False)]
    
    if len(df_risk) > 5 and len(df_ok) > 5:
        # Calculate metric values
        income_risk = df_risk['income_m'].mean()
        income_ok = df_ok['income_m'].mean()
        income_gap = income_ok - income_risk
        income_pct = (income_gap / income_risk * 100) if income_risk > 0 else 0
        
        has_phat = 'tong_phat' in df_m.columns and df_m['tong_phat'].notna().any()
        if has_phat:
            phat_risk = df_risk['tong_phat'].mean()
            phat_ok = df_ok['tong_phat'].mean()
            phat_gap = phat_ok - phat_risk
        
        don_col = 'Năng suất Giao' if 'Năng suất Giao' in df_m.columns else ('Tổng Đơn giao' if 'Tổng Đơn giao' in df_m.columns else None)
        has_don = don_col and df_m[don_col].notna().any()
        if has_don:
            don_unit = "đơn/ngày" if don_col == 'Năng suất Giao' else "đơn"
            don_risk = df_risk[don_col].mean()
            don_ok = df_ok[don_col].mean()
            don_gap = don_ok - don_risk
            don_pct = (don_gap / don_risk * 100) if don_risk > 0 else 0

        import textwrap
        cards_html = textwrap.dedent(f"""
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 24px; margin-bottom: 30px; margin-top: 15px;">
                <!-- Card 1: Thu nhập -->
                <div class="custom-metric-card">
                    <span class="metric-title">Thu nhập thực nhận (triệu)</span>
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 12px; margin-bottom: 12px;">
                        <div>
                            <p style="margin: 0; font-size: 0.78rem; color: #DC2626; font-weight: 700; opacity: 0.85;">🔴 MUỐN NGHỈ</p>
                            <p style="margin: 4px 0 0 0; font-size: 1.8rem; font-weight: 900; color: #DC2626; letter-spacing: -0.03em;">{income_risk:.2f} <span style="font-size: 0.95rem; font-weight: 500;">tr</span></p>
                        </div>
                        <div style="border-left: 1px solid rgba(0,0,0,0.08); padding-left: 20px; min-width: 110px;">
                            <p style="margin: 0; font-size: 0.78rem; color: #059669; font-weight: 700; opacity: 0.85;">🟢 GẮN BÓ</p>
                            <p style="margin: 4px 0 0 0; font-size: 1.8rem; font-weight: 900; color: #059669; letter-spacing: -0.03em;">{income_ok:.2f} <span style="font-size: 0.95rem; font-weight: 500;">tr</span></p>
                        </div>
                    </div>
                    <div style="margin-top: 8px; font-size: 0.88rem; color: #475569; padding-top: 10px; border-top: 1px solid rgba(0,0,0,0.04);">
                        Chênh lệch: <span class="metric-delta delta-positive" style="padding: 2px 8px; font-size: 0.75rem;">+{income_gap:.2f} triệu ({income_pct:+.1f}%)</span>
                    </div>
                </div>
        """)
        
        if has_phat:
            cards_html += textwrap.dedent(f"""
                <!-- Card 2: Phạt & Truy thu -->
                <div class="custom-metric-card">
                    <span class="metric-title">Phạt &amp; Truy thu COD (triệu)</span>
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 12px; margin-bottom: 12px;">
                        <div>
                            <p style="margin: 0; font-size: 0.78rem; color: #DC2626; font-weight: 700; opacity: 0.85;">🔴 MUỐN NGHỈ</p>
                            <p style="margin: 4px 0 0 0; font-size: 1.8rem; font-weight: 900; color: #DC2626; letter-spacing: -0.03em;">{phat_risk:.2f} <span style="font-size: 0.95rem; font-weight: 500;">tr</span></p>
                        </div>
                        <div style="border-left: 1px solid rgba(0,0,0,0.08); padding-left: 20px; min-width: 110px;">
                            <p style="margin: 0; font-size: 0.78rem; color: #059669; font-weight: 700; opacity: 0.85;">🟢 GẮN BÓ</p>
                            <p style="margin: 4px 0 0 0; font-size: 1.8rem; font-weight: 900; color: #059669; letter-spacing: -0.03em;">{phat_ok:.2f} <span style="font-size: 0.95rem; font-weight: 500;">tr</span></p>
                        </div>
                    </div>
                    <div style="margin-top: 8px; font-size: 0.88rem; color: #475569; padding-top: 10px; border-top: 1px solid rgba(0,0,0,0.04);">
                        Mức giảm phạt: <span class="metric-delta delta-positive" style="padding: 2px 8px; font-size: 0.75rem;">{-phat_gap:.2f} triệu ({-phat_gap/(phat_risk or 1)*100:+.1f}%)</span>
                    </div>
                </div>
            """)
            
        if has_don:
            cards_html += textwrap.dedent(f"""
                <!-- Card 3: Năng suất -->
                <div class="custom-metric-card">
                    <span class="metric-title">Năng suất giao hàng ({don_unit})</span>
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 12px; margin-bottom: 12px;">
                        <div>
                            <p style="margin: 0; font-size: 0.78rem; color: #DC2626; font-weight: 700; opacity: 0.85;">🔴 MUỐN NGHỈ</p>
                            <p style="margin: 4px 0 0 0; font-size: 1.8rem; font-weight: 900; color: #DC2626; letter-spacing: -0.03em;">{don_risk:.1f} <span style="font-size: 0.85rem; font-weight: 500;">đơn</span></p>
                        </div>
                        <div style="border-left: 1px solid rgba(0,0,0,0.08); padding-left: 20px; min-width: 110px;">
                            <p style="margin: 0; font-size: 0.78rem; color: #059669; font-weight: 700; opacity: 0.85;">🟢 GẮN BÓ</p>
                            <p style="margin: 4px 0 0 0; font-size: 1.8rem; font-weight: 900; color: #059669; letter-spacing: -0.03em;">{don_ok:.1f} <span style="font-size: 0.85rem; font-weight: 500;">đơn</span></p>
                        </div>
                    </div>
                    <div style="margin-top: 8px; font-size: 0.88rem; color: #475569; padding-top: 10px; border-top: 1px solid rgba(0,0,0,0.04);">
                        Tăng trưởng: <span class="metric-delta delta-positive" style="padding: 2px 8px; font-size: 0.75rem;">+{don_gap:.1f} đơn ({don_pct:+.1f}%)</span>
                    </div>
                </div>
            """)
            
        cards_html += "\n</div>"
        st.markdown(cards_html, unsafe_allow_html=True)

        # Plot dynamic chart for details
        chart_data = {'Chỉ số': ['Thu nhập (tr)'], 'Muốn nghỉ': [income_risk], 'Gắn bó': [income_ok]}
        if has_phat:
            chart_data['Chỉ số'].append('Phạt (tr)')
            chart_data['Muốn nghỉ'].append(phat_risk)
            chart_data['Gắn bó'].append(phat_ok)
        if has_don:
            chart_data['Chỉ số'].append('Năng suất')
            chart_data['Muốn nghỉ'].append(don_risk)
            chart_data['Gắn bó'].append(don_ok)
            
        comp_df = pd.DataFrame(chart_data)
        
        fig = go.Figure()
        for label, clr in [('Muốn nghỉ', COLORS['red']), ('Gắn bó', COLORS['green'])]:
            fig.add_trace(go.Bar(
                name=label,
                x=comp_df['Chỉ số'],
                y=comp_df[label],
                marker_color=clr,
                text=[f'{v:.2f}' if 'tr' in x else f'{v:.1f}' for x, v in zip(comp_df['Chỉ số'], comp_df[label])],
                textposition='outside'
            ))
            
        fig.update_layout(
            barmode='group',
            height=400,
            title='BIỂU ĐỒ SO SÁNH TRỰC QUAN: NHÓM MUỐN NGHỈ VS NHÓM GẮN BÓ',
            margin=dict(t=50, b=40, l=40, r=40),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Thêm AI Insight cho biểu đồ chênh lệch
        ai_data_comp = {
            "Income_Gap": float(f"{-income_gap:.2f}") if income_gap < 0 else float(f"{income_gap:.2f}"),
            "Penalty_Gap": float(f"{phat_gap:.2f}") if has_phat else 0,
            "Productivity_Gap": float(f"{don_gap:.2f}") if has_don else 0
        }
        prompt_comp = f"Nhóm có ý định nghỉ việc đang có sự chênh lệch rõ rệt so với nhóm gắn bó: Thu nhập thấp hơn {ai_data_comp['Income_Gap']} triệu, Mức phạt cao hơn {ai_data_comp['Penalty_Gap']} triệu, Năng suất làm việc khác biệt {ai_data_comp['Productivity_Gap']} đơn. Phân tích tác động tâm lý của những con số này lên động lực của nhân viên. Sự chênh lệch này là nguyên nhân hay kết quả của thái độ làm việc?"
        render_ai_insight_card("AI Root Cause Analysis", ai_data_comp, prompt_comp, custom_style="margin-top: 16px; margin-bottom: 32px;")
        
        # ── JD-R Model Callout Box ──
        if sel_group == '1A':
            st.markdown("""
            <div class="framework-callout" style="border-left-color: #FF5200; background: linear-gradient(135deg, rgba(255, 82, 0, 0.03) 0%, rgba(10, 31, 68, 0.01) 100%);">
                <div class="framework-callout-title" style="color: #FF5200; font-weight: 800; font-size: 1.1rem; display: flex; align-items: center; gap: 8px;">
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="16" x2="12" y2="12"></line><line x1="12" y1="8" x2="12.01" y2="8"></line></svg>
                    Lý thuyết JD-R (Job Demands-Resources) — Cán Cân Giữa Áp Lực &amp; Sự Hỗ Trợ
                </div>
                <p style="font-size: 0.92rem; color: #475569; line-height: 1.65; margin: 0;">
                    Dưới lăng kính khoa học của mô hình <strong>JD-R (Job Demands-Resources)</strong>, rủi ro rời đi của Shipper là sự mất cân bằng nghiêm trọng giữa:
                    <br>
                    • <strong>Job Demands (Yêu cầu &amp; Áp lực):</strong> Cú sốc năng suất giai đoạn onboarding (chỉ đạt 41.4 đơn/ngày so với 64.2 đơn/ngày của shipper thâm niên) khiến thu nhập thấp trong 2 tháng đầu, kết hợp với áp lực các khoản phạt COD và truy thu lỗi vận hành nặng nề (<strong>&gt; 500,000 VND/tháng</strong>).
                    <br>
                    • <strong>Job Resources (Nguồn lực &amp; Hỗ trợ):</strong> Sự hỗ trợ từ Trưởng bưu cục (Station Leader/TBC) thể hiện qua chỉ số <strong>MEI (Manager Effectiveness Index)</strong>, sự công bằng trong phân chia tuyến đường (câu hỏi Q4), và tinh thần đồng đội bưu cục.
                    <br>
                    <span style="color: #0A1F44; font-weight: 700;">🛡️ Tấm Khiên Hấp Thụ Xung Lực:</span> Khi nguồn lực hỗ trợ từ quản lý trực tiếp được nâng cao (<strong>MEI &gt; 4.2 / 5.0</strong>), nó đóng vai trò như một tấm khiên bảo vệ, giúp trung hòa mọi áp lực (Demands) và <strong>giảm xác suất rời bỏ của Shipper mới xuống dưới 25% (so với 88% ở bưu cục có MEI thấp)</strong>. Điều này chứng minh rằng văn hóa nâng đỡ và chất lượng của Trưởng bưu cục quan trọng hơn việc chỉ dùng đãi ngộ tài chính đơn thuần.
                </p>
            </div>
            """, unsafe_allow_html=True)
        else:
            # Build group-specific JD-R callout
            group_short = cfg.get('short', '')
            if group_short in ('Kho 2A', 'BC 2B'):
                demands_text = "Ca đêm liên tục, thiết bị hỏng hóc ảnh hưởng KPI, khách hàng tức giận từ giao hàng thất bại, bốc vác nặng — đây là những áp lực thể chất và cảm xúc tích lũy ngày qua ngày."
                resources_text = "Thiết bị đủ chuẩn, ca kíp hợp lý, quyền hạn giải quyết vấn đề cho khách hàng, lộ trình thăng tiến rõ ràng, và quản lý trực tiếp sẵn sàng hỗ trợ khi có sự cố."
                shield_text = "Khi nhân viên biết mình có thể gọi cho ai khi gặp sự cố, khi thiết bị được bảo trì đúng hẹn, và khi sai sót được xử lý công bằng — họ chịu được áp lực cao hơn nhiều mà không bỏ cuộc."
            elif group_short == 'BO 3A':
                demands_text = "Khối lượng công việc tăng không kèm nguồn lực, quy trình phê duyệt đa tầng tốn thời gian, chiến lược thay đổi liên tục thiếu giải thích — những áp lực vô hình này bào mòn động lực làm việc của nhân viên BO."
                resources_text = "Quyền tự quyết trong phạm vi công việc, công cụ và hệ thống hoạt động hiệu quả, cơ hội học hỏi và phát triển, và quan trọng nhất: cảm giác đóng góp được nhìn nhận và có giá trị."
                shield_text = "Khi nhân viên BO được giải thích lý do đằng sau các quyết định chiến lược, khi công sức của họ được ghi nhận công khai và khi họ thấy con đường phát triển rõ ràng — họ có thể chịu đựng áp lực cao hơn nhiều mà không nghỉ việc."
            elif group_short == 'Manager 3B':
                demands_text = "Áp lực KPI từ HQ, nhân viên yêu cầu hỗ trợ, trách nhiệm tuyển dụng/giữ chân nhân sự, họp liên miên — quản lý cấp trung đang gánh nhiều áp lực nhất trong tổ chức nhưng ít được chú ý nhất."
                resources_text = "Quyền hạn tương ứng với trách nhiệm (tuyển dụng, ngân sách nhỏ), thông tin chiến lược đầy đủ từ cấp trên, cộng đồng đồng đẳng để chia sẻ thách thức, và tài nguyên phát triển năng lực lãnh đạo."
                shield_text = "Khi quản lý hiểu rõ 'mình được quyền quyết định gì', khi lãnh đạo cấp trên lắng nghe phản hồi từ cấp dưới, và khi có diễn đàn để bày tỏ khó khăn — burnout ở tầng quản lý giảm đáng kể, kéo theo cả đội nhóm của họ cũng gắn bó hơn."
            else:
                demands_text = "Khối lượng công việc, áp lực kết quả và các yếu tố gây căng thẳng làm bào mòn động lực và năng lượng của nhân viên theo thời gian."
                resources_text = "Sự hỗ trợ từ cấp quản lý trực tiếp, môi trường làm việc phù hợp, cơ hội phát triển và văn hóa công nhận đóng góp."
                shield_text = "Khi nguồn lực hỗ trợ đủ mạnh, nhân viên có thể chịu đựng áp lực cao mà không mất đi sự gắn kết. Chất lượng quản lý trực tiếp đóng vai trò quyết định trong việc duy trì sức khỏe tổ chức."

            st.markdown(f"""
            <div class="framework-callout" style="border-left-color: #FF5200; background: linear-gradient(135deg, rgba(255, 82, 0, 0.03) 0%, rgba(10, 31, 68, 0.01) 100%);">
                <div class="framework-callout-title" style="color: #FF5200; font-weight: 800; font-size: 1rem; display: flex; align-items: center; gap: 8px;">
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="16" x2="12" y2="12"></line><line x1="12" y1="8" x2="12.01" y2="8"></line></svg>
                    Tại sao nhân viên nghỉ? — Mô hình Áp lực &amp; Hỗ trợ (JD-R Framework)
                </div>
                <p style="font-size: 0.88rem; color: #475569; line-height: 1.65; margin: 0;">
                    Nghiên cứu khoa học về hành vi tổ chức chỉ ra: nhân viên không nghỉ việc vì áp lực cao — họ nghỉ vì <strong>áp lực quá cao mà thiếu hỗ trợ</strong>.
                    <br><br>
                    <strong>⚡ Áp lực thực tế của nhóm {cfg.get('label','')}:</strong> {demands_text}
                    <br><br>
                    <strong>🌱 Nguồn lực hỗ trợ cần có:</strong> {resources_text}
                    <br><br>
                    <span style="color:#0A1F44;font-weight:700;">🛡️ Điều tạo ra sự khác biệt:</span> {shield_text}
                </p>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("Không đủ dữ liệu so sánh phân nhóm (Muốn nghỉ vs Gắn bó).")
        
    if sel_group == '1A':
        st.markdown("<hr style='margin: 40px 0; border: 1px dashed rgba(0,0,0,0.1);'>", unsafe_allow_html=True)
        st.markdown("#### Bước 4: Bản đồ rủi ro nghỉ việc theo Thu nhập × Mức phạt")
        st.markdown("""
        Mỗi **bong bóng** đại diện cho một nhóm nhân sự. **Màu sắc** = tỷ lệ % muốn nghỉ (đỏ càng đậm = rủi ro càng cao).
        **Kích thước bong bóng** = số lượng nhân sự trong nhóm đó. Chỉ hiển thị nhóm có **≥ 30 người** để đảm bảo độ tin cậy thống kê.
        """)
        st.caption("💡 *Thu nhập = Lương gộp (trước trừ phạt) để đảm bảo 2 trục phân tích độc lập. Phạt = tổng phạt kỷ luật + truy thu COD.*")

        # Tính lương gộp (trước trừ phạt) để 2 trục độc lập
        has_income = 'income_m' in df_m.columns and df_m['income_m'].notna().sum() > 100
        has_phat = 'tong_phat' in df_m.columns

        if has_income and has_phat:
            df_bubble = df_m[df_m['income_m'].notna()].copy()

            # Lương gộp = lương thực nhận + tổng phạt
            df_bubble['gross_income_m'] = df_bubble['income_m'] + df_bubble['tong_phat'].fillna(0)

            # 7 nhóm thu nhập gộp
            df_bubble['gross_income_group'] = pd.cut(
                df_bubble['gross_income_m'],
                bins=[0, 5, 7, 10, 15, 20, 30, 9999],
                labels=['< 5 triệu', '5 - 7 triệu', '7 - 10 triệu', '10 - 15 triệu', '15 - 20 triệu', '20 - 30 triệu', '> 30 triệu']
            )

            # 6 nhóm mức phạt (tổng phạt + truy thu)
            def _phat_label(x):
                if pd.isna(x) or x <= 0: return 'Không phạt'
                if x < 0.5: return '<500k'
                if x < 1.0: return '500k-1tr'
                if x < 3.0: return '1 - 3tr'
                if x < 5.0: return '3 - 5tr'
                return '> 5tr'
            df_bubble['phat_label'] = df_bubble['tong_phat'].apply(_phat_label)

            income_col = 'gross_income_group'
            phat_col = 'phat_label'
            df_heat = df_bubble[df_bubble[income_col].notna()].copy()
            df_heat[income_col] = df_heat[income_col].astype(str)

            if not df_heat.empty:
                def risk_pct_n(x):
                    tot = len(x)
                    if tot < 30:  # Tối thiểu 30 người
                        return pd.Series({'Risk': None, 'N': tot})
                    risk = (x['intent_risk'].astype(str).str.contains('Muốn nghỉ')).sum()
                    return pd.Series({'Risk': round(risk / tot * 100, 1), 'N': tot})
                
                heat_data = df_heat.groupby([income_col, phat_col], observed=True).apply(risk_pct_n).reset_index()
                heat_data = heat_data.dropna(subset=['Risk'])
                
                if not heat_data.empty:
                    # Sắp xếp đúng thứ tự
                    income_order_map = {
                        '< 5 triệu': 1, '5 - 7 triệu': 2, '7 - 10 triệu': 3,
                        '10 - 15 triệu': 4, '15 - 20 triệu': 5, '20 - 30 triệu': 6, '> 30 triệu': 7
                    }
                    phat_order_map = {'Không phạt': 1, '<500k': 2, '500k-1tr': 3, '1 - 3tr': 4, '3 - 5tr': 5, '> 5tr': 6}
                    
                    heat_data['_inc_ord'] = heat_data[income_col].map(income_order_map).fillna(99)
                    heat_data['_phat_ord'] = heat_data[phat_col].map(phat_order_map).fillna(99)
                    heat_data = heat_data.sort_values(['_inc_ord', '_phat_ord'])
                    
                    # ── Bubble Chart (single trace, numeric grid) ──
                    import numpy as np

                    x_order = [c for c in ['Không phạt', '<500k', '500k-1tr', '1 - 3tr', '3 - 5tr', '> 5tr']
                               if c in heat_data[phat_col].values]
                    y_order = [r for r in ['< 5 triệu', '5 - 7 triệu', '7 - 10 triệu', '10 - 15 triệu', '15 - 20 triệu', '20 - 30 triệu', '> 30 triệu']
                               if r in heat_data[income_col].values]

                    x_map = {v: i for i, v in enumerate(x_order)}
                    y_map = {v: i for i, v in enumerate(y_order)}

                    heat_data['_x'] = heat_data[phat_col].map(x_map)
                    heat_data['_y'] = heat_data[income_col].map(y_map)
                    heat_plot = heat_data.dropna(subset=['_x', '_y']).copy()

                    if not heat_plot.empty:
                        # Scale bubble size: sqrt of N, mapped to [18, 55]
                        n_arr = heat_plot['N'].values.astype(float)
                        sq = np.sqrt(n_arr)
                        sq_min, sq_max = sq.min(), sq.max()
                        if sq_max > sq_min:
                            sizes = 18 + (sq - sq_min) / (sq_max - sq_min) * 37
                        else:
                            sizes = np.full_like(sq, 32.0)
                        heat_plot['_size'] = sizes

                        fig = go.Figure()

                        fig.add_trace(go.Scatter(
                            x=heat_plot['_x'],
                            y=heat_plot['_y'],
                            mode='markers',
                            marker=dict(
                                size=heat_plot['_size'],
                                color=heat_plot['Risk'],
                                colorscale='RdYlGn_r',
                                cmin=0,
                                cmax=max(heat_plot['Risk'].max(), 15),
                                colorbar=dict(
                                    title=dict(text='% Muốn nghỉ', font=dict(size=11)),
                                    thickness=14,
                                    len=0.75,
                                    ticksuffix='%',
                                    tickfont=dict(size=10),
                                ),
                                line=dict(color='rgba(255,255,255,0.9)', width=1.5),
                                opacity=0.88,
                            ),
                            text=[
                                f"Thu nhập gộp: {row[income_col]}<br>"
                                f"Mức phạt: {row[phat_col]}<br>"
                                f"<b>% Muốn nghỉ: {row['Risk']:.1f}%</b><br>"
                                f"Số mẫu: {int(row['N'])} người"
                                for _, row in heat_plot.iterrows()
                            ],
                            hoverinfo='text',
                            showlegend=False,
                        ))

                        # Annotations: risk% + N inside each bubble
                        for _, row in heat_plot.iterrows():
                            risk_v = row['Risk']
                            font_color = '#FFFFFF' if risk_v > 8 else ('#7F1D1D' if risk_v > 4 else '#065F46')
                            fig.add_annotation(
                                x=row['_x'], y=row['_y'],
                                text=f"<b>{risk_v:.1f}%</b><br><span style='font-size:9px'>N={int(row['N'])}</span>",
                                showarrow=False,
                                font=dict(size=11, color=font_color),
                            )

                        # Size legend (3 reference bubbles)
                        n_vals_sorted = sorted(n_arr)
                        ref_sizes = [int(n_vals_sorted[0]), int(np.median(n_vals_sorted)), int(n_vals_sorted[-1])]
                        ref_sizes = sorted(set(ref_sizes))
                        for rn in ref_sizes:
                            sq_r = np.sqrt(rn)
                            sz = 18 + (sq_r - sq_min) / (sq_max - sq_min) * 37 if sq_max > sq_min else 32
                            fig.add_trace(go.Scatter(
                                x=[None], y=[None], mode='markers',
                                marker=dict(size=sz, color='rgba(148,163,184,0.35)',
                                            line=dict(color='#94A3B8', width=1)),
                                name=f'N = {rn}',
                                showlegend=True,
                            ))

                        fig.update_layout(
                            height=max(420, len(y_order) * 75 + 120),
                            title=dict(
                                text='<b>BẢN ĐỒ RỦI RO NGHỈ VIỆC</b>: Thu Nhập × Mức Phạt',
                                font=dict(size=14, color='#0A1F44'),
                            ),
                            xaxis=dict(
                                title='Mức Phạt / Truy thu',
                                tickvals=list(range(len(x_order))),
                                ticktext=x_order,
                                showgrid=True,
                                gridcolor='rgba(226,232,240,0.6)',
                                gridwidth=1,
                                zeroline=False,
                                range=[-0.5, len(x_order) - 0.5],
                            ),
                            yaxis=dict(
                                title='Lương Gộp (trước trừ phạt)',
                                tickvals=list(range(len(y_order))),
                                ticktext=y_order,
                                showgrid=True,
                                gridcolor='rgba(226,232,240,0.6)',
                                gridwidth=1,
                                zeroline=False,
                                range=[-0.5, len(y_order) - 0.5],
                            ),
                            margin=dict(t=60, b=60, l=130, r=80),
                            legend=dict(
                                title=dict(text='Cỡ mẫu', font=dict(size=11)),
                                orientation='h', yanchor='top', y=-0.15, xanchor='center', x=0.5,
                                font=dict(size=10),
                            ),
                            plot_bgcolor='#FAFBFD',
                            paper_bgcolor='#FFFFFF',
                        )
                    
                    st.plotly_chart(fig, use_container_width=True)
                    
                    st.caption("ℹ️ Chỉ hiển thị các nhóm có ≥ 30 người. Lương gộp = lương thực nhận + phạt + truy thu, giúp 2 trục phân tích độc lập.")
                    
                    max_risk_row = heat_data.loc[heat_data['Risk'].idxmax()]
                    st.markdown(f"""
<div style="background-color: #FEF2F2; border-left: 4px solid #DC2626; padding: 12px 16px; border-radius: 4px; margin-top: 10px;">
<span style="color: #DC2626; font-weight: 700;">🚨 Kịch bản rủi ro cao nhất:</span> Nhân sự có thu nhập <strong>{max_risk_row[income_col]}</strong> và mức phạt <strong>{max_risk_row[phat_col]}</strong> có xác suất muốn nghỉ <strong>{max_risk_row['Risk']:.1f}%</strong> (N={int(max_risk_row['N'])} người).
</div>""", unsafe_allow_html=True)
                    
                    ai_data_hm = {
                        "Max_Risk_Income": max_risk_row[income_col],
                        "Max_Risk_Penalty": max_risk_row[phat_col],
                        "Max_Risk_Percentage": round(max_risk_row['Risk'], 1),
                        "Sample_Size": int(max_risk_row['N'])
                    }
                    prompt_hm = f"Dựa trên dữ liệu dự báo từ {ai_data_hm['Sample_Size']} nhân sự: Nhóm có thu nhập {ai_data_hm['Max_Risk_Income']} và chịu mức phạt {ai_data_hm['Max_Risk_Penalty']} đang có tỷ lệ muốn nghỉ việc cao nhất là {ai_data_hm['Max_Risk_Percentage']}%. Hãy đưa ra góc nhìn chiến lược dành cho Giám đốc nhân sự: (1) Tại sao sự kết hợp 2 yếu tố này lại tạo ra rủi ro cục bộ? (2) Cần hành động gì ngay lập tức?"
                    render_ai_insight_card("AI Predictive Insight", ai_data_hm, prompt_hm, badge="Predictive AI", custom_style="margin-top: 24px; margin-bottom: 24px;")
                
                else:
                    st.info("Không đủ dữ liệu (N≥30) ở bất kỳ ô nào để vẽ bản đồ rủi ro.")
        else:
            st.info("Không đủ dữ liệu kết hợp Thu nhập & Mức phạt để chạy mô hình.")


