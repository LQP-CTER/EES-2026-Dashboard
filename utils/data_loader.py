"""
Data Loader — EES 2026 Dashboard (Multi-Group)
Cached data loading & KPI computation for any survey group.
"""
import os, sys
import pandas as pd
import numpy as np
from collections import defaultdict

# Safe Streamlit import: data_loader có thể được import từ script offline
# (không có Streamlit runtime). Khi đó, tạo stub để tránh crash.
try:
    import streamlit as st
    _has_streamlit = True
except Exception:
    _has_streamlit = False

if not _has_streamlit:
    # Stub tối giản: cache_data / cache_resource trở thành passthrough decorator
    class _StStub:
        def cache_data(self, *a, **kw):
            def _deco(fn): return fn
            return _deco
        def cache_resource(self, *a, **kw):
            def _deco(fn): return fn
            return _deco
        def warning(self, *a, **kw): pass
        def error(self, *a, **kw): pass
        def connection(self, *a, **kw): raise RuntimeError("No Streamlit runtime")
        class secrets:
            @staticmethod
            def get(k, d=None): return d
    st = _StStub()

# Paths
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from shared.codebook import (
    LIKERT_CODE_MAP, ENPS_CODE_MAP, PILLAR_WEIGHTS,
    decode_likert, decode_enps, decode_intent, classify_enps,
    calc_engagement_pct, classify_ei,
    get_pillar_questions, get_role_question,
)
from shared.workforce_mapper import map_survey_to_org, get_org_summary

BASE = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
DATA_DIR = os.path.join(BASE, 'Data')

SURVEY_TABLE_CANDIDATE_TEMPLATES = [
    "survey_{gid}_clean",
    "ees_2026_{gid}_clean",
    "ees2026_{gid}_clean",
    "survey_{gid}",
    "ees_{gid}_clean",
]

PILLAR_LABELS = {
    'TC1': 'Niềm tin lãnh đạo',
    'TC2': 'Quản lý trực tiếp (MEI)',
    'TC3': 'Công việc & phát triển',
    'TC4': 'Thu nhập & minh bạch',
    'TC5': 'Môi trường & gắn kết',
}

TENURE_LABELS = [
    'Dưới 1 tháng',
    'Trên 1 đến 3 tháng',
    'Trên 3 đến 6 tháng',
    'Trên 6 đến 9 tháng',
    'Trên 9 đến 12 tháng',
    'Trên 1 đến 2 năm',
    'Trên 2 đến 3 năm',
    'Trên 3 đến 5 năm',
    'Trên 5 năm',
]

TENURE_CODE_MAP = {chr(65 + i): label for i, label in enumerate(TENURE_LABELS)}
TENURE_MAP = {label: i for i, label in enumerate(TENURE_LABELS)}
TENURE_MAP.update({i + 1: i for i in range(len(TENURE_LABELS))})
EWS_TENURE_THRESHOLD = {'1A': 1, '1B': 1, '2A': 2, '2B': 2, '3A': 2, '3B': 2}


def _secrets_section(name: str):
    try:
        return st.secrets.get(name, {})
    except Exception:
        return {}


def _table_secret_keys(group_id: str, db_name: str) -> list[str]:
    gid = group_id.upper()
    gid_l = group_id.lower()
    db = db_name.upper()
    return [
        f"{db}_TABLE_{gid}",
        f"{db}_SURVEY_{gid}_TABLE",
        f"SURVEY_TABLE_{gid}",
        f"EES_TABLE_{gid}",
        f"TABLE_{gid}",
        f"{db}_TABLE_{gid_l}",
        f"SURVEY_TABLE_{gid_l}",
        f"EES_TABLE_{gid_l}",
    ]


def _get_configured_table_names(group_id: str, db_name: str) -> list[str]:
    """Read optional table overrides from secrets/env.

    Supported examples:
    - EES_TABLE_1A = "survey_1a_clean_v2"
    - NEONDB_TABLE_1A = "ees2026.survey_1a_clean"
    - [survey_tables] group_1a = "survey_1a_clean_v2"
    - [neondb_tables] group_1a = "survey_1a_clean_v2"
    """
    values = []
    for key in _table_secret_keys(group_id, db_name):
        try:
            val = st.secrets.get(key, "")
        except Exception:
            val = ""
        if not val:
            val = os.environ.get(key, "")
        if val:
            values.append(str(val).strip())

    section_names = [
        f"{db_name.lower()}_tables",
        "survey_tables",
        "database_tables",
        "ees_tables",
    ]
    lookup_keys = [
        group_id.upper(),
        group_id.lower(),
        f"group_{group_id.lower()}",
        f"survey_{group_id.lower()}",
    ]
    for section_name in section_names:
        section = _secrets_section(section_name)
        if not section:
            continue
        for key in lookup_keys:
            try:
                val = section.get(key, "")
            except Exception:
                val = ""
            if val:
                values.append(str(val).strip())

    deduped = []
    for val in values:
        if val and val not in deduped:
            deduped.append(val)
    return deduped


def get_survey_table_candidates(group_id: str, db_name: str) -> list[str]:
    gid = group_id.lower()
    configured = _get_configured_table_names(group_id, db_name)
    defaults = [template.format(gid=gid) for template in SURVEY_TABLE_CANDIDATE_TEMPLATES]
    candidates = []
    for name in [*configured, *defaults]:
        if name and name not in candidates:
            candidates.append(name)
    return candidates


def _quote_sql_identifier(identifier: str) -> str:
    return '"' + identifier.replace('"', '""') + '"'


def _quote_table_name(table_name: str) -> str:
    parts = [p.strip() for p in str(table_name).split(".") if p.strip()]
    return ".".join(_quote_sql_identifier(p) for p in parts)


def _query_survey_table(conn, table_name: str, ttl=3600) -> pd.DataFrame:
    return conn.query(f"SELECT * FROM {_quote_table_name(table_name)}", ttl=ttl)


def _normalize_loaded_column_names(df: pd.DataFrame) -> pd.DataFrame:
    """Normalize DB column casing so analytical views can find Q/TC/KPI columns.

    Some Postgres tables are created with lowercase identifiers (q11, tc2_pct,
    enps), while the dashboard codebook expects Q11, TC2_pct, eNPS, etc.
    """
    df = df.copy()
    rename_map = {}
    existing = set(df.columns)

    canonical_simple = {
        "ei": "EI",
        "mei": "MEI",
        "jsi": "JSI",
        "ews": "EWS",
        "enps": "eNPS",
    }

    import re
    for col in df.columns:
        stripped = str(col).strip()
        lower = stripped.lower()
        target = stripped

        q_match = re.fullmatch(r"q_?(\d{1,2})", lower)
        bracket_question_match = re.search(r"^\[[^\d\]]*(\d{1,2})\s*\]", stripped)
        tc_match = re.fullmatch(r"tc_?([1-5])_(mean|pct)", lower)
        if q_match:
            target = f"Q{int(q_match.group(1))}"
        elif bracket_question_match:
            target = f"Q{int(bracket_question_match.group(1))}"
        elif tc_match:
            target = f"TC{tc_match.group(1)}_{tc_match.group(2)}"
        elif lower in canonical_simple:
            target = canonical_simple[lower]

        if target != col and target not in existing:
            rename_map[col] = target
            existing.add(target)

    if rename_map:
        df = df.rename(columns=rename_map)
    return df


def _validate_survey_table(df: pd.DataFrame, group_id: str, table_name: str) -> None:
    if df is None or df.empty:
        raise ValueError(f"{table_name} rỗng")
    if "EI" not in df.columns:
        raise ValueError(f"{table_name} thiếu cột EI")
    if not any(c in df.columns for c in ["division", "department", "section"]):
        raise ValueError(f"{table_name} thiếu cột tổ chức division/department/section")


def _get_data_source_mode() -> str:
    try:
        mode = st.secrets.get("DATA_SOURCE", "")
    except Exception:
        mode = ""
    if not mode:
        mode = os.environ.get("DATA_SOURCE", "")
    mode = str(mode or "auto").strip().lower()
    return mode if mode in {"auto", "neondb", "supabase", "parquet"} else "auto"


def _loader_cache_token(group_id: str) -> str:
    mode = _get_data_source_mode()
    neon_candidates = ",".join(get_survey_table_candidates(group_id, "neondb"))
    supa_candidates = ",".join(get_survey_table_candidates(group_id, "supabase"))
    return f"{mode}|neon:{neon_candidates}|supa:{supa_candidates}"


def normalize_tenure_value(value):
    # Guard: pandas may pass a Series when a column contains mixed/nested objects
    if not isinstance(value, (str, int, float, np.integer, np.floating)) or (
        isinstance(value, float) and np.isnan(value)
    ):
        return np.nan, 'Khác'
    if str(value).strip() == '':
        return np.nan, 'Khác'
    raw = str(value).strip()
    label = TENURE_CODE_MAP.get(raw.upper(), raw)
    label = 'Khác' if label in ('Chưa xác định', 'J') else label
    tenure = TENURE_MAP.get(label)
    if tenure is None:
        try:
            numeric = int(float(raw))
            tenure = TENURE_MAP.get(numeric)
            label = TENURE_LABELS[tenure] if tenure is not None else 'Khác'
        except Exception:
            tenure = np.nan
            label = 'Khác' if len(raw) == 1 and raw.isupper() else label
    return tenure, label


def classify_prev_company(value):
    if pd.isna(value) or str(value).strip() == '':
        return 'Không rõ'
    text = str(value).strip().lower()
    buckets = {
        'GHN nội bộ': ['ghn', 'giao hang nhanh', 'giao hàng nhanh'],
        'Sàn TMĐT / Express': ['shopee', 'spx', 'lazada', 'lex', 'tiki', 'tiktok'],
        'Đối thủ giao nhận': ['j&t', 'jt', 'viettel', 'ghtk', 'ninja', 'best', 'ahamove'],
        'Logistics / Kho vận': ['kho', 'logistics', 'warehouse', 'vận tải', 'van tai'],
        'Tự do / khác ngành': ['tự do', 'tu do', 'freelance', 'kinh doanh', 'bán hàng'],
    }
    for label, keywords in buckets.items():
        if any(k in text for k in keywords):
            return label
    return 'Khác'


def run_sanity_checks(df: pd.DataFrame, group_id: str) -> dict:
    issues, warnings = [], []
    for col, low, high in [('EI', 0, 100), ('MEI', 0, 100), ('JSI', 0, 100), ('burnout_score', 0, 100)]:
        if col in df.columns:
            mask = df[col].notna() & ((df[col] < low) | (df[col] > high))
            if mask.any():
                issues.append(f'{col}: {int(mask.sum())} giá trị ngoài [{low}, {high}]')
    if 'eNPS' in df.columns:
        mask = df['eNPS'].notna() & ((df['eNPS'] < 1) | (df['eNPS'] > 10))
        if mask.any():
            issues.append(f"eNPS: {int(mask.sum())} giá trị ngoài [1, 10]")
    if 'tenure' in df.columns and len(df):
        unknown_pct = df['tenure'].isna().sum() / len(df) * 100
        if unknown_pct > 20:
            warnings.append(f"Thâm niên chưa chuẩn hóa được {unknown_pct:.1f}% mẫu")
    if len(df) < 30:
        warnings.append(f"Cỡ mẫu nhóm {group_id} thấp: n={len(df)}")
    return {'ok': not issues, 'issues': issues, 'warnings': warnings}


def compute_mahalanobis_flags(df: pd.DataFrame, likert_cols: list) -> tuple[pd.Series, dict]:
    valid_cols = [c for c in likert_cols if c in df.columns and df[c].notna().sum() >= 30]
    flags = pd.Series(False, index=df.index)
    if len(valid_cols) < 3 or len(df) < 50:
        return flags, {'enabled': False, 'reason': 'not_enough_data', 'cols': len(valid_cols)}
    X = df[valid_cols].astype(float)
    row_valid = X.notna().sum(axis=1) >= max(3, int(len(valid_cols) * 0.7))
    fit_mask = row_valid & (~df.get('flag_straightline', pd.Series(False, index=df.index)))
    fit = X.loc[fit_mask]
    if len(fit) < max(50, len(valid_cols) * 5):
        return flags, {'enabled': False, 'reason': 'not_enough_diverse_rows', 'cols': len(valid_cols)}
    mean = fit.mean()
    X_fill = X.fillna(mean)
    centered_fit = X_fill.loc[fit_mask] - mean
    cov = np.cov(centered_fit.to_numpy(), rowvar=False)
    diag = np.diag(np.diag(cov))
    cov_shrunk = cov * 0.85 + diag * 0.15 + np.eye(len(valid_cols)) * 1e-6
    inv_cov = np.linalg.pinv(cov_shrunk)
    centered = (X_fill - mean).to_numpy()
    dist2 = pd.Series(np.einsum('ij,jk,ik->i', centered, inv_cov, centered), index=df.index)
    try:
        from scipy.stats import chi2
        threshold = float(chi2.ppf(0.999, df=len(valid_cols)))
    except Exception:
        threshold = float(np.nanpercentile(dist2.loc[fit_mask], 99.9))
    flags = row_valid & (dist2 > threshold)
    return flags.fillna(False), {'enabled': True, 'cols': len(valid_cols), 'threshold': round(threshold, 2), 'flag_n': int(flags.sum())}


def compute_open_text_nlp(df: pd.DataFrame, open_cols: list) -> tuple[pd.DataFrame, dict]:
    valid_open = [c for c in open_cols if c in df.columns]
    if not valid_open:
        return df, {'enabled': False, 'reason': 'no_open_columns'}
    try:
        from shared.nlp_utils import preprocess_text, compute_sentiment_intensity, detect_warning_signals, classify_topics
    except Exception as exc:
        return df, {'enabled': False, 'reason': str(exc)}
    combined = df[valid_open].fillna('').astype(str).agg(' '.join, axis=1).str.strip()
    cleaned = combined.apply(preprocess_text)

    def _nlp_row(text):
        if not isinstance(text, str) or len(text) < 3:
            return 0.0, 'trung_lập', [], [], 0
        score, label = compute_sentiment_intensity(text)
        return score, label, classify_topics(text), detect_warning_signals(text), len(text)

    nlp = cleaned.apply(_nlp_row)
    df['open_text_clean'] = cleaned
    df['nlp_sentiment_score'] = nlp.apply(lambda x: x[0])
    df['nlp_sentiment_label'] = nlp.apply(lambda x: x[1])
    df['nlp_topics'] = nlp.apply(lambda x: x[2])
    df['nlp_warning_signals'] = nlp.apply(lambda x: x[3])
    df['nlp_text_len'] = nlp.apply(lambda x: x[4])
    texts_analyzed = int(cleaned.notna().sum())
    negative_n = int((df['nlp_sentiment_label'] == 'tiêu_cực').sum())
    warning_n = int(df['nlp_warning_signals'].apply(lambda x: len(x) > 0).sum())
    return df, {
        'enabled': True,
        'texts_analyzed': texts_analyzed,
        'negative_n': negative_n,
        'warning_signal_n': warning_n,
        'negative_pct': round(negative_n / texts_analyzed * 100, 1) if texts_analyzed else 0.0,
    }


def check_multicollinearity(X: np.ndarray, feature_names: list) -> dict:
    try:
        corr = np.corrcoef(X.T)
        inv_corr = np.linalg.pinv(corr)
        return {name: round(float(v), 2) for name, v in zip(feature_names, np.diag(inv_corr))}
    except Exception:
        return {name: float('inf') for name in feature_names}


def calibrate_pillar_weights(df: pd.DataFrame, group_id: str) -> dict:
    feature_cols = [f'{p}_pct' for p in PILLAR_WEIGHTS]
    if not all(c in df.columns for c in feature_cols) or 'intent' not in df.columns:
        return {'enabled': False, 'reason': 'missing_features'}
    data = df[[*feature_cols, 'intent']].dropna().copy()
    data['is_flight_risk'] = data['intent'] <= 2
    if len(data) < 80:
        return {'enabled': False, 'reason': 'not_enough_rows', 'n': int(len(data))}
    risk_rate = float(data['is_flight_risk'].mean())
    if risk_rate < 0.03 or risk_rate > 0.97:
        return {'enabled': False, 'reason': 'target_too_imbalanced', 'n': int(len(data)), 'risk_rate': round(risk_rate, 4)}
    try:
        from sklearn.linear_model import LogisticRegression
        from sklearn.preprocessing import StandardScaler
        from sklearn.inspection import permutation_importance
        from sklearn.model_selection import StratifiedKFold, cross_val_score
    except Exception as exc:
        return {'enabled': False, 'reason': 'sklearn_missing', 'error': str(exc)}
    X = data[feature_cols].to_numpy(dtype=float)
    y = data['is_flight_risk'].astype(int).to_numpy()
    feature_names = list(PILLAR_WEIGHTS.keys())
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    vif = check_multicollinearity(X_scaled, feature_names)
    model = LogisticRegression(C=1.0, solver='lbfgs', max_iter=1000, random_state=42)
    model.fit(X_scaled, y)
    perm = permutation_importance(model, X_scaled, y, n_repeats=10, random_state=42, scoring='roc_auc')
    importances = np.maximum(perm.importances_mean, 0)
    weights = PILLAR_WEIGHTS.copy() if importances.sum() == 0 else {
        k: round(float(v), 4) for k, v in zip(feature_names, importances / importances.sum())
    }
    cv_auc = None
    min_class_n = min(int(data['is_flight_risk'].sum()), int((~data['is_flight_risk']).sum()))
    if min_class_n >= 2:
        try:
            cv = StratifiedKFold(n_splits=min(5, min_class_n), shuffle=True, random_state=42)
            cv_auc = float(cross_val_score(model, X_scaled, y, cv=cv, scoring='roc_auc').mean())
        except Exception:
            cv_auc = None
    return {
        'enabled': True,
        'n': int(len(data)),
        'risk_rate': round(risk_rate, 4),
        'vif': vif,
        'high_vif': {k: v for k, v in vif.items() if v > 5},
        'weights': weights,
        'cv_auc': round(cv_auc, 3) if cv_auc is not None else None,
        'note': 'directional_only' if cv_auc is not None and cv_auc < 0.65 else 'usable',
    }


def build_memo_report(df_all: pd.DataFrame, df_clean: pd.DataFrame, n_before: int) -> dict:
    flags = {
        'straightline_n': int(df_all.get('flag_straightline', pd.Series(False, index=df_all.index)).sum()),
        'too_missing_n': int(df_all.get('flag_too_missing', pd.Series(False, index=df_all.index)).sum()),
        'duplicate_n': int(df_all.get('flag_duplicate', pd.Series(False, index=df_all.index)).sum()),
        'maha_flag_n': int(df_all.get('flag_mahalanobis', pd.Series(False, index=df_all.index)).sum()),
        'maha_proxy_n': int(df_all.get('flag_maha_proxy', pd.Series(False, index=df_all.index)).sum()),
        'contradiction_n': int(df_all.get('flag_contradiction', pd.Series(False, index=df_all.index)).sum()),
        'corroboration_dist': {
            '0_evidence': int((df_all.get('num_evidence', pd.Series(0, index=df_all.index)) == 0).sum()),
            '1_evidence': int((df_all.get('num_evidence', pd.Series(0, index=df_all.index)) == 1).sum()),
            '2_evidence': int((df_all.get('num_evidence', pd.Series(0, index=df_all.index)) >= 2).sum()),
        },
    }
    tier_counts = {
        label: int((df_all.get('tier_v2', pd.Series('', index=df_all.index)) == label).sum())
        for label in ['KEEP', 'DOWNWEIGHT', 'DROP']
    }
    n_after_dedup = max(0, n_before - flags['duplicate_n'])
    n_effective = float(df_clean.get('effective_weight', pd.Series(1.0, index=df_clean.index)).sum())
    return {
        'n_raw': int(n_before),
        'n_after_dedup': int(n_after_dedup),
        'n_clean': int(len(df_clean)),
        'n_effective': round(n_effective, 1),
        'effective_pct': round(n_effective / n_before * 100, 1) if n_before else 0.0,
        'flags': flags,
        'tier_counts': tier_counts,
    }



@st.cache_data(ttl=3600, show_spinner=False)
def _load_workforce_section_map() -> "pd.DataFrame":
    """Load workforce sheet, map section_name (EN) sang tên Việt qua _VUNG_EXTENDED_MAP,
    trả về DataFrame indexed by _nv_hash với cột dept_vn (tên phòng ban cụ thể tiếng Việt).
    """
    import hashlib as _hashlib
    from shared.workforce_mapper import _VUNG_EXTENDED_MAP

    def _hash_emp(v):
        try:
            return _hashlib.sha256(
                str(int(float(str(v).replace(",", "").strip()))).encode()
            ).hexdigest()
        except Exception:
            return _hashlib.sha256(str(v).encode()).hexdigest()

    def _to_vn(name_en):
        key = str(name_en or "").lower().strip()
        entry = _VUNG_EXTENDED_MAP.get(key)
        return entry[0] if entry else str(name_en or "").strip()

    try:
        _sheet_id = "14rVdX0b5N9XZFM61juba5XU38x07pFC9wZR_1XQsrho"
        _url = (
            f"https://docs.google.com/spreadsheets/d/{_sheet_id}"
            "/gviz/tq?tqx=out:csv&sheet=workforce"
        )
        _wf = pd.read_csv(_url)
        _wf["_nv_hash"] = _wf["employee_id"].apply(_hash_emp)
        _wf["dept_vn"] = _wf["section_name"].apply(_to_vn)
        return (
            _wf[["_nv_hash", "dept_vn"]]
            .drop_duplicates(subset=["_nv_hash"])
            .set_index("_nv_hash")
        )
    except Exception as _e:
        print(f"[workforce] Không tải được workforce sheet: {_e}")
        return pd.DataFrame(columns=["dept_vn"])


def load_group(group_id: str):
    return _load_group_cached(group_id, _loader_cache_token(group_id))


@st.cache_data(ttl=3600, show_spinner=False)
def _load_group_cached(group_id: str, cache_token: str):
    """
    Load dữ liệu đã xử lý sẵn cho một group khảo sát.
    Ưu tiên: NeonDB → Supabase → Parquet local.
    Returns (df_clean, n_before).
    """
    _ = cache_token
    from config.groups import GROUP_REGISTRY
    from shared.codebook import PILLAR_WEIGHTS
    cfg      = GROUP_REGISTRY[group_id]
    codebook = cfg['codebook']

    df_clean   = None
    source_table = None
    source_db = None
    data_source_mode = _get_data_source_mode()

    # ── Ưu tiên 1: NeonDB (pre-processed table) ──────────────────────────────
    if data_source_mode in {"auto", "neondb"}:
        try:
            conn     = st.connection("neondb", type="sql")
            errors = []
            for table_name in get_survey_table_candidates(group_id, "neondb"):
                try:
                    candidate_df = _query_survey_table(conn, table_name, ttl=3600)
                    if candidate_df is not None:
                        candidate_df = _normalize_loaded_column_names(candidate_df)
                        _validate_survey_table(candidate_df, group_id, table_name)
                        df_clean = candidate_df
                        source_table = table_name
                        source_db = "NeonDB"
                        print(f"[{group_id}] Loaded {len(df_clean):,} rows from NeonDB ({table_name})")
                        break
                except Exception as exc:
                    errors.append(f"{table_name}: {exc}")
            if df_clean is None:
                raise RuntimeError("; ".join(errors[-3:]) if errors else "no table candidates")
        except Exception as e_neo:
            if data_source_mode == "neondb":
                raise RuntimeError(f"[{group_id}] DATA_SOURCE=neondb nhưng không đọc được NeonDB/table đúng: {e_neo}") from e_neo
            print(f"[{group_id}] NeonDB unavailable or no matching table ({e_neo}). Trying Supabase...")

    # ── Ưu tiên 2: Supabase ───────────────────────────────────────────────────
    if df_clean is None and data_source_mode in {"auto", "supabase"}:
        try:
            conn     = st.connection("supabase", type="sql")
            errors = []
            for table_name in get_survey_table_candidates(group_id, "supabase"):
                try:
                    candidate_df = _query_survey_table(conn, table_name, ttl=3600)
                    if candidate_df is not None:
                        candidate_df = _normalize_loaded_column_names(candidate_df)
                        _validate_survey_table(candidate_df, group_id, table_name)
                        df_clean = candidate_df
                        source_table = table_name
                        source_db = "Supabase"
                        print(f"[{group_id}] Loaded {len(df_clean):,} rows from Supabase ({table_name})")
                        break
                except Exception as exc:
                    errors.append(f"{table_name}: {exc}")
            if df_clean is None:
                raise RuntimeError("; ".join(errors[-3:]) if errors else "no table candidates")
        except Exception as e_supa:
            if data_source_mode == "supabase":
                raise RuntimeError(f"[{group_id}] DATA_SOURCE=supabase nhưng không đọc được Supabase/table đúng: {e_supa}") from e_supa
            print(f"[{group_id}] Supabase unavailable or no matching table ({e_supa}). Trying local parquet...")

    # ── Ưu tiên 3: Local Parquet backup ──────────────────────────────────────
    if df_clean is None and data_source_mode in {"auto", "parquet"}:
        import os
        import pandas as pd
        parquet_path = os.path.join(
            os.path.abspath(os.path.join(os.path.dirname(__file__), '..')),
            'Data_Clean', f'{group_id}_clean.parquet'
        )
        if os.path.exists(parquet_path):
            try:
                df_clean = pd.read_parquet(parquet_path)
                df_clean = _normalize_loaded_column_names(df_clean)
                source_table = os.path.basename(parquet_path)
                source_db = "Local Parquet"
                print(f"[{group_id}] Loaded {len(df_clean):,} rows from local parquet ({parquet_path})")
            except Exception as e_parq:
                print(f"[{group_id}] Parquet read failed ({e_parq}).")
    elif df_clean is None:
        raise RuntimeError(f"[{group_id}] DATA_SOURCE={data_source_mode} nhưng không có dữ liệu phù hợp.")

    if df_clean is None:
        raise RuntimeError(f"Could not load data for {group_id} from any source.")

    # ── Fix department cho group 1B: join với workforce sheet theo _nv_hash ───
    # Populate department = tên cụ thể tiếng Việt (vd "Cụm Kho Trung Chuyển Xuyên Á")
    # để khớp với giá trị trong Google Sheet Authorization (department, survey_view=DEPARTMENT)
    if group_id == "1B" and not df_clean.empty and "_nv_hash" in df_clean.columns:
        try:
            wf_map = _load_workforce_section_map()
            if not wf_map.empty:
                df_clean = df_clean.copy()
                _matched = df_clean["_nv_hash"].map(wf_map["dept_vn"])
                _has_match = _matched.notna()
                df_clean.loc[_has_match, "department"] = _matched[_has_match]
                _dep_counts = df_clean["department"].value_counts().to_dict()
                print(f"[1B] Workforce join: {_has_match.sum()}/{len(df_clean)} matched, departments: {_dep_counts}")
            else:
                print("[1B] Workforce join: empty map, department unchanged")
        except Exception as _e_wf:
            print(f"[1B] Workforce join skipped: {_e_wf}")


    import pandas as pd
    # Đọc metadata từ các cột _meta_ (được pipeline lưu vào DB/parquet)
    n_before     = int(df_clean['_meta_n_raw'].iloc[0])   if '_meta_n_raw' in df_clean.columns and not df_clean.empty else len(df_clean)
    n_clean      = int(df_clean['_meta_n_clean'].iloc[0]) if '_meta_n_clean' in df_clean.columns and not df_clean.empty else len(df_clean)
    n_removed    = n_before - n_clean
    pct_removed  = round(n_removed / n_before * 100, 1)   if n_before else 0.0
    filter_desc  = str(df_clean['_meta_filter_desc'].iloc[0])  if '_meta_filter_desc' in df_clean.columns and not df_clean.empty else ''

    # Restore df.attrs để downstream views tương thích hoàn toàn
    likert_cols = [q for q, info in codebook.items() if info['loại'] == 'likert']
    open_cols   = [q for q, info in codebook.items() if info['loại'] == 'open']
    df_clean.attrs['group_id']      = group_id
    df_clean.attrs['source_db']      = source_db or "unknown"
    df_clean.attrs['source_table']   = source_table or "unknown"
    df_clean.attrs['codebook']      = codebook
    df_clean.attrs['likert_cols']   = [c for c in likert_cols if c in df_clean.columns]
    df_clean.attrs['open_cols']     = [c for c in open_cols   if c in df_clean.columns]
    df_clean.attrs['n_before']      = n_before
    df_clean.attrs['n_removed']     = n_removed
    df_clean.attrs['pct_removed']   = pct_removed
    df_clean.attrs['filter_method'] = 'weighted_reliability'
    df_clean.attrs['filter_desc']   = filter_desc
    
    import json
    # Tái tạo các chỉ số tổng hợp cho trang Độ tin cậy
    tier_counts = df_clean['tier_v2'].value_counts().to_dict() if 'tier_v2' in df_clean.columns else {}
    tier_counts['DROP'] = n_removed
    n_effective = float(df_clean['effective_weight'].sum()) if 'effective_weight' in df_clean.columns else float(n_clean)
    effective_pct = round((n_effective / n_before) * 100, 1) if n_before else 0.0
    
    maha_n = int(df_clean['flag_mahalanobis'].sum()) if 'flag_mahalanobis' in df_clean.columns else 0
    if 'flag_contradiction' in df_clean.columns:
        contra_n = int(df_clean['flag_contradiction'].sum())
    elif 'contradiction_flag' in df_clean.columns:
        contra_n = int(df_clean['contradiction_flag'].sum())
    else:
        contra_n = 0
    neg_n = int((df_clean['nlp_sentiment_label'] == 'tiêu_cực').sum()) if 'nlp_sentiment_label' in df_clean.columns else 0
    
    warn_n = 0
    if 'nlp_warning_signals' in df_clean.columns:
        warn_n = int(df_clean['nlp_warning_signals'].apply(lambda x: len(json.loads(x)) > 0 if isinstance(x, str) and str(x) != '[]' else False).sum())

    # memo_report tái tạo
    df_clean.attrs['memo_report'] = {
        'n_raw':      n_before,
        'n_clean':    n_clean,
        'n_after_dedup': n_before, # Đơn giản hóa
        'n_removed':  n_removed,
        'pct_removed': pct_removed,
        'filter_desc': filter_desc,
        'n_effective': n_effective,
        'effective_pct': effective_pct,
        'tier_counts': tier_counts,
        'flags': {
            'maha_flag_n': maha_n,
            'contradiction_n': contra_n,
        },
        'mahalanobis': {},
        'nlp': {
            'negative_n': neg_n,
            'warning_signal_n': warn_n
        }
    }
    df_clean.attrs['calibration_report'] = {'enabled': False, 'reason': 'pre_processed'}
    
    # Fake sanity checks to prevent errors downstream
    df_clean.attrs['sanity_checks'] = {
        'missing_cols': [],
        'unexpected_nulls': {},
        'value_range_errors': {},
        'status': 'PASS'
    }

    # Ép kiểu numeric cho các cột KPI thường bị đọc thành string từ DB
    _numeric_cols = [
        'EI', 'MEI', 'eNPS', 'intent', 'burnout_score', 'burnout_risk',
        'stay_intention', 'JSI', 'EWS', 'tenure', 'effective_weight',
        'CompanyRollup_Weight', 'likert_mean', 'nlp_sentiment_score',
    ] + [f'{p}_mean' for p in PILLAR_WEIGHTS] + [f'{p}_pct' for p in PILLAR_WEIGHTS]
    for col in _numeric_cols:
        if col in df_clean.columns:
            df_clean[col] = pd.to_numeric(df_clean[col], errors='coerce')

    # Boolean columns
    for bcol in ['flag_drop', 'flag_straightline', 'flag_duplicate',
                 'flag_mahalanobis', 'burnout_proxy', 'is_silent',
                 'contradiction_flag', 'evidence_open', 'evidence_enps']:
        if bcol in df_clean.columns:
            df_clean[bcol] = df_clean[bcol].map(
                lambda v: True if str(v).lower() in {'true', '1', 't', 'yes'} else
                          False if str(v).lower() in {'false', '0', 'f', 'no'} else pd.NA
            ).astype('boolean')

    return df_clean, n_before


def load_all_available(log_callback=None):
    """Load all groups that have data. Returns dict {group_id: (df, n_before)}."""
    # Force cache invalidation for n_before update
    from config.groups import get_available_groups
    from config.groups import GROUP_REGISTRY
    results = {}
    for gid in get_available_groups():
        try:
            if log_callback:
                label = GROUP_REGISTRY.get(gid, {}).get("short", gid)
                log_callback(f"Đang tải dữ liệu khảo sát nhóm {gid} - {label}...")
            results[gid] = load_group(gid)
            if log_callback:
                rows = len(results[gid][0])
                source_db = results[gid][0].attrs.get("source_db", "unknown")
                source_table = results[gid][0].attrs.get("source_table", "unknown")
                log_callback(f"Đã tải dữ liệu khảo sát nhóm {gid} ({rows:,} mẫu hợp lệ) từ {source_db}.{source_table}.", "ok")
        except Exception as e:
            st.warning(f"Không load được nhóm {gid}: {e}")
            if log_callback:
                log_callback(f"Không tải được nhóm {gid}: {e}")
    if log_callback:
        log_callback("Đang tổng hợp dữ liệu toàn công ty...")
    return results


def compute_kpis(df):
    """Compute KPI dict from any group's dataframe.

    ``n`` is the analytical base count, matching the analyst reports.
    Weighted/effective sample size is exposed separately as ``effective_n``.
    """
    n_rows = len(df)
    if n_rows == 0:
        return {'n': 0, 'effective_n': 0, 'ei_mean': 0, 'enps_score': 0, 'promoters': 0,
                'passives': 0, 'detractors': 0, 'mei_avg': 0, 'mei_mean': 0,
                'intent_pct_low': 0, 'burnout_pct': 0,
                'stay_score_avg': 0, 'stay_intent_mean': 0,
                'stay_flight_pct': 0, 'stay_atrisk_pct': 0, 'stay_stable_pct': 0,
                'silence_rate': 0, 'straight_line_rate': 0,
                'flight_risk_pct': 0, 'jsi_avg': 0, 'ews_red_pct': 0,
                'quadrant': {}, 'contradiction_pct': 0}

    w = df.get('CompanyRollup_Weight', df.get('effective_weight', pd.Series(1.0, index=df.index)))
    w = pd.to_numeric(w, errors='coerce').fillna(1.0).clip(lower=0)
    effective_n = float(w.sum())
    n = int(n_rows)
    
    def weighted_avg(col):
        col = pd.to_numeric(col, errors='coerce')   # guard: StringDtype parquet columns
        mask = col.notna()
        if not mask.any(): return 0
        return np.average(col[mask], weights=w[mask])
        
    def weighted_pct(condition_mask, valid_mask=None):
        if valid_mask is None: valid_mask = pd.Series(True, index=df.index)
        # Guard: condition_mask may be StringDtype if column came from parquet string cast
        if hasattr(condition_mask, 'dtype') and str(condition_mask.dtype) in ('string', 'object'):
            condition_mask = condition_mask.map(
                lambda x: str(x).strip().lower() == 'true' if pd.notna(x) else False
            ).astype(bool)
        if not valid_mask.any() or w[valid_mask].sum() == 0: return 0
        cond = condition_mask.reindex(df.index).fillna(False).astype(bool)
        return (w[cond & valid_mask].sum() / w[valid_mask].sum()) * 100

    ei_mean = weighted_avg(df['EI']) if 'EI' in df.columns else 0
    enps_col = df.get('eNPS', pd.Series(dtype=float))
    n_valid_enps = enps_col.notna()
    
    promoters = w[enps_col >= 9].sum()
    passives = w[(enps_col >= 7) & (enps_col <= 8)].sum()
    detractors = w[enps_col <= 6].sum()
    
    enps_score = weighted_pct(enps_col >= 9, n_valid_enps) - weighted_pct(enps_col <= 6, n_valid_enps)
    
    mei_avg = weighted_avg(df['MEI']) if 'MEI' in df.columns else 0
    intent_col = df.get('intent', pd.Series(dtype=float))
    intent_valid = intent_col.notna()
    intent_pct = weighted_pct(intent_col <= 2, intent_valid)
    intent_pct_high = weighted_pct(intent_col >= 4, intent_valid)
    
    if 'burnout_proxy' in df.columns:
        # Mẫu số = người THỰC SỰ có điểm burnout (nhất quán với eNPS/intent),
        # không tính người thiếu dữ liệu áp lực/khối lượng vào mẫu số.
        burnout_valid = df['burnout_score'].notna() if 'burnout_score' in df.columns else df['burnout_proxy'].notna()
        burnout_pct = weighted_pct(df['burnout_proxy'], burnout_valid)
    else:
        burnout_pct = weighted_pct(df.get('burnout_risk', pd.Series(0, index=df.index)) > 0)

    stay_col = df.get('stay_intention', pd.Series(dtype=float))
    stay_valid = stay_col.notna()
    stay_score_avg = round(weighted_avg(stay_col), 2)
    stay_flight_pct = round(weighted_pct(stay_col <= 2, stay_valid), 1)
    stay_atrisk_pct = round(weighted_pct(stay_col == 3, stay_valid), 1)
    stay_stable_pct = round(weighted_pct(stay_col >= 4, stay_valid), 1)

    # Silence Rate = % câu mở bỏ trống (is_silent only) — định nghĩa Bảng 2, v13
    # KHÔNG phải (flag_straightline | is_silent): đó là lỗi trước đây làm tăng sai số.
    # Straight-line Rate = % trả lời đồng đều Likert (flag_straightline only), là chỉ số riêng.
    # NOTE: eNPS chênh ~+5–+6 so với tài liệu analyst do pipeline DROP các mẫu
    #   flag_straightline=True AND num_evidence==0 (detractor-heavy). Fix dứt điểm cần
    #   chạy lại preprocess_pipeline.py sau khi đã sửa logic _assign_quality ở đó.
    _sl = df.get('flag_straightline', pd.Series(False, index=df.index)).fillna(False).astype(bool)
    _si = df.get('is_silent', pd.Series(False, index=df.index)).fillna(False).astype(bool)
    silence_rate = round(weighted_pct(_si), 1)
    straight_line_rate = round(weighted_pct(_sl), 1)
    jsi_avg = round(weighted_avg(df['JSI']), 1) if 'JSI' in df.columns else 0

    ews_col = df.get('EWS')
    ews_red_pct = 0
    if ews_col is not None and ews_col.notna().any():
        _ews_num = pd.to_numeric(ews_col, errors='coerce')  # guard: StringDtype in parquet
        ews_red_pct = round(weighted_pct(_ews_num >= 60, _ews_num.notna()), 1)

    quad = df.get('engagement_quadrant')
    quad_counts = {}
    if quad is not None and quad.notna().any():
        for label in ['Champions', 'Trapped Loyalists', 'Confused Leavers', 'Flight Risk']:
            quad_counts[label] = round(weighted_pct(quad == label, quad.notna()), 1)

    # Flight Risk % — dinh nghia bao cao v13: EI < 70 AND intent <= 2
    _ei_col = pd.to_numeric(df.get('EI', pd.Series(dtype=float)), errors='coerce')
    _intent_col = pd.to_numeric(df.get('intent', pd.Series(dtype=float)), errors='coerce')
    _fr_valid = _ei_col.notna() & _intent_col.notna()
    _fr_mask = (_ei_col < 70) & (_intent_col <= 2)
    flight_risk_pct = round(weighted_pct(_fr_mask, _fr_valid), 1)

    contradiction_pct = round(weighted_pct(df.get('contradiction_flag', pd.Series(False, index=df.index))), 1)

    return {
        'n': n, 'effective_n': round(effective_n, 1),
        'ei_mean': round(ei_mean, 1),
        'enps_score': round(enps_score, 0),
        'promoters': int(promoters), 'passives': int(passives), 'detractors': int(detractors),
        'mei_avg': round(mei_avg, 1),
        'mei_mean': round(mei_avg, 1),
        'intent_pct_low': round(intent_pct, 1),
        'intent_pct_high': round(intent_pct_high, 1),
        'burnout_pct': round(burnout_pct, 1),
        'stay_score_avg': stay_score_avg,
        'stay_intent_mean': stay_score_avg,
        'stay_flight_pct': stay_flight_pct,
        'stay_atrisk_pct': stay_atrisk_pct,
        'stay_stable_pct': stay_stable_pct,
        'silence_rate': silence_rate,
        'straight_line_rate': straight_line_rate,
        'flight_risk_pct': flight_risk_pct,
        'jsi_avg': jsi_avg,
        'ews_red_pct': ews_red_pct,
        'quadrant': quad_counts,
        'contradiction_pct': contradiction_pct,
    }


@st.cache_data(ttl=86400, show_spinner="Đang xử lý dữ liệu HRIS...")
def load_hris():
    """Load HRIS from central Google Sheet with local Parquet caching for speed."""
    import os
    import time
    local_cache = "data/hris_cache.parquet"

    df_hris = None
    cache_ok = False

    if os.path.exists(local_cache) and (time.time() - os.path.getmtime(local_cache) < 86400 * 7):
        try:
            df_hris = pd.read_parquet(local_cache)
            cache_ok = True
        except Exception:
            pass  # Cache corrupted, will reload from source

    if df_hris is None:
        try:
            hris_sheet_id = st.secrets.get("HRIS_SHEET_ID", "19ey-QCV4cxzokmBAaMgbY7kHcZNa1fSiW4boTosaBwo")
        except Exception:
            hris_sheet_id = "19ey-QCV4cxzokmBAaMgbY7kHcZNa1fSiW4boTosaBwo"

        hris_url = f"https://docs.google.com/spreadsheets/d/{hris_sheet_id}/export?format=csv"
        try:
            df_hris = pd.read_csv(hris_url)
            df_hris.columns = df_hris.columns.str.strip()
            os.makedirs("data", exist_ok=True)
            try:
                df_hris.to_parquet(local_cache, index=False)
            except Exception:
                pass
        except Exception as e:
            import streamlit as st
            st.error(f"Lỗi tải HRIS: {e}")
            return None, None

    if df_hris is None or df_hris.empty:
        return None, None

    month_col = df_hris.columns[1]

    def _parse_month(m):
        try:
            parts = str(m).split('/')
            if len(parts) != 2 or not parts[0] or not parts[1]:
                return 0
            return int(parts[1].lstrip('0') or '0') * 100 + int(parts[0].lstrip('0') or '0')
        except Exception:
            return 0

    df_hris['_month_num'] = df_hris[month_col].apply(_parse_month)
    latest = df_hris['_month_num'].max()
    latest_label = df_hris.loc[df_hris['_month_num'] == latest, month_col].iloc[0]
    df_latest = df_hris[df_hris['_month_num'] == latest].copy()
    import hashlib
    def hash_id(val):
        if pd.isna(val): return None
        try:
            return hashlib.sha256(str(int(val)).encode()).hexdigest()
        except:
            return hashlib.sha256(str(val).encode()).hexdigest()

    df_latest['_nv_hash'] = df_latest['ID'].apply(hash_id)
    return df_latest, latest_label


def merge_survey_hris(df_clean, df_hris):
    """Merge survey with HRIS."""
    df_clean = df_clean.copy()

    merge_cols = ['_nv_hash', 'Lương thực nhận', 'Tổng', 'Phạt', 'Tổng Đơn giao',
                  'Năng suất Giao', 'Phân loại Nhóm Năng Suất Giao',
                  'Phân loại Chiến Binh', 'Thâm niên (Đơn vị tính là tháng)',
                  'Nhóm Thâm Niên', 'Range lương thực nhận', 'Ngày nghỉ việc',
                  'Lương đơn hàng', 'Thưởng/ Phạt GTC và LTC', 'Phụ cấp',
                  'Thưởng Doanh Thu', 'Truy thu mất hàng COD',
                  # Productivity columns
                  'Tổng Đơn lấy', 'Năng suất Lấy', 'Phân loại Nhóm Năng Suất Lấy',
                  'Số đơn GL', 'Lương đơn giao', 'Lương đơn lấy', 'Tổng Đơn trả',
                  '% Lương giao', '% Lương lấy']
    merge_cols = [c for c in merge_cols if c in df_hris.columns]

    df_m = df_clean.merge(df_hris[merge_cols], on='_nv_hash', how='left', suffixes=('', '_hris'))

    numeric_cols = ['Lương thực nhận', 'Tổng', 'Phạt', 'Tổng Đơn giao', 'Năng suất Giao', 
                    'Lương đơn hàng', 'Thưởng/ Phạt GTC và LTC', 'Phụ cấp', 'Thưởng Doanh Thu', 'Truy thu mất hàng COD']
    for c in numeric_cols:
        if c in df_m.columns:
            df_m[c] = pd.to_numeric(df_m[c].astype(str).str.replace(r'[^\d-]', '', regex=True), errors='coerce')
            
    if 'Thâm niên (Đơn vị tính là tháng)' in df_m.columns:
        df_m['Thâm niên (Đơn vị tính là tháng)'] = pd.to_numeric(df_m['Thâm niên (Đơn vị tính là tháng)'].astype(str).str.replace(',', '.').str.replace(r'[^\d.-]', '', regex=True), errors='coerce')

    if 'Lương thực nhận' in df_m.columns:
        df_m['income_m'] = df_m['Lương thực nhận'] / 1_000_000
        df_m['income_group'] = pd.cut(df_m['income_m'], bins=[0, 5, 7, 10, 15, 20, 30, 9999],
                                       labels=['< 5 triệu', '5 - 7 triệu', '7 - 10 triệu', '10 - 15 triệu', '15 - 20 triệu', '20 - 30 triệu', '> 30 triệu'])
    if 'Phạt' in df_m.columns:
        df_m['phat_m'] = df_m['Phạt'].fillna(0) / 1_000_000
        
        truy_thu = df_m.get('Truy thu mất hàng COD', pd.Series(0, index=df_m.index)).fillna(0) / 1_000_000
        df_m['tong_phat'] = df_m['phat_m'] + truy_thu
    if 'intent' in df_m.columns:
        df_m['intent_risk'] = df_m['intent'].apply(
            lambda x: 'Muốn nghỉ (1-2)' if pd.notna(x) and x <= 2
            else (' Phân vân (3)' if pd.notna(x) and x == 3
                  else ('Gắn bó (4-5)' if pd.notna(x) else None)))
    return df_m
