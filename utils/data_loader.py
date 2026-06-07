"""
Data Loader — EES 2026 Dashboard (Multi-Group)
Cached data loading & KPI computation for any survey group.
"""
import os, sys
import pandas as pd
import numpy as np
from collections import defaultdict
import streamlit as st

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


def normalize_tenure_value(value):
    if pd.isna(value) or str(value).strip() == '':
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
def load_group(group_id: str):
    """Load & clean a single survey group. Returns (df_clean, n_before)."""
    from config.groups import GROUP_REGISTRY
    cfg = GROUP_REGISTRY[group_id]
    codebook = cfg['codebook']
    try:
        try:
            conn = st.connection("neondb", type="sql")
            table_name = f"survey_{group_id.lower()}"
            df_raw = conn.query(f"SELECT * FROM {table_name}", ttl=3600)
            print(f" Đã tải {len(df_raw)} dòng dữ liệu {group_id} từ NeonDB siêu tốc!")
        except Exception as e_neon:
            print(f"Lỗi kết nối NeonDB ({e_neon}). Đang thử Supabase...")
            conn = st.connection("supabase", type="sql")
            table_name = f"survey_{group_id.lower()}"
            df_raw = conn.query(f"SELECT * FROM {table_name}", ttl=3600)
            print(f" Đã tải {len(df_raw)} dòng dữ liệu {group_id} từ Supabase siêu tốc!")
    except Exception as e:
        # Fallback to CSV if DB is not reachable
        print(f"Lỗi kết nối cả Supabase và NeonDB ({e}). Đang dùng file dự phòng (Google Sheets)...")
        df_raw = pd.read_csv(cfg['url'])
    n_before = len(df_raw)

    # Rename columns
    col_rename = {}
    for q_id, q_info in codebook.items():
        idx = q_info['col_idx']
        if idx < len(df_raw.columns):
            col_rename[df_raw.columns[idx]] = q_id
    df = df_raw.rename(columns=col_rename).copy()

    likert_cols = [q for q, info in codebook.items() if info['loại'] == 'likert']
    open_cols = [q for q, info in codebook.items() if info['loại'] == 'open']

    # Decode
    for col in likert_cols:
        if col in df.columns:
            df[col] = df[col].apply(decode_likert)
    if 'Q31' in df.columns:
        df['eNPS'] = df['Q31'].apply(decode_enps)
    if 'Q30' in df.columns:
        df['intent'] = df['Q30'].apply(decode_intent)
    else:
        df['intent'] = None
    df['eNPS_group'] = df.get('eNPS', pd.Series(dtype=float)).apply(classify_enps)

    # Decode demographic Q5 (Thâm niên) if present.
    if 'Q5' in df.columns:
        tenure_norm = df['Q5'].apply(normalize_tenure_value)
        df['tenure'] = tenure_norm.apply(lambda x: x[0])
        df['tenure_label'] = tenure_norm.apply(lambda x: x[1])
        df['Q5'] = df['tenure_label']

    if 'Q6' in df.columns:
        df['prev_company_cat'] = df['Q6'].apply(classify_prev_company)

    # Quality flags
    df['likert_mean'] = df[likert_cols].mean(axis=1)
    df['_likert_sd'] = df[likert_cols].std(axis=1)
    df['n_valid_likert'] = df[likert_cols].notna().sum(axis=1)
    df['flag_straightline'] = (df['_likert_sd'] == 0) & (df['n_valid_likert'] >= 10)
    df['flag_too_missing'] = (df[likert_cols].isna().sum(axis=1) / len(likert_cols) * 100) > 80

    # Hàm kiểm tra câu hỏi mở có ý nghĩa không
    def is_meaningless(text):
        if pd.isna(text): return True
        t = str(text).strip().lower()
        if t in ['', 'không', 'khong', 'không có', 'khong co', 'không ý kiến', 'khong y kien', 'k', 'ko', 'none', 'na', 'n/a', '-', '.']:
            return True
        if len(t) < 2 and not t.isalnum(): return True
        return False

    df['flag_empty_open'] = df[open_cols].apply(lambda row: all(is_meaningless(x) for x in row), axis=1) if open_cols else True
    df['evidence_open'] = ~df['flag_empty_open']
    df, _nlp_report = compute_open_text_nlp(df, open_cols)
    
    enps_col = df.get('eNPS', pd.Series(dtype=float))
    df['evidence_enps'] = False
    if 'eNPS' in df.columns:
        df['evidence_enps'] = (
            ((df['likert_mean'] >= 4) & (enps_col >= 9)) |
            ((df['likert_mean'].between(3, 4, inclusive='both')) & (enps_col.between(7, 8, inclusive='both'))) |
            ((df['likert_mean'] <= 2) & (enps_col <= 6))
        )
        
    df['num_evidence'] = df['evidence_open'].astype(int) + df['evidence_enps'].astype(int)

    if 'eNPS' in df.columns:
        df['flag_contradiction'] = (
            ((df['likert_mean'] >= 4) & (df['eNPS'] <= 6)) |
            ((df['likert_mean'] <= 2) & (df['eNPS'] >= 9))
        )
    else:
        df['flag_contradiction'] = False

    def get_long_open(row):
        txt = " ".join([str(x).strip() for x in row[open_cols] if pd.notna(x) and str(x).strip()])
        return txt if len(txt) >= 25 else np.nan

    df['_long_open'] = df.apply(get_long_open, axis=1) if open_cols else np.nan
    dup_cols = [c for c in likert_cols if c in df.columns]
    if 'eNPS' in df.columns:
        dup_cols.append('eNPS')
    if '_long_open' in df.columns:
        dup_cols.append('_long_open')
    df['flag_duplicate'] = False
    if dup_cols and '_long_open' in dup_cols:
        df['flag_duplicate'] = df.duplicated(subset=dup_cols, keep='first') & df['_long_open'].notna()

    df['flag_maha_proxy'] = df['flag_too_missing'] | ((df['_likert_sd'] > 1.8) & (df['n_valid_likert'] >= 10))
    df['flag_mahalanobis'], _mahalanobis_report = compute_mahalanobis_flags(df, likert_cols)

    def _assign_quality(row):
        if row['flag_too_missing'] or row['flag_duplicate'] or row['flag_mahalanobis']:
            return 0.0, 'DROP'
        if row['flag_straightline'] and row['num_evidence'] == 0:
            return 0.0, 'DROP'
        if row['num_evidence'] == 0:
            return 0.3, 'DOWNWEIGHT'
        if row['flag_straightline'] or row['flag_contradiction'] or row['num_evidence'] == 1:
            return 0.7, 'DOWNWEIGHT'
        else:
            return 1.0, 'KEEP'

    quality = df.apply(_assign_quality, axis=1)
    df['effective_weight'] = [x[0] for x in quality]
    df['tier_v2'] = [x[1] for x in quality]
    df['CompanyRollup_Weight'] = df['effective_weight']
    df['flag_drop'] = df['tier_v2'] == 'DROP'

    df_clean = df[~df['flag_drop']].copy()
    _filter_method = 'weighted_reliability'
    _filter_desc   = 'Tính effective_weight (0.3 / 0.7 / 1.0) và tier_v2. DROP khi thiếu dữ liệu nặng, trùng lặp, Mahalanobis outlier hoặc straightline không có bằng chứng.'

    _n_removed = n_before - len(df_clean)
    _pct_removed = round(_n_removed / n_before * 100, 1) if n_before > 0 else 0

    # Org mapping
    vung_col = df_clean.columns[10]
    for c in df_clean.columns:
        if 'Vùng' in str(c) or 'vùng' in str(c):
            vung_col = c; break
    # Pre-mapping: dịch tên địa điểm tiếng Anh của 1B → tiếng Việt
    # trước khi workforce mapper lookup (Mapping sheet chỉ có tên tiếng Việt)
    _1B_EN_VN = {
        'xuyen a sorting centers':   'Cụm Kho Trung Chuyển Xuyên Á',
        'hung yen sorting centers':  'Cụm Kho Trung Chuyển Hưng Yên',
        'm12 sorting centers':       'Cụm Kho Trung Chuyển M12',
        'dai tu sorting centers':    'Cụm Kho Trung Chuyển Đài Tư',
        'freight operations - hcm':  'Bộ Phận Vận Hành HCM',
        'freight operations - hn':   'Bộ Phận Vận Hành HN',
        'xbg region':                'Vùng XBG',
        'ttb region':                'Vùng TTB',
        'nno region':                'Vùng HNO',
    }
    if group_id == '1B' and vung_col in df_clean.columns:
        df_clean[vung_col] = df_clean[vung_col].apply(
            lambda x: _1B_EN_VN.get(str(x).strip().lower(), x) if pd.notna(x) else x
        )

    try:
        raw_clean_df = df_raw.loc[df_clean.index].copy()
        df_clean = map_survey_to_org(df_clean, group=group_id, vung_col=vung_col,
                                     id_col=df_clean.columns[1], raw_df=raw_clean_df)

                                     
        if group_id == '3A':
            EXCLUDE_DIVS = [
                "phòng dịch vụ kho vận", 
                "phòng kinh doanh khách hàng lớn",
                "phòng nền tảng vận hành",
                "technology operations department"
            ]
            m_exclude = (
                df_clean["division"].astype(str).str.strip().str.lower().isin(EXCLUDE_DIVS) |
                df_clean["department"].astype(str).str.strip().str.lower().isin(EXCLUDE_DIVS) |
                df_clean["section"].astype(str).str.strip().str.lower().isin(EXCLUDE_DIVS) |
                df_clean["sv_label"].astype(str).str.strip().str.lower().isin(EXCLUDE_DIVS)
            )
            n_before -= m_exclude.sum()
            df_clean = df_clean[~m_exclude].copy()
    except Exception as e:
        print(f"Lỗi map data: {e}")
        df_clean['division'] = 'Khác'
        df_clean['department'] = 'Khác'
        df_clean['section'] = 'Khác'

    report_mask = df['flag_drop'] | df.index.isin(df_clean.index)
    _memo_report = build_memo_report(df[report_mask], df_clean, n_before)
    _memo_report['mahalanobis'] = _mahalanobis_report
    _memo_report['nlp'] = _nlp_report
    _n_removed = n_before - len(df_clean)
    _pct_removed = round(_n_removed / n_before * 100, 1) if n_before > 0 else 0

    # Pillar scores
    pillar_cols = defaultdict(list)
    for q_id, info in codebook.items():
        if info['trụ_cột']:
            pillar_cols[info['trụ_cột']].append(q_id)
    for pillar, cols in pillar_cols.items():
        valid = [c for c in cols if c in df_clean.columns]
        df_clean[f'{pillar}_mean'] = df_clean[valid].mean(axis=1)
        df_clean[f'{pillar}_pct'] = df_clean[f'{pillar}_mean'].apply(calc_engagement_pct)

    _calibration_report = calibrate_pillar_weights(df_clean, group_id)

    # EI — weighted sum của các trụ cột, CHUẨN HÓA LẠI trọng số theo từng dòng
    # trên các trụ cột thực sự có điểm. Tránh EI bị NaN khi một người bỏ trống
    # trọn một trụ cột (vd 1A/1B chỉ có 2 câu TC1), và tránh under-weight khi
    # thiếu cột trụ cột.
    pillar_pcts = [f'{p}_pct' for p in PILLAR_WEIGHTS.keys()]
    weights = list(PILLAR_WEIGHTS.values())
    present = [(p, w) for p, w in zip(pillar_pcts, weights) if p in df_clean.columns]
    if present:
        pct_frame = pd.DataFrame({p: df_clean[p] for p, _ in present})
        w_series = pd.Series({p: w for p, w in present})
        valid_mask = pct_frame.notna()
        eff_w = valid_mask.mul(w_series, axis=1)
        w_sum = eff_w.sum(axis=1)
        weighted = (pct_frame.fillna(0.0) * eff_w).sum(axis=1)
        df_clean['EI'] = np.where(w_sum > 0, weighted / w_sum, np.nan)
    else:
        df_clean['EI'] = np.nan
    df_clean['EI_class'] = df_clean['EI'].apply(classify_ei)

    # MEI — Manager Effectiveness Index (% câu TC2 được đánh ≥4)
    # Dùng toàn bộ câu TC2 của ĐÚNG nhóm thay vì hard-code Q-number theo 1A/1B.
    # (Với 2A/2B/3A/3B, TC2 = Q13-Q17; với 1A/1B, TC2 = Q11-Q15.)
    mei_cols = [c for c in get_pillar_questions(group_id, 'TC2') if c in df_clean.columns]
    if mei_cols:
        df_clean['MEI'] = df_clean[mei_cols].apply(
            lambda r: (r >= 4).sum() / r.notna().sum() * 100 if r.notna().sum() > 0 else None, axis=1)

    # Burnout score 0-100 theo v3. Giữ burnout_risk để view/anomaly cũ tương thích.
    pressure_roles = ['pressure', 'workload']
    pressure = [q for q in (get_role_question(group_id, r) for r in pressure_roles)
                if q and q in df_clean.columns]
    if pressure:
        burnout_components = [((5 - df_clean[q]) / 4 * 100) for q in pressure]
        df_clean['burnout_score'] = sum(burnout_components) / len(burnout_components)
        df_clean['burnout_score'] = df_clean['burnout_score'].round(1)
        df_clean['burnout_proxy'] = df_clean['burnout_score'] >= 50
        df_clean['burnout_risk'] = (df_clean['burnout_score'] - 50) / 25

    # Stay Intention — dùng câu Ý ĐỊNH Ở LẠI thực sự (Q30 → cột `intent`),
    # KHÔNG dùng Q22 (vốn là câu Likert thuộc TC4). Thang 1–5, cao = muốn ở lại.
    # Flight Risk: ≤ 2 | At Risk: = 3 | Stable: ≥ 4
    if 'intent' in df_clean.columns and df_clean['intent'].notna().any():
        df_clean['stay_intention'] = df_clean['intent']
        df_clean['stay_risk_group'] = df_clean['intent'].apply(
            lambda v: ('Flight Risk' if v <= 2 else ('At Risk' if v == 3 else 'Stable'))
            if pd.notna(v) else None
        )

    # ════════════════════════════════════════════════════════════
    # CHỈ SỐ NỀN TẢNG (Foundation Indices) — mục 4.1 KE_HOACH
    # ════════════════════════════════════════════════════════════

    # 1) Silence Rate — tỷ lệ KHÔNG điền câu hỏi mở "Cần cải thiện".
    #    Silence cao = thiếu niềm tin rằng phản hồi có tác dụng.
    #    Tài liệu gọi là Q26; trong codebook này câu "Cần thay đổi/cải thiện"
    #    là câu mở cuối cùng (Q34). Fallback: dùng flag_empty_open nếu thiếu.
    improve_open = None
    for cand in ['Q34', 'Q33', 'Q32']:
        if cand in df_clean.columns:
            improve_open = cand
            break
    if improve_open is not None:
        df_clean['is_silent'] = df_clean[improve_open].apply(is_meaningless)
    else:
        df_clean['is_silent'] = df_clean.get('flag_empty_open', pd.Series(True, index=df_clean.index))

    # 2) JSI Proxy (Overall Job Satisfaction Index)
    #    JSI ≈ 0.4*TC4 + 0.3*TC3_workload + 0.3*TC5_respect  (thang %, 0-100)
    #    - TC4: dùng TC4_pct (đãi ngộ & công bằng)
    #    - TC3_workload: câu workload (cường độ/khối lượng) — role 'workload'
    #    - TC5_respect: câu pride/được tôn trọng — role 'pride'
    workload_q = get_role_question(group_id, 'workload')
    respect_q = get_role_question(group_id, 'pride')
    tc4_pct_series = df_clean.get('TC4_pct')
    if tc4_pct_series is not None:
        workload_pct = (df_clean[workload_q].apply(calc_engagement_pct)
                        if workload_q and workload_q in df_clean.columns else None)
        respect_pct = (df_clean[respect_q].apply(calc_engagement_pct)
                       if respect_q and respect_q in df_clean.columns else None)
        # Nếu thiếu thành phần nào, rút trọng số về phần còn lại (chuẩn hóa).
        comps, weights = [], []
        comps.append(tc4_pct_series); weights.append(0.4)
        if workload_pct is not None:
            comps.append(workload_pct); weights.append(0.3)
        if respect_pct is not None:
            comps.append(respect_pct); weights.append(0.3)
        wsum = sum(weights)
        df_clean['JSI'] = sum(c * (w / wsum) for c, w in zip(comps, weights))

    # 3) Early Warning Score (EWS) — cảnh báo nghỉ sớm cho nhóm thâm niên mới.
    #    Dựa trên: ý định ở lại (intent), TC2 (quản lý), TC3 (điều kiện).
    #    Điểm 0-100, cao = rủi ro cao. Chỉ tính cho nhóm mới; còn lại = NaN.
    if 'tenure' in df_clean.columns:
        ews_threshold = EWS_TENURE_THRESHOLD.get(group_id, 2)
        early_mask = df_clean['tenure'].notna() & (df_clean['tenure'] <= ews_threshold)

        def _ews(row):
            score = 0.0
            n = 0
            # Intent thấp → rủi ro cao
            iv = row.get('intent')
            if pd.notna(iv):
                score += (5 - iv) / 4 * 40; n += 1   # tối đa 40 điểm
            tc2 = row.get('TC2_pct')
            if pd.notna(tc2):
                score += (100 - tc2) / 100 * 30; n += 1  # tối đa 30
            tc3 = row.get('TC3_pct')
            if pd.notna(tc3):
                score += (100 - tc3) / 100 * 30; n += 1  # tối đa 30
            return round(score, 1) if n > 0 else None

        df_clean['EWS'] = None
        if early_mask.any():
            df_clean.loc[early_mask, 'EWS'] = df_clean.loc[early_mask].apply(_ews, axis=1)
        df_clean['EWS_flag'] = df_clean['EWS'].apply(
            lambda v: 'Cảnh báo đỏ' if pd.notna(v) and v >= 60
            else ('Theo dõi' if pd.notna(v) and v >= 40 else ('Ổn' if pd.notna(v) else None))
        )

    # 4) Engagement Quadrant — v3 dùng EI x eNPS.
    #    Champions / Trapped Loyalists / Confused Leavers / Flight Risk.
    if 'eNPS' in df_clean.columns and 'EI' in df_clean.columns:
        def _quadrant(row):
            e = row.get('eNPS')
            ei = row.get('EI')
            if pd.isna(e) or pd.isna(ei):
                return None
            enps_high = e >= 9
            ei_high = ei >= 65
            if enps_high and ei_high:
                return 'Champions'
            if (not enps_high) and ei_high:
                return 'Trapped Loyalists'
            if enps_high and (not ei_high):
                return 'Confused Leavers'
            return 'Flight Risk'
        df_clean['engagement_quadrant'] = df_clean.apply(_quadrant, axis=1)

    # 5) Contradiction Index (per-row) — gắn kết cao (EI) nhưng phản hồi mở tiêu cực.
    #    Đánh dấu hàng có EI cao nhưng vẫn "im lặng/né tránh" hoặc intent thấp,
    #    phục vụ phát hiện "sức khỏe giả" (fear-based compliance). Sentiment chi tiết
    #    được tính ở tầng NLP; ở đây chỉ đánh dấu mâu thuẫn EI↑ vs intent↓.
    if 'EI' in df_clean.columns and 'intent' in df_clean.columns:
        df_clean['contradiction_flag'] = (
            (df_clean['EI'] >= 75) & (df_clean['intent'] <= 2)
        )

    # NLP prep
    try:
        from shared.nlp_utils import preprocess_text
        for q in open_cols:
            if q in df_clean.columns:
                df_clean[f'{q}_clean'] = df_clean[q].apply(
                    lambda x: preprocess_text(str(x)) if pd.notna(x) and len(str(x).strip()) > 3 else None)
    except Exception:
        pass

    import hashlib
    def hash_id(val):
        if pd.isna(val): return None
        try:
            return hashlib.sha256(str(int(val)).encode()).hexdigest()
        except:
            return hashlib.sha256(str(val).encode()).hexdigest()

    # Anonymize ID
    id_col = None
    for c in df_clean.columns:
        if str(c).strip().lower() in ['id nhân viên', 'employee id', 'id_nv', 'id']:
            id_col = c
            break
    if id_col is None:
        id_col = df_clean.columns[1]

    df_clean['_nv_hash'] = df_clean[id_col].apply(hash_id)
    df_clean = df_clean.drop(columns=[id_col])

    # Store metadata
    df_clean.attrs['group_id']      = group_id
    df_clean.attrs['likert_cols']   = likert_cols
    df_clean.attrs['open_cols']     = open_cols
    df_clean.attrs['codebook']      = codebook
    df_clean.attrs['n_before']      = n_before
    df_clean.attrs['n_removed']     = _n_removed
    df_clean.attrs['pct_removed']   = _pct_removed
    df_clean.attrs['filter_method'] = _filter_method
    df_clean.attrs['filter_desc']   = _filter_desc
    df_clean.attrs['memo_report']   = _memo_report
    df_clean.attrs['calibration_report'] = _calibration_report
    df_clean.attrs['sanity_checks'] = run_sanity_checks(df_clean, group_id)

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
                log_callback(f"Đã tải dữ liệu khảo sát nhóm {gid} ({rows:,} mẫu hợp lệ).", "ok")
        except Exception as e:
            st.warning(f"Không load được nhóm {gid}: {e}")
            if log_callback:
                log_callback(f"Không tải được nhóm {gid}: {e}")
    if log_callback:
        log_callback("Đang tổng hợp dữ liệu toàn công ty...")
    return results


def compute_kpis(df):
    """Compute KPI dict from any group's dataframe using CompanyRollup_Weight."""
    n_rows = len(df)
    if n_rows == 0:
        return {'n': 0, 'ei_mean': 0, 'enps_score': 0, 'promoters': 0,
                'passives': 0, 'detractors': 0, 'mei_avg': 0,
                'intent_pct_low': 0, 'burnout_pct': 0,
                'stay_score_avg': 0, 'stay_flight_pct': 0,
                'stay_atrisk_pct': 0, 'stay_stable_pct': 0,
                'silence_rate': 0, 'jsi_avg': 0, 'ews_red_pct': 0,
                'quadrant': {}, 'contradiction_pct': 0}

    w = df.get('CompanyRollup_Weight', pd.Series(1.0, index=df.index))
    n = int(w.sum()) # effective n
    
    def weighted_avg(col):
        mask = col.notna()
        if not mask.any(): return 0
        return np.average(col[mask], weights=w[mask])
        
    def weighted_pct(condition_mask, valid_mask=None):
        if valid_mask is None: valid_mask = pd.Series(True, index=df.index)
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

    silence_rate = round(weighted_pct(df['is_silent']), 1) if 'is_silent' in df.columns else 0
    jsi_avg = round(weighted_avg(df['JSI']), 1) if 'JSI' in df.columns else 0

    ews_col = df.get('EWS')
    ews_red_pct = 0
    if ews_col is not None and ews_col.notna().any():
        ews_red_pct = round(weighted_pct(ews_col >= 60, ews_col.notna()), 1)

    quad = df.get('engagement_quadrant')
    quad_counts = {}
    if quad is not None and quad.notna().any():
        for label in ['Champions', 'Trapped Loyalists', 'Confused Leavers', 'Flight Risk']:
            quad_counts[label] = round(weighted_pct(quad == label, quad.notna()), 1)

    contradiction_pct = round(weighted_pct(df.get('contradiction_flag', pd.Series(False, index=df.index))), 1)

    return {
        'n': n, 'ei_mean': round(ei_mean, 1),
        'enps_score': round(enps_score, 0),
        'promoters': int(promoters), 'passives': int(passives), 'detractors': int(detractors),
        'mei_avg': round(mei_avg, 1),
        'intent_pct_low': round(intent_pct, 1),
        'intent_pct_high': round(intent_pct_high, 1),
        'burnout_pct': round(burnout_pct, 1),
        'stay_score_avg': stay_score_avg,
        'stay_flight_pct': stay_flight_pct,
        'stay_atrisk_pct': stay_atrisk_pct,
        'stay_stable_pct': stay_stable_pct,
        'silence_rate': silence_rate,
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
    
    try:
        # Tối ưu hóa: Ưu tiên đọc từ file Parquet cục bộ nếu có (tốc độ ánh sáng)
        if os.path.exists(local_cache) and (time.time() - os.path.getmtime(local_cache) < 86400 * 7):
            df_hris = pd.read_parquet(local_cache)
        else:
            try:
                hris_sheet_id = st.secrets.get("HRIS_SHEET_ID", "19ey-QCV4cxzokmBAaMgbY7kHcZNa1fSiW4boTosaBwo")
            except Exception:
                hris_sheet_id = "19ey-QCV4cxzokmBAaMgbY7kHcZNa1fSiW4boTosaBwo"
            
            hris_url = f"https://docs.google.com/spreadsheets/d/{hris_sheet_id}/export?format=csv"
            df_hris = pd.read_csv(hris_url)
            df_hris.columns = df_hris.columns.str.strip()
            
            # Lưu cache ra file parquet để dùng cho các lần sau
            os.makedirs("data", exist_ok=True)
            try:
                df_hris.to_parquet(local_cache, index=False)
            except Exception:
                pass  # Bỏ qua nếu môi trường không hỗ trợ pyarrow/fastparquet
                
    except Exception as e:
        import streamlit as st
        st.error(f"Lỗi tải HRIS: {e}")
        return None, None
    month_col = df_hris.columns[1]

    def _parse_month(m):
        try:
            parts = str(m).split('/')
            return int(parts[1].lstrip('0')) * 100 + int(parts[0])
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
