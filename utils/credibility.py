"""
Data Credibility utilities — EES 2026 Dashboard.

Cung cấp:
  - confidence_badge(n, participation_rate)  → HTML badge tin cậy
  - confidence_level(n)                       → 'high'|'medium'|'low'|'insufficient'
  - triangulate_pillar(...)                   → dict signals + strength
  - PILLAR_KEYWORDS                           → keyword mapping cho open-text corroboration
"""
from __future__ import annotations

import pandas as pd

from shared.codebook import PILLAR_META, get_pillar_questions

# ── Keyword mapping: trụ cột → từ khóa open-text ────────────────────
PILLAR_KEYWORDS: dict[str, list[str]] = {
    "TC1": [
        "lãnh đạo", "ban điều hành", "bge", "định hướng", "chiến lược",
        "quyết định", "thông tin", "truyền thông", "minh bạch thông tin",
        "không biết", "không rõ", "thông báo", "tin tưởng lãnh đạo",
    ],
    "TC2": [
        "quản lý", "sếp", "trưởng", "giám sát", "supervisor",
        "hỗ trợ", "công bằng", "phản hồi", "ghi nhận", "khen",
        "phân công", "thiên vị", "không công bằng", "quản lý trực tiếp",
        "manager", "team lead",
    ],
    "TC3": [
        "công cụ", "hệ thống", "app", "phần mềm", "thiết bị",
        "quá tải", "tải công việc", "burnout", "căng thẳng", "mệt mỏi",
        "phát triển", "đào tạo", "thăng tiến", "thay đổi", "quy trình",
        "lộ trình", "career", "học hỏi", "cơ hội", "công việc",
    ],
    "TC4": [
        "lương", "thu nhập", "thưởng", "phụ cấp", "khấu trừ",
        "tính lương", "tiền", "đãi ngộ", "không công bằng lương",
        "minh bạch", "cách tính", "giải thích thu nhập", "lương thấp",
        "chế độ", "c&b", "lương thưởng",
    ],
    "TC5": [
        "đồng đội", "đồng nghiệp", "team", "nhóm", "phối hợp",
        "tự hào", "ý nghĩa", "môi trường", "văn hóa", "belonging",
        "áp lực", "kiệt sức", "cạn sức", "không muốn ở lại",
        "gắn kết", "thân thiện", "kết nối",
    ],
}


# ── Badge HTML ────────────────────────────────────────────────────────

def confidence_badge(n: int, participation_rate: float | None = None) -> str:
    """
    Trả về HTML inline badge cho mức độ tin cậy dữ liệu.

    Ngưỡng:
      N ≥ 50  → Đủ tin cậy  (xanh)
      N 20-49 → Tín hiệu    (vàng)
      N 5-19  → Cần thận trọng (cam)
      N < 5   → Không đủ mẫu  (đỏ)
    """
    if n >= 50:
        label, color, bg = "Đủ tin cậy", "#15803D", "#F0FDF4"
        border = "#86EFAC"
    elif n >= 20:
        label, color, bg = "Tín hiệu", "#CA8A04", "#FEFCE8"
        border = "#FDE68A"
    elif n >= 5:
        label, color, bg = "Cần thận trọng", "#EA580C", "#FFF7ED"
        border = "#FED7AA"
    else:
        label, color, bg = "Không đủ mẫu", "#DC2626", "#FEF2F2"
        border = "#FECACA"

    part_text = (
        f" · {participation_rate:.0f}% tham gia" if participation_rate is not None else ""
    )
    return (
        f'<span style="background:{bg};color:{color};border:1px solid {border};'
        f'padding:3px 9px;border-radius:6px;font-size:0.72rem;font-weight:700;'
        f'display:inline-block;white-space:nowrap;">'
        f"N={n:,}{part_text} · {label}"
        f"</span>"
    )


def confidence_level(n: int) -> str:
    """Trả về chuỗi mức độ: 'high' | 'medium' | 'low' | 'insufficient'."""
    if n >= 50:
        return "high"
    if n >= 20:
        return "medium"
    if n >= 5:
        return "low"
    return "insufficient"


# ── Internal helpers ──────────────────────────────────────────────────

def _pillar_score(df: pd.DataFrame, group_id: str, pillar_id: str) -> float | None:
    qs = [q for q in get_pillar_questions(group_id, pillar_id) if q in df.columns]
    if not qs:
        return None
    vals = df[qs].apply(pd.to_numeric, errors="coerce").mean(axis=1).dropna()
    return float(vals.mean()) if len(vals) >= 3 else None


def _opentext_mentions(df: pd.DataFrame, pillar_id: str) -> int:
    open_col = None
    for cand in ["Q34", "Q33", "Q32"]:
        if cand in df.columns:
            open_col = cand
            break
    if open_col is None:
        return 0
    keywords = PILLAR_KEYWORDS.get(pillar_id, [])
    if not keywords:
        return 0
    mask = df[open_col].dropna().apply(
        lambda x: any(k in str(x).lower() for k in keywords)
    )
    return int(mask.sum())


# ── Triangulation ─────────────────────────────────────────────────────

def triangulate_pillar(
    df_unit: pd.DataFrame,
    df_bench: pd.DataFrame,
    pillar_id: str,
    group_id: str,
    cfg: dict | None = None,
) -> dict:
    """
    Kiểm tra bằng chứng chéo (3 nguồn độc lập) cho một vấn đề trụ cột tại đơn vị.

    Trả về:
    {
        "signals":        [ {"type": str, "text": str}, ... ],
        "strength":       "Mạnh" | "Vừa" | "Yếu" | "Chưa rõ" | "Không đủ mẫu",
        "strength_score": int (0–3),
    }
    """
    if len(df_unit) < 5:
        return {"signals": [], "strength": "Không đủ mẫu", "strength_score": 0}

    signals: list[dict] = []
    pillar_name = PILLAR_META.get(pillar_id, {}).get("name", pillar_id)

    # ── Signal 1: Điểm Likert thấp hơn benchmark ──────────────────────
    score_unit = _pillar_score(df_unit, group_id, pillar_id)
    score_bench = _pillar_score(df_bench, group_id, pillar_id)
    if score_unit is not None and score_bench is not None:
        delta = score_unit - score_bench
        if delta <= -0.15:
            signals.append({
                "type": "likert_gap",
                "text": (
                    f"Điểm {pillar_name} = {score_unit:.2f}/5 "
                    f"(benchmark {score_bench:.2f}, thấp hơn {abs(delta):.2f} điểm)"
                ),
            })

    # ── Signal 2: Flight risk tại unit cao hơn benchmark ──────────────
    if "intent" in df_unit.columns and "intent" in df_bench.columns:
        fr_unit = (pd.to_numeric(df_unit["intent"], errors="coerce") <= 2).mean() * 100
        fr_bench = (pd.to_numeric(df_bench["intent"], errors="coerce") <= 2).mean() * 100
        if fr_unit >= fr_bench + 8:
            signals.append({
                "type": "flight_risk",
                "text": (
                    f"Flight risk {fr_unit:.1f}% tại đơn vị "
                    f"(benchmark nhóm {fr_bench:.1f}%, cao hơn {fr_unit - fr_bench:.1f}%)"
                ),
            })

    # ── Signal 3: Open-text đề cập keywords của trụ cột này ───────────
    n_mentions = _opentext_mentions(df_unit, pillar_id)
    if n_mentions >= 2:
        signals.append({
            "type": "opentext",
            "text": f"{n_mentions} phản hồi mở đề cập chủ đề liên quan đến {pillar_name}",
        })

    n_signals = len(signals)
    if n_signals >= 3:
        strength = "Mạnh"
    elif n_signals == 2:
        strength = "Vừa"
    elif n_signals == 1:
        strength = "Yếu"
    else:
        strength = "Chưa rõ"

    return {
        "signals": signals,
        "strength": strength,
        "strength_score": n_signals,
    }


def render_triangulation_box(tri: dict) -> str:
    """Trả về HTML box hiển thị kết quả triangulation."""
    if tri["strength"] == "Không đủ mẫu":
        return ""

    color_map = {
        "Mạnh":   ("#15803D", "#F0FDF4", "#86EFAC"),
        "Vừa":    ("#CA8A04", "#FEFCE8", "#FDE68A"),
        "Yếu":    ("#EA580C", "#FFF7ED", "#FED7AA"),
        "Chưa rõ":("#64748B", "#F8FAFC", "#E2E8F0"),
    }
    c, bg, bd = color_map.get(tri["strength"], ("#64748B", "#F8FAFC", "#E2E8F0"))

    icons = {"Mạnh": "✅", "Vừa": "⚡", "Yếu": "⚠️", "Chưa rõ": "—"}
    icon = icons.get(tri["strength"], "")

    signals_html = "".join(
        f'<li style="margin-bottom:3px;">{s["text"]}</li>'
        for s in tri["signals"]
    )
    if not signals_html:
        signals_html = "<li>Chưa đủ tín hiệu corroboration</li>"

    return (
        f'<div style="background:{bg};border:1px solid {bd};border-left:3px solid {c};'
        f'border-radius:8px;padding:10px 13px;margin-top:8px;">'
        f'<div style="font-size:.68rem;font-weight:800;color:{c};text-transform:uppercase;'
        f'letter-spacing:.07em;margin-bottom:5px;">'
        f'{icon} Bằng chứng chéo: {tri["strength"]}'
        f"</div>"
        f'<ul style="font-size:.8rem;color:#334155;line-height:1.65;margin:0;padding-left:16px;">'
        f"{signals_html}"
        f"</ul>"
        f"</div>"
    )
