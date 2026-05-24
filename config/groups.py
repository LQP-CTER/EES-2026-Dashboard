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

GROUP_REGISTRY = {
    '1A': {
        'label': 'Nhóm 1A — Shipper / NVPTTT',
        'short': 'Shipper',
        'url': 'https://docs.google.com/spreadsheets/d/1300S7vaEgY20_3LXv4WxooygZoX4DtUYGuTw8yIVeG0/export?format=csv',
        'codebook': CODEBOOK_1A,
        'hris_file': 'EX-2026_Chi tiet thu nhap NVPTTT total_update 28.04.xlsx',
        'color': '#FF5200',
    },
    '1B': {
        'label': 'Nhóm 1B — Tài xế GXT/TXXT',
        'short': 'Tài xế',
        'url': 'https://docs.google.com/spreadsheets/d/1Cb_92qG_ocWGQFzNytPIvu8zNBugJvuNlkEZADZILIU/export?format=csv',
        'codebook': CODEBOOK_1B,
        'hris_file': None,
        'color': '#006FAD',
    },
    '2A': {
        'label': 'Nhóm 2A — Nhân viên Kho/TTTC',
        'short': 'Kho 2A',
        'url': 'https://docs.google.com/spreadsheets/d/1T3Ct9m-ls2BsUs5hmqVbKnRsHuuoyk8eAwPaJ5i0GgI/export?format=csv',
        'codebook': CODEBOOK_2A,
        'hris_file': None,
        'color': '#10B981',
    },
    '2B': {
        'label': 'Nhóm 2B — Nhân viên Bưu cục',
        'short': 'BC 2B',
        'url': 'https://docs.google.com/spreadsheets/d/1ZiH3s13f5NPGaBWzLK1DjErJFNCNG-oICaPVnDBPPpg/export?format=csv',
        'codebook': CODEBOOK_2B,
        'hris_file': None,
        'color': '#8B5CF6',
    },
    '3A': {
        'label': 'Nhóm 3A — Back Office (BO)',
        'short': 'BO 3A',
        'url': 'https://docs.google.com/spreadsheets/d/1QwJP-3bYP94n_5qMPZxn6PAz3y7pAEb1J8mdBZCqHb4/export?format=csv',
        'codebook': CODEBOOK_3A,
        'hris_file': None,
        'color': '#F59E0B',
    },
    '3B': {
        'label': 'Nhóm 3B — Quản lý / Lãnh đạo',
        'short': 'Manager 3B',
        'url': 'https://docs.google.com/spreadsheets/d/1bAML12n1WOn6HQMxF0373_NL-4KBon66uZuQFbSG_sc/export?format=csv',
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
