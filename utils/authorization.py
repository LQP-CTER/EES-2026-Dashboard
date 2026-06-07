import os
import re
from typing import Optional
from urllib.parse import quote

import pandas as pd
import streamlit as st


DEFAULT_AUTHORIZATION_TAB = "Authorization"


def _get_secret_or_env(key: str, default: str = "") -> str:
    try:
        value = st.secrets.get(key, "")
        if value:
            return str(value)
    except Exception:
        pass
    return os.environ.get(key, default)


def _normalize_header(value: str) -> str:
    value = str(value or "").strip().lower()
    value = re.sub(r"[\s\-]+", "_", value)
    return value


def _normalize_text(value: str) -> str:
    return str(value or "").strip()


def _authorization_csv_url() -> str:
    explicit_url = _get_secret_or_env("AUTHORIZATION_SHEET_URL")
    if explicit_url:
        return explicit_url

    sheet_id = _get_secret_or_env("AUTHORIZATION_SHEET_ID")
    if not sheet_id:
        raise ValueError(
            "Thiếu AUTHORIZATION_SHEET_ID hoặc AUTHORIZATION_SHEET_URL trong secrets.toml / environment."
        )

    tab_name = _get_secret_or_env("AUTHORIZATION_TAB", DEFAULT_AUTHORIZATION_TAB)
    return f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={quote(tab_name)}"


@st.cache_data(ttl=300, show_spinner=False)
def load_authorization_table() -> pd.DataFrame:
    """Load active dashboard authorization rows from Google Sheets."""
    df = pd.read_csv(_authorization_csv_url())
    df = df.dropna(how="all")
    df.columns = [_normalize_header(c) for c in df.columns]

    required = {"email", "status"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Authorization sheet thiếu cột bắt buộc: {', '.join(sorted(missing))}")

    for col in ["email", "status", "role", "division", "department", "section", "survey_view", "full_name", "idnv", "job_title"]:
        if col not in df.columns:
            df[col] = ""
        df[col] = df[col].fillna("").map(_normalize_text)

    df["email_norm"] = df["email"].str.lower()
    df["status_norm"] = df["status"].str.upper()
    df["role_norm"] = df["role"].str.upper()
    df["survey_view_norm"] = df["survey_view"].str.upper()
    return df


def get_authorized_user(email: str) -> Optional[dict]:
    """Return authorization scope for an ACTIVE email, or None when blocked."""
    email_norm = str(email or "").strip().lower()
    if not email_norm:
        return None

    df = load_authorization_table()
    matched = df[(df["email_norm"] == email_norm) & (df["status_norm"] == "ACTIVE")]
    if matched.empty:
        return None

    first = matched.iloc[0]
    return {
        "email": email_norm,
        "idnv": first.get("idnv", ""),
        "full_name": first.get("full_name", ""),
        "job_title": first.get("job_title", ""),
        "role": first.get("role", "User") or "User",
        "divisions": sorted({v for v in matched["division"].tolist() if v}),
        "departments": sorted({v for v in matched["department"].tolist() if v}),
        "sections": sorted({v for v in matched["section"].tolist() if v}),
        "survey_view": sorted({v for v in matched["survey_view_norm"].tolist() if v}) or ["ALL"],
        "rows": len(matched),
    }


def is_authorized_email(email: str) -> bool:
    return get_authorized_user(email) is not None


# ══════════════════════════════════════════════════════════════
# DATA SCOPE — giới hạn data 1 user được xem theo cấp tổ chức
# ══════════════════════════════════════════════════════════════
def _norm_compare(value: str) -> str:
    """Chuẩn hóa để so khớp tên đơn vị: bỏ hoa/thường + gộp khoảng trắng."""
    return re.sub(r"\s+", " ", str(value or "").strip().lower())


# survey_view (CẤP phân quyền) → (tên cột trong scope, tên cột data trong df)
_SCOPE_LEVELS = {
    "SECTION": ("sections", "section"),
    "DEPARTMENT": ("departments", "department"),
    "PHONG_BAN": ("departments", "department"),
    "DIVISION": ("divisions", "division"),
    "KHOI": ("divisions", "division"),
}


def resolve_data_scope(authorization: Optional[dict]) -> dict:
    """Xác định phạm vi data 1 user được phép xem.

    Trả về dict:
        {'unrestricted': bool, 'level': str|None, 'column': str|None, 'values': list,
         'misconfigured': bool}

    - Admin hoặc survey_view rỗng/ALL  → unrestricted (xem hết).
    - survey_view = SECTION/DEPARTMENT/DIVISION → giới hạn theo cột tương ứng.
    - survey_view có cấp nhưng KHÔNG có giá trị đơn vị → misconfigured (fail-closed).
    """
    if not authorization:
        return {"unrestricted": True, "level": None, "column": None, "values": [], "misconfigured": False}

    role = str(authorization.get("role", "")).strip().upper()
    if role == "ADMIN":
        return {"unrestricted": True, "level": None, "column": None, "values": [], "misconfigured": False}

    views = [str(v).strip().upper() for v in authorization.get("survey_view", []) if str(v).strip()]
    if not views or "ALL" in views:
        return {"unrestricted": True, "level": None, "column": None, "values": [], "misconfigured": False}

    # Ưu tiên cấp HẸP nhất nếu khai báo nhiều cấp: Section > Department > Division
    for level_key in ("SECTION", "DEPARTMENT", "PHONG_BAN", "DIVISION", "KHOI"):
        if level_key in views:
            scope_field, df_col = _SCOPE_LEVELS[level_key]
            values = [v for v in authorization.get(scope_field, []) if str(v).strip()]
            if values:
                return {"unrestricted": False, "level": level_key, "column": df_col,
                        "values": values, "misconfigured": False}
            # Có cấp nhưng thiếu giá trị → fail-closed
            return {"unrestricted": False, "level": level_key, "column": df_col,
                    "values": [], "misconfigured": True}

    # survey_view có giá trị lạ không nhận diện được → fail-closed cho an toàn
    return {"unrestricted": False, "level": None, "column": None, "values": [], "misconfigured": True}


def apply_scope_filter(df, authorization):
    """Lọc df theo phạm vi của user. Trả về (df_đã_lọc, scope_dict).

    - unrestricted        → trả về df nguyên vẹn.
    - có scope hợp lệ      → chỉ giữ các dòng khớp column ∈ values (so khớp chuẩn hóa).
    - misconfigured / cột không tồn tại trong df → trả về df rỗng (fail-closed).
    """
    scope = resolve_data_scope(authorization)
    if scope["unrestricted"]:
        return df, scope
    if df is None:
        return df, scope

    col = scope["column"]
    values = scope["values"]
    if scope["misconfigured"] or not col or not values or col not in df.columns:
        return df.iloc[0:0].copy(), scope

    targets = {_norm_compare(v) for v in values}
    mask = df[col].map(lambda x: _norm_compare(x) in targets)
    return df[mask].copy(), scope
