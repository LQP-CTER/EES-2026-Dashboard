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
    # Try reading from Streamlit Secrets
    try:
        val = st.secrets.get(key, "")
        if val:
            return val
    except Exception:
        pass
    
    # Try reading from Environment Variables
    import os
    val = os.environ.get(key, "")
    if val:
        return val

    # Fallback to the consolidated Central Sheet ID if specific sheet is not specified
    try:
        central_id = st.secrets.get("CENTRAL_SHEET_ID", st.secrets.get("WF_SHEET_ID", "1wiv9c12jnSe7QFbqD-SHQo2tOWMD5My0pyE5JbmtYkU"))
    except Exception:
        central_id = os.environ.get("CENTRAL_SHEET_ID", os.environ.get("WF_SHEET_ID", "1wiv9c12jnSe7QFbqD-SHQo2tOWMD5My0pyE5JbmtYkU"))

    if not central_id:
        central_id = "1wiv9c12jnSe7QFbqD-SHQo2tOWMD5My0pyE5JbmtYkU"

    # Map keys to sheet tabs in the unified central Google Sheet
    sheet_map = {
        'SHEET_1A': '1A - Data',
        'SHEET_1B': '1B - Data',
        'SHEET_2A': '2A - Data',
        'SHEET_2B': '2B - Data',
        'SHEET_3A': '3A - Data',
        'SHEET_3B': '3B - Data'
    }
    
    if key in sheet_map:
        sheet_name_encoded = sheet_map[key].replace(' ', '%20')
        return f"https://docs.google.com/spreadsheets/d/{central_id}/gviz/tq?tqx=out:csv&sheet={sheet_name_encoded}"

    return ""

GROUP_REGISTRY = {
    '1A': {
        'label': 'Nhóm 1A — Nhân viên Giao nhận',
        'short': 'Nhân viên Giao nhận',
        'url': get_secret('SHEET_1A'),
        'codebook': CODEBOOK_1A,
        'hris_file': 'EX-2026_Chi tiet thu nhap NVPTTT total_update 28.04.xlsx',
        'color': '#FF5200',
    },
    '1B': {
        'label': 'Nhóm 1B — Tài xế xe tải',
        'short': 'Tài xế xe tải',
        'url': get_secret('SHEET_1B'),
        'codebook': CODEBOOK_1B,
        'hris_file': None,
        'color': '#006FAD',
    },
    '2A': {
        'label': 'Nhóm 2A — Nhân viên Vận hành Kho',
        'short': 'Nhân viên Vận hành Kho',
        'url': get_secret('SHEET_2A'),
        'codebook': CODEBOOK_2A,
        'hris_file': None,
        'color': '#10B981',
    },
    '2B': {
        'label': 'Nhóm 2B — Quản lý Vận hành Tuyến đầu',
        'short': 'Quản lý Vận hành Tuyến đầu',
        'url': get_secret('SHEET_2B'),
        'codebook': CODEBOOK_2B,
        'hris_file': None,
        'color': '#8B5CF6',
    },
    '3A': {
        'label': 'Nhóm 3A — Nhân viên Văn phòng',
        'short': 'Nhân viên Văn phòng',
        'url': get_secret('SHEET_3A'),
        'codebook': CODEBOOK_3A,
        'hris_file': None,
        'color': '#F59E0B',
    },
    '3B': {
        'label': 'Nhóm 3B — Quản lý HQ',
        'short': 'Quản lý HQ',
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
