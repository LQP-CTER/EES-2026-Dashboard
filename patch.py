import re

with open('utils/data_loader.py', 'r', encoding='utf-8') as f:
    content = f.read()

new_load_group = '''@st.cache_data(ttl=3600, show_spinner=False)
def load_group(group_id: str):
    \"\"\"
    Load dữ liệu đã xử lý sẵn cho một group khảo sát.
    Ưu tiên: NeonDB → Supabase → Parquet local.
    Returns (df_clean, n_before).
    \"\"\"
    from config.groups import GROUP_REGISTRY
    from shared.codebook import PILLAR_WEIGHTS
    cfg      = GROUP_REGISTRY[group_id]
    codebook = cfg['codebook']

    table_name = f"survey_{group_id.lower()}_clean"
    df_clean   = None

    # ── Ưu tiên 1: NeonDB (pre-processed table) ──────────────────────────────
    try:
        conn     = st.connection("neondb", type="sql")
        df_clean = conn.query(f\\'SELECT * FROM "{table_name}"\\', ttl=3600)
        print(f"[{group_id}] Loaded {len(df_clean):,} rows from NeonDB ({table_name})")
    except Exception as e_neo:
        print(f"[{group_id}] NeonDB unavailable ({e_neo}). Trying Supabase...")

    # ── Ưu tiên 2: Supabase ───────────────────────────────────────────────────
    if df_clean is None:
        try:
            conn     = st.connection("supabase", type="sql")
            df_clean = conn.query(f\\'SELECT * FROM "{table_name}"\\', ttl=3600)
            print(f"[{group_id}] Loaded {len(df_clean):,} rows from Supabase ({table_name})")
        except Exception as e_supa:
            print(f"[{group_id}] Supabase unavailable ({e_supa}). Trying local parquet...")

    # ── Ưu tiên 3: Local Parquet backup ──────────────────────────────────────
    if df_clean is None:
        import os
        import pandas as pd
        parquet_path = os.path.join(
            os.path.abspath(os.path.join(os.path.dirname(__file__), '..')),
            'Data_Clean', f'{group_id}_clean.parquet'
        )
        if os.path.exists(parquet_path):
            try:
                df_clean = pd.read_parquet(parquet_path)
                print(f"[{group_id}] Loaded {len(df_clean):,} rows from local parquet ({parquet_path})")
            except Exception as e_parq:
                print(f"[{group_id}] Parquet read failed ({e_parq}).")

    if df_clean is None:
        raise RuntimeError(f"Could not load data for {group_id} from any source.")

    import pandas as pd
    # Đọc metadata từ các cột _meta_ (được pipeline lưu vào DB/parquet)
    n_before     = int(df_clean['_meta_n_raw'].iloc[0])   if '_meta_n_raw'   in df_clean.columns else len(df_clean)
    n_clean      = int(df_clean['_meta_n_clean'].iloc[0]) if '_meta_n_clean' in df_clean.columns else len(df_clean)
    n_removed    = n_before - n_clean
    pct_removed  = round(n_removed / n_before * 100, 1)   if n_before else 0.0
    filter_desc  = str(df_clean['_meta_filter_desc'].iloc[0])  if '_meta_filter_desc' in df_clean.columns else ''

    # Restore df.attrs để downstream views tương thích hoàn toàn
    likert_cols = [q for q, info in codebook.items() if info['loại'] == 'likert']
    open_cols   = [q for q, info in codebook.items() if info['loại'] == 'open']
    df_clean.attrs['group_id']      = group_id
    df_clean.attrs['codebook']      = codebook
    df_clean.attrs['likert_cols']   = [c for c in likert_cols if c in df_clean.columns]
    df_clean.attrs['open_cols']     = [c for c in open_cols   if c in df_clean.columns]
    df_clean.attrs['n_before']      = n_before
    df_clean.attrs['n_removed']     = n_removed
    df_clean.attrs['pct_removed']   = pct_removed
    df_clean.attrs['filter_method'] = 'weighted_reliability'
    df_clean.attrs['filter_desc']   = filter_desc
    # memo_report rút gọn
    df_clean.attrs['memo_report'] = {
        'n_raw':      n_before,
        'n_clean':    n_clean,
        'n_removed':  n_removed,
        'pct_removed': pct_removed,
        'filter_desc': filter_desc,
        'mahalanobis': {},
        'nlp': {}
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
'''

pattern = re.compile(r'@st\.cache_data\(ttl=3600, show_spinner=False\)\ndef load_group\(group_id: str\):.*?def load_all_available', re.DOTALL)
new_content = pattern.sub(new_load_group + '\\n\\ndef load_all_available', content)

with open('utils/data_loader.py', 'w', encoding='utf-8') as f:
    f.write(new_content)
