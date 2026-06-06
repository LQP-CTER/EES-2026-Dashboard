"""Cross-pillar priority scan for unit-level risk."""

import numpy as np
import pandas as pd

from shared.codebook import PILLAR_META, PILLAR_ORDER
from utils.segment_risk import MIN_SEGMENT_N, _weighted_avg, _weighted_pct


UNIT_LEVELS = {
    "region": "Vùng",
    "division": "Division",
    "department": "Department",
    "section": "Section",
}


PAIR_PLAYBOOK = {
    ("TC1", "TC2"): ("Direction-to-manager gap", "Kiểm tra cascade thông tin: lãnh đạo nói gì, quản lý trực tiếp diễn giải và hỗ trợ ra sao."),
    ("TC1", "TC3"): ("Strategy-to-execution gap", "Rà lại thay đổi quy trình/công cụ: nhân viên có tin định hướng nhưng không vận hành được trơn tru."),
    ("TC1", "TC4"): ("Trust-to-fairness gap", "Ưu tiên minh bạch cơ chế thu nhập/phạt/đánh giá vì thiếu công bằng sẽ làm mất niềm tin nhanh."),
    ("TC1", "TC5"): ("Trust-to-belonging gap", "Điều tra cảm giác tự hào, an toàn tâm lý và kết nối với tổ chức ở nhóm này."),
    ("TC2", "TC3"): ("Manager-workload friction", "Quản lý trực tiếp cần xử lý workload, công cụ, lịch/ca hoặc hỗ trợ xử lý sự cố trước."),
    ("TC2", "TC4"): ("Fairness execution risk", "Đây thường là rủi ro công bằng trong phân bổ, đánh giá hoặc xử lý quyền lợi. Cần audit cách quản lý áp dụng chính sách."),
    ("TC2", "TC5"): ("Local culture risk", "Can thiệp ở cấp quản lý trực tiếp: ghi nhận, phản hồi, xử lý xung đột và an toàn tâm lý."),
    ("TC3", "TC4"): ("Workload-pay exchange risk", "So lại trao đổi công sức - thu nhập: workload/OT/công cụ có đang làm nhân viên thấy không đáng công."),
    ("TC3", "TC5"): ("Burnout environment risk", "Ưu tiên giảm áp lực vận hành và cải thiện điều kiện làm việc trước khi truyền thông gắn kết."),
    ("TC4", "TC5"): ("Reward-pride erosion", "Nếu thu nhập/công bằng thấp kéo theo tự hào thấp, cần xử lý quyền lợi cụ thể trước các hoạt động văn hóa."),
}


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


def _pair_key(a: str, b: str) -> tuple[str, str]:
    return tuple(sorted([a, b], key=PILLAR_ORDER.index))


def _pair_playbook(selected: str, companion: str) -> dict:
    title, action = PAIR_PLAYBOOK.get(
        _pair_key(selected, companion),
        ("Cross-pillar risk", "Đào sâu hai trụ cột thấp nhất cùng lúc; tránh xử lý từng vấn đề như các silo tách rời."),
    )
    return {"pattern": title, "action": action}


def build_cross_pillar_priority(
    df: pd.DataFrame,
    selected_pillar: str,
    min_n: int = MIN_SEGMENT_N,
    threshold: float = 65.0,
    top_n: int = 18,
) -> dict:
    """Find units where the selected pillar co-occurs with another weak pillar."""
    if df is None or df.empty:
        return {"enabled": False, "reason": "empty_data"}

    pillar_cols = [f"{p}_pct" for p in PILLAR_ORDER if f"{p}_pct" in df.columns]
    selected_col = f"{selected_pillar}_pct"
    if selected_col not in df.columns or len(pillar_cols) < 2:
        return {"enabled": False, "reason": "missing_pillar_columns"}

    rows = []
    for unit_col, unit_label in UNIT_LEVELS.items():
        if unit_col not in df.columns:
            continue
        valid = df[unit_col].notna() & (df[unit_col].astype(str).str.strip() != "")
        for unit_value, grp_idx in df.loc[valid, [unit_col]].groupby(unit_col).groups.items():
            grp = df.loc[grp_idx]
            if len(grp) < min_n:
                continue

            scores = {
                p: _weighted_avg(grp, f"{p}_pct")
                for p in PILLAR_ORDER
                if f"{p}_pct" in grp.columns
            }
            selected_score = scores.get(selected_pillar, np.nan)
            if np.isnan(selected_score):
                continue

            other_scores = {p: v for p, v in scores.items() if p != selected_pillar and not np.isnan(v)}
            if not other_scores:
                continue
            companion = min(other_scores, key=other_scores.get)
            companion_score = other_scores[companion]
            low_pillars = [p for p, score in scores.items() if not np.isnan(score) and score < threshold]
            if selected_score >= threshold and companion_score >= threshold:
                continue

            flight = _flight_risk(grp)
            burnout = _burnout_pct(grp)
            risk_score = (
                max(0, threshold - selected_score) * 0.32
                + max(0, threshold - companion_score) * 0.28
                + max(0, len(low_pillars) - 1) * 7
                + (0 if np.isnan(flight) else flight) * 0.22
                + (0 if np.isnan(burnout) else burnout) * 0.18
            )
            playbook = _pair_playbook(selected_pillar, companion)
            rows.append({
                "Cấp": unit_label,
                "Đơn vị": str(unit_value),
                "N": int(len(grp)),
                "Trụ cột đang xem": selected_pillar,
                "Điểm trụ cột": round(float(selected_score), 1),
                "Trụ cột đi kèm": companion,
                "Điểm đi kèm": round(float(companion_score), 1),
                "Số trụ cột <65": len(low_pillars),
                "% Muốn nghỉ": round(float(flight), 1) if not np.isnan(flight) else np.nan,
                "% Burnout": round(float(burnout), 1) if not np.isnan(burnout) else np.nan,
                "Risk Score": round(float(risk_score), 1),
                "Pattern": playbook["pattern"],
                "Next action": playbook["action"],
            })

    if not rows:
        return {"enabled": False, "reason": "no_cross_pillar_risk"}

    risk_df = pd.DataFrame(rows).sort_values(["Risk Score", "N"], ascending=[False, False]).head(top_n).reset_index(drop=True)
    companion_df = (
        risk_df.groupby("Trụ cột đi kèm")
        .agg(unit_count=("Đơn vị", "count"), avg_risk=("Risk Score", "mean"))
        .reset_index()
        .sort_values(["unit_count", "avg_risk"], ascending=[False, False])
    )
    companion_df["Tên trụ cột"] = companion_df["Trụ cột đi kèm"].map(
        {p: PILLAR_META.get(p, {}).get("short", p) for p in PILLAR_ORDER}
    )
    top = risk_df.iloc[0].to_dict()
    return {
        "enabled": True,
        "risk_df": risk_df,
        "companion_df": companion_df,
        "top": top,
        "selected_label": PILLAR_META.get(selected_pillar, {}).get("short", selected_pillar),
    }
