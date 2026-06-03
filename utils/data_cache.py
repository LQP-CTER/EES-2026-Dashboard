"""
Data Cache Manager — EES 2026
Local Parquet cache để tránh reload + reprocess dữ liệu mỗi lần.
"""
import os
import hashlib
import time
import pandas as pd
from pathlib import Path

CACHE_DIR = Path("data/cache")
CACHE_TTL = 86400 * 7  # 7 ngày


def _ensure_cache_dir():
    CACHE_DIR.mkdir(parents=True, exist_ok=True)


def _get_cache_path(group_id: str) -> Path:
    return CACHE_DIR / f"processed_{group_id}.parquet"


def _get_meta_path(group_id: str) -> Path:
    return CACHE_DIR / f"meta_{group_id}.json"


def get_cache_info(group_id: str) -> dict:
    """Trả về thông tin cache: exists, age, valid."""
    cache_path = _get_cache_path(group_id)
    meta_path = _get_meta_path(group_id)
    
    if not cache_path.exists():
        return {'exists': False, 'valid': False, 'age_hours': None}
    
    age_seconds = time.time() - cache_path.stat().st_mtime
    age_hours = age_seconds / 3600
    valid = age_seconds < CACHE_TTL
    
    return {
        'exists': True,
        'valid': valid,
        'age_hours': round(age_hours, 1),
        'path': cache_path
    }


def load_from_cache(group_id: str) -> tuple:
    """Load processed data từ cache. Returns (df, n_before) or None."""
    cache_path = _get_cache_path(group_id)
    
    if not cache_path.exists():
        return None
    
    try:
        df = pd.read_parquet(cache_path)
        
        # Restore attrs từ metadata columns
        n_before = int(df.attrs.get('n_before', len(df)))
        group_id_attr = df.attrs.get('group_id', group_id)
        
        # Restore open_cols
        open_cols = [c for c in ['C24_clean', 'C25_clean', 'C26_clean'] if c in df.columns]
        df.attrs['open_cols'] = [c.replace('_clean', '') for c in open_cols]
        df.attrs['group_id'] = group_id_attr
        df.attrs['n_before'] = n_before
        
        return df, n_before
    except Exception as e:
        print(f"  ⚠ Cache corrupted for {group_id}: {e}")
        return None


def save_to_cache(group_id: str, df: pd.DataFrame, n_before: int):
    """Save processed data to cache."""
    _ensure_cache_dir()
    cache_path = _get_cache_path(group_id)
    
    # Store metadata in attrs
    df.attrs['n_before'] = n_before
    df.attrs['group_id'] = group_id
    
    try:
        df.to_parquet(cache_path, index=False)
        print(f"  💾 Đã cache {len(df):,} rows → {cache_path.name}")
    except Exception as e:
        print(f"  ⚠ Không lưu cache được: {e}")


def invalidate_cache(group_id: str = None):
    """Xóa cache cho 1 nhóm hoặc tất cả."""
    if group_id:
        cache_path = _get_cache_path(group_id)
        if cache_path.exists():
            cache_path.unlink()
            print(f"  🗑️ Đã xóa cache: {group_id}")
    else:
        _ensure_cache_dir()
        for f in CACHE_DIR.glob("*.parquet"):
            f.unlink()
        print(f"  🗑️ Đã xóa toàn bộ cache")
