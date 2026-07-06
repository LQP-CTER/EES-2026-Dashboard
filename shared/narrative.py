"""
Narrative Generator — EES 2026
Auto-generate insight paragraphs từ dữ liệu phân tích.
"""

from shared.codebook import classify_ei


def narrative_kpi_summary(group_name, n_total, n_clean, ei, enps, mei, intent_pct_low=None, burnout_high_pct=None):
    """Sinh paragraph tổng kết KPI chính."""
    ei_class = classify_ei(ei)
    ei_emoji = {'Xuất sắc': '', 'Khỏe mạnh': '', 'Cần theo dõi': '', 'Nghiêm trọng': ''}.get(ei_class, '')
    enps_label = 'Xuất sắc' if enps >= 50 else ('Tốt' if enps >= 30 else ('Ổn' if enps >= 0 else 'Cần cải thiện'))

    lines = [
        f"{ei_emoji} **{group_name}** thu được **{n_clean:,}** phản hồi hợp lệ (trên {n_total:,} tổng).",
        f"Chỉ số gắn kết (EI) đạt **{ei:.1f}%** — mức **{ei_class}**.",
        f"eNPS = **{enps:+.0f}** ({enps_label}), cho thấy {'đa số nhân viên sẵn sàng giới thiệu GHN' if enps >= 30 else 'cần cải thiện trải nghiệm nhân viên'}.",
        f"Hiệu quả quản lý trực tiếp (MEI) = **{mei:.1f}%**{'.' if mei >= 70 else ' — cần cải thiện vai trò quản lý.'}",
    ]
    if intent_pct_low is not None and intent_pct_low > 10:
        lines.append(f" **{intent_pct_low:.1f}%** nhân viên có ý định rời trong 3 tháng tới.")
    if burnout_high_pct is not None and burnout_high_pct > 20:
        lines.append(f" **{burnout_high_pct:.1f}%** nhân viên có dấu hiệu burnout cao.")

    return '\n'.join(lines)


def narrative_pillar(pillar_scores, pillar_labels):
    """Sinh insight cho 5 trụ cột."""
    sorted_p = sorted(pillar_scores.items(), key=lambda x: x[1])
    weakest = sorted_p[0]
    strongest = sorted_p[-1]
    gap = strongest[1] - weakest[1]

    weak_label = pillar_labels.get(weakest[0], weakest[0])
    strong_label = pillar_labels.get(strongest[0], strongest[0])

    lines = [
        f" Trụ cột mạnh nhất: **{strong_label}** ({strongest[1]:.1f}%). "
        f"Trụ cột yếu nhất: **{weak_label}** ({weakest[1]:.1f}%).",
        f"Khoảng cách giữa trụ cột mạnh và yếu nhất: **{gap:.1f} điểm %** — "
        f"{'cho thấy sự chênh lệch đáng kể cần hành động.' if gap > 15 else 'mức chênh lệch bình thường.'}",
    ]

    # Flag pillars below 50%
    below_50 = [p for p, v in sorted_p if v < 50]
    if below_50:
        below_labels = ', '.join([pillar_labels.get(p, p) for p in below_50])
        lines.append(f" Trụ cột dưới ngưỡng 50%: **{below_labels}** — cần hành động khẩn cấp.")

    return '\n'.join(lines)


def narrative_comparison(df_grouped, metric_col, group_col, metric_name='EI', top_n=3):
    """Sinh insight so sánh top vs bottom."""
    df_s = df_grouped.sort_values(metric_col, ascending=False)
    top = df_s.head(top_n)
    bottom = df_s.tail(top_n)

    top_names = ', '.join([f"**{r[group_col]}** ({r[metric_col]:.1f})" for _, r in top.iterrows()])
    bot_names = ', '.join([f"**{r[group_col]}** ({r[metric_col]:.1f})" for _, r in bottom.iterrows()])

    gap = top[metric_col].mean() - bottom[metric_col].mean()

    lines = [
        f" Top {top_n} {metric_name}: {top_names}",
        f" Bottom {top_n} {metric_name}: {bot_names}",
        f" Chênh lệch TB giữa top và bottom: **{gap:.1f} điểm** — "
        f"{'khoảng cách lớn, cần tìm hiểu nguyên nhân.' if gap > 20 else 'khoảng cách vừa phải.'}",
    ]
    return '\n'.join(lines)


def narrative_demographics(demo_results):
    """Sinh insight từ phân tích nhân khẩu học."""
    lines = []
    if 'generation' in demo_results:
        gen = demo_results['generation']
        if gen:
            best_gen = max(gen.items(), key=lambda x: x[1])
            worst_gen = min(gen.items(), key=lambda x: x[1])
            lines.append(
                f" **{best_gen[0]}** có EI cao nhất ({best_gen[1]:.1f}%), "
                f"**{worst_gen[0]}** thấp nhất ({worst_gen[1]:.1f}%)."
            )

    if 'tenure' in demo_results:
        ten = demo_results['tenure']
        if ten:
            # Detect honeymoon effect
            items = list(ten.items())
            if len(items) >= 3 and items[0][1] > items[2][1]:
                lines.append(
                    f" Phát hiện **hiệu ứng trăng mật**: nhóm mới ({items[0][0]}) "
                    f"gắn kết {items[0][1]:.1f}%, giảm xuống {items[2][1]:.1f}% "
                    f"sau {items[2][0]}."
                )

    return '\n'.join(lines) if lines else 'Không đủ dữ liệu nhân khẩu học để phân tích.'


def narrative_retention(pct_at_risk, top_risk_groups):
    """Sinh insight retention risk."""
    lines = [
        f" **{pct_at_risk:.1f}%** nhân viên có ý định rời (Q30 ≤ 2) trong 3 tháng tới.",
    ]
    if top_risk_groups:
        risk_items = ', '.join([f"**{g}** ({p:.0f}%)" for g, p in top_risk_groups[:5]])
        lines.append(f" Nhóm rủi ro cao nhất: {risk_items}")

    if pct_at_risk > 20:
        lines.append(" Tỷ lệ rủi ro vượt ngưỡng 20% — cần chương trình giữ chân ngay lập tức.")
    elif pct_at_risk > 10:
        lines.append(" Tỷ lệ rủi ro 10-20% — cần theo dõi sát và can thiệp sớm.")

    return '\n'.join(lines)


def narrative_action_priorities(top_priorities, maintain_items):
    """Sinh tổng kết hành động ưu tiên."""
    lines = ['##  3 Hành động ưu tiên', '']
    for i, (q, name, corr, score) in enumerate(top_priorities[:3], 1):
        lines.append(
            f"**{i}. {name}** ({q}): Điểm {score:.2f}/5, tương quan {corr:.3f} với EI. "
            f"{'Điểm thấp + ảnh hưởng lớn → ưu tiên cải thiện.' if score < 3.5 else 'Điểm trung bình, cần nâng lên.'}"
        )
    lines.append('')
    if maintain_items:
        maintain_names = ', '.join([f"{name} ({q})" for q, name, _, _ in maintain_items[:3]])
        lines.append(f" **Duy trì**: {maintain_names} — đang tốt, tiếp tục phát huy.")

    return '\n'.join(lines)
