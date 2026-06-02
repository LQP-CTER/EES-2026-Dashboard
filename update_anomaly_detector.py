with open('extracted_code.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

def get_block(n):
    start = -1
    end = -1
    for i, l in enumerate(lines):
        if l.startswith(f'# BLOCK {n}'):
            start = i + 1
        elif start != -1 and l.startswith(f'# BLOCK {n+1}'):
            end = i
            break
    if end == -1: end = len(lines)
    return ''.join(lines[start:end])

b4 = get_block(4)
b5 = get_block(5)

new_content = '''"""
ANOMALY DETECTOR — EES 2026 Dashboard (v3.0)
"""
import pandas as pd
import numpy as np

from shared.codebook import get_role_question, get_pillar_questions
from shared.codebook import EWS_TENURE_THRESHOLD, TENURE_MAP, TENURE_LABELS

def _safe_mean(series):
    vals = series.dropna()
    return vals.mean() if len(vals) >= 5 else None

def _q(df, col):
    if col in df.columns: return df[col]
    return None

def _qmean(df, col):
    q = _q(df, col)
    return _safe_mean(q) if q is not None else None

def _role_mean(df, group_id, role):
    qid = get_role_question(group_id, role)
    if qid is None: return None, None
    return qid, _qmean(df, qid)

def _pillar_pct(df, pillar_id):
    col = f'{pillar_id}_pct'
    if col in df.columns: return df[col].mean()
    return None

''' + b4 + '\n' + b5 + '''

# ─────────────────────────────────────────────────────────────
# MAIN DISPATCHER
# ─────────────────────────────────────────────────────────────

PILLAR_DETECTORS = {
    'TC1': detect_TC1,
    'TC2': detect_TC2,
    'TC3': detect_TC3,
    'TC4': detect_TC4,
    'TC5': detect_TC5,
}

def detect_pillar_anomalies(df, group_id, pillar_id):
    detector = PILLAR_DETECTORS.get(pillar_id)
    if detector is None or df is None or df.empty:
        return []
    try:
        return detector(df, group_id)
    except Exception as e:
        return [{'id': 'ERROR', 'pillar': pillar_id, 'severity': 'watch',
                 'title': 'Lỗi phân tích', 'message': str(e), 'data': {}, 'action': ''}]

def detect_cross_pillar(df, group_id=''):
    return detect_cross_pillar_patterns(df, group_id)

def detect_all_anomalies(df, group_id):
    all_anomalies = []
    for pid in ['TC1', 'TC2', 'TC3', 'TC4', 'TC5']:
        all_anomalies.extend(detect_pillar_anomalies(df, group_id, pid))
    all_anomalies.extend(detect_cross_pillar(df, group_id))
    order = {'critical': 0, 'warning': 1, 'watch': 2}
    return sorted(all_anomalies, key=lambda x: order.get(x.get('severity', 'watch'), 3))
'''

with open('utils/anomaly_detector.py', 'w', encoding='utf-8') as f:
    f.write(new_content)
print('Updated anomaly_detector.py')
