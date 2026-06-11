"""
Unit Report data-prep helpers — EES 2026 Dashboard.

Cung cấp:
  - get_org_options(df)                         → {division: [...], department: [...], section: [...]}
  - build_unit_df(df, sel_div, sel_dept, sel_sec) → pd.DataFrame
  - get_unit_label(sel_div, sel_dept, sel_sec)   → str
  - get_unit_level(sel_div, sel_dept, sel_sec)   → 'division'|'department'|'section'|'group'
  - pillar_scores_comparison(df_unit, df_bench, group_id) → list[dict]
  - kpis_with_delta(df_unit, df_bench)           → dict (kpis + delta_ keys)
  - get_open_col(df)                             → str | None
  - get_participation_rate(df_unit, df_bench)    → float | None
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from shared.codebook import PILLAR_META, PILLAR_ORDER, get_pillar_questions
from utils.data_loader import compute_kpis

_BAD_VALS = frozenset({"nan", "none", "", "n/a", "không xác định", "unknown", "null"})


# ── Org options ───────────────────────────────────────────────────────

def get_org_options(df: pd.DataFrame) -> dict[str, list[str]]:
    """
    Trả về các giá trị hợp lệ cho division / department / section.
    """
    result: dict[str, list[str]] = {}
    for col in ("division", "department", "section"):
        if col in df.columns:
            vals = sorted([
                v for v in df[col].dropna().unique()
                if str(v).strip().lower() not in _BAD_VALS
            ])
            result[col] = vals
        else:
            result[col] = []
    return result


# ── Filter ────────────────────────────────────────────────────────────

def build_unit_df(
    df: pd.DataFrame,
    sel_div: str | None = None,
    sel_dept: str | None = None,
    sel_sec: str | None = None,
) -> pd.DataFrame:
    """
    Filter df về đơn vị được chọn. Trả về bản copy đã lọc.
    Nếu không có gì được chọn, trả về df gốc (copy).
    """
    out = df
    if sel_div and "division" in out.columns:
        out = out[out["division"] == sel_div]
    if sel_dept and "department" in out.columns:
        out = out[out["department"] == sel_dept]
    if sel_sec and "section" in out.columns:
        out = out[out["section"] == sel_sec]
    return out.copy()


# ── Label / Level ─────────────────────────────────────────────────────

def get_unit_label(
    sel_div: str | None,
    sel_dept: str | None,
    sel_sec: str | None,
) -> str:
    parts = [p for p in [sel_div, sel_dept, sel_sec] if p]
    return " / ".join(parts) if parts else "Toàn nhóm"


def get_unit_level(
    sel_div: str | None,
    sel_dept: str | None,
    sel_sec: str | None,
) -> str:
    """Trả về cấp thấp nhất đang được chọn."""
    if sel_sec:
        return "section"
    if sel_dept:
        return "department"
    if sel_div:
        return "division"
    return "group"


# ── Pillar comparison ─────────────────────────────────────────────────

def pillar_scores_comparison(
    df_unit: pd.DataFrame,
    df_bench: pd.DataFrame,
    group_id: str,
) -> list[dict]:
    """
    Tính điểm TB mỗi trụ cột cho unit và benchmark.

    Mỗi phần tử:
    {
        pillar_id, name, color,
        score_unit, score_bench, delta,
        n_questions, n_respondents,
        pct_unit,   # (score-1)/4*100 để dùng trong radar
        pct_bench,
    }
    """
    rows = []
    for p in PILLAR_ORDER:
        qs = [q for q in get_pillar_questions(group_id, p) if q in df_unit.columns]
        if not qs:
            continue
        u_vals = (
            df_unit[qs]
            .apply(pd.to_numeric, errors="coerce")
            .mean(axis=1)
            .dropna()
        )
        b_vals = (
            df_bench[qs]
            .apply(pd.to_numeric, errors="coerce")
            .mean(axis=1)
            .dropna()
        )
        if len(u_vals) < 3:
            continue
        score_u = float(u_vals.mean())
        score_b = float(b_vals.mean()) if len(b_vals) >= 3 else None
        delta = round(score_u - score_b, 2) if score_b is not None else None
        rows.append({
            "pillar_id": p,
            "name": PILLAR_META[p]["name"],
            "color": PILLAR_META[p].get("color", "#FF5200"),
            "score_unit": round(score_u, 2),
            "score_bench": round(score_b, 2) if score_b is not None else None,
            "delta": delta,
            "n_questions": len(qs),
            "n_respondents": int(len(u_vals)),
            "pct_unit": round((score_u - 1) / 4 * 100, 1),
            "pct_bench": round((score_b - 1) / 4 * 100, 1) if score_b is not None else None,
        })
    return rows


# ── KPIs with delta ───────────────────────────────────────────────────

def kpis_with_delta(df_unit: pd.DataFrame, df_bench: pd.DataFrame) -> dict:
    """
    Tính KPIs cho unit và benchmark, trả về dict có cả delta_ và bench_ keys.
    """
    ku = compute_kpis(df_unit)
    kb = compute_kpis(df_bench)

    result = dict(ku)

    def _safe_delta(a, b):
        try:
            return round(float(a) - float(b), 1)
        except Exception:
            return None

    result["delta_ei"]      = _safe_delta(ku["ei_mean"],         kb["ei_mean"])
    result["delta_enps"]    = _safe_delta(ku["enps_score"],       kb["enps_score"])
    result["delta_flight"]  = _safe_delta(ku["intent_pct_low"],   kb["intent_pct_low"])
    result["delta_burnout"] = _safe_delta(ku["burnout_pct"],      kb["burnout_pct"])
    result["delta_mei"]     = _safe_delta(ku.get("mei_avg", 0),   kb.get("mei_avg", 0))

    result["bench_ei"]      = round(float(kb["ei_mean"]), 1)
    result["bench_enps"]    = round(float(kb["enps_score"]), 0)
    result["bench_flight"]  = round(float(kb["intent_pct_low"]), 1)
    result["bench_burnout"] = round(float(kb["burnout_pct"]), 1)
    result["bench_mei"]     = round(float(kb.get("mei_avg", 0)), 1)
    return result


# ── Open-text column ──────────────────────────────────────────────────

def get_open_col(df: pd.DataFrame) -> str | None:
    for cand in ["Q34", "Q33", "Q32"]:
        if cand in df.columns:
            return cand
    return None


# ── Participation rate ────────────────────────────────────────────────

def get_participation_rate(
    df_unit: pd.DataFrame, df_bench: pd.DataFrame
) -> float | None:
    n_bench = len(df_bench)
    if n_bench == 0:
        return None
    return round(len(df_unit) / n_bench * 100, 1)


# ── Per-question detail for one pillar ───────────────────────────────

def pillar_question_detail(
    df_unit: pd.DataFrame,
    df_bench: pd.DataFrame,
    group_id: str,
    pillar_id: str,
) -> pd.DataFrame:
    """
    Trả về DataFrame chi tiết mỗi câu hỏi trong trụ cột:
    Câu | Nội dung | Điểm unit | Điểm bench | Delta | % Tiêu cực (unit) | N
    """
    from shared.codebook import get_question_label
    qs = [q for q in get_pillar_questions(group_id, pillar_id) if q in df_unit.columns]
    rows = []
    for q in qs:
        u_vals = pd.to_numeric(df_unit[q], errors="coerce").dropna()
        b_vals = pd.to_numeric(df_bench[q], errors="coerce").dropna()
        if len(u_vals) < 3:
            continue
        score_u = float(u_vals.mean())
        score_b = float(b_vals.mean()) if len(b_vals) >= 3 else None
        rows.append({
            "Câu": q,
            "Nội dung": get_question_label(group_id, q) or q,
            "Điểm đơn vị": round(score_u, 2),
            "Điểm nhóm": round(score_b, 2) if score_b else None,
            "Delta": round(score_u - score_b, 2) if score_b else None,
            "% Tiêu cực": round((u_vals <= 2).mean() * 100, 1),
            "N": int(len(u_vals)),
        })
    if not rows:
        return pd.DataFrame()
    df_out = pd.DataFrame(rows)
    df_out = df_out.sort_values("Điểm đơn vị", ascending=True).reset_index(drop=True)
    return df_out
