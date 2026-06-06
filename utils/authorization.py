import os
import re
from typing import Optional
from urllib.parse import quote

import pandas as pd
import streamlit as st


DEFAULT_AUTHORIZATION_SHEET_ID = "14rVdX0b5N9XZFM61juba5XU38x07pFC9wZR_1XQsrho"
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

    sheet_id = _get_secret_or_env("AUTHORIZATION_SHEET_ID", DEFAULT_AUTHORIZATION_SHEET_ID)
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

    for col in ["email", "status", "role", "department", "section", "survey_view", "full_name", "idnv", "job_title"]:
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
        "departments": sorted({v for v in matched["department"].tolist() if v}),
        "sections": sorted({v for v in matched["section"].tolist() if v}),
        "survey_view": sorted({v for v in matched["survey_view_norm"].tolist() if v}) or ["ALL"],
        "rows": len(matched),
    }


def is_authorized_email(email: str) -> bool:
    return get_authorized_user(email) is not None
