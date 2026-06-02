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
    get_codebook, PILLAR_WEIGHTS, get_role_question, get_pillar_questions, 
    classify_ei, calc_engagement_pct, get_item,
    TENURE_MAP, TENURE_LABELS, EWS_TENURE_THRESHOLD, SENIOR_TENURE_THRESHOLD,
    ENPS_BINS, ENPS_LABELS, ENPS_PROMOTER_MIN, ENPS_DETRACTOR_MAX,
    MIN_UNIT_N, ANOMALY_STD_MULTIPLIER, DEFAULT_WEIGHTS, CALIBRATED_WEIGHTS,
    DEMO_MAP
)
from scipy import stats as scipy_stats
from sklearn.linear_model import LogisticRegression, RidgeClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.inspection import permutation_importance
from sklearn.model_selection import cross_val_score
import warnings

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


import pandas as pd
import numpy as np
import re

# ---- 2.1 Tenure normalization ----

def normalize_tenure(df: pd.DataFrame) -> pd.DataFrame:
    """
    Chuẩn hóa cột tenure từ D5 (raw) → tenure (ordinal int) + tenure_label (string).
    Xử lý được: string tiếng Việt, số 1–9, mixed cases.
    """
    if 'tenure_raw' not in df.columns:
        return df

    def _parse_tenure(val):
        if pd.isna(val):
            return -1
        val_str = str(val).strip()
        # Thử map trực tiếp trước
        if val_str in TENURE_MAP:
            return TENURE_MAP[val_str]
        # Thử convert số
        try:
            return TENURE_MAP.get(int(float(val_str)), -1)
        except (ValueError, TypeError):
            pass
        # Fuzzy match: tìm số tháng/năm trong string
        if 'dưới 1' in val_str.lower() or '< 1' in val_str.lower():
            return 0
        return -1

    df['tenure'] = df['tenure_raw'].apply(_parse_tenure)
    df['tenure_label'] = df['tenure'].map(
        {i: label for i, label in enumerate(TENURE_LABELS)}
    ).fillna('Unknown')
    return df


# ---- 2.2 Generation normalization ----

GEN_MAP = {
    'Trước 1980 (Gen X)':  'Gen X',
    'Gen X':               'Gen X',
    1:                     'Gen X',
    '1981 – 1989 (Gen Y)': 'Gen Y (older)',
    '1990 – 1996 (Gen Y)': 'Gen Y (younger)',
    'Gen Y':               'Gen Y (older)',
    2:                     'Gen Y (older)',
    3:                     'Gen Y (younger)',
    '1997 – 2000 (Gen Z)': 'Gen Z',
    'Từ 2001 trở đi (Gen Z)': 'Gen Z',
    'Gen Z':               'Gen Z',
    4:                     'Gen Z',
    5:                     'Gen Z',
}

def normalize_gen(df: pd.DataFrame) -> pd.DataFrame:
    if 'gen_raw' in df.columns:
        df['gen'] = df['gen_raw'].map(GEN_MAP).fillna('Unknown')
        # Simplified 3-gen version for cross-tab analysis
        df['gen3'] = df['gen'].map(
            lambda x: 'Gen X' if x == 'Gen X'
                      else 'Gen Z' if x == 'Gen Z'
                      else 'Gen Y' if 'Gen Y' in str(x) else 'Unknown'
        )
    return df


# ---- 2.3 Column rename (Demographic) ----

def rename_demographics(df: pd.DataFrame, group_id: str) -> pd.DataFrame:
    """Đổi tên cột D1–D9 sang tên ngữ nghĩa theo DEMO_MAP."""
    rename_dict = DEMO_MAP.get(group_id, {})
    return df.rename(columns=rename_dict)


# ---- 2.4 Prev company NLP taxonomy ----
# FIX #11: Framework xử lý D6 (prev_company) thay vì bỏ qua

PREV_COMPANY_TAXONOMY = {
    'logistics_competitor': ['ninja', 'j&t', 'jt', 'viettel post', 'best', 'ghn', 'snappy', 'grab'],
    'logistics_adjacent':   ['lazada', 'shopee', 'tiki', 'sendo', 'vnpost', 'bưu điện'],
    'manufacturing':        ['samsung', 'intel', 'khu công nghiệp', 'nhà máy', 'xưởng'],
    'retail_food':          ['vinmart', 'bách hóa', 'circle k', 'highland', 'phúc long'],
    'first_job':            ['chưa làm', 'lần đầu', 'sinh viên', 'mới ra trường'],
    'other':                [],  # default bucket
}

def classify_prev_company(val: str) -> str:
    """Phân loại câu trả lời D6 thành taxonomy bucket."""
    if pd.isna(val) or str(val).strip() == '':
        return 'not_answered'
    val_lower = str(val).lower()
    for category, keywords in PREV_COMPANY_TAXONOMY.items():
        if any(kw in val_lower for kw in keywords):
            return category
    # Heuristic: nếu quá ngắn (<5 ký tự) → unclear
    if len(val_lower.strip()) < 5:
        return 'unclear'
    return 'other'

def process_prev_company(df: pd.DataFrame) -> pd.DataFrame:
    if 'prev_company' in df.columns:
        df['prev_company_cat'] = df['prev_company'].apply(classify_prev_company)
    return df


# ---- 2.5 Master normalization runner ----

def normalize_raw_data(df: pd.DataFrame, group_id: str) -> pd.DataFrame:
    """
    Entry point duy nhất. Chạy ngay sau khi load CSV/Excel từ survey platform.
    Thứ tự: rename → tenure → gen → prev_company
    """
    df = rename_demographics(df, group_id)
    df = normalize_tenure(df)
    df = normalize_gen(df)
    df = process_prev_company(df)
    return df

from scipy import stats as scipy_stats
from sklearn.linear_model import LogisticRegression, RidgeClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.inspection import permutation_importance
from sklearn.model_selection import cross_val_score
import warnings


# ---- 3.1 Pillar Score ----

def compute_pillar_score(df: pd.DataFrame, group_id: str, pillar: str) -> pd.Series:
    """
    Tính điểm trụ cột = trung bình các items, convert sang % (0–100).
    Missing: cần ≥ 50% items có dữ liệu; nếu không → NaN.
    NOTE: Giả định MCAR (Missing Completely At Random) — analyst cần verify.
    """
    qs = get_pillar_questions(group_id, pillar)
    valid_qs = [q for q in qs if q in df.columns]
    if not valid_qs:
        return pd.Series(np.nan, index=df.index)

    raw = df[valid_qs]
    min_valid = max(1, int(len(valid_qs) * 0.5))
    enough_data = raw.notna().sum(axis=1) >= min_valid
    score = raw.mean(axis=1)
    score[~enough_data] = np.nan
    return ((score - 1) / 4 * 100).round(2)


# ---- 3.2 Burnout Proxy ----
# FIX #2: Công thức chuẩn — không clip, không mất thông tin điểm 4–5

def compute_burnout(df: pd.DataFrame, group_id: str) -> pd.DataFrame:
    """
    Burnout Proxy = trung bình reverse của workload + pressure items.
    Thang 0–100 (cao = burnout risk cao).
    Cả hai items cần có dữ liệu; nếu chỉ có 1 → dùng item đó.
    """
    wl_col = get_item(group_id, 'workload')
    pr_col = get_item(group_id, 'pressure')

    has_wl = wl_col and wl_col in df.columns
    has_pr = pr_col and pr_col in df.columns

    if has_wl and has_pr and wl_col != pr_col:
        # FIX: (5 - x) / 4 * 100 → 1→100%, 5→0% — không clip, không mất info
        burnout_wl = (5 - df[wl_col]) / 4 * 100
        burnout_pr = (5 - df[pr_col]) / 4 * 100
        df['burnout_score'] = ((burnout_wl + burnout_pr) / 2).round(1)
        df['burnout_proxy'] = (df['burnout_score'] >= 50).astype(int)
    elif has_wl:
        df['burnout_score'] = ((5 - df[wl_col]) / 4 * 100).round(1)
        df['burnout_proxy'] = (df['burnout_score'] >= 50).astype(int)
    else:
        df['burnout_score'] = np.nan
        df['burnout_proxy'] = np.nan

    # NOTE 3B: pressure = workload (cùng câu C18), burnout_score sẽ chỉ dùng 1 item
    if group_id == '3B':
        df['burnout_note'] = 'Single-item burnout proxy (3B pressure=workload=C18)'

    return df


# ---- 3.3 Cronbach Alpha ----
# FIX #3: Luôn trả về dict — không có type inconsistency

def cronbach_alpha(df: pd.DataFrame, cols: list) -> dict:
    """
    Tính độ tin cậy cho một pillar.
    LUÔN trả về dict với keys: type, value, n_items, interpretation, warning.
    """
    valid_cols = [c for c in cols if c in df.columns]
    data = df[valid_cols].dropna()

    base = {'n_items': len(valid_cols), 'n_respondents': len(data)}

    if len(valid_cols) < 2:
        return {**base, 'type': 'insufficient', 'value': None,
                'interpretation': 'Cần ≥ 2 items', 'warning': 'Không tính được'}

    if len(valid_cols) == 2:
        # 2 items: Pearson r (không phải alpha)
        if len(data) < 5:
            return {**base, 'type': 'pearson_r', 'value': None,
                    'warning': 'Cỡ mẫu quá nhỏ (n<5)'}
        r, p = scipy_stats.pearsonr(data[valid_cols[0]], data[valid_cols[1]])
        return {
            **base, 'type': 'pearson_r', 'value': round(float(r), 3),
            'p_value': round(float(p), 4),
            'interpretation': (
                'Tương quan mạnh (r≥0.6)' if r >= 0.6 else
                'Tương quan trung bình (0.3≤r<0.6)' if r >= 0.3 else
                'Tương quan yếu (r<0.3)'
            ),
            'warning': '2-item scale: dùng Pearson r, không phải Cronbach alpha. Interpret with caution.'
        }

    # ≥ 3 items: Cronbach alpha
    n_items  = len(valid_cols)
    item_var = data.var(axis=0, ddof=1).sum()
    total_var = data.sum(axis=1).var(ddof=1)
    if total_var == 0:
        return {**base, 'type': 'cronbach_alpha', 'value': None,
                'warning': 'Zero variance — all respondents answered the same'}
    alpha = (n_items / (n_items - 1)) * (1 - item_var / total_var)
    alpha = float(np.clip(alpha, -1, 1))  # bound theo lý thuyết

    return {
        **base, 'type': 'cronbach_alpha', 'value': round(alpha, 3),
        'interpretation': (
            'Tốt (α≥0.70)' if alpha >= 0.70 else
            'Chấp nhận được (0.60≤α<0.70)' if alpha >= 0.60 else
            'Thấp (α<0.60) — interpret trụ cột này thận trọng'
        ),
        'warning': (
            None if alpha >= 0.60
            else f'⚠️ Cronbach α = {round(alpha,3)} < 0.60 — items trong trụ cột này đo nhiều construct khác nhau'
        )
    }


def validate_pillar_reliability(df: pd.DataFrame, group_id: str) -> dict:
    """Chạy reliability check cho tất cả pillars của một group."""
    report = {}
    for pillar in ['TC1', 'TC2', 'TC3', 'TC4', 'TC5']:
        qs = get_pillar_questions(group_id, pillar)
        report[pillar] = cronbach_alpha(df, qs)
    return report


# ---- 3.4 All Indices ----

def compute_all_indices(df: pd.DataFrame, group_id: str,
                        weights: dict = None) -> pd.DataFrame:
    """
    Tính toàn bộ derived indices. Chạy trên FULL dataset (không filter theo unit).
    Trả về df với các cột mới.
    """
    if weights is None:
        weights = CALIBRATED_WEIGHTS.get(group_id, DEFAULT_WEIGHTS)

    pillars = ['TC1', 'TC2', 'TC3', 'TC4', 'TC5']

    # 1. Pillar Scores
    for p in pillars:
        df[f'{p}_score'] = compute_pillar_score(df, group_id, p)
        df[f'{p}_pct'] = df[f'{p}_score']

    # 2. Engagement Index
    available = [p for p in pillars if f'{p}_score' in df.columns]
    w_sum = sum(weights[p] for p in available)
    df['EI'] = sum(df[f'{p}_score'] * (weights[p] / w_sum) for p in available).round(2)

    # 3. Manager Effectiveness Index (proxy)
    df['MEI'] = df['TC2_score']
    # Nota: MEI = TC2_score là proxy. Lý tưởng cần 360 feedback riêng.

    # 4. Burnout
    df = compute_burnout(df, group_id)

    # 5. Attrition / eNPS
    if 'C22' in df.columns:
        df['attrition_score'] = df['C22']
        df['attrition_risk']  = (6 - df['C22'])   # reverse: 5=high risk
        df['is_flight_risk']  = (df['C22'] <= 2).astype(int)

    if 'C23' in df.columns:
        df['eNPS_raw'] = df['C23']
        df['eNPS_cat'] = pd.cut(df['C23'], bins=ENPS_BINS, labels=ENPS_LABELS)

    # 6. Career Growth Index
    career_col = get_item(group_id, 'career')
    if career_col and career_col in df.columns:
        df['career_index'] = ((df[career_col] - 1) / 4 * 100).round(1)

    # 7. Psychological Safety Score
    ps_col = get_item(group_id, 'psych_safety')
    if ps_col and ps_col in df.columns:
        df['psych_safety_score'] = ((df[ps_col] - 1) / 4 * 100).round(1)

    # 8. Respect Index
    resp_col = get_item(group_id, 'respect')
    if resp_col and resp_col in df.columns:
        df['respect_index'] = ((df[resp_col] - 1) / 4 * 100).round(1)

    # 9. JSI Proxy
    # FIX #10: workload item per group được lấy qua get_item() — đúng cho 3B (C18/TC5)
    tc4_s = df.get('TC4_score', pd.Series(np.nan, index=df.index))
    wl_col = get_item(group_id, 'workload')
    wl_s   = ((df[wl_col] - 1) / 4 * 100) if wl_col and wl_col in df.columns else pd.Series(np.nan, index=df.index)
    bl_col = get_item(group_id, 'belonging') or get_item(group_id, 'pride') or get_item(group_id, 'respect')
    bl_s   = ((df[bl_col] - 1) / 4 * 100) if bl_col and bl_col in df.columns else pd.Series(np.nan, index=df.index)
    df['JSI'] = (0.4 * tc4_s + 0.3 * wl_s + 0.3 * bl_s).round(2)
    if group_id == '3B':
        df['JSI_note'] = 'JSI workload component = C18 (TC5) cho 3B — cross-pillar'

    return df


# ---- 3.5 Aggregate to unit level ----

def aggregate_unit(df: pd.DataFrame, group_col: str = 'unit') -> pd.DataFrame:
    """Tổng hợp individual → unit-level. Loại đơn vị n < MIN_UNIT_N."""
    score_cols = [c for c in df.columns if c.endswith('_score') or c in ['EI', 'MEI', 'JSI', 'eNPS_raw']]
    binary_cols = ['is_flight_risk', 'burnout_proxy']

    agg = df.groupby(group_col)[score_cols].agg(['mean', 'std']).round(2)
    agg.columns = ['_'.join(c) for c in agg.columns]

    # Sample size (tránh dùng tên cột giả định)
    agg['n'] = df.groupby(group_col)[score_cols[0]].count()

    for col in binary_cols:
        if col in df.columns:
            agg[f'{col}_pct'] = (df.groupby(group_col)[col].mean() * 100).round(1)

    if 'eNPS_cat' in df.columns:
        enps = df.groupby(group_col)['eNPS_cat'].value_counts(normalize=True).unstack(fill_value=0)
        agg['eNPS_score'] = ((enps.get('Promoter', 0) - enps.get('Detractor', 0)) * 100).round(1)

    # Ẩn đơn vị có n < MIN_UNIT_N
    small = agg['n'] < MIN_UNIT_N
    if small.any():
        print(f"⚠️ {small.sum()} đơn vị bị ẩn do n < {MIN_UNIT_N}: {agg[small].index.tolist()}")
    return agg[~small]


# ---- 3.6 Weight Calibration ----
# FIX #1: Ridge Regression + VIF check thay vì Logistic Regression thuần

def check_multicollinearity(X: np.ndarray, feature_names: list) -> dict:
    """
    Tính VIF (Variance Inflation Factor) cho từng feature.
    VIF > 5 = multicollinearity đáng lo ngại.
    VIF > 10 = multicollinearity nghiêm trọng.
    """
    from numpy.linalg import inv
    try:
        corr = np.corrcoef(X.T)
        vif_values = np.diag(inv(corr))
        return {name: round(float(v), 2) for name, v in zip(feature_names, vif_values)}
    except np.linalg.LinAlgError:
        return {name: float('inf') for name in feature_names}


def calibrate_weights(df: pd.DataFrame, group_id: str,
                      min_n: int = 50, min_flight_rate: float = 0.05) -> dict:
    """
    Calibrate pillar weights empirically dựa trên Permutation Importance.
    FIX #1: Dùng Ridge Logistic + Permutation Importance thay vì raw coefficients
    vì raw Logistic coefficients bị distorted bởi multicollinearity.

    Workflow:
    1. Check multicollinearity (VIF)
    2. Nếu VIF cao → dùng Ridge (L2 penalty giảm variance)
    3. Dùng Permutation Importance (không bị bias bởi scale hay collinearity)
    4. Normalize permutation importance thành weights
    """
    features = ['TC1_score', 'TC2_score', 'TC3_score', 'TC4_score', 'TC5_score']
    target   = 'is_flight_risk'
    data = df[[*features, target]].dropna()

    print(f"\n=== Calibrating weights cho nhóm {group_id} ===")
    print(f"Sample size: n={len(data)}, flight_risk={data[target].mean():.1%}")

    if len(data) < min_n:
        print(f"⚠️ n={len(data)} < {min_n} — cỡ mẫu nhỏ, dùng default weights")
        return DEFAULT_WEIGHTS

    if data[target].mean() < min_flight_rate:
        print(f"⚠️ Flight risk rate {data[target].mean():.1%} < {min_flight_rate:.0%} — quá ít cases, dùng default weights")
        return DEFAULT_WEIGHTS

    X = data[features].values
    y = data[target].values
    feature_short = ['TC1', 'TC2', 'TC3', 'TC4', 'TC5']

    # Step 1: VIF check
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    vif = check_multicollinearity(X_scaled, feature_short)
    high_vif = {k: v for k, v in vif.items() if v > 5}
    print(f"VIF: {vif}")
    if high_vif:
        print(f"⚠️ Multicollinearity detected (VIF>5): {high_vif} → dùng Ridge")

    # Step 2: Fit Ridge Logistic Regression
    # alpha=1.0 là regularization strength — có thể tune nếu cần
    from sklearn.linear_model import LogisticRegression
    model = LogisticRegression(penalty='l2', C=1.0, solver='lbfgs',
                                max_iter=1000, random_state=42)
    model.fit(X_scaled, y)

    # Step 3: Cross-validated permutation importance (không bị bias bởi collinearity)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        perm = permutation_importance(model, X_scaled, y, n_repeats=20,
                                       random_state=42, scoring='roc_auc')

    importances = perm.importances_mean
    importances = np.maximum(importances, 0)  # clip âm về 0

    if importances.sum() == 0:
        print("⚠️ Permutation importance = 0 cho tất cả features — dùng default weights")
        return DEFAULT_WEIGHTS

    weights = dict(zip(feature_short, (importances / importances.sum()).round(4)))
    print(f"✅ Calibrated weights: {weights}")

    # Cross-validation score để báo cáo độ tin cậy
    cv_auc = cross_val_score(model, X_scaled, y, cv=5, scoring='roc_auc').mean()
    print(f"Model CV AUC: {cv_auc:.3f} {'✅ Đủ tin cậy' if cv_auc > 0.65 else '⚠️ Thấp — weights nên treat as directional only'}")

    CALIBRATED_WEIGHTS[group_id] = weights
    return weights


# ---- 3.7 Relative Thresholds ----

def compute_relative_thresholds(df: pd.DataFrame, group_id: str) -> dict:
    """
    Tính ngưỡng anomaly từ distribution thực của GHN.
    Chạy 1 lần trên FULL dataset sau khi đã compute_all_indices().
    """
    metrics = ['TC1_score', 'TC2_score', 'TC3_score', 'TC4_score', 'TC5_score',
               'EI', 'MEI', 'burnout_score', 'career_index', 'JSI',
               'respect_index', 'psych_safety_score']
    binary  = ['is_flight_risk']

    thresholds = {}
    for m in metrics:
        if m not in df.columns:
            continue
        s = df[m].dropna()
        if len(s) < 10:
            continue
        thresholds[m] = {
            'mean': round(s.mean(), 2), 'std': round(s.std(), 2),
            'p10':  round(s.quantile(0.10), 2), 'p25': round(s.quantile(0.25), 2),
            'p50':  round(s.quantile(0.50), 2), 'p75': round(s.quantile(0.75), 2),
            'p90':  round(s.quantile(0.90), 2),
        }

    for b in binary:
        if b in df.columns:
            s = df[b].dropna()
            thresholds[f'{b}_pct'] = {
                'mean': round(s.mean() * 100, 2),
                'p25':  round(s.quantile(0.25) * 100, 2),
                'p75':  round(s.quantile(0.75) * 100, 2),
                'p90':  round(s.quantile(0.90) * 100, 2),
            }

    return thresholds

def run_data_quality_pipeline(df: pd.DataFrame, group_id: str) -> tuple:
    """
    Step 0 — bắt buộc trước mọi phân tích.
    Returns: (df_clean, quality_report)
    """
    content_cols = [f'C{i}' for i in range(1, 22) if f'C{i}' in df.columns]
    report = {
        'original_n': len(df), 'group_id': group_id,
        'flags': {}, 'warnings': [], 'excluded_ids': []
    }
    excl = pd.Series(False, index=df.index)

    # Flag 1: Straight-liners (≥80% cùng điểm trong content questions)
    def _is_straightliner(row):
        vals = row[content_cols].dropna()
        return len(vals) >= 10 and vals.value_counts(normalize=True).max() >= 0.80

    sl = df.apply(_is_straightliner, axis=1)
    report['flags']['straight_liners'] = int(sl.sum())
    if sl.any():
        report['warnings'].append(f"⚠️ {sl.sum()} straight-liner responses (≥80% cùng điểm)")
    excl |= sl

    # Flag 2: Speeders
    if 'completion_time_sec' in df.columns:
        sp = df['completion_time_sec'] < 180
        report['flags']['speeders'] = int(sp.sum())
        if sp.any():
            report['warnings'].append(f"⚠️ {sp.sum()} responses < 3 phút")
        excl |= sp

    # Flag 3: Logical inconsistency (pride cao nhưng muốn nghỉ — flag, không loại)
    pride_col = get_item(group_id, 'pride')
    if pride_col and pride_col in df.columns and 'C22' in df.columns:
        incon = (df[pride_col] >= 4) & (df['C22'] == 1)
        report['flags']['logical_inconsistency'] = int(incon.sum())
        if incon.any():
            report['warnings'].append(
                f"ℹ️ {incon.sum()} responses: Pride≥4 nhưng C22=1 — review thủ công"
            )

    # Flag 4: Excessive missing (>30% content questions)
    miss_rate = df[content_cols].isna().mean(axis=1)
    emiss = miss_rate > 0.30
    report['flags']['excessive_missing'] = int(emiss.sum())
    if emiss.any():
        report['warnings'].append(f"⚠️ {emiss.sum()} responses thiếu >30% câu hỏi")
    excl |= emiss

    # Flag 5: Anonymity check per unit
    if 'unit' in df.columns:
        small = df['unit'].value_counts()
        small = small[small < MIN_UNIT_N].index.tolist()
        if small:
            report['warnings'].append(
                f"🔒 {len(small)} đơn vị n < {MIN_UNIT_N} — kết quả sẽ bị ẩn: {small[:5]}"
            )

    # Silence pattern (3 câu mở riêng biệt — FIX v2)
    open_cols = [c for c in ['C24', 'C25', 'C26'] if c in df.columns]
    if open_cols:
        is_blank = {c: (df[c].isna() | (df[c].astype(str).str.strip() == '')) for c in open_cols}
        report['silence_rate'] = {
            c: round(is_blank[c].mean() * 100, 1) for c in open_cols
        }
        if len(open_cols) == 3:
            all_skip    = is_blank['C24'] & is_blank['C25'] & is_blank['C26']
            only_c26    = is_blank['C24'] & is_blank['C25'] & ~is_blank['C26']
            report['silence_rate']['all_3_skip']       = round(all_skip.mean() * 100, 1)
            report['silence_rate']['frustration_only']  = round(only_c26.mean() * 100, 1)
            if report['silence_rate']['all_3_skip'] > 50:
                report['warnings'].append(
                    f"🔴 {report['silence_rate']['all_3_skip']}% không điền bất kỳ câu mở nào — "
                    f"dấu hiệu thiếu tin tưởng vào ẩn danh"
                )
            if report['silence_rate'].get('frustration_only', 0) > 15:
                report['warnings'].append(
                    f"⚡ {report['silence_rate']['frustration_only']}% chỉ điền C26 (vấn đề) — "
                    f"frustration cao, không thấy điểm tích cực"
                )

    # Summary
    report['excluded_n'] = int(excl.sum())
    report['clean_n']    = int((~excl).sum())
    report['excl_rate']  = round(report['excluded_n'] / report['original_n'] * 100, 1)
    if report['excl_rate'] > 15:
        report['warnings'].append(
            f"🔴 Tỷ lệ loại cao ({report['excl_rate']}%) — kiểm tra quy trình thu thập dữ liệu"
        )

    df_clean = df[~excl].copy()
    return df_clean, report

def analyze_tenure_cohorts(df, group_id):
    """Phân tích EI theo cohort thâm niên → phát hiện Tenure Cliff và EWS."""
    if 'tenure' not in df.columns or 'EI' not in df.columns:
        return {}
    metrics = [c for c in ['EI','TC4_score','TC2_score','burnout_score','is_flight_risk'] if c in df.columns]
    cohort = df.groupby('tenure')[metrics].agg(['mean','count']).round(2)
    cohort.index = [TENURE_LABELS[i] if i < len(TENURE_LABELS) else i for i in cohort.index]
    company_ei = df['EI'].mean()
    ews_thresh = EWS_TENURE_THRESHOLD.get(group_id, 2)
    early_mask = df['tenure'] <= ews_thresh
    early_ei   = df.loc[early_mask, 'EI'].mean() if early_mask.any() else np.nan
    result = {'cohort_data': cohort.to_dict(), 'ews': [], 'cliffs': []}
    if not np.isnan(early_ei) and early_ei < company_ei - 10:
        result['ews'].append({'ei_gap': round(company_ei - early_ei, 1),
                              'action': 'Review onboarding — EI drop 0–6 tháng = early turnover signal'})
    return result


@st.cache_data(ttl=3600, show_spinner=" Đang tải dữ liệu...")
def load_group(group_id: str):
    """Load & clean a single survey group using v3 playbook pipeline. Returns (df_clean, n_before)."""
    from config.groups import GROUP_REGISTRY
    import streamlit as st
    import pandas as pd
    cfg = GROUP_REGISTRY[group_id]
    codebook = cfg['codebook']
    try:
        conn = st.connection("supabase", type="sql")
        table_name = f"survey_{group_id.lower()}"
        df_raw = conn.query(f"SELECT * FROM {table_name}", ttl=3600)
    except Exception as e:
        df_raw = pd.read_csv(cfg['url'])
    n_before = len(df_raw)

    col_rename = {}
    for q_id, q_info in codebook.items():
        idx = q_info['col_idx']
        if idx < len(df_raw.columns):
            col_rename[df_raw.columns[idx]] = q_id
    df = df_raw.rename(columns=col_rename).copy()
    
    # Hash ID nhân viên để join với HRIS (bảo mật)
    from shared.security import hash_id
    if 'ID nhân viên' in df.columns:
        df['_nv_hash'] = df['ID nhân viên'].apply(hash_id)
    elif 'ID' in df.columns:
        df['_nv_hash'] = df['ID'].apply(hash_id)

    q_to_v3 = {}
    for i in range(1, 10): q_to_v3[f'Q{i}'] = f'D{i}'
    for i in range(1, 22): q_to_v3[f'Q{i+8}'] = f'C{i}'
    q_to_v3['Q30'] = 'C22'
    q_to_v3['Q31'] = 'C23'
    q_to_v3['Q32'] = 'C24'
    q_to_v3['Q33'] = 'C25'
    q_to_v3['Q34'] = 'C26'
    
    if 'Q5' in df.columns:
        df['Q5_legacy'] = df['Q5']

    df = df.rename(columns=q_to_v3)

    if 'Q5_legacy' in df.columns:
        df['Q5'] = df['Q5_legacy']

    df = normalize_raw_data(df, group_id)
    
    from shared.codebook import decode_intent, decode_enps, decode_likert
    if 'C22' in df.columns: df['C22'] = df['C22'].apply(decode_intent)
    if 'C23' in df.columns: df['C23'] = df['C23'].apply(decode_enps)
        
    for i in range(1, 22):
        c = f'C{i}'
        if c in df.columns:
            df[c] = df[c].apply(decode_likert)

    df = compute_all_indices(df, group_id)
    
    # Backward compatibility for legacy UI variables
    if 'C23' in df.columns:
        df['eNPS'] = df['C23']
    if 'C22' in df.columns:
        df['intent'] = df['C22']
    if 'C14' in df.columns:
        df['stay_intention'] = df['C14']
    
    df.attrs['group_id'] = group_id
    df.attrs['open_cols'] = ['C24', 'C25', 'C26']
    df.attrs['codebook'] = codebook
    
    vung_col = None
    for c in df.columns:
        if 'vùng' in str(c).lower(): vung_col = c; break
    if vung_col is None and 'D10' in df.columns: vung_col = 'D10'
    
    try:
        from shared.workforce_mapper import map_survey_to_org
        df = map_survey_to_org(df, group=group_id, vung_col=vung_col, id_col=df.columns[1], raw_df=df_raw)
    except:
        pass
        
    return df, n_before

@st.cache_data(ttl=3600, show_spinner="Đang tải toàn bộ dữ liệu...")
def load_all_available():
    """Load all groups that have data. Returns dict {group_id: (df, n_before)}."""
    from config.groups import get_available_groups
    results = {}
    for gid in get_available_groups():
        try:
            results[gid] = load_group(gid)
        except Exception as e:
            st.warning(f"Không load được nhóm {gid}: {e}")
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
    if isinstance(w, pd.DataFrame): w = w.iloc[:, 0]
    n = int(w.sum()) # effective n
    
    def weighted_avg(col):
        if isinstance(col, pd.DataFrame): col = col.iloc[:, 0]
        mask = col.notna().to_numpy(dtype=bool)
        if not mask.any(): return 0
        return np.average(col.to_numpy()[mask], weights=w.to_numpy()[mask])
        
    def weighted_pct(condition_mask, valid_mask=None):
        if isinstance(condition_mask, pd.DataFrame): condition_mask = condition_mask.iloc[:, 0]
        cond_arr = condition_mask.to_numpy(dtype=bool, na_value=False)
        
        if valid_mask is None: 
            valid_mask_arr = np.ones(len(df), dtype=bool)
        else:
            if isinstance(valid_mask, pd.DataFrame): valid_mask = valid_mask.iloc[:, 0]
            valid_mask_arr = valid_mask.to_numpy(dtype=bool, na_value=False)
            
        w_arr = w.to_numpy()
        
        if not valid_mask_arr.any() or w_arr[valid_mask_arr].sum() == 0: return 0
        return (w_arr[cond_arr & valid_mask_arr].sum() / w_arr[valid_mask_arr].sum()) * 100

    ei_mean = weighted_avg(df['EI']) if 'EI' in df.columns else 0
    enps_col = df.get('eNPS', pd.Series(np.nan, index=df.index))
    if isinstance(enps_col, pd.DataFrame): enps_col = enps_col.iloc[:, 0]
    n_valid_enps = enps_col.notna()
    
    w_series = pd.Series(w.to_numpy(), index=df.index)
    
    promoters = w_series[enps_col >= 9].sum()
    passives = w_series[(enps_col >= 7) & (enps_col <= 8)].sum()
    detractors = w_series[enps_col <= 6].sum()
    
    enps_score = weighted_pct(enps_col >= 9, n_valid_enps) - weighted_pct(enps_col <= 6, n_valid_enps)
    
    mei_avg = weighted_avg(df['MEI']) if 'MEI' in df.columns else 0
    intent_col = df.get('intent', pd.Series(np.nan, index=df.index))
    if isinstance(intent_col, pd.DataFrame): intent_col = intent_col.iloc[:, 0]
    intent_valid = intent_col.notna()
    intent_pct = weighted_pct(intent_col <= 2, intent_valid)
    intent_pct_high = weighted_pct(intent_col >= 4, intent_valid)
    
    burnout_pct = weighted_pct(df.get('burnout_proxy', pd.Series(0, index=df.index)) > 0)

    q22_col = df.get('stay_intention', pd.Series(np.nan, index=df.index))
    if isinstance(q22_col, pd.DataFrame): q22_col = q22_col.iloc[:, 0]
    q22_valid = q22_col.notna()
    stay_score_avg = round(weighted_avg(q22_col), 2)
    stay_flight_pct = round(weighted_pct(q22_col <= 2, q22_valid), 1)
    stay_atrisk_pct = round(weighted_pct(q22_col == 3, q22_valid), 1)
    stay_stable_pct = round(weighted_pct(q22_col >= 4, q22_valid), 1)

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
        'n': int(n), 
        'ei_mean': float(round(ei_mean, 1)),
        'enps_score': float(round(enps_score, 0)),
        'promoters': int(promoters), 'passives': int(passives), 'detractors': int(detractors),
        'mei_avg': float(round(mei_avg, 1)),
        'intent_pct_low': float(round(intent_pct, 1)),
        'intent_pct_high': float(round(intent_pct_high, 1)),
        'burnout_pct': float(round(burnout_pct, 1)),
        'stay_score_avg': float(stay_score_avg) if stay_score_avg else 0,
        'stay_flight_pct': float(stay_flight_pct) if stay_flight_pct else 0,
        'stay_atrisk_pct': float(stay_atrisk_pct) if stay_atrisk_pct else 0,
        'stay_stable_pct': float(stay_stable_pct) if stay_stable_pct else 0,
        'silence_rate': float(silence_rate) if silence_rate else 0,
        'jsi_avg': float(jsi_avg) if jsi_avg else 0,
        'ews_red_pct': float(ews_red_pct) if ews_red_pct else 0,
        'quadrant': {k: float(v) for k, v in quad_counts.items()},
        'contradiction_pct': float(contradiction_pct) if contradiction_pct else 0,
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
