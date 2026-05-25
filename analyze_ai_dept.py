import pandas as pd
from utils.data_loader import load_group
from config.groups import GROUP_REGISTRY

group_id = '3B'
df_clean, _ = load_group(group_id)
ai_dept = df_clean[df_clean['department'] == 'Phòng AI Cốt Lõi & Nền Tảng Dữ Liệu']

print(f"Number of respondents: {len(ai_dept)}")
if len(ai_dept) > 0:
    print(f"Mean EI: {ai_dept['EI'].mean():.1f}%")
    
    cfg = GROUP_REGISTRY[group_id]
    df_raw = pd.read_csv(cfg['url'])
    
    likert_cols = df_clean.attrs['likert_cols']
    codebook = df_clean.attrs['codebook']
    
    print("\n--- Mean Score per Question ---")
    q_means = ai_dept[likert_cols].mean().sort_values()
    for q_id, mean_val in q_means.items():
        col_idx = codebook[q_id]['col_idx']
        if col_idx < len(df_raw.columns):
            q_text = df_raw.columns[col_idx]
        else:
            q_text = "Unknown"
        print(f"{q_id}: {mean_val:.2f} - {str(q_text).strip()}")
        
    print("\n--- Open-ended Feedback ---")
    open_cols = df_clean.attrs['open_cols']
    for q in open_cols:
        if q in ai_dept.columns:
            feedbacks = ai_dept[q].dropna().tolist()
            if feedbacks:
                col_idx = codebook[q]['col_idx']
                q_text = df_raw.columns[col_idx] if col_idx < len(df_raw.columns) else "Unknown"
                print(f"\n{q} ({q_text.strip()}):")
                for f in feedbacks:
                    print(f" - {f}")
