"""
ANOMALY CARD RENDERER — EES 2026 Dashboard
Hiển thị anomaly alerts theo format chuẩn.
"""

import streamlit as st


SEVERITY_CONFIG = {
    'critical': {
        'bg': '#FEF2F2', 'border': '#DC2626', 'icon': '',
        'badge_bg': '#DC2626', 'badge_text': '#FFFFFF', 'label': 'Khẩn cấp',
    },
    'warning': {
        'bg': '#FFFBEB', 'border': '#D97706', 'icon': '',
        'badge_bg': '#D97706', 'badge_text': '#FFFFFF', 'label': 'Cảnh báo',
    },
    'watch': {
        'bg': '#FFFFF0', 'border': '#CA8A04', 'icon': '',
        'badge_bg': '#CA8A04', 'badge_text': '#FFFFFF', 'label': 'Theo dõi',
    },
}


def render_anomaly_card(anomaly: dict, show_action: bool = True):
    """Hiển thị một anomaly card với style đẹp."""
    sev = anomaly.get('severity', 'watch')
    cfg = SEVERITY_CONFIG.get(sev, SEVERITY_CONFIG['watch'])

    action_html = ''
    if show_action and anomaly.get('action'):
        action_html = (
            f'<div style="margin-top: 12px; padding: 12px 16px; background: rgba(255,255,255,0.8); '
            f'border-radius: 8px; border-left: 3px solid {cfg["border"]};">'
            f'<span style="font-size: 0.72rem; font-weight: 700; color: {cfg["border"]}; '
            f'text-transform: uppercase; letter-spacing: 0.08em;">'
            f'Hành động 30 ngày'
            f'</span>'
            f'<div style="font-size: 0.85rem; color: #374151; margin-top: 6px; line-height: 1.65;">'
            f'{anomaly["action"]}'
            f'</div>'
            f'</div>'
        )

    st.markdown(f"""
<div style="background: {cfg['bg']}; border: 1px solid {cfg['border']}30;
            border-left: 4px solid {cfg['border']}; border-radius: 12px;
            padding: 18px 22px; margin-bottom: 14px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.04);">
    <div style="display: flex; align-items: flex-start; gap: 14px;">
        <div style="flex-shrink: 0;">
            <span style="background: {cfg['badge_bg']}; color: {cfg['badge_text']};
                         font-size: 0.68rem; font-weight: 700; padding: 4px 12px;
                         border-radius: 6px; text-transform: uppercase;
                         letter-spacing: 0.08em;">
                {cfg['label']}
            </span>
        </div>
        <div style="flex: 1; min-width: 0;">
            <div style="font-size: 0.92rem; font-weight: 700; color: #0A1F44; margin-bottom: 8px;
                        letter-spacing: -0.01em;">
                {anomaly.get('title', anomaly.get('name', anomaly.get('pattern', '')))}
            </div>
            <div style="font-size: 0.85rem; color: #475569; line-height: 1.7;">
                {anomaly.get('message', anomaly.get('note', anomaly.get('interpretation', '')))}
            </div>
            {action_html}
        </div>
    </div>
</div>
""", unsafe_allow_html=True)


def render_anomaly_summary_banner(anomalies: list):
    """Hiển thị banner tóm tắt số lượng anomaly theo mức độ."""
    if not anomalies:
        st.markdown("""
<div style="background: #F0FDF4; border: 1px solid #22C55E30; border-radius: 10px;
            padding: 12px 18px; margin-bottom: 16px; display: flex; align-items: center; gap: 10px;">
    <span style="font-size: 0.85rem; color: #166534; font-weight: 600;">
        Không phát hiện bất thường đáng lo ngại. Tiếp tục theo dõi.
    </span>
</div>
""", unsafe_allow_html=True)
        return

    n_critical = sum(1 for a in anomalies if a.get('severity') == 'critical')
    n_warning  = sum(1 for a in anomalies if a.get('severity') == 'warning')
    n_watch    = sum(1 for a in anomalies if a.get('severity') == 'watch')

    parts = []
    if n_critical: parts.append(f"<span style='color:#DC2626;font-weight:800;'>{n_critical} Khẩn cấp</span>")
    if n_warning:  parts.append(f"<span style='color:#D97706;font-weight:800;'>{n_warning} Cảnh báo</span>")
    if n_watch:    parts.append(f"<span style='color:#CA8A04;font-weight:700;'>{n_watch} Theo dõi</span>")
    summary = " &nbsp;·&nbsp; ".join(parts)

    bg = '#FEF2F2' if n_critical else '#FFFBEB' if n_warning else '#FFFFF0'
    border = '#DC2626' if n_critical else '#D97706' if n_warning else '#CA8A04'

    st.markdown(f"""
<div style="background: {bg}; border: 1px solid {border}30; border-left: 4px solid {border};
            border-radius: 12px; padding: 16px 20px; margin-bottom: 24px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.04);">
    <div style="font-size: 0.85rem; color: #0A1F44; margin-bottom: 6px; font-weight: 700;
                letter-spacing: -0.01em;">
        Phát hiện {len(anomalies)} bất thường cần chú ý:
    </div>
    <div style="font-size: 0.9rem; color: #475569;">{summary}</div>
</div>
""", unsafe_allow_html=True)


def render_anomaly_tab(anomalies: list, pillar_id: str = None, show_cross: bool = True):
    """
    Render toàn bộ tab bất thường.
    pillar_id: nếu set → chỉ show anomaly của pillar đó
    show_cross: có show cross-pillar không
    """
    from utils.ai_generator import render_ai_insight_card
    from shared.codebook import PILLAR_META

    if pillar_id:
        pillar_anomalies = [a for a in anomalies if a.get('pillar') == pillar_id]
        cross_anomalies  = [a for a in anomalies if a.get('pillar') == 'CROSS'] if show_cross else []
    else:
        pillar_anomalies = [a for a in anomalies if a.get('pillar') != 'CROSS']
        cross_anomalies  = [a for a in anomalies if a.get('pillar') == 'CROSS']

    all_shown = pillar_anomalies + cross_anomalies
    render_anomaly_summary_banner(all_shown)

    if pillar_anomalies:
        if pillar_id:
            meta = PILLAR_META.get(pillar_id, {})
            st.markdown(f"#### Bất thường trong {meta.get('name', pillar_id)}")
        else:
            st.markdown("#### Bất thường theo Trụ cột")
        for a in pillar_anomalies:
            render_anomaly_card(a, show_action=True)

    if cross_anomalies and show_cross:
        st.markdown("---")
        st.markdown("#### Pattern Liên Trụ cột")
        st.caption("Những nguy hiểm này chỉ nhìn thấy được khi phân tích tất cả trụ cột cùng lúc.")
        for a in cross_anomalies:
            render_anomaly_card(a, show_action=True)

    if not all_shown:
        st.info("Không phát hiện pattern bất thường đáng lo ngại trong điều kiện hiện tại.")

    # AI synthesis
    if all_shown:
        st.markdown("---")
        critical_titles = [a.get('title', a.get('name', a.get('pattern', ''))) for a in all_shown if a.get('severity') == 'critical']
        warning_titles  = [a.get('title', a.get('name', a.get('pattern', ''))) for a in all_shown if a.get('severity') == 'warning']

        p_name = PILLAR_META.get(pillar_id, {}).get('name', 'trụ cột này') if pillar_id else 'toàn nhóm'
        prompt = (
            f"Phân tích tổng hợp các bất thường DỰA VÀO DỮ LIỆU THỰC TẾ trong {p_name} "
            f"(TUYỆT ĐỐI KHÔNG bịa thêm pattern nào khác):\n"
            f"{'Vấn đề khẩn cấp: ' + '; '.join(critical_titles) + '. ' if critical_titles else ''}"
            f"{'Cảnh báo: ' + '; '.join(warning_titles) + '. ' if warning_titles else ''}"
            f"(1) Xác định NÚT THẮT — pattern nào nếu giải quyết sẽ kéo các vấn đề khác lên? "
            f"(2) Nếu không can thiệp, điều gì xảy ra trong 3-6 tháng? "
            f"(3) Nếu chỉ có ngân sách cho 1 can thiệp, đầu tư vào đâu? "
            f"CHỈ phân tích từ các bất thường đã liệt kê."
        )
        ai_data = {
            'Total_Anomalies': len(all_shown),
            'Critical_Count': len(critical_titles),
            'Critical_Patterns': critical_titles,
            'Warning_Patterns': warning_titles,
            'Focus': p_name,
        }
        render_ai_insight_card(
            "Phân tích Tổng hợp Bất thường",
            ai_data, prompt,
            custom_style="margin-top: 20px;"
        )
