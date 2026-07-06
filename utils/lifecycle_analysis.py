"""Tenure / lifecycle diagnostics for EES 2026."""

import numpy as np
import pandas as pd

from shared.codebook import get_pillar_questions, get_question_label
from utils.data_loader import EWS_TENURE_THRESHOLD, TENURE_LABELS
from utils.segment_risk import MIN_SEGMENT_N, _weighted_avg, _weighted_pct, summarize_segment_voice_signals


def _flight_risk(df: pd.DataFrame) -> float:
    if "intent" not in df.columns:
        return np.nan
    vals = pd.to_numeric(df["intent"], errors="coerce")
    return _weighted_pct(df, vals <= 2, vals.notna())


def _burnout_pct(df: pd.DataFrame) -> float:
    if "burnout_proxy" in df.columns:
        return _weighted_pct(df, df["burnout_proxy"].fillna(False).astype(bool))
    if "burnout_risk" in df.columns:
        return _weighted_pct(df, pd.to_numeric(df["burnout_risk"], errors="coerce").fillna(0) > 0)
    if "burnout_score" in df.columns:
        return _weighted_pct(df, pd.to_numeric(df["burnout_score"], errors="coerce") >= 50)
    return np.nan


def _enps(df: pd.DataFrame) -> float:
    if "eNPS" not in df.columns:
        return np.nan
    vals = pd.to_numeric(df["eNPS"], errors="coerce")
    valid = vals.notna()
    return _weighted_pct(df, vals >= 9, valid) - _weighted_pct(df, vals <= 6, valid)


def _weakest_question(df: pd.DataFrame, group_id: str, pillar_id: str | None) -> dict:
    q_cols = []
    if pillar_id:
        q_cols = [q for q in get_pillar_questions(group_id, pillar_id) if q in df.columns]
    if not q_cols:
        return {}

    rows = []
    for q in q_cols:
        vals = pd.to_numeric(df[q], errors="coerce")
        valid = vals.notna()
        if valid.sum() < MIN_SEGMENT_N:
            continue
        rows.append({
            "q": q,
            "label": get_question_label(group_id, q),
            "mean": _weighted_avg(df, q),
            "negative_pct": _weighted_pct(df, vals <= 2, valid),
        })
    if not rows:
        return {}
    worst = sorted(rows, key=lambda x: (x["mean"], -x["negative_pct"]))[0]
    return {
        "Câu yếu nhất": worst["q"],
        "Nhãn câu yếu": worst["label"],
        "Điểm câu yếu": round(float(worst["mean"]), 2),
        "% tiêu cực câu yếu": round(float(worst["negative_pct"]), 1),
    }


def _risk_score(ei: float, flight: float, burnout: float, enps: float, pillar_score: float = np.nan) -> float:
    score = (
        max(0, 100 - (0 if np.isnan(ei) else ei)) * 0.35
        + (0 if np.isnan(flight) else flight) * 0.30
        + (0 if np.isnan(burnout) else burnout) * 0.20
        + max(0, -(0 if np.isnan(enps) else enps)) * 0.15
    )
    if not np.isnan(pillar_score):
        score = score * 0.75 + max(0, 100 - pillar_score) * 0.25
    return float(score)


def build_lifecycle_risk(
    df: pd.DataFrame,
    group_id: str,
    pillar_id: str | None = None,
    min_n: int = MIN_SEGMENT_N,
) -> dict:
    """Summarize tenure cohorts with only cohorts below min_n hidden."""
    if df is None or df.empty or "tenure" not in df.columns:
        return {"enabled": False, "reason": "missing_tenure"}

    rows = []
    for tenure_idx, grp in df[df["tenure"].notna()].groupby("tenure"):
        if len(grp) < min_n:
            continue
        tenure_idx = int(tenure_idx)
        pillar_score = np.nan
        if pillar_id and f"{pillar_id}_pct" in grp.columns:
            pillar_score = _weighted_avg(grp, f"{pillar_id}_pct")

        ei = _weighted_avg(grp, "EI")
        flight = _flight_risk(grp)
        burnout = _burnout_pct(grp)
        enps = _enps(grp)
        risk_score = _risk_score(ei, flight, burnout, enps, pillar_score)

        row = {
            "tenure": tenure_idx,
            "Thâm niên": TENURE_LABELS[tenure_idx] if 0 <= tenure_idx < len(TENURE_LABELS) else str(tenure_idx),
            "N": int(len(grp)),
            "EI (%)": round(float(ei), 1) if not np.isnan(ei) else np.nan,
            "eNPS": round(float(enps), 0) if not np.isnan(enps) else np.nan,
            "% Muốn nghỉ": round(float(flight), 1) if not np.isnan(flight) else np.nan,
            "% Burnout": round(float(burnout), 1) if not np.isnan(burnout) else np.nan,
            "Risk Score": round(float(risk_score), 1),
        }
        if not np.isnan(pillar_score):
            row[f"Điểm {pillar_id} (%)"] = round(float(pillar_score), 1)
        row.update(_weakest_question(grp, group_id, pillar_id))
        rows.append(row)

    if not rows:
        return {"enabled": False, "reason": "not_enough_cohorts"}

    cohort_df = pd.DataFrame(rows).sort_values("tenure")
    risk_df = cohort_df.sort_values(["Risk Score", "N"], ascending=[False, False]).reset_index(drop=True)
    ews_threshold = EWS_TENURE_THRESHOLD.get(group_id, 2)
    early = cohort_df[cohort_df["tenure"] <= ews_threshold]
    mature = cohort_df[cohort_df["tenure"] > ews_threshold]
    early_gap = np.nan
    if not early.empty and not mature.empty:
        early_gap = round(float(mature["EI (%)"].mean() - early["EI (%)"].mean()), 1)

    cliff = None
    diffs = cohort_df.set_index("tenure")["EI (%)"].diff().dropna()
    if not diffs.empty and diffs.min() <= -6:
        cliff_idx = int(diffs.idxmin())
        cliff = {
            "label": TENURE_LABELS[cliff_idx] if 0 <= cliff_idx < len(TENURE_LABELS) else str(cliff_idx),
            "drop": round(float(diffs.min()), 1),
        }

    worst = risk_df.iloc[0].to_dict() if not risk_df.empty else {}
    worst_tenure = worst.get("tenure")
    worst_df = pd.DataFrame()
    voice_signals = {"enabled": False}
    if worst_tenure is not None:
        worst_df = df.loc[df["tenure"] == worst_tenure].copy()
        voice_signals = summarize_segment_voice_signals(worst_df)

    return {
        "enabled": True,
        "cohort_df": cohort_df,
        "risk_df": risk_df,
        "worst": worst,
        "worst_df": worst_df,
        "hotspots": lifecycle_hotspots(worst_df, pillar_id, min_n=min_n),
        "voice_signals": voice_signals,
        "playbook": lifecycle_playbook(worst, group_id),
        "ews_window": TENURE_LABELS[ews_threshold] if 0 <= ews_threshold < len(TENURE_LABELS) else str(ews_threshold),
        "early_gap": early_gap,
        "cliff": cliff,
    }


def lifecycle_hotspots(
    cohort_df: pd.DataFrame,
    pillar_id: str | None = None,
    min_n: int = MIN_SEGMENT_N,
) -> pd.DataFrame:
    """Find unit hotspots inside the highest-risk tenure cohort."""
    if cohort_df is None or cohort_df.empty:
        return pd.DataFrame()
    rows = []
    label_map = {
        "region": "Vùng",
        "division": "Division",
        "department": "Department",
        "section": "Section",
    }
    for col, label in label_map.items():
        if col not in cohort_df.columns:
            continue
        for value, grp in cohort_df.groupby(col):
            if pd.isna(value) or str(value).strip() == "" or len(grp) < min_n:
                continue
            ei = _weighted_avg(grp, "EI")
            flight = _flight_risk(grp)
            burnout = _burnout_pct(grp)
            enps = _enps(grp)
            pillar_score = _weighted_avg(grp, f"{pillar_id}_pct") if pillar_id and f"{pillar_id}_pct" in grp.columns else np.nan
            row = {
                "Cấp": label,
                "Đơn vị": str(value),
                "N": int(len(grp)),
                "EI (%)": round(float(ei), 1) if not np.isnan(ei) else np.nan,
                "% Muốn nghỉ": round(float(flight), 1) if not np.isnan(flight) else np.nan,
                "% Burnout": round(float(burnout), 1) if not np.isnan(burnout) else np.nan,
                "eNPS": round(float(enps), 0) if not np.isnan(enps) else np.nan,
                "Risk Score": round(_risk_score(ei, flight, burnout, enps, pillar_score), 1),
            }
            if not np.isnan(pillar_score):
                row[f"Điểm {pillar_id} (%)"] = round(float(pillar_score), 1)
            rows.append(row)
    if not rows:
        return pd.DataFrame()
    return pd.DataFrame(rows).sort_values(["Risk Score", "N"], ascending=[False, False]).head(12).reset_index(drop=True)


def lifecycle_playbook(worst: dict, group_id: str) -> dict:
    """Rule-based action prompt for the highest-risk tenure cohort."""
    tenure_idx = worst.get("tenure")
    label = worst.get("Thâm niên", "cohort được chọn")
    weak_q = worst.get("Câu yếu nhất")
    weak_label = worst.get("Nhãn câu yếu")
    weak_text = f" Câu cần soi kỹ: {weak_q} - {weak_label}." if weak_q and weak_label else ""

    if tenure_idx is None:
        focus = "Kiểm tra lại cohort thâm niên"
        action = "Xác minh mapping thâm niên và chọn cohort có đủ mẫu trước khi kết luận."
    elif tenure_idx <= EWS_TENURE_THRESHOLD.get(group_id, 2):
        focus = "Onboarding / early warning"
        action = "Thiết kế check-in tuần 2, 4, 8 và 12; ưu tiên quản lý trực tiếp, hướng dẫn quy trình và kỳ vọng thu nhập/công việc thực tế."
    elif tenure_idx <= 4:
        focus = "Giai đoạn thích nghi sau onboarding"
        action = "Kiểm tra điểm vỡ kỳ vọng sau 6-12 tháng: workload, công bằng phân bổ, cơ hội học việc và phản hồi từ quản lý."
    elif tenure_idx <= 5:
        focus = "Giai đoạn giữ chân 1-2 năm"
        action = "Mở career conversation và cơ chế ghi nhận; nhóm này thường cần thấy lộ trình phát triển hoặc lý do rõ ràng để tiếp tục ở lại."
    else:
        focus = "Nhân sự thâm niên / plateau risk"
        action = "Rà soát career plateau, vai trò mới và mức công nhận; dùng nhóm này làm nguồn mentor nếu engagement vẫn khỏe, hoặc can thiệp nếu điểm đang tụt."

    return {
        "focus": focus,
        "action": action + weak_text,
        "label": label,
    }
