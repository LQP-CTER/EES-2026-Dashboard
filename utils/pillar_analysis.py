"""Pillar-specific analysis profiles and lightweight evidence builders."""

from __future__ import annotations

import numpy as np
import pandas as pd

from shared.codebook import get_question_label, get_role_question
from utils.segment_risk import MIN_SEGMENT_N, scan_risk_segments, slice_segment


PILLAR_ANALYSIS_PROFILES = {
    "TC1": {
        "lens": "Niềm tin có được chuyển thành sự rõ ràng và sẵn sàng đồng hành hay không?",
        "focus": "Phân biệt vấn đề niềm tin vào định hướng với đứt gãy truyền thông.",
        "roles": ["info_trust", "info_timely"],
        "contrasts": [
            ("info_trust", "info_timely", "Khoảng cách niềm tin - thông tin"),
        ],
        "outcomes": [("eNPS", "eNPS"), ("intent", "Ý định ở lại"), ("EI", "EI")],
        "risk_weights": {"pillar": 0.38, "enps": 0.27, "flight": 0.20, "ei": 0.15},
        "driver": "Đứt gãy niềm tin hoặc truyền thông lãnh đạo",
        "actions": {
            "info_trust": ("Ban Điều hành", "Làm rõ 3 quyết định chiến lược đang tạo nhiều hoài nghi và công bố nguyên tắc ra quyết định."),
            "info_timely": ("Internal Communications + Unit Head", "Thiết lập SLA truyền thông thay đổi và kiểm tra mức độ tiếp nhận tại đơn vị có điểm thấp."),
        },
        "anomaly_focus": "Tìm nghịch lý tin lãnh đạo nhưng thiếu thông tin, hoặc niềm tin cao nhưng ý định nghỉ vẫn lớn.",
    },
    "TC2": {
        "lens": "Trải nghiệm quản lý đang yếu ở hỗ trợ, công bằng hay phản hồi?",
        "focus": "Đo manager effect và xác định hành vi quản lý tạo ra chênh lệch giữa các đơn vị.",
        "roles": ["mgr_support", "mgr_fairness", "mgr_feedback"],
        "contrasts": [
            ("mgr_support", "mgr_fairness", "Hỗ trợ - công bằng"),
            ("mgr_support", "mgr_feedback", "Hỗ trợ - phản hồi"),
        ],
        "outcomes": [("MEI", "MEI"), ("intent", "Ý định ở lại"), ("EI", "EI")],
        "risk_weights": {"pillar": 0.38, "mei": 0.27, "flight": 0.20, "ei": 0.15},
        "driver": "Chất lượng quản lý trực tiếp không đồng đều",
        "actions": {
            "mgr_support": ("Unit Head", "Chuẩn hóa cơ chế escalation và thời gian phản hồi khi nhân viên cần hỗ trợ."),
            "mgr_fairness": ("Ops + HRBP", "Audit phân ca, phân việc và quyết định quản lý tại các đơn vị có fairness thấp."),
            "mgr_feedback": ("People Manager", "Triển khai check-in ngắn định kỳ, có phản hồi hai chiều và ghi nhận hành vi cụ thể."),
        },
        "anomaly_focus": "Tìm manager island, bất công trong phân bổ và trường hợp MEI cao nhưng vẫn không giữ được người.",
    },
    "TC3": {
        "lens": "Điểm nghẽn nằm ở công cụ, tải công việc, thay đổi hay cơ hội phát triển?",
        "focus": "Tách ma sát vận hành hằng ngày khỏi khoảng trống phát triển dài hạn.",
        "roles": ["tool", "workload", "change_guide", "career"],
        "contrasts": [
            ("tool", "workload", "Công cụ - tải công việc"),
            ("change_guide", "career", "Thích ứng thay đổi - phát triển"),
        ],
        "outcomes": [("JSI", "JSI"), ("burnout_score", "Burnout"), ("intent", "Ý định ở lại")],
        "risk_weights": {"pillar": 0.34, "burnout": 0.32, "flight": 0.19, "ei": 0.15},
        "driver": "Ma sát công việc và lộ trình phát triển",
        "actions": {
            "tool": ("Product/Tech + Ops", "Chốt danh sách ba lỗi công cụ gây mất thời gian nhiều nhất và công bố owner, ETA xử lý."),
            "workload": ("Ops Owner", "Rà tải công việc, lịch/ca và điểm nghẽn quy trình tại cohort burnout cao."),
            "change_guide": ("Process Owner", "Mọi thay đổi phải có thông báo trước, SOP và người hỗ trợ trong giai đoạn chuyển đổi."),
            "career": ("HRBP + Functional Head", "Mở career conversation cho nhóm thâm niên đang có điểm phát triển thấp."),
        },
        "anomaly_focus": "Tìm burnout ẩn, công cụ cản trở, tenure cliff và thay đổi quy trình thiếu hướng dẫn.",
    },
    "TC4": {
        "lens": "Bất mãn đến từ mức thu nhập, cảm nhận công bằng hay thiếu minh bạch?",
        "focus": "Không đồng nhất vấn đề đãi ngộ với vấn đề hiểu và tin vào cách tính.",
        "roles": ["income_fair", "transparency", "incident_support"],
        "contrasts": [
            ("income_fair", "transparency", "Công bằng - minh bạch"),
            ("transparency", "incident_support", "Minh bạch - xử lý sự cố"),
        ],
        "outcomes": [("intent", "Ý định ở lại"), ("eNPS", "eNPS"), ("EI", "EI")],
        "risk_weights": {"pillar": 0.38, "flight": 0.30, "enps": 0.20, "ei": 0.12},
        "driver": "Cảm nhận công bằng và minh bạch thu nhập",
        "actions": {
            "income_fair": ("C&B + Business Owner", "Đối chiếu nhóm công việc tương đồng và giải thích rõ nguyên tắc công bằng trong đãi ngộ."),
            "transparency": ("C&B + Product", "Viết lại cách hiển thị cấu phần thu nhập, phụ cấp và khấu trừ theo ngôn ngữ người dùng."),
            "incident_support": ("Ops Finance", "Thiết lập SLA và đầu mối xử lý các sự cố ảnh hưởng trực tiếp đến thu nhập."),
        },
        "anomaly_focus": "Tìm pay fairness gap, thiếu minh bạch và trường hợp thu nhập không giải thích được flight risk.",
    },
    "TC5": {
        "lens": "Gắn kết đang được nâng đỡ bởi tự hào và đồng đội, hay bị bào mòn bởi áp lực?",
        "focus": "Đọc đồng thời belonging, peer support, pride và sức chịu đựng của nhân viên.",
        "roles": ["peer", "pride", "pressure"],
        "contrasts": [
            ("pride", "pressure", "Tự hào - áp lực"),
            ("peer", "pressure", "Hỗ trợ đồng đội - áp lực"),
        ],
        "outcomes": [("eNPS", "eNPS"), ("burnout_score", "Burnout"), ("intent", "Ý định ở lại")],
        "risk_weights": {"pillar": 0.32, "burnout": 0.30, "enps": 0.23, "flight": 0.15},
        "driver": "Belonging, tự hào và sức khỏe gắn kết",
        "actions": {
            "peer": ("Unit Head", "Xác định điểm đứt gãy phối hợp và giao một owner xử lý ma sát giữa các nhóm liên quan."),
            "pride": ("Leadership + Internal Communications", "Kết nối đóng góp của đơn vị với kết quả khách hàng bằng bằng chứng cụ thể, không chỉ truyền thông khẩu hiệu."),
            "pressure": ("Unit Head + HRBP", "Rà workload, nhịp làm việc và nguồn gây áp lực tại cohort có burnout cao nhất."),
        },
        "anomaly_focus": "Tìm pride-burnout paradox, thiếu belonging và nhóm vẫn tự hào nhưng đã gần cạn sức.",
    },
}


ROLE_LABELS = {
    "info_trust": "Niềm tin vào định hướng",
    "info_timely": "Thông tin kịp thời",
    "mgr_support": "Quản lý hỗ trợ",
    "mgr_fairness": "Quản lý công bằng",
    "mgr_feedback": "Phản hồi và ghi nhận",
    "tool": "Công cụ và hệ thống",
    "workload": "Tải công việc",
    "change_guide": "Hướng dẫn thay đổi",
    "career": "Cơ hội phát triển",
    "income_fair": "Công bằng thu nhập",
    "transparency": "Minh bạch cách tính",
    "incident_support": "Hỗ trợ sự cố",
    "peer": "Hỗ trợ đồng đội",
    "pride": "Tự hào và thuộc về",
    "pressure": "Áp lực bền vững",
}


def get_analysis_profile(pillar_id: str) -> dict:
    return PILLAR_ANALYSIS_PROFILES[pillar_id]


def build_role_scorecard(df: pd.DataFrame, group_id: str, pillar_id: str) -> pd.DataFrame:
    rows = []
    seen_questions = set()
    for role in get_analysis_profile(pillar_id)["roles"]:
        question = get_role_question(group_id, role)
        if not question or question not in df.columns or question in seen_questions:
            continue
        seen_questions.add(question)
        values = pd.to_numeric(df[question], errors="coerce").dropna()
        if len(values) < 5:
            continue
        rows.append({
            "Vai trò": role,
            "Tín hiệu": ROLE_LABELS.get(role, role),
            "Câu hỏi": question,
            "Nội dung": get_question_label(group_id, question),
            "Điểm TB": round(float(values.mean()), 2),
            "% Tích cực": round(float((values >= 4).mean() * 100), 1),
            "% Tiêu cực": round(float((values <= 2).mean() * 100), 1),
            "N": int(len(values)),
        })
    if not rows:
        return pd.DataFrame()
    return pd.DataFrame(rows).sort_values(["Điểm TB", "% Tiêu cực"], ascending=[True, False])


def build_contrast_evidence(df: pd.DataFrame, group_id: str, pillar_id: str) -> pd.DataFrame:
    rows = []
    profile = get_analysis_profile(pillar_id)
    for left_role, right_role, title in profile["contrasts"]:
        left_q = get_role_question(group_id, left_role)
        right_q = get_role_question(group_id, right_role)
        if (
            not left_q or not right_q or left_q == right_q
            or left_q not in df.columns or right_q not in df.columns
        ):
            continue
        left = pd.to_numeric(df[left_q], errors="coerce").dropna()
        right = pd.to_numeric(df[right_q], errors="coerce").dropna()
        if len(left) < 5 or len(right) < 5:
            continue
        left_mean = float(left.mean())
        right_mean = float(right.mean())
        gap = left_mean - right_mean
        rows.append({
            "Đối chiếu": title,
            "Vế 1": ROLE_LABELS.get(left_role, left_role),
            "Điểm 1": round(left_mean, 2),
            "Vế 2": ROLE_LABELS.get(right_role, right_role),
            "Điểm 2": round(right_mean, 2),
            "Khoảng cách": round(abs(gap), 2),
            "Tín hiệu yếu hơn": ROLE_LABELS.get(right_role if gap > 0 else left_role, right_role if gap > 0 else left_role),
            "Mức tín hiệu": "Rõ" if abs(gap) >= 0.4 else "Theo dõi" if abs(gap) >= 0.2 else "Cân bằng",
        })
    return pd.DataFrame(rows)


def build_outcome_links(df: pd.DataFrame, group_id: str, pillar_id: str) -> pd.DataFrame:
    scorecard = build_role_scorecard(df, group_id, pillar_id)
    questions = scorecard["Câu hỏi"].tolist() if not scorecard.empty else []
    if not questions:
        return pd.DataFrame()

    pillar_score = df[questions].apply(pd.to_numeric, errors="coerce").mean(axis=1)
    rows = []
    for column, label in get_analysis_profile(pillar_id)["outcomes"]:
        if column in df.columns:
            outcome = pd.to_numeric(df[column], errors="coerce")
        elif column == "burnout_score" and "burnout_proxy" in df.columns:
            outcome = df["burnout_proxy"].map({
                True: 1.0, False: 0.0,
                "True": 1.0, "False": 0.0,
                "true": 1.0, "false": 0.0,
                1: 1.0, 0: 0.0,
            })
        elif column == "burnout_score" and "burnout_risk" in df.columns:
            outcome = pd.to_numeric(df["burnout_risk"], errors="coerce")
        else:
            continue
        valid = pillar_score.notna() & outcome.notna()
        if valid.sum() < 30 or pillar_score.loc[valid].nunique() < 2 or outcome.loc[valid].nunique() < 2:
            continue
        correlation = float(pillar_score.loc[valid].corr(outcome.loc[valid], method="spearman"))
        if np.isnan(correlation):
            continue
        rows.append({
            "Kết quả liên quan": label,
            "Tương quan Spearman": round(correlation, 3),
            "N": int(valid.sum()),
            "Mức bằng chứng": "Mạnh" if abs(correlation) >= 0.5 else "Vừa" if abs(correlation) >= 0.3 else "Yếu",
        })
    return pd.DataFrame(rows).sort_values("Tương quan Spearman", key=lambda s: s.abs(), ascending=False) if rows else pd.DataFrame()


def build_specialized_risk_segments(df: pd.DataFrame, group_id: str, pillar_id: str, top_n: int = 12) -> pd.DataFrame:
    base = scan_risk_segments(df, pillar_filter=pillar_id, min_n=MIN_SEGMENT_N, top_n=40)
    if base.empty:
        return base

    profile = get_analysis_profile(pillar_id)
    weights = profile["risk_weights"]
    pillar_col = f"Điểm {pillar_id} (%)"
    role_questions = []
    for role in profile["roles"]:
        question = get_role_question(group_id, role)
        if question and question in df.columns and question not in role_questions:
            role_questions.append(question)

    if pillar_col not in base.columns or base[pillar_col].isna().all():
        derived_scores = []
        for _, row in base.iterrows():
            segment = slice_segment(df, row["_segment_col"], row["_segment_value"])
            if not role_questions:
                derived_scores.append(np.nan)
                continue
            score_5 = segment[role_questions].apply(pd.to_numeric, errors="coerce").mean(axis=1).mean()
            derived_scores.append((float(score_5) - 1) / 4 * 100 if not pd.isna(score_5) else np.nan)
        base[pillar_col] = derived_scores

    def deficit(series, midpoint=100):
        values = pd.to_numeric(series, errors="coerce")
        return (midpoint - values).clip(lower=0).fillna(0)

    empty_metric = pd.Series(np.nan, index=base.index, dtype=float)
    score = pd.Series(0.0, index=base.index)
    score += deficit(base.get(pillar_col, empty_metric)) * weights.get("pillar", 0)
    score += deficit(base.get("EI (%)", empty_metric)) * weights.get("ei", 0)
    score += pd.to_numeric(base.get("% Muốn nghỉ", empty_metric), errors="coerce").fillna(0) * weights.get("flight", 0)
    score += pd.to_numeric(base.get("% Burnout", empty_metric), errors="coerce").fillna(0) * weights.get("burnout", 0)
    score += (-pd.to_numeric(base.get("eNPS", empty_metric), errors="coerce").fillna(0)).clip(lower=0) * weights.get("enps", 0)
    score += deficit(base.get("MEI (%)", empty_metric)) * weights.get("mei", 0)

    result = base.copy()
    result["Risk Score chuyên biệt"] = score.round(1)
    result = result.sort_values(
        ["Risk Score chuyên biệt", "N"],
        ascending=[False, False],
    ).head(top_n).reset_index(drop=True)
    diagnoses = []
    owners = []
    actions = []
    for _, row in result.iterrows():
        segment = slice_segment(df, row["_segment_col"], row["_segment_value"])
        segment_scorecard = build_role_scorecard(segment, group_id, pillar_id)
        if segment_scorecard.empty:
            weakest_role = profile["roles"][0]
            weakest_signal = profile["driver"]
        else:
            weakest = segment_scorecard.iloc[0]
            weakest_role = weakest["Vai trò"]
            weakest_signal = f"{weakest['Tín hiệu']} thấp ({weakest['Điểm TB']:.2f}/5)"
        owner, action = profile["actions"].get(
            weakest_role,
            ("Pillar Owner", "Xác minh nguyên nhân tại segment trước khi can thiệp."),
        )
        diagnoses.append(weakest_signal)
        owners.append(owner)
        actions.append(action)
    result["Chẩn đoán trọng tâm"] = diagnoses
    result["Owner đề xuất"] = owners
    result["Hành động đầu tiên"] = actions
    return result


def build_action_evidence(df: pd.DataFrame, group_id: str, pillar_id: str) -> dict:
    profile = get_analysis_profile(pillar_id)
    scorecard = build_role_scorecard(df, group_id, pillar_id)
    contrasts = build_contrast_evidence(df, group_id, pillar_id)
    outcomes = build_outcome_links(df, group_id, pillar_id)

    if scorecard.empty:
        return {"enabled": False, "profile": profile}

    weakest = scorecard.iloc[0].to_dict()
    owner, action = profile["actions"].get(
        weakest["Vai trò"],
        ("Pillar Owner", "Xác minh nguyên nhân tại các nhóm có điểm thấp trước khi chốt hành động."),
    )
    return {
        "enabled": True,
        "profile": profile,
        "weakest": weakest,
        "top_contrast": contrasts.sort_values("Khoảng cách", ascending=False).iloc[0].to_dict() if not contrasts.empty else None,
        "top_outcome": outcomes.iloc[0].to_dict() if not outcomes.empty else None,
        "owner": owner,
        "action": action,
        "confidence": "Tín hiệu định lượng đủ mẫu" if weakest["N"] >= 30 else "Tín hiệu cần theo dõi",
    }
