"""
Segment Risk Scan helpers.

This module adds a lightweight, directional scan across available workforce
segments without replacing the existing pillar drilldowns.
"""

import numpy as np
import pandas as pd

from shared.codebook import PILLAR_META, PILLAR_ORDER, get_pillar_questions, get_question_label


MIN_SEGMENT_N = 5
DEFAULT_SEGMENT_COLS = [
    "region",
    "division",
    "department",
    "section",
    "tenure_label",
    "prev_company_cat",
]

SEGMENT_LABELS = {
    "region": "Vùng",
    "division": "Division",
    "department": "Department",
    "section": "Section",
    "tenure_label": "Thâm niên",
    "prev_company_cat": "Nguồn trước GHN",
}


def _weights(df: pd.DataFrame) -> pd.Series:
    w = df.get("CompanyRollup_Weight", pd.Series(1.0, index=df.index))
    w = pd.to_numeric(w, errors="coerce").fillna(1.0).clip(lower=0)
    return w


def _weighted_avg(df: pd.DataFrame, col: str) -> float:
    if col not in df.columns:
        return np.nan
    vals = pd.to_numeric(df[col], errors="coerce")
    mask = vals.notna()
    if not mask.any():
        return np.nan
    w = _weights(df).loc[mask]
    if w.sum() <= 0:
        return float(vals.loc[mask].mean())
    return float(np.average(vals.loc[mask], weights=w))


def _weighted_pct(df: pd.DataFrame, condition: pd.Series, valid: pd.Series | None = None) -> float:
    if valid is None:
        valid = pd.Series(True, index=df.index)
    valid = valid.reindex(df.index).fillna(False).astype(bool)
    if not valid.any():
        return np.nan
    w = _weights(df)
    total = w.loc[valid].sum()
    if total <= 0:
        return np.nan
    condition = condition.reindex(df.index).fillna(False).astype(bool)
    return float(w.loc[condition & valid].sum() / total * 100)


def _risk_level(score: float) -> str:
    if score >= 55:
        return "Critical"
    if score >= 40:
        return "Warning"
    return "Watch"


def _primary_driver(ei_gap: float, flight: float, burnout: float, enps_drag: float, pillar_gap: float) -> str:
    candidates = {
        "EI thấp": max(ei_gap, 0),
        "Muốn nghỉ cao": max(flight, 0),
        "Burnout cao": max(burnout, 0),
        "eNPS âm": max(enps_drag, 0),
    }
    if not np.isnan(pillar_gap):
        candidates["Điểm trụ cột thấp"] = max(pillar_gap, 0)
    return max(candidates, key=candidates.get)


def _segment_record(
    df_seg: pd.DataFrame,
    segment_col: str,
    segment_value,
    pillar_filter: str | None,
) -> dict:
    n = int(len(df_seg))
    ei = _weighted_avg(df_seg, "EI")
    mei = _weighted_avg(df_seg, "MEI")
    jsi = _weighted_avg(df_seg, "JSI")

    enps = np.nan
    if "eNPS" in df_seg.columns:
        enps_col = pd.to_numeric(df_seg["eNPS"], errors="coerce")
        valid_enps = enps_col.notna()
        enps = _weighted_pct(df_seg, enps_col >= 9, valid_enps) - _weighted_pct(df_seg, enps_col <= 6, valid_enps)

    flight = np.nan
    if "intent" in df_seg.columns:
        intent_col = pd.to_numeric(df_seg["intent"], errors="coerce")
        flight = _weighted_pct(df_seg, intent_col <= 2, intent_col.notna())

    burnout = np.nan
    if "burnout_proxy" in df_seg.columns:
        burnout = _weighted_pct(df_seg, df_seg["burnout_proxy"].fillna(False).astype(bool))
    elif "burnout_risk" in df_seg.columns:
        burnout = _weighted_pct(df_seg, pd.to_numeric(df_seg["burnout_risk"], errors="coerce").fillna(0) > 0)
    elif "burnout_score" in df_seg.columns:
        burnout = _weighted_pct(df_seg, pd.to_numeric(df_seg["burnout_score"], errors="coerce") >= 50)

    pillar_score = np.nan
    if pillar_filter:
        p_col = f"{pillar_filter}_pct"
        pillar_score = _weighted_avg(df_seg, p_col)

    ei_gap = 100 - ei if not np.isnan(ei) else 0
    flight_score = 0 if np.isnan(flight) else flight
    burnout_score = 0 if np.isnan(burnout) else burnout
    enps_drag = 0 if np.isnan(enps) else max(0, -enps)
    pillar_gap = 100 - pillar_score if not np.isnan(pillar_score) else np.nan

    if not np.isnan(pillar_gap):
        risk_score = (
            ei_gap * 0.25
            + flight_score * 0.25
            + burnout_score * 0.18
            + enps_drag * 0.12
            + pillar_gap * 0.20
        )
    else:
        risk_score = (
            ei_gap * 0.35
            + flight_score * 0.30
            + burnout_score * 0.20
            + enps_drag * 0.15
        )

    record = {
        "_segment_col": segment_col,
        "_segment_value": segment_value,
        "Segment Type": SEGMENT_LABELS.get(segment_col, segment_col),
        "Segment": str(segment_value),
        "N": n,
        "Risk Level": _risk_level(risk_score),
        "Risk Score": round(float(risk_score), 1),
        "EI (%)": round(float(ei), 1) if not np.isnan(ei) else np.nan,
        "eNPS": round(float(enps), 0) if not np.isnan(enps) else np.nan,
        "MEI (%)": round(float(mei), 1) if not np.isnan(mei) else np.nan,
        "JSI (%)": round(float(jsi), 1) if not np.isnan(jsi) else np.nan,
        "% Muốn nghỉ": round(float(flight), 1) if not np.isnan(flight) else np.nan,
        "% Burnout": round(float(burnout), 1) if not np.isnan(burnout) else np.nan,
        "Primary Driver": _primary_driver(ei_gap, flight_score, burnout_score, enps_drag, pillar_gap),
    }
    if pillar_filter and not np.isnan(pillar_score):
        record[f"Điểm {pillar_filter} (%)"] = round(float(pillar_score), 1)
    return record


def scan_risk_segments(
    df: pd.DataFrame,
    segment_cols: list[str] | None = None,
    pillar_filter: str | None = None,
    min_n: int = MIN_SEGMENT_N,
    top_n: int = 20,
) -> pd.DataFrame:
    """Return highest-risk segments with only groups below min_n hidden."""
    if df is None or df.empty:
        return pd.DataFrame()

    segment_cols = segment_cols or DEFAULT_SEGMENT_COLS
    rows = []
    for col in segment_cols:
        if col not in df.columns:
            continue
        work = df[[col]].copy()
        valid_values = work[col].notna() & (work[col].astype(str).str.strip() != "")
        for value, grp_idx in work.loc[valid_values].groupby(col).groups.items():
            df_seg = df.loc[grp_idx]
            if len(df_seg) < min_n:
                continue
            rows.append(_segment_record(df_seg, col, value, pillar_filter))

    if not rows:
        return pd.DataFrame()
    out = pd.DataFrame(rows)
    return out.sort_values(["Risk Score", "N"], ascending=[False, False]).head(top_n).reset_index(drop=True)


def slice_segment(df: pd.DataFrame, segment_col: str, segment_value) -> pd.DataFrame:
    if df is None or df.empty or segment_col not in df.columns:
        return pd.DataFrame()
    return df.loc[df[segment_col] == segment_value].copy()


def build_segment_driver_profile(
    df: pd.DataFrame,
    group_id: str,
    segment_col: str,
    segment_value,
    min_n: int = MIN_SEGMENT_N,
) -> dict:
    """Build pillar and weakest-question diagnostics for one selected segment."""
    seg = slice_segment(df, segment_col, segment_value)
    if len(seg) < min_n:
        return {"enabled": False, "reason": "sample_too_small", "n": len(seg)}

    pillar_rows = []
    question_rows = []
    for pillar_id in PILLAR_ORDER:
        p_col = f"{pillar_id}_pct"
        if p_col in seg.columns:
            seg_score = _weighted_avg(seg, p_col)
            all_score = _weighted_avg(df, p_col)
        else:
            q_cols = [q for q in get_pillar_questions(group_id, pillar_id) if q in seg.columns]
            if not q_cols:
                continue
            seg_score = float(np.nanmean([_weighted_avg(seg, q) for q in q_cols]))
            all_score = float(np.nanmean([_weighted_avg(df, q) for q in q_cols]))
            seg_score = (seg_score - 1) / 4 * 100 if not np.isnan(seg_score) else np.nan
            all_score = (all_score - 1) / 4 * 100 if not np.isnan(all_score) else np.nan

        if np.isnan(seg_score):
            continue
        gap = seg_score - all_score if not np.isnan(all_score) else np.nan
        pillar_rows.append({
            "Trụ cột": f"{pillar_id} · {PILLAR_META.get(pillar_id, {}).get('short', pillar_id)}",
            "Mã": pillar_id,
            "Điểm segment": round(float(seg_score), 1),
            "Điểm toàn nhóm": round(float(all_score), 1) if not np.isnan(all_score) else np.nan,
            "Chênh lệch": round(float(gap), 1) if not np.isnan(gap) else np.nan,
        })

        for q in get_pillar_questions(group_id, pillar_id):
            if q not in seg.columns:
                continue
            seg_mean = _weighted_avg(seg, q)
            all_mean = _weighted_avg(df, q)
            vals = pd.to_numeric(seg[q], errors="coerce")
            valid = vals.notna()
            if valid.sum() < min_n or np.isnan(seg_mean):
                continue
            question_rows.append({
                "Trụ cột": pillar_id,
                "Câu hỏi": q,
                "Nhãn": get_question_label(group_id, q),
                "Điểm TB": round(float(seg_mean), 2),
                "% Tích cực": round(_weighted_pct(seg, vals >= 4, valid), 1),
                "% Tiêu cực": round(_weighted_pct(seg, vals <= 2, valid), 1),
                "Chênh toàn nhóm": round(float(seg_mean - all_mean), 2) if not np.isnan(all_mean) else np.nan,
                "N": int(valid.sum()),
            })

    pillar_df = pd.DataFrame(pillar_rows).sort_values("Điểm segment", ascending=True) if pillar_rows else pd.DataFrame()
    question_df = pd.DataFrame(question_rows).sort_values(["Điểm TB", "% Tiêu cực"], ascending=[True, False]) if question_rows else pd.DataFrame()
    return {
        "enabled": True,
        "n": len(seg),
        "segment_df": seg,
        "pillar_df": pillar_df,
        "question_df": question_df,
        "voice_signals": summarize_segment_voice_signals(seg),
    }


def _flatten_listlike(series: pd.Series) -> list:
    items = []
    for value in series.dropna():
        if isinstance(value, (list, tuple, set)):
            items.extend([str(v) for v in value if str(v).strip()])
        elif isinstance(value, str):
            text = value.strip()
            if not text:
                continue
            if text.startswith("[") and text.endswith("]"):
                text = text.strip("[]")
                parts = [p.strip().strip("'\"") for p in text.split(",")]
                items.extend([p for p in parts if p])
            else:
                items.append(text)
    return items


def summarize_segment_voice_signals(seg: pd.DataFrame) -> dict:
    """Summarize precomputed NLP columns for the selected segment, if available."""
    result = {"enabled": False}
    text_len = pd.to_numeric(seg.get("nlp_text_len", pd.Series(dtype=float)), errors="coerce")
    has_text = text_len.fillna(0) > 0
    text_n = int(has_text.sum())
    if text_n == 0 and "nlp_sentiment_label" not in seg.columns and "nlp_topics" not in seg.columns:
        return result

    result.update({"enabled": True, "text_n": text_n})
    if "nlp_sentiment_label" in seg.columns:
        labels = seg.loc[has_text, "nlp_sentiment_label"].astype(str)
        neg_n = int((labels == "tiêu_cực").sum())
        result["negative_n"] = neg_n
        result["negative_pct"] = round(neg_n / max(text_n, 1) * 100, 1)

    if "nlp_warning_signals" in seg.columns:
        warnings = _flatten_listlike(seg.loc[has_text, "nlp_warning_signals"])
        result["warning_n"] = len(warnings)
        result["top_warnings"] = pd.Series(warnings).value_counts().head(5).to_dict() if warnings else {}

    if "nlp_topics" in seg.columns:
        topics = _flatten_listlike(seg.loc[has_text, "nlp_topics"])
        result["top_topics"] = pd.Series(topics).value_counts().head(5).to_dict() if topics else {}

    return result
