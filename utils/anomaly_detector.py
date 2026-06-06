"""
ANOMALY DETECTOR — EES 2026 Dashboard
Core engine để phát hiện các pattern bất thường trong từng trụ cột và liên trụ cột.

Mỗi hàm trả về list[dict] với format:
{
    'id':       str,    # Mã pattern (TC1_A1, XP_1, v.v.)
    'pillar':   str,    # Trụ cột liên quan ('TC1'...'TC5' hoặc 'CROSS')
    'severity': str,    # 'critical' | 'warning' | 'watch'
    'title':    str,    # Tiêu đề ngắn
    'message':  str,    # Mô tả chi tiết
    'data':     dict,   # Dữ liệu thô hỗ trợ
    'action':   str,    # Đề xuất hành động trong 30 ngày
}
"""

import pandas as pd
import numpy as np

from shared.codebook import get_role_question, get_pillar_questions


# ─────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────

TENURE_EARLY = ['Dưới 1 tháng', 'Trên 1 đến 3 tháng', 'Trên 3 đến 6 tháng']
TENURE_SENIOR = ['Trên 2 đến 3 năm', 'Trên 3 đến 5 năm', 'Trên 5 năm']
EWS_TENURE_THRESHOLD = {'1A': 1, '1B': 1, '2A': 2, '2B': 2, '3A': 2, '3B': 2}
TENURE_MONTH_MAP = {
    0: 0.5, 1: 2, 2: 4.5, 3: 7.5, 4: 10.5,
    5: 18, 6: 30, 7: 48, 8: 72,
}


def _safe_mean(series):
    vals = series.dropna()
    return vals.mean() if len(vals) >= 5 else None


def _q(df, col):
    """Safe column access — returns None if column missing."""
    if col in df.columns:
        return df[col]
    return None


def _qmean(df, col):
    q = _q(df, col)
    return _safe_mean(q) if q is not None else None


def _role_mean(df, group_id, role):
    """Trả về điểm TB của câu đóng vai trò `role` cho `group_id`.

    Cốt lõi của bản refactor: anomaly detector KHÔNG còn hard-code số câu
    theo layout 1A/1B. Mọi tham chiếu "câu công cụ", "câu thăng tiến",
    "câu thu nhập"... đều tra qua role → đúng cho cả 6 nhóm.
    """
    qid = get_role_question(group_id, role)
    if qid is None:
        return None, None
    return qid, _qmean(df, qid)


def _pillar_pct(df, pillar_id):
    col = f'{pillar_id}_pct'
    if col in df.columns:
        return df[col].mean()
    return None


def _flight_risk_pct(df):
    if 'intent' not in df.columns:
        return None
    valid = df['intent'].dropna()
    return (valid <= 2).sum() / len(valid) * 100 if len(valid) > 0 else None


def _burnout_pct(df):
    if 'burnout_proxy' in df.columns:
        valid = df['burnout_proxy'].dropna()
        return valid.astype(bool).sum() / len(valid) * 100 if len(valid) > 0 else None
    if 'burnout_score' in df.columns:
        valid = df['burnout_score'].dropna()
        return (valid >= 50).sum() / len(valid) * 100 if len(valid) > 0 else None
    if 'burnout_risk' in df.columns:
        valid = df['burnout_risk'].dropna()
        return (valid > 0).sum() / len(valid) * 100 if len(valid) > 0 else None
    return None


def _infer_gen3(series):
    """Infer Gen X/Y/Z from either label text or birth year values."""
    def _one(v):
        if pd.isna(v):
            return None
        text = str(v).strip().lower()
        if 'gen x' in text or 'trước 1980' in text:
            return 'Gen X'
        if 'gen z' in text or '1997' in text or '2001' in text:
            return 'Gen Z'
        if 'gen y' in text or '1981' in text or '1990' in text:
            return 'Gen Y'
        try:
            year = int(float(text[:4]))
            if year < 1981:
                return 'Gen X'
            if year >= 1997:
                return 'Gen Z'
            return 'Gen Y'
        except Exception:
            return None
    return series.apply(_one)


def _severity_badge(s):
    return {'critical': 'Khẩn cấp', 'warning': 'Cảnh báo', 'watch': 'Theo dõi'}.get(s, s)


# ─────────────────────────────────────────────────────────────
# TC1 — NIỀM TIN & ĐỊNH HƯỚNG
# ─────────────────────────────────────────────────────────────

def detect_TC1(df, group_id=''):
    anomalies = []
    trust_q, q9  = _role_mean(df, group_id, 'info_trust')   # vd Q9
    timely_q, q10 = _role_mean(df, group_id, 'info_timely')  # vd Q10
    ei  = df['EI'].mean() if 'EI' in df.columns else None
    tc1 = _pillar_pct(df, 'TC1')
    intent_pct = None
    if 'intent' in df.columns:
        valid = df['intent'].dropna()
        intent_pct = (valid <= 2).sum() / len(valid) * 100 if len(valid) > 0 else None

    # TC1_A1: Mất niềm tin cục bộ
    if tc1 is not None and tc1 < 55:
        anomalies.append({
            'id': 'TC1_A1', 'pillar': 'TC1', 'severity': 'critical',
            'title': 'Mất niềm tin vào tổ chức',
            'message': f'Điểm TC1 chỉ đạt {tc1:.1f}% — thấp hơn ngưỡng an toàn (55%). Nhân viên đang mất niềm tin vào định hướng và chiến lược của GHN.',
            'data': {'TC1_pct': round(tc1, 1), 'EI': round(ei, 1) if ei else None},
            'action': 'Tổ chức Town Hall trong vòng 30 ngày — BLĐ chia sẻ trực tiếp chiến lược và giải đáp thắc mắc. Ưu tiên vùng/đơn vị có điểm TC1 thấp nhất.'
        })

    # TC1_A2: Thông tin đứt gãy
    if q9 is not None and q10 is not None and (q9 - q10) > 0.45:
        anomalies.append({
            'id': 'TC1_A2', 'pillar': 'TC1', 'severity': 'warning',
            'title': 'Thông tin bị đứt gãy giữa cấp quản lý và nhân viên',
            'message': (
                f'Nhân viên TIN vào định hướng GHN (Q9={q9:.2f}/5) nhưng KHÔNG NHẬN ĐƯỢC thông tin kịp thời (Q10={q10:.2f}/5). '
                f'Khoảng cách {q9-q10:.2f} điểm cho thấy kênh truyền thông nội bộ đang có vấn đề, không phải niềm tin.'
            ),
            'data': {'Q9_tin_BLD': round(q9, 2), 'Q10_thong_tin': round(q10, 2), 'gap': round(q9-q10, 2)},
            'action': 'Kiểm tra kênh thông báo: nhân viên đang nhận tin qua kênh nào? Thêm kênh trực tiếp (Zalo nhóm, bảng thông báo bưu cục) thay vì chỉ qua quản lý.'
        })

    # TC1_A3: Nghịch lý tin tưởng
    if tc1 is not None and tc1 > 72 and intent_pct is not None and intent_pct > 18:
        tc2 = _pillar_pct(df, 'TC2')
        tc4 = _pillar_pct(df, 'TC4')
        anomalies.append({
            'id': 'TC1_A3', 'pillar': 'TC1', 'severity': 'warning',
            'title': 'Nghịch lý: Tin BLĐ nhưng vẫn muốn nghỉ',
            'message': (
                f'TC1 cao ({tc1:.1f}%) nhưng {intent_pct:.1f}% muốn nghỉ. '
                f'Vấn đề KHÔNG nằm ở niềm tin — hãy kiểm tra TC2 ({tc2:.1f}% nếu có) và TC4 ({tc4:.1f}% nếu có).'
            ),
            'data': {'TC1_pct': round(tc1, 1), 'flight_risk_pct': round(intent_pct, 1)},
            'action': 'Drill-down vào TC2 (quản lý) và TC4 (thu nhập) — đó mới là nguyên nhân thực sự.'
        })

    return anomalies


# ─────────────────────────────────────────────────────────────
# TC2 — QUẢN LÝ TRỰC TIẾP
# ─────────────────────────────────────────────────────────────

def detect_TC2(df, group_id=''):
    anomalies = []
    tc2 = _pillar_pct(df, 'TC2')
    ei  = df['EI'].mean() if 'EI' in df.columns else None
    mei = df['MEI'].mean() if 'MEI' in df.columns else None
    support_q, q11 = _role_mean(df, group_id, 'mgr_support')   # 1A/1B: Q11 | 2A-3B: Q13
    fairness_q, q12 = _role_mean(df, group_id, 'mgr_fairness')  # 1A/1B: Q12 | 2A-3B: Q14
    feedback_q, q15 = _role_mean(df, group_id, 'mgr_feedback')  # 1A/1B: Q15 | 2A-3B: Q17
    intent_pct = None
    if 'intent' in df.columns:
        valid = df['intent'].dropna()
        intent_pct = (valid <= 2).sum() / len(valid) * 100 if len(valid) > 0 else None

    # TC2_A1: Manager Island
    if mei is not None and ei is not None and mei > 75 and ei < 62:
        anomalies.append({
            'id': 'TC2_A1', 'pillar': 'TC2', 'severity': 'warning',
            'title': 'Manager Island — Quản lý tốt nhưng tổ chức yếu',
            'message': (
                f'MEI (Hiệu quả Quản lý) = {mei:.1f}% rất tốt, nhưng EI tổng thể chỉ {ei:.1f}%. '
                f'Nhân viên hài lòng với quản lý trực tiếp nhưng KHÔNG hài lòng với tổ chức. '
                f'Nguyên nhân thường nằm ở TC1 (chiến lược mờ nhạt) hoặc TC4 (thu nhập thấp).'
            ),
            'data': {'MEI': round(mei, 1), 'EI': round(ei, 1)},
            'action': 'Giữ điểm mạnh ở TC2. Tập trung can thiệp vào trụ cột kéo EI xuống nhất — xem biểu đồ 5 trụ cột bên dưới.'
        })

    # TC2_A2: Phân biệt đối xử (phân đơn/lịch không công bằng)
    if q11 is not None and q12 is not None and (q11 - q12) > 0.55:
        anomalies.append({
            'id': 'TC2_A2', 'pillar': 'TC2', 'severity': 'warning',
            'title': 'Phân công không công bằng là vấn đề chính',
            'message': (
                f'Hỗ trợ từ quản lý ({support_q}={q11:.2f}) tốt hơn nhiều so với công bằng phân công ({fairness_q}={q12:.2f}). '
                f'Nhân viên cảm nhận quản lý HỖ TRỢ tốt nhưng PHÂN ĐƠN/LỊCH không công bằng. '
                f'Đây là ngòi nổ chính cho mâu thuẫn nội bộ và flight risk.'
            ),
            'data': {f'{support_q}_ho_tro': round(q11, 2), f'{fairness_q}_cong_bang': round(q12, 2), 'gap': round(q11-q12, 2)},
            'action': 'Audit quy trình phân đơn/phân lịch. Xem xét thuật toán có tạo ra bất công không (tuyến dài vs ngắn, khu vực dày vs thưa).'
        })

    # TC2_A3: Quản lý yếu toàn diện
    if tc2 is not None and tc2 < 52:
        anomalies.append({
            'id': 'TC2_A3', 'pillar': 'TC2', 'severity': 'critical',
            'title': 'Khủng hoảng quản lý — Yếu toàn diện',
            'message': (
                f'TC2 chỉ đạt {tc2:.1f}% — dưới ngưỡng nguy hiểm (52%). '
                f'TC2 là trụ cột có trọng số cao nhất (25%). Điểm yếu ở đây sẽ kéo EI toàn nhóm xuống và '
                f'tạo domino effect: quản lý yếu → nhân viên bất mãn → nghỉ việc hàng loạt.'
            ),
            'data': {'TC2_pct': round(tc2, 1)},
            'action': 'Manager Coaching khẩn cấp cho các quản lý ở đơn vị điểm thấp nhất. Xác định "best practice manager" trong cùng nhóm để nhân rộng.'
        })

    # TC2_A4: MEI shield thất bại
    if mei is not None and intent_pct is not None and mei > 72 and intent_pct > 15:
        anomalies.append({
            'id': 'TC2_A4', 'pillar': 'TC2', 'severity': 'warning',
            'title': 'MEI cao nhưng vẫn muốn nghỉ — Thu nhập đang override',
            'message': (
                f'MEI = {mei:.1f}% (quản lý tốt) nhưng {intent_pct:.1f}% nhân viên muốn nghỉ. '
                f'Thu nhập (TC4) hoặc điều kiện làm việc (TC3) đang "override" quản lý tốt. '
                f'Quản lý tốt là điều kiện cần nhưng CHƯA ĐỦ để giữ người.'
            ),
            'data': {'MEI': round(mei, 1), 'flight_risk_pct': round(intent_pct, 1)},
            'action': 'Kiểm tra TC4 và TC3 — đó mới là nguyên nhân khiến quản lý tốt cũng không giữ được người.'
        })

    # TC2_A5: Feedback một chiều
    if q15 is not None and feedback_q is not None:
        tc2_qs = [c for c in get_pillar_questions(group_id, 'TC2') if c in df.columns]
        means = {q: _qmean(df, q) for q in tc2_qs if _qmean(df, q) is not None}
        if means and q15 == min(means.values()) and q15 < 3.6:
            anomalies.append({
                'id': 'TC2_A5', 'pillar': 'TC2', 'severity': 'watch',
                'title': 'Phản hồi một chiều — Nhân viên không được lắng nghe',
                'message': (
                    f'Câu về phản hồi ({feedback_q}={q15:.2f}) là điểm thấp nhất trong TC2. '
                    f'Nhân viên có thể hoàn thành công việc nhưng không cảm thấy được lắng nghe và ghi nhận. '
                    f'Đây là dấu hiệu sớm của silent disengagement.'
                ),
                'data': {f'{feedback_q}_phan_hoi': round(q15, 2)},
                'action': 'Triển khai "weekly check-in 5 phút" — quản lý hỏi 2 câu: "Tuần này có vấn đề gì không?" và "Cần hỗ trợ gì?".'
            })

    return anomalies


# ─────────────────────────────────────────────────────────────
# TC3 — CÔNG VIỆC & ĐIỀU KIỆN VẬN HÀNH
# ─────────────────────────────────────────────────────────────

def detect_TC3(df, group_id=''):
    anomalies = []
    tool_q, q16 = _role_mean(df, group_id, 'tool')          # 1A/1B: Q16 | 2A-3B: Q18
    workload_q, q18 = _role_mean(df, group_id, 'workload')   # 1A/1B: Q18 | 2A-3B: Q21
    career_q, q19 = _role_mean(df, group_id, 'career')       # 1A/1B: Q19 | 2A-3B: Q21
    change_q, q20 = _role_mean(df, group_id, 'change_guide')  # 1A/1B: Q20 | 2A-3B: Q20
    timely_q, q10 = _role_mean(df, group_id, 'info_timely')   # TC1 — thông báo kịp thời

    burnout_pct = None
    if 'burnout_risk' in df.columns:
        valid = df['burnout_risk'].dropna()
        burnout_pct = (valid > 0).sum() / len(valid) * 100 if len(valid) > 0 else None

    # TC3_A1: Công cụ cản trở
    if q16 is not None and q16 < 3.5 and tool_q is not None:
        anomalies.append({
            'id': 'TC3_A1', 'pillar': 'TC3', 'severity': 'warning',
            'title': 'Công cụ/App đang cản trở công việc, không phải hỗ trợ',
            'message': (
                f'{tool_q} (App/thiết bị/công cụ) = {q16:.2f}/5 — dưới ngưỡng 3.5. '
                f'Công cụ kém không chỉ ảnh hưởng hiệu suất mà còn tạo ra frustration mỗi ngày, '
                f'tích lũy thành bất mãn tổng thể. Liên kết với HRIS: năng suất thực tế có bị ảnh hưởng không?'
            ),
            'data': {f'{tool_q}_cong_cu': round(q16, 2)},
            'action': 'Thu thập báo lỗi công cụ/thiết bị cụ thể từ nhân viên. Fix lỗi ưu tiên cao trong 2 tuần. Thông báo rõ roadmap cải thiện.'
        })

    # TC3_A2: Burnout ẩn
    if q18 is not None and burnout_pct is not None and q18 > 3.5 and burnout_pct > 28 and workload_q is not None:
        anomalies.append({
            'id': 'TC3_A2', 'pillar': 'TC3', 'severity': 'critical',
            'title': 'Burnout ẩn — Nhân viên không nhận ra mình đang kiệt sức',
            'message': (
                f'Nhân viên tự đánh giá cường độ ổn ({workload_q}={q18:.2f}) nhưng chỉ số Burnout thực tế lên tới {burnout_pct:.1f}%. '
                f'Đây là "burnout blind spot" — nguy hiểm vì không có dấu hiệu cảnh báo sớm từ chính nhân viên. '
                f'Flip point thường xảy ra đột ngột khi vượt qua ngưỡng chịu đựng.'
            ),
            'data': {f'{workload_q}_cuong_do': round(q18, 2), 'burnout_pct': round(burnout_pct, 1)},
            'action': 'Pulse check hàng tháng về tải công việc. Xem xét giảm KPI đơn vào mùa thấp điểm để tái nạp năng lượng cho nhân viên.'
        })

    # TC3_A3: Trần thủy tinh (Glass Ceiling)
    if q19 is not None and career_q is not None and 'Q5' in df.columns:
        senior_mask = df['Q5'].isin(TENURE_SENIOR)
        if senior_mask.sum() >= 10:
            senior_career = df.loc[senior_mask, career_q].dropna().mean()
            junior_mask = df['Q5'].isin(TENURE_EARLY)
            junior_career = df.loc[junior_mask, career_q].dropna().mean() if junior_mask.sum() >= 10 else None
            if senior_career < 3.2 and (junior_career is None or (junior_career - senior_career) > 0.3):
                anomalies.append({
                    'id': 'TC3_A3', 'pillar': 'TC3', 'severity': 'warning',
                    'title': 'Trần thủy tinh — Nhóm cựu binh không thấy con đường thăng tiến',
                    'message': (
                        f'Nhóm thâm niên > 2 năm đánh giá lộ trình thăng tiến chỉ {senior_career:.2f}/5. '
                        f'Đây là "trần thủy tinh" điển hình — nhân viên cũ ở lại vì quán tính, '
                        f'không vì kỳ vọng phát triển. Khi có cơ hội tốt hơn, họ sẽ ra đi ngay.'
                    ),
                    'data': {
                        'senior_career_score': round(senior_career, 2),
                        'junior_career_score': round(junior_career, 2) if junior_career else None,
                    },
                    'action': 'Công bố lộ trình thăng tiến rõ ràng với milestones cụ thể. Tổ chức Career Conversation 1-1 cho nhóm thâm niên > 12 tháng trong 30 ngày.'
                })

    # TC3_A4: Thay đổi không hướng dẫn + Thông tin kém
    if q20 is not None and q10 is not None and q20 < 3.4 and q10 < 3.5 and change_q is not None:
        anomalies.append({
            'id': 'TC3_A4', 'pillar': 'TC3', 'severity': 'warning',
            'title': 'Double Gap: Thay đổi không được thông báo VÀ không được hướng dẫn',
            'message': (
                f'TC1-{timely_q} (thông báo kịp thời) = {q10:.2f} thấp, kết hợp {change_q} (hướng dẫn khi thay đổi) = {q20:.2f} thấp. '
                f'Đây là "double gap": nhân viên không biết thay đổi sắp đến VÀ khi đến cũng không biết làm gì. '
                f'Gây ra lo lắng, sai sót và mất tin tưởng.'
            ),
            'data': {f'{timely_q}_thong_bao': round(q10, 2), f'{change_q}_huong_dan': round(q20, 2)},
            'action': 'Bất kỳ thay đổi quy trình nào cần kèm SOP rõ ràng. Triển khai "Change Communication Checklist": thông báo trước 7 ngày + hướng dẫn thực hành.'
        })

    return anomalies


# ─────────────────────────────────────────────────────────────
# TC4 — THU NHẬP & MINH BẠCH
# ─────────────────────────────────────────────────────────────

def detect_TC4(df, group_id=''):
    anomalies = []
    income_q, q21 = _role_mean(df, group_id, 'income_fair')        # 1A/1B: Q21 | 2A-3B: Q22
    transp_q, q22_tc4 = _role_mean(df, group_id, 'transparency')   # 1A/1B: Q22 | 2A-3B: Q23
    incident_q, q25 = _role_mean(df, group_id, 'incident_support')  # Q25 cho cả hai layout
    tc4 = _pillar_pct(df, 'TC4')

    intent_pct = None
    if 'intent' in df.columns:
        valid = df['intent'].dropna()
        intent_pct = (valid <= 2).sum() / len(valid) * 100 if len(valid) > 0 else None

    tc5 = _pillar_pct(df, 'TC5')

    # TC4_A1: Cảm nhận bất công (có thể do minh bạch, không phải mức lương)
    if q21 is not None and q21 < 3.4 and income_q is not None:
        anomalies.append({
            'id': 'TC4_A1', 'pillar': 'TC4', 'severity': 'warning',
            'title': 'Thu nhập bị cảm nhận là không công bằng',
            'message': (
                f'{income_q} (thu nhập phản ánh công sức) = {q21:.2f}/5. '
                f'Lưu ý: vấn đề có thể là MINH BẠCH, không phải mức lương. '
                f'Cần so sánh với dữ liệu HRIS: nếu thu nhập thực tế ổn mà {income_q} vẫn thấp → '
                f'nhân viên không hiểu cách tính, không phải lương thấp.'
            ),
            'data': {f'{income_q}_cong_bang': round(q21, 2)},
            'action': 'Tổ chức buổi giải thích "Lương của bạn được tính như thế nào" cho nhân viên TC4 thấp nhất. Đơn giản hóa cách trình bày thu nhập trên App.'
        })

    # TC4_A2: Phạt không minh bạch
    if q21 is not None and q22_tc4 is not None and (q21 - q22_tc4) > 0.45 and transp_q is not None:
        anomalies.append({
            'id': 'TC4_A2', 'pillar': 'TC4', 'severity': 'warning',
            'title': 'Phạt/Thu nhập hiển thị không rõ ràng',
            'message': (
                f'{income_q} (thu nhập công bằng) = {q21:.2f} vs {transp_q} (minh bạch cách tính/phạt) = {q22_tc4:.2f}. '
                f'Khoảng cách {q21-q22_tc4:.2f} điểm: nhân viên CHẤP NHẬN thu nhập nhưng không hiểu các khoản khấu trừ/phạt. '
                f'Sự mờ ám về phạt tạo ra cảm giác bị bất công dù mức lương ổn.'
            ),
            'data': {income_q: round(q21, 2), f'{transp_q}_minh_bach': round(q22_tc4, 2)},
            'action': 'Cải thiện UI màn hình thu nhập: tách rõ lương cơ bản / thưởng / phạt / khấu trừ thành từng dòng với giải thích đơn giản.'
        })

    # TC4_A3: Thu nhập ổn nhưng vẫn muốn nghỉ
    if tc4 is not None and tc4 > 68 and intent_pct is not None and intent_pct > 18:
        tc2 = _pillar_pct(df, 'TC2')
        anomalies.append({
            'id': 'TC4_A3', 'pillar': 'TC4', 'severity': 'warning',
            'title': 'Income Paradox — Thu nhập ổn nhưng vẫn muốn nghỉ',
            'message': (
                f'TC4 = {tc4:.1f}% (thu nhập ổn) nhưng {intent_pct:.1f}% muốn nghỉ. '
                f'Vấn đề KHÔNG phải tiền. Kiểm tra TC2 ({f"{tc2:.1f}%" if tc2 else "N/A"}) và TC5 — '
                f'quản lý kém hoặc văn hóa độc hại là nguyên nhân thực sự.'
            ),
            'data': {'TC4_pct': round(tc4, 1), 'flight_risk_pct': round(intent_pct, 1)},
            'action': 'Phỏng vấn 10 nhân viên muốn nghỉ — hỏi thẳng: "Nếu không phải vì lương, điều gì đang khiến bạn muốn đi?"'
        })

    # TC4_A4: Hỗ trợ sự cố kém
    if q25 is not None and incident_q is not None:
        tc4_qs = [c for c in get_pillar_questions(group_id, 'TC4') if c in df.columns]
        means = {q: _qmean(df, q) for q in tc4_qs if _qmean(df, q) is not None}
        if means and q25 <= min(means.values()) + 0.05 and q25 < 3.5:
            anomalies.append({
                'id': 'TC4_A5', 'pillar': 'TC4', 'severity': 'watch',
                'title': 'Hỗ trợ sự cố ảnh hưởng thu nhập — Điểm yếu nhất TC4',
                'message': (
                    f'{incident_q} (hỗ trợ sự cố ảnh hưởng thu nhập) = {q25:.2f} — thấp nhất trong TC4. '
                    f'Khi nhân viên gặp sự cố (giao hàng thất bại, mất hàng, tai nạn) mà không được hỗ trợ, '
                    f'thu nhập bị cắt và bất mãn bùng phát ngay lập tức.'
                ),
                'data': {f'{incident_q}_ho_tro_su_co': round(q25, 2)},
                'action': 'Thiết lập quy trình xử lý khiếu nại sự cố trong 24h. Nhân viên phải biết đầu mối liên hệ và timeline xử lý rõ ràng.'
            })

    return anomalies


# ─────────────────────────────────────────────────────────────
# TC5 — MÔI TRƯỜNG & SỰ GẮN KẾT
# ─────────────────────────────────────────────────────────────

def detect_TC5(df, group_id=''):
    anomalies = []
    peer_q, q27 = _role_mean(df, group_id, 'peer')        # 1A: Q27 | 1B: Q26 | 2A-3B: Q27
    pride_q, q28 = _role_mean(df, group_id, 'pride')       # 1A: Q28 | 1B: Q27 | 2A-3B: Q28
    pressure_q, q29 = _role_mean(df, group_id, 'pressure')  # 1A: Q29 | 1B: Q28 | 2A-3B: Q29
    ei = df['EI'].mean() if 'EI' in df.columns else None

    burnout_pct = _burnout_pct(df)
    intent_pct = _flight_risk_pct(df)

    # TC5_A1: Tự hào nhưng kiệt sức
    if q28 is not None and q29 is not None and q28 > 3.9 and q29 < 3.2 and pride_q and pressure_q:
        anomalies.append({
            'id': 'TC5_A1', 'pillar': 'TC5', 'severity': 'critical',
            'title': 'Tự hào nhưng đang kiệt sức — Sắp đến điểm bùng phát',
            'message': (
                f'Nhân viên tự hào về GHN ({pride_q}={q28:.2f}) nhưng áp lực đang xâm lấn cuộc sống ({pressure_q}={q29:.2f}). '
                f'Đây là pattern nguy hiểm nhất: yêu công ty NHƯNG không chịu nổi. '
                f'Khi vượt ngưỡng chịu đựng, họ sẽ nghỉ đột ngột và không thể giữ lại.'
            ),
            'data': {f'{pride_q}_tu_hao': round(q28, 2), f'{pressure_q}_ap_luc': round(q29, 2)},
            'action': 'Giảm tải ngay: xem xét KPI có hợp lý không. Triển khai "No-Deadline Friday" hoặc giờ nghỉ phép tăng thêm cho nhóm có áp lực cao nhất.'
        })

    # TC5_A2: Đồng nghiệp tốt, công ty tệ (Social Glue Risk)
    if q27 is not None and ei is not None and q27 > 4.0 and ei < 57 and peer_q:
        anomalies.append({
            'id': 'TC5_A2', 'pillar': 'TC5', 'severity': 'warning',
            'title': 'Social Glue Risk — Ở lại vì bạn bè, không vì tổ chức',
            'message': (
                f'Đồng nghiệp hỗ trợ tốt ({peer_q}={q27:.2f}) nhưng EI tổng thể thấp ({ei:.1f}%). '
                f'Nhân viên ở lại vì TẬP THỂ, không vì tổ chức. '
                f'Rủi ro: khi 1-2 người bạn thân nghỉ, cả nhóm có thể nghỉ theo (domino effect).'
            ),
            'data': {f'{peer_q}_dong_nghiep': round(q27, 2), 'EI': round(ei, 1)},
            'action': 'Theo dõi các đơn vị có turnover cao: khi 1 người nghỉ, pulse check ngay các đồng nghiệp thân thiết trong vòng 2 tuần.'
        })

    # TC5_A3: Burnout nghịch lý
    if q29 is not None and burnout_pct is not None and q29 > 3.8 and burnout_pct > 25 and pressure_q:
        anomalies.append({
            'id': 'TC5_A5', 'pillar': 'TC5', 'severity': 'critical',
            'title': 'Burnout Blind Spot — Nhân viên không nhận ra mình đang kiệt sức',
            'message': (
                f'Nhân viên tự đánh giá áp lực OK ({pressure_q}={q29:.2f}) nhưng Burnout Risk Index cho thấy '
                f'{burnout_pct:.1f}% đang trong vùng nguy hiểm. '
                f'Đây là "burnout mù" — nhân viên đã normalize mức độ kiệt sức đến mức coi là bình thường. '
                f'Flip point thường xảy ra đột ngột.'
            ),
            'data': {f'{pressure_q}_ap_luc': round(q29, 2), 'burnout_pct': round(burnout_pct, 1)},
            'action': 'Áp dụng Burnout Assessment ẩn danh hàng quý thay vì chỉ dựa vào self-report. Xây dựng early warning system dựa trên HRIS (vắng mặt, hiệu suất giảm).'
        })

    # TC5_A4: Pride Paradox
    if q28 is not None and intent_pct is not None and q28 > 4.0 and intent_pct > 15 and pride_q:
        anomalies.append({
            'id': 'TC5_P1', 'pillar': 'TC5', 'severity': 'warning',
            'title': 'Pride Paradox — Tự hào về GHN nhưng vẫn muốn nghỉ',
            'message': (
                f'Nhân viên tự hào ({pride_q}={q28:.2f}) nhưng {intent_pct:.1f}% muốn nghỉ. '
                f'Vấn đề nằm ở ĐIỀU KIỆN, không phải TÌNH CẢM. Họ yêu GHN nhưng điều kiện làm việc '
                f'(TC3 hoặc TC4) đang buộc họ phải ra đi.'
            ),
            'data': {f'{pride_q}_tu_hao': round(q28, 2), 'flight_risk_pct': round(intent_pct, 1)},
            'action': 'Phỏng vấn exit nhóm này: "Điều gì duy nhất khiến bạn ở lại nếu được thay đổi?" — câu trả lời sẽ chỉ rõ điều kiện cần cải thiện.'
        })

    return anomalies


# ─────────────────────────────────────────────────────────────
# CROSS-PILLAR PATTERNS
# ─────────────────────────────────────────────────────────────

def detect_cross_pillar(df, group_id=''):
    """Phát hiện các pattern liên trụ cột nguy hiểm."""
    anomalies = []

    ei = df['EI'].mean() if 'EI' in df.columns else None
    mei = df['MEI'].mean() if 'MEI' in df.columns else None
    tc1 = _pillar_pct(df, 'TC1')
    tc2 = _pillar_pct(df, 'TC2')
    tc3 = _pillar_pct(df, 'TC3')
    tc4 = _pillar_pct(df, 'TC4')
    tc5 = _pillar_pct(df, 'TC5')

    burnout_pct = None
    if 'burnout_risk' in df.columns:
        valid = df['burnout_risk'].dropna()
        burnout_pct = (valid > 0).sum() / len(valid) * 100 if len(valid) > 0 else None

    intent_pct = None
    if 'intent' in df.columns:
        valid = df['intent'].dropna()
        intent_pct = (valid <= 2).sum() / len(valid) * 100 if len(valid) > 0 else None

    # XP_1: Committed Under Pressure
    if burnout_pct is not None and intent_pct is not None and burnout_pct > 12 and intent_pct < 5:
        anomalies.append({
            'id': 'XP_1', 'pillar': 'CROSS', 'severity': 'warning',
            'title': 'Committed Under Pressure — Gắn bó trong kiệt sức',
            'message': (
                f'Burnout cao ({burnout_pct:.1f}%) nhưng ít người muốn nghỉ ({intent_pct:.1f}%). '
                f'Nhân viên đang "chịu đựng vì trách nhiệm". Khi vượt ngưỡng chịu đựng, '
                f'họ sẽ nghỉ đồng loạt và không có dấu hiệu báo trước.'
            ),
            'data': {'burnout_pct': round(burnout_pct, 1), 'flight_risk_pct': round(intent_pct, 1)},
            'action': 'Không chủ quan dù turnover thấp. Thực hiện Pulse Survey hàng tháng để phát hiện suy giảm trước khi flip.'
        })

    # XP_2: Silent Disengaged (Quiet Quitting)
    if ei is not None and intent_pct is not None and ei < 57 and intent_pct < 5:
        anomalies.append({
            'id': 'XP_2', 'pillar': 'CROSS', 'severity': 'critical',
            'title': 'Silent Disengaged — Quiet Quitting đang xảy ra',
            'message': (
                f'EI thấp ({ei:.1f}%) nhưng rất ít người muốn nghỉ ({intent_pct:.1f}%). '
                f'"Quiet Quitting" điển hình — nhân viên BUÔNG XUÔI nhưng chưa nghỉ. '
                f'Họ làm đủ để không bị sa thải, không hơn. Năng suất âm thầm suy giảm theo thời gian.'
            ),
            'data': {'EI': round(ei, 1), 'flight_risk_pct': round(intent_pct, 1)},
            'action': 'Đừng đo chỉ turnover. Đo năng suất, sáng kiến, số lượt vắng mặt — đó là dấu hiệu của quiet quitting.'
        })

    # XP_3: Manager Island
    if mei is not None and ei is not None and mei > 75 and ei < 60:
        anomalies.append({
            'id': 'XP_3', 'pillar': 'CROSS', 'severity': 'warning',
            'title': 'Manager Island — Quản lý tốt, tổ chức yếu',
            'message': (
                f'MEI = {mei:.1f}% (quản lý xuất sắc) nhưng EI chung = {ei:.1f}% (thấp). '
                f'Nhân viên hài lòng với QL trực tiếp nhưng ghét tổ chức. '
                f'Vấn đề nằm ở cấp chiến lược (TC1), thu nhập (TC4) hoặc văn hóa công ty (TC5).'
            ),
            'data': {'MEI': round(mei, 1), 'EI': round(ei, 1)},
            'action': 'Giữ và thưởng những quản lý tốt. Can thiệp vào trụ cột kéo EI xuống — không phải TC2.'
        })

    # XP_6: Onboarding Shock
    if 'tenure' in df.columns:
        early_mask = df['tenure'].notna() & (df['tenure'] <= EWS_TENURE_THRESHOLD.get(group_id, 2))
    elif 'Q5' in df.columns:
        early_mask = df['Q5'].isin(TENURE_EARLY)
    else:
        early_mask = None
    if early_mask is not None:
        if early_mask.sum() >= 10:
            early_df = df[early_mask]
            early_ei = early_df['EI'].mean() if 'EI' in early_df.columns else None
            overall_ei = df['EI'].mean() if 'EI' in df.columns else None
            if early_ei is not None and overall_ei is not None and (overall_ei - early_ei) > 8:
                anomalies.append({
                    'id': 'XP_6', 'pillar': 'CROSS', 'severity': 'warning',
                    'title': 'Onboarding Shock — Nhóm mới có EI thấp hơn đáng kể',
                    'message': (
                        f'Nhóm < 6 tháng có EI = {early_ei:.1f}% so với trung bình {overall_ei:.1f}%. '
                        f'Khoảng cách {overall_ei-early_ei:.1f} điểm cho thấy onboarding đang có vấn đề. '
                        f'Nhân viên mới bị "sốc văn hóa" trong 3 tháng đầu — đây là nguồn gốc của early attrition.'
                    ),
                    'data': {'early_EI': round(early_ei, 1), 'overall_EI': round(overall_ei, 1)},
                    'action': 'Redesign onboarding 90 ngày: tập trung vào TC2 (buddy system) và TC3 (hướng dẫn quy trình). Check-in bắt buộc tuần 2, 4, 8, 12.'
                })

    # XP_7: Tenure Cliff
    if 'EI' in df.columns and ('tenure' in df.columns or 'Q5' in df.columns):
        tenure_map = {
            'Dưới 1 tháng': 0.5, 'Trên 1 đến 3 tháng': 2, 'Trên 3 đến 6 tháng': 4.5,
            'Trên 6 đến 9 tháng': 7.5, 'Trên 9 đến 12 tháng': 10.5, 'Trên 1 đến 2 năm': 18,
            'Trên 2 đến 3 năm': 30, 'Trên 3 đến 5 năm': 48, 'Trên 5 năm': 72
        }
        source_col = 'tenure' if 'tenure' in df.columns else 'Q5'
        df_work = df[[source_col, 'EI']].copy()
        df_work['tenure_month'] = (
            df_work[source_col].map(TENURE_MONTH_MAP)
            if source_col == 'tenure'
            else df_work[source_col].map(tenure_map)
        )
        tenure_ei = df_work.dropna().groupby('tenure_month')['EI'].mean().reset_index()
        tenure_ei = tenure_ei.sort_values('tenure_month')
        if len(tenure_ei) >= 4:
            # Tìm điểm giảm đột ngột
            diffs = tenure_ei['EI'].diff()
            cliff_idx = diffs.abs().idxmax()
            if diffs.loc[cliff_idx] < -6:
                cliff_tenure = tenure_ei.loc[cliff_idx, 'tenure_month']
                cliff_drop = abs(diffs.loc[cliff_idx])
                anomalies.append({
                    'id': 'XP_7', 'pillar': 'CROSS', 'severity': 'watch',
                    'title': f'Tenure Cliff — Điểm giảm đột ngột ở mốc ~{cliff_tenure:.0f} tháng',
                    'message': (
                        f'EI giảm {cliff_drop:.1f} điểm tại mốc thâm niên ~{cliff_tenure:.0f} tháng. '
                        f'"Cliff" xảy ra khi kỳ vọng ban đầu gặp thực tế — đây là thời điểm nhân viên '
                        f'bắt đầu đánh giá lại quyết định ở lại GHN.'
                    ),
                    'data': {'cliff_at_month': round(cliff_tenure, 0), 'ei_drop': round(cliff_drop, 1)},
                    'action': f'Tạo "milestone intervention" tại mốc {cliff_tenure:.0f} tháng: 1-1 với HR, cập nhật lộ trình phát triển, ghi nhận đóng góp.'
                })

    # XP_8: Generation Gap
    gen_col = 'gen3' if 'gen3' in df.columns else ('Q1' if 'Q1' in df.columns else None)
    pillar_cols = [f'{p}_pct' for p in ['TC1', 'TC2', 'TC3', 'TC4', 'TC5'] if f'{p}_pct' in df.columns]
    if gen_col and len(pillar_cols) >= 2:
        df_gen = df[[gen_col, *pillar_cols]].copy()
        df_gen['gen3_norm'] = df_gen[gen_col] if gen_col == 'gen3' else _infer_gen3(df_gen[gen_col])
        gen_counts = df_gen['gen3_norm'].value_counts()
        if gen_counts.get('Gen Z', 0) >= 10 and gen_counts.get('Gen X', 0) >= 10:
            gen_scores = df_gen.groupby('gen3_norm')[pillar_cols].mean()
            gap_series = gen_scores.loc['Gen X'] - gen_scores.loc['Gen Z']
            sig = gap_series[gap_series > 12]
            if len(sig) >= 2:
                anomalies.append({
                    'id': 'XP_8', 'pillar': 'CROSS', 'severity': 'warning',
                    'title': 'Generation Gap — Khoảng cách thế hệ có tính hệ thống',
                    'message': (
                        f'Gen Z thấp hơn Gen X trên {len(sig)} trụ cột, với khoảng cách lớn nhất '
                        f'{sig.max():.1f} điểm. Đây không phải khác biệt cá nhân mà là khác biệt kỳ vọng '
                        f'giữa thế hệ: cách truyền thông, công cụ, cơ hội phát triển hoặc công bằng có thể đang không hợp với nhóm trẻ.'
                    ),
                    'data': {
                        'gap_pillars': {k.replace('_pct', ''): round(float(v), 1) for k, v in sig.items()},
                        'gen_z_n': int(gen_counts.get('Gen Z', 0)),
                        'gen_x_n': int(gen_counts.get('Gen X', 0)),
                    },
                    'action': 'Tách pulse follow-up cho Gen Z: hỏi 3 chủ đề ngắn về phát triển, công cụ và phản hồi quản lý. Không dùng cùng thông điệp cho mọi thế hệ.'
                })

    # XP_9: Engagement Quadrant distribution (EI x eNPS)
    if 'engagement_quadrant' in df.columns:
        quad = df['engagement_quadrant'].dropna()
    elif 'EI' in df.columns and 'eNPS' in df.columns:
        ei_median = df['EI'].median()
        conditions = [
            (df['EI'] >= ei_median) & (df['eNPS'] >= 9),
            (df['EI'] >= ei_median) & (df['eNPS'] <= 6),
            (df['EI'] < ei_median) & (df['eNPS'] >= 9),
        ]
        choices = ['Champions', 'Trapped Loyalists', 'Confused Leavers']
        quad = pd.Series(np.select(conditions, choices, default='Flight Risk'), index=df.index).dropna()
    else:
        quad = pd.Series(dtype=object)
    if len(quad) >= 30:
        dist = quad.value_counts()
        flight_like = dist.get('Flight Risk', 0) + dist.get('Confused Leavers', 0)
        flight_like_pct = flight_like / len(quad) * 100
        trapped_pct = dist.get('Trapped Loyalists', 0) / len(quad) * 100
        if flight_like_pct >= 25 or trapped_pct >= 35:
            anomalies.append({
                'id': 'XP_9', 'pillar': 'CROSS', 'severity': 'warning' if flight_like_pct < 35 else 'critical',
                'title': 'Engagement Quadrant — Cơ cấu gắn kết lệch rủi ro',
                'message': (
                    f'Nhóm rủi ro/đang rời bỏ về mặt tâm lý chiếm {flight_like_pct:.1f}%, '
                    f'Trapped Loyalists chiếm {trapped_pct:.1f}%. Phân bố này cho thấy EI trung bình có thể che mất '
                    f'các nhóm nhân viên có hành vi rất khác nhau.'
                ),
                'data': {'distribution': dist.to_dict(), 'risk_like_pct': round(flight_like_pct, 1), 'trapped_pct': round(trapped_pct, 1)},
                'action': 'Tách hành động theo quadrant: Champions giữ vai trò đại sứ, Trapped Loyalists cần tháo nút thắt, Flight Risk cần phỏng vấn giữ chân có chọn lọc.'
            })

    # XP_10: Contradiction Index — EI cao nhưng im lặng/tiêu cực.
    silence_rate = None
    if 'is_silent' in df.columns:
        silence_rate = df['is_silent'].dropna().astype(bool).mean() * 100
    negative_rate = None
    if 'nlp_sentiment_label' in df.columns:
        valid_sent = df['nlp_sentiment_label'].dropna()
        if len(valid_sent) >= 20:
            negative_rate = (valid_sent == 'tiêu_cực').sum() / len(valid_sent) * 100
    contradiction_pct = None
    if 'contradiction_flag' in df.columns:
        contradiction_pct = df['contradiction_flag'].dropna().astype(bool).mean() * 100
    if ei is not None and ei >= 70 and (
        (silence_rate is not None and silence_rate >= 55) or
        (negative_rate is not None and negative_rate >= 35) or
        (contradiction_pct is not None and contradiction_pct >= 8)
    ):
        silence_txt = f'{silence_rate:.1f}%' if silence_rate is not None else 'N/A'
        negative_txt = f'{negative_rate:.1f}%' if negative_rate is not None else 'N/A'
        anomalies.append({
            'id': 'XP_10', 'pillar': 'CROSS', 'severity': 'warning',
            'title': 'Contradiction Index — Sức khỏe gắn kết có dấu hiệu giả',
            'message': (
                f'EI đang cao ({ei:.1f}%) nhưng tín hiệu hành vi không đồng thuận: '
                f'Silence {silence_txt}, sentiment tiêu cực {negative_txt}. '
                f'Đây là dấu hiệu cần kiểm tra fear-based compliance hoặc tâm lý ngại nói thật.'
            ),
            'data': {
                'EI': round(ei, 1),
                'silence_rate': round(silence_rate, 1) if silence_rate is not None else None,
                'negative_rate': round(negative_rate, 1) if negative_rate is not None else None,
                'contradiction_pct': round(contradiction_pct, 1) if contradiction_pct is not None else None,
            },
            'action': 'Chạy focus group ẩn danh với câu hỏi mở: "Điều gì mọi người ngại nói ra trong khảo sát?". Không dùng quản lý trực tiếp điều phối phiên này.'
        })

    # XP_11: Quiet Exodus — không kiệt sức nhưng vẫn muốn đi.
    burnout_mean = df['burnout_score'].dropna().mean() if 'burnout_score' in df.columns and df['burnout_score'].notna().any() else None
    if intent_pct is not None and intent_pct >= 10 and burnout_mean is not None and burnout_mean < 35:
        pillar_scores = {p: v for p, v in {'TC1': tc1, 'TC2': tc2, 'TC3': tc3, 'TC4': tc4, 'TC5': tc5}.items() if v is not None}
        root = min(pillar_scores, key=pillar_scores.get) if pillar_scores else 'Unknown'
        root_score = pillar_scores.get(root)
        root_score_txt = f'{root_score:.1f}%' if root_score is not None else 'N/A'
        anomalies.append({
            'id': 'XP_11', 'pillar': 'CROSS', 'severity': 'critical' if intent_pct >= 18 else 'warning',
            'title': 'Quiet Exodus — Muốn rời đi dù không phải vì kiệt sức',
            'message': (
                f'Flight risk đạt {intent_pct:.1f}% trong khi burnout trung bình chỉ {burnout_mean:.1f}/100. '
                f'Nhân viên không đi vì quá tải; họ đang rời đi vì một nút thắt khác. Trụ cột thấp nhất hiện là {root} '
                f'({root_score_txt}).'
            ),
            'data': {'flight_risk_pct': round(intent_pct, 1), 'burnout_score': round(burnout_mean, 1), 'likely_root': root, 'root_score': round(root_score, 1) if root_score else None},
            'action': f'Ưu tiên phỏng vấn giữ chân theo root cause {root}. Hỏi trực tiếp: "Điều gì không liên quan đến tải việc nhưng khiến bạn muốn rời GHN?"'
        })

    return anomalies


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
    """Chạy anomaly detection cho một trụ cột cụ thể."""
    detector = PILLAR_DETECTORS.get(pillar_id)
    if detector is None or df is None or df.empty:
        return []
    try:
        return detector(df, group_id)
    except Exception as e:
        return [{'id': 'ERROR', 'pillar': pillar_id, 'severity': 'watch',
                 'title': 'Lỗi phân tích', 'message': str(e), 'data': {}, 'action': ''}]


def detect_all_anomalies(df, group_id):
    """Chạy tất cả detection: từng TC + cross-pillar."""
    all_anomalies = []
    for pid in ['TC1', 'TC2', 'TC3', 'TC4', 'TC5']:
        all_anomalies.extend(detect_pillar_anomalies(df, group_id, pid))
    all_anomalies.extend(detect_cross_pillar(df, group_id))
    # Sort: critical first
    order = {'critical': 0, 'warning': 1, 'watch': 2}
    return sorted(all_anomalies, key=lambda x: order.get(x.get('severity', 'watch'), 3))


def _percentile_rank(value, values, higher_is_better=True):
    if values is None:
        return None
    vals = pd.Series(values).dropna().astype(float)
    if value is None or pd.isna(value) or len(vals) < 10:
        return None
    pct = (vals <= value).mean() * 100
    return round(float(pct if higher_is_better else 100 - pct), 1)


def compute_relative_thresholds(df):
    """Distribution thresholds for current group/reference data."""
    metrics = ['EI', 'MEI', 'JSI', 'burnout_score', 'TC1_pct', 'TC2_pct', 'TC3_pct', 'TC4_pct', 'TC5_pct']
    thresholds = {}
    for col in metrics:
        if col not in df.columns:
            continue
        s = df[col].dropna().astype(float)
        if len(s) < 10:
            continue
        thresholds[col] = {
            'mean': round(float(s.mean()), 2),
            'std': round(float(s.std()), 2),
            'p10': round(float(s.quantile(0.10)), 2),
            'p25': round(float(s.quantile(0.25)), 2),
            'p50': round(float(s.quantile(0.50)), 2),
            'p75': round(float(s.quantile(0.75)), 2),
            'p90': round(float(s.quantile(0.90)), 2),
        }
    return thresholds


def analyze_tenure_cohorts(df, group_id):
    """Tenure cohort summary used by Phase 4 deep dives."""
    if 'tenure' not in df.columns or 'EI' not in df.columns:
        return {'enabled': False, 'reason': 'missing_tenure_or_ei'}

    agg_map = {'EI': 'mean'}
    for col in ['burnout_score', 'JSI']:
        if col in df.columns:
            agg_map[col] = 'mean'
    if 'intent' in df.columns:
        df_work = df.copy()
        df_work['is_flight_risk'] = df_work['intent'] <= 2
        agg_map['is_flight_risk'] = 'mean'
    else:
        df_work = df

    cohort = df_work.groupby('tenure').agg(agg_map)
    cohort['n'] = df_work.groupby('tenure')['EI'].count()
    cohort = cohort[cohort['n'] >= 5].sort_index()
    if cohort.empty:
        return {'enabled': False, 'reason': 'not_enough_cohort_n'}

    label_map = {
        0: 'Dưới 1 tháng', 1: '1-3 tháng', 2: '3-6 tháng', 3: '6-9 tháng',
        4: '9-12 tháng', 5: '1-2 năm', 6: '2-3 năm', 7: '3-5 năm', 8: 'Trên 5 năm',
    }
    records = []
    for idx, row in cohort.iterrows():
        records.append({
            'tenure': int(idx) if pd.notna(idx) else None,
            'label': label_map.get(int(idx), str(idx)) if pd.notna(idx) else 'Khác',
            'n': int(row['n']),
            'EI': round(float(row['EI']), 1),
            'burnout_score': round(float(row['burnout_score']), 1) if 'burnout_score' in row.index and pd.notna(row['burnout_score']) else None,
            'flight_risk_pct': round(float(row['is_flight_risk']) * 100, 1) if 'is_flight_risk' in row.index and pd.notna(row['is_flight_risk']) else None,
        })

    cliff = None
    diffs = cohort['EI'].diff().dropna()
    if not diffs.empty and diffs.min() <= -6:
        cliff_idx = int(diffs.idxmin())
        cliff = {
            'label': label_map.get(cliff_idx, str(cliff_idx)),
            'drop': round(float(diffs.min()), 1),
        }

    ews_threshold = EWS_TENURE_THRESHOLD.get(group_id, 2)
    early = cohort[cohort.index <= ews_threshold]
    mature = cohort[cohort.index > ews_threshold]
    early_gap = None
    if not early.empty and not mature.empty:
        early_gap = round(float(mature['EI'].mean() - early['EI'].mean()), 1)

    return {
        'enabled': True,
        'records': records,
        'cliff': cliff,
        'early_gap': early_gap,
        'ews_window': label_map.get(ews_threshold, str(ews_threshold)),
    }


def compute_unit_health(df, reference_df=None):
    """Health snapshot. Uses reference percentiles when available."""
    ei = df['EI'].mean() if 'EI' in df.columns else np.nan
    burnout = df['burnout_score'].mean() if 'burnout_score' in df.columns else np.nan
    flight = _flight_risk_pct(df)

    if reference_df is not None and not reference_df.empty:
        ei_pct = _percentile_rank(ei, reference_df.get('EI'), True) if 'EI' in reference_df.columns else None
        burnout_pct = _percentile_rank(burnout, reference_df.get('burnout_score'), False) if 'burnout_score' in reference_df.columns else None
        flight_pct = None
        components = [v for v in [ei_pct, burnout_pct, flight_pct] if v is not None]
        note = 'Health score dùng percentile rank so với reference distribution.'
    else:
        components = []
        if not np.isnan(ei):
            components.append(ei)
        if burnout is not None and not np.isnan(burnout):
            components.append(100 - burnout)
        if flight is not None:
            components.append(100 - flight)
        note = 'Health score gọn = trung bình EI, retention và inverse burnout.'

    health = float(np.mean(components)) if components else np.nan
    if np.isnan(health):
        label = 'Không đủ dữ liệu'
    elif health >= 75:
        label = 'Khỏe'
    elif health >= 60:
        label = 'Theo dõi'
    else:
        label = 'Rủi ro'

    return {
        'score': round(health, 1) if not np.isnan(health) else None,
        'label': label,
        'EI': round(float(ei), 1) if not np.isnan(ei) else None,
        'burnout_score': round(float(burnout), 1) if burnout is not None and not np.isnan(burnout) else None,
        'flight_risk_pct': round(float(flight), 1) if flight is not None else None,
        'note': note,
    }


def build_deep_dive_plan(df, group_id, scan):
    """Group-specific deep-dive dispatcher from v3, grounded in detected patterns."""
    anomalies = scan.get('all_anomalies', [])
    ids = {a.get('id') for a in anomalies}
    lowest_pillar = None
    pillar_scores = {
        p: _pillar_pct(df, p) for p in ['TC1', 'TC2', 'TC3', 'TC4', 'TC5']
    }
    pillar_scores = {k: v for k, v in pillar_scores.items() if v is not None}
    if pillar_scores:
        lowest_pillar = min(pillar_scores, key=pillar_scores.get)

    playbook = {
        '1A': {
            'focus': 'Thu nhập, phân đơn/khu vực và App Driver',
            'triggers': ['TC4_A1', 'TC4_A5', 'TC5_A5', 'TC3_A1'],
            'questions': [
                'TC4 thấp do mức thu nhập thật hay do nhân viên không hiểu cách tính/phạt?',
                'Có vùng/khu vực nào bị chênh phân đơn hoặc hỗ trợ sự cố không?',
                'App Driver/công cụ có đang tạo frustration hằng ngày không?',
            ],
        },
        '1B': {
            'focus': 'Tuyến dài/ngắn, ca đêm, phụ cấp và an toàn',
            'triggers': ['TC5_A5', 'TC3_A1', 'TC4_A1'],
            'questions': [
                'Lịch chạy và tuyến có tạo cảm giác bất công không?',
                'Phụ cấp/phạt/chi phí đường dài có minh bạch đủ không?',
                'Áp lực an toàn nghề nghiệp có bị bình thường hóa không?',
            ],
        },
        '2A': {
            'focus': 'Ca/kíp, OT fairness, onboarding và an toàn lao động',
            'triggers': ['XP_6', 'TC3_A2', 'TC2_A2'],
            'questions': [
                'Nhân sự mới có EI thấp hơn rõ rệt không?',
                'OT/ca/kíp có phân bổ công bằng không?',
                'Thiết bị/quy trình kho có đang tạo quá tải ngầm không?',
            ],
        },
        '2B': {
            'focus': 'Áp lực kép, autonomy và năng lực quản lý tuyến đầu',
            'triggers': ['XP_1', 'TC2_A1', 'TC2_A3'],
            'questions': [
                'Quản lý tuyến đầu đang kẹt giữa KPI và hỗ trợ đội ngũ ở điểm nào?',
                'MEI cao/thấp có khớp với flight risk không?',
                'Autonomy có đủ để xử lý vấn đề vận hành tại chỗ không?',
            ],
        },
        '3A': {
            'focus': 'Process debt, phối hợp liên phòng ban và career block',
            'triggers': ['XP_2', 'TC3_A3', 'TC3_A4'],
            'questions': [
                'Nút thắt quy trình nào gây friction liên phòng ban nhiều nhất?',
                'Career path có đang là nguyên nhân rời đi âm thầm không?',
                'Nhóm nào có EI thấp nhưng chưa muốn nghỉ?',
            ],
        },
        '3B': {
            'focus': 'Strategy clarity, succession, peer collaboration và workload lãnh đạo',
            'triggers': ['XP_1', 'XP_10', 'TC1_A1'],
            'questions': [
                'Lãnh đạo có rõ ưu tiên chiến lược và quyền quyết định không?',
                'Áp lực lãnh đạo có đang được normalize như một điều hiển nhiên không?',
                'Peer collaboration có đủ thực chất để giải quyết bài toán cross-function không?',
            ],
        },
    }
    spec = playbook.get(group_id, {
        'focus': f'Đi sâu vào {lowest_pillar or "trụ cột thấp nhất"}',
        'triggers': [],
        'questions': ['Xác định nhóm có điểm thấp nhất và phỏng vấn nguyên nhân trực tiếp.'],
    })
    matched = [t for t in spec['triggers'] if t in ids]
    urgency = 'HIGH' if any(a.get('severity') == 'critical' for a in anomalies if a.get('id') in matched) else ('MEDIUM' if matched else 'LOW')
    return {
        'focus': spec['focus'],
        'matched_triggers': matched,
        'urgency': urgency,
        'lowest_pillar': lowest_pillar,
        'lowest_pillar_score': round(float(pillar_scores[lowest_pillar]), 1) if lowest_pillar else None,
        'questions': spec['questions'],
        'next_step': 'Chạy deep dive theo playbook nhóm và ưu tiên các trigger đã match.' if matched else 'Chưa có trigger đặc thù; bắt đầu từ trụ cột thấp nhất và cohort tenure rủi ro.',
    }


def build_priority_actions(anomalies, limit=5):
    """Pick the highest-signal actions from anomaly results."""
    severity_rank = {'critical': 0, 'warning': 1, 'watch': 2}
    pillar_rank = {'CROSS': 0, 'TC2': 1, 'TC4': 2, 'TC3': 3, 'TC1': 4, 'TC5': 5}
    seen = set()
    actions = []
    for item in sorted(
        anomalies,
        key=lambda a: (severity_rank.get(a.get('severity', 'watch'), 3), pillar_rank.get(a.get('pillar'), 9), a.get('id', ''))
    ):
        action = item.get('action')
        if not action or action in seen:
            continue
        seen.add(action)
        actions.append({
            'id': item.get('id'),
            'pillar': item.get('pillar'),
            'severity': item.get('severity'),
            'title': item.get('title'),
            'action': action,
        })
        if len(actions) >= limit:
            break
    return actions


def run_full_anomaly_scan(df, group_id, reference_df=None):
    """Full cached-friendly anomaly scan for a group/unit."""
    pillar_anomalies = {
        pid: detect_pillar_anomalies(df, group_id, pid)
        for pid in ['TC1', 'TC2', 'TC3', 'TC4', 'TC5']
    }
    cross = detect_cross_pillar(df, group_id)
    flat = [a for rows in pillar_anomalies.values() for a in rows] + cross
    order = {'critical': 0, 'warning': 1, 'watch': 2}
    flat = sorted(flat, key=lambda x: order.get(x.get('severity', 'watch'), 3))

    scan = {
        'group_id': group_id,
        'unit_n': int(len(df)),
        'health_score': compute_unit_health(df, reference_df=reference_df),
        'relative_thresholds': compute_relative_thresholds(reference_df if reference_df is not None else df),
        'tenure_cohorts': analyze_tenure_cohorts(df, group_id),
        'pillar_anomalies': pillar_anomalies,
        'cross_pillar_patterns': cross,
        'all_anomalies': flat,
        'priority_actions': build_priority_actions(flat),
        'counts': {
            'critical': sum(1 for a in flat if a.get('severity') == 'critical'),
            'warning': sum(1 for a in flat if a.get('severity') == 'warning'),
            'watch': sum(1 for a in flat if a.get('severity') == 'watch'),
        },
    }
    scan['deep_dive_plan'] = build_deep_dive_plan(df, group_id, scan)
    return scan
