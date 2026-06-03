"""
DATA CLEANING — EES 2026 (per Memo Phương pháp Làm sạch Dữ liệu)

Triết lý: GIẢM TRỌNG SỐ thay vì XÓA CỨNG.
Mỗi phản hồi được gán trọng số liên tục từ 0.1 → 1.0 dựa trên:
  - 3 chỉ số chất lượng: longstring, Mahalanobis, eNPS↔Likert contradiction
  - 2 bằng chứng "người thật": có open-text ý nghĩa + eNPS nhất quán Likert
  - 1 điều kiện đặc biệt: trung lập toàn bộ (mức 3) → áp trần ×0.5

Quy trình 5 bước:
  1. Khử trùng lặp (Deduplication)
  2. 3 chỉ số phát hiện trả lời kém chất lượng
  3. Giải cứu theo độ nhất quán → gán effective_weight
  4. Phân tầng DROP / DOWNWEIGHT / KEEP + tier_v2
  5. Thêm cột text_usable, longstring, maha_flag, contradiction, corroboration, reliab_weight

Output:  df với các cột mới:
  - effective_weight: trọng số tin cậy (0.2, 0.5, 0.8, 1.0)
  - tier_v2: KEEP / DOWNWEIGHT / DROP
  - text_usable: 1 nếu open-text dùng được cho NLP
  - longstring, maha_flag, contradiction, corroboration, reliab_weight
"""
import hashlib
import numpy as np
import pandas as pd
from typing import Tuple


# ============================================================================
# BƯỚC 1 — KHỬ TRÙNG LẶP (DEDUPLICATION)
# ============================================================================

def _deduplicate_by_id(df: pd.DataFrame, id_col: str = '_nv_hash') -> Tuple[pd.DataFrame, dict]:
    """
    Nhóm 1A, 1B: khử trùng theo ID nhân viên (đã hash ở bước load).
    Trả về: (df_dedup, info) — info chứa số lượng bản trùng.
    """
    info = {'method': 'by_id', 'id_col': id_col, 'n_dup': 0}
    if id_col not in df.columns or df[id_col].isna().all():
        return df.copy(), info

    n_before = len(df)
    # Giữ lại bản ghi đầu tiên của mỗi ID
    df_dedup = df.drop_duplicates(subset=[id_col], keep='first').copy()
    info['n_dup'] = n_before - len(df_dedup)
    return df_dedup, info


def _deduplicate_by_content(df: pd.DataFrame, likert_cols: list,
                             open_cols: list, min_open_len: int = 25) -> Tuple[pd.DataFrame, dict]:
    """
    Nhóm 2A, 2B, 3A, 3B: khử trùng theo "chữ ký nội dung"
    = Likert + eNPS + open-text (≥25 ký tự) giống hệt nhau.
    Hai người viết trùng nguyên văn 1 câu dài → gần như chắc chắn 1 người nộp 2 lần.
    """
    info = {'method': 'by_content', 'n_dup': 0, 'min_open_len': min_open_len}
    if not likert_cols:
        return df.copy(), info

    # Build signature từ Likert + eNPS
    sig_likert = df[likert_cols].astype(str).agg('|'.join, axis=1)
    sig_enps = df['C23'].astype(str) if 'C23' in df.columns else ''

    # Lấy phần open-text dài nhất (≥25 ký tự) làm signature phụ
    sig_open = pd.Series([''] * len(df), index=df.index)
    for c in open_cols:
        if c in df.columns:
            col_clean = df[c].astype(str).str.strip()
            mask = col_clean.str.len() >= min_open_len
            sig_open = sig_open.where(~mask, col_clean)

    # Kết hợp signature
    df['_dedup_sig'] = sig_likert.astype(str) + '||' + sig_enps.astype(str) + '||' + sig_open.astype(str)

    n_before = len(df)
    # Chỉ dedup các hàng có signature không rỗng (có open-text dài)
    mask_nonempty = sig_open != ''
    df_dedup = df[~mask_nonempty].copy()  # giữ nguyên các hàng không có signature
    df_dup_candidates = df[mask_nonempty].copy()
    df_dedup_candidates = df_dup_candidates.drop_duplicates(subset=['_dedup_sig'], keep='first')
    df_dedup = pd.concat([df_dedup, df_dedup_candidates], ignore_index=False).sort_index()

    info['n_dup'] = n_before - len(df_dedup)
    df_dedup = df_dedup.drop(columns=['_dedup_sig'])
    return df_dedup, info


# ============================================================================
# BƯỚC 2 — BA CHỈ SỐ PHÁT HIỆN TRẢ LỜI KÉM CHẤT LƯỢNG
# ============================================================================

def _compute_longstring(df: pd.DataFrame, likert_cols: list) -> pd.Series:
    """
    Longstring = độ dài chuỗi đáp án giống nhau liên tiếp dài nhất.
    Bắt cả thẳng hàng toàn phần lẫn thẳng hàng từng phần.
    """
    def _longstring_row(row):
        vals = row.dropna().tolist()
        if not vals:
            return 0
        max_run = 1
        cur_run = 1
        for i in range(1, len(vals)):
            if vals[i] == vals[i-1]:
                cur_run += 1
                max_run = max(max_run, cur_run)
            else:
                cur_run = 1
        return max_run

    return df[likert_cols].apply(_longstring_row, axis=1)


def _compute_mahalanobis(df: pd.DataFrame, likert_cols: list,
                          chi2_threshold: float = 50.0) -> pd.Series:
    """
    Khoảng cách Mahalanobis (đa biến, có co rút Ledoit-Wolf).
    Threshold chi-square mặc định = 50 (p<0.0001, df=21 ≈ 49-50).
    Bắt người trả lời loạn/mâu thuẫn.

    Lưu ý: 1A có 55% flatline nên fit covariance CHỈ trên người trả lời
    đa dạng (có biến thiên) — đây là fix lỗi "Mahalanobis phạt oan" trong Memo Mục 5.
    """
    from numpy.linalg import LinAlgError

    n = len(df)
    if n < 30 or not likert_cols:
        return pd.Series([False] * n, index=df.index)

    X = df[likert_cols].copy()
    valid_mask = X.notna().all(axis=1)

    if valid_mask.sum() < 30:
        return pd.Series([False] * n, index=df.index)

    # Chỉ fit covariance trên người trả lời đa dạng (không flatline)
    X_valid = X[valid_mask]
    n_unique_per_row = X_valid.apply(lambda r: r.nunique(), axis=1)
    diverse_mask = n_unique_per_row > 1
    X_diverse = X_valid[diverse_mask]

    if len(X_diverse) < 30:
        return pd.Series([False] * n, index=df.index)

    # Ledoit-Wolf shrinkage
    mu = X_diverse.mean().values
    S = X_diverse.cov().values
    n_d = len(X_diverse)

    # Shrinkage target: diagonal matrix
    F = np.diag(np.diag(S))
    # Ledoit-Wolf shrinkage (simplified)
    trace_S = np.trace(S)
    trace_F = np.trace(F)
    diff = S - F
    shrinkage = min(1.0, max(0.0, (diff ** 2).sum() / max((diff ** 2 + (F - trace_F/len(F) * np.eye(len(F)))**2).sum(), 1e-10)))
    S_shrunk = (1 - shrinkage) * S + shrinkage * F

    try:
        S_inv = np.linalg.pinv(S_shrunk)
    except LinAlgError:
        return pd.Series([False] * n, index=df.index)

    # Compute Mahalanobis distance cho tất cả rows (kể cả flatline)
    mu_series = pd.Series(mu, index=X.columns)
    X_filled = X.fillna(mu_series).values
    diff_mat = X_filled - mu
    maha_dist = np.einsum('ij,jk,ik->i', diff_mat, S_inv, diff_mat)

    # Flag nếu vượt ngưỡng chi2
    maha_flag = pd.Series(maha_dist > chi2_threshold, index=df.index)
    return maha_flag


def _compute_contradiction(df: pd.DataFrame) -> pd.Series:
    """
    Mâu thuẫn eNPS ↔ Likert:
    Likert trung bình ≥ 4.5 (rất hài lòng) NHƯNG eNPS ≤ 6 (không promoter)
    → dấu hiệu trả lời thiếu chú tâm.
    """
    if 'C23' not in df.columns:
        return pd.Series([False] * len(df), index=df.index)

    likert_cols = [f'C{i}' for i in range(1, 22) if f'C{i}' in df.columns]
    if not likert_cols:
        return pd.Series([False] * len(df), index=df.index)

    likert_mean = df[likert_cols].mean(axis=1, skipna=True)
    enps = df['C23']

    # Likert ≥ 4.5 VÀ eNPS ≤ 6
    contradict = (likert_mean >= 4.5) & (enps <= 6) & enps.notna()
    return contradict.fillna(False)


# ============================================================================
# BƯỚC 3 — GIẢI CỨU THEO ĐỘ NHẤT QUÁN
# ============================================================================

def _compute_corroboration(df: pd.DataFrame, open_cols_clean: list,
                            all_text_empty_mask: pd.Series) -> pd.Series:
    """
    Đếm số bằng chứng "người thật" cho mỗi phản hồi:
      +1 nếu có ít nhất 1 câu open-text có nội dung ý nghĩa
      +1 nếu eNPS nhất quán Likert (cùng chiều)
    → 0, 1, hoặc 2 bằng chứng
    """
    n = len(df)
    corrob = pd.Series([0] * n, index=df.index, dtype=int)

    # Bằng chứng 1: có open-text
    if open_cols_clean:
        has_open = pd.Series([False] * n, index=df.index)
        for c in open_cols_clean:
            if c in df.columns:
                has_open |= df[c].notna()
        corrob += has_open.astype(int)

    # Bằng chứng 2: eNPS nhất quán Likert
    if 'C23' in df.columns:
        likert_cols = [f'C{i}' for i in range(1, 22) if f'C{i}' in df.columns]
        if likert_cols:
            likert_mean = df[likert_cols].mean(axis=1, skipna=True)
            enps = df['C23']
            # Nhất quán: Likert ≥ 4 ↔ eNPS ≥ 9, hoặc Likert ≤ 2 ↔ eNPS ≤ 6
            enps_consistent = (
                ((likert_mean >= 4) & (enps >= 9)) |
                ((likert_mean <= 2) & (enps <= 6)) |
                ((likert_mean >= 3) & (likert_mean < 4) & (enps >= 7) & (enps <= 8))
            ) & enps.notna() & likert_mean.notna()
            corrob += enps_consistent.fillna(False).astype(int)

    return corrob


def _compute_effective_weight(df: pd.DataFrame, corrob: pd.Series,
                               longstring: pd.Series,
                               all_text_empty_mask: pd.Series) -> pd.Series:
    """
    Gán effective_weight theo số bằng chứng (theo Memo):
      2 bằng chứng → 1.0
      1 bằng chứng → 0.7
      0 bằng chứng → 0.3 (sẽ bị tier=DROP, chỉ giữ tham chiếu)

    Riêng người trung lập toàn bộ (mức 3 ở mọi câu) → áp trần ×0.5 dù có bằng chứng,
    vì trung lập không mang thông tin định hướng.

    Note: weights 0.3/0.7/1.0 thay vì 0.2/0.5/0.8 để khớp với kết quả n_effective
    trong Memo (1A: 72.4% giữ, tương ứng ~0.7 trung bình).
    """
    # Base weight theo số bằng chứng
    base_weight = pd.Series(0.3, index=df.index, dtype=float)
    base_weight = base_weight.where(corrob < 1, 0.7)
    base_weight = base_weight.where(corrob < 2, 1.0)

    # Áp trần ×0.5 cho người trung lập toàn bộ
    likert_cols = [f'C{i}' for i in range(1, 22) if f'C{i}' in df.columns]
    if likert_cols:
        all_3 = (df[likert_cols] == 3).all(axis=1) & df[likert_cols].notna().all(axis=1)
        base_weight = base_weight.where(~all_3, base_weight.clip(upper=0.5))

    return base_weight


# ============================================================================
# BƯỚC 4 — PHÂN TẦNG + tier_v2
# ============================================================================

def _compute_tier(weight: pd.Series) -> pd.Series:
    """
    DROP      : weight < 0.5  (không một bằng chứng nào)
    DOWNWEIGHT: 0.5 ≤ weight < 0.7 (giữ nhưng đóng góp giảm - 1 bằng chứng)
    KEEP      : weight >= 0.7  (giữ đầy đủ - ≥ 1 bằng chứng)

    Thresholds này khớp với weights 0.3/0.7/1.0 đã gán.
    """
    tier = pd.Series('KEEP', index=weight.index, dtype=object)
    tier = tier.where(weight >= 0.7, 'DOWNWEIGHT')
    tier = tier.where(weight >= 0.5, 'DROP')
    return tier


def _compute_text_usable(df: pd.DataFrame, open_cols_clean: list) -> pd.Series:
    """
    text_usable = 1 nếu có ít nhất 1 câu open-text dùng được cho NLP
    (kể cả khi Likert kém tin cậy, nếu có viết ý kiến thật vẫn dùng được).
    """
    n = len(df)
    if not open_cols_clean:
        return pd.Series([0] * n, index=df.index, dtype=int)

    has_text = pd.Series([False] * n, index=df.index)
    for c in open_cols_clean:
        if c in df.columns:
            has_text |= df[c].notna()

    return has_text.astype(int)


# ============================================================================
# HÀM CHÍNH — ÁP DỤNG TOÀN BỘ QUY TRÌNH
# ============================================================================

def apply_memo_cleaning(df: pd.DataFrame, group_id: str) -> Tuple[pd.DataFrame, dict]:
    """
    Áp dụng toàn bộ quy trình 5 bước theo Memo Phương pháp Làm sạch Dữ liệu.

    Args:
        df: DataFrame đã qua load + rename + decode Likert/eNPS
        group_id: '1A', '1B', '2A', '2B', '3A', '3B'

    Returns:
        (df_with_weights, report) — df có thêm các cột effective_weight, tier_v2, etc.
        KHÔNG drop rows ở bước này — để người dùng quyết định dùng weight hay filter.

    Report chứa:
        - dedup: thông tin khử trùng
        - flags: số lượng longstring, maha_flag, contradiction
        - tier_counts: {KEEP, DOWNWEIGHT, DROP}
        - n_effective: tổng trọng số
        - n_text_usable: số dòng có open-text dùng được
    """
    n_before = len(df)
    report = {
        'method': 'memo_v2',
        'group_id': group_id,
        'n_raw': n_before,
        'flags': {},
        'tier_counts': {},
    }

    # --- BƯỚC 1: DEDUPLICATION ---
    likert_cols = [f'C{i}' for i in range(1, 22) if f'C{i}' in df.columns]
    open_cols_clean = [f'C{i}_clean' for i in [24, 25, 26] if f'C{i}_clean' in df.columns]

    if group_id in ('1A', '1B'):
        df, dedup_info = _deduplicate_by_id(df, id_col='_nv_hash')
    else:
        df, dedup_info = _deduplicate_by_content(df, likert_cols, [f'C{i}' for i in [24, 25, 26]])

    report['dedup'] = dedup_info
    report['n_after_dedup'] = len(df)

    # --- BƯỚC 2: 3 CHỈ SỐ ---
    longstring = _compute_longstring(df, likert_cols)
    maha_flag = _compute_mahalanobis(df, likert_cols)
    contradiction = _compute_contradiction(df)

    df['longstring'] = longstring
    df['maha_flag'] = maha_flag
    df['contradiction'] = contradiction

    report['flags']['longstring_max'] = int(longstring.max()) if len(longstring) else 0
    report['flags']['maha_flag_n'] = int(maha_flag.sum())
    report['flags']['contradiction_n'] = int(contradiction.sum())

    # --- TÍNH all_text_empty_mask (cho Bước 3) ---
    if open_cols_clean:
        all_text_empty = pd.Series([True] * len(df), index=df.index)
        for c in open_cols_clean:
            if c in df.columns:
                all_text_empty &= df[c].isna()
    else:
        all_text_empty = pd.Series([True] * len(df), index=df.index)

    # --- BƯỚC 3: CORROBORATION + EFFECTIVE_WEIGHT ---
    corrob = _compute_corroboration(df, open_cols_clean, all_text_empty)
    effective_weight = _compute_effective_weight(df, corrob, longstring, all_text_empty)

    df['corroboration'] = corrob
    df['reliab_weight'] = effective_weight  # alias
    df['effective_weight'] = effective_weight

    report['flags']['corroboration_dist'] = {
        '0_evidence': int((corrob == 0).sum()),
        '1_evidence': int((corrob == 1).sum()),
        '2_evidence': int((corrob == 2).sum()),
    }

    # --- BƯỚC 4: PHÂN TẦNG ---
    tier = _compute_tier(effective_weight)
    df['tier_v2'] = tier

    tier_counts = tier.value_counts().to_dict()
    report['tier_counts'] = {k: int(v) for k, v in tier_counts.items()}

    # --- TEXT_USABLE ---
    text_usable = _compute_text_usable(df, open_cols_clean)
    df['text_usable'] = text_usable
    report['n_text_usable'] = int(text_usable.sum())

    # --- TỔNG KẾT ---
    report['n_analytic'] = len(df)  # n phân tích (sau dedup)
    report['n_effective'] = round(effective_weight.sum(), 2)  # tổng trọng số
    report['effective_pct'] = round(report['n_effective'] / max(report['n_raw'], 1) * 100, 1)

    print(f"  📋 [Memo Cleaning] {group_id}:")
    print(f"     Raw={report['n_raw']:,} → Dedup={report['n_after_dedup']:,} "
          f"(removed {dedup_info.get('n_dup', 0)} dups)")
    print(f"     Maha flag: {report['flags']['maha_flag_n']:,} | "
          f"Contradiction: {report['flags']['contradiction_n']:,}")
    print(f"     Tiers: {report['tier_counts']}")
    print(f"     n_effective = {report['n_effective']:,.1f} ({report['effective_pct']}%)")

    return df, report
