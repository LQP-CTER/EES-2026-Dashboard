"""
preprocess_pipeline.py — EES 2026 Offline Data Pipeline
========================================================
Chạy trên máy tính cá nhân (không cần Streamlit).
Thực hiện toàn bộ pipeline xử lý dữ liệu nặng:
  1. Load raw .xlsx từ Data/
  2. Decode + Quality scoring + NLP + Org Mapping
  3. Tính EI, MEI, Burnout, JSI, EWS, Quadrant, Silence Rate
  4. Xuất Data_Clean/{group}_clean.parquet (local backup)
  5. Upload lên Supabase + NeonDB

Cách chạy:
  python scripts/preprocess_pipeline.py              # Tất cả 6 groups
  python scripts/preprocess_pipeline.py --group 1A  # Chỉ 1 group
  python scripts/preprocess_pipeline.py --skip-upload  # Chỉ xuất parquet
"""

import sys
import os
import argparse
import json
import hashlib
import warnings
from collections import defaultdict
from datetime import datetime

warnings.filterwarnings("ignore")

# Thêm project root vào path để import được shared modules
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, PROJECT_ROOT)

import numpy as np
import pandas as pd

# ─────────────────────────────────────────────────────────────────────────────
# 1. ĐỌC CREDENTIALS TỪ secrets.toml
# ─────────────────────────────────────────────────────────────────────────────
def _load_secrets():
    """Đọc .streamlit/secrets.toml mà không cần Streamlit."""
    try:
        import tomllib  # Python 3.11+
    except ImportError:
        try:
            import tomli as tomllib  # pip install tomli
        except ImportError:
            print("  [WARNING] Không tìm thấy tomllib/tomli. Cài đặt: pip install tomli")
            return {}
    secrets_path = os.path.join(PROJECT_ROOT, ".streamlit", "secrets.toml")
    if not os.path.exists(secrets_path):
        print(f"  [WARNING] Không tìm thấy {secrets_path}")
        return {}
    with open(secrets_path, "rb") as f:
        return tomllib.load(f)


SECRETS = _load_secrets()


def _get_db_url(name: str) -> str:
    """Lấy connection URL từ secrets."""
    connections = SECRETS.get("connections", {})
    if name in connections:
        return connections[name].get("url", "")
    return ""


def _get_table_name(group_id: str, db_name: str) -> str:
    """Resolve survey table name from secrets/env, fallback to legacy name."""
    gid = group_id.upper()
    gid_l = group_id.lower()
    db = db_name.upper()
    env_keys = [
        f"{db}_TABLE_{gid}",
        f"{db}_SURVEY_{gid}_TABLE",
        f"SURVEY_TABLE_{gid}",
        f"EES_TABLE_{gid}",
        f"TABLE_{gid}",
        f"{db}_TABLE_{gid_l}",
        f"SURVEY_TABLE_{gid_l}",
        f"EES_TABLE_{gid_l}",
    ]
    for key in env_keys:
        val = os.environ.get(key, "").strip()
        if val:
            return val

    section_names = [
        f"{db_name.lower()}_tables",
        "survey_tables",
        "database_tables",
        "ees_tables",
    ]
    lookup_keys = [gid, gid_l, f"group_{gid_l}", f"survey_{gid_l}"]
    for section_name in section_names:
        section = SECRETS.get(section_name, {})
        if not section:
            continue
        for key in lookup_keys:
            val = str(section.get(key, "")).strip()
            if val:
                return val

    return f"survey_{gid_l}_clean"


# ─────────────────────────────────────────────────────────────────────────────
# 2. IMPORT CÁC MODULE XỬ LÝ (tái sử dụng từ project)
# ─────────────────────────────────────────────────────────────────────────────
print("Đang khởi tạo modules...")
from shared.codebook import (
    LIKERT_CODE_MAP, ENPS_CODE_MAP, PILLAR_WEIGHTS,
    decode_likert, decode_enps, decode_intent, classify_enps,
    calc_engagement_pct, classify_ei,
    get_pillar_questions, get_role_question,
    CODEBOOK_1A, CODEBOOK_1B, CODEBOOK_2A, CODEBOOK_2B, CODEBOOK_3A, CODEBOOK_3B,
)
from shared.workforce_mapper import map_survey_to_org
from shared.nlp_utils import (
    preprocess_text, compute_sentiment_intensity,
    detect_warning_signals, classify_topics,
)
from utils.data_loader import (
    normalize_tenure_value, classify_prev_company,
    compute_mahalanobis_flags, EWS_TENURE_THRESHOLD,
    TENURE_LABELS,
)

print("  Modules OK.")

# ─────────────────────────────────────────────────────────────────────────────
# 3. REGISTRY CÁC GROUP (tương tự config/groups.py nhưng không dùng Streamlit)
# ─────────────────────────────────────────────────────────────────────────────
DATA_DIR      = os.path.join(PROJECT_ROOT, "Data")
DATA_CLEAN_DIR = os.path.join(PROJECT_ROOT, "Data_Clean")
os.makedirs(DATA_CLEAN_DIR, exist_ok=True)

GROUP_REGISTRY = {
    "1A": {"label": "[1A] Nhân viên Giao nhận", "file": "EES-2026-Final-1A.xlsx", "codebook": CODEBOOK_1A},
    "1B": {"label": "[1B] Tài xế xe tải",        "file": "EES-2026-Final-1B.xlsx", "codebook": CODEBOOK_1B},
    "2A": {"label": "[2A] Nhân viên Vận hành Kho","file": "EES-2026-Final-2A.xlsx", "codebook": CODEBOOK_2A},
    "2B": {"label": "[2B] Nhân viên Kho (khác)",  "file": "EES-2026-Final-2B.xlsx", "codebook": CODEBOOK_2B},
    "3A": {"label": "[3A] Nhân viên Văn phòng",   "file": "EES-2026-Final-3A.xlsx", "codebook": CODEBOOK_3A},
    "3B": {"label": "[3B] Kỹ thuật/IT",           "file": "EES-2026-Final-3B.xlsx", "codebook": CODEBOOK_3B},
}

# ─────────────────────────────────────────────────────────────────────────────
# 4. CORE PROCESSING FUNCTION
# ─────────────────────────────────────────────────────────────────────────────
def _is_meaningless(text):
    if pd.isna(text): return True
    t = str(text).strip().lower()
    # Mở rộng tập filler để bắt đúng "câu mở bỏ trống" theo định nghĩa analyst v13
    _FILLER = {
        "", "không", "khong", "không có", "khong co", "không ý kiến",
        "khong y kien", "k", "ko", "none", "na", "n/a", "-", ".",
        # Thêm các filler phổ biến trong khảo sát tiếng Việt
        "ok", "oke", "okay", "oki", "tốt", "tot", "bình thường", "binh thuong",
        "ổn", "on", "ổn rồi", "ổn hết", "không có gì", "khong co gi",
        "không có gì thêm", "khong co gi them", "không có ý kiến gì thêm",
        "không ý kiến gì", "không có gì để nói", "chưa có", "chua co",
        "chưa", "no", "x", "không biết", "khong biet", "bình thường thôi",
        "chưa có ý kiến", "không có phản hồi", "không có góp ý",
        "chưa có góp ý", "tốt rồi", "ổn định", "bình thường bình thường",
    }
    if t in _FILLER:
        return True
    return len(t) < 2 and not t.isalnum()


def process_group(group_id: str) -> pd.DataFrame:
    """Xử lý đầy đủ một group khảo sát. Trả về df_clean đã tính xong tất cả KPI."""
    cfg      = GROUP_REGISTRY[group_id]
    codebook = cfg["codebook"]
    filepath = os.path.join(DATA_DIR, cfg["file"])

    print(f"\n[{group_id}] Load raw data từ {cfg['file']}...")
    if not os.path.exists(filepath):
        print(f"  SKIP: File không tồn tại — {filepath}")
        return None

    df_raw = pd.read_excel(filepath)
    n_before = len(df_raw)
    print(f"  Raw rows: {n_before:,}")

    # ── Rename columns ────────────────────────────────────────────────────────
    col_rename = {}
    for q_id, q_info in codebook.items():
        idx = q_info["col_idx"]
        if idx < len(df_raw.columns):
            col_rename[df_raw.columns[idx]] = q_id
    df = df_raw.rename(columns=col_rename).copy()

    likert_cols = [q for q, info in codebook.items() if info["loại"] == "likert"]
    open_cols   = [q for q, info in codebook.items() if info["loại"] == "open"]

    # ── Decode Likert / eNPS / Intent ─────────────────────────────────────────
    for col in likert_cols:
        if col in df.columns:
            df[col] = df[col].apply(decode_likert)
    if "Q31" in df.columns:
        df["eNPS"] = df["Q31"].apply(decode_enps)
    if "Q30" in df.columns:
        df["intent"] = df["Q30"].apply(decode_intent)
    else:
        df["intent"] = None
    df["eNPS_group"] = df.get("eNPS", pd.Series(dtype=float)).apply(classify_enps)

    if "Q5" in df.columns:
        tenure_norm       = df["Q5"].apply(normalize_tenure_value)
        df["tenure"]      = tenure_norm.apply(lambda x: x[0])
        df["tenure_label"]= tenure_norm.apply(lambda x: x[1])
        df["Q5"]          = df["tenure_label"]

    if "Q6" in df.columns:
        df["prev_company_cat"] = df["Q6"].apply(classify_prev_company)

    # ── Quality Flags ─────────────────────────────────────────────────────────
    print(f"  [1/6] Quality flags...")
    df["likert_mean"]    = df[likert_cols].mean(axis=1)
    df["_likert_sd"]     = df[likert_cols].std(axis=1)
    df["n_valid_likert"] = df[likert_cols].notna().sum(axis=1)
    df["flag_straightline"] = (df["_likert_sd"] == 0) & (df["n_valid_likert"] >= 10)
    df["flag_too_missing"]  = (df[likert_cols].isna().sum(axis=1) / len(likert_cols) * 100) > 80
    df["flag_empty_open"]   = df[open_cols].apply(lambda row: all(_is_meaningless(x) for x in row), axis=1) if open_cols else True
    df["evidence_open"]     = ~df["flag_empty_open"]

    enps_col = df.get("eNPS", pd.Series(dtype=float))
    df["evidence_enps"] = False
    if "eNPS" in df.columns:
        df["evidence_enps"] = (
            ((df["likert_mean"] >= 4) & (enps_col >= 9)) |
            ((df["likert_mean"].between(3, 4, inclusive="both")) & (enps_col.between(7, 8, inclusive="both"))) |
            ((df["likert_mean"] <= 2) & (enps_col <= 6))
        )
    df["num_evidence"] = df["evidence_open"].astype(int) + df["evidence_enps"].astype(int)

    if "eNPS" in df.columns:
        df["flag_contradiction"] = (
            ((df["likert_mean"] >= 4) & (df["eNPS"] <= 6)) |
            ((df["likert_mean"] <= 2) & (df["eNPS"] >= 9))
        )
    else:
        df["flag_contradiction"] = False

    # Duplicate detection
    def _get_long_open(row):
        txt = " ".join([str(x).strip() for x in row[open_cols] if pd.notna(x) and str(x).strip()])
        return txt if len(txt) >= 25 else np.nan

    df["_long_open"] = df.apply(_get_long_open, axis=1) if open_cols else np.nan
    dup_cols = [c for c in likert_cols if c in df.columns]
    if "eNPS" in df.columns:
        dup_cols.append("eNPS")
    if "_long_open" in df.columns:
        dup_cols.append("_long_open")
    df["flag_duplicate"] = False
    if dup_cols and "_long_open" in dup_cols:
        df["flag_duplicate"] = df.duplicated(subset=dup_cols, keep="first") & df["_long_open"].notna()

    df["flag_maha_proxy"] = df["flag_too_missing"] | ((df["_likert_sd"] > 1.8) & (df["n_valid_likert"] >= 10))
    print(f"  [2/6] Mahalanobis outlier detection...")
    df["flag_mahalanobis"], _ = compute_mahalanobis_flags(df, likert_cols)

    # ── Quality Tier ──────────────────────────────────────────────────────────
    def _assign_quality(row):
        # Chỉ DROP khi có lỗi cứng: thiếu dữ liệu nặng, trùng lặp, Mahalanobis outlier.
        if row["flag_too_missing"] or row["flag_duplicate"] or row["flag_mahalanobis"]:
            return 0.0, "DROP"
        # KHÔNG DROP straight-line+no-evidence: tài liệu analyst v13 quy định
        # "KHÔNG loại bỏ, chỉ downweight ×0,5". Nhóm này nhiều detractor/neutral,
        # DROP sẽ thổi phồng eNPS +5–+6 so với benchmark.
        # Thay vào đó: downweight mạnh (0.3) vì không có bằng chứng gắn kết nào.
        if row["num_evidence"] == 0:
            return 0.3, "DOWNWEIGHT"
        if row["flag_straightline"] or row["flag_contradiction"] or row["num_evidence"] == 1:
            return 0.7, "DOWNWEIGHT"
        return 1.0, "KEEP"

    quality = df.apply(_assign_quality, axis=1)
    df["effective_weight"]       = [x[0] for x in quality]
    df["tier_v2"]                = [x[1] for x in quality]
    df["CompanyRollup_Weight"]   = df["effective_weight"]
    df["flag_drop"]              = df["tier_v2"] == "DROP"

    df_clean = df[~df["flag_drop"]].copy()
    n_clean  = len(df_clean)
    print(f"  Sau lọc: {n_clean:,} / {n_before:,} mẫu ({round((1 - n_clean/n_before)*100, 1)}% bị loại)")

    # ── Org Mapping ───────────────────────────────────────────────────────────
    print(f"  [3/6] Org mapping (HRIS)...")
    vung_col = df_clean.columns[10] if len(df_clean.columns) > 10 else df_clean.columns[0]
    for c in df_clean.columns:
        if "Vùng" in str(c) or "vùng" in str(c):
            vung_col = c; break

    # ── Org Mapping (Native From Survey) ──────────────────────────────────────
    print(f"  [3/6] Org mapping (Native from Survey)...")
    df_clean["section"] = "Khác"

    if group_id in ["1A", "1B"]:
        div_name = "Khối Thị Trường" if group_id == "1A" else "Khối Vận Hành"
        df_clean["division"] = div_name
        df_clean["department"] = df_clean[vung_col].fillna("Khác").astype(str)
    else:
        # Find the division column
        div_col = None
        for c in df_clean.columns:
            c_str = str(c).lower().strip()
            if c_str.startswith("khối/ phòng ban bạn đang làm việc") or c_str.startswith("phòng ban bạn đang làm việc") or c_str.startswith("khối/phòng ban bạn đang làm việc"):
                # Prefer the one that actually has data (for 3B)
                if df_clean[c].notna().any():
                    div_col = c
                    break

        # Find the department columns
        dept_cols = []
        for c in df_clean.columns:
            c_str = str(c).lower().strip()
            if c_str.startswith("bạn thuộc"):
                dept_cols.append(c)

        if div_col:
            df_clean["division"] = df_clean[div_col].fillna("Khác").astype(str)
            if dept_cols:
                # bfill across department columns to get the first non-null
                dept_series = df_clean[dept_cols].bfill(axis=1).iloc[:, 0]
                df_clean["department"] = dept_series.fillna(df_clean[div_col]).astype(str)
            else:
                df_clean["department"] = df_clean[div_col].fillna("Khác").astype(str)
        else:
            df_clean["division"] = "Khác"
            df_clean["department"] = "Khác"

    # Clean up newline and spaces
    df_clean["division"] = df_clean["division"].str.replace("\n", " ").str.strip()
    df_clean["department"] = df_clean["department"].str.replace("\n", " ").str.strip()

    # Apply 3A exclusions
    if group_id == "3A":
        EXCLUDE_DIVS = [
            "phòng dịch vụ kho vận",
            "phòng kinh doanh khách hàng lớn",
            "phòng nền tảng vận hành",
            "technology operations department",
        ]
        m_exc = (
            df_clean["division"].astype(str).str.strip().str.lower().isin(EXCLUDE_DIVS) |
            df_clean["department"].astype(str).str.strip().str.lower().isin(EXCLUDE_DIVS) |
            df_clean["section"].astype(str).str.strip().str.lower().isin(EXCLUDE_DIVS)
        )
        n_before -= m_exc.sum()
        df_clean = df_clean[~m_exc].copy()

    # ── Pillar Scores & EI ────────────────────────────────────────────────────
    print(f"  [4/6] KPI columns (EI, MEI, Burnout, JSI, EWS)...")
    pillar_cols = defaultdict(list)
    for q_id, info in codebook.items():
        if info["trụ_cột"]:
            pillar_cols[info["trụ_cột"]].append(q_id)
    for pillar, cols in pillar_cols.items():
        valid = [c for c in cols if c in df_clean.columns]
        df_clean[f"{pillar}_mean"] = df_clean[valid].mean(axis=1)
        df_clean[f"{pillar}_pct"]  = df_clean[f"{pillar}_mean"].apply(calc_engagement_pct)

    pillar_pcts = [f"{p}_pct" for p in PILLAR_WEIGHTS.keys()]
    weights_list = list(PILLAR_WEIGHTS.values())
    present = [(p, w) for p, w in zip(pillar_pcts, weights_list) if p in df_clean.columns]
    if present:
        pct_frame = pd.DataFrame({p: df_clean[p] for p, _ in present})
        w_series  = pd.Series({p: w for p, w in present})
        valid_mask = pct_frame.notna()
        eff_w  = valid_mask.mul(w_series, axis=1)
        w_sum  = eff_w.sum(axis=1)
        weighted = (pct_frame.fillna(0.0) * eff_w).sum(axis=1)
        df_clean["EI"] = np.where(w_sum > 0, weighted / w_sum, np.nan)
    else:
        df_clean["EI"] = np.nan
    df_clean["EI_class"] = df_clean["EI"].apply(classify_ei)

    # MEI
    mei_cols = [c for c in get_pillar_questions(group_id, "TC2") if c in df_clean.columns]
    if mei_cols:
        df_clean["MEI"] = df_clean[mei_cols].apply(
            lambda r: (r >= 4).sum() / r.notna().sum() * 100 if r.notna().sum() > 0 else None, axis=1)

    # Burnout
    pressure_roles = ["pressure", "workload"]
    pressure = [q for q in (get_role_question(group_id, r) for r in pressure_roles) if q and q in df_clean.columns]
    if pressure:
        df_clean["burnout_score"] = (sum(((5 - df_clean[q]) / 4 * 100) for q in pressure) / len(pressure)).round(1)
        df_clean["burnout_proxy"] = df_clean["burnout_score"] >= 50
        df_clean["burnout_risk"]  = (df_clean["burnout_score"] - 50) / 25

    # Stay intention
    if "intent" in df_clean.columns and df_clean["intent"].notna().any():
        df_clean["stay_intention"] = df_clean["intent"]
        df_clean["stay_risk_group"] = df_clean["intent"].apply(
            lambda v: ("Flight Risk" if v <= 2 else ("At Risk" if v == 3 else "Stable")) if pd.notna(v) else None
        )

    # Silence Rate
    improve_open = next((c for c in ["Q34", "Q33", "Q32"] if c in df_clean.columns), None)
    if improve_open:
        df_clean["is_silent"] = df_clean[improve_open].apply(_is_meaningless)
    else:
        df_clean["is_silent"] = df_clean.get("flag_empty_open", pd.Series(True, index=df_clean.index))

    # JSI
    workload_q = get_role_question(group_id, "workload")
    respect_q  = get_role_question(group_id, "pride")
    tc4_pct    = df_clean.get("TC4_pct")
    if tc4_pct is not None:
        comps, wts = [tc4_pct], [0.4]
        if workload_q and workload_q in df_clean.columns:
            comps.append(df_clean[workload_q].apply(calc_engagement_pct)); wts.append(0.3)
        if respect_q and respect_q in df_clean.columns:
            comps.append(df_clean[respect_q].apply(calc_engagement_pct));  wts.append(0.3)
        wsum = sum(wts)
        df_clean["JSI"] = sum(c * (w / wsum) for c, w in zip(comps, wts))

    # EWS
    if "tenure" in df_clean.columns:
        ews_threshold = EWS_TENURE_THRESHOLD.get(group_id, 2)
        early_mask = df_clean["tenure"].notna() & (df_clean["tenure"] <= ews_threshold)
        def _ews(row):
            score, n = 0.0, 0
            if pd.notna(iv := row.get("intent")):     score += (5 - iv) / 4 * 40; n += 1
            if pd.notna(tc2 := row.get("TC2_pct")):   score += (100 - tc2) / 100 * 30; n += 1
            if pd.notna(tc3 := row.get("TC3_pct")):   score += (100 - tc3) / 100 * 30; n += 1
            return round(score, 1) if n > 0 else None
        df_clean["EWS"] = None
        if early_mask.any():
            df_clean.loc[early_mask, "EWS"] = df_clean.loc[early_mask].apply(_ews, axis=1)
        df_clean["EWS_flag"] = df_clean["EWS"].apply(
            lambda v: "Cảnh báo đỏ" if pd.notna(v) and v >= 60
            else ("Theo dõi" if pd.notna(v) and v >= 40 else ("Ổn" if pd.notna(v) else None))
        )

    # Engagement Quadrant
    if "eNPS" in df_clean.columns and "EI" in df_clean.columns:
        def _quad(row):
            e, ei = row.get("eNPS"), row.get("EI")
            if pd.isna(e) or pd.isna(ei): return None
            return ("Champions" if e >= 9 and ei >= 65 else
                    "Trapped Loyalists" if ei >= 65 else
                    "Confused Leavers" if e >= 9 else "Flight Risk")
        df_clean["engagement_quadrant"] = df_clean.apply(_quad, axis=1)

    # Contradiction Index
    if "EI" in df_clean.columns and "intent" in df_clean.columns:
        df_clean["contradiction_flag"] = (df_clean["EI"] >= 75) & (df_clean["intent"] <= 2)

    # ── NLP (offline) ────────────────────────────────────────────────────────
    print(f"  [5/6] NLP: sentiment, topics, warning signals...")
    for col in open_cols:
        if col in df_clean.columns:
            df_clean[f"{col}_clean"] = df_clean[col].apply(
                lambda x: preprocess_text(str(x)) if pd.notna(x) and len(str(x).strip()) > 3 else None
            )

    # Gộp tất cả câu hỏi mở đã clean thành 1 cột duy nhất để phân tích NLP
    def _safe_join(parts):
        return " ".join(p for p in parts if isinstance(p, str) and len(p.strip()) > 0) or None

    combined_parts = [
        df_clean[f"{col}_clean"]
        for col in open_cols
        if f"{col}_clean" in df_clean.columns
    ]
    if combined_parts:
        df_clean["open_text_combined"] = pd.concat(combined_parts, axis=1).apply(
            lambda row: _safe_join(row.tolist()), axis=1
        )
    else:
        df_clean["open_text_combined"] = None

    def _nlp_row(text):
        if not isinstance(text, str) or len(text) < 3:
            return 0.0, "trung_lập", "[]", "[]"
        score, label = compute_sentiment_intensity(text)
        topics   = classify_topics(text)
        warnings = detect_warning_signals(text)
        return (
            score, label,
            json.dumps(topics,   ensure_ascii=False),
            json.dumps([str(w) for w in warnings], ensure_ascii=False),
        )

    nlp_results = df_clean["open_text_combined"].apply(_nlp_row)
    df_clean["nlp_sentiment_score"]   = nlp_results.apply(lambda x: x[0])
    df_clean["nlp_sentiment_label"]   = nlp_results.apply(lambda x: x[1])
    df_clean["nlp_topics"]            = nlp_results.apply(lambda x: x[2])   # JSON string
    df_clean["nlp_warning_signals"]   = nlp_results.apply(lambda x: x[3])   # JSON string

    # ── Anonymize ID ──────────────────────────────────────────────────────────
    # Tìm cột ID nhân viên theo tên trước, rồi fallback sang cột đầu tiên
    # có vẻ là số nguyên (heuristic: phần lớn giá trị convert được sang int)
    _id_names = {"id nhân viên", "employee id", "id_nv", "id", "mã nv", "ma nv",
                 "mã nhân viên", "ma nhan vien", "staff id", "emp id"}
    id_col = next(
        (c for c in df_clean.columns if str(c).strip().lower() in _id_names),
        None
    )
    if id_col is None:
        # Heuristic: thử các cột đầu tiên xem cột nào có giá trị giống int
        for c in df_clean.columns[:5]:
            sample = df_clean[c].dropna().head(20)
            try:
                converted = sample.apply(lambda x: int(float(str(x).replace(",", "").strip())))
                if converted.nunique() > 1:
                    id_col = c
                    break
            except (ValueError, TypeError):
                continue
    if id_col is None:
        id_col = df_clean.columns[0]  # last resort

    def _safe_hash(v):
        if pd.isna(v):
            return None
        try:
            return hashlib.sha256(str(int(float(str(v).replace(",", "").strip()))).encode()).hexdigest()
        except (ValueError, TypeError):
            return hashlib.sha256(str(v).encode()).hexdigest()

    df_clean["_nv_hash"] = df_clean[id_col].apply(_safe_hash)
    df_clean = df_clean.drop(columns=[id_col], errors="ignore")

    # ── Thêm metadata columns (cho trang Độ tin cậy dữ liệu) ────────────────
    df_clean["_meta_group_id"]    = group_id
    df_clean["_meta_n_raw"]       = n_before
    df_clean["_meta_n_clean"]     = len(df_clean)
    df_clean["_meta_n_drop"]      = n_before - len(df_clean)
    df_clean["_meta_pct_removed"] = round((n_before - len(df_clean)) / n_before * 100, 1) if n_before else 0.0
    df_clean["_meta_filter_desc"] = (
        "Tính effective_weight (0.3/0.7/1.0) và tier_v2. DROP khi thiếu dữ liệu nặng, "
        "trùng lặp, Mahalanobis outlier hoặc straightline không có bằng chứng."
    )
    df_clean["_meta_processed_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    print(f"  [6/6] Done — {len(df_clean):,} mẫu sạch.")
    return df_clean, n_before


# ─────────────────────────────────────────────────────────────────────────────
# 5. EXPORT TO PARQUET
# ─────────────────────────────────────────────────────────────────────────────
def export_parquet(df_clean: pd.DataFrame, group_id: str):
    out_path = os.path.join(DATA_CLEAN_DIR, f"{group_id}_clean.parquet")

    # Sanitize: ép tất cả cột object về string để PyArrow không bị mixed-type error
    df_out = df_clean.copy()
    for col in df_out.columns:
        if df_out[col].dtype == object:
            # Chuyển sang pandas StringDtype (nullable) — tương thích Parquet hoàn toàn
            df_out[col] = df_out[col].apply(
                lambda x: None if (x is None or (isinstance(x, float) and pd.isna(x))) else str(x)
            ).astype("string")

    df_out.to_parquet(out_path, index=False)
    size_mb = os.path.getsize(out_path) / (1024 * 1024)
    print(f"  Parquet: {out_path} ({size_mb:.1f} MB)")


# ─────────────────────────────────────────────────────────────────────────────
# 6. UPLOAD TO DATABASE (DROP + RECREATE)
# ─────────────────────────────────────────────────────────────────────────────
def _get_engine(db_name: str):
    """Tạo SQLAlchemy engine từ secrets.toml connection URL."""
    try:
        from sqlalchemy import create_engine
    except ImportError:
        print("  WARN: sqlalchemy chưa cài. Chạy: pip install sqlalchemy psycopg2-binary")
        return None
    url = _get_db_url(db_name)
    if not url:
        print(f"  WARN: Không tìm thấy connection URL cho '{db_name}' trong secrets.toml")
        return None
    return create_engine(url)


def _sanitize_df_for_sql(df: pd.DataFrame) -> pd.DataFrame:
    """Đảm bảo tất cả cột tương thích với SQL (không có list/dict)."""
    df = df.copy()
    for col in df.columns:
        if df[col].dtype == object:
            df[col] = df[col].apply(
                lambda x: json.dumps(x, ensure_ascii=False) if isinstance(x, (list, dict)) else x
            )
    return df


def upload_to_db(df_clean: pd.DataFrame, group_id: str, db_name: str):
    table_name = _get_table_name(group_id, db_name)
    engine = _get_engine(db_name)
    if engine is None:
        return False
    try:
        df_upload = _sanitize_df_for_sql(df_clean)
        # DROP + recreate: luôn có dữ liệu sạch nhất
        df_upload.to_sql(
            table_name, engine,
            if_exists="replace",   # DROP cũ, tạo mới
            index=False,
            chunksize=500,
            method="multi",
        )
        print(f"  [{db_name.upper()}] Uploaded {len(df_upload):,} rows → {table_name}")
        return True
    except Exception as e:
        print(f"  [{db_name.upper()}] FAILED: {e}")
        return False


# ─────────────────────────────────────────────────────────────────────────────
# 7. MAIN
# ─────────────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description="EES 2026 Offline Preprocessing Pipeline")
    parser.add_argument("--group",        type=str, default=None, help="Chỉ xử lý 1 group (VD: 1A)")
    parser.add_argument("--skip-upload",  action="store_true",   help="Chỉ xuất parquet, không upload DB")
    parser.add_argument("--skip-neondb",  action="store_true",   help="Bỏ qua NeonDB")
    parser.add_argument("--skip-supabase",action="store_true",   help="Bỏ qua Supabase")
    args = parser.parse_args()

    groups = [args.group] if args.group else list(GROUP_REGISTRY.keys())
    unknown = [g for g in groups if g not in GROUP_REGISTRY]
    if unknown:
        print(f"ERROR: Group không hợp lệ: {unknown}. Hợp lệ: {list(GROUP_REGISTRY.keys())}")
        sys.exit(1)

    print(f"\n{'='*60}")
    print(f"EES 2026 Offline Preprocessing Pipeline")
    print(f"Groups: {groups}  |  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}")

    summary = []
    for group_id in groups:
        result = process_group(group_id)
        if result is None:
            summary.append({"group": group_id, "status": "SKIP (file không tồn tại)"})
            continue

        df_clean, n_before = result

        # Export parquet
        export_parquet(df_clean, group_id)

        # Upload DB
        if not args.skip_upload:
            ok_neo  = True if args.skip_neondb  else upload_to_db(df_clean, group_id, "neondb")
            ok_supa = True if args.skip_supabase else upload_to_db(df_clean, group_id, "supabase")
        else:
            ok_neo = ok_supa = None

        summary.append({
            "group": group_id,
            "n_raw": n_before,
            "n_clean": len(df_clean),
            "parquet": "OK",
            "neondb":  "SKIP" if (args.skip_upload or args.skip_neondb)  else ("OK" if ok_neo  else "FAIL"),
            "supabase":"SKIP" if (args.skip_upload or args.skip_supabase) else ("OK" if ok_supa else "FAIL"),
        })

    # Summary
    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")
    for s in summary:
        if "n_raw" in s:
            pct = round((1 - s["n_clean"] / s["n_raw"]) * 100, 1)
            print(f"  [{s['group']}] {s['n_raw']:>5,} raw → {s['n_clean']:>5,} clean ({pct}% loại) "
                  f"| Parquet:{s['parquet']}  NeonDB:{s['neondb']}  Supabase:{s['supabase']}")
        else:
            print(f"  [{s['group']}] {s['status']}")
    print(f"\nHoàn tất! — {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("Tiếp theo: Vào Admin Panel → Làm mới Cache để Dashboard đọc dữ liệu mới.\n")


if __name__ == "__main__":
    main()
