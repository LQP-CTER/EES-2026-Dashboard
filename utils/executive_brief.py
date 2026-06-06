"""Executive brief and 30-60-90 plan helpers."""

import pandas as pd


def _phase_from_window(window: str) -> str:
    text = str(window or "")
    if "7" in text or "14" in text:
        return "0-30 ngày"
    if "30" in text:
        return "30-60 ngày"
    return "60-90 ngày"


def build_30_60_90_plan(action_queue: pd.DataFrame) -> pd.DataFrame:
    """Convert action queue into a compact implementation plan."""
    if action_queue is None or action_queue.empty:
        return pd.DataFrame()
    plan = action_queue.copy()
    plan["Giai đoạn"] = plan["Thời hạn"].apply(_phase_from_window)
    plan["Kết quả mong đợi"] = plan.apply(
        lambda r: (
            "Có nguyên nhân giữ chân rõ ràng và owner xử lý"
            if "Muốn nghỉ" in str(r.get("Vấn đề chính", ""))
            else "Giảm nhiễu vận hành và có mốc theo dõi lại"
            if "Burnout" in str(r.get("Vấn đề chính", "")) or "workload" in str(r.get("Vấn đề chính", "")).lower()
            else "Có quyết định can thiệp cụ thể cho nhóm rủi ro"
        ),
        axis=1,
    )
    cols = [
        "Giai đoạn", "Ưu tiên", "Nguồn", "Đối tượng", "N", "Risk Score",
        "Vấn đề chính", "Owner gợi ý", "Hành động", "Kết quả mong đợi",
    ]
    return plan[[c for c in cols if c in plan.columns]].reset_index(drop=True)


def build_executive_brief(action_queue: pd.DataFrame, lifecycle: dict | None, cross_priority: dict | None) -> dict:
    """Build report-ready bullets from the current pillar risk blocks."""
    if action_queue is None or action_queue.empty:
        return {"enabled": False}

    top = action_queue.iloc[0]
    immediate_n = int((action_queue["Ưu tiên"] == "Immediate").sum()) if "Ưu tiên" in action_queue.columns else 0
    high_n = int((action_queue["Ưu tiên"] == "High").sum()) if "Ưu tiên" in action_queue.columns else 0
    top_owner = action_queue["Owner gợi ý"].mode().iloc[0] if "Owner gợi ý" in action_queue.columns and not action_queue["Owner gợi ý"].mode().empty else "N/A"

    lifecycle_text = "Chưa có lifecycle signal nổi bật."
    if lifecycle and lifecycle.get("enabled"):
        worst = lifecycle.get("worst", {})
        lifecycle_text = (
            f"Cohort thâm niên cần chú ý nhất: {worst.get('Thâm niên', 'N/A')} "
            f"(N={worst.get('N', 0)}, Risk={worst.get('Risk Score', 0)})."
        )

    cross_text = "Chưa có cross-pillar hotspot nổi bật."
    if cross_priority and cross_priority.get("enabled"):
        x = cross_priority.get("top", {})
        cross_text = (
            f"Hotspot liên trụ cột: {x.get('Cấp', '')} {x.get('Đơn vị', 'N/A')} "
            f"với cặp {x.get('Trụ cột đang xem', 'N/A')} + {x.get('Trụ cột đi kèm', 'N/A')}."
        )

    plan_df = build_30_60_90_plan(action_queue)
    owner_summary = (
        action_queue.groupby("Owner gợi ý")
        .agg(action_count=("Đối tượng", "count"), avg_risk=("Risk Score", "mean"))
        .reset_index()
        .sort_values(["action_count", "avg_risk"], ascending=[False, False])
    )

    return {
        "enabled": True,
        "headline": f"Ưu tiên số 1: {top.get('Đối tượng')} - {top.get('Vấn đề chính')}",
        "bullets": [
            f"Tổng số hành động đề xuất: {len(action_queue)}; trong đó Immediate={immediate_n}, High={high_n}.",
            f"Owner cần vào cuộc nhiều nhất: {top_owner}.",
            lifecycle_text,
            cross_text,
        ],
        "plan_df": plan_df,
        "owner_summary": owner_summary,
    }
