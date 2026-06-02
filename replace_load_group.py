import re

with open('utils/data_loader.py', 'r', encoding='utf-8') as f:
    orig = f.read()

new_load_group = '''def load_group(group_id: str):
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
'''

new_orig = re.sub(r'def load_group\(group_id: str\):.*?(?=\n@st\.cache_data|\Z)', new_load_group, orig, flags=re.DOTALL)
with open('utils/data_loader.py', 'w', encoding='utf-8') as f:
    f.write(new_orig)
print('Replaced load_group in data_loader.py')
