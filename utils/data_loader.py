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


@st.cache_data(ttl=3600, show_spinner=" Đang tải dữ liệu...")
def load_group(group_id: str):
    """Load & clean a single survey group. Returns (df_clean, n_before)."""
    from config.groups import GROUP_REGISTRY
    cfg = GROUP_REGISTRY[group_id]
    codebook = cfg['codebook']
    try:
        # Load directly from Supabase via standard SQL Connection
        conn = st.connection("supabase", type="sql")
        table_name = f"survey_{group_id.lower()}"
        df_raw = conn.query(f"SELECT * FROM {table_name}", ttl=3600)
        print(f" Đã tải {len(df_raw)} dòng dữ liệu {group_id} từ Supabase siêu tốc!")
    except Exception as e:
        # Fallback to CSV if DB is not reachable
        print(f"Lỗi kết nối Supabase ({e}). Đang dùng file dự phòng (Google Sheets)...")
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
        'J': 'Khác'
    }
    if 'Q5' in df.columns:
        df['Q5'] = df['Q5'].apply(lambda x: Q5_MAP.get(str(x).strip().upper(), str(x).strip()) if pd.notna(x) and str(x).strip() != '' else 'Khác')
        # If it's a 1-character string not in Q5_MAP, map it to 'Khác'
        df['Q5'] = df['Q5'].apply(lambda x: 'Khác' if isinstance(x, str) and len(x) == 1 and x.isupper() else x)
        df['Q5'] = df['Q5'].replace('Chưa xác định', 'Khác')


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
    
    enps_col = df.get('eNPS', pd.Series(dtype=float))
    df['evidence_enps'] = False
    if 'eNPS' in df.columns:
        df['evidence_enps'] = (
            ((df['likert_mean'] >= 4) & (enps_col >= 7)) |
            ((df['likert_mean'] <= 2) & (enps_col <= 6))
        )
        
    df['num_evidence'] = df['evidence_open'].astype(int) + df['evidence_enps'].astype(int)
    
    def _calc_weight(row):
        if not row['flag_straightline']:
            return 1.0, False
        ev = row['num_evidence']
        is_neutral = (row['likert_mean'] == 3)
        if ev == 0:
            return 0.2, True
        elif ev == 1:
            w = 0.5
        else:
            w = 0.8
        if is_neutral:
            w = min(w, 0.5)
        return w, False

    res = df.apply(_calc_weight, axis=1)
    df['CompanyRollup_Weight'] = [x[0] for x in res]
    df['flag_drop'] = [x[1] for x in res]
    
    if group_id == '2A':
        dup_cols = likert_cols.copy()
        if 'eNPS' in df.columns: dup_cols.append('eNPS')
        def get_long_open(row):
            txt = " ".join([str(x) for x in row[open_cols] if pd.notna(x)])
            return txt if len(txt) >= 25 else np.nan
        df['_long_open'] = df.apply(get_long_open, axis=1)
        dup_cols.append('_long_open')
        is_dup = df.duplicated(subset=dup_cols, keep='first') & df['_long_open'].notna()
        df.loc[is_dup, 'flag_drop'] = True

    df_clean = df[~df['flag_drop']].copy()
    _filter_method = 'weighted_reliability'
    _filter_desc   = 'Tính trọng số tin cậy (0.2 - 1.0). Chỉ loại (DROP) nếu thẳng hàng VÀ không có bằng chứng (không open, không nhất quán eNPS)'

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
                df_clean["section"].astype(str).str.strip().str.lower().isin(EXCLUDE_DIVS)
            )
            df_clean = df_clean[~m_exclude].copy()
    except Exception as e:
        print(f"Lỗi map data: {e}")
        df_clean['division'] = 'Khác'
        df_clean['department'] = 'Khác'
        df_clean['section'] = 'Khác'

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

    # MEI — Manager Effectiveness Index (% câu TC2 được đánh ≥4)
    # Dùng toàn bộ câu TC2 của ĐÚNG nhóm thay vì hard-code Q-number theo 1A/1B.
    # (Với 2A/2B/3A/3B, TC2 = Q13-Q17; với 1A/1B, TC2 = Q11-Q15.)
    mei_cols = [c for c in get_pillar_questions(group_id, 'TC2') if c in df_clean.columns]
    if mei_cols:
        df_clean['MEI'] = df_clean[mei_cols].apply(
            lambda r: (r >= 4).sum() / r.notna().sum() * 100 if r.notna().sum() > 0 else None, axis=1)

    # Burnout risk = áp lực (đảo chiều) trừ nguồn lực hỗ trợ.
    # Vai trò câu hỏi (pressure / workload / mgr_support / tool) được tra theo nhóm.
    pressure_roles = ['pressure', 'workload']
    resource_roles = ['mgr_support', 'tool']
    pressure = [q for q in (get_role_question(group_id, r) for r in pressure_roles)
                if q and q in df_clean.columns]
    resource = [q for q in (get_role_question(group_id, r) for r in resource_roles)
                if q and q in df_clean.columns]
    if pressure and resource:
        df_clean['burnout_risk'] = df_clean[pressure].mean(axis=1) - df_clean[resource].mean(axis=1)

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

    # 3) Early Warning Score (EWS) — cảnh báo nghỉ sớm cho nhóm thâm niên ≤ 3 tháng.
    #    Dựa trên: ý định ở lại (intent), TC2 (quản lý), TC3 (điều kiện).
    #    Điểm 0-100, cao = rủi ro cao. Chỉ tính cho nhóm mới; còn lại = NaN.
    EARLY_TENURE = ['Dưới 1 tháng', 'Trên 1 đến 3 tháng', '< 1 tháng', '1-3 tháng']
    if 'Q5' in df_clean.columns:
        early_mask = df_clean['Q5'].isin(EARLY_TENURE)

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

    # 4) Engagement Quadrant — phân loại dựa trên eNPS (cao/thấp) và intent (cao/thấp).
    #    Tài liệu dùng eNPS × Q22; ở đây Q22-stay được thay bằng intent thực.
    #    Champions / Trapped Loyalists / Confused Leavers / Flight Risk.
    if 'eNPS' in df_clean.columns and 'intent' in df_clean.columns:
        def _quadrant(row):
            e = row.get('eNPS')
            i = row.get('intent')
            if pd.isna(e) or pd.isna(i):
                return None
            enps_high = e >= 7         # Passive/Promoter
            stay_high = i >= 4         # muốn ở lại
            if enps_high and stay_high:
                return 'Champions'
            if (not enps_high) and stay_high:
                return 'Trapped Loyalists'
            if enps_high and (not stay_high):
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

    return df_clean, n_before


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
    
    burnout_pct = weighted_pct(df.get('burnout_risk', pd.Series(0, index=df.index)) > 0)

    q22_col = df.get('stay_intention', pd.Series(dtype=float))
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
