"""Audit dashboard KPI outputs against the analyst pack baselines.

Run from project root:
    python scripts/audit_dashboard_kpis.py

This script is diagnostic only. It does not modify data or upload anything.
"""

import os
import sys

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, PROJECT_ROOT)

from utils.data_loader import compute_kpis, load_group


ANALYST_BASELINE = {
    "1A": {"n": 12262, "ei_mean": 73.5, "enps_score": 31.8, "intent_pct_low": 5.5, "mei_avg": 81.7},
    "1B": {"n": 784, "ei_mean": 75.9, "enps_score": 47.8, "intent_pct_low": 2.1},
    "2A": {"n": 4819, "ei_mean": 72.4, "enps_score": 28.5, "intent_pct_low": 3.4, "mei_avg": 78.8},
    "2B": {"n": 425, "ei_mean": 78.9, "enps_score": 59.6, "intent_pct_low": 2.7, "mei_avg": 89.1},
    "3A": {"n": 822, "ei_mean": 71.5, "enps_score": 16.3, "intent_pct_low": 4.0, "mei_avg": 81.8},
    "3B": {"n": 109, "ei_mean": 73.6, "enps_score": 32.7, "intent_pct_low": 0.9},
}


def _fmt_delta(value, expected):
    if value is None or expected is None:
        return "n/a"
    delta = float(value) - float(expected)
    return f"{delta:+.1f}"


def main():
    print("EES 2026 Dashboard KPI Audit")
    print("=" * 96)
    header = f"{'Group':<5}{'Metric':<18}{'Dashboard':>14}{'Analyst':>14}{'Delta':>12}{'Status':>12}"
    print(header)
    print("-" * len(header))

    for gid, expected in ANALYST_BASELINE.items():
        try:
            df, _ = load_group(gid)
            kpis = compute_kpis(df)
        except Exception as exc:
            print(f"{gid:<5}{'LOAD_ERROR':<18}{str(exc)[:60]:>40}")
            continue

        for metric, baseline in expected.items():
            value = kpis.get(metric)
            if metric == "n":
                delta = int(value or 0) - int(baseline)
                ok = abs(delta) <= 0
                delta_text = f"{delta:+d}"
                value_text = f"{int(value or 0):,}"
                base_text = f"{int(baseline):,}"
            else:
                delta = float(value or 0) - float(baseline)
                ok = abs(delta) <= 0.3
                delta_text = _fmt_delta(value, baseline)
                value_text = f"{float(value or 0):.1f}"
                base_text = f"{float(baseline):.1f}"
            status = "OK" if ok else "CHECK"
            print(f"{gid:<5}{metric:<18}{value_text:>14}{base_text:>14}{delta_text:>12}{status:>12}")
        print("-" * len(header))


if __name__ == "__main__":
    main()

