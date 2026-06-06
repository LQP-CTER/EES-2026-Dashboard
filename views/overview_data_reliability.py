"""
View: Độ tin cậy dữ liệu (subsection của Overview) — EES 2026
Mô tả chi tiết quy trình làm sạch dữ liệu 5 bước theo Memo "Phương pháp Làm sạch",
và số mẫu còn lại sau mỗi bước cho cả 6 nhóm khảo sát.
"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from shared.plotly_theme import apply_theme


# Brand colors (đồng bộ với Overview)
NAVY = "#0A1F44"
ORANGE = "#FF5200"
GREEN = "#10B981"
RED = "#DC2626"
BLUE = "#1D4ED8"
PURPLE = "#7C3AED"
SLATE_50 = "#F8FAFC"
SLATE_200 = "#E2E8F0"
SLATE_500 = "#64748B"


# ============================================================================
# DATA — Tổng hợp từ apply_memo_cleaning
# ============================================================================

@st.cache_data(show_spinner=False, ttl=3600)
def _compute_reliability_table():
    """
    Chạy apply_memo_cleaning cho cả 6 nhóm, tổng hợp thành DataFrame tóm tắt.
    Kết quả cache 1h — đủ nhanh vì load_group đã có Parquet cache.
    """
    from utils.data_loader import load_group

    GROUPS = [
        ('1A', 'Shipper',       12955),
        ('1B', 'Tài xế',         801),
        ('2A', 'NV Kho',         4892),
        ('2B', 'QL Tuyến đầu',   425),
        ('3A', 'NV Văn phòng',   917),
        ('3B', 'Manager HO',     109),
    ]

    rows = []
    for gid, label, raw_expected in GROUPS:
        try:
            df, n_raw = load_group(gid)
            if df is None or df.empty:
                continue
            report = df.attrs.get('memo_report', {})
            nlp = report.get('nlp', {})
            calibration = df.attrs.get('calibration_report', {})
            rows.append({
                'Nhóm': f'{gid} · {label}',
                'Mẫu thô (Supabase)': n_raw,
                'Sau Dedup': int(report.get('n_after_dedup', n_raw)),
                'Maha flag': int(report.get('flags', {}).get('maha_flag_n', 0)),
                'Contradiction': int(report.get('flags', {}).get('contradiction_n', 0)),
                'NLP tiêu cực': int(nlp.get('negative_n', 0)),
                'NLP cảnh báo': int(nlp.get('warning_signal_n', 0)),
                'Ridge AUC': calibration.get('cv_auc') if calibration.get('cv_auc') is not None else float('nan'),
                'VIF cao': len(calibration.get('high_vif', {})) if calibration.get('enabled') else 0,
                '0 bằng chứng': int(report.get('flags', {}).get('corroboration_dist', {}).get('0_evidence', 0)),
                '1 bằng chứng': int(report.get('flags', {}).get('corroboration_dist', {}).get('1_evidence', 0)),
                '2 bằng chứng': int(report.get('flags', {}).get('corroboration_dist', {}).get('2_evidence', 0)),
                'KEEP': int(report.get('tier_counts', {}).get('KEEP', 0)),
                'DOWNWEIGHT': int(report.get('tier_counts', {}).get('DOWNWEIGHT', 0)),
                'DROP': int(report.get('tier_counts', {}).get('DROP', 0)),
                'n hiệu dụng': float(report.get('n_effective', 0)),
                '% giữ': float(report.get('effective_pct', 0)),
            })
        except Exception as e:
            st.warning(f"Không tải được nhóm {gid}: {e}")
            continue
    return pd.DataFrame(rows)


# ============================================================================
# VISUALS
# ============================================================================

def _funnel_chart(df: pd.DataFrame):
    """Funnel chart: Raw → Sau Dedup → n_effective (toàn hệ thống)."""
    raw = int(df['Mẫu thô (Supabase)'].sum())
    dedup = int(df['Sau Dedup'].sum())
    eff = float(df['n hiệu dụng'].sum())

    fig = go.Figure(go.Funnel(
        y=['① Mẫu thô từ Supabase', '② Sau khử trùng lặp', '③ n hiệu dụng (sau 5 bước)'],
        x=[raw, dedup, eff],
        textposition="inside",
        textinfo="value+percent initial",
        marker=dict(color=[ORANGE, BLUE, GREEN],
                    line=dict(width=2, color='white')),
        connector=dict(line=dict(color=SLATE_200, width=2, dash='dot')),
        hovertemplate='<b>%{y}</b><br>Số mẫu: %{x:,}<br>Tỷ lệ: %{percentInitial}<extra></extra>',
    ))
    fig.update_layout(
        height=380,
        margin=dict(l=20, r=20, t=30, b=20),
        paper_bgcolor='white',
        font=dict(family='Inter, sans-serif'),
    )
    return fig


def _tier_bar_chart(df: pd.DataFrame):
    """Stacked bar chart: tier counts per group."""
    groups = df['Nhóm'].tolist()
    keep = df['KEEP'].tolist()
    downweight = df['DOWNWEIGHT'].tolist()
    drop = df['DROP'].tolist()

    fig = go.Figure()
    fig.add_trace(go.Bar(name='KEEP (giữ đầy đủ)', y=groups, x=keep,
                         orientation='h', marker_color=GREEN,
                         text=[f'{v:,}' for v in keep], textposition='inside',
                         textfont=dict(color='white', size=11)))
    fig.add_trace(go.Bar(name='DOWNWEIGHT (giảm 30%)', y=groups, x=downweight,
                         orientation='h', marker_color='#F59E0B',
                         text=[f'{v:,}' for v in downweight], textposition='inside',
                         textfont=dict(color='white', size=11)))
    fig.add_trace(go.Bar(name='DROP (loại bỏ)', y=groups, x=drop,
                         orientation='h', marker_color=RED,
                         text=[f'{v:,}' for v in drop], textposition='inside',
                         textfont=dict(color='white', size=11)))
    fig.update_layout(
        barmode='stack',
        height=380,
        margin=dict(l=20, r=20, t=30, b=20),
        paper_bgcolor='white',
        plot_bgcolor='white',
        xaxis=dict(title='Số phản hồi', gridcolor=SLATE_200, showgrid=True),
        yaxis=dict(autorange='reversed'),
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
        font=dict(family='Inter, sans-serif'),
    )
    return fig


def _corroboration_chart(df: pd.DataFrame):
    """Stacked bar: 0/1/2 evidence per group."""
    groups = df['Nhóm'].tolist()
    e0 = df['0 bằng chứng'].tolist()
    e1 = df['1 bằng chứng'].tolist()
    e2 = df['2 bằng chứng'].tolist()

    fig = go.Figure()
    fig.add_trace(go.Bar(name='0 bằng chứng (weight 0.3)', y=groups, x=e0,
                         orientation='h', marker_color=RED,
                         text=[f'{v:,}' for v in e0], textposition='inside',
                         textfont=dict(color='white', size=11)))
    fig.add_trace(go.Bar(name='1 bằng chứng (weight 0.7)', y=groups, x=e1,
                         orientation='h', marker_color='#F59E0B',
                         text=[f'{v:,}' for v in e1], textposition='inside',
                         textfont=dict(color='white', size=11)))
    fig.add_trace(go.Bar(name='2 bằng chứng (weight 1.0)', y=groups, x=e2,
                         orientation='h', marker_color=GREEN,
                         text=[f'{v:,}' for v in e2], textposition='inside',
                         textfont=dict(color='white', size=11)))
    fig.update_layout(
        barmode='stack',
        height=380,
        margin=dict(l=20, r=20, t=30, b=20),
        paper_bgcolor='white',
        plot_bgcolor='white',
        xaxis=dict(title='Số phản hồi', gridcolor=SLATE_200, showgrid=True),
        yaxis=dict(autorange='reversed'),
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
        font=dict(family='Inter, sans-serif'),
    )
    return fig


def _step_card(num: int, title: str, body_html: str, accent: str = ORANGE):
    """Một card mô tả 1 bước trong quy trình."""
    return f"""
    <div style="background:white;border:1px solid {SLATE_200};border-left:5px solid {accent};
                border-radius:12px;padding:22px 26px;margin-bottom:18px;
                box-shadow:0 1px 2px rgba(10,31,68,0.04)">
        <div style="display:flex;align-items:center;gap:12px;margin-bottom:12px">
            <div style="background:{accent};color:white;width:32px;height:32px;border-radius:50%;
                        display:flex;align-items:center;justify-content:center;
                        font-weight:900;font-size:0.95rem;flex-shrink:0">{num}</div>
            <h4 style="font-size:1.05rem;font-weight:800;color:{NAVY};margin:0">{title}</h4>
        </div>
        <div style="font-size:0.88rem;color:{SLATE_500};line-height:1.75;padding-left:44px">{body_html}</div>
    </div>
    """


# ============================================================================
# RENDER
# ============================================================================

def render():
    apply_theme()

    # ── Section header ────────────────────────────────────────────────────
    st.markdown(f"""
    <div style="background:linear-gradient(135deg,{NAVY} 0%,#1E3A8A 100%);border-radius:16px;
                padding:32px 36px;color:white;margin:48px 0 36px;position:relative;overflow:hidden">
        <div style="position:absolute;top:0;right:0;width:220px;height:220px;
                    background:radial-gradient(circle,rgba(255,82,0,0.25) 0%,transparent 70%);"></div>
        <p style="font-size:0.72rem;font-weight:800;letter-spacing:0.18em;
                  text-transform:uppercase;color:#FFB89A;margin:0 0 10px">
            EES 2026 · Phương pháp luận
        </p>
        <h2 style="font-size:2.2rem;font-weight:900;letter-spacing:-0.02em;margin:0 0 12px;line-height:1.1">
            Độ tin cậy dữ liệu
        </h2>
        <p style="font-size:0.95rem;color:#CBD5E1;line-height:1.65;margin:0;max-width:780px">
            Mỗi phản hồi được đánh giá bằng 3 chỉ số chất lượng, sau đó gán trọng số tin cậy
            dựa trên bằng chứng "người thật" — thay vì xóa cứng. Quy trình 5 bước theo
            <em>Memo Phương pháp Làm sạch Dữ liệu</em> giữ lại tối đa thông tin có giá trị
            đồng thời giảm tiếng ồn do trả lời thiếu chú tâm.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # ── Load data summary ─────────────────────────────────────────────────
    with st.spinner("Đang tính toán độ tin cậy cho 6 nhóm..."):
        summary_df = _compute_reliability_table()

    if summary_df.empty:
        st.error("Không tải được dữ liệu. Vui lòng thử lại sau.")
        return

    # ── KPI tổng ─────────────────────────────────────────────────────────
    raw_total   = int(summary_df['Mẫu thô (Supabase)'].sum())
    dedup_total = int(summary_df['Sau Dedup'].sum())
    eff_total   = float(summary_df['n hiệu dụng'].sum())
    keep_total  = int(summary_df['KEEP'].sum())
    down_total  = int(summary_df['DOWNWEIGHT'].sum())
    drop_total  = int(summary_df['DROP'].sum())
    pct_keep    = round(eff_total / max(raw_total, 1) * 100, 1)

    c1, c2, c3, c4 = st.columns(4)
    for col, (label, val, sub, color, bg) in zip(
        [c1, c2, c3, c4],
        [("Mẫu thô", f"{raw_total:,}", "từ Supabase · 6 nhóm", NAVY, SLATE_50),
         ("Sau Dedup", f"{dedup_total:,}", "khử trùng lặp", BLUE, "#EFF6FF"),
         ("n hiệu dụng", f"{eff_total:,.1f}", f"~{pct_keep}% mẫu thô", GREEN, "#F0FDF4"),
         ("Phân tầng", f"{keep_total:,} / {down_total:,} / {drop_total:,}", "KEEP / DOWNWEIGHT / DROP", PURPLE, "#F5F3FF")],
    ):
        with col:
            label_, val_, sub_, color_, bg_ = label
            st.markdown(f"""
            <div style="background:{bg_};border:1px solid {color_}33;border-radius:12px;
                        padding:18px 20px;height:120px">
                <div style="font-size:0.7rem;font-weight:700;color:{color_};text-transform:uppercase;
                            letter-spacing:0.08em;margin-bottom:8px">{label_}</div>
                <div style="font-size:1.7rem;font-weight:900;color:{NAVY};line-height:1;
                            letter-spacing:-0.02em">{val_}</div>
                <div style="font-size:0.75rem;color:{SLATE_500};margin-top:8px">{sub_}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ══════════════════════════════════════════════════════════════════════
    # 1. TRIẾT LÝ — TẠI SAO GIẢM TRỌNG SỐ THAY VÌ XÓA CỨNG
    # ══════════════════════════════════════════════════════════════════════
    st.markdown(f"""
    <h3 style="font-size:1.4rem;font-weight:800;color:{NAVY};margin:32px 0 16px;
               border-bottom:2px solid {SLATE_200};padding-bottom:10px">
        1. Triết lý làm sạch — Giảm trọng số thay vì xóa cứng
    </h3>
    """, unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f"""
        <div style="background:#FEF2F2;border:1px solid #FECACA;border-left:4px solid {RED};
                    border-radius:10px;padding:20px 24px;height:100%">
            <div style="font-size:0.78rem;font-weight:800;color:{RED};text-transform:uppercase;
                        letter-spacing:0.06em;margin-bottom:10px">Cách cũ · Xóa cứng</div>
            <p style="font-size:0.88rem;color:#475569;line-height:1.7;margin:0">
                Nếu dùng <strong>1 tiêu chí đơn lẻ</strong> (ví dụ: straight-line) để xóa
                toàn bộ phản hồi, ta vứt mất <strong>thông tin quý từ các phản hồi thẳng hàng
                nhưng vẫn có câu hỏi mở chất lượng</strong>. Lực lượng lao động trực tiếp
                (1A, 2A) trả lời nhanh và đồng thuận là <em>đặc trưng tâm lý nhóm</em>,
                không phải dữ liệu rác.
            </p>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
        <div style="background:#F0FDF4;border:1px solid #BBF7D0;border-left:4px solid {GREEN};
                    border-radius:10px;padding:20px 24px;height:100%">
            <div style="font-size:0.78rem;font-weight:800;color:{GREEN};text-transform:uppercase;
                        letter-spacing:0.06em;margin-bottom:10px">Cách Memo · Trọng số liên tục</div>
            <p style="font-size:0.88rem;color:#475569;line-height:1.7;margin:0">
                Mỗi phản hồi được gán <strong>effective_weight từ 0.3 → 1.0</strong> dựa
                trên <em>3 chỉ số chất lượng + 2 bằng chứng "người thật"</em>. Các con số
                trong dashboard là <strong>trung bình có trọng số</strong>, không phải
                trung bình cộng. Giữ lại thông tin định hướng từ mọi phản hồi có giá trị.
            </p>
        </div>
        """, unsafe_allow_html=True)

    # ══════════════════════════════════════════════════════════════════════
    # 2. QUY TRÌNH 5 BƯỚC
    # ══════════════════════════════════════════════════════════════════════
    st.markdown(f"""
    <h3 style="font-size:1.4rem;font-weight:800;color:{NAVY};margin:48px 0 16px;
               border-bottom:2px solid {SLATE_200};padding-bottom:10px">
        2. Quy trình 5 bước theo Memo
    </h3>
    """, unsafe_allow_html=True)

    st.markdown(_step_card(
        1, "Khử trùng lặp (Deduplication)",
        f"""Phát hiện các bản ghi <em>trùng ID nhân viên</em> (1A, 1B) hoặc <em>trùng chữ ký nội dung</em>
        (2A, 2B, 3A, 3B — dựa trên Likert + eNPS + open-text ≥25 ký tự).
        Hai người viết trùng nguyên văn 1 câu dài → gần như chắc chắn 1 người nộp 2 lần.
        Chỉ giữ bản đầu tiên, loại bỏ các bản sau.""",
        accent=BLUE
    ), unsafe_allow_html=True)

    st.markdown(_step_card(
        2, "Ba chỉ số chất lượng (phát hiện trả lời thiếu chú tâm)",
        f"""<ul style="margin:0;padding-left:18px">
            <li><strong>Longstring</strong> — độ dài chuỗi đáp án giống nhau liên tiếp dài nhất. Bắt thẳng hàng toàn phần lẫn thẳng hàng từng phần.</li>
            <li><strong>Khoảng cách Mahalanobis</strong> (đa biến, có co rút Ledoit-Wolf, threshold χ² = 50 ~ p&lt;0.0001, df=21) — bắt người trả lời loạn/mâu thuẫn <em>đa chiều</em>. <strong>Lưu ý:</strong> 1A có 55% flatline nên covariance chỉ fit trên diverse rows để tránh phạt oan.</li>
            <li><strong>Mâu thuẫn eNPS ↔ Likert</strong> — Likert ≥ 4.5 (rất hài lòng) NHƯNG eNPS ≤ 6 (không promoter) → dấu hiệu trả lời không chú tâm.</li>
        </ul>""",
        accent="#F59E0B"
    ), unsafe_allow_html=True)

    st.markdown(_step_card(
        3, "Corroboration — Đếm bằng chứng 'người thật'",
        f"""Mỗi phản hồi được đếm <strong>0, 1 hoặc 2 bằng chứng</strong>:
        <ul style="margin:6px 0 0;padding-left:18px">
            <li><strong>+1</strong> nếu có ít nhất 1 câu open-text có nội dung ý nghĩa (không phải "Không", "ko", "không có ý kiến"... — đã được lọc tự động).</li>
            <li><strong>+1</strong> nếu eNPS nhất quán với Likert (Likert ≥ 4 ↔ eNPS ≥ 9; Likert ≤ 2 ↔ eNPS ≤ 6; Likert 3–4 ↔ eNPS 7–8).</li>
        </ul>
        Đây là bước "giải cứu" — phản hồi straight-line nhưng có text thật vẫn được đánh giá cao.""",
        accent=PURPLE
    ), unsafe_allow_html=True)

    st.markdown(_step_card(
        4, "Gán effective_weight (0.3 / 0.7 / 1.0)",
        f"""Trọng số tin cậy được gán theo số bằng chứng:
        <ul style="margin:6px 0 0;padding-left:18px">
            <li><strong>2 bằng chứng</strong> → weight = <strong>1.0</strong> (đầy đủ, có cả text lẫn eNPS nhất quán)</li>
            <li><strong>1 bằng chứng</strong> → weight = <strong>0.7</strong> (có 1 trong 2 dấu hiệu)</li>
            <li><strong>0 bằng chứng</strong> → weight = <strong>0.3</strong> (chỉ tham chiếu, không đóng góp vào trung bình)</li>
        </ul>
        Riêng người <strong>trung lập toàn bộ</strong> (mức 3 ở mọi câu Likert) → áp trần ×0.5, vì trung lập không mang thông tin định hướng.""",
        accent=GREEN
    ), unsafe_allow_html=True)

    st.markdown(_step_card(
        5, "Phân tầng tier_v2: KEEP / DOWNWEIGHT / DROP",
        f"""Ba tầng dựa trên effective_weight:
        <ul style="margin:6px 0 0;padding-left:18px">
            <li><span style="background:{GREEN};color:white;padding:2px 8px;border-radius:4px;font-weight:700;font-size:0.78rem">KEEP</span> — weight ≥ 0.7 (giữ đầy đủ, đa số phản hồi)</li>
            <li><span style="background:#F59E0B;color:white;padding:2px 8px;border-radius:4px;font-weight:700;font-size:0.78rem">DOWNWEIGHT</span> — weight 0.5–0.7 (giữ nhưng giảm 30% đóng góp)</li>
            <li><span style="background:{RED};color:white;padding:2px 8px;border-radius:4px;font-weight:700;font-size:0.78rem">DROP</span> — weight &lt; 0.5 (không bằng chứng nào — chỉ tham chiếu)</li>
        </ul>
        Trong dashboard, <strong>trung bình các chỉ số</strong> được tính bằng
        <code>Σ(value × effective_weight) / Σ(effective_weight)</code>.""",
        accent=RED
    ), unsafe_allow_html=True)

    # ══════════════════════════════════════════════════════════════════════
    # 3. FUNNEL — MẪU THÔ → MẪU CÒN LẠI
    # ══════════════════════════════════════════════════════════════════════
    st.markdown(f"""
    <h3 style="font-size:1.4rem;font-weight:800;color:{NAVY};margin:48px 0 16px;
               border-bottom:2px solid {SLATE_200};padding-bottom:10px">
        3. Số mẫu còn lại (toàn hệ thống)
    </h3>
    """, unsafe_allow_html=True)

    st.plotly_chart(_funnel_chart(summary_df), width='stretch')

    st.markdown(f"""
    <p style="font-size:0.82rem;color:{SLATE_500};line-height:1.7;margin-top:8px;font-style:italic">
        <strong>Mẫu thô</strong> = số record lấy từ Supabase (19.886 dòng — gồm 6 nhóm).
        <strong>Sau Dedup</strong> = đã khử trùng lặp (một số nhân viên nộp 2 lần).
        <strong>n hiệu dụng</strong> = tổng trọng số tin cậy — phản ánh lượng thông tin thực sự
        dùng được, không phải số đầu đếm thô. Tỷ lệ ~75% nghĩa là khoảng 1/4 phản hồi bị giảm
        trọng số đáng kể do thiếu bằng chứng "người thật".
    </p>
    """, unsafe_allow_html=True)

    # ══════════════════════════════════════════════════════════════════════
    # 4. BẢNG TỔNG HỢP 6 NHÓM
    # ══════════════════════════════════════════════════════════════════════
    st.markdown(f"""
    <h3 style="font-size:1.4rem;font-weight:800;color:{NAVY};margin:48px 0 16px;
               border-bottom:2px solid {SLATE_200};padding-bottom:10px">
        4. Bảng tổng hợp theo 6 nhóm khảo sát
    </h3>
    """, unsafe_allow_html=True)

    st.dataframe(
        summary_df.style.format({
            'Mẫu thô (Supabase)': '{:,}',
            'Sau Dedup': '{:,}',
            'Maha flag': '{:,}',
            'Contradiction': '{:,}',
            'NLP tiêu cực': '{:,}',
            'NLP cảnh báo': '{:,}',
            'Ridge AUC': '{:.3f}',
            'VIF cao': '{:,}',
            '0 bằng chứng': '{:,}',
            '1 bằng chứng': '{:,}',
            '2 bằng chứng': '{:,}',
            'KEEP': '{:,}',
            'DOWNWEIGHT': '{:,}',
            'DROP': '{:,}',
            'n hiệu dụng': '{:,.1f}',
            '% giữ': '{:.1f}%',
        }),
        width='stretch',
        height=320,
    )

    # ══════════════════════════════════════════════════════════════════════
    # 5. CHART — PHÂN TẦNG
    # ══════════════════════════════════════════════════════════════════════
    st.markdown(f"""
    <h3 style="font-size:1.4rem;font-weight:800;color:{NAVY};margin:48px 0 16px;
               border-bottom:2px solid {SLATE_200};padding-bottom:10px">
        5. Phân tầng tier_v2 theo nhóm
    </h3>
    """, unsafe_allow_html=True)

    st.plotly_chart(_tier_bar_chart(summary_df), width='stretch')

    st.markdown(f"""
    <p style="font-size:0.82rem;color:{SLATE_500};line-height:1.7;margin-top:8px;font-style:italic">
        <strong>Nhận xét nổi bật:</strong>
        Nhóm <strong>1A · Shipper</strong> có số lượng DROP lớn nhất (2.531 bản — tương ứng 19.5% mẫu thô).
        Đây là nhóm straight-line cao do đặc thù trả lời nhanh của lực lượng lao động trực tiếp,
        <em>không phải dữ liệu rác</em> — vẫn được giữ làm tham chiếu nhưng giảm đóng góp vào trung bình.
    </p>
    """, unsafe_allow_html=True)

    # ══════════════════════════════════════════════════════════════════════
    # 6. CHART — CORROBORATION
    # ══════════════════════════════════════════════════════════════════════
    st.markdown(f"""
    <h3 style="font-size:1.4rem;font-weight:800;color:{NAVY};margin:48px 0 16px;
               border-bottom:2px solid {SLATE_200};padding-bottom:10px">
        6. Phân bố bằng chứng 'người thật' theo nhóm
    </h3>
    """, unsafe_allow_html=True)

    st.plotly_chart(_corroboration_chart(summary_df), width='stretch')

    st.markdown(f"""
    <p style="font-size:0.82rem;color:{SLATE_500};line-height:1.7;margin-top:8px;font-style:italic">
        <strong>Cách đọc:</strong> Mỗi cột thể hiện tổng số phản hồi của một nhóm, chia theo
        số bằng chứng "người thật" tìm được. Nhóm nào có tỷ lệ <span style="color:{GREEN};font-weight:700">2 bằng chứng</span>
        cao (cột xanh) thì dữ liệu càng đáng tin cậy — vì vừa có open-text chất lượng, vừa eNPS nhất quán với Likert.
        Nhóm 1A vẫn có 9.844 phản hồi (76% mẫu thô) đạt 2 bằng chứng — kết quả rất tích cực.
    </p>
    """, unsafe_allow_html=True)

    # ══════════════════════════════════════════════════════════════════════
    # 7. LƯU Ý SỬ DỤNG
    # ══════════════════════════════════════════════════════════════════════
    st.markdown(f"""
    <h3 style="font-size:1.4rem;font-weight:800;color:{NAVY};margin:48px 0 16px;
               border-bottom:2px solid {SLATE_200};padding-bottom:10px">
        7. Lưu ý khi đọc kết quả
    </h3>
    """, unsafe_allow_html=True)

    notes = [
        ("Các con số trong dashboard là trung bình có trọng số", NAVY, SLATE_50,
         "Khi tính EI, MEI, burnout, JSI... dashboard dùng <code>Σ(value × effective_weight) / Σ(effective_weight)</code>. "
         "Con số này phản ánh lượng thông tin thực sự, không phải trung bình cộng đơn thuần."),
        ("n hiệu dụng ≠ số lượng phản hồi", BLUE, "#EFF6FF",
         "Hai con số có thể khác nhau đáng kể. Ví dụ nhóm 1A: 12.955 phản hồi nhưng n hiệu dụng = 9.142 — "
         "nghĩa là dashboard <em>đang lắng nghe tương đương</em> tiếng nói của ~9.100 người."),
        ("Cronbach α = 0.94–0.99 (rất cao)", "#F59E0B", "#FFFBEB",
         "Hệ số quá cao có thể phản ánh hiệu ứng halo (đồng ý/toàn bộ) chứ không hẳn nhất quán tâm lý. "
         "Báo cáo <strong>luôn đính kèm phân phối điểm</strong> và <strong>phân tích open-text</strong> để tam giác hóa."),
        ("Lát cắt nhỏ cần biên tin cậy", PURPLE, "#F5F3FF",
         "Dashboard chỉ ẩn lát cắt có n &lt; 5 để tránh kết luận từ mẫu quá nhỏ. "
         "Segment từ n=5 đến n=29 vẫn được hiển thị, nhưng nên đọc như tín hiệu định hướng "
         "và cần kiểm tra thêm trước khi ra quyết định cấp cao."),
    ]
    for title, color, bg, body in notes:
        st.markdown(f"""
        <div style="background:{bg};border:1px solid {color}33;border-left:4px solid {color};
                    border-radius:10px;padding:16px 22px;margin-bottom:12px">
            <div style="font-size:0.88rem;font-weight:700;color:{NAVY};margin-bottom:6px">{title}</div>
            <div style="font-size:0.84rem;color:#475569;line-height:1.7">{body}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
