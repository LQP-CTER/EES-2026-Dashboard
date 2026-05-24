"""
Group Registry — EES 2026
Mỗi nhóm khảo sát = 1 entry.
"""
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from shared.codebook import (
    CODEBOOK_1A, CODEBOOK_1B, 
    CODEBOOK_2A, CODEBOOK_2B, 
    CODEBOOK_3A, CODEBOOK_3B
)

import streamlit as st

def get_secret(key):
    try:
        return st.secrets.get(key, "")
    except Exception:
        import os
        return os.environ.get(key, "")

GROUP_REGISTRY = {
    '1A': {
        'label': 'Nhóm 1A — Shipper / NVPTTT',
        'short': 'Shipper',
        'url': get_secret('SHEET_1A'),
        'codebook': CODEBOOK_1A,
        'hris_file': 'EX-2026_Chi tiet thu nhap NVPTTT total_update 28.04.xlsx',
        'color': '#FF5200',
    },
    '1B': {
        'label': 'Nhóm 1B — Tài xế GXT/TXXT',
        'short': 'Tài xế',
        'url': get_secret('SHEET_1B'),
        'codebook': CODEBOOK_1B,
        'hris_file': None,
        'color': '#006FAD',
    },
    '2A': {
        'label': 'Nhóm 2A — Nhân viên Kho/TTTC',
        'short': 'Kho 2A',
        'url': get_secret('SHEET_2A'),
        'codebook': CODEBOOK_2A,
        'hris_file': None,
        'color': '#10B981',
    },
    '2B': {
        'label': 'Nhóm 2B — Nhân viên Bưu cục',
        'short': 'BC 2B',
        'url': get_secret('SHEET_2B'),
        'codebook': CODEBOOK_2B,
        'hris_file': None,
        'color': '#8B5CF6',
    },
    '3A': {
        'label': 'Nhóm 3A — Back Office (BO)',
        'short': 'BO 3A',
        'url': get_secret('SHEET_3A'),
        'codebook': CODEBOOK_3A,
        'hris_file': None,
        'color': '#F59E0B',
    },
    '3B': {
        'label': 'Nhóm 3B — Quản lý / Lãnh đạo',
        'short': 'Manager 3B',
        'url': get_secret('SHEET_3B'),
        'codebook': CODEBOOK_3B,
        'hris_file': None,
        'color': '#EF4444',
    }
}

def get_available_groups():
    """Return all groups from the registry since data is fetched from URLs."""
    available = {}
    for gid, cfg in GROUP_REGISTRY.items():
        if 'url' in cfg and cfg['url']:
            available[gid] = cfg
    return available
