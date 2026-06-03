"""
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
    col = f'{pillar_id}_score'
    if col in df.columns: return df[col].mean()
    col_pct = f'{pillar_id}_pct'
    if col_pct in df.columns: return df[col_pct].mean()
    return None

def get_unit_hris(df_survey_unit: pd.DataFrame,
                  df_hris: pd.DataFrame,
                  join_key: str = 'employee_id') -> pd.DataFrame | None:
    """
    FIX #6: Filter HRIS về đúng unit trước khi dùng bất kỳ HRIS metric nào.
    Không pre-filter = income benchmark tính trên toàn công ty = SAI.
    """
    if df_hris is None:
        return None
    if join_key not in df_survey_unit.columns or join_key not in df_hris.columns:
        print(f"⚠️ Join key '{join_key}' không có trong survey hoặc HRIS — HRIS enrichment bị bỏ qua")
        return None
    unit_ids = df_survey_unit[join_key].dropna().unique()
    filtered = df_hris[df_hris[join_key].isin(unit_ids)]
    if len(filtered) == 0:
        print(f"⚠️ Không tìm thấy HRIS records cho unit này (n_survey={len(df_survey_unit)})")
        return None
    return filtered


### 5.2 Per-Pillar Anomaly Detectors

def _is_low(val, thresh_dict, key='p25'):
    """Helper: kiểm tra val < ngưỡng, trả False nếu thiếu dữ liệu."""
    if np.isnan(val) or thresh_dict.get(key) is None:
        return False
    return val < thresh_dict[key]

def _is_high(val, thresh_dict, key='p75'):
    if np.isnan(val) or thresh_dict.get(key) is None:
        return False
    return val > thresh_dict[key]


def detect_TC1_anomalies(unit_df, company_thresholds, group_id):
    anomalies = []
    t1 = company_thresholds.get('TC1_score', {})
    ei_t = company_thresholds.get('EI', {})

    tc1_mean = unit_df['TC1_score'].mean() if 'TC1_score' in unit_df.columns else np.nan
    ei_mean  = unit_df['EI'].mean()         if 'EI' in unit_df.columns else np.nan

    # A1: Mất niềm tin cục bộ
    if _is_low(tc1_mean, t1) and not _is_low(ei_mean, ei_t):
        anomalies.append({'id': 'TC1_A1', 'pattern': 'Mất niềm tin cục bộ',
                          'tc1': round(tc1_mean, 1), 'company_p25': t1.get('p25')})

    # A2: Thông tin đứt gãy — FIX #4: dùng alias, không dùng position
    trust_col = get_item(group_id, 'trust_item')
    comms_col = get_item(group_id, 'comms_item')
    if trust_col and comms_col and trust_col in unit_df.columns and comms_col in unit_df.columns:
        trust_mean = unit_df[trust_col].mean()
        comms_mean = unit_df[comms_col].mean()
        gap = trust_mean - comms_mean
        if gap > 0.5:
            anomalies.append({
                'id': 'TC1_A2', 'pattern': 'Thông tin đứt gãy',
                'trust': round(trust_mean, 2), 'comms': round(comms_mean, 2),
                'gap': round(gap, 2),
                'interpretation': 'Tin BLĐ nhưng KHÔNG được thông báo kịp thời → kênh truyền thông vấn đề'
            })
    elif group_id == '3B':
        pass  # 3B không có comms_item — TC1_A2 không apply

    # A3: Nghịch lý tin tưởng
    fr_t   = company_thresholds.get('is_flight_risk_pct', {})
    fr_pct = unit_df['is_flight_risk'].mean() * 100 if 'is_flight_risk' in unit_df.columns else np.nan
    if _is_high(tc1_mean, t1) and _is_high(fr_pct, fr_t):
        anomalies.append({'id': 'TC1_A3', 'pattern': 'Nghịch lý tin tưởng',
                          'tc1': round(tc1_mean, 1), 'flight_pct': round(fr_pct, 1),
                          'note': 'Tin BLĐ nhưng vẫn muốn nghỉ → deep dive TC2–TC4'})

    # A4: Generation Gap
    if 'gen3' in unit_df.columns and 'TC1_score' in unit_df.columns:
        gen_tc1 = unit_df.groupby('gen3')['TC1_score'].mean()
        gz = gen_tc1.get('Gen Z', np.nan)
        gx = gen_tc1.get('Gen X', np.nan)
        if not np.isnan(gz) and not np.isnan(gx) and (gx - gz) > 20:
            anomalies.append({'id': 'TC1_A4', 'pattern': 'Generation Gap',
                              'gen_z_tc1': round(gz, 1), 'gen_x_tc1': round(gx, 1),
                              'gap_pct': round(gx - gz, 1)})
    return anomalies


def detect_TC2_anomalies(unit_df, company_thresholds, group_id):
    anomalies = []
    t2 = company_thresholds.get('TC2_score', {})
    ei_t = company_thresholds.get('EI', {})
    fr_t = company_thresholds.get('is_flight_risk_pct', {})

    tc2_mean = unit_df['TC2_score'].mean() if 'TC2_score' in unit_df.columns else np.nan
    ei_mean  = unit_df['EI'].mean()         if 'EI' in unit_df.columns else np.nan
    fr_pct   = unit_df['is_flight_risk'].mean() * 100 if 'is_flight_risk' in unit_df.columns else np.nan

    # A1: Manager Island
    if _is_high(tc2_mean, t2) and _is_low(ei_mean, ei_t):
        anomalies.append({'id': 'TC2_A1', 'pattern': 'Manager Island',
                          'tc2': round(tc2_mean, 1), 'ei': round(ei_mean, 1),
                          'risk': 'NV ở lại vì QL — rủi ro nếu QL nghỉ'})

    # A2: Fairness gap
    fair_col    = get_item(group_id, 'fairness')
    tc2_qs      = get_pillar_questions(group_id, 'TC2')
    support_col = tc2_qs[0] if tc2_qs else None
    if (fair_col and fair_col in unit_df.columns and
            support_col and support_col in unit_df.columns and
            fair_col != support_col):
        gap = unit_df[support_col].mean() - unit_df[fair_col].mean()
        if gap > 0.6:
            anomalies.append({
                'id': 'TC2_A2', 'pattern': 'Phân biệt đối xử / Thiếu công bằng',
                'support': round(unit_df[support_col].mean(), 2),
                'fairness': round(unit_df[fair_col].mean(), 2),
                'gap': round(gap, 2)
            })

    # A3: QL yếu toàn diện
    if _is_low(tc2_mean, t2, 'p10') and len(unit_df) >= 15:
        breakdown = {q: round(unit_df[q].mean(), 2) for q in tc2_qs if q in unit_df.columns}
        anomalies.append({'id': 'TC2_A3', 'pattern': 'Quản lý yếu toàn diện',
                          'tc2': round(tc2_mean, 1), 'n': len(unit_df),
                          'breakdown': breakdown})

    # A4: MEI shield thất bại
    if _is_high(tc2_mean, t2) and _is_high(fr_pct, fr_t):
        anomalies.append({'id': 'TC2_A4', 'pattern': 'MEI shield thất bại',
                          'tc2': round(tc2_mean, 1), 'flight_pct': round(fr_pct, 1),
                          'note': 'QL tốt nhưng TC4 (thu nhập) quá thấp override'})

    # A5: Feedback item yếu nhất
    feed_col = get_item(group_id, 'feedback')
    if feed_col and tc2_qs:
        tc2_means = {q: unit_df[q].mean() for q in tc2_qs if q in unit_df.columns}
        if tc2_means and min(tc2_means, key=tc2_means.get) == feed_col:
            anomalies.append({'id': 'TC2_A5', 'pattern': 'Feedback một chiều',
                              'feedback_score': round(tc2_means[feed_col], 2),
                              'tc2_avg': round(np.mean(list(tc2_means.values())), 2)})
    return anomalies


def detect_TC3_anomalies(unit_df, company_thresholds, group_id):
    anomalies = []
    tc3_qs  = get_pillar_questions(group_id, 'TC3')
    tc3_means = {q: unit_df[q].mean() for q in tc3_qs if q in unit_df.columns}
    bn_t = company_thresholds.get('burnout_score', {})

    # A1: Công cụ cản trở (item đầu TC3)
    tool_col = get_item(group_id, 'tool')
    if tool_col and tool_col in unit_df.columns and unit_df[tool_col].mean() < 3.0:
        anomalies.append({'id': 'TC3_A1', 'pattern': 'Công cụ cản trở',
                          'tool_score': round(unit_df[tool_col].mean(), 2),
                          'note': 'Cross-check HRIS năng suất đơn vị này'})

    # A2: Burnout ẩn
    wl_col = get_item(group_id, 'workload')
    if (wl_col and wl_col in unit_df.columns and 'burnout_score' in unit_df.columns):
        wl_mean = unit_df[wl_col].mean()
        bn_mean = unit_df['burnout_score'].mean()
        if wl_mean > 3.0 and _is_high(bn_mean, bn_t):
            anomalies.append({'id': 'TC3_A2', 'pattern': 'Burnout ẩn',
                              'perceived_workload_ok': round(wl_mean, 2),
                              'burnout_score': round(bn_mean, 1),
                              'note': 'Triangulate với NLP câu mở C25/C26'})

    # A3: Trần thủy tinh
    career_col = get_item(group_id, 'career')
    if career_col and career_col in unit_df.columns and 'tenure' in unit_df.columns:
        senior = unit_df['tenure'] >= SENIOR_TENURE_THRESHOLD
        s_career = unit_df.loc[senior, career_col].mean()
        j_career = unit_df.loc[~senior, career_col].mean()
        if not np.isnan(s_career) and s_career < 3.0:
            anomalies.append({'id': 'TC3_A3', 'pattern': 'Trần thủy tinh',
                              'senior_career': round(s_career, 2),
                              'junior_career': round(j_career, 2) if not np.isnan(j_career) else None,
                              'interpretation': 'NV lâu năm không thấy tương lai → quiet quitting'})

    # A4: Hướng dẫn thay đổi kém (item cuối TC3)
    if tc3_qs and tc3_means:
        guidance_col = tc3_qs[-1]
        if guidance_col in tc3_means and min(tc3_means, key=tc3_means.get) == guidance_col:
            anomalies.append({'id': 'TC3_A4', 'pattern': 'Thay đổi không hướng dẫn',
                              'score': round(tc3_means[guidance_col], 2),
                              'note': 'Check TC1_A2: thường đi kèm'})

    # A5: An toàn lao động (1B, 2A)
    safety_col = get_item(group_id, 'safety') or get_item(group_id, 'safety_labor')
    if safety_col and safety_col in unit_df.columns and unit_df[safety_col].mean() < 3.0:
        anomalies.append({'id': 'TC3_A5', 'pattern': 'ATLĐ bị xem nhẹ',
                          'safety_score': round(unit_df[safety_col].mean(), 2),
                          'action': 'Ưu tiên cao — kiểm tra vật chất + NLP tìm "tai nạn", "nguy hiểm"'})
    return anomalies


def detect_TC4_anomalies(unit_df, company_thresholds, group_id, df_hris_full=None):
    anomalies = []
    # FIX #6: filter HRIS theo unit TRƯỚC khi dùng
    df_hris = get_unit_hris(unit_df, df_hris_full)

    t4 = company_thresholds.get('TC4_score', {})
    fr_t = company_thresholds.get('is_flight_risk_pct', {})

    income_col = get_item(group_id, 'income_fair')
    trans_col  = get_item(group_id, 'transparency')
    tc4_qs     = get_pillar_questions(group_id, 'TC4')

    # A1: Bất công cảm nhận
    if income_col and income_col in unit_df.columns:
        inc_mean = unit_df[income_col].mean()
        if _is_low(inc_mean, t4, 'p25'):
            r = {'id': 'TC4_A1', 'pattern': 'Bất công cảm nhận',
                 'perceived_fairness': round(inc_mean, 2)}
            if df_hris is not None and 'income_m' in df_hris.columns:
                unit_inc = df_hris['income_m'].mean()  # Đã filter → đúng unit
                company_median = company_thresholds.get('hris_income_median', None)
                r['unit_avg_income'] = round(unit_inc, 0)
                if company_median and unit_inc > company_median and _is_low(inc_mean, t4, 'p25'):
                    r['interpretation'] = '🔑 Thu nhập TRÊN median nhưng cảm nhận THẤP → vấn đề minh bạch'
            anomalies.append(r)

    # A2: Minh bạch kém
    if (trans_col and trans_col in unit_df.columns and
            income_col and income_col in unit_df.columns and
            trans_col != income_col):
        gap = unit_df[income_col].mean() - unit_df[trans_col].mean()
        if gap > 0.5:
            r = {'id': 'TC4_A2', 'pattern': 'Phạt/Phụ cấp không minh bạch',
                 'transparency': round(unit_df[trans_col].mean(), 2),
                 'income_fair': round(unit_df[income_col].mean(), 2),
                 'gap': round(gap, 2)}
            if df_hris is not None and 'tong_phat' in df_hris.columns:
                r['pct_penalized'] = round((df_hris['tong_phat'] > 0).mean() * 100, 1)
                r['avg_penalty']   = round(df_hris['tong_phat'].mean(), 0)
            anomalies.append(r)

    # A3: Tiền tốt vẫn nghỉ
    tc4_mean = unit_df['TC4_score'].mean() if 'TC4_score' in unit_df.columns else np.nan
    fr_pct   = unit_df['is_flight_risk'].mean() * 100 if 'is_flight_risk' in unit_df.columns else np.nan
    if _is_high(tc4_mean, t4) and _is_high(fr_pct, fr_t):
        anomalies.append({'id': 'TC4_A3', 'pattern': 'Thu nhập tốt, vẫn muốn nghỉ',
                          'tc4': round(tc4_mean, 1), 'flight_pct': round(fr_pct, 1),
                          'note': 'Tiền không phải nguyên nhân → deep dive TC2, TC5'})

    # A4: Hỗ trợ sự cố kém
    if tc4_qs:
        incident_col = get_item(group_id, 'incident_pay')
        if incident_col and incident_col in unit_df.columns:
            inc_pay = unit_df[incident_col].mean()
            tc4_means = {q: unit_df[q].mean() for q in tc4_qs if q in unit_df.columns}
            if tc4_means and min(tc4_means, key=tc4_means.get) == incident_col:
                anomalies.append({'id': 'TC4_A4', 'pattern': 'Hỗ trợ sự cố kém',
                                  'score': round(inc_pay, 2),
                                  'note': 'NLP: tìm "sự cố", "bồi thường", "không ai giúp"'})
    return anomalies


def detect_TC5_anomalies(unit_df, company_thresholds, group_id):
    anomalies = []
    bn_t = company_thresholds.get('burnout_score', {})
    ei_t = company_thresholds.get('EI', {})
    fr_t = company_thresholds.get('is_flight_risk_pct', {})
    rs_t = company_thresholds.get('respect_index', {})

    pride_col   = get_item(group_id, 'pride')
    peer_col    = get_item(group_id, 'peer')
    pressure_col= get_item(group_id, 'pressure')
    respect_col = get_item(group_id, 'respect')

    burnout_mean = unit_df['burnout_score'].mean() if 'burnout_score' in unit_df.columns else np.nan
    ei_mean      = unit_df['EI'].mean()             if 'EI' in unit_df.columns else np.nan

    # A1: Tự hào nhưng kiệt sức
    if pride_col and pride_col in unit_df.columns:
        if unit_df[pride_col].mean() > 3.8 and _is_high(burnout_mean, bn_t):
            anomalies.append({'id': 'TC5_A1', 'pattern': 'Tự hào nhưng kiệt sức',
                              'pride': round(unit_df[pride_col].mean(), 2),
                              'burnout': round(burnout_mean, 1),
                              'risk': 'Committed Under Pressure — sẽ flip nếu không can thiệp'})

    # A2: Social Glue Risk
    if peer_col and peer_col in unit_df.columns:
        if unit_df[peer_col].mean() > 3.8 and _is_low(ei_mean, ei_t):
            anomalies.append({'id': 'TC5_A2', 'pattern': 'Social Glue Risk',
                              'peer': round(unit_df[peer_col].mean(), 2), 'ei': round(ei_mean, 1),
                              'risk': 'Ở lại vì bạn — domino khi 1 người nghỉ'})

    # A3 + EWS: Onboarding Shock — FIX #5: dùng EWS_TENURE_THRESHOLD constant
    ews_thresh = EWS_TENURE_THRESHOLD.get(group_id, 2)
    if pressure_col and pressure_col in unit_df.columns and 'tenure' in unit_df.columns:
        new_mask = unit_df['tenure'] <= ews_thresh
        new_df   = unit_df[new_mask]
        if len(new_df) >= 3:
            new_pressure = new_df[pressure_col].mean()
            if new_pressure < 3.0:
                new_fr = new_df['is_flight_risk'].mean() * 100 if 'is_flight_risk' in new_df.columns else None
                anomalies.append({
                    'id': 'TC5_A3', 'pattern': 'Onboarding Shock — EWS',
                    'new_n': len(new_df), 'new_pressure': round(new_pressure, 2),
                    'new_flight_pct': round(new_fr, 1) if new_fr else None,
                    'ews_window': f'tenure ≤ index {ews_thresh} ({TENURE_LABELS[ews_thresh]})',
                    'action': '🚨 HRBP gặp nhóm này trong tuần này'
                })

    # A4: Burnout blind spot
    if pressure_col and pressure_col in unit_df.columns:
        if unit_df[pressure_col].mean() >= 3.8 and _is_high(burnout_mean, bn_t):
            anomalies.append({'id': 'TC5_A4', 'pattern': 'Burnout Blind Spot',
                              'perceived_ok': round(unit_df[pressure_col].mean(), 2),
                              'burnout': round(burnout_mean, 1),
                              'note': 'NV không nhận ra mình kiệt sức — normalize hóa áp lực'})

    # A5: Respect Deficit
    if respect_col and respect_col in unit_df.columns:
        if _is_low(unit_df[respect_col].mean(), rs_t):
            fr_pct = unit_df['is_flight_risk'].mean() * 100 if 'is_flight_risk' in unit_df.columns else None
            anomalies.append({'id': 'TC5_A5', 'pattern': 'Respect Deficit',
                              'respect': round(unit_df[respect_col].mean(), 2),
                              'flight_pct': round(fr_pct, 1) if fr_pct else None,
                              'note': '⚡ Strongest attrition predictor cho lao động trực tiếp'})
    return anomalies


def detect_cross_pillar_patterns(unit_df: pd.DataFrame,
                                   company_thresholds: dict,
                                   group_id: str) -> list:
    """
    FIX #7: Vectorized operations — không dùng iterrows()
    FIX #5: EWS dùng EWS_TENURE_THRESHOLD constant
    FIX #8: Health score dùng percentile rank, không phải trọng số tùy tiện
    """
    patterns = []
    t = company_thresholds

    def get_mean(col): return unit_df[col].mean() if col in unit_df.columns else np.nan
    def low(val, key, pkey='p25'): return not np.isnan(val) and val < t.get(key, {}).get(pkey, np.inf)
    def high(val, key, pkey='p75'): return not np.isnan(val) and val > t.get(key, {}).get(pkey, -np.inf)

    tc1 = get_mean('TC1_score'); tc2 = get_mean('TC2_score')
    tc3 = get_mean('TC3_score'); tc4 = get_mean('TC4_score'); tc5 = get_mean('TC5_score')
    ei  = get_mean('EI'); burnout = get_mean('burnout_score')
    fr  = unit_df['is_flight_risk'].mean() * 100 if 'is_flight_risk' in unit_df.columns else np.nan

    # XP_1: Committed Under Pressure
    if high(burnout, 'burnout_score') and low(fr, 'is_flight_risk_pct'):
        patterns.append({'id': 'XP_1', 'name': 'Committed Under Pressure',
                         'burnout': round(burnout, 1), 'flight_pct': round(fr, 1),
                         'urgency': 'HIGH', 'action': 'Workload review + 1-1 trước khi flip'})

    # XP_2: Silent Disengaged
    if low(ei, 'EI') and low(fr, 'is_flight_risk_pct'):
        patterns.append({'id': 'XP_2', 'name': 'Silent Disengaged — Quiet Quitting',
                         'ei': round(ei, 1), 'flight_pct': round(fr, 1),
                         'urgency': 'MEDIUM', 'action': 'Skip-level conversation để tìm nguyên nhân thật'})

    # XP_3: Manager Island
    if high(tc2, 'TC2_score') and low(ei, 'EI'):
        worst_pillars = sorted([('TC1',tc1),('TC3',tc3),('TC4',tc4),('TC5',tc5)],
                                key=lambda x: x[1] if not np.isnan(x[1]) else 999)[:2]
        patterns.append({'id': 'XP_3', 'name': 'Manager Island',
                         'tc2': round(tc2, 1), 'ei': round(ei, 1),
                         'weakest': worst_pillars, 'urgency': 'MEDIUM'})

    # XP_4: Flight Risk Cluster
    if high(fr, 'is_flight_risk_pct', 'p90'):
        patterns.append({'id': 'XP_4', 'name': '🚨 Flight Risk Cluster',
                         'flight_pct': round(fr, 1),
                         'urgency': 'CRITICAL', 'action': 'HRBP + Line Mgr gặp trong 48h'})

    # XP_5: Income Paradox
    if high(tc4, 'TC4_score') and low(ei, 'EI'):
        patterns.append({'id': 'XP_5', 'name': 'Income Paradox',
                         'tc4': round(tc4, 1), 'ei': round(ei, 1),
                         'note': 'Tiền không phải vấn đề — deep dive TC2, TC3, TC5',
                         'urgency': 'MEDIUM'})

    # XP_6: Onboarding Shock EWS — FIX #5: consistent window
    ews_thresh = EWS_TENURE_THRESHOLD.get(group_id, 2)
    if 'tenure' in unit_df.columns and 'is_flight_risk' in unit_df.columns:
        new_mask = unit_df['tenure'] <= ews_thresh
        new_df   = unit_df[new_mask]
        if len(new_df) >= 3:
            new_fr  = new_df['is_flight_risk'].mean() * 100
            new_tc2 = new_df['TC2_score'].mean() if 'TC2_score' in new_df.columns else np.nan
            if new_fr > 30 or low(new_tc2, 'TC2_score'):
                patterns.append({'id': 'XP_6', 'name': 'Onboarding Shock EWS',
                                 'new_n': len(new_df), 'new_flight_pct': round(new_fr, 1),
                                 'new_tc2': round(new_tc2, 1) if not np.isnan(new_tc2) else None,
                                 'window': TENURE_LABELS[ews_thresh],
                                 'urgency': 'HIGH', 'action': 'Kích hoạt 30-60-90 day program'})

    # XP_7: Tenure Cliff
    if 'tenure' in unit_df.columns and 'EI' in unit_df.columns:
        tenure_ei = unit_df.groupby('tenure')['EI'].mean().reindex(range(len(TENURE_LABELS)))
        tenure_ei = tenure_ei.dropna()
        if len(tenure_ei) >= 4:
            diffs = tenure_ei.diff().dropna()
            cliff_idx_int = int(diffs.idxmin())
            cliff_val = float(diffs.min())
            if cliff_val < -15:
                patterns.append({'id': 'XP_7', 'name': 'Tenure Cliff',
                                 'cliff_at': TENURE_LABELS[cliff_idx_int] if cliff_idx_int < len(TENURE_LABELS) else cliff_idx_int,
                                 'ei_drop': round(cliff_val, 1), 'urgency': 'MEDIUM'})

    # XP_8: Generation Gap
    if 'gen3' in unit_df.columns:
        pillar_cols = [c for c in ['TC1_score','TC2_score','TC3_score','TC4_score','TC5_score']
                       if c in unit_df.columns]
        gen_scores = unit_df.groupby('gen3')[pillar_cols].mean()
        if 'Gen Z' in gen_scores.index and 'Gen X' in gen_scores.index:
            gap_series = gen_scores.loc['Gen X'] - gen_scores.loc['Gen Z']
            sig_pillars = gap_series[gap_series > 20].index.tolist()
            if len(sig_pillars) >= 2:
                patterns.append({'id': 'XP_8', 'name': 'Generation Gap Systemic',
                                 'significant_pillars': sig_pillars,
                                 'gen_z': gen_scores.loc['Gen Z'].round(1).to_dict(),
                                 'gen_x': gen_scores.loc['Gen X'].round(1).to_dict(),
                                 'urgency': 'MEDIUM'})

    # XP_9: Engagement Quadrant — FIX #7: vectorized, no iterrows
    # FIX: dùng EI × eNPS (không phải attrition × eNPS như v1)
    if 'EI' in unit_df.columns and 'eNPS_raw' in unit_df.columns:
        ei_median = t.get('EI', {}).get('p50', unit_df['EI'].median())
        conditions = [
            (unit_df['EI'] >= ei_median) & (unit_df['eNPS_raw'] >= ENPS_PROMOTER_MIN),
            (unit_df['EI'] <  ei_median) & (unit_df['eNPS_raw'] >= ENPS_PROMOTER_MIN),
            (unit_df['EI'] >= ei_median) & (unit_df['eNPS_raw'] <= ENPS_DETRACTOR_MAX),
        ]
        choices = ['Champions', 'Trapped Loyalists', 'Confused Leavers']
        quad = pd.Series(np.select(conditions, choices, default='Flight Risk'), index=unit_df.index)
        dist = quad.value_counts()
        patterns.append({'id': 'XP_9', 'name': 'Engagement Quadrant',
                         'distribution': dist.to_dict(),
                         'pct': (dist / len(quad) * 100).round(1).to_dict(),
                         'note': 'Dùng EI × eNPS (không phải attrition × eNPS)'})

    # XP_10: Contradiction Index (Fear-based compliance)
    silence_rate = t.get('_silence_all_3_skip', 0)
    if high(ei, 'EI') and silence_rate > 50:
        patterns.append({'id': 'XP_10', 'name': 'Contradiction Index',
                         'ei': round(ei, 1), 'silence_rate': silence_rate,
                         'note': 'EI cao + Silence cao → sợ nói thật', 'urgency': 'CHECK'})

    # XP_11: Quiet Exodus
    if low(burnout, 'burnout_score', 'p25') and high(fr, 'is_flight_risk_pct'):
        pillar_scores = {p: v for p, v in
                         [('TC1',tc1),('TC2',tc2),('TC3',tc3),('TC4',tc4),('TC5',tc5)]
                         if not np.isnan(v)}
        root = min(pillar_scores, key=pillar_scores.get) if pillar_scores else 'Unknown'
        patterns.append({'id': 'XP_11', 'name': 'Quiet Exodus',
                         'flight_pct': round(fr, 1), 'burnout': round(burnout, 1),
                         'likely_root': root,
                         'root_score': round(pillar_scores.get(root, 0), 1),
                         'urgency': 'HIGH'})

    return patterns


# ---- 6.1 Unit Health Score — FIX #8: percentile rank ----

def compute_unit_health(unit_df: pd.DataFrame,
                         company_distributions: dict) -> dict:
    """
    FIX #8: Dùng percentile rank so với GHN distribution.
    Không còn trọng số tùy tiện (0.5/0.3/0.2).
    100 = tốt nhất trong công ty, 0 = tệ nhất.
    """
    def pct_rank(val, dist_array):
        if np.isnan(val) or dist_array is None:
            return None
        return round(float(scipy_stats.percentileofscore(dist_array, val)), 1)

    ei_dist       = company_distributions.get('EI')
    burnout_dist  = company_distributions.get('burnout_score')
    flight_dist   = company_distributions.get('is_flight_risk')

    ei_val      = unit_df['EI'].mean() if 'EI' in unit_df.columns else np.nan
    burnout_val = unit_df['burnout_score'].mean() if 'burnout_score' in unit_df.columns else np.nan
    flight_val  = unit_df['is_flight_risk'].mean() * 100 if 'is_flight_risk' in unit_df.columns else np.nan

    return {
        'EI_percentile':      pct_rank(ei_val, ei_dist),           # cao = tốt
        'burnout_percentile': 100 - (pct_rank(burnout_val, burnout_dist) or 0),  # cao = tốt
        'retention_percentile': 100 - (pct_rank(flight_val, flight_dist) or 0),  # cao = tốt
        'note': 'Percentile rank within GHN. Không thể so sánh across years nếu distribution thay đổi.'
    }


def run_full_anomaly_scan(unit_df, company_thresholds, group_id,
                           df_hris_full=None, company_distributions=None) -> dict:
    """Entry point duy nhất. Chạy toàn bộ scan cho một unit."""
    return {
        'group_id': group_id, 'unit_n': len(unit_df),
        'pillar_anomalies': {
            'TC1': detect_TC1_anomalies(unit_df, company_thresholds, group_id),
            'TC2': detect_TC2_anomalies(unit_df, company_thresholds, group_id),
            'TC3': detect_TC3_anomalies(unit_df, company_thresholds, group_id),
            'TC4': detect_TC4_anomalies(unit_df, company_thresholds, group_id, df_hris_full),
            'TC5': detect_TC5_anomalies(unit_df, company_thresholds, group_id),
        },
        'cross_pillar_patterns': detect_cross_pillar_patterns(unit_df, company_thresholds, group_id),
        'health_score': compute_unit_health(unit_df, company_distributions or {}),
        'priority_actions': [
            p for p in detect_cross_pillar_patterns(unit_df, company_thresholds, group_id)
            if p.get('urgency') in ('CRITICAL', 'HIGH')
        ]
    }



# ─────────────────────────────────────────────────────────────
# MAIN DISPATCHER
# ─────────────────────────────────────────────────────────────

PILLAR_DETECTORS = {
    'TC1': detect_TC1_anomalies,
    'TC2': detect_TC2_anomalies,
    'TC3': detect_TC3_anomalies,
    'TC4': detect_TC4_anomalies,
    'TC5': detect_TC5_anomalies,
}

def detect_pillar_anomalies(df, group_id, pillar_id, company_thresholds=None, df_hris=None):
    detector = PILLAR_DETECTORS.get(pillar_id)
    if detector is None or df is None or df.empty:
        return []
    try:
        if company_thresholds is None:
            from utils.data_loader import compute_relative_thresholds
            company_thresholds = compute_relative_thresholds(df, group_id)
        if pillar_id == 'TC4':
            return detector(df, company_thresholds, group_id, df_hris)
        return detector(df, company_thresholds, group_id)
    except Exception as e:
        return [{'id': 'ERROR', 'pillar': pillar_id, 'severity': 'watch',
                 'title': 'Lỗi phân tích', 'message': str(e), 'data': {}, 'action': ''}]

def detect_cross_pillar(df, group_id=''):
    from utils.data_loader import compute_relative_thresholds
    company_thresholds = compute_relative_thresholds(df, group_id)
    return detect_cross_pillar_patterns(df, company_thresholds, group_id)

def detect_all_anomalies(df, group_id, company_thresholds=None):
    all_anomalies = []
    if company_thresholds is None:
        from utils.data_loader import compute_relative_thresholds
        company_thresholds = compute_relative_thresholds(df, group_id)
    for pid in ['TC1', 'TC2', 'TC3', 'TC4', 'TC5']:
        all_anomalies.extend(detect_pillar_anomalies(df, group_id, pid, company_thresholds))
    all_anomalies.extend(detect_cross_pillar(df, group_id))
    order = {'critical': 0, 'warning': 1, 'watch': 2}
    return sorted(all_anomalies, key=lambda x: order.get(x.get('severity', 'watch'), 3))
