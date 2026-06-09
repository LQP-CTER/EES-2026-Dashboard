"""
View: Thẩm định & Độ tin cậy dữ liệu — EES 2026
Trình bày cách xử lý và thẩm định dữ liệu của từng nhóm để tăng độ tin cậy.
"""

import streamlit as st
import pandas as pd

# Base64 AI logo (same as ai_generator.py)
_AI_LOGO_B64 = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAIAAAD8GO2jAAADT0lEQVR4nO1WTWwVVRT+zp15f33PlhojIivKAl0RiKgNCalhUV2ZEBODC+PPorpxQQIoG10TMLjDjQloSKORjUlTF6AYFdPUrjRFTU0auwBCAi/w/mbmns+cmVc0ffPo66I7Tu7M3HvPPd+558w5514hic0kt6noeKhgAAr7cnp/vnQfgOiNDMlYPdObHUVh/jTJZh3UdMu0N4FKVcKCMZMYrUZqTMoCIU6GRnKN6FFAQoTNuh7dJ3frCARJIkHAexGePSjHv7Ylpw/L3CWtlUQTBCE9WRsJTs1JdTQTH8ACQG4u40bsyuAQ4CHFgFcu8u1/bMvfX0Q5CG7VGUKaYBvceqcvztp/kFlw+7p+/Jrs3Me7N93laXjP0z9i7huGBfNHEuG5l+XIfoROXzgsw49zad4d+UJGt/VaYN7OoXZDo5Z2Wsn7BzgBf/adbDpemI1/nc36/uy7xjp+QDtNjdpsN3KR+iggqT45Ns4J6KGCX7lG9UziLiuJqd6vXNNDRU4gOfY8ve8Hk1eLfGKvKxdk4Spqjjt2u+27zPVBaHFFtQ7Ebd/FHbtRc7Lwi/5w4b7gGspTIOnk5XMoCCLF2B4bqu+yMm42HNvDSFEQfnfuP8F1FJBwjlELK4tSJBQYfTKN914iHt1mqVKkrCyaiHO9+d+nXEctiVtZIqF5Z7VCrLUUjXr6FUQta3nUoyCDKtdQGaYHSsD8DNUbirmF1tIhVTk/I2VIQlaGTeS++AMtMCAJi9y5Fx3hUAlLf/HzE3CBNQOQrK/nP5ClP1kpoSMytlfCYroDGfREk8kpCKEqtQDTJ/2ZN3T5NwvQJNbl3/XMmzJ9EtUAqlZaJ6f64uRXU1U450+9KjNf4rESkgT3PKoOT4wZ9/rf0lA8EjAI5VZHX3olOPpVJjKwAptM8/nDF2X+Z2wJEBaQRBKpMYvOHOJj3PZ8Zlw+mpVKzZyTV037nwdZUWo39NP38O1nEgPF1dqYQCKwAEy+JVOfSLmWU4LWV7CqA4Au/oRL5/nHVanfsNXDW/HUuBx83T29///LNq4gE05Tr5sTWeBXR7p4qgbdH33gI1O9qbEStEo+MVwL3HVog2cy08UP3PLAt4r8/cjG1j+82Q1Am367/hffvQmZc1fQbgAAAABJRU5ErkJggg=="


def _sec(title: str, subtitle: str = "") -> str:
    accent = '<span style="width:3px;height:15px;background:#FF5200;border-radius:2px;display:inline-block;flex-shrink:0"></span>'
    html = (
        f'<h3 style="font-size:0.92rem;font-weight:700;color:#0A1F44;'
        f'margin:28px 0 12px;padding-bottom:10px;border-bottom:1px solid #F1F5F9;'
        f'display:flex;align-items:center;gap:8px">{accent}{title}</h3>'
    )
    if subtitle:
        html += f'<p style="font-size:0.82rem;color:#64748B;margin:-6px 0 16px;font-weight:500">{subtitle}</p>'
    return html


def _callout(title: str, body: str, color: str = "#FF5200", bg: str = "#FFF8F5") -> str:
    return f"""
    <div style="background:{bg};border:1px solid {color}33;border-left:4px solid {color};
                border-radius:10px;padding:18px 22px;margin:16px 0;">
        <div style="font-size:0.88rem;font-weight:700;color:#0A1F44;margin-bottom:8px;
                    display:flex;align-items:center;gap:8px;">
            <img src="{_AI_LOGO_B64}" style="width:16px;height:16px"> {title}
        </div>
        <div style="font-size:0.84rem;color:#475569;line-height:1.7">{body}</div>
    </div>"""


def _info_box(body: str) -> str:
    return f"""
    <div style="background:#F8FAFC;border:1px solid #E2E8F0;border-radius:10px;
                padding:16px 20px;margin:12px 0;font-size:0.85rem;color:#475569;line-height:1.7">
        {body}
    </div>"""


def _metric_tile(label: str, value: str, note: str, accent: str, bg: str, val_size: str = "clamp(1.7rem, 2vw, 2.25rem)") -> str:
    return f"""
    <div style="background:{bg};border:1px solid {accent}33;border-radius:18px;
                padding:18px 18px 20px;box-shadow:0 16px 30px rgba(10,31,68,.08);
                position:relative;overflow:hidden;min-width:0;">
        <div style="position:absolute;top:0;left:0;right:0;height:4px;background:linear-gradient(90deg,{accent},#FFB38B);"></div>
        <div style="font-size:.68rem;font-weight:800;color:{accent};text-transform:uppercase;letter-spacing:.12em;margin-bottom:10px;">
            {label}
        </div>
        <div style="font-size:{val_size};font-weight:900;color:#0A1F44;line-height:.95;letter-spacing:-.04em;font-variant-numeric:tabular-nums;white-space:nowrap;">
            {value}
        </div>
        <div style="font-size:.78rem;color:#64748B;line-height:1.45;margin-top:8px;">
            {note}
        </div>
    </div>
    """


_RELIABILITY_GROUPS = [
    ('1A', 'Shipper',       12955),
    ('1B', 'Tài xế',         801),
    ('2A', 'NV Kho',         4892),
    ('2B', 'QL Tuyến đầu',   425),
    ('3A', 'NV Văn phòng',   917),
    ('3B', 'Manager HO',     109),
]

DEEPDIVE_QUALITY_TOTALS = {
    "headcount": 21353,
    "raw": 20005,
    "dropped": 878,
    "cleaned": 19221,
    "straightline_weighted": 8757,
    "effective_base": 16435,
}

DEEPDIVE_GROUP_BASE = [
    {
        "Nhóm": "1A · Nhân viên giao nhận",
        "Raw submissions": 12955,
        "Dropped": 693,
        "Cleaned base": 12262,
        "EI": 73.5,
        "eNPS": 31.8,
        "Stay": 4.01,
        "Leave %": 5.3,
        "Silence %": 58.8,
        "MEI": 81.7,
        "Flight Risk %": 5.5,
    },
    {
        "Nhóm": "1B · Tài xế",
        "Raw submissions": 801,
        "Dropped": 17,
        "Cleaned base": 784,
        "EI": 75.9,
        "eNPS": 47.8,
        "Stay": None,
        "Leave %": 2.1,
        "Silence %": 61.7,
        "MEI": None,
        "Flight Risk %": None,
    },
    {
        "Nhóm": "2A · Nhân viên kho",
        "Raw submissions": 4892,
        "Dropped": 73,
        "Cleaned base": 4819,
        "EI": 72.4,
        "eNPS": 28.5,
        "Stay": None,
        "Leave %": 3.4,
        "Silence %": 10.4,
        "MEI": 78.8,
        "Flight Risk %": None,
    },
    {
        "Nhóm": "2B · Quản lý tuyến đầu",
        "Raw submissions": 425,
        "Dropped": 0,
        "Cleaned base": 425,
        "EI": 78.9,
        "eNPS": 59.6,
        "Stay": 4.36,
        "Leave %": 2.7,
        "Silence %": 4.9,
        "MEI": 89.1,
        "Flight Risk %": None,
    },
    {
        "Nhóm": "3A · Nhân viên văn phòng",
        "Raw submissions": 917,
        "Dropped": 95,
        "Cleaned base": 822,
        "EI": 71.5,
        "eNPS": 16.3,
        "Stay": 4.01,
        "Leave %": 4.0,
        "Silence %": 6.2,
        "MEI": 81.8,
        "Flight Risk %": None,
    },
    {
        "Nhóm": "3B · Manager HO",
        "Raw submissions": 109,
        "Dropped": 0,
        "Cleaned base": 109,
        "EI": 73.6,
        "eNPS": 32.7,
        "Stay": None,
        "Leave %": 0.9,
        "Silence %": 9.2,
        "MEI": None,
        "Flight Risk %": None,
    },
]


def _reliability_row(gid, label, df, n_raw):
    report = df.attrs.get('memo_report', {})
    nlp = report.get('nlp', {})
    calibration = df.attrs.get('calibration_report', {})
    return {
        'Nhóm': f'{gid} · {label}',
        'Mẫu thô (Supabase)': n_raw,
        'Sau Dedup': int(report.get('n_after_dedup', n_raw)),
        'Maha flag': int(report.get('flags', {}).get('maha_flag_n', 0)),
        'Contradiction': int(report.get('flags', {}).get('contradiction_n', 0)),
        'NLP tiêu cực': int(nlp.get('negative_n', 0)),
        'NLP cảnh báo': int(nlp.get('warning_signal_n', 0)),
        'AUC (Logistic)': calibration.get('cv_auc') if calibration.get('cv_auc') is not None else float('nan'),
        'VIF cao': len(calibration.get('high_vif', {})) if calibration.get('enabled') else 0,
        '0 bằng chứng': int(report.get('flags', {}).get('corroboration_dist', {}).get('0_evidence', 0)),
        '1 bằng chứng': int(report.get('flags', {}).get('corroboration_dist', {}).get('1_evidence', 0)),
        '2 bằng chứng': int(report.get('flags', {}).get('corroboration_dist', {}).get('2_evidence', 0)),
        'KEEP': int(report.get('tier_counts', {}).get('KEEP', 0)),
        'DOWNWEIGHT': int(report.get('tier_counts', {}).get('DOWNWEIGHT', 0)),
        'DROP': int(report.get('tier_counts', {}).get('DROP', 0)),
        'n hiệu dụng': float(report.get('n_effective', 0)),
        '% giữ': float(report.get('effective_pct', 0)),
    }


def compute_reliability_table(log_callback=None):
    """Load and summarize reliability metrics for all 6 survey groups."""
    from utils.data_loader import load_group

    rows = []
    for gid, label, _raw_expected in _RELIABILITY_GROUPS:
        try:
            if log_callback:
                log_callback(f"Đang tải dữ liệu khảo sát nhóm {gid} - {label}...")
            df, n_raw = load_group(gid)
            if df is None or df.empty:
                if log_callback:
                    log_callback(f"Nhóm {gid} không có dữ liệu.")
                continue
            rows.append(_reliability_row(gid, label, df, n_raw))
            if log_callback:
                log_callback(f"Đã tải dữ liệu khảo sát nhóm {gid} ({len(df):,} mẫu hợp lệ).", "ok")
        except Exception as e:
            st.warning(f"Không tải được nhóm {gid}: {e}")
            if log_callback:
                log_callback(f"Không tải được nhóm {gid}: {e}")
            continue
    if log_callback:
        log_callback("Đang tổng hợp bảng độ tin cậy...")
    return pd.DataFrame(rows)


def render(summary_df=None):
    st.markdown("""
    <style>
    .dt-shell {
        border-radius: 28px;
        padding: 32px;
        margin: 20px 0 28px;
        background:
            radial-gradient(circle at 10% 0%, rgba(255,82,0,.10), transparent 28%),
            radial-gradient(circle at 90% 14%, rgba(29,78,216,.08), transparent 30%),
            linear-gradient(135deg, #FFFFFF 0%, #F8FAFC 54%, #EEF6FF 100%);
        border: 1px solid rgba(226,232,240,.95);
        box-shadow: 0 24px 64px rgba(10,31,68,.11), inset 0 1px 0 rgba(255,255,255,.96);
    }
    .dt-hero {
        display:grid;
        grid-template-columns:minmax(0,1.25fr) minmax(320px,.75fr);
        gap:24px;
        align-items:stretch;
    }
    .dt-kicker {
        display:inline-flex;
        align-items:center;
        gap:8px;
        padding:7px 12px;
        border-radius:999px;
        background:#FFF4EF;
        border:1px solid #FFD5BF;
        color:#FF5200;
        font-size:.72rem;
        font-weight:800;
        letter-spacing:.16em;
        text-transform:uppercase;
        margin-bottom:14px;
    }
    .dt-kicker::before {
        content:'';
        width:8px;
        height:8px;
        border-radius:50%;
        background:#10B981;
        box-shadow:0 0 0 5px rgba(16,185,129,.14);
    }
    .dt-title {
        font-size:clamp(2.1rem, 3.4vw, 3.4rem);
        line-height:1.04;
        letter-spacing:-.04em;
        font-weight:900;
        color:#0A1F44;
        margin:0 0 14px;
    }
    .dt-subtitle {
        color:#475569;
        font-size:1rem;
        line-height:1.72;
        font-weight:500;
        margin:0;
        max-width:760px;
    }
    .dt-hero-panel {
        border-radius:24px;
        padding:22px;
        background:linear-gradient(145deg, rgba(10,31,68,.96), rgba(29,78,216,.88));
        box-shadow:0 24px 52px rgba(10,31,68,.22);
        color:#fff;
        position:relative;
        overflow:hidden;
        min-height:220px;
    }
    .dt-hero-panel::before {
        content:'';
        position:absolute;
        inset:0;
        background:
            linear-gradient(rgba(255,255,255,.08) 1px, transparent 1px),
            linear-gradient(90deg, rgba(255,255,255,.07) 1px, transparent 1px);
        background-size:30px 30px;
        opacity:.55;
        pointer-events:none;
    }
    .dt-hero-panel::after {
        content:'';
        position:absolute;
        width:220px;
        height:220px;
        right:-70px;
        bottom:-100px;
        background:radial-gradient(circle, rgba(255,82,0,.42) 0%, transparent 65%);
        pointer-events:none;
    }
    .dt-hero-panel-inner {
        position:relative;
        z-index:1;
        display:flex;
        flex-direction:column;
        gap:18px;
        height:100%;
    }
    .dt-hero-label {
        font-size:.72rem;
        font-weight:800;
        letter-spacing:.18em;
        text-transform:uppercase;
        color:#FFDBCC;
    }
    .dt-hero-score {
        font-size:clamp(2.5rem, 4vw, 4.4rem);
        line-height:.9;
        font-weight:900;
        letter-spacing:-.05em;
    }
    .dt-hero-mini {
        color:rgba(255,255,255,.82);
        font-size:.84rem;
        line-height:1.55;
        max-width:280px;
    }
    .dt-hero-pills {
        margin-top:auto;
        display:flex;
        flex-wrap:wrap;
        gap:8px;
    }
    .dt-pill {
        display:inline-flex;
        align-items:center;
        padding:7px 11px;
        border-radius:999px;
        background:rgba(255,255,255,.12);
        border:1px solid rgba(255,255,255,.18);
        color:#fff;
        font-size:.68rem;
        font-weight:800;
        backdrop-filter:blur(10px);
    }
    .dt-metrics {
        display:grid;
        grid-template-columns:repeat(5,minmax(0,1fr));
        gap:16px;
        margin-top:18px;
    }
    .dt-card {
        background:#fff;
        border:1px solid #E2E8F0;
        border-radius:18px;
        padding:18px 20px;
        box-shadow:0 14px 30px rgba(10,31,68,.06);
    }
    .dt-tabs-shell {
        margin-top:18px;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap:8px;
        background:#F8FAFC;
        padding:8px;
        border-radius:18px;
        border:1px solid #E2E8F0;
    }
    .stTabs [data-baseweb="tab"] {
        background:transparent;
        border-radius:12px;
        padding:10px 14px;
        font-weight:700;
        color:#64748B;
    }
    .stTabs [aria-selected="true"] {
        background:#fff;
        color:#0A1F44;
        box-shadow:0 8px 22px rgba(10,31,68,.10);
    }
    @media (max-width: 1080px) {
        .dt-hero { grid-template-columns:1fr; }
        .dt-metrics { grid-template-columns:repeat(2,minmax(0,1fr)); }
    }
    @media (max-width: 760px) {
        .dt-shell { padding:20px; border-radius:22px; }
        .dt-metrics { grid-template-columns:1fr; }
    }
    </style>
    """, unsafe_allow_html=True)

    if summary_df is None:
        summary_df = compute_reliability_table()

    runtime_available = summary_df is not None and not summary_df.empty

    totals = DEEPDIVE_QUALITY_TOTALS
    headcount_total = totals["headcount"]
    raw_total = totals["raw"]
    drop_total = totals["dropped"]
    cleaned_total = totals["cleaned"]
    straightline_total = totals["straightline_weighted"]
    eff_total = totals["effective_base"]
    participation_pct = raw_total / max(headcount_total, 1) * 100
    drop_pct = drop_total / max(raw_total, 1) * 100
    straightline_pct = straightline_total / max(cleaned_total, 1) * 100
    effective_pct = eff_total / max(cleaned_total, 1) * 100

    st.markdown(f"""
    <div class="dt-shell">
        <div class="dt-hero">
            <div>
                <span class="dt-kicker">EES 2026 · Phương pháp luận</span>
                <h1 class="dt-title">Thẩm định &amp; Độ tin cậy dữ liệu</h1>
                <p class="dt-subtitle">Khung xử lý dữ liệu được thiết kế để giữ lại tín hiệu hữu ích, giảm nhiễu do trả lời thiếu chú tâm, và đưa ra base phân tích có thể đọc được một cách nhất quán.</p>
            </div>
            <div class="dt-hero-panel">
                <div class="dt-hero-panel-inner">
                    <span class="dt-hero-label">DeepDive v13 · Bảng chất lượng dữ liệu</span>
                    <div>
                        <div class="dt-hero-score">19,221</div>
                        <div class="dt-hero-mini">Mẫu phân tích sau làm sạch, lấy theo bảng dữ liệu chính trong EES 2026 DeepDive v13 Final.</div>
                    </div>
                    <div class="dt-hero-pills">
                        <span class="dt-pill">Phản hồi thô 20,005</span>
                        <span class="dt-pill">Bị loại 878</span>
                        <span class="dt-pill">n hiệu dụng 16,435</span>
                    </div>
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="dt-metrics">
        {_metric_tile("HRIS base", f"{headcount_total:,}", "Tổng nhân sự trong bảng DeepDive v13", "#0A1F44", "#F8FAFC")}
        {_metric_tile("Phản hồi thô", f"{raw_total:,}", f"{participation_pct:.1f}% / HRIS base", "#1D4ED8", "#EFF6FF")}
        {_metric_tile("Mẫu phân tích", f"{cleaned_total:,}", f"loại {drop_total:,} phản hồi ({drop_pct:.1f}%)", "#10B981", "#F0FDF4")}
        {_metric_tile("Straight-line", f"{straightline_total:,}", f"{straightline_pct:.1f}% / cleaned base", "#F97316", "#FFF7ED")}
        {_metric_tile("n hiệu dụng", f"{eff_total:,}", f"{effective_pct:.1f}% / cleaned base", "#7C3AED", "#F5F3FF")}
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="dt-card" style="margin:18px 0 26px;">
        <p style="font-size:0.88rem;color:#475569;line-height:1.75;margin:0">
            Các chỉ số chính trong trang này được cố định theo bảng dữ liệu của
            <strong>EES_2026_DeepDive_v13_Final.pdf</strong>: HRIS base 21,353, phản hồi thô
            20,005, mẫu phân tích sau làm sạch 19,221, straight-line weighted 8,757 và
            n hiệu dụng 16,435. Bảng runtime bên dưới chỉ dùng để đối chiếu kỹ thuật khi cần.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # ── Tabs for each section ───────────────────────────────────────
    tab1, tab2, tab3, tab4 = st.tabs([
        "1.1 · Tỷ lệ tham gia & đại diện",
        "1.2 · Phân hạng độ tin cậy & Base",
        "1.3 · Thang đo & Cronbach Alpha",
        "1.4 · Lưu ý sử dụng kết quả",
    ])

    # ═══════════════════════════════════════════════════
    # TAB 1: TỶ LỆ THAM GIA & ĐẠI DIỆN
    # ═══════════════════════════════════════════════════
    with tab1:
        st.markdown(_sec("Tỷ lệ tham gia & Tính đại diện"), unsafe_allow_html=True)

        st.markdown("""
        <p style="font-size:0.88rem;color:#475569;line-height:1.75">
            Theo bảng dữ liệu trong DeepDive v13, tỷ lệ tham gia toàn công ty đạt
            <strong>93.7%</strong> với <strong>20,005</strong> phản hồi trên nền HRIS
            <strong>21,353</strong> nhân sự. Sau bước làm sạch, base phân tích còn
            <strong>19,221</strong> mẫu; phần bị loại khỏi base chính là <strong>878</strong>
            phản hồi, tương đương <strong>4.4%</strong> mẫu thô.
        </p>
        """, unsafe_allow_html=True)

        # KPI cards
        cols = st.columns(4)
        kpi_data = [
            ("Tổng GHN", "93.7%", "20,005 / 21,353", "#FF5200", "#FFF3EE"),
            ("Mẫu phân tích", "19,221", "sau loại 878 phản hồi", "#10B981", "#F0FDF4"),
            ("Straight-line", "8,757", "45.6% / cleaned base", "#3B82F6", "#EFF6FF"),
            ("n hiệu dụng", "16,435", "85.5% / cleaned base", "#8B5CF6", "#F5F3FF"),
        ]
        for col, (label, val, sub, color, bg) in zip(cols, kpi_data):
            with col:
                st.markdown(f"""
                <div style="background:{bg};border:1px solid {color}33;border-radius:12px;
                            padding:18px 20px;text-align:center;">
                    <div style="font-size:0.68rem;font-weight:700;color:{color};text-transform:uppercase;
                                letter-spacing:0.08em;margin-bottom:8px">{label}</div>
                    <div style="font-size:2rem;font-weight:900;color:#0A1F44;line-height:1;
                                letter-spacing:-0.03em">{val}</div>
                    <div style="font-size:0.75rem;color:#64748B;margin-top:6px">{sub}</div>
                </div>
                """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("""
        <p style="font-size:0.88rem;color:#475569;line-height:1.75">
            <strong>Hai nhóm nhỏ cần thận trọng khi đọc lát cắt sâu:</strong>
            Manager HO (3B, n=109, biên sai số ±3.4%) và Quản lý tuyến đầu (2B, n=425).
            Với các nhóm này, chênh lệch nhỏ giữa các đơn vị con có thể chỉ là nhiễu thống kê —
            không nên đọc như sự khác biệt cấu trúc mà không kiểm tra thêm.
        </p>
        """, unsafe_allow_html=True)

        st.markdown(_callout(
            "Ý nghĩa thực tiễn",
            "Với 1A, bảng DeepDive ghi nhận 12,955 phản hồi thô và 12,262 mẫu phân tích sau làm sạch. "
            "Tỷ lệ silence/straight-line cao cần được đọc như một tín hiệu chất lượng dữ liệu cần hiệu chỉnh trọng số, "
            "không tự động đồng nghĩa toàn bộ nhóm là dữ liệu rác.",
            color="#10B981", bg="#F0FDF4"
        ), unsafe_allow_html=True)

    # ═══════════════════════════════════════════════════
    # TAB 2: PHÂN HẠNG ĐỘ TIN CẬY & BASE PHÂN TÍCH
    # ═══════════════════════════════════════════════════
    with tab2:
        st.markdown(_sec("Phân hạng độ tin cậy & Base phân tích"), unsafe_allow_html=True)

        st.markdown("""
        <p style="font-size:0.88rem;color:#475569;line-height:1.75;margin-bottom:12px">
            Bảng dưới đây viết lại theo đúng bảng dữ liệu trong <strong>EES 2026 DeepDive v13 Final</strong>.
            Luồng đọc số là: HRIS base → phản hồi thô → phản hồi bị loại khỏi base chính →
            cleaned analytical base → straight-line weighted → effective base.
        </p>
        <ul style="font-size:0.85rem;color:#475569;line-height:1.7;margin-bottom:20px;padding-left:20px">
            <li><strong>Phản hồi thô (Raw submissions):</strong> toàn bộ phản hồi thu thập theo từng nhóm khảo sát.</li>
            <li><strong>Bị loại (Dropped):</strong> phản hồi bị loại khỏi base phân tích đã làm sạch trong bảng DeepDive.</li>
            <li><strong>Mẫu phân tích (Cleaned base):</strong> mẫu chính thức dùng để đọc EI, eNPS, Leave, Silence và các trụ cột.</li>
            <li><strong>n hiệu dụng (Effective base):</strong> tổng n sau hiệu chỉnh trọng số chất lượng, dùng cho số tổng thể.</li>
        </ul>
        """, unsafe_allow_html=True)

        df_table = pd.DataFrame(DEEPDIVE_GROUP_BASE)
        df_table["Drop %"] = df_table["Dropped"] / df_table["Raw submissions"].clip(lower=1) * 100
        df_table["Cleaned %"] = df_table["Cleaned base"] / df_table["Raw submissions"].clip(lower=1) * 100
        df_table = df_table[[
            "Nhóm", "Raw submissions", "Dropped", "Drop %", "Cleaned base",
            "Cleaned %", "EI", "eNPS", "Leave %", "Silence %", "MEI", "Flight Risk %"
        ]].rename(columns={
            "Raw submissions": "Phản hồi thô (Raw)",
            "Dropped": "Bị loại (Dropped)",
            "Drop %": "Tỷ lệ loại (Drop %)",
            "Cleaned base": "Mẫu phân tích (Cleaned)",
            "Cleaned %": "Tỷ lệ giữ (Cleaned %)",
            "Leave %": "Ý định nghỉ (Leave %)",
            "Silence %": "Im lặng (Silence %)",
            "Flight Risk %": "Rủi ro rời bỏ (Flight Risk)",
        })

        st.dataframe(
            df_table.style.format({
                "Phản hồi thô (Raw)": "{:,.0f}",
                "Bị loại (Dropped)": "{:,.0f}",
                "Tỷ lệ loại (Drop %)": "{:.1f}%",
                "Mẫu phân tích (Cleaned)": "{:,.0f}",
                "Tỷ lệ giữ (Cleaned %)": "{:.1f}%",
                "EI": "{:.1f}",
                "eNPS": "{:+.1f}",
                "Ý định nghỉ (Leave %)": "{:.1f}%",
                "Im lặng (Silence %)": "{:.1f}%",
                "MEI": "{:.1f}",
                "Rủi ro rời bỏ (Flight Risk)": "{:.1f}%",
            }, na_rep="-"),
            width="stretch",
            height=300,
            hide_index=True,
        )

        st.markdown("""
        <p style="font-size:0.78rem;color:#94A3B8;margin-top:12px;line-height:1.6;font-style:italic">
            * DeepDive v13 trình bày n hiệu dụng ở cấp tổng thể là 16,435; bảng nhóm phía trên
            dùng cleaned base theo từng nhóm, không ép phân bổ lại n hiệu dụng theo nhóm khi tài liệu
            không công bố chi tiết phân bổ này.
        </p>
        """, unsafe_allow_html=True)

        advanced_cols = [
            'Nhóm', 'Maha flag', 'NLP tiêu cực', 'NLP cảnh báo',
            'AUC (Logistic)', 'VIF cao', 'KEEP', 'DOWNWEIGHT', 'DROP', 'n hiệu dụng'
        ]
        if runtime_available:
            live_cols = [c for c in advanced_cols if c in summary_df.columns]
            if live_cols:
                with st.expander("Đối chiếu runtime từ dữ liệu đang load (tham khảo kỹ thuật)", expanded=False):
                    st.caption("Bảng này phục vụ kiểm tra Mahalanobis, NLP và Logistic/VIF trong phiên hiện tại; không thay thế số chuẩn trong DeepDive v13.")
                    st.dataframe(
                        summary_df[live_cols].style.format({
                            'Maha flag': '{:,}',
                            'NLP tiêu cực': '{:,}',
                            'NLP cảnh báo': '{:,}',
                            'AUC (Logistic)': '{:.3f}',
                            'VIF cao': '{:,}',
                            'KEEP': '{:,}',
                            'DOWNWEIGHT': '{:,}',
                            'DROP': '{:,}',
                            'n hiệu dụng': '{:,.1f}',
                        }),
                        width='stretch',
                        height=260,
                    )

        st.markdown("<br>", unsafe_allow_html=True)

        # Two validation points callout
        st.markdown(f"""
        <div style="background:#FFFBEB;border:1px solid #FDE68A;border-left:4px solid #F59E0B;
                    border-radius:10px;padding:20px 24px;margin-top:12px">
            <div style="font-size:0.9rem;font-weight:700;color:#0A1F44;margin-bottom:14px;
                        display:flex;align-items:center;gap:8px">
                <img src="{_AI_LOGO_B64}" style="width:16px;height:16px">
                Hai điểm cần xác nhận trước khi trình chính thức
            </div>
            <div style="font-size:0.85rem;color:#475569;line-height:1.75">
                <strong>(1)</strong> File nhóm 2B chứa một bảng "test" 223 phản hồi không trùng
                điểm với 425 phản hồi chính; nếu gộp sẽ vượt quá tỷ lệ tham gia nhân sự thực
                của nhóm — cần xác minh nguồn gốc.<br><br>
                <strong>(2)</strong> So sánh với baseline 2025 (Engagement 8.02/10; eNPS +33.61%)
                cần thận trọng: thang đo đổi từ 1–10 sang 1–5 và cơ cấu nhóm khác nhau. Con số
                2026 không nên đọc là "sụt giảm" mà là một điểm khởi đầu mới trên thước đo mới.
            </div>
        </div>
        """, unsafe_allow_html=True)

    # ═══════════════════════════════════════════════════
    # TAB 3: THANG ĐO & CRONBACH ALPHA
    # ═══════════════════════════════════════════════════
    with tab3:
        st.markdown(_sec("Độ tin cậy thang đo & Cảnh báo"), unsafe_allow_html=True)

        st.markdown("""
        <p style="font-size:0.88rem;color:#475569;line-height:1.75">
            Hệ số Cronbach Alpha của bộ 22 câu Likert đạt <strong>0.94–0.99</strong> ở cả 6 nhóm —
            thang đo nhất quán nội tại ở mức rất cao. Tuy nhiên hệ số quá cao (&gt;0.95) kèm tỷ
            lệ trả lời đồng nhất lớn cũng là tín hiệu của một số câu hỏi trùng lặp và/hoặc xu
            hướng trả lời đồng thuận — do đó báo cáo này luôn đọc kèm <em>phân phối điểm</em>
            và <em>phản hồi mở</em>, không chỉ dựa vào điểm trung bình.
        </p>
        """, unsafe_allow_html=True)

        # Alpha table
        alpha_data = {
            "Nhóm": ["1A - Shipper", "1B - Tài xế", "2A - NV Kho",
                     "2B - QL tuyến đầu", "3A - NV Văn phòng", "3B - Manager HO"],
            "Cronbach α": [0.97, 0.96, 0.98, 0.95, 0.94, 0.99],
            "Số câu Likert": [22, 22, 22, 22, 22, 22],
            "Đánh giá": ["Rất cao", "Rất cao", "Rất cao", "Cao", "Cao", "Cực cao — theo dõi"],
        }
        alpha_df = pd.DataFrame(alpha_data)

        eval_color = {
            "Rất cao": ("#15803D", "#F0FDF4"),
            "Cao": ("#1D4ED8", "#EFF6FF"),
            "Cực cao — theo dõi": ("#D97706", "#FFFBEB"),
        }

        header_cols2 = st.columns([2.5, 1.2, 1.5, 2])
        for col, h, bg in zip(
            header_cols2,
            ["Nhóm", "Cronbach α", "Số câu Likert", "Đánh giá"],
            ["#0A1F44", "#0A1F44", "#0A1F44", "#0A1F44"]
        ):
            with col:
                st.markdown(
                    f'<div style="background:{bg};color:white;padding:10px 14px;'
                    f'border-radius:8px 8px 0 0 ;font-size:0.78rem;font-weight:700">{h}</div>',
                    unsafe_allow_html=True
                )

        for i, row in alpha_df.iterrows():
            bg = "#FFFFFF" if i % 2 == 0 else "#F8FAFC"
            ev_color, ev_bg = eval_color.get(row["Đánh giá"], ("#475569", "#F8FAFC"))
            row_cols2 = st.columns([2.5, 1.2, 1.5, 2])
            cell = f"background:{bg};padding:9px 14px;font-size:0.84rem;border-bottom:1px solid #F1F5F9"
            with row_cols2[0]:
                st.markdown(f'<div style="{cell};font-weight:600;color:#0A1F44">{row["Nhóm"]}</div>', unsafe_allow_html=True)
            with row_cols2[1]:
                st.markdown(f'<div style="{cell};text-align:center;font-weight:700;color:#0A1F44">{row["Cronbach α"]:.2f}</div>', unsafe_allow_html=True)
            with row_cols2[2]:
                st.markdown(f'<div style="{cell};text-align:center;color:#475569">{row["Số câu Likert"]}</div>', unsafe_allow_html=True)
            with row_cols2[3]:
                st.markdown(
                    f'<div style="{cell}"><span style="background:{ev_bg};color:{ev_color};'
                    f'padding:3px 10px;border-radius:20px;font-size:0.75rem;font-weight:700">'
                    f'{row["Đánh giá"]}</span></div>',
                    unsafe_allow_html=True
                )

        st.markdown("<br>", unsafe_allow_html=True)

        st.markdown(_callout(
            "Hệ số quá cao cần đọc kèm phân phối",
            "Cronbach α > 0.95 ở nhóm kho và shipper có thể phản ánh hiệu ứng halo "
            "(người trả lời đồng ý hoặc không đồng ý với toàn bộ bộ câu hỏi theo xu hướng chung), "
            "không hẳn là sự nhất quán tâm lý thực sự. "
            "Đây là lý do báo cáo <strong>luôn đính kèm biểu đồ phân phối điểm</strong> và "
            "<strong>phân tích phản hồi mở định tính</strong> để tam giác hóa với điểm trung bình.",
            color="#F59E0B", bg="#FFFBEB"
        ), unsafe_allow_html=True)

        # Pillar reliability breakdown
        st.markdown(_sec("Độ tin cậy theo từng Trụ cột"), unsafe_allow_html=True)

        pillar_alpha = {
            "Trụ cột": [
                "TC1 · Gắn kết Tổ chức",
                "TC2 · Quản lý Trực tiếp",
                "TC3 · Môi trường & Điều kiện",
                "TC4 · Thu nhập & Phúc lợi",
                "TC5 · Phát triển & Cơ hội",
            ],
            "Số câu": [7, 5, 4, 3, 3],
            "α trung bình": [0.93, 0.91, 0.89, 0.87, 0.88],
            "Ghi chú": [
                "Nhất quán cao — đọc kèm eNPS",
                "Nhất quán cao — kiểm tra gap Q9 vs Q12",
                "Nhất quán — xem phân phối tầng lớp",
                "Cảnh báo: 2 câu tương quan rất cao (r=0.91)",
                "Ổn định — nhưng câu Q19 có phân kỳ tenure",
            ]
        }

        pillar_alpha_df = pd.DataFrame(pillar_alpha)
        for i, row in pillar_alpha_df.iterrows():
            bg = "#FFFFFF" if i % 2 == 0 else "#F8FAFC"
            p_cols = st.columns([3, 1, 1.2, 3])
            cell_s = f"background:{bg};padding:8px 12px;font-size:0.83rem;border-bottom:1px solid #F1F5F9"
            with p_cols[0]:
                st.markdown(f'<div style="{cell_s};font-weight:600;color:#0A1F44">{row["Trụ cột"]}</div>', unsafe_allow_html=True)
            with p_cols[1]:
                st.markdown(f'<div style="{cell_s};text-align:center;color:#64748B">{row["Số câu"]}</div>', unsafe_allow_html=True)
            with p_cols[2]:
                alpha_val = row["α trung bình"]
                a_color = "#15803D" if alpha_val >= 0.90 else "#D97706"
                st.markdown(f'<div style="{cell_s};text-align:center;font-weight:700;color:{a_color}">{alpha_val:.2f}</div>', unsafe_allow_html=True)
            with p_cols[3]:
                st.markdown(f'<div style="{cell_s};color:#64748B;font-style:italic">{row["Ghi chú"]}</div>', unsafe_allow_html=True)

    # ═══════════════════════════════════════════════════
    # TAB 4: LƯU Ý SỬ DỤNG KẾT QUẢ
    # ═══════════════════════════════════════════════════
    with tab4:
        st.markdown(_sec("Lưu ý khi đọc và sử dụng kết quả"), unsafe_allow_html=True)

        notes = [
            (
                "Không so sánh trực tiếp với 2025",
                "#EF4444", "#FEF2F2",
                "Thang đo 2026 (1–5) khác với 2025 (1–10). Điểm Engagement 2026 = 3.8/5 "
                "<strong>không phải</strong> sụt giảm từ 8.02/10 — đây là hai thước đo độc lập. "
                "Cần quy đổi cùng thang hoặc dùng %Favorable thay vì điểm tuyệt đối để so sánh.",
            ),
            (
                "Đọc phân phối, không chỉ điểm trung bình",
                "#D97706", "#FFFBEB",
                "Với nhóm có trả lời đồng nhất cao (1A), điểm trung bình 3.9 có thể che khuất "
                "bimodal distribution (rất nhiều người 4–5 VÀ một nhóm nhỏ 1–2). "
                "Luôn xem biểu đồ phân phối Likert trước khi kết luận.",
            ),
            (
                "Lát cắt nhỏ cần biên tin cậy",
                "#3B82F6", "#EFF6FF",
                "Dashboard chỉ ẩn các lát cắt có n < 5 để tránh kết luận từ mẫu quá nhỏ. "
                "Các segment từ n=5 đến n=29 vẫn được hiển thị, nhưng nên đọc như tín hiệu định hướng "
                "và cần kiểm tra thêm trước khi ra quyết định cấp cao.",
            ),
            (
                "Nhóm 2B cần xác minh dữ liệu",
                "#8B5CF6", "#F5F3FF",
                "File 2B có bảng 'test' 223 phản hồi chưa được xác nhận nguồn gốc. "
                "Kết quả 2B trong dashboard hiện <strong>chưa bao gồm</strong> 223 phản hồi này. "
                "Cần xác nhận từ nhóm HR trước khi dùng cho quyết định cấp cao.",
            ),
            (
                "Câu hỏi mở là tam giác hóa định tính",
                "#10B981", "#F0FDF4",
                "Kết quả Likert phản ánh xu hướng tổng thể; câu hỏi mở Q34 (mong muốn thay đổi) "
                "cung cấp context định tính. Hai nguồn nên đọc <strong>song song</strong> — "
                "không nên dùng một nguồn để bác bỏ nguồn kia.",
            ),
        ]

        for title, color, bg, body in notes:
            st.markdown(f"""
            <div style="background:{bg};border:1px solid {color}33;border-left:4px solid {color};
                        border-radius:10px;padding:18px 22px;margin-bottom:16px;">
                <div style="font-size:0.88rem;font-weight:700;color:#0A1F44;margin-bottom:8px">{title}</div>
                <div style="font-size:0.84rem;color:#475569;line-height:1.7">{body}</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(f"""
        <div style="background:#0A1F44;border-radius:12px;padding:24px 28px;color:white">
            <div style="display:flex;align-items:center;gap:10px;margin-bottom:14px">
                <img src="{_AI_LOGO_B64}" style="width:20px;height:20px">
                <span style="font-size:0.9rem;font-weight:700;color:#F8FAFC">
                    Tóm tắt độ tin cậy tổng thể
                </span>
            </div>
            <p style="font-size:0.85rem;color:#94A3B8;line-height:1.75;margin:0">
                Dữ liệu EES 2026 có <strong style="color:white">độ tin cậy cao</strong> ở cấp độ tổng thể và đủ đại diện
                cho toàn bộ lực lượng lao động GHN. Các kết luận cấp công ty và cấp nhóm lớn
                (n &gt; 500) có thể được đọc trực tiếp. Lát cắt nhỏ (phòng ban, section)
                cần thêm bước xác nhận định tính. Phân tích AI trong dashboard
                <strong style="color:white">không thay thế phán đoán của HR/người quản lý</strong> —
                đây là công cụ hỗ trợ nhận diện tín hiệu, không phải kết luận cuối cùng.
            </p>
        </div>
        """, unsafe_allow_html=True)
