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
        'file': 'EES-2026-1A (Mapped).xlsx',
        'sheet': 'Mapped Data',
        'codebook': CODEBOOK_1A,
        'hris_file': 'EX-2026_Chi tiet thu nhap NVPTTT total_update 28.04.xlsx',
        'color': '#FF5200',
    },
    '1B': {
        'label': 'Nhóm 1B — Tài xế GXT/TXXT',
        'short': 'Tài xế',
        'file': 'EES-2026-1B (Mapped).xlsx',
        'sheet': 'Mapped Data',
        'codebook': CODEBOOK_1B,
        'hris_file': None,
        'color': '#006FAD',
    },
    '2A': {
        'label': 'Nhóm 2A — Nhân viên Kho/TTTC',
        'short': 'Kho 2A',
        'file': 'EES-2026-Final-2A (Responses).xlsx',
        'sheet': 'Form Responses 1',
        'codebook': CODEBOOK_2A,
        'hris_file': None,
        'color': '#10B981',
    },
    '2B': {
        'label': 'Nhóm 2B — Nhân viên Bưu cục',
        'short': 'BC 2B',
        'file': 'EES-2026-Final-2B (Responses).xlsx',
        'sheet': 'Form Responses 1',
        'codebook': CODEBOOK_2B,
        'hris_file': None,
        'color': '#8B5CF6',
    },
    '3A': {
        'label': 'Nhóm 3A — Back Office (BO)',
        'short': 'BO 3A',
        'file': 'EES-2026-Final-3A (Responses).xlsx',
        'sheet': 'Form Responses 1',
        'codebook': CODEBOOK_3A,
        'hris_file': None,
        'color': '#F59E0B',
    },
    '3B': {
        'label': 'Nhóm 3B — Quản lý / Lãnh đạo',
        'short': 'QL 3B',
        'file': 'EES-2026-Final-3B (Responses).xlsx',
        'sheet': 'Form Responses 1',
        'codebook': CODEBOOK_3B,
        'hris_file': None,
        'color': '#EF4444',
    },
}

def get_available_groups():
    """Return groups that have data files on disk."""
    data_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'Data'))
    available = {}
    for gid, cfg in GROUP_REGISTRY.items():
        fpath = os.path.join(data_dir, cfg['file'])
        if os.path.exists(fpath):
            available[gid] = cfg
    return available
