import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import pandas as pd
import streamlit as st
st.cache_data.clear()

from utils.data_loader import load_group, load_hris, merge_survey_hris

df_clean, _ = load_group('1A')
df_hris, _ = load_hris()
df_m = merge_survey_hris(df_clean, df_hris)

# Create phat_label (same as view_d_root_cause.py)
def _phat_label(x):
    if pd.isna(x): return 'Chưa rõ'
    if x <= 0:   return 'Không phạt'
    if x < 0.5:  return '<500k'
    if x < 1.0:  return '500-1tr'
    if x < 3.0:  return '1 - 3tr'
    if x < 5.0:  return '3 - 5tr'
    return '> 5tr'
df_m['phat_label'] = df_m['tong_phat'].apply(_phat_label)

print(f"=== OVERALL ===")
print(f"Total: {len(df_m)}")
print(f"Overall quit rate: {(df_m['intent_risk'].str.contains('Muốn nghỉ').sum()/len(df_m)*100):.1f}%")
print(f"\nIntent distribution:")
print(df_m['intent_risk'].value_counts())
print(f"\nphat_label distribution:")
print(df_m['phat_label'].value_counts())

# Check raw tong_phat values
print(f"\n=== tong_phat stats ===")
print(f"mean: {df_m['tong_phat'].mean():.4f} triệu")
print(f"median: {df_m['tong_phat'].median():.4f} triệu")
print(f"max: {df_m['tong_phat'].max():.4f} triệu")
print(f"tong_phat == 0: {(df_m['tong_phat'] == 0).sum()}")
print(f"tong_phat > 0: {(df_m['tong_phat'] > 0).sum()}")

# Raw Phạt column before conversion
print(f"\n=== RAW Phạt column ===")
if 'Phạt' in df_m.columns:
    print(f"dtype: {df_m['Phạt'].dtype}")
    print(f"sample values: {df_m['Phạt'].dropna().head(10).tolist()}")
    print(f"mean: {df_m['Phạt'].mean():.0f}")
    print(f"max: {df_m['Phạt'].max():.0f}")

# Cross-tab: Quit rate by income × penalty (THE KEY CHECK)
print(f"\n{'='*80}")
print(f"=== CROSS-TAB: QUIT RATE by INCOME × PENALTY ===")
print(f"{'='*80}")

income_col = 'income_group'
df_heat = df_m[(df_m['phat_label'] != 'Chưa rõ') & (df_m[income_col].notna())].copy()

inc_order = ['< 5 triệu', '5 - 7 triệu', '7 - 10 triệu', '10 - 15 triệu', '15 - 20 triệu']
phat_order = ['Không phạt', '<500k', '500-1tr', '1 - 3tr', '3 - 5tr', '> 5tr']

print(f"\n{'Mức TN':<18s} | {'Mức phạt':<12s} | {'N':>6s} | {'Quit':>5s} | {'%Quit':>6s} | {'Stay':>5s} | {'%Stay':>6s}")
print("-" * 80)
for inc in inc_order:
    for phat in phat_order:
        cell = df_heat[(df_heat[income_col].astype(str) == inc) & (df_heat['phat_label'] == phat)]
        n = len(cell)
        if n < 5:
            continue
        quit_n = cell['intent_risk'].str.contains('Muốn nghỉ').sum()
        stay_n = cell['intent_risk'].str.contains('Gắn bó').sum()
        quit_pct = quit_n / n * 100
        stay_pct = stay_n / n * 100
        flag = "  SUSPICIOUS" if (quit_pct < 5 and phat in ['1 - 3tr', '3 - 5tr', '> 5tr'] and inc in ['< 5 triệu', '5 - 7 triệu']) else ""
        print(f"{inc:<18s} | {phat:<12s} | {n:6d} | {quit_n:5d} | {quit_pct:5.1f}% | {stay_n:5d} | {stay_pct:5.1f}%{flag}")
    print("-" * 80)

# Check if income_group bins match actual income values
print(f"\n=== INCOME SANITY CHECK ===")
for inc in inc_order:
    subset = df_m[df_m[income_col].astype(str) == inc]
    if len(subset) > 0:
        print(f"{inc:<18s} | N={len(subset):5d} | income_m: mean={subset['income_m'].mean():.2f}, min={subset['income_m'].min():.2f}, max={subset['income_m'].max():.2f}")

# Check: Do people with HIGH penalty AND LOW income actually exist?
print(f"\n=== HIGH PENALTY + LOW INCOME DEEP CHECK ===")
extreme = df_m[(df_m['income_m'] < 5) & (df_m['tong_phat'] >= 1)]
print(f"N (income < 5tr AND penalty >= 1tr): {len(extreme)}")
if len(extreme) > 0:
    print(f"Intent distribution:\n{extreme['intent_risk'].value_counts()}")
    print(f"income_m: {extreme['income_m'].describe()}")
    print(f"tong_phat: {extreme['tong_phat'].describe()}")
    # Is tong_phat maybe already in wrong units?
    print(f"\nSample rows (income_m, tong_phat, Phạt raw, intent):")
    cols_show = ['income_m', 'tong_phat', 'intent_risk']
    if 'Phạt' in extreme.columns:
        cols_show.insert(2, 'Phạt')
    print(extreme[cols_show].head(15).to_string())
