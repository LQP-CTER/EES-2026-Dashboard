"""
Anomaly Detector — EES 2026 Dashboard
Phát hiện các pattern bất thường ở cấp đơn vị (section/department).
"""
import pandas as pd
import numpy as np


# ─────────────────────────────────────────────
# Pattern definitions (no icons, clean labels)
# ─────────────────────────────────────────────
PATTERNS = {
    'committed_pressure': {
        'label':  'Áp lực không lối thoát',
        'color':  '#7C3AED',  # tím
        'bg':     '#F5F3FF',
        'desc':   (
            'Nhân viên chịu áp lực cao nhưng gắn bó vì lý do khác (quản lý tốt, '
            'văn hóa nhóm, tính chất công việc). Cần giảm tải khối lượng công việc '
            'sớm — nhóm này có thể chuyển sang "muốn nghỉ" đột ngột khi áp lực vượt ngưỡng.'
        ),
    },
    'flight_risk': {
        'label':  'Nguy cơ nghỉ hàng loạt',
        'color':  '#DC2626',  # đỏ
        'bg':     '#FEF2F2',
        'desc':   (
            'Tỉ lệ nhân viên có ý định rời khỏi tổ chức cao. Cần ưu tiên phỏng vấn '
            'giữ chân (Retention Interview) và rà soát nguyên nhân cốt lõi — lương, '
            'cơ hội phát triển, hoặc chất lượng quản lý.'
        ),
    },
    'silent_disengaged': {
        'label':  'Buông xuôi thầm lặng',
        'color':  '#EA580C',  # cam
        'bg':     '#FFF7ED',
        'desc':   (
            'EI thấp nhưng không có dấu hiệu muốn nghỉ — nhân viên đã "buông xuôi", '
            'không còn nỗ lực nhưng vẫn ở lại. Đây là dạng Quiet Quitting nguy hiểm '
            'vì ảnh hưởng đến năng suất và văn hóa nhưng không nhìn thấy trong chỉ số nghỉ việc.'
        ),
    },
    'manager_island': {
        'label':  'Quản lý tốt — Tổ chức yếu',
        'color':  '#B45309',  # vàng nâu
        'bg':     '#FEFCE8',
        'desc':   (
            'Quản lý trực tiếp được đánh giá cao nhưng điểm gắn kết tổ chức thấp. '
            'Nhân viên hài lòng với cấp trên nhưng không tin tưởng vào định hướng '
            'chiến lược, chính sách đãi ngộ hoặc văn hóa công ty.'
        ),
    },
    'data_reliability': {
        'label':  'Cảnh báo độ tin cậy dữ liệu',
        'color':  '#64748B',  # xám
        'bg':     '#F8FAFC',
        'desc':   (
            'Tỉ lệ straight-lining cao — nhiều người đánh cùng một điểm cho tất cả '
            'câu hỏi. Các chỉ số của đơn vị này cần được diễn giải thận trọng vì '
            'dữ liệu có thể không phản ánh đúng thực tế.'
        ),
    },
    'high_performer': {
        'label':  'Đơn vị xuất sắc',
        'color':  '#15803D',  # xanh lá
        'bg':     '#F0FDF4',
        'desc':   (
            'Đơn vị có sức khỏe tổ chức tốt — EI cao, burnout thấp và ít người muốn '
            'nghỉ. Đây là benchmarking unit: nên tìm hiểu và nhân rộng các thực hành '
            'quản lý tốt từ đơn vị này sang các bộ phận khác.'
        ),
    },
}


def _sl_pct(df_unit):
    """Tỉ lệ straight-liner còn trong mẫu."""
    if 'flag_straightline' in df_unit.columns:
        return df_unit['flag_straightline'].mean() * 100
    return 0.0


def detect_unit_anomalies(df_unit, min_n: int = 15) -> list[dict]:
    """
    Phát hiện các pattern bất thường cho 1 đơn vị.
    Trả về list[dict] với các key: id, label, color, bg, desc, metrics
    """
    n = len(df_unit)
    if n < min_n:
        return []

    results = []

    # ── Tính toán metrics ──
    ei = df_unit['EI'].mean() if 'EI' in df_unit.columns else None

    intent_col = df_unit.get('intent', pd.Series(dtype=float))
    n_valid_i = intent_col.notna().sum()
    quit_pct = (intent_col <= 2).sum() / n_valid_i * 100 if n_valid_i > 0 else None

    burnout_pct = None
    if 'burnout_risk' in df_unit.columns:
        n_b = df_unit['burnout_risk'].notna().sum()
        burnout_pct = (df_unit['burnout_risk'] > 0).sum() / n_b * 100 if n_b > 0 else 0

    mei_avg = df_unit['MEI'].mean() if 'MEI' in df_unit.columns else None
    sl_pct = _sl_pct(df_unit)

    # ── Áp dụng rules ──

    # 1. Committed Under Pressure
    if burnout_pct is not None and quit_pct is not None:
        if burnout_pct > 12 and quit_pct < 5:
            results.append(_make(
                'committed_pressure',
                metrics={
                    'Burnout': f'{burnout_pct:.1f}%',
                    'Muốn nghỉ': f'{quit_pct:.1f}%',
                    'MEI': f'{mei_avg:.1f}%' if mei_avg else 'N/A',
                }
            ))

    # 2. Flight Risk
    if quit_pct is not None and quit_pct > 20:
        results.append(_make(
            'flight_risk',
            metrics={
                'Muốn nghỉ': f'{quit_pct:.1f}%',
                'EI': f'{ei:.1f}%' if ei else 'N/A',
                'eNPS': _enps_str(df_unit),
            }
        ))

    # 3. Silent Disengaged
    if ei is not None and quit_pct is not None:
        if ei < 55 and quit_pct < 5:
            results.append(_make(
                'silent_disengaged',
                metrics={
                    'EI': f'{ei:.1f}%',
                    'Muốn nghỉ': f'{quit_pct:.1f}%',
                }
            ))

    # 4. Manager Island
    if mei_avg is not None and ei is not None:
        if mei_avg > 80 and ei < 60:
            results.append(_make(
                'manager_island',
                metrics={
                    'MEI': f'{mei_avg:.1f}%',
                    'EI': f'{ei:.1f}%',
                }
            ))

    # 5. Data Reliability
    if sl_pct > 25:
        results.append(_make(
            'data_reliability',
            metrics={
                'Straight-line': f'{sl_pct:.1f}%',
                'N mẫu': str(n),
            }
        ))

    # 6. High Performer (positive)
    if ei is not None and burnout_pct is not None and quit_pct is not None:
        if ei >= 75 and burnout_pct < 10 and quit_pct < 8:
            results.append(_make(
                'high_performer',
                metrics={
                    'EI': f'{ei:.1f}%',
                    'Burnout': f'{burnout_pct:.1f}%',
                    'Muốn nghỉ': f'{quit_pct:.1f}%',
                }
            ))

    return results


def _make(pattern_id: str, metrics: dict) -> dict:
    p = PATTERNS[pattern_id]
    return {
        'id':      pattern_id,
        'label':   p['label'],
        'color':   p['color'],
        'bg':      p['bg'],
        'desc':    p['desc'],
        'metrics': metrics,
    }


def _enps_str(df_unit) -> str:
    if 'eNPS' not in df_unit.columns:
        return 'N/A'
    col = df_unit['eNPS'].dropna()
    if len(col) == 0:
        return 'N/A'
    pro = (col >= 9).sum()
    det = (col <= 6).sum()
    score = (pro - det) / len(col) * 100
    return f'{score:+.0f}'
