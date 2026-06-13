"""
Script kiểm tra sự khớp giữa KPI trên dashboard và báo cáo DeepDive v13.
Chạy: python scripts/audit_kpis.py
"""
import pandas as pd
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
from utils.data_loader import compute_kpis, load_group

# --- SỐ LIỆU TRONG BÁO CÁO DEEPDIVE v13 ---
REPORT_METRICS = {
    "1A": {"EI": 73.5, "eNPS": 31.8, "Stay": 4.01, "Leave": 5.3, "MEI": 81.7, "Silence": 58.8, "FlightRisk": 5.5},
    "1B": {"EI": 75.9, "eNPS": 47.8, "Stay": 4.24, "Leave": 2.1, "MEI": 83.7, "Silence": 61.7, "FlightRisk": 2.3},
    "2A": {"EI": 72.4, "eNPS": 28.5, "Stay": 4.05, "Leave": 3.4, "MEI": 78.8, "Silence": 10.4, "FlightRisk": 3.8},
    "2B": {"EI": 78.9, "eNPS": 59.6, "Stay": 4.36, "Leave": 2.7, "MEI": 89.1, "Silence": 4.9,  "FlightRisk": 3.3},
    "3A": {"EI": 71.5, "eNPS": 16.3, "Stay": 4.01, "Leave": 4.0, "MEI": 81.8, "Silence": 6.2,  "FlightRisk": 4.0},
    "3B": {"EI": 73.6, "eNPS": 32.7, "Stay": 4.27, "Leave": 0.9, "MEI": 79.7, "Silence": 9.2,  "FlightRisk": 0.9},
    "Total": {"EI": 73.4, "eNPS": 31.7, "Stay": 4.04, "Leave": 4.57, "MEI": 81.3, "Silence": 43.1, "EffN": 16424}
}

print("=" * 80)
print("AUDIT: KPI DASHBOARD vs BÁO CÁO DEEPDIVE v13")
print("=" * 80)
print()

groups = ['1A', '1B', '2A', '2B', '3A', '3B']
all_dfs = []
results = {}

for g in groups:
    try:
        df, n_before = load_group(g)  # uppercase: '1A', '1B', etc.
        all_dfs.append(df)
        kpis = compute_kpis(df)
        results[g] = {
            "n": len(df),
            "n_before": n_before,
            "EI": kpis.get("ei_mean", 0),
            "eNPS": kpis.get("enps_score", 0),
            "Stay": kpis.get("stay_intent_mean", 0),
            "Leave": kpis.get("intent_pct_low", 0),
            "MEI": kpis.get("mei_mean", 0),
            "Silence": kpis.get("silence_rate", 0),
            "FlightRisk": kpis.get("flight_risk_pct", 0),
            "EffN": kpis.get("effective_n", 0),
        }
    except Exception as e:
        print(f"LOI khi load nhom {g}: {e}")
        results[g] = {}

# Tính tổng
if all_dfs:
    df_all = pd.concat(all_dfs, ignore_index=True)
    kpis_all = compute_kpis(df_all)
    results["Total"] = {
        "EI": kpis_all.get("ei_mean", 0),
        "eNPS": kpis_all.get("enps_score", 0),
        "Stay": kpis_all.get("stay_intent_mean", 0),
        "Leave": kpis_all.get("intent_pct_low", 0),
        "MEI": kpis_all.get("mei_mean", 0),
        "Silence": kpis_all.get("silence_rate", 0),
        "EffN": kpis_all.get("effective_n", 0),
    }

# In kết quả so sánh
header = f"{'Nhóm':<8} {'Chỉ số':<12} {'Dashboard':>12} {'Báo cáo':>12} {'Chênh lệch':>12} {'Trạng thái':<12}"
print(header)
print("-" * len(header))

TOLERANCE = {"EI": 0.5, "eNPS": 1.0, "Stay": 0.05, "Leave": 0.5, "MEI": 1.0, "Silence": 2.0, "FlightRisk": 0.5}

all_checks = []
for group in list(groups) + ["Total"]:
    if group not in results or not results[group]:
        continue
    report = REPORT_METRICS.get(group, {})
    dash = results[group]
    
    metrics_to_check = ["EI", "eNPS", "Stay", "Leave", "MEI", "Silence"]
    if group != "Total":
        metrics_to_check.append("FlightRisk")
    else:
        metrics_to_check.append("EffN")

    for metric in metrics_to_check:
        if metric not in dash or metric not in report:
            continue
        dash_val = dash[metric]
        rep_val = report[metric]
        diff = dash_val - rep_val
        tol = TOLERANCE.get(metric, 1.0)
        ok = abs(diff) <= tol
        status = "✅ OK" if ok else "❌ LỆCH"
        print(f"{group:<8} {metric:<12} {dash_val:>12.2f} {rep_val:>12.2f} {diff:>+12.2f}  {status}")
        all_checks.append((group, metric, ok, diff))

print()
print("=" * 80)
n_ok = sum(1 for _, _, ok, _ in all_checks if ok)
n_fail = sum(1 for _, _, ok, _ in all_checks if not ok)
print(f"TỔNG KẾT: {n_ok}/{len(all_checks)} chỉ số khớp, {n_fail} chỉ số cần xem xét")

if n_fail > 0:
    print()
    print("CÁC CHỈ SỐ CẦN XEM LẠI:")
    for group, metric, ok, diff in all_checks:
        if not ok:
            dash_val = results[group].get(metric, "N/A")
            rep_val = REPORT_METRICS.get(group, {}).get(metric, "N/A")
            print(f"  [{group}] {metric}: Dashboard={dash_val:.2f}, Báo cáo={rep_val}, Chênh={diff:+.2f}")
