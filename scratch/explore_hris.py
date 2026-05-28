import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import pandas as pd
import streamlit as st

from utils.data_loader import load_hris, merge_survey_hris, load_group

df_hris, label = load_hris()
if df_hris is not None:
    print(f"HRIS period: {label}")
    print(f"HRIS shape: {df_hris.shape}")
    print(f"\n=== ALL HRIS COLUMNS ===")
    for i, c in enumerate(df_hris.columns):
        dtype = df_hris[c].dtype
        n_valid = df_hris[c].notna().sum()
        sample = df_hris[c].dropna().head(3).tolist()
        print(f"  [{i:3d}] {c:50s} | dtype={str(dtype):10s} | valid={n_valid:5d} | sample={sample}")
    
    print(f"\n=== PRODUCTIVITY-RELATED COLUMNS ===")
    prod_keywords = ['đơn', 'giao', 'lấy', 'năng suất', 'tổng đơn', 'pickup', 'delivery', 'phân loại']
    for c in df_hris.columns:
        if any(kw in c.lower() for kw in prod_keywords):
            print(f"  {c}")
            print(f"    dtype: {df_hris[c].dtype}")
            print(f"    valid: {df_hris[c].notna().sum()}")
            print(f"    unique: {df_hris[c].nunique()}")
            if df_hris[c].dtype in ['float64', 'int64']:
                print(f"    mean: {df_hris[c].mean():.2f}, median: {df_hris[c].median():.2f}")
                print(f"    min: {df_hris[c].min()}, max: {df_hris[c].max()}")
            else:
                print(f"    value_counts:\n{df_hris[c].value_counts().head(10).to_string()}")
            print()
    
    # Also check survey Q4 (route fairness question)
    df_survey, _ = load_group('1A')
    print(f"\n=== SURVEY Q4 (route fairness) ===")
    q4_cols = [c for c in df_survey.columns if 'Q4' in str(c) or 'tuyến' in str(c).lower() or 'công bằng' in str(c).lower()]
    print(f"  Q4-related cols: {q4_cols}")
    
    # Check codebook for Q4
    from utils.data_loader import GROUPS
    cfg = GROUPS.get('1A', {})
    codebook = cfg.get('codebook', {})
    for q, info in codebook.items():
        if 'Q4' in q or 'tuyến' in str(info.get('tên', '')).lower() or 'phân' in str(info.get('tên', '')).lower():
            print(f"  {q}: {info}")
else:
    print("No HRIS data!")
