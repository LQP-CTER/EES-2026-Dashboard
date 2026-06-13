import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from textwrap import dedent
from utils.data_loader import compute_kpis, PILLAR_LABELS
from shared.plotly_theme import fig_card, apply_theme, COLORS
from utils.benchmark_2025 import get_company_benchmark_2025, get_external_benchmarks
from utils.ai_generator import render_ai_insight_card, render_ai_insight_card_dual
from views.view_i_data_trust import DEEPDIVE_QUALITY_TOTALS
from shared.codebook import get_codebook, get_question_label

MIN_DEPARTMENT_N = 3  # Chỉ hiển thị phòng ban có N > 2
MIN_ORG_SEGMENT_N = 5


def _render_benchmark_executive_summary(
    total_ei,
    total_enps,
    total_participants,
    total_cleaned,
    total_dropped,
):
    """Executive Summary nhẹ, chỉ dùng số chính thức và mốc đối sánh trực tiếp."""
    external = get_external_benchmarks()
    ei_benchmark = external["ei_logistics"]["value"]
    enps_benchmark = external["enps_transportation"]["value"]
    ei_gap = total_ei - ei_benchmark
    enps_gap = total_enps - enps_benchmark
    retained_rate = (total_cleaned / total_participants * 100) if total_participants else 0.0

    ei_read = (
        f"cao hơn {abs(ei_gap):.1f} điểm"
        if ei_gap >= 0
        else f"thấp hơn {abs(ei_gap):.1f} điểm"
    )
    enps_read = (
        f"cao hơn {abs(enps_gap):.0f} điểm"
        if enps_gap >= 0
        else f"thấp hơn {abs(enps_gap):.0f} điểm"
    )

    st.html(dedent(f"""
    <section class="benchmark-summary">
        <div class="benchmark-summary-head">
            <div>
                <div class="benchmark-summary-kicker">EXECUTIVE SUMMARY · ĐỐI SÁNH</div>
                <h3>Tóm tắt vị thế EES 2026</h3>
                <p>Đọc nhanh vị thế gắn kết của GHN so với mốc tham chiếu ngành và quy mô dữ liệu chính thức đang được sử dụng.</p>
            </div>
            <div class="benchmark-summary-status">Dữ liệu đã đồng bộ</div>
        </div>

        <div class="benchmark-summary-grid">
            <article class="benchmark-summary-card benchmark-summary-card--blue">
                <span>EI - Chỉ số gắn kết</span>
                <strong>{total_ei:.1f}</strong>
                <p>{ei_read} so với mốc logistics {ei_benchmark:.0f}.</p>
            </article>
            <article class="benchmark-summary-card benchmark-summary-card--orange">
                <span>eNPS - Mức sẵn sàng giới thiệu</span>
                <strong>{total_enps:+.0f}</strong>
                <p>{enps_read} so với mốc vận tải {enps_benchmark:+.0f}.</p>
            </article>
            <article class="benchmark-summary-card benchmark-summary-card--green">
                <span>Mẫu thu thập</span>
                <strong>{total_participants:,}</strong>
                <p>Nguồn phản hồi chính thức đã truyền thông.</p>
            </article>
            <article class="benchmark-summary-card benchmark-summary-card--navy">
                <span>Mẫu phân tích</span>
                <strong>{total_cleaned:,}</strong>
                <p>Giữ lại {retained_rate:.1f}% sau khi loại {total_dropped:,} phản hồi.</p>
            </article>
        </div>

        <div class="benchmark-summary-reading">
            <div>
                <span>Vị thế hiện tại</span>
                <p>EI đang cao hơn mốc ngành logistics, trong khi eNPS ở sát mốc vận tải. Khoảng cách này cho thấy trải nghiệm nội bộ nhìn chung tích cực nhưng mức sẵn sàng giới thiệu GHN vẫn còn dư địa cải thiện.</p>
            </div>
            <div>
                <span>Ưu tiên điều hành</span>
                <p>Không nên chỉ nhìn điểm tổng. Cần tiếp tục đọc chênh lệch giữa Khối, Phòng ban và Section để xác định nơi điểm gắn kết chưa chuyển thành niềm tin và ý định gắn bó.</p>
            </div>
            <div>
                <span>Nguyên tắc sử dụng</span>
                <p>Executive Summary dùng cùng một base với dashboard: {total_participants:,} mẫu thu thập và {total_cleaned:,} mẫu phân tích. Không sử dụng các base cũ từ phiên bản Benchmark trước.</p>
            </div>
        </div>
    </section>
    """))
UNKNOWN_ORG_VALUE = "Chưa xác định"

# Tập hợp các giá trị "rác" xuất phát từ pipeline cũ hoặc HRIS không xác định được.
# _normalize_org_columns sẽ thay tất cả thành None để groupby tự bỏ qua.
_ORG_BAD_VALUES = {
    "không xác định", "chưa xác định", "khong xac dinh", "chua xac dinh",
    "khác", "khac", "nan", "none", "null", "", "n/a", "na",
}


def _normalize_org_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Normalize org columns: fill missing/legacy-bad values with None so
    groupby(dropna=True) silently skips them instead of surfacing a spurious
    'Không xác định' / 'Khác' category in every chart."""
    df = df.copy()
    fallback_map = {
        "division": ["division", "Khối", "Khoi", "Division", "Khối/Phòng ban", "Khối / Phòng ban"],
        "department": ["department", "Phòng ban", "Phong ban", "Department", "Bộ phận", "Bo phan"],
        "section": ["section", "Section", "Vùng", "Vung", "Khu vực", "Khu vuc"],
    }
    for target, candidates in fallback_map.items():
        if target not in df.columns:
            source = next((c for c in candidates if c in df.columns), None)
            if source is not None:
                df[target] = df[source]
        if target in df.columns:
            clean = df[target].astype("string").str.replace(r"\s+", " ", regex=True).str.strip()
            # Replace null, empty, legacy bad strings → None (pandas NA)
            bad_mask = clean.isna() | clean.eq("") | clean.str.lower().isin(_ORG_BAD_VALUES)
            df[target] = clean.mask(bad_mask, other=pd.NA)
    return df


def _fmt_num(value) -> str:
    return f"{int(value):,}"


def _pct(numerator, denominator) -> float:
    return round((numerator / denominator) * 100, 1) if denominator else 0.0


def _build_department_question_diagnostics(df_department: pd.DataFrame) -> pd.DataFrame:
    """Rank weak Likert questions while preserving each survey group's wording."""
    rows = []
    if "_survey_group" not in df_department.columns:
        return pd.DataFrame()

    for group_id, df_group in df_department.groupby("_survey_group", dropna=True):
        codebook = get_codebook(str(group_id))
        if not codebook:
            continue
        for question_id, meta in codebook.items():
            if meta.get("loại") != "likert" or question_id not in df_group.columns:
                continue
            values = pd.to_numeric(df_group[question_id], errors="coerce").dropna()
            if len(values) < MIN_DEPARTMENT_N:
                continue
            rows.append(
                {
                    "Nhóm": str(group_id),
                    "Câu hỏi": question_id,
                    "N": len(values),
                    "Nội dung": get_question_label(str(group_id), question_id),
                    "Trụ cột": PILLAR_LABELS.get(meta.get("trụ_cột"), meta.get("trụ_cột", "N/A")),
                    "Điểm TB": round(float(values.mean()), 2),
                    "Tích cực (%)": round(float((values >= 4).mean() * 100), 1),
                    "Tiêu cực (%)": round(float((values <= 2).mean() * 100), 1),
                }
            )

    if not rows:
        return pd.DataFrame()
    return pd.DataFrame(rows).sort_values(
        ["Điểm TB", "Tiêu cực (%)", "N"],
        ascending=[True, False, False],
    ).reset_index(drop=True)


@st.fragment
def _render_org_deep_dive(df_total: pd.DataFrame):
    """Render an evidence-led diagnosis by division, department, or section."""
    if not any(col in df_total.columns for col in ("division", "department", "section")):
        return

    st.markdown(
        """
        <div style="margin:34px 0 14px;padding-top:24px;border-top:1px solid #E2E8F0;">
            <div style="font-size:.72rem;font-weight:850;color:#FF5200;text-transform:uppercase;letter-spacing:.14em;margin-bottom:6px;">
                Deep Dive Đơn Vị
            </div>
            <div style="font-size:1.35rem;font-weight:900;color:#0A1F44;letter-spacing:-.02em;">
                Chẩn đoán theo Khối, Phòng ban và Section
            </div>
            <div style="font-size:.84rem;color:#64748B;line-height:1.6;margin-top:6px;">
                Chọn tuần tự cấp tổ chức để đọc đồng thời KPI, trụ cột, câu hỏi yếu và thâm niên.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col_div, col_dept, col_sec = st.columns(3)
    selected_division = None
    selected_department = None
    selected_section = None

    def _org_options(frame: pd.DataFrame, column: str) -> list[str]:
        if column not in frame.columns:
            return []
        valid = frame[frame[column].notna()].copy()
        valid = valid[
            ~valid[column].astype(str).str.strip().str.lower().isin(_ORG_BAD_VALUES)
        ]
        return sorted(
            str(value)
            for value, group in valid.groupby(column, dropna=True)
            if len(group) >= MIN_DEPARTMENT_N
        )

    df_selection = df_total
    division_options = _org_options(df_total, "division")
    if division_options:
        with col_div:
            selected_division = st.selectbox(
                "Khối",
                options=[None] + division_options,
                format_func=lambda x: "— Chọn Khối —" if x is None else x,
                key="company_deep_dive_division",
            )
        if selected_division:
            df_selection = df_selection[df_selection["division"].astype(str) == selected_division]

    department_enabled = bool(selected_division) or not division_options
    department_options = _org_options(df_selection, "department") if department_enabled else []
    with col_dept:
        selected_department = st.selectbox(
            "Phòng ban",
            options=[None] + department_options,
            format_func=lambda x: "— Tất cả phòng ban —" if x is None else x,
            key=f"company_deep_dive_department_{selected_division or 'all'}",
            disabled=not department_enabled,
        )
    if selected_department:
        df_selection = df_selection[df_selection["department"].astype(str) == selected_department]

    section_enabled = bool(selected_department) or (department_enabled and not department_options)
    section_options = _org_options(df_selection, "section") if section_enabled else []
    with col_sec:
        selected_section = st.selectbox(
            "Section",
            options=[None] + section_options,
            format_func=lambda x: "— Tất cả Section —" if x is None else x,
            key=(
                f"company_deep_dive_section_"
                f"{selected_division or 'all'}_{selected_department or 'all'}"
            ),
            disabled=not section_enabled,
        )
    if selected_section:
        df_selection = df_selection[df_selection["section"].astype(str) == selected_section]

    if not (selected_division or selected_department or selected_section):
        first_level = "Khối" if division_options else "Phòng ban" if department_options else "Section"
        st.caption(f"Chọn {first_level}, sau đó có thể thu hẹp tiếp theo cấp tổ chức bên dưới.")
        return

    df_department = df_selection.copy()
    selected_unit = selected_section or selected_department or selected_division
    selected_level = "Section" if selected_section else "Phòng ban" if selected_department else "Khối"
    if len(df_department) < MIN_DEPARTMENT_N:
        st.info(f"{selected_level} này không đủ tối thiểu 3 mẫu để phân tích.")
        return

    kpis = compute_kpis(df_department)
    company_kpis = compute_kpis(df_total)
    ei_gap = round(kpis["ei_mean"] - company_kpis["ei_mean"], 1)
    enps_gap = round(kpis["enps_score"] - company_kpis["enps_score"], 0)

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Số mẫu", f"{kpis['n']:,}")
    c2.metric("EI", f"{kpis['ei_mean']:.1f}%", delta=f"{ei_gap:+.1f} so với GHN")
    c3.metric("eNPS", f"{kpis['enps_score']:+.0f}", delta=f"{enps_gap:+.0f} so với GHN")
    c4.metric("Rủi ro nghỉ việc", f"{kpis['intent_pct_low']:.1f}%")
    c5.metric("MEI", f"{kpis.get('mei_avg', 0):.1f}%")

    pillar_rows = []
    for pillar_id, pillar_label in PILLAR_LABELS.items():
        col = f"{pillar_id}_pct"
        if col not in df_department.columns:
            continue
        dept_values = pd.to_numeric(df_department[col], errors="coerce").dropna()
        company_values = pd.to_numeric(df_total[col], errors="coerce").dropna()
        if dept_values.empty:
            continue
        dept_score = float(dept_values.mean())
        company_score = float(company_values.mean()) if not company_values.empty else dept_score
        pillar_rows.append(
            {
                "Trụ cột": pillar_label,
                "Điểm phòng ban": round(dept_score, 1),
                "GHN": round(company_score, 1),
                "Chênh lệch": round(dept_score - company_score, 1),
            }
        )
    df_pillars = pd.DataFrame(pillar_rows)

    col_pillar, col_segment = st.columns([1.15, 0.85])
    with col_pillar:
        if not df_pillars.empty:
            df_pillars_plot = df_pillars.sort_values("Điểm phòng ban", ascending=True)
            fig_pillar = go.Figure()
            fig_pillar.add_trace(
                go.Bar(
                    y=df_pillars_plot["Trụ cột"],
                    x=df_pillars_plot["Điểm phòng ban"],
                    orientation="h",
                    name=selected_unit,
                    marker_color=[
                        "#10B981" if score >= 75 else "#F59E0B" if score >= 65 else "#EF4444"
                        for score in df_pillars_plot["Điểm phòng ban"]
                    ],
                    text=[f"{score:.1f}%" for score in df_pillars_plot["Điểm phòng ban"]],
                    textposition="outside",
                )
            )
            fig_pillar.add_trace(
                go.Scatter(
                    y=df_pillars_plot["Trụ cột"],
                    x=df_pillars_plot["GHN"],
                    mode="markers",
                    name="GHN",
                    marker=dict(color="#0A1F44", size=9, symbol="diamond"),
                )
            )
            fig_pillar = fig_card(
                fig_pillar,
                "Hồ sơ 5 Trụ Cột",
                f"Thanh màu là {selected_level.lower()}, điểm kim cương là toàn GHN",
            )
            fig_pillar.update_layout(
                xaxis=dict(range=[0, 105]),
                yaxis=dict(autorange="reversed"),
                legend=dict(orientation="h", y=1.08),
                height=390,
            )
            st.plotly_chart(fig_pillar, width="stretch", key="department_deep_dive_pillars")
        else:
            st.info("Đơn vị chưa có dữ liệu tổng hợp 5 trụ cột.")

    with col_segment:
        section_rows = []
        if "section" in df_department.columns:
            for section, df_section in df_department.groupby("section", dropna=True):
                if len(df_section) < MIN_DEPARTMENT_N:
                    continue
                section_kpis = compute_kpis(df_section)
                section_rows.append(
                    {
                        "Section": section,
                        "N": section_kpis["n"],
                        "EI (%)": round(section_kpis["ei_mean"], 1),
                        "eNPS": round(section_kpis["enps_score"], 0),
                    }
                )
        df_sections = pd.DataFrame(section_rows)
        if not df_sections.empty:
            df_sections = df_sections.sort_values("EI (%)", ascending=True)
            fig_section = go.Figure(
                go.Bar(
                    y=df_sections["Section"],
                    x=df_sections["EI (%)"],
                    orientation="h",
                    marker_color=[
                        "#10B981" if score >= 75 else "#F59E0B" if score >= 65 else "#EF4444"
                        for score in df_sections["EI (%)"]
                    ],
                    text=[f"{score:.1f}% · n={n}" for score, n in zip(df_sections["EI (%)"], df_sections["N"])],
                    textposition="inside",
                )
            )
            fig_section = fig_card(fig_section, "Điểm nóng theo Section", "Chỉ hiển thị section có N > 2")
            fig_section.update_layout(
                xaxis=dict(range=[0, 100]),
                yaxis=dict(autorange="reversed"),
                height=max(330, len(df_sections) * 30 + 90),
            )
            st.plotly_chart(fig_section, width="stretch", key="department_deep_dive_sections")
        else:
            st.info("Không có Section trực thuộc nào đạt N > 2.")

    question_diagnostics = _build_department_question_diagnostics(df_department)
    st.markdown("##### Câu hỏi đang kéo trải nghiệm xuống")
    if not question_diagnostics.empty:
        weakest_questions = question_diagnostics.head(8).copy()
        st.dataframe(
            weakest_questions,
            width="stretch",
            hide_index=True,
            column_config={
                "Điểm TB": st.column_config.NumberColumn(format="%.2f"),
                "Tích cực (%)": st.column_config.NumberColumn(format="%.1f%%"),
                "Tiêu cực (%)": st.column_config.NumberColumn(format="%.1f%%"),
            },
        )
    else:
        weakest_questions = pd.DataFrame()
        st.info("Chưa có đủ dữ liệu câu hỏi để xếp hạng cho đơn vị này.")

    tenure_rows = []
    if "Q5" in df_department.columns:
        for tenure, df_tenure in df_department.groupby("Q5", dropna=True):
            if len(df_tenure) < MIN_DEPARTMENT_N:
                continue
            tenure_kpis = compute_kpis(df_tenure)
            tenure_rows.append(
                {
                    "Thâm niên": tenure,
                    "N": tenure_kpis["n"],
                    "EI (%)": round(tenure_kpis["ei_mean"], 1),
                    "eNPS": round(tenure_kpis["enps_score"], 0),
                    "Rủi ro nghỉ việc (%)": round(tenure_kpis["intent_pct_low"], 1),
                }
            )
    df_tenure = pd.DataFrame(tenure_rows)
    if not df_tenure.empty:
        df_tenure = df_tenure.sort_values("EI (%)", ascending=True)
        fig_tenure = go.Figure(
            go.Bar(
                y=df_tenure["Thâm niên"],
                x=df_tenure["EI (%)"],
                orientation="h",
                marker_color=[
                    "#10B981" if score >= 75 else "#F59E0B" if score >= 65 else "#EF4444"
                    for score in df_tenure["EI (%)"]
                ],
                text=[
                    f"{ei:.1f}% · eNPS {enps:+.0f} · n={n}"
                    for ei, enps, n in zip(df_tenure["EI (%)"], df_tenure["eNPS"], df_tenure["N"])
                ],
                textposition="inside",
            )
        )
        fig_tenure = fig_card(
            fig_tenure,
            "Lát cắt Thâm niên",
            "Tìm nhóm thâm niên đang kéo trải nghiệm của đơn vị xuống",
        )
        fig_tenure.update_layout(
            xaxis=dict(range=[0, 100]),
            yaxis=dict(autorange="reversed"),
            height=max(340, len(df_tenure) * 34 + 90),
        )
        st.plotly_chart(fig_tenure, width="stretch", key="department_deep_dive_tenure")

    weakest_pillar = None
    strongest_pillar = None
    if not df_pillars.empty:
        weakest_pillar = df_pillars.loc[df_pillars["Điểm phòng ban"].idxmin()].to_dict()
        strongest_pillar = df_pillars.loc[df_pillars["Điểm phòng ban"].idxmax()].to_dict()

    weakest_question_records = []
    if not weakest_questions.empty:
        weakest_question_records = weakest_questions.head(3)[
            ["Nhóm", "Câu hỏi", "Nội dung", "Trụ cột", "N", "Điểm TB", "Tích cực (%)", "Tiêu cực (%)"]
        ].to_dict("records")

    ai_data = {
        "Cấp đơn vị": selected_level,
        "Đơn vị": selected_unit,
        "Khối": selected_division,
        "Phòng ban": selected_department,
        "Section": selected_section,
        "N": int(kpis["n"]),
        "EI": round(kpis["ei_mean"], 1),
        "Chênh lệch EI so với GHN": ei_gap,
        "eNPS": round(kpis["enps_score"], 0),
        "Chênh lệch eNPS so với GHN": enps_gap,
        "Rủi ro nghỉ việc": round(kpis["intent_pct_low"], 1),
        "MEI": round(kpis.get("mei_avg", 0), 1),
        "Trụ cột yếu nhất": weakest_pillar,
        "Trụ cột mạnh nhất": strongest_pillar,
        "Ba câu hỏi yếu nhất": weakest_question_records,
        "Section thấp nhất": (
            df_sections.head(3).to_dict("records") if not df_sections.empty else []
        ),
        "Nhóm thâm niên thấp nhất": (
            df_tenure.head(3).to_dict("records") if not df_tenure.empty else []
        ),
    }
    prompt = (
        "Viết chẩn đoán Deep Dive cho đơn vị tổ chức này theo phong cách Master Report. "
        "Mở bằng một tên chẩn đoán ngắn phản ánh vấn đề nổi bật nhất. "
        "Phân tích lần lượt hiện tượng, các bằng chứng đang kéo EI/eNPS xuống, nguyên nhân có khả năng "
        "từ trụ cột, câu hỏi hoặc section, và hai hành động ưu tiên có thể triển khai. "
        "Chỉ sử dụng dữ liệu JSON được cung cấp. Nếu dữ liệu chỉ thể hiện tương quan hoặc điểm thấp, "
        "phải dùng cách diễn đạt 'tín hiệu', 'có khả năng' hoặc 'cần kiểm chứng', không khẳng định quan hệ nhân quả."
    )
    render_ai_insight_card(
        f"AI Deep Dive {selected_level} · {selected_unit}",
        ai_data,
        prompt,
        badge="Department Diagnosis",
        custom_style="margin-top:20px;",
    )


def _render_data_processing_section(
    headcount,
    raw,
    dropped,
    cleaned,
    all_data,
):
    cards = [
        ("HRIS / Headcount", headcount, "Nền nhân sự dùng để đối chiếu độ phủ", "#0A1F44"),
        ("Mẫu thu thập", raw, f"{_pct(raw, headcount):.1f}% / tổng nhân sự HRIS", "#1D4ED8"),
        ("Mẫu bị loại", dropped, f"{_pct(dropped, raw):.1f}% mẫu không đưa vào phân tích", "#FF5200"),
        ("Mẫu sau loại", cleaned, f"{_pct(cleaned, headcount):.1f}% / HRIS dùng cho dashboard", "#10B981"),
    ]
    card_html = "\n".join(
        f"""
        <div class="ghn-process-card" style="--accent:{accent}">
            <div class="ghn-process-label">{label}</div>
            <div class="ghn-process-value">{_fmt_num(value)}</div>
            <div class="ghn-process-note">{note}</div>
        </div>
        """
        for label, value, note, accent in cards
    )

    st.markdown(
        """
        <style>
        .ghn-process-wrap {
            border-radius:24px;
            padding:24px;
            margin:0 0 26px;
            background:
                radial-gradient(circle at 12% 0%, rgba(255,82,0,.10), transparent 30%),
                linear-gradient(135deg, #FFFFFF 0%, #F8FAFC 62%, #EEF6FF 100%);
            border:1px solid #E2E8F0;
            box-shadow:0 18px 44px rgba(10,31,68,.08);
        }
        .ghn-process-head {
            display:flex;
            justify-content:space-between;
            gap:18px;
            align-items:flex-end;
            flex-wrap:wrap;
            margin-bottom:18px;
        }
        .ghn-process-kicker {
            color:#FF5200;
            font-size:.72rem;
            font-weight:850;
            text-transform:uppercase;
            letter-spacing:.14em;
            margin-bottom:6px;
        }
        .ghn-process-title {
            color:#0A1F44;
            font-size:1.35rem;
            font-weight:900;
            letter-spacing:-.02em;
        }
        .ghn-process-desc {
            max-width:620px;
            color:#64748B;
            font-size:.84rem;
            line-height:1.62;
            font-weight:550;
        }
        .ghn-process-flow {
            display:grid;
            grid-template-columns:repeat(4,minmax(0,1fr));
            gap:14px;
        }
        .ghn-process-card {
            position:relative;
            min-width:0;
            overflow:hidden;
            border-radius:18px;
            background:rgba(255,255,255,.88);
            border:1px solid rgba(226,232,240,.95);
            box-shadow:0 14px 30px rgba(10,31,68,.07);
            padding:17px 17px 18px;
        }
        .ghn-process-card::before {
            content:'';
            position:absolute;
            top:0;
            left:0;
            right:0;
            height:4px;
            background:linear-gradient(90deg,var(--accent),#FFB38B);
        }
        .ghn-process-label {
            color:var(--accent);
            font-size:.68rem;
            font-weight:850;
            letter-spacing:.1em;
            text-transform:uppercase;
            margin-bottom:10px;
        }
        .ghn-process-value {
            color:#0A1F44;
            font-size:clamp(1.6rem,2.25vw,2.35rem);
            font-weight:950;
            line-height:.95;
            letter-spacing:-.04em;
            font-variant-numeric:tabular-nums;
            white-space:nowrap;
        }
        .ghn-process-note {
            color:#64748B;
            font-size:.78rem;
            line-height:1.45;
            margin-top:8px;
            font-weight:550;
        }
        @media (max-width:1180px) {
            .ghn-process-flow { grid-template-columns:repeat(3,minmax(0,1fr)); }
        }
        @media (max-width:720px) {
            .ghn-process-wrap { padding:20px; border-radius:22px; }
            .ghn-process-flow { grid-template-columns:1fr; }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.html(
        dedent(
            f"""
            <div class="ghn-process-wrap">
                <div class="ghn-process-head">
                    <div>
                        <div class="ghn-process-kicker">Xử lý dữ liệu</div>
                        <div class="ghn-process-title">Từ mẫu thu thập đến mẫu phân tích</div>
                    </div>
                    <div class="ghn-process-desc">
                        Số liệu sử dụng cùng một base đã truyền thông, từ mẫu thu thập
                        đến mẫu sau làm sạch dùng cho phân tích.
                    </div>
                </div>
                <div class="ghn-process-flow">
                    {card_html}
                </div>
            </div>
            """
        )
    )

    # Bảng chất lượng dữ liệu theo nhóm — đồng bộ với trang Độ tin cậy dữ liệu
    from views.view_i_data_trust import DEEPDIVE_GROUP_BASE
    
    df_table = pd.DataFrame(DEEPDIVE_GROUP_BASE)
    df_table["Drop %"] = df_table["Dropped"] / df_table["Raw submissions"].clip(lower=1) * 100
    df_table["Cleaned %"] = df_table["Cleaned base"] / df_table["Raw submissions"].clip(lower=1) * 100
    df_table = df_table[[
        "Nhóm", "Raw submissions", "Dropped", "Drop %", "Cleaned base",
        "Cleaned %", "EI", "eNPS", "Leave %", "Silence %", "MEI", "Flight Risk %"
    ]].rename(columns={
        "Raw submissions": "Phản hồi thô",
        "Dropped": "Bị loại",
        "Drop %": "Tỷ lệ loại",
        "Cleaned base": "Mẫu phân tích",
        "Cleaned %": "Tỷ lệ giữ",
        "Leave %": "Ý định nghỉ",
        "Silence %": "Im lặng",
        "Flight Risk %": "Rủi ro rời bỏ",
    })

    st.dataframe(
        df_table.style.format({
            "Phản hồi thô": "{:,.0f}",
            "Bị loại": "{:,.0f}",
            "Tỷ lệ loại": "{:.1f}%",
            "Mẫu phân tích": "{:,.0f}",
            "Tỷ lệ giữ": "{:.1f}%",
            "EI": "{:.1f}",
            "eNPS": "{:+.1f}",
            "Ý định nghỉ": "{:.1f}%",
            "Im lặng": "{:.1f}%",
            "MEI": "{:.1f}",
            "Rủi ro rời bỏ": "{:.1f}%",
        }, na_rep="-"),
        width="stretch",
        hide_index=True,
    )


def render(all_data, available_groups, scope_restricted=False):
    if not all_data:
        st.error("Không tìm thấy dữ liệu nào.")
        return

    apply_theme()

    all_dfs = []
    total_n_before = 0
    for group_id, (df, n_before) in all_data.items():
        df_group = df.copy()
        df_group["_survey_group"] = group_id
        all_dfs.append(df_group)
        total_n_before += n_before

    df_total = _normalize_org_columns(pd.concat(all_dfs, ignore_index=True))
    total_kpis = compute_kpis(df_total)
    total_ei = total_kpis['ei_mean']
    total_enps = total_kpis['enps_score']
    total_intent = total_kpis['intent_pct_low']
    total_mei = total_kpis.get('mei_avg', 0.0)

    # Số liệu toàn công ty chỉ được dùng cho tài khoản không bị giới hạn scope.
    from views.view_i_data_trust import DEEPDIVE_QUALITY_TOTALS
    if scope_restricted:
        total_participants = len(df_total)
        total_cleaned = len(df_total)
        total_headcount = None
        total_rr = None
        cleaned_rr = None
    else:
        total_participants = DEEPDIVE_QUALITY_TOTALS["raw"]
        total_cleaned = DEEPDIVE_QUALITY_TOTALS["cleaned"]
        # Workforce runtime có thể chứa nhân sự phát sinh sau kỳ khảo sát.
        total_headcount = DEEPDIVE_QUALITY_TOTALS["headcount"]
        total_rr = round((total_participants / total_headcount) * 100, 1)
        cleaned_rr = round((total_cleaned / total_headcount) * 100, 1)
    bm = get_company_benchmark_2025()
    ei_delta = total_ei - bm['ei_mean']
    enps_delta = total_enps - bm['enps_score']
    scope_display = "phạm vi được cấp quyền" if scope_restricted else "toàn tổ chức"

    if scope_restricted:
        hero_kicker = "GHN · Phạm vi được cấp quyền"
        hero_title = "Tổng quan dữ liệu<br/>trong phạm vi của bạn"
        hero_subtitle = (
            "Các chỉ số và phân tích bên dưới chỉ sử dụng dữ liệu thuộc Khối, "
            "Phòng ban hoặc Section đã được cấp quyền."
        )
        hero_mini_html = f"""
            <div class="ghn-mini"><span>Mẫu trong phạm vi</span><strong>{total_cleaned:,}</strong></div>
            <div class="ghn-mini"><span>Số nhóm có dữ liệu</span><strong>{len(all_data)}</strong></div>
            <div class="ghn-mini"><span>EI so với 2025</span><strong>{ei_delta:+.1f}</strong></div>
            <div class="ghn-mini"><span>Phạm vi</span><strong>Đã giới hạn</strong></div>
        """
        hero_metrics_html = f"""
            <div class="ghn-metric" style="--accent:#1D4ED8"><div class="ghn-metric-label">Mẫu trong phạm vi</div><div class="ghn-metric-value">{total_cleaned:,}</div><div class="ghn-metric-sub">Chỉ gồm dữ liệu tài khoản được phép xem</div></div>
            <div class="ghn-metric" style="--accent:#10B981"><div class="ghn-metric-label">Số nhóm khảo sát</div><div class="ghn-metric-value">{len(all_data)}</div><div class="ghn-metric-sub">Nhóm có dữ liệu trong phạm vi hiện tại</div></div>
            <div class="ghn-metric" style="--accent:#F97316"><div class="ghn-metric-label">EI trong phạm vi</div><div class="ghn-metric-value">{total_ei:.1f}</div><div class="ghn-metric-sub">Tính trên mẫu được cấp quyền</div></div>
            <div class="ghn-metric" style="--accent:#64748B"><div class="ghn-metric-label">eNPS trong phạm vi</div><div class="ghn-metric-value">{total_enps:+.0f}</div><div class="ghn-metric-sub">Không bao gồm đơn vị ngoài phạm vi</div></div>
        """
    else:
        hero_kicker = "GHN · Tổng quan tổ chức"
        hero_title = "Tổng quan GHN<br/>trên nền dữ liệu EES 2026"
        hero_subtitle = (
            "Một lớp điều hành tổng hợp cho thấy quy mô tham gia, sức khỏe gắn kết, "
            "khoảng cách giữa các đơn vị và các điểm cần ưu tiên trước khi đi sâu vào từng nhóm khảo sát."
        )
        hero_mini_html = f"""
            <div class="ghn-mini"><span>Tỷ lệ phản hồi</span><strong>{total_rr:.1f}%</strong></div>
            <div class="ghn-mini"><span>EI so với 2025</span><strong>{ei_delta:+.1f}</strong></div>
            <div class="ghn-mini"><span>Mẫu hợp lệ</span><strong>{total_cleaned:,}</strong></div>
            <div class="ghn-mini"><span>Độ phủ dữ liệu</span><strong>{cleaned_rr:.1f}%</strong></div>
        """
        hero_metrics_html = f"""
            <div class="ghn-metric" style="--accent:#0A1F44"><div class="ghn-metric-label">Tổng nhân sự</div><div class="ghn-metric-value">{total_headcount:,}</div><div class="ghn-metric-sub">Headcount toàn tổ chức GHN</div></div>
            <div class="ghn-metric" style="--accent:#1D4ED8"><div class="ghn-metric-label">Đã tham gia</div><div class="ghn-metric-value">{total_participants:,}</div><div class="ghn-metric-sub">{total_rr:.1f}% tỷ lệ phản hồi</div></div>
            <div class="ghn-metric" style="--accent:#10B981"><div class="ghn-metric-label">Mẫu phân tích</div><div class="ghn-metric-value">{total_cleaned:,}</div><div class="ghn-metric-sub">{cleaned_rr:.1f}% / headcount sau lọc memo</div></div>
            <div class="ghn-metric" style="--accent:#64748B"><div class="ghn-metric-label">Chưa tham gia</div><div class="ghn-metric-value">{max(total_headcount - total_participants, 0):,}</div><div class="ghn-metric-sub">{max(round((1 - total_participants / total_headcount) * 100, 1), 0):.1f}% chưa phản hồi</div></div>
        """

    st.markdown('''
    <style>
    .ghn-shell {
        border-radius:28px;
        padding:32px;
        margin:20px 0 28px;
        background:
            radial-gradient(circle at 8% 0%, rgba(255,82,0,.12), transparent 28%),
            radial-gradient(circle at 92% 12%, rgba(29,78,216,.10), transparent 30%),
            linear-gradient(135deg, #FFFFFF 0%, #F8FAFC 54%, #EEF6FF 100%);
        border:1px solid rgba(226,232,240,.95);
        box-shadow:0 24px 64px rgba(10,31,68,.11), inset 0 1px 0 rgba(255,255,255,.96);
        overflow:hidden;
    }
    .ghn-hero {
        display:grid;
        grid-template-columns:minmax(0,1.15fr) minmax(340px,.85fr);
        gap:26px;
        align-items:stretch;
    }
    .ghn-kicker {
        display:inline-flex;
        align-items:center;
        gap:8px;
        padding:7px 12px;
        border-radius:999px;
        background:#FFF4EF;
        border:1px solid #FFD5BF;
        color:#FF5200;
        font-size:.72rem;
        font-weight:850;
        letter-spacing:.15em;
        text-transform:uppercase;
        margin-bottom:14px;
    }
    .ghn-kicker::before {
        content:'';
        width:8px;
        height:8px;
        border-radius:50%;
        background:#10B981;
        box-shadow:0 0 0 5px rgba(16,185,129,.14);
    }
    .ghn-title {
        font-size:clamp(2.25rem,3.45vw,3.65rem);
        line-height:1.03;
        letter-spacing:-.04em;
        font-weight:950;
        color:#0A1F44;
        margin:0 0 14px;
    }
    .ghn-subtitle {
        color:#475569;
        font-size:1rem;
        line-height:1.72;
        font-weight:550;
        margin:0;
        max-width:760px;
    }
    .ghn-command {
        position:relative;
        min-height:285px;
        border-radius:24px;
        padding:24px;
        overflow:hidden;
        color:#fff;
        background:
            linear-gradient(rgba(255,255,255,.08) 1px, transparent 1px),
            linear-gradient(90deg, rgba(255,255,255,.07) 1px, transparent 1px),
            linear-gradient(145deg, rgba(10,31,68,.98), rgba(29,78,216,.88));
        background-size:34px 34px,34px 34px,auto;
        box-shadow:0 24px 54px rgba(10,31,68,.24);
        transform:perspective(1200px) rotateY(-3deg) rotateX(1deg);
    }
    .ghn-command::after {
        content:'';
        position:absolute;
        width:210px;
        height:210px;
        right:-72px;
        bottom:-86px;
        background:radial-gradient(circle, rgba(255,82,0,.44), transparent 66%);
        pointer-events:none;
    }
    .ghn-command-label {
        position:relative;
        z-index:1;
        font-size:.72rem;
        font-weight:850;
        letter-spacing:.17em;
        text-transform:uppercase;
        color:#FFDBCC;
    }
    .ghn-command-score {
        position:relative;
        z-index:1;
        margin-top:18px;
        font-size:clamp(3rem,5.3vw,5rem);
        line-height:.9;
        font-weight:950;
        letter-spacing:-.06em;
    }
    .ghn-command-sub {
        position:relative;
        z-index:1;
        color:rgba(255,255,255,.82);
        font-size:.86rem;
        line-height:1.55;
        margin-top:10px;
    }
    .ghn-mini-grid {
        position:relative;
        z-index:1;
        display:grid;
        grid-template-columns:repeat(2,minmax(0,1fr));
        gap:10px;
        margin-top:28px;
    }
    .ghn-mini {
        border-radius:14px;
        padding:12px 13px;
        background:rgba(255,255,255,.12);
        border:1px solid rgba(255,255,255,.18);
        backdrop-filter:blur(10px);
    }
    .ghn-mini span { display:block; font-size:.66rem; font-weight:800; letter-spacing:.1em; text-transform:uppercase; color:#BFDBFE; margin-bottom:6px; }
    .ghn-mini strong { display:block; font-size:1.2rem; line-height:1; font-weight:900; color:#fff; }
    .ghn-metrics {
        display:grid;
        grid-template-columns:repeat(4,minmax(0,1fr));
        gap:16px;
        margin-top:22px;
    }
    .ghn-metric {
        position:relative;
        overflow:hidden;
        min-width:0;
        border-radius:18px;
        padding:18px 18px 20px;
        background:rgba(255,255,255,.86);
        border:1px solid rgba(226,232,240,.95);
        box-shadow:0 16px 30px rgba(10,31,68,.08);
    }
    .ghn-metric::before {
        content:'';
        position:absolute;
        top:0;
        left:0;
        right:0;
        height:4px;
        background:linear-gradient(90deg,var(--accent),#FFB38B);
    }
    .ghn-metric-label {
        color:var(--accent);
        font-size:.68rem;
        font-weight:850;
        text-transform:uppercase;
        letter-spacing:.11em;
        margin-bottom:10px;
    }
    .ghn-metric-value {
        font-size:clamp(1.7rem,2.35vw,2.55rem);
        font-weight:950;
        line-height:.95;
        color:#0A1F44;
        letter-spacing:-.04em;
        font-variant-numeric:tabular-nums;
        white-space:nowrap;
    }
    .ghn-metric-sub {
        font-size:.78rem;
        color:#64748B;
        line-height:1.45;
        margin-top:8px;
        font-weight:550;
    }
    .ghn-context {
        display:grid;
        grid-template-columns:repeat(4,minmax(0,1fr));
        gap:14px;
        margin-top:20px;
    }
    .ghn-context-card {
        background:#fff;
        border:1px solid #E2E8F0;
        border-radius:16px;
        padding:16px 17px;
        box-shadow:0 14px 30px rgba(10,31,68,.06);
        min-height:130px;
    }
    .ghn-context-chip {
        display:inline-flex;
        align-items:center;
        padding:5px 10px;
        border-radius:999px;
        background:#FFF4EF;
        border:1px solid #FFD5BF;
        color:#FF5200;
        font-size:.68rem;
        font-weight:850;
        letter-spacing:.08em;
        text-transform:uppercase;
        margin-bottom:10px;
    }
    .ghn-context-card h4 { margin:0 0 7px; font-size:.94rem; color:#0A1F44; font-weight:850; letter-spacing:-.01em; }
    .ghn-context-card p { margin:0; color:#64748B; font-size:.82rem; line-height:1.6; font-weight:520; }
    .ghn-band {
        border-radius:22px;
        padding:20px;
        margin:0 0 26px;
        background:#fff;
        border:1px solid #E2E8F0;
        box-shadow:0 18px 42px rgba(10,31,68,.08);
    }
    .benchmark-summary {
        margin:26px 0 30px;
        padding:24px;
        border:1px solid #DCE6F4;
        border-radius:20px;
        background:#FFFFFF;
        box-shadow:0 18px 42px rgba(10,31,68,.07);
    }
    .benchmark-summary-head {
        display:flex;
        align-items:flex-start;
        justify-content:space-between;
        gap:20px;
        margin-bottom:18px;
    }
    .benchmark-summary-kicker {
        color:#FF5200;
        font-size:.68rem;
        font-weight:850;
        letter-spacing:.14em;
        text-transform:uppercase;
        margin-bottom:6px;
    }
    .benchmark-summary-head h3 {
        margin:0;
        color:#0A1F44;
        font-size:1.35rem;
        font-weight:900;
    }
    .benchmark-summary-head p {
        max-width:760px;
        margin:7px 0 0;
        color:#64748B;
        font-size:.84rem;
        line-height:1.55;
    }
    .benchmark-summary-status {
        flex:0 0 auto;
        padding:7px 11px;
        border:1px solid #A7F3D0;
        border-radius:999px;
        background:#ECFDF5;
        color:#047857;
        font-size:.7rem;
        font-weight:800;
    }
    .benchmark-summary-grid {
        display:grid;
        grid-template-columns:repeat(4,minmax(0,1fr));
        gap:12px;
    }
    .benchmark-summary-card {
        min-width:0;
        padding:16px;
        border:1px solid #E2E8F0;
        border-top:3px solid var(--benchmark-accent);
        border-radius:12px;
        background:#F8FAFC;
    }
    .benchmark-summary-card--blue { --benchmark-accent:#2563EB; }
    .benchmark-summary-card--orange { --benchmark-accent:#F97316; }
    .benchmark-summary-card--green { --benchmark-accent:#10B981; }
    .benchmark-summary-card--navy { --benchmark-accent:#0A1F44; }
    .benchmark-summary-card span {
        display:block;
        min-height:34px;
        color:#64748B;
        font-size:.67rem;
        font-weight:800;
        letter-spacing:.06em;
        text-transform:uppercase;
        line-height:1.35;
    }
    .benchmark-summary-card strong {
        display:block;
        margin-top:8px;
        color:#0A1F44;
        font-size:clamp(1.55rem,2vw,2.15rem);
        font-weight:900;
        line-height:1;
        font-variant-numeric:tabular-nums;
    }
    .benchmark-summary-card p {
        margin:8px 0 0;
        color:#64748B;
        font-size:.76rem;
        line-height:1.5;
    }
    .benchmark-summary-reading {
        display:grid;
        grid-template-columns:repeat(3,minmax(0,1fr));
        gap:0;
        margin-top:18px;
        padding-top:18px;
        border-top:1px solid #E2E8F0;
    }
    .benchmark-summary-reading > div {
        padding:0 18px;
        border-left:1px solid #E2E8F0;
    }
    .benchmark-summary-reading > div:first-child {
        padding-left:0;
        border-left:0;
    }
    .benchmark-summary-reading > div:last-child { padding-right:0; }
    .benchmark-summary-reading span {
        color:#0A1F44;
        font-size:.78rem;
        font-weight:850;
    }
    .benchmark-summary-reading p {
        margin:6px 0 0;
        color:#64748B;
        font-size:.78rem;
        line-height:1.58;
    }
    @media (max-width:1080px) {
        .ghn-hero { grid-template-columns:1fr; }
        .ghn-command { transform:none; }
        .ghn-metrics, .ghn-context { grid-template-columns:repeat(2,minmax(0,1fr)); }
        .benchmark-summary-grid { grid-template-columns:repeat(2,minmax(0,1fr)); }
    }
    @media (max-width:720px) {
        .ghn-shell { padding:20px; border-radius:22px; }
        .ghn-metrics, .ghn-context, .ghn-mini-grid { grid-template-columns:1fr; }
        .benchmark-summary { padding:18px; border-radius:16px; }
        .benchmark-summary-head { display:block; }
        .benchmark-summary-status { display:inline-flex; margin-top:12px; }
        .benchmark-summary-grid, .benchmark-summary-reading { grid-template-columns:1fr; }
        .benchmark-summary-reading > div {
            padding:14px 0;
            border-left:0;
            border-top:1px solid #E2E8F0;
        }
        .benchmark-summary-reading > div:first-child {
            padding-top:0;
            border-top:0;
        }
    }
    </style>
    ''', unsafe_allow_html=True)

    hero_html = dedent(f'''
    <div class="ghn-shell">
        <div class="ghn-hero">
            <div>
                <span class="ghn-kicker">{hero_kicker}</span>
                <h1 class="ghn-title">{hero_title}</h1>
                <p class="ghn-subtitle">{hero_subtitle}</p>
            </div>
            <div class="ghn-command">
                <div class="ghn-command-label">Trung tâm điều hành gắn kết</div>
                <div class="ghn-command-score">{total_ei:.1f}</div>
                <div class="ghn-command-sub">EI {scope_display} · eNPS {total_enps:+.0f} · Rủi ro nghỉ việc {total_intent:.1f}%</div>
                <div class="ghn-mini-grid">
                    {hero_mini_html}
                </div>
            </div>
        </div>

        <div class="ghn-metrics">
            {hero_metrics_html}
        </div>


    </div>
    ''')
    st.html(hero_html)
    if not scope_restricted:
        _render_data_processing_section(
            headcount=total_headcount,
            raw=total_participants,
            dropped=DEEPDIVE_QUALITY_TOTALS["dropped"],
            cleaned=total_cleaned,
            all_data=all_data,
        )

    # Executive company overview section
    from shared.plotly_theme import make_html_kpi
    st.html(dedent(f"""
    <div class="ghn-band">
        <div style="display:flex;align-items:flex-end;justify-content:space-between;gap:16px;flex-wrap:wrap;margin-bottom:14px;">
            <div>
                <div style="font-size:.72rem;font-weight:850;color:#FF5200;text-transform:uppercase;letter-spacing:.14em;margin-bottom:6px;">TỔNG QUAN GIAO HÀNG NHANH</div>
                <div style="font-size:1.35rem;font-weight:900;color:#0A1F44;letter-spacing:-.02em;">Bốn chỉ số chiến lược</div>
            </div>
            <div style="font-size:.82rem;color:#64748B;font-weight:550;">So sánh với baseline 2025 và trạng thái hiện tại của {scope_display}.</div>
        </div>
    </div>
    """))
    kpi_c1, kpi_c2, kpi_c3, kpi_c4 = st.columns(4)
    with kpi_c1:
        st.markdown(make_html_kpi("EI - Chỉ số gắn kết", f"{total_ei:.1f}", delta=f"{ei_delta:+.1f}", color="blue", icon="", progress_val=total_ei), unsafe_allow_html=True)
    with kpi_c2:
        st.markdown(make_html_kpi("eNPS - Mức sẵn sàng giới thiệu", f"{total_enps:+.0f}", delta=f"{enps_delta:+.0f}", color="orange", icon="", progress_val=(total_enps+100)/2), unsafe_allow_html=True)
    with kpi_c3:
        st.markdown(make_html_kpi("Attrition Risk - Rủi ro nghỉ việc", f"{total_intent:.1f}%", delta="N/A", color="red", icon="", progress_val=total_intent), unsafe_allow_html=True)
    with kpi_c4:
        st.markdown(make_html_kpi("MEI - Quản lý trực tiếp", f"{total_mei:.1f}", delta="N/A", color="green", icon="", progress_val=total_mei), unsafe_allow_html=True)

    if not scope_restricted:
        _render_benchmark_executive_summary(
            total_ei=total_ei,
            total_enps=total_enps,
            total_participants=total_participants,
            total_cleaned=total_cleaned,
            total_dropped=DEEPDIVE_QUALITY_TOTALS["dropped"],
        )

    # Calculate dynamic insights across divisions
    div_stats = []
    if 'division' in df_total.columns:
        for div, df_div in df_total.groupby('division', dropna=True):
            if len(df_div) < MIN_ORG_SEGMENT_N:
                continue
            kpis = compute_kpis(df_div)
            kpis['division'] = div
            div_stats.append(kpis)
    df_div_stats = pd.DataFrame(div_stats)

    if not df_div_stats.empty:
        ei_col = df_div_stats['ei_mean'].dropna()
        if ei_col.empty:
            top_div = bot_div = df_div_stats.iloc[0]
        else:
            top_div = df_div_stats.loc[ei_col.idxmax()]
            bot_div = df_div_stats.loc[ei_col.idxmin()]
        
        pillar_scores = {}
        for p in PILLAR_LABELS.keys():
            col = f'{p}_pct'
            if col in df_total.columns:
                mean_val = df_total[col].mean()
                if pd.notna(mean_val):
                    pillar_scores[p] = mean_val
        if pillar_scores:
            top_pillar_key = max(pillar_scores, key=pillar_scores.get)
            bot_pillar_key = min(pillar_scores, key=pillar_scores.get)
            top_pillar_name = PILLAR_LABELS[top_pillar_key]
            bot_pillar_name = PILLAR_LABELS[bot_pillar_key]
        else:
            top_pillar_name = bot_pillar_name = "N/A"

        ai_data = {
            "Total_EI": round(total_ei, 1),
            "Total_eNPS": round(total_enps, 0),
            "EI_Delta_YoY": round(ei_delta, 1),
            "Top_Division": top_div['division'],
            "Top_Division_EI": round(top_div['ei_mean'], 1),
            "Top_Pillar": top_pillar_name,
            "Bottom_Division": bot_div['division'],
            "Bottom_Division_EI": round(bot_div['ei_mean'], 1),
            "Bottom_Pillar": bot_pillar_name,
            "Total_Attrition_Risk": round(total_intent, 1)
        }
        
        _data_short = (
            f"Bạn là chuyên gia phân tích nhân sự GHN Express. Dựa vào đúng các số liệu sau — KHÔNG thêm số liệu ngoài danh sách:\n"
            f"- EI {scope_display}: {ai_data['Total_EI']}% (thay đổi {ai_data['EI_Delta_YoY']:+.1f} điểm so với 2025)\n"
            f"- eNPS: {ai_data['Total_eNPS']:+.0f}\n"
            f"- Tỷ lệ nhân viên có nguy cơ nghỉ việc: {ai_data['Total_Attrition_Risk']:.1f}%\n"
            f"- Đơn vị EI cao nhất: {ai_data['Top_Division']} ({ai_data['Top_Division_EI']:.1f}%)\n"
            f"- Đơn vị EI thấp nhất: {ai_data['Bottom_Division']} ({ai_data['Bottom_Division_EI']:.1f}%)\n"
            f"- Trụ cột gắn kết mạnh nhất: {ai_data['Top_Pillar']}\n"
            f"- Trụ cột gắn kết yếu nhất: {ai_data['Bottom_Pillar']}\n\n"
            f"Viết theo đúng 5 mục sau, mỗi mục 1-2 câu, ngôn ngữ tự nhiên như analyst đang báo cáo nhanh cho Ban Giám Đốc:\n"
            f"- **Sự suy giảm gắn kết:** [nhận định ngắn về EI, xu hướng và ý nghĩa]\n"
            f"- **Rủi ro nghỉ việc:** [đánh giá nhanh mức độ nguy cơ attrition]\n"
            f"- **Khoảng cách giữa các phòng ban:** [so sánh đơn vị cao nhất và thấp nhất, khoảng cách đó lớn hay nhỏ]\n"
            f"- **Trụ cột mạnh nhất và yếu nhất:** [nhận định ngắn — giải thích trụ cột là khía cạnh trải nghiệm nào để người không làm HR cũng hiểu]\n"
            f"- **Chiến lược cải thiện cấp bách:** [1-2 ưu tiên rõ ràng nhất cần hành động ngay]\n\n"
            f"Chỉ dùng đúng các con số đã cung cấp. Không nhắc tên framework hay học thuật."
        )
        _data_long = (
            f"Bạn là chuyên gia phân tích nhân sự GHN Express. Dựa vào đúng các số liệu sau — KHÔNG thêm số liệu ngoài danh sách:\n"
            f"- EI {scope_display}: {ai_data['Total_EI']}% (thay đổi {ai_data['EI_Delta_YoY']:+.1f} điểm so với 2025)\n"
            f"- eNPS: {ai_data['Total_eNPS']:+.0f}\n"
            f"- Tỷ lệ nhân viên có nguy cơ nghỉ việc: {ai_data['Total_Attrition_Risk']:.1f}%\n"
            f"- Đơn vị EI cao nhất: {ai_data['Top_Division']} ({ai_data['Top_Division_EI']:.1f}%)\n"
            f"- Đơn vị EI thấp nhất: {ai_data['Bottom_Division']} ({ai_data['Bottom_Division_EI']:.1f}%)\n"
            f"- Trụ cột gắn kết mạnh nhất: {ai_data['Top_Pillar']}\n"
            f"- Trụ cột gắn kết yếu nhất: {ai_data['Bottom_Pillar']}\n\n"
            f"Viết theo đúng 5 mục sau, mỗi mục 3-4 câu phân tích sâu, tự nhiên như analyst đang giải thích bối cảnh cho Ban Giám Đốc:\n"
            f"- **Sự suy giảm gắn kết:** [phân tích EI và eNPS — con số đang nói lên điều gì, và tại sao xu hướng này đáng lo hoặc đáng chú ý]\n"
            f"- **Rủi ro nghỉ việc:** [phân tích mức độ rủi ro, ý nghĩa với tổ chức, và nhóm nào cần theo dõi trước]\n"
            f"- **Khoảng cách giữa các phòng ban:** [phân tích khoảng cách EI, điều đó phản ánh gì, và hệ quả nếu không can thiệp]\n"
            f"- **Trụ cột mạnh nhất và yếu nhất:** [giải thích ý nghĩa của trụ cột này trong trải nghiệm hàng ngày của nhân viên, và hàm ý cho tổ chức]\n"
            f"- **Chiến lược cải thiện cấp bách:** [phân tích lý do ưu tiên, đề xuất hành động cụ thể có thể triển khai trong ngắn hạn]\n\n"
            f"Chỉ dùng đúng các con số đã cung cấp. Không nhắc tên framework hay học thuật."
        )
        render_ai_insight_card_dual("AI Executive Summary & Insight", ai_data, _data_short, _data_long)

    # ══════════════════════════════════════════════════════════════
    # SECTION 2: ORG DRILLDOWN (KHỐI / DIVISION)
    # ══════════════════════════════════════════════════════════════
    from shared.plotly_theme import section_header
    st.markdown(section_header("Phân Tích Cấp Tổ Chức", "Mức độ gắn kết và sức khỏe tổ chức theo Khối / Division"), unsafe_allow_html=True)
    
    if not df_div_stats.empty:
        df_div_stats = df_div_stats.sort_values('ei_mean', ascending=True)
        
        c1, c2 = st.columns([1, 1])
        with c1:
            fig_bar = go.Figure(go.Bar(
                y=df_div_stats['division'], x=df_div_stats['ei_mean'],
                orientation='h', marker_color=COLORS['blue'],
                text=[f'{v:.1f}%' for v in df_div_stats['ei_mean']],
                textposition='inside'
            ))
            fig_bar = fig_card(fig_bar, 'EI theo Khối / Division', 'Mức độ gắn kết trung bình')
            fig_bar.update_layout(xaxis=dict(range=[0, 100], showgrid=True))
            st.plotly_chart(fig_bar, width='stretch', key="company_overview_chart_250")
            
        with c2:
            # Heatmap of pillars by division
            hm_data = []
            for div, df_div in df_total.groupby('division', dropna=True):
                if len(df_div) < MIN_ORG_SEGMENT_N:
                    continue
                row = {'division': div}
                for p, plabel in PILLAR_LABELS.items():
                    col = f'{p}_pct'
                    if col in df_div.columns:
                        row[plabel] = df_div[col].mean()
                hm_data.append(row)
            df_hm = pd.DataFrame(hm_data).set_index('division')

            if df_hm.shape[1] > 0:
                fig_hm = go.Figure(data=go.Heatmap(
                    z=df_hm.values,
                    x=df_hm.columns,
                    y=df_hm.index,
                    colorscale='RdYlGn',
                    zmin=50, zmax=90,
                    text=df_hm.round(1).values,
                    texttemplate="%{text}",
                    showscale=False
                ))
                fig_hm = fig_card(fig_hm, 'Heatmap 5 Trụ Cột theo Khối', 'Phân bổ sức khỏe tổ chức')
                st.plotly_chart(fig_hm, width='stretch', key="company_overview_chart_276")
            else:
                st.info("Chưa có dữ liệu trụ cột theo Khối để dựng heatmap.")
            
        # --- AI Insight for Division ---
        if len(df_div_stats) > 1 and df_hm.shape[1] > 0:
            top_div = df_div_stats.iloc[-1]['division']
            bot_div = df_div_stats.iloc[0]['division']
            lowest_pillar = df_hm.mean().idxmin()
            
            org_ai_data = {
                "Top_Division": top_div,
                "Top_EI": round(df_div_stats.iloc[-1]['ei_mean'], 1),
                "Bottom_Division": bot_div,
                "Bottom_EI": round(df_div_stats.iloc[0]['ei_mean'], 1),
                "Lowest_System_Pillar": lowest_pillar
            }
            prompt = (
                f"Bạn là chuyên gia phân tích nhân sự GHN. Người đọc vừa xem biểu đồ EI và heatmap trụ cột theo khối."
                f" Dưới đây là các số liệu thực tế — chỉ dùng đúng những con số này:\n"
                f"- Đơn vị EI cao nhất: {org_ai_data['Top_Division']} ({org_ai_data['Top_EI']:.1f}%)\n"
                f"- Đơn vị EI thấp nhất: {org_ai_data['Bottom_Division']} ({org_ai_data['Bottom_EI']:.1f}%)\n"
                f"- Trụ cột điểm thấp nhất trong {scope_display}: {org_ai_data['Lowest_System_Pillar']}\n\n"
                f"Viết theo 3 mục sau, mỗi mục 2-3 câu, tự nhiên như analyst đang tóm tắt biểu đồ vừa xem:\n"
                f"- **Khoảng cách EI giữa các khối:** [con số đó lớn hay nhỏ, và điều gì có thể đang xảy ra bên dưới]\n"
                f"- **Trụ cột yếu nhất trong phạm vi:** [giải thích trụ cột {org_ai_data['Lowest_System_Pillar']} ảnh hưởng như thế nào đến trải nghiệm nhân viên hàng ngày]\n"
                f"- **Ưu tiên can thiệp:** [đơn vị nào và vấn đề gì cần xử lý trước, lý do ngắn gọn]\n\n"
                f"Chỉ dùng đúng các con số đã cung cấp. Không nhắc tên framework hay học thuật."
            )
            render_ai_insight_card("AI Organization Insight", org_ai_data, prompt, custom_style="margin-top: 24px; padding: 20px;")

    # ══════════════════════════════════════════════════════════════
    # SECTION 2b: DRILLDOWN – PHÒNG BAN & SECTION
    # ══════════════════════════════════════════════════════════════
    st.markdown(section_header("Phân Tích Chi Tiết — Phòng Ban & Section",
                               "So sánh EI, eNPS và 5 trụ cột theo từng phòng ban / section"), unsafe_allow_html=True)

    st.markdown(
        f"""<div style="display:inline-flex;align-items:center;gap:8px;
                        background:#FFF8F0;border:1px solid #FFD5BF;border-radius:8px;
                        padding:7px 14px;margin-bottom:12px;font-size:0.78rem;color:#B45309;font-weight:600;">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor"
                 stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                <circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/>
                <line x1="12" y1="16" x2="12.01" y2="16"/>
            </svg>
            Chỉ hiển thị phòng ban / section có <strong style="margin:0 3px">N &gt; {MIN_ORG_SEGMENT_N}</strong> mẫu để đảm bảo tính đại diện thống kê.
        </div>""",
        unsafe_allow_html=True
    )

    def _build_drilldown_table(df_src, group_col, label, min_n=MIN_ORG_SEGMENT_N):
        rows = []
        for grp_val, grp_df in df_src.groupby(group_col, dropna=True):  # dropna=True: bỏ qua hàng không xác định
            if len(grp_df) < min_n:
                continue
            kpis = compute_kpis(grp_df)
            row = {
                label: grp_val,
                'N': kpis['n'],
                'EI (%)': round(kpis['ei_mean'], 1),
                'eNPS': round(kpis['enps_score'], 0),
                'Rủi ro nghỉ việc (%)': round(kpis['intent_pct_low'], 1),
            }
            for p, plabel in PILLAR_LABELS.items():
                col = f'{p}_pct'
                if col in grp_df.columns:
                    row[plabel] = round(grp_df[col].mean(), 1)
            rows.append(row)
        if not rows:
            return pd.DataFrame()
        tbl = pd.DataFrame(rows).sort_values('EI (%)', ascending=False).reset_index(drop=True)
        return tbl

    def _color_ei(v):
        try:
            v = float(v)
            c = '#10B981' if v >= 75 else '#F59E0B' if v >= 65 else '#EF4444'
            return f'color:{c};font-weight:700'
        except Exception:
            return ''

    def _color_enps(v):
        try:
            v = float(v)
            c = '#10B981' if v >= 20 else '#F59E0B' if v >= 0 else '#EF4444'
            return f'color:{c};font-weight:700'
        except Exception:
            return ''

    def _heatmap_pillar(v):
        try:
            v = float(v)
            if v >= 78:   return 'background-color:#D1FAE5;color:#065F46'
            elif v >= 72: return 'background-color:#FEF3C7;color:#92400E'
            else:          return 'background-color:#FEE2E2;color:#991B1B'
        except Exception:
            return ''

    pillar_cols = [lbl for lbl in PILLAR_LABELS.values()]

    tab_dept, tab_section = st.tabs(["Theo Phòng Ban (Department)", "Theo Section"])

    with tab_dept:
        if 'department' in df_total.columns:
            tbl_dept = _build_drilldown_table(df_total, 'department', 'Phòng Ban', min_n=MIN_DEPARTMENT_N)
            if not tbl_dept.empty:
                # Summary KPI row
                kd1, kd2, kd3 = st.columns(3)
                kd1.metric("Số phòng ban phân tích", len(tbl_dept))
                kd2.metric("EI cao nhất", f"{tbl_dept['EI (%)'].max():.1f}%", delta=tbl_dept.iloc[0]['Phòng Ban'])
                kd3.metric("EI thấp nhất", f"{tbl_dept['EI (%)'].iloc[-1]:.1f}%", delta=tbl_dept.iloc[-1]['Phòng Ban'], delta_color="inverse")

                # Bar chart EI by department
                fig_dept = go.Figure(go.Bar(
                    y=tbl_dept['Phòng Ban'], x=tbl_dept['EI (%)'],
                    orientation='h',
                    marker=dict(
                        color=[
                            '#10B981' if v >= 75 else '#F59E0B' if v >= 65 else '#EF4444'
                            for v in tbl_dept['EI (%)']
                        ],
                        cornerradius=4,
                    ),
                    text=[f"{v:.1f}%" for v in tbl_dept['EI (%)']],
                    textposition='outside',
                ))
                fig_dept.add_vline(x=75, line_dash='dot', line_color='#10B981', line_width=1.5,
                                   annotation_text='75% target', annotation_position='top right')
                fig_dept = fig_card(fig_dept, 'EI theo Phòng Ban', 'Mức độ gắn kết trung bình')
                fig_dept.update_layout(
                    height=max(300, len(tbl_dept) * 28 + 80),
                    xaxis=dict(range=[0, 100]),
                    yaxis=dict(autorange='reversed'),
                )
                st.plotly_chart(fig_dept, width='stretch', key="dept_ei_bar")

                # Detailed table with pillar heatmap
                st.markdown("##### Bảng chi tiết — EI, eNPS & 5 Trụ Cột theo Phòng Ban")
                avail_pillar_cols = [c for c in pillar_cols if c in tbl_dept.columns]

                # Format numbers into strings before styling
                tbl_dept_fmt = tbl_dept.copy()
                for c in ['EI (%)', 'Rủi ro nghỉ việc (%)'] + avail_pillar_cols:
                    if c in tbl_dept_fmt.columns:
                        tbl_dept_fmt[c] = tbl_dept_fmt[c].apply(lambda v: f"{v:.1f}")
                if 'eNPS' in tbl_dept_fmt.columns:
                    tbl_dept_fmt['eNPS'] = tbl_dept_fmt['eNPS'].apply(lambda v: f"{v:+.0f}")

                # Re-use raw numeric cols for coloring via the original tbl_dept
                def _style_dept_row(row_idx, col, raw_df, fmt_df):
                    pass  # not used

                # Build style using original numeric tbl for color logic, display fmt df
                def _make_styler(fmt_df, raw_df, ei_col, enps_col, pillar_col_list):
                    def _ei_style(col_series):
                        return [_color_ei(raw_df.loc[i, ei_col]) for i in raw_df.index]
                    def _enps_style(col_series):
                        return [_color_enps(raw_df.loc[i, enps_col]) for i in raw_df.index]
                    def _pillar_style(col_series, col_name):
                        return [_heatmap_pillar(raw_df.loc[i, col_name]) for i in raw_df.index]

                    s = fmt_df.style.set_table_styles([
                        {'selector': 'th', 'props': [('background-color', '#F8FAFC'), ('color', '#475569'),
                                                      ('font-size', '0.73rem'), ('font-weight', '700'),
                                                      ('text-align', 'center')]},
                        {'selector': 'td', 'props': [('font-size', '0.78rem'), ('text-align', 'center')]},
                        {'selector': 'td:first-child', 'props': [('text-align', 'left')]},
                    ])
                    s = s.apply(_ei_style, subset=[ei_col], axis=0)
                    s = s.apply(_enps_style, subset=[enps_col], axis=0)
                    for pc in pillar_col_list:
                        if pc in fmt_df.columns:
                            s = s.apply(lambda col, _pc=pc: _pillar_style(col, _pc), subset=[pc], axis=0)
                    return s

                styled_dept = _make_styler(tbl_dept_fmt, tbl_dept.reset_index(drop=True),
                                           'EI (%)', 'eNPS', avail_pillar_cols)
                st.dataframe(styled_dept, width='stretch', hide_index=True)
            else:
                st.info("Không có phòng ban nào có số mẫu trên 2.")
        else:
            st.info("Dữ liệu chưa có cột 'department'.")

    with tab_section:
        if 'section' in df_total.columns:
            tbl_section = _build_drilldown_table(df_total, 'section', 'Section')
            if not tbl_section.empty:
                ks1, ks2, ks3 = st.columns(3)
                ks1.metric("Số section phân tích", len(tbl_section))
                ks2.metric("EI cao nhất", f"{tbl_section['EI (%)'].max():.1f}%", delta=tbl_section.iloc[0]['Section'])
                ks3.metric("EI thấp nhất", f"{tbl_section['EI (%)'].iloc[-1]:.1f}%", delta=tbl_section.iloc[-1]['Section'], delta_color="inverse")

                # Bar chart – paginated nếu nhiều section
                max_section_show = min(len(tbl_section), 60)
                if max_section_show <= 10:
                    n_show = max_section_show
                else:
                    n_show = st.slider(
                        "Số section hiển thị (sắp xếp theo EI)",
                        min_value=10,
                        max_value=max_section_show,
                        value=min(30, max_section_show),
                        step=5,
                        key="section_slider",
                    )
                tbl_section_show = pd.concat([
                    tbl_section.head(n_show // 2),
                    tbl_section.tail(n_show - n_show // 2)
                ]).drop_duplicates()

                fig_sec = go.Figure(go.Bar(
                    y=tbl_section_show['Section'], x=tbl_section_show['EI (%)'],
                    orientation='h',
                    marker=dict(
                        color=[
                            '#10B981' if v >= 75 else '#F59E0B' if v >= 65 else '#EF4444'
                            for v in tbl_section_show['EI (%)']
                        ],
                        cornerradius=4,
                    ),
                    text=[f"{v:.1f}%" for v in tbl_section_show['EI (%)']],
                    textposition='outside',
                ))
                fig_sec.add_vline(x=75, line_dash='dot', line_color='#10B981', line_width=1.5)
                fig_sec = fig_card(fig_sec, 'EI theo Section', f'Top & Bottom {n_show} section')
                fig_sec.update_layout(
                    height=max(350, len(tbl_section_show) * 26 + 80),
                    xaxis=dict(range=[0, 100]),
                    yaxis=dict(autorange='reversed'),
                )
                st.plotly_chart(fig_sec, width='stretch', key="section_ei_bar")

                st.markdown("##### Bảng đầy đủ — EI, eNPS & 5 Trụ Cột theo Section")
                avail_pillar_cols_s = [c for c in pillar_cols if c in tbl_section.columns]

                tbl_section_fmt = tbl_section.copy()
                for c in ['EI (%)', 'Rủi ro nghỉ việc (%)'] + avail_pillar_cols_s:
                    if c in tbl_section_fmt.columns:
                        tbl_section_fmt[c] = tbl_section_fmt[c].apply(lambda v: f"{v:.1f}")
                if 'eNPS' in tbl_section_fmt.columns:
                    tbl_section_fmt['eNPS'] = tbl_section_fmt['eNPS'].apply(lambda v: f"{v:+.0f}")

                styled_section = _make_styler(tbl_section_fmt, tbl_section.reset_index(drop=True),
                                              'EI (%)', 'eNPS', avail_pillar_cols_s)
                st.dataframe(styled_section, width='stretch', hide_index=True)
            else:
                st.info(f"Không đủ mẫu theo section (tối thiểu {MIN_ORG_SEGMENT_N} người / section).")
        else:
            st.info("Dữ liệu chưa có cột 'section'.")

    _render_org_deep_dive(df_total)

    # ══════════════════════════════════════════════════════════════
    # SECTION 3: DEMOGRAPHICS (THÂM NIÊN & CẤP BẬC)
    # ══════════════════════════════════════════════════════════════
    st.markdown(section_header("Phân Tích Nhân Khẩu Học", "Phân mảnh mức độ gắn kết theo Thâm niên và Cấp bậc"), unsafe_allow_html=True)
    
    # Define demographic groups from Q5 if 'Q5' exists
    demographics_cols = []
    if 'Q5' in df_total.columns:
        demographics_cols.append(('Q5', 'Thâm niên'))
    
    if demographics_cols:
        for idx, (col, title) in enumerate(demographics_cols):
            # Compute stats by this col
            demo_stats = []
            for val, df_sub in df_total.groupby(col):
                if len(df_sub) < 5: continue
                kpis = compute_kpis(df_sub)
                kpis['group'] = val
                demo_stats.append(kpis)
            
            if demo_stats:
                df_demo = pd.DataFrame(demo_stats)
                if col == 'Q5':
                    order = [
                        'Dưới 1 tháng', 'Trên 1 đến 3 tháng', 'Trên 3 đến 6 tháng',
                        'Trên 6 đến 9 tháng', 'Trên 9 đến 12 tháng', 'Trên 1 đến 2 năm',
                        'Trên 2 đến 3 năm', 'Trên 3 đến 5 năm', 'Trên 5 năm', 'Khác'
                    ]
                    # Append any unknown J or other categories to the end
                    existing = df_demo['group'].tolist()
                    for g in existing:
                        if g not in order: order.append(g)
                    df_demo['group_cat'] = pd.Categorical(df_demo['group'], categories=order, ordered=True)
                    df_demo = df_demo.sort_values('group_cat')
                else:
                    df_demo = df_demo.sort_values('n', ascending=False)
                    
                fig_demo = go.Figure()
                fig_demo.add_trace(go.Bar(
                    y=df_demo['group'], x=df_demo['ei_mean'], name='EI', orientation='h',
                    marker_color=COLORS['blue'], text=[f'{v:.1f}%' for v in df_demo['ei_mean']], textposition='outside'
                ))
                fig_demo.add_trace(go.Bar(
                    y=df_demo['group'], x=df_demo['enps_score'], name='eNPS', orientation='h',
                    marker_color=COLORS['green'], text=[f'{v:+.0f}' for v in df_demo['enps_score']], textposition='outside'
                ))
                fig_demo.update_layout(
                    barmode='group',
                    yaxis={'autorange': 'reversed'}
                )
                fig_demo = fig_card(fig_demo, f'EI & eNPS theo {title}', 'Phân mảnh sự gắn kết')
                
                st.plotly_chart(fig_demo, width='stretch', key="company_overview_chart_346")
                
                # --- AI Insight for Demographics ---
                if len(df_demo) > 1:
                    top_group = df_demo.iloc[0]['group']
                    bot_group = df_demo.iloc[-1]['group']
                    demo_ai_data = {
                        "Highest_Engagement_Group": top_group,
                        "Top_EI": round(df_demo.iloc[0]['ei_mean'], 1),
                        "Lowest_Engagement_Group": bot_group,
                        "Bottom_EI": round(df_demo.iloc[-1]['ei_mean'], 1)
                    }
                    prompt = (
                        f"Bạn là chuyên gia phân tích nhân sự GHN. Người đọc vừa xem biểu đồ EI theo thâm niên."
                        f" Dưới đây là số liệu thực tế — chỉ dùng đúng những con số này:\n"
                        f"- Nhóm có EI cao nhất: {demo_ai_data['Highest_Engagement_Group']} ({demo_ai_data['Top_EI']:.1f}%)\n"
                        f"- Nhóm có EI thấp nhất: {demo_ai_data['Lowest_Engagement_Group']} ({demo_ai_data['Bottom_EI']:.1f}%)\n\n"
                        f"Viết theo 3 mục sau, mỗi mục 2-3 câu, tự nhiên như analyst đang tóm tắt cho Giám Đốc Nhân Sự:\n"
                        f"- **Nhóm gắn kết cao và thấp:** [so sánh hai nhóm, khoảng cách đó lớn hay nhỏ trong bối cảnh tổ chức]\n"
                        f"- **Ý nghĩa với hành trình nhân viên:** [nhóm {demo_ai_data['Lowest_Engagement_Group']} đang trải qua giai đoạn gì, điều gì có thể đang xảy ra với họ]\n"
                        f"- **Đề xuất can thiệp:** [ưu tiên cụ thể cho nhóm có EI thấp, lý do ngắn gọn]\n\n"
                        f"Chỉ dùng đúng các con số đã cung cấp. Không nhắc tên framework hay học thuật."
                    )
                    render_ai_insight_card("AI Demographic Insight", demo_ai_data, prompt, custom_style="margin-top: 16px; padding: 20px;")

    else:
        st.info("Chưa có dữ liệu Nhân khẩu học trong các nhóm hiện tại.")

    # ══════════════════════════════════════════════════════════════
    # SECTION 4: EVP & NLP INSIGHTS
    # ══════════════════════════════════════════════════════════════
    st.markdown(section_header("EVP & Lắng Nghe Nhân Viên (NLP)", "Phân tích từ khóa từ câu hỏi mở — định vị Thương hiệu Tuyển dụng"), unsafe_allow_html=True)
    
    # Collect all NLP clean responses
    open_responses = []
    for c in df_total.columns:
        if c.endswith('_clean') and 'Q' in c:
            open_responses.extend(df_total[c].dropna().tolist())
            
    if open_responses:
        # Simple extraction of common words (simulating EVP model)
        from collections import Counter
        import re
        all_text = " ".join(open_responses).lower()
        words = re.findall(r'\b[a-z_àáãạảăẵẳâầấậẫẩđèéẹẻẽêềếệểễìíịỉĩòóọỏõôồốộổỗơờớợởỡùúụủũưừứựửữỳýỵỷỹ]{3,}\b', all_text)
        
        # Define some key EVP buckets manually for GHN context based on NLP Expert Report
        evp_buckets = {
            'Phạt & Truy thu (INCOME_Penalty)': ['phạt', 'trừ', 'truy thu', 'đền', 'bắt đền', 'đơn giá', 'sai địa chỉ'],
            'Minh bạch thu nhập (INCOME_Transparency)': ['minh bạch', 'cách tính', 'không rõ', 'chưa rõ', 'thắc mắc lương'],
            'Lương & Phụ cấp cơ bản (INCOME_Base)': ['lương', 'thưởng', 'thu nhập', 'phụ cấp', 'xăng', 'tiền', 'chế độ'],
            'Quá tải công việc (BURNOUT_Overload)': ['quá tải', 'mệt', 'nhiều việc', 'áp lực', 'báo cáo', 'đuối'],
            'Thiếu ngày nghỉ (BURNOUT_NoRest)': ['ngày nghỉ', 'nghỉ phép', 'không được nghỉ', 'làm suốt', 'nghỉ ngơi', 'chủ nhật'],
            'Hỗ trợ từ quản lý (MGR_Support)': ['quản lý', 'sếp', 'hỗ trợ', 'tận tâm', 'giúp đỡ', 'tbc', 'am', 'lãnh đạo'],
            'Lộ trình phát triển (CAREER_Path)': ['thăng tiến', 'phát triển', 'lộ trình', 'tương lai', 'học hỏi', 'đào tạo'],
            'Quy trình & Công cụ (OPS_Process)': ['quy trình', 'thủ tục', 'rườm rà', 'hệ thống', 'app', 'lỗi', 'pda', 'chậm', 'thao tác'],
            'Đồng nghiệp & Môi trường (ENV_Team)': ['môi trường', 'đồng nghiệp', 'anh em', 'hòa đồng', 'vui vẻ', 'thân thiện', 'tập thể'],
            'Tự chủ thời gian (POS_Flexibility)': ['chủ động', 'thời gian', 'tự do', 'không gò bó', 'thoải mái', 'linh hoạt']
        }
        
        evp_counts = {k: 0 for k in evp_buckets.keys()}
        for k, keywords in evp_buckets.items():
            for kw in keywords:
                # Use simple count for the keyword in the entire text
                # We add a simple space padding check or regex word boundary
                pattern = r'\b' + re.escape(kw) + r'\b'
                evp_counts[k] += len(re.findall(pattern, all_text))
                    
        df_evp = pd.DataFrame(list(evp_counts.items()), columns=['EVP_Factor', 'Mentions']).sort_values('Mentions', ascending=True)
        
        c_evp1, c_evp2 = st.columns([1, 1.2])
        with c_evp1:
            fig_evp = go.Figure(go.Bar(
                y=df_evp['EVP_Factor'], x=df_evp['Mentions'],
                orientation='h', marker_color=COLORS['blue'],
                text=df_evp['Mentions'], textposition='inside'
            ))
            fig_evp = fig_card(fig_evp, 'Từ khóa EVP nổi bật', 'Tần suất được nhắc đến trong câu hỏi mở')
            st.plotly_chart(fig_evp, width='stretch', key="company_overview_chart_406")
            
        with c_evp2:
            df_evp_ai = df_evp[df_evp['Mentions'] > 0]
            if df_evp_ai.empty:
                st.info("Chưa có đủ từ khóa để phân tích sâu.")
            else:
                nlp_ai_data = {
                    "EVP_Buckets_Frequencies": df_evp_ai.set_index('EVP_Factor')['Mentions'].to_dict(),
                    "Top_Bucket": df_evp_ai.iloc[-1]['EVP_Factor'],
                    "Bottom_Bucket_with_mentions": df_evp_ai.iloc[0]['EVP_Factor']
                }
                prompt = (
                    f"Bạn là chuyên gia phân tích nhân sự GHN. Người đọc vừa xem biểu đồ tần suất chủ đề từ các câu trả lời mở của nhân viên."
                    f" Dưới đây là dữ liệu thực tế — chỉ nhắc đến các chủ đề có mentions > 0:\n"
                    f"{nlp_ai_data['EVP_Buckets_Frequencies']}\n\n"
                    f"Viết theo 3 mục sau, mỗi mục 2-3 câu, tự nhiên như analyst đang giải thích biểu đồ cho Giám Đốc:\n"
                    f"- **Chủ đề được nhắc nhiều nhất:** [đây là chủ đề {nlp_ai_data['Top_Bucket']} — điều đó phản ánh gì về điều nhân viên đang thực sự quan tâm hoặc muốn nói]\n"
                    f"- **Chủ đề ít được nhắc nhất:** [đó là tín hiệu tốt hay là khoảng trống cần chú ý — phân tích ngắn gọn]\n"
                    f"- **Định hướng EVP:** [dựa trên toàn bộ dữ liệu, tổ chức nên ưu tiên cải thiện hoặc duy trì yếu tố nào để thu hút và giữ chân nhân tài]\n\n"
                    f"Chỉ dùng đúng các con số đã cung cấp. Không nhắc tên framework hay học thuật."
                )
                render_ai_insight_card("AI NLP Insight: Định Vị Thương Hiệu (EVP)", nlp_ai_data, prompt, badge="NLP Engine", custom_style="height: 100%; margin-bottom: 0; padding: 24px;")
    else:
        st.info("Chưa có dữ liệu câu hỏi mở (NLP) để phân tích EVP.")

