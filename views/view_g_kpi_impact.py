import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from shared.plotly_theme import COLORS, apply_theme

# ─── Group-specific factor definitions ────────────────────────────────────────
# Each group has its own factors + impact weights based on survey pillar relevance
GROUP_FACTORS = {
    'Shipper': {
        'factors': [
            "Chất lượng Quản lý Bưu cục (MEI)",
            "Thu nhập & Công bằng tuyến đường",
            "Hỗ trợ sự cố & Đền bù COD",
            "Ổn định App & Công cụ làm việc",
            "Văn hóa & Đồng đội Bưu cục",
        ],
        'weights': {
            "Chất lượng Quản lý Bưu cục (MEI)":     0.34,
            "Thu nhập & Công bằng tuyến đường":     0.28,
            "Hỗ trợ sự cố & Đền bù COD":           0.18,
            "Ổn định App & Công cụ làm việc":       0.12,
            "Văn hóa & Đồng đội Bưu cục":           0.08,
        },
        'default_salary': 8_000_000,
        'hire_cost_pct': 25,
    },
    'Tài xế': {
        'factors': [
            "Điều phối viên & Phân tuyến công bằng",
            "An toàn lao động & Hỗ trợ dọc tuyến",
            "Thu nhập & Phụ cấp đường dài",
            "Trang thiết bị & Bảo dưỡng xe",
            "Tinh thần đội xe & Được tôn trọng",
        ],
        'weights': {
            "Điều phối viên & Phân tuyến công bằng": 0.32,
            "An toàn lao động & Hỗ trợ dọc tuyến":  0.26,
            "Thu nhập & Phụ cấp đường dài":          0.20,
            "Trang thiết bị & Bảo dưỡng xe":         0.14,
            "Tinh thần đội xe & Được tôn trọng":     0.08,
        },
        'default_salary': 10_000_000,
        'hire_cost_pct': 20,
    },
    'Kho 2A': {
        'factors': [
            "Bố trí ca kíp & Tải trọng công việc",
            "Thiết bị & Điều kiện kho",
            "Lộ trình thăng tiến & Phát triển",
            "Công bằng KPI & Ghi nhận đóng góp",
            "Quản lý trực tiếp & Hỗ trợ ca",
        ],
        'weights': {
            "Bố trí ca kíp & Tải trọng công việc":  0.30,
            "Thiết bị & Điều kiện kho":              0.22,
            "Lộ trình thăng tiến & Phát triển":      0.20,
            "Công bằng KPI & Ghi nhận đóng góp":     0.18,
            "Quản lý trực tiếp & Hỗ trợ ca":         0.10,
        },
        'default_salary': 8_500_000,
        'hire_cost_pct': 22,
    },
    'BC 2B': {
        'factors': [
            "Hỗ trợ xử lý khiếu nại & Quyền hạn",
            "Phối hợp với Shipper & Quy trình giao-nhận",
            "Điều kiện cơ sở vật chất Bưu cục",
            "Thu nhập & Công nhận đóng góp",
            "Quản lý Bưu cục & Hỗ trợ nhân viên",
        ],
        'weights': {
            "Hỗ trợ xử lý khiếu nại & Quyền hạn":     0.31,
            "Phối hợp với Shipper & Quy trình giao-nhận": 0.24,
            "Điều kiện cơ sở vật chất Bưu cục":         0.20,
            "Thu nhập & Công nhận đóng góp":             0.16,
            "Quản lý Bưu cục & Hỗ trợ nhân viên":       0.09,
        },
        'default_salary': 8_000_000,
        'hire_cost_pct': 20,
    },
    'BO 3A': {
        'factors': [
            "Lãnh đạo & Truyền thông Chiến lược",
            "Quy trình nội bộ & Công cụ làm việc",
            "Cơ hội phát triển & Học hỏi",
            "Ghi nhận đóng góp & Thu nhập",
            "Khối lượng công việc & Cân bằng cuộc sống",
        ],
        'weights': {
            "Lãnh đạo & Truyền thông Chiến lược":  0.28,
            "Quy trình nội bộ & Công cụ làm việc": 0.25,
            "Cơ hội phát triển & Học hỏi":          0.20,
            "Ghi nhận đóng góp & Thu nhập":         0.17,
            "Khối lượng công việc & Cân bằng cuộc sống": 0.10,
        },
        'default_salary': 15_000_000,
        'hire_cost_pct': 35,
    },
    'Manager 3B': {
        'factors': [
            "Định hướng Chiến lược & Quyền tự quyết",
            "Sự hỗ trợ từ Lãnh đạo cấp trên",
            "Nguồn lực & Công cụ để lãnh đạo hiệu quả",
            "Phát triển năng lực Lãnh đạo",
            "Ghi nhận & Đãi ngộ xứng đáng",
        ],
        'weights': {
            "Định hướng Chiến lược & Quyền tự quyết": 0.32,
            "Sự hỗ trợ từ Lãnh đạo cấp trên":         0.26,
            "Nguồn lực & Công cụ để lãnh đạo hiệu quả": 0.18,
            "Phát triển năng lực Lãnh đạo":             0.14,
            "Ghi nhận & Đãi ngộ xứng đáng":             0.10,
        },
        'default_salary': 25_000_000,
        'hire_cost_pct': 50,
    },
}

# Default fallback
_DEFAULT_FACTORS = {
    'factors': [
        "Chất lượng Quản lý trực tiếp",
        "Thu nhập & Công bằng đãi ngộ",
        "Môi trường & Công cụ làm việc",
        "Cơ hội Phát triển bản thân",
        "Văn hóa & Ghi nhận",
    ],
    'weights': {
        "Chất lượng Quản lý trực tiếp":   0.30,
        "Thu nhập & Công bằng đãi ngộ":  0.25,
        "Môi trường & Công cụ làm việc": 0.20,
        "Cơ hội Phát triển bản thân":    0.15,
        "Văn hóa & Ghi nhận":            0.10,
    },
    'default_salary': 12_000_000,
    'hire_cost_pct': 30,
}


def render(df, cfg):
    apply_theme()
    st.markdown('<div class="sec-h3"><div class="sec-accent"></div>MÔ PHỎNG TÁC ĐỘNG (KPI SIMULATOR)</div>', unsafe_allow_html=True)

    # Non-DA user explanation
    st.markdown("""
    <div style="background:#F0FDF4;border:1px solid #BBF7D0;border-radius:12px;padding:16px 20px;margin-bottom:20px;">
        <div>
            <div style="font-size:0.82rem;font-weight:700;color:#15803D;margin-bottom:4px;">Công cụ tính ROI — Nếu cải thiện X thì tiết kiệm được bao nhiêu tiền?</div>
            <div style="font-size:0.8rem;color:#475569;line-height:1.55;">
                Công cụ này giúp Lãnh đạo <strong>quy đổi việc cải thiện gắn kết thành tiền</strong>: khi nhân viên gắn kết hơn, họ ít nghỉ hơn — giảm chi phí tuyển dụng và đào tạo lại.
                Chọn nhân tố muốn cải thiện, kéo thanh trượt để xem ngay ước tính tiết kiệm.
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if df is None or df.empty:
        st.warning("Không đủ dữ liệu.")
        return

    # Resolve group-specific config
    short = cfg.get('short', '')
    grp_cfg = GROUP_FACTORS.get(short, _DEFAULT_FACTORS)
    factors         = grp_cfg['factors']
    impact_weights  = grp_cfg['weights']
    default_salary  = grp_cfg['default_salary']
    default_hire_pct= grp_cfg['hire_cost_pct']

    col1, col2 = st.columns([1, 2])
    with col1:
        st.markdown("**1. Cài đặt kịch bản**")
        selected_factor = st.selectbox(
            "Nhân tố muốn cải thiện:",
            factors,
            help="Chọn nhân tố mà khảo sát cho thấy đang ở mức thấp hoặc có ảnh hưởng lớn nhất (xem View F)."
        )
        improvement = st.slider(
            "Mức độ cải thiện kỳ vọng (0.1 = cải thiện nhẹ, 1.0 = cải thiện đáng kể):",
            min_value=0.1, max_value=1.0, value=0.3, step=0.1,
            help="Một điểm Likert tương đương khoảng 20% nhân viên chuyển từ 'không đồng ý' sang 'đồng ý'."
        )
        avg_salary = st.number_input(
            "Lương TB/tháng của nhóm (VND):",
            min_value=3_000_000, max_value=80_000_000,
            value=default_salary, step=500_000,
            help="Dùng mức lương thực tế của nhóm để tính chi phí thay thế khi có người nghỉ."
        )
        hiring_cost_ratio = st.slider(
            "Chi phí tuyển dụng + đào tạo lại (% lương năm):",
            10, 100, default_hire_pct, step=5,
            help="Gồm chi phí đăng tuyển, onboarding, đào tạo và mất năng suất trong giai đoạn đầu."
        )

    with col2:
        st.markdown("**2. Kết quả Dự phóng**")

        # Calculate impact
        weight = impact_weights.get(selected_factor, 0.15)
        enps_increase = improvement * weight * 100
        current_enps  = df['eNPS'].mean() if 'eNPS' in df.columns else 20
        new_enps = current_enps + enps_increase

        # Retention gain: every 10pt eNPS lift → ~5% fewer leavers
        retention_gain = (enps_increase / 10) * 0.05
        people_saved   = max(1, int(len(df) * retention_gain)) if retention_gain > 0 else 0

        # Financial impact
        cost_per_hire = avg_salary * 12 * (hiring_cost_ratio / 100)
        money_saved   = people_saved * cost_per_hire

        # Display weight context
        st.markdown(f"""
        <div style="background:#F8FAFC;border:1px solid #E2E8F0;border-radius:10px;padding:10px 14px;margin-bottom:14px;font-size:0.78rem;color:#475569;">
            📌 Nhân tố <strong style="color:#0A1F44;">"{selected_factor}"</strong> chiếm <strong style="color:#FF5200;">{weight*100:.0f}%</strong> trọng số trong mô hình dự báo nghỉ việc của nhóm <strong>{cfg.get('label','')}</strong>.
            Cải thiện nhân tố này <strong>{improvement} điểm</strong> ước tính nâng eNPS lên <strong>+{enps_increase:.1f} điểm</strong>.
        </div>
        """, unsafe_allow_html=True)

        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown('<div class="custom-metric-card">', unsafe_allow_html=True)
            st.markdown('<div class="metric-title">eNPS dự báo mới</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="metric-value-row"><span class="metric-value" style="color:{COLORS["green"]}">{new_enps:+.1f}</span></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="metric-delta delta-positive">Tăng {enps_increase:+.1f} điểm</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

        with c2:
            st.markdown('<div class="custom-metric-card">', unsafe_allow_html=True)
            st.markdown('<div class="metric-title">Nhân sự giữ chân được</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="metric-value-row"><span class="metric-value" style="color:{COLORS["blue"]}">{people_saved}</span><span class="metric-unit">người</span></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="metric-delta delta-neutral">Từ nhóm có nguy cơ nghỉ</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

        with c3:
            st.markdown('<div class="custom-metric-card">', unsafe_allow_html=True)
            st.markdown('<div class="metric-title">Tiết kiệm chi phí (ROI)</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="metric-value-row"><span class="metric-value" style="color:{COLORS["orange"]}">{money_saved/1_000_000:,.0f}</span><span class="metric-unit">Tr VNĐ</span></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="metric-delta delta-positive">Chi phí tuyển mới + đào tạo</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # Explanation for non-DA users
        cost_per_person_m = cost_per_hire / 1_000_000
        st.markdown(f"""
        <div style="background:#FFFBEB;border:1px solid #FDE68A;border-radius:10px;padding:14px 18px;font-size:0.82rem;line-height:1.65;">
            <strong style="color:#92400E;">Cách đọc con số này:</strong>
            Mỗi nhân viên nghỉ việc khiến công ty mất khoảng <strong style="color:#B45309;">{cost_per_person_m:.1f} triệu VNĐ</strong>
            (tuyển dụng + onboarding + đào tạo + mất năng suất trong 2–3 tháng đầu).
            Nếu cải thiện <em>"{selected_factor}"</em> giúp giữ lại <strong>{people_saved} người</strong>,
            công ty tiết kiệm được <strong style="color:#B45309;">{money_saved/1_000_000:,.0f} triệu VNĐ</strong>
            — đây là con số ROI thực tế từ việc đầu tư vào trải nghiệm nhân viên.
        </div>
        """, unsafe_allow_html=True)

        # Factor weight bar chart
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("**Trọng số tác động của từng nhân tố** — Nhân tố nào ảnh hưởng nhiều nhất đến khả năng giữ chân nhân sự?")
        df_weights = pd.DataFrame([
            {'Nhân tố': k, 'Trọng số (%)': v*100, 'Được chọn': k == selected_factor}
            for k, v in impact_weights.items()
        ]).sort_values('Trọng số (%)', ascending=True)

        colors_bar = [COLORS['orange'] if row['Được chọn'] else COLORS['blue']
                      for _, row in df_weights.iterrows()]
        fig = go.Figure(go.Bar(
            y=df_weights['Nhân tố'],
            x=df_weights['Trọng số (%)'],
            orientation='h',
            marker_color=colors_bar,
            text=[f"{v:.0f}%" for v in df_weights['Trọng số (%)']],
            textposition='outside'
        ))
        fig.update_layout(
            height=280, margin=dict(l=10, r=50, t=20, b=10),
            xaxis_title="% ảnh hưởng đến quyết định nghỉ việc",
            yaxis_title="", showlegend=False,
            xaxis=dict(range=[0, max(df_weights['Trọng số (%)']) * 1.3])
        )
        st.plotly_chart(fig, use_container_width=True)
