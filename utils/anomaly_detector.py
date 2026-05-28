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


# ─────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────

TENURE_EARLY = ['Dưới 1 tháng', 'Trên 1 đến 3 tháng', 'Trên 3 đến 6 tháng']
TENURE_SENIOR = ['Trên 2 đến 3 năm', 'Trên 3 đến 5 năm', 'Trên 5 năm']


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


def _pillar_pct(df, pillar_id):
    col = f'{pillar_id}_pct'
    if col in df.columns:
        return df[col].mean()
    return None


def _severity_badge(s):
    return {'critical': 'Khẩn cấp', 'warning': 'Cảnh báo', 'watch': 'Theo dõi'}.get(s, s)


# ─────────────────────────────────────────────────────────────
# TC1 — NIỀM TIN & ĐỊNH HƯỚNG
# ─────────────────────────────────────────────────────────────

def detect_TC1(df, group_id=''):
    anomalies = []
    q9  = _qmean(df, 'Q9')
    q10 = _qmean(df, 'Q10')
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
    q11 = _qmean(df, 'Q11')
    q12 = _qmean(df, 'Q12')
    q15 = _qmean(df, 'Q15')
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
                f'Hỗ trợ từ quản lý (Q11={q11:.2f}) tốt hơn nhiều so với công bằng phân công (Q12={q12:.2f}). '
                f'Nhân viên cảm nhận quản lý HỖ TRỢ tốt nhưng PHÂN ĐƠN/LỊCH không công bằng. '
                f'Đây là ngòi nổ chính cho mâu thuẫn nội bộ và flight risk.'
            ),
            'data': {'Q11_ho_tro': round(q11, 2), 'Q12_cong_bang': round(q12, 2), 'gap': round(q11-q12, 2)},
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
    if q15 is not None:
        tc2_qs = [c for c in ['Q11','Q12','Q13','Q14','Q15'] if c in df.columns]
        means = {q: _qmean(df, q) for q in tc2_qs if _qmean(df, q) is not None}
        if means and q15 == min(means.values()) and q15 < 3.6:
            anomalies.append({
                'id': 'TC2_A5', 'pillar': 'TC2', 'severity': 'watch',
                'title': 'Phản hồi một chiều — Nhân viên không được lắng nghe',
                'message': (
                    f'Câu về phản hồi (Q15={q15:.2f}) là điểm thấp nhất trong TC2. '
                    f'Nhân viên có thể hoàn thành công việc nhưng không cảm thấy được lắng nghe và ghi nhận. '
                    f'Đây là dấu hiệu sớm của silent disengagement.'
                ),
                'data': {'Q15_phan_hoi': round(q15, 2)},
                'action': 'Triển khai "weekly check-in 5 phút" — quản lý hỏi 2 câu: "Tuần này có vấn đề gì không?" và "Cần hỗ trợ gì?".'
            })

    return anomalies


# ─────────────────────────────────────────────────────────────
# TC3 — CÔNG VIỆC & ĐIỀU KIỆN VẬN HÀNH
# ─────────────────────────────────────────────────────────────

def detect_TC3(df, group_id=''):
    anomalies = []
    q16 = _qmean(df, 'Q16')
    q18 = _qmean(df, 'Q18')
    q19 = _qmean(df, 'Q19')
    q20 = _qmean(df, 'Q20')
    q10 = _qmean(df, 'Q10')  # TC1 — thông báo kịp thời

    burnout_pct = None
    if 'burnout_risk' in df.columns:
        valid = df['burnout_risk'].dropna()
        burnout_pct = (valid > 0).sum() / len(valid) * 100 if len(valid) > 0 else None

    # TC3_A1: Công cụ cản trở
    if q16 is not None and q16 < 3.5:
        anomalies.append({
            'id': 'TC3_A1', 'pillar': 'TC3', 'severity': 'warning',
            'title': 'Công cụ/App đang cản trở công việc, không phải hỗ trợ',
            'message': (
                f'Q16 (App/thiết bị) = {q16:.2f}/5 — dưới ngưỡng 3.5. '
                f'Công cụ kém không chỉ ảnh hưởng hiệu suất mà còn tạo ra frustration mỗi ngày, '
                f'tích lũy thành bất mãn tổng thể. Liên kết với HRIS: năng suất thực tế có bị ảnh hưởng không?'
            ),
            'data': {'Q16_cong_cu': round(q16, 2)},
            'action': 'Thu thập báo lỗi App Driver cụ thể từ nhân viên. Fix bug ưu tiên cao trong 2 tuần. Thông báo rõ roadmap cải thiện.'
        })

    # TC3_A2: Burnout ẩn
    if q18 is not None and burnout_pct is not None and q18 > 3.5 and burnout_pct > 28:
        anomalies.append({
            'id': 'TC3_A2', 'pillar': 'TC3', 'severity': 'critical',
            'title': 'Burnout ẩn — Nhân viên không nhận ra mình đang kiệt sức',
            'message': (
                f'Nhân viên tự đánh giá cường độ ổn (Q18={q18:.2f}) nhưng chỉ số Burnout thực tế lên tới {burnout_pct:.1f}%. '
                f'Đây là "burnout blind spot" — nguy hiểm vì không có dấu hiệu cảnh báo sớm từ chính nhân viên. '
                f'Flip point thường xảy ra đột ngột khi vượt qua ngưỡng chịu đựng.'
            ),
            'data': {'Q18_cuong_do': round(q18, 2), 'burnout_pct': round(burnout_pct, 1)},
            'action': 'Pulse check hàng tháng về tải công việc. Xem xét giảm KPI đơn vào mùa thấp điểm để tái nạp năng lượng cho nhân viên.'
        })

    # TC3_A3: Trần thủy tinh (Glass Ceiling)
    if q19 is not None and 'Q5' in df.columns:
        senior_mask = df['Q5'].isin(TENURE_SENIOR)
        if senior_mask.sum() >= 10:
            senior_career = df.loc[senior_mask, 'Q19'].dropna().mean()
            junior_mask = df['Q5'].isin(TENURE_EARLY)
            junior_career = df.loc[junior_mask, 'Q19'].dropna().mean() if junior_mask.sum() >= 10 else None
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
    if q20 is not None and q10 is not None and q20 < 3.4 and q10 < 3.5:
        anomalies.append({
            'id': 'TC3_A4', 'pillar': 'TC3', 'severity': 'warning',
            'title': 'Double Gap: Thay đổi không được thông báo VÀ không được hướng dẫn',
            'message': (
                f'TC1-Q10 (thông báo kịp thời) = {q10:.2f} thấp, kết hợp Q20 (hướng dẫn khi thay đổi) = {q20:.2f} thấp. '
                f'Đây là "double gap": nhân viên không biết thay đổi sắp đến VÀ khi đến cũng không biết làm gì. '
                f'Gây ra lo lắng, sai sót và mất tin tưởng.'
            ),
            'data': {'Q10_thong_bao': round(q10, 2), 'Q20_huong_dan': round(q20, 2)},
            'action': 'Bất kỳ thay đổi quy trình nào cần kèm SOP rõ ràng. Triển khai "Change Communication Checklist": thông báo trước 7 ngày + hướng dẫn thực hành.'
        })

    return anomalies


# ─────────────────────────────────────────────────────────────
# TC4 — THU NHẬP & MINH BẠCH
# ─────────────────────────────────────────────────────────────

def detect_TC4(df, group_id=''):
    anomalies = []
    q21 = _qmean(df, 'Q21')
    q22_tc4 = _qmean(df, 'Q22')  # Trong 1A: App hiển thị rõ phạt/thu nhập
    q25 = _qmean(df, 'Q25')
    tc4 = _pillar_pct(df, 'TC4')

    intent_pct = None
    if 'intent' in df.columns:
        valid = df['intent'].dropna()
        intent_pct = (valid <= 2).sum() / len(valid) * 100 if len(valid) > 0 else None

    tc5 = _pillar_pct(df, 'TC5')

    # TC4_A1: Cảm nhận bất công (có thể do minh bạch, không phải mức lương)
    if q21 is not None and q21 < 3.4:
        anomalies.append({
            'id': 'TC4_A1', 'pillar': 'TC4', 'severity': 'warning',
            'title': 'Thu nhập bị cảm nhận là không công bằng',
            'message': (
                f'Q21 (thu nhập phản ánh công sức) = {q21:.2f}/5. '
                f'Lưu ý: vấn đề có thể là MINH BẠCH, không phải mức lương. '
                f'Cần so sánh với dữ liệu HRIS: nếu thu nhập thực tế ổn mà Q21 vẫn thấp → '
                f'nhân viên không hiểu cách tính, không phải lương thấp.'
            ),
            'data': {'Q21_cong_bang': round(q21, 2)},
            'action': 'Tổ chức buổi giải thích "Lương của bạn được tính như thế nào" cho nhân viên TC4 thấp nhất. Đơn giản hóa cách trình bày thu nhập trên App.'
        })

    # TC4_A2: Phạt không minh bạch
    if q21 is not None and q22_tc4 is not None and (q21 - q22_tc4) > 0.45:
        anomalies.append({
            'id': 'TC4_A2', 'pillar': 'TC4', 'severity': 'warning',
            'title': 'Phạt/Thu nhập hiển thị không rõ ràng',
            'message': (
                f'Q21 (thu nhập công bằng) = {q21:.2f} vs Q22 (App hiển thị rõ phạt) = {q22_tc4:.2f}. '
                f'Khoảng cách {q21-q22_tc4:.2f} điểm: nhân viên CHẤP NHẬN thu nhập nhưng không hiểu các khoản khấu trừ/phạt. '
                f'Sự mờ ám về phạt tạo ra cảm giác bị bất công dù mức lương ổn.'
            ),
            'data': {'Q21': round(q21, 2), 'Q22_app_phat': round(q22_tc4, 2)},
            'action': 'Cải thiện UI màn hình thu nhập App Driver: tách rõ lương cơ bản / thưởng / phạt / khấu trừ thành từng dòng với giải thích đơn giản.'
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
    if q25 is not None:
        tc4_qs = [c for c in ['Q21','Q22','Q23','Q24','Q25'] if c in df.columns]
        means = {q: _qmean(df, q) for q in tc4_qs if _qmean(df, q) is not None}
        if means and q25 <= min(means.values()) + 0.05 and q25 < 3.5:
            anomalies.append({
                'id': 'TC4_A5', 'pillar': 'TC4', 'severity': 'watch',
                'title': 'Hỗ trợ sự cố ảnh hưởng thu nhập — Điểm yếu nhất TC4',
                'message': (
                    f'Q25 (hỗ trợ sự cố ảnh hưởng thu nhập) = {q25:.2f} — thấp nhất trong TC4. '
                    f'Khi nhân viên gặp sự cố (giao hàng thất bại, mất hàng, tai nạn) mà không được hỗ trợ, '
                    f'thu nhập bị cắt và bất mãn bùng phát ngay lập tức.'
                ),
                'data': {'Q25_ho_tro_su_co': round(q25, 2)},
                'action': 'Thiết lập quy trình xử lý khiếu nại sự cố trong 24h. Nhân viên phải biết đầu mối liên hệ và timeline xử lý rõ ràng.'
            })

    return anomalies


# ─────────────────────────────────────────────────────────────
# TC5 — MÔI TRƯỜNG & SỰ GẮN KẾT
# ─────────────────────────────────────────────────────────────

def detect_TC5(df, group_id=''):
    anomalies = []
    q27 = _qmean(df, 'Q27')
    q28 = _qmean(df, 'Q28')
    q29 = _qmean(df, 'Q29')
    ei = df['EI'].mean() if 'EI' in df.columns else None

    burnout_pct = None
    if 'burnout_risk' in df.columns:
        valid = df['burnout_risk'].dropna()
        burnout_pct = (valid > 0).sum() / len(valid) * 100 if len(valid) > 0 else None

    intent_pct = None
    if 'intent' in df.columns:
        valid = df['intent'].dropna()
        intent_pct = (valid <= 2).sum() / len(valid) * 100 if len(valid) > 0 else None

    # TC5_A1: Tự hào nhưng kiệt sức
    if q28 is not None and q29 is not None and q28 > 3.9 and q29 < 3.2:
        anomalies.append({
            'id': 'TC5_A1', 'pillar': 'TC5', 'severity': 'critical',
            'title': 'Tự hào nhưng đang kiệt sức — Sắp đến điểm bùng phát',
            'message': (
                f'Nhân viên tự hào về GHN (Q28={q28:.2f}) nhưng áp lực đang xâm lấn cuộc sống (Q29={q29:.2f}). '
                f'Đây là pattern nguy hiểm nhất: yêu công ty NHƯNG không chịu nổi. '
                f'Khi vượt ngưỡng chịu đựng, họ sẽ nghỉ đột ngột và không thể giữ lại.'
            ),
            'data': {'Q28_tu_hao': round(q28, 2), 'Q29_ap_luc': round(q29, 2)},
            'action': 'Giảm tải ngay: xem xét KPI có hợp lý không. Triển khai "No-Deadline Friday" hoặc giờ nghỉ phép tăng thêm cho nhóm có áp lực cao nhất.'
        })

    # TC5_A2: Đồng nghiệp tốt, công ty tệ (Social Glue Risk)
    if q27 is not None and ei is not None and q27 > 4.0 and ei < 57:
        anomalies.append({
            'id': 'TC5_A2', 'pillar': 'TC5', 'severity': 'warning',
            'title': 'Social Glue Risk — Ở lại vì bạn bè, không vì tổ chức',
            'message': (
                f'Đồng nghiệp hỗ trợ tốt (Q27={q27:.2f}) nhưng EI tổng thể thấp ({ei:.1f}%). '
                f'Nhân viên ở lại vì TẬP THỂ, không vì tổ chức. '
                f'Rủi ro: khi 1-2 người bạn thân nghỉ, cả nhóm có thể nghỉ theo (domino effect).'
            ),
            'data': {'Q27_dong_nghiep': round(q27, 2), 'EI': round(ei, 1)},
            'action': 'Theo dõi các đơn vị có turnover cao: khi 1 người nghỉ, pulse check ngay các đồng nghiệp thân thiết trong vòng 2 tuần.'
        })

    # TC5_A3: Burnout nghịch lý
    if q29 is not None and burnout_pct is not None and q29 > 3.8 and burnout_pct > 25:
        anomalies.append({
            'id': 'TC5_A5', 'pillar': 'TC5', 'severity': 'critical',
            'title': 'Burnout Blind Spot — Nhân viên không nhận ra mình đang kiệt sức',
            'message': (
                f'Nhân viên tự đánh giá áp lực OK (Q29={q29:.2f}) nhưng Burnout Risk Index cho thấy '
                f'{burnout_pct:.1f}% đang trong vùng nguy hiểm. '
                f'Đây là "burnout mù" — nhân viên đã normalize mức độ kiệt sức đến mức coi là bình thường. '
                f'Flip point thường xảy ra đột ngột.'
            ),
            'data': {'Q29_ap_luc': round(q29, 2), 'burnout_pct': round(burnout_pct, 1)},
            'action': 'Áp dụng Burnout Assessment ẩn danh hàng quý thay vì chỉ dựa vào self-report. Xây dựng early warning system dựa trên HRIS (vắng mặt, hiệu suất giảm).'
        })

    # TC5_A4: Pride Paradox
    if q28 is not None and intent_pct is not None and q28 > 4.0 and intent_pct > 15:
        anomalies.append({
            'id': 'TC5_P1', 'pillar': 'TC5', 'severity': 'warning',
            'title': 'Pride Paradox — Tự hào về GHN nhưng vẫn muốn nghỉ',
            'message': (
                f'Nhân viên tự hào (Q28={q28:.2f}) nhưng {intent_pct:.1f}% muốn nghỉ. '
                f'Vấn đề nằm ở ĐIỀU KIỆN, không phải TÌNH CẢM. Họ yêu GHN nhưng điều kiện làm việc '
                f'(TC3 hoặc TC4) đang buộc họ phải ra đi.'
            ),
            'data': {'Q28_tu_hao': round(q28, 2), 'flight_risk_pct': round(intent_pct, 1)},
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
    if 'Q5' in df.columns:
        early_mask = df['Q5'].isin(TENURE_EARLY)
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
    if 'Q5' in df.columns and 'EI' in df.columns:
        tenure_map = {
            'Dưới 1 tháng': 0.5, 'Trên 1 đến 3 tháng': 2, 'Trên 3 đến 6 tháng': 4.5,
            'Trên 6 đến 9 tháng': 7.5, 'Trên 9 đến 12 tháng': 10.5, 'Trên 1 đến 2 năm': 18,
            'Trên 2 đến 3 năm': 30, 'Trên 3 đến 5 năm': 48, 'Trên 5 năm': 72
        }
        df_work = df[['Q5', 'EI']].copy()
        df_work['tenure_month'] = df_work['Q5'].map(tenure_map)
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
