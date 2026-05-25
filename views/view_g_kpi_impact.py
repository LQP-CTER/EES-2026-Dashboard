import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from shared.plotly_theme import COLORS, apply_theme

def render(df, cfg):
    st.markdown('<div class="sec-h3"><div class="sec-accent"></div>MÔ PHỎNG TÁC ĐỘNG (KPI SIMULATOR)</div>', unsafe_allow_html=True)
    st.markdown('<p class="sec-desc">Công cụ giả lập giúp Lãnh đạo ra quyết định: Thay đổi một nhân tố sẽ tiết kiệm bao nhiêu chi phí nhân sự?</p>', unsafe_allow_html=True)

    if df is None or df.empty:
        st.warning("Không đủ dữ liệu.")
        return

    # Mock Data for Simulator based on typical EES Random Forest output
    factors = [
        "Khối lượng & Sức khỏe",
        "Lãnh đạo & Chiến lược",
        "Hỗ trợ HO & Quy trình",
        "Phát triển bản thân",
        "Đãi ngộ & Ghi nhận"
    ]
    
    impact_weights = {
        "Khối lượng & Sức khỏe": 0.31,
        "Lãnh đạo & Chiến lược": 0.12,
        "Hỗ trợ HO & Quy trình": 0.11,
        "Phát triển bản thân": 0.11,
        "Đãi ngộ & Ghi nhận": 0.08
    }

    col1, col2 = st.columns([1, 2])
    with col1:
        st.markdown("**1. Cài đặt kịch bản (Scenario)**")
        selected_factor = st.selectbox("Nhân tố muốn cải thiện:", factors)
        improvement = st.slider("Mức tăng kỳ vọng (điểm Likert):", min_value=0.1, max_value=1.0, value=0.3, step=0.1)
        
        avg_salary = st.number_input("Mức lương TB/tháng (VND):", min_value=5000000, max_value=50000000, value=15000000, step=1000000)
        hiring_cost_ratio = st.slider("Chi phí tuyển dụng & Đào tạo lại (% lương năm):", 10, 100, 30, step=5)
        
    with col2:
        st.markdown("**2. Kết quả Dự phóng (Projected Impact)**")
        
        # Calculate impact
        enps_increase = improvement * impact_weights[selected_factor] * 100  # simplified linear projection
        current_enps = df['eNPS'].mean() if 'eNPS' in df.columns else 20
        new_enps = current_enps + enps_increase
        
        # Estimate retention (rule of thumb: 10 points eNPS = 5% retention improvement)
        retention_gain = (enps_increase / 10) * 0.05
        people_saved = int(len(df) * retention_gain)
        if people_saved < 1 and retention_gain > 0: people_saved = 1
        
        # Financial impact
        cost_per_hire = avg_salary * 12 * (hiring_cost_ratio / 100)
        money_saved = people_saved * cost_per_hire
        
        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown('<div class="custom-metric-card">', unsafe_allow_html=True)
            st.markdown('<div class="metric-title">Dự báo eNPS Mới</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="metric-value-row"><span class="metric-value" style="color:{COLORS["green"]}">{new_enps:+.1f}</span></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="metric-delta delta-positive">Tăng {enps_increase:+.1f} điểm</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
            
        with c2:
            st.markdown('<div class="custom-metric-card">', unsafe_allow_html=True)
            st.markdown('<div class="metric-title">Nhân sự giữ chân</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="metric-value-row"><span class="metric-value" style="color:{COLORS["blue"]}">{people_saved}</span><span class="metric-unit">người</span></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="metric-delta delta-neutral">Từ nhóm Nguy cơ</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
            
        with c3:
            st.markdown('<div class="custom-metric-card">', unsafe_allow_html=True)
            st.markdown('<div class="metric-title">Tiết kiệm (ROI)</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="metric-value-row"><span class="metric-value" style="color:{COLORS["orange"]}">{money_saved/1000000:,.0f}</span><span class="metric-unit">Triệu VNĐ</span></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="metric-delta delta-positive">Chi phí thay thế</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
            
        st.markdown("<br>", unsafe_allow_html=True)
        st.info(f"💡 **Insight:** Để đạt được ROI **{money_saved/1000000:,.0f} triệu VNĐ**, Lãnh đạo cần triển khai các Action Plan tập trung vào **{selected_factor}** sao cho điểm trung bình của nhân tố này tăng lên {improvement} điểm.")

