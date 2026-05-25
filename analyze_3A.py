import pandas as pd
from utils.data_loader import load_group
from config.groups import GROUP_REGISTRY

group_id = '3A'
df_clean, _ = load_group(group_id)

print(f"Total respondents in 3A: {len(df_clean)}")
print(f"Mean EI of 3A: {df_clean['EI'].mean():.1f}%")

cfg = GROUP_REGISTRY[group_id]
df_raw = pd.read_csv(cfg['url'])

likert_cols = df_clean.attrs['likert_cols']
codebook = df_clean.attrs['codebook']

print("\n--- Bottom 10 Lowest Scoring Questions ---")
q_means = df_clean[likert_cols].mean().sort_values()
for q_id, mean_val in q_means.head(10).items():
    col_idx = codebook[q_id]['col_idx']
    if col_idx < len(df_raw.columns):
        q_text = df_raw.columns[col_idx]
    else:
        q_text = "Unknown"
    print(f"{q_id}: {mean_val:.2f} - {str(q_text).strip()}")
    
print("\n--- Bottom 10 Departments by EI ---")
# Only consider departments with at least 5 respondents
dept_stats = df_clean.groupby('department').agg(
    n_count=('EI', 'count'),
    mean_ei=('EI', 'mean')
)
dept_stats = dept_stats[dept_stats['n_count'] >= 5]
bottom_depts = dept_stats.sort_values('mean_ei').head(10)
for dept, row in bottom_depts.iterrows():
    print(f"{dept} (N={int(row['n_count'])}): {row['mean_ei']:.1f}%")

print("\n--- Bottom 5 Divisions by EI ---")
div_stats = df_clean.groupby('division').agg(
    n_count=('EI', 'count'),
    mean_ei=('EI', 'mean')
)
div_stats = div_stats[div_stats['n_count'] >= 10]
bottom_divs = div_stats.sort_values('mean_ei').head(5)
for div, row in bottom_divs.iterrows():
    print(f"{div} (N={int(row['n_count'])}): {row['mean_ei']:.1f}%")
