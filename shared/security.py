"""
Security utilities — EES 2026
Hash ID nhân viên để join với HRIS (bảo mật).
"""
import hashlib
import pandas as pd


def hash_id(val):
    if pd.isna(val):
        return None
    try:
        return hashlib.sha256(str(int(val)).encode()).hexdigest()
    except (ValueError, TypeError):
        return hashlib.sha256(str(val).encode()).hexdigest()
