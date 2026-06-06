"""Unified priority action queue for risk findings."""

import pandas as pd

from utils.segment_risk import MIN_SEGMENT_N, scan_risk_segments


SEGMENT_ACTIONS = {
    "Muốn nghỉ cao": ("HRBP + quản lý trực tiếp", "7 ngày", "Phỏng vấn giữ chân 10-15 người trong segment; xác định 3 nguyên nhân nghỉ gần nhất."),
    "Burnout cao": ("Ops owner", "14 ngày", "Rà tải công việc, lịch/ca và hỗ trợ vận hành; xử lý điểm nghẽn áp lực trước."),
    "eNPS âm": ("HRBP", "14 ngày", "Gom phản hồi mở tiêu cực thành 3 chủ đề; xử lý vấn đề cụ thể trước khi truyền thông rộng."),
    "Điểm trụ cột thấp": ("Pillar owner", "30 ngày", "Đi vào trụ cột/câu hỏi yếu nhất và chọn 1 hành động có thể hoàn tất trong 2-4 tuần."),
    "EI thấp": ("HRBP + unit head", "30 ngày", "Chạy pulse check ngắn và so với nhóm cùng cấp để xác định rủi ro cục bộ hay hệ thống."),
}


def _urgency(score: float) -> str:
    if score >= 55:
        return "Immediate"
    if score >= 40:
        return "High"
    return "Watch"


def _append_segment_actions(rows: list, df: pd.DataFrame, pillar_id: str | None, limit: int) -> None:
    risk_df = scan_risk_segments(df, pillar_filter=pillar_id, min_n=MIN_SEGMENT_N, top_n=limit)
    if risk_df.empty:
        return
    for _, row in risk_df.head(limit).iterrows():
        driver = row.get("Primary Driver", "EI thấp")
        owner, window, action = SEGMENT_ACTIONS.get(driver, SEGMENT_ACTIONS["EI thấp"])
        score = float(row.get("Risk Score", 0))
        rows.append({
            "Nguồn": "Segment Risk",
            "Đối tượng": f"{row.get('Segment Type')} · {row.get('Segment')}",
            "N": int(row.get("N", 0)),
            "Risk Score": round(score, 1),
            "Ưu tiên": _urgency(score),
            "Vấn đề chính": driver,
            "Owner gợi ý": owner,
            "Thời hạn": window,
            "Hành động": action,
        })


def _append_lifecycle_action(rows: list, lifecycle: dict) -> None:
    if not lifecycle or not lifecycle.get("enabled"):
        return
    worst = lifecycle.get("worst", {})
    playbook = lifecycle.get("playbook", {})
    score = float(worst.get("Risk Score", 0) or 0)
    rows.append({
        "Nguồn": "Lifecycle Risk",
        "Đối tượng": worst.get("Thâm niên", "Cohort thâm niên"),
        "N": int(worst.get("N", 0) or 0),
        "Risk Score": round(score, 1),
        "Ưu tiên": _urgency(score),
        "Vấn đề chính": playbook.get("focus", "Cohort thâm niên rủi ro"),
        "Owner gợi ý": "HRBP + quản lý tuyến",
        "Thời hạn": "30 ngày",
        "Hành động": playbook.get("action", "Đào sâu cohort thâm niên rủi ro nhất và xác định điểm vỡ kỳ vọng."),
    })


def _append_cross_pillar_actions(rows: list, cross_priority: dict, limit: int) -> None:
    if not cross_priority or not cross_priority.get("enabled"):
        return
    risk_df = cross_priority.get("risk_df", pd.DataFrame())
    if risk_df.empty:
        return
    for _, row in risk_df.head(limit).iterrows():
        score = float(row.get("Risk Score", 0) or 0)
        rows.append({
            "Nguồn": "Cross-Pillar",
            "Đối tượng": f"{row.get('Cấp')} · {row.get('Đơn vị')}",
            "N": int(row.get("N", 0) or 0),
            "Risk Score": round(score, 1),
            "Ưu tiên": _urgency(score),
            "Vấn đề chính": row.get("Pattern", "Cross-pillar risk"),
            "Owner gợi ý": "Pillar owners + unit head",
            "Thời hạn": "30 ngày",
            "Hành động": row.get("Next action", "Xử lý đồng thời hai trụ cột yếu nhất thay vì tách silo."),
        })


def build_priority_action_queue(
    df: pd.DataFrame,
    group_id: str,
    pillar_id: str | None = None,
    lifecycle: dict | None = None,
    cross_priority: dict | None = None,
    limit_per_source: int = 5,
) -> pd.DataFrame:
    """Combine segment, lifecycle and cross-pillar findings into one action queue."""
    rows = []
    _append_segment_actions(rows, df, pillar_id, limit_per_source)
    _append_lifecycle_action(rows, lifecycle or {})
    _append_cross_pillar_actions(rows, cross_priority or {}, limit_per_source)
    if not rows:
        return pd.DataFrame()

    out = pd.DataFrame(rows)
    priority_order = {"Immediate": 0, "High": 1, "Watch": 2}
    out["_priority_order"] = out["Ưu tiên"].map(priority_order).fillna(9)
    return (
        out.sort_values(["_priority_order", "Risk Score", "N"], ascending=[True, False, False])
        .drop(columns=["_priority_order"])
        .head(12)
        .reset_index(drop=True)
    )
