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
)
from shared.workforce_mapper import map_survey_to_org, get_org_summary

BASE = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
DATA_DIR = os.path.join(BASE, 'Data')

PILLAR_LABELS = {
    'TC1': 'Niềm tin & Định hướng', 'TC2': 'Quản lý Trực tiếp',
    'TC3': 'Môi trường & Công cụ', 'TC4': 'Đãi ngộ & Công bằng',
    'TC5': 'Văn hóa & Tự hào',
}


@st.cache_data(ttl=3600, show_spinner="📂 Đang tải dữ liệu...")
def load_group(group_id: str):
    """Load & clean a single survey group. Returns (df_clean, n_before)."""
    from config.groups import GROUP_REGISTRY
    cfg = GROUP_REGISTRY[group_id]
    codebook = cfg['codebook']
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

    # Decode demographic Q5 (Thâm niên) if present
    Q5_MAP = {
        'A': 'Dưới 1 tháng', 'B': 'Trên 1 đến 3 tháng', 'C': 'Trên 3 đến 6 tháng',
        'D': 'Trên 6 đến 9 tháng', 'E': 'Trên 9 đến 12 tháng', 'F': 'Trên 1 đến 2 năm',
        'G': 'Trên 2 đến 3 năm', 'H': 'Trên 3 đến 5 năm', 'I': 'Trên 5 năm',
        'J': 'Chưa xác định'
    }
    if 'Q5' in df.columns:
        df['Q5'] = df['Q5'].apply(lambda x: Q5_MAP.get(str(x).strip().upper(), str(x).strip()) if pd.notna(x) and str(x).strip() != '' else 'Chưa xác định')
        # If it's a 1-character string not in Q5_MAP, map it to 'Chưa xác định'
        df['Q5'] = df['Q5'].apply(lambda x: 'Chưa xác định' if isinstance(x, str) and len(x) == 1 and x.isupper() else x)


    # Quality flags
    df['likert_mean'] = df[likert_cols].mean(axis=1)
    df['_likert_sd'] = df[likert_cols].std(axis=1)
    df['n_valid_likert'] = df[likert_cols].notna().sum(axis=1)
    df['flag_straightline'] = (df['_likert_sd'] == 0) & (df['n_valid_likert'] >= 10)
    df['flag_too_missing'] = (df[likert_cols].isna().sum(axis=1) / len(likert_cols) * 100) > 80
    df_clean = df[~df['flag_too_missing']].copy()

    # Org mapping
    vung_col = df_clean.columns[10]
    for c in df_clean.columns:
        if 'Vùng' in str(c) or 'vùng' in str(c):
            vung_col = c; break
    try:
        df_clean = map_survey_to_org(df_clean, group=group_id, vung_col=vung_col,
                                     id_col=df_clean.columns[1])
    except Exception:
        df_clean['division'] = 'N/A'
        df_clean['department'] = 'N/A'
        df_clean['section'] = df_clean.get(vung_col, 'N/A')

    # Pillar scores
    pillar_cols = defaultdict(list)
    for q_id, info in codebook.items():
        if info['trụ_cột']:
            pillar_cols[info['trụ_cột']].append(q_id)
    for pillar, cols in pillar_cols.items():
        valid = [c for c in cols if c in df_clean.columns]
        df_clean[f'{pillar}_mean'] = df_clean[valid].mean(axis=1)
        df_clean[f'{pillar}_pct'] = df_clean[f'{pillar}_mean'].apply(calc_engagement_pct)

    # EI
    pillar_pcts = [f'{p}_pct' for p in PILLAR_WEIGHTS.keys()]
    weights = list(PILLAR_WEIGHTS.values())
    df_clean['EI'] = sum(df_clean[p] * w for p, w in zip(pillar_pcts, weights) if p in df_clean.columns)
    df_clean['EI_class'] = df_clean['EI'].apply(classify_ei)

    # MEI
    mei_cols = ['Q11', 'Q12', 'Q14', 'Q15']
    vm = [c for c in mei_cols if c in df_clean.columns]
    if vm:
        df_clean['MEI'] = df_clean[vm].apply(
            lambda r: (r >= 4).sum() / r.notna().sum() * 100 if r.notna().sum() > 0 else None, axis=1)

    # Burnout risk
    pressure = [c for c in ['Q18', 'Q29'] if c in df_clean.columns]
    resource = [c for c in ['Q11', 'Q16'] if c in df_clean.columns]
    if pressure and resource:
        df_clean['burnout_risk'] = df_clean[pressure].mean(axis=1) - df_clean[resource].mean(axis=1)

    # NLP prep
    try:
        from shared.nlp_utils import preprocess_text
        for q in open_cols:
            if q in df_clean.columns:
                df_clean[f'{q}_clean'] = df_clean[q].apply(
                    lambda x: preprocess_text(str(x)) if pd.notna(x) and len(str(x).strip()) > 3 else None)
    except Exception:
        pass

    # Store metadata
    df_clean.attrs['group_id'] = group_id
    df_clean.attrs['likert_cols'] = likert_cols
    df_clean.attrs['open_cols'] = open_cols
    df_clean.attrs['codebook'] = codebook

    return df_clean, n_before


def load_all_available():
    """Load all groups that have data. Returns dict {group_id: (df, n_before)}."""
    from config.groups import get_available_groups
    results = {}
    for gid in get_available_groups():
        try:
            results[gid] = load_group(gid)
        except Exception as e:
            st.warning(f"⚠️ Không load được nhóm {gid}: {e}")
    return results


def compute_kpis(df):
    """Compute KPI dict from any group's dataframe."""
    n = len(df)
    if n == 0:
        return {'n': 0, 'ei_mean': 0, 'enps_score': 0, 'promoters': 0,
                'passives': 0, 'detractors': 0, 'mei_avg': 0,
                'intent_pct_low': 0, 'burnout_pct': 0}

    ei_mean = df['EI'].mean()
    enps_col = df.get('eNPS', pd.Series(dtype=float))
    n_valid_enps = enps_col.notna().sum()
    promoters = (enps_col >= 9).sum()
    passives = ((enps_col >= 7) & (enps_col <= 8)).sum()
    detractors = (enps_col <= 6).sum()
    enps_score = (promoters - detractors) / n_valid_enps * 100 if n_valid_enps > 0 else 0
    mei_avg = df['MEI'].mean() if 'MEI' in df.columns else 0
    intent_col = df.get('intent', pd.Series(dtype=float))
    intent_low = (intent_col <= 2).sum()
    intent_pct = intent_low / intent_col.notna().sum() * 100 if intent_col.notna().sum() > 0 else 0
    burnout_high = (df['burnout_risk'] > 0).sum() if 'burnout_risk' in df.columns else 0
    burnout_pct = burnout_high / n * 100

    return {
        'n': n, 'ei_mean': round(ei_mean, 1),
        'enps_score': round(enps_score, 0),
        'promoters': int(promoters), 'passives': int(passives), 'detractors': int(detractors),
        'mei_avg': round(mei_avg, 1),
        'intent_pct_low': round(intent_pct, 1),
        'burnout_pct': round(burnout_pct, 1),
    }


@st.cache_data(ttl=3600, show_spinner="📂 Đang tải HRIS...")
def load_hris(group_id: str):
    """Load HRIS for a specific group."""
    from config.groups import GROUP_REGISTRY
    cfg = GROUP_REGISTRY[group_id]
    if not cfg.get('hris_file'):
        return None, None
    fpath = os.path.join(DATA_DIR, cfg['hris_file'])
    if not os.path.exists(fpath):
        return None, None

    df_hris = pd.read_excel(fpath, engine='openpyxl')
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
    df_latest['_nv_id'] = pd.to_numeric(df_latest['ID'], errors='coerce').astype('Int64')
    return df_latest, latest_label


def merge_survey_hris(df_clean, df_hris):
    """Merge survey with HRIS."""
    id_col = df_clean.columns[1]
    df_clean = df_clean.copy()
    df_clean['_nv_id'] = pd.to_numeric(df_clean[id_col], errors='coerce').astype('Int64')

    merge_cols = ['_nv_id', 'Lương thực nhận', 'Tổng', 'Phạt', 'Tổng Đơn giao',
                  'Năng suất Giao', 'Phân loại Nhóm Năng Suất Giao',
                  'Phân loại Chiến Binh ', 'Thâm niên (Đơn vị tính là tháng)',
                  'Nhóm Thâm Niên', 'Range lương thực nhận', 'Ngày nghỉ việc',
                  'Lương đơn hàng', 'Thưởng/ Phạt GTC và LTC', 'Phụ cấp',
                  'Thưởng Doanh Thu', 'Truy thu mất hàng COD']
    merge_cols = [c for c in merge_cols if c in df_hris.columns]

    df_m = df_clean.merge(df_hris[merge_cols], on='_nv_id', how='left', suffixes=('', '_hris'))

    if 'Lương thực nhận' in df_m.columns:
        df_m['income_m'] = df_m['Lương thực nhận'] / 1_000_000
        df_m['income_group'] = pd.cut(df_m['income_m'], bins=[0, 5, 7, 10, 15, 200],
                                       labels=['< 5 triệu', '5-7 triệu', '7-10 triệu', '10-15 triệu', '> 15 triệu'])
    if 'Phạt' in df_m.columns:
        df_m['phat_m'] = df_m['Phạt'].fillna(0) / 1_000_000
        truy_thu = df_m.get('Truy thu mất hàng COD', pd.Series(0, index=df_m.index)).fillna(0) / 1_000_000
        df_m['tong_phat'] = df_m['phat_m'] + truy_thu
    if 'intent' in df_m.columns:
        df_m['intent_risk'] = df_m['intent'].apply(
            lambda x: '🔴 Muốn nghỉ (1-2)' if pd.notna(x) and x <= 2
            else ('🟡 Phân vân (3)' if pd.notna(x) and x == 3
                  else ('🟢 Gắn bó (4-5)' if pd.notna(x) else None)))
    return df_m
