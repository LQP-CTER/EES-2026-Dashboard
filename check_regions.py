import pandas as pd
from utils.data_loader import load_group, compute_kpis

df_1a, _ = load_group('1A')
for r in ['ĐCL', 'XBG']:
    d = df_1a[df_1a['Vùng'] == r]
    if len(d) > 0:
        k = compute_kpis(d)
        print(f"1A {r}: EI={k['ei_mean']}, MEI={k['mei_mean']}, FR={k['flight_risk_pct']}")

df_2b, _ = load_group('2B')
col_vung = 'Bạn thuộc Vùng nào?'
for r in ['ĐCL', 'HCM', 'DNB', 'TTB', 'DBB', 'TNG']:
    d = df_2b[df_2b[col_vung] == r]
    if len(d) > 0:
        k = compute_kpis(d)
        print(f"2B {r}: EI={k['ei_mean']}, MEI={k['mei_mean']}, FR={k['flight_risk_pct']}")
