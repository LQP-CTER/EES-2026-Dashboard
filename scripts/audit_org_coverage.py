"""Audit org coverage for the GHN overview page.

Run from project root:
    python scripts/audit_org_coverage.py

This script reads the six cleaned survey groups through the same loader used by
the dashboard, then reports how many Division/Department/Section segments exist
and how many are visible under the overview page threshold.
"""

import os
import sys

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, PROJECT_ROOT)

import pandas as pd

from utils.data_loader import load_all_available
from views.company_overview import MIN_ORG_SEGMENT_N, _normalize_org_columns


def _print_counts(df: pd.DataFrame, cols: list, title: str) -> None:
    if not all(c in df.columns for c in cols):
        missing = [c for c in cols if c not in df.columns]
        print(f"\n{title}: missing columns {missing}")
        return

    counts = (
        df.groupby(cols, dropna=False)
        .size()
        .reset_index(name="N")
        .sort_values(["N", *cols], ascending=[False, *([True] * len(cols))])
    )
    visible = counts[counts["N"] >= MIN_ORG_SEGMENT_N]
    hidden = counts[counts["N"] < MIN_ORG_SEGMENT_N]

    print(f"\n{title}")
    print("-" * 96)
    print(f"Total segments: {len(counts):,}")
    print(f"Visible N >= {MIN_ORG_SEGMENT_N}: {len(visible):,}")
    print(f"Hidden N < {MIN_ORG_SEGMENT_N}: {len(hidden):,}")

    if hidden.empty:
        return

    print("\nHidden small segments:")
    print(hidden.to_string(index=False, max_rows=80))


def main() -> None:
    all_data = load_all_available()
    if not all_data:
        raise RuntimeError("No survey data loaded.")

    frames = []
    print("Loaded groups")
    print("-" * 96)
    for group_id, (df, n_before) in all_data.items():
        df = df.copy()
        df["_survey_group"] = group_id
        frames.append(df)
        print(f"{group_id}: cleaned={len(df):,} raw={n_before:,}")

    df_total = _normalize_org_columns(pd.concat(frames, ignore_index=True))
    print(f"\nCombined cleaned rows: {len(df_total):,}")

    _print_counts(df_total, ["division"], "Division coverage")
    _print_counts(df_total, ["division", "department"], "Division + Department coverage")
    _print_counts(df_total, ["division", "department", "section"], "Division + Department + Section coverage")


if __name__ == "__main__":
    main()
