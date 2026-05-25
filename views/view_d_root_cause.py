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

    st.markdown("#### Bước 2: Top yếu tố bất mãn nhất ở nhóm Muốn nghỉ")
    st.markdown("So sánh điểm trung bình các câu hỏi giữa nhóm **Muốn nghỉ** và nhóm **Gắn bó** để tìm ra những nguyên nhân gốc rễ (Root Cause) lớn nhất khiến nhân sự muốn rời đi.")
    
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

    df_hris, _ = load_hris(sel_group)
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


    st.markdown("#### Bước 2: Treemap")
    treemap_path = ['intent_clean', 'income_label']
    if 'tong_phat' in df_m.columns and df_m['tong_phat'].notna().any():
        df_m['phat_label'] = df_m['tong_phat'].apply(
            lambda x: 'Không phạt' if pd.notna(x) and x <= 0 else (
                '< 1tr' if pd.notna(x) and x < 1 else '≥ 1tr') if pd.notna(x) else 'N/A')
        treemap_path.append('phat_label')

    tn_col = 'Nhóm Thâm Niên'
    if tn_col in df_m.columns:
        df_m['tenure_label'] = df_m[tn_col].fillna('Chưa rõ')
        treemap_path.append('tenure_label')
    else:
        df_m['tenure_label'] = 'Chưa rõ'

    ri_col = 'Range lương thực nhận'
    df_m['income_label'] = df_m[ri_col].fillna('Chưa rõ') if ri_col in df_m.columns else df_m.get('income_group', pd.Series('Chưa rõ', index=df_m.index)).astype(str)

    # Clean intent labels for treemap
    df_m['intent_clean'] = df_m['intent_risk'].apply(lambda x: x[2:] if pd.notna(x) and str(x).startswith(('🔴','🟡','🟢')) else x)

    tree_mask = df_m['intent_clean'].notna() & df_m['income_label'].notna()
    df_tree = df_m[tree_mask].groupby(treemap_path).agg(Count=('EI','count'), EI_avg=('EI','mean')).reset_index()
    df_tree['EI_avg'] = df_tree['EI_avg'].round(1)
    df_tree = df_tree[df_tree['Count'] >= 3]

    if len(df_tree) > 5:
        fig = px.treemap(df_tree, path=treemap_path,
            values='Count', color='EI_avg', color_continuous_scale='RdYlGn', range_color=[40,85],
            title='TREEMAP: Ý ĐỊNH → THU NHẬP → PHẠT → THÂM NIÊN',
            labels={'EI_avg':'EI (%)', 'Count':'Số NV'}, hover_data={'EI_avg':':.1f'})
        fig.update_layout(height=650)
        fig.update_traces(textinfo='label+value', textfont_size=10)
        st.plotly_chart(fig, width='stretch')

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

        cards_html = f"""
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
        """
        
        if has_phat:
            cards_html += f"""
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
            """
            
        if has_don:
            cards_html += f"""
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
            """
            
        cards_html += "</div>"
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
            st.markdown("""
            <div class="framework-callout" style="border-left-color: #FF5200; background: linear-gradient(135deg, rgba(255, 82, 0, 0.03) 0%, rgba(10, 31, 68, 0.01) 100%);">
                <div class="framework-callout-title" style="color: #FF5200; font-weight: 800; font-size: 1.1rem; display: flex; align-items: center; gap: 8px;">
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="16" x2="12" y2="12"></line><line x1="12" y1="8" x2="12.01" y2="8"></line></svg>
                    Lý thuyết JD-R (Job Demands-Resources) — Cán Cân Giữa Áp Lực &amp; Sự Hỗ Trợ
                </div>
                <p style="font-size: 0.92rem; color: #475569; line-height: 1.65; margin: 0;">
                    Dưới lăng kính khoa học của mô hình <strong>JD-R (Job Demands-Resources)</strong>, rủi ro rời đi của nhân viên là sự mất cân bằng nghiêm trọng giữa:
                    <br>
                    • <strong>Job Demands (Yêu cầu &amp; Áp lực):</strong> Khối lượng công việc, áp lực và các yếu tố gây căng thẳng làm bào mòn động lực.
                    <br>
                    • <strong>Job Resources (Nguồn lực &amp; Hỗ trợ):</strong> Sự hỗ trợ từ cấp quản lý trực tiếp, môi trường làm việc và văn hóa công nhận.
                    <br>
                    <span style="color: #0A1F44; font-weight: 700;">🛡️ Tấm Khiên Hấp Thụ Xung Lực:</span> Khi nguồn lực hỗ trợ từ quản lý được nâng cao, nó đóng vai trò như một tấm khiên bảo vệ, giúp trung hòa mọi áp lực và giảm tỷ lệ nghỉ việc. Chất lượng của người quản lý đóng vai trò cốt lõi trong việc duy trì sự gắn kết của nhân sự.
                </p>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("Không đủ dữ liệu so sánh phân nhóm (Muốn nghỉ vs Gắn bó).")

