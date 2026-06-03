"""Test Memo Cleaning trên từng nhóm."""
import sys
sys.path.insert(0, '.')

import warnings
warnings.filterwarnings('ignore')

from utils.data_loader import load_group
from utils.data_cleaning_memo import apply_memo_cleaning

GROUPS = ['1A', '1B', '2A', '2B', '3A', '3B']

# Kết quả mong đợi từ Memo
EXPECTED = {
    '1A': {'raw': 12955, 'n_effective': 9377, 'pct': 72.4},
    '1B': {'raw': 801,   'n_effective': 630,  'pct': 78.7},
    '2A': {'raw': 4892,  'n_effective': 3827, 'pct': 78.2},
    '2B': {'raw': 425,   'n_effective': 358,  'pct': 84.2},
    '3A': {'raw': 917,   'n_effective': 798,  'pct': 87.0},
    '3B': {'raw': 109,   'n_effective': 102,  'pct': 93.3},
}

print("="*80)
print("TEST MEMO CLEANING — So sánh với kết quả từ Memo")
print("="*80)

for gid in GROUPS:
    print(f"\n--- Nhóm {gid} ---")
    try:
        df, n_before = load_group(gid)
        if df is None or df.empty:
            print(f"  ❌ Failed to load")
            continue

        # Lấy report
        report = df.attrs.get('memo_report', {})
        n_eff = report.get('n_effective', 0)
        tier_counts = report.get('tier_counts', {})
        flags = report.get('flags', {})

        print(f"  Raw: {n_before:,}")
        print(f"  After dedup: {report.get('n_after_dedup', 0):,}")
        print(f"  Tiers: {tier_counts}")
        print(f"  n_effective: {n_eff:,.1f}")
        print(f"  Effective %: {report.get('effective_pct', 0)}%")
        print(f"  Expected: {EXPECTED[gid]['n_effective']:,} ({EXPECTED[gid]['pct']}%)")

        # Check columns
        new_cols = ['effective_weight', 'tier_v2', 'text_usable', 'longstring', 'maha_flag', 'contradiction', 'corroboration']
        missing = [c for c in new_cols if c not in df.columns]
        if missing:
            print(f"  ⚠ Missing columns: {missing}")
        else:
            print(f"  ✅ All memo columns present")

    except Exception as e:
        import traceback
        print(f"  ❌ Error: {e}")
        traceback.print_exc()
