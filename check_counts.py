import pandas as pd
from utils.data_loader import load_group

ALL_GROUPS = ['1A', '1B', '2A', '2B', '3A', '3B']
for group in ALL_GROUPS:
    print(f'\n==== Group {group} ====')
    try:
        df_clean, n_before = load_group(group)
        print(f'Total raw: {n_before}')
        print(f'Total clean: {len(df_clean)}')
        
        # Check mapping column
        if 'section' in df_clean.columns and df_clean['section'].nunique() > 1:
            grp_col = 'section'
        elif 'department' in df_clean.columns and df_clean['department'].nunique() > 1:
            grp_col = 'department'
        else:
            grp_col = 'division' if 'division' in df_clean.columns else None
            
        if grp_col:
            khac_mask = df_clean[grp_col] == 'Khác'
            khac_count = khac_mask.sum()
            mapped_count = len(df_clean) - khac_count
            print(f'Mapped to {grp_col}: {mapped_count}')
            print(f'Mapped to Khác: {khac_count}')
            
            if khac_count > 0:
                print('Khác values (Q3):')
                print(df_clean[khac_mask].iloc[:, 3].value_counts().head())
        else:
            print('No grouping column found!')
            
    except Exception as e:
        print(f'Error: {e}')
