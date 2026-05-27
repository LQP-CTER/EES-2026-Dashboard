"""
Workforce Mapper — EES 2026
Map survey data → Division / Department / Section
bằng cách kết nối với file Google Sheets Workforce Data và Mapping.
Logic được kế thừa từ dự án EES-TRACKING để loại bỏ triệt để 'Không xác định'.
"""
import pandas as pd
import os
import unicodedata
import re
import streamlit as st

# ══════════════════════════════════════════════════════════════
# CONSTANTS & HELPERS
# ══════════════════════════════════════════════════════════════
try:
    WF_SHEET_ID = st.secrets.get("WF_SHEET_ID", "1wiv9c12jnSe7QFbqD-SHQo2tOWMD5My0pyE5JbmtYkU")
except Exception:
    WF_SHEET_ID = "1wiv9c12jnSe7QFbqD-SHQo2tOWMD5My0pyE5JbmtYkU"

# Các cột string trong workforce — thứ tự ưu tiên khi search
WF_STR_COLS = [
    "section_name_vn", "section_name",
    "department_name_vn", "department_name",
    "team_name_vn", "team_name",
    "division_name_vn", "division_name",
    "group_name",
]

def _norm(s):
    if s is None or pd.isna(s): return ""
    s = unicodedata.normalize("NFD", str(s).strip().lower())
    return re.sub(r"[^a-z0-9]", "", "".join(c for c in s if unicodedata.category(c) != "Mn"))

def _clean(v):
    if v is None: return None
    s = str(v).strip()
    return None if s in ("", "nan", "None") else s

def _find_col(df: pd.DataFrame, *keywords) -> str | None:
    """Tìm cột đầu tiên trong df có chứa bất kỳ keyword nào (case-insensitive)."""
    for col in df.columns:
        cl = str(col).lower()
        if any(k.lower() in cl for k in keywords):
            return col
    return None

# ══════════════════════════════════════════════════════════════
# LOAD WORKFORCE + MAPPING
# ══════════════════════════════════════════════════════════════
@st.cache_data(ttl=3600, show_spinner="Đang tải Workforce & Mapping…")
def load_workforce_and_mapping() -> tuple[pd.DataFrame, dict, dict]:
    import time
    export_url = f"https://docs.google.com/spreadsheets/d/{WF_SHEET_ID}/export?format=xlsx"
    
    df_wf = pd.DataFrame()
    df_map = pd.DataFrame()
    
    for attempt in range(3):
        try:
            try:
                df_wf = pd.read_excel(export_url, sheet_name="Workforce Data", engine="calamine")
                df_map = pd.read_excel(export_url, sheet_name="Mapping", engine="calamine")
            except ImportError:
                df_wf = pd.read_excel(export_url, sheet_name="Workforce Data")
                df_map = pd.read_excel(export_url, sheet_name="Mapping")
            break
        except Exception as e:
            if attempt == 2:
                print(f"Lỗi tải Workforce: {e}")
            else:
                time.sleep(2)

    # ── Chuẩn hóa workforce ──
    if df_wf.empty:
        return df_wf, {}, {}

    df_wf = df_wf.dropna(how="all").copy()
    df_wf.columns = [str(c).strip() for c in df_wf.columns]
    for col in WF_STR_COLS + ["bu_name", "survey_group", "jobtitle_name"]:
        if col not in df_wf.columns: df_wf[col] = None
        df_wf[col] = df_wf[col].astype(str).str.strip().replace(["nan", "", "None"], None)
    df_wf["status"] = pd.to_numeric(df_wf.get("status", pd.Series()), errors="coerce")

    # ── Hierarchical Fill to resolve missing classifications ──
    for c_div, c_dept, c_sec in [
        ("division_name_vn", "department_name_vn", "section_name_vn"),
        ("division_name", "department_name", "section_name")
    ]:
        if c_div in df_wf.columns and c_dept in df_wf.columns:
            df_wf[c_dept] = df_wf[c_dept].fillna(df_wf[c_div])
        if c_dept in df_wf.columns and c_sec in df_wf.columns:
            df_wf[c_sec] = df_wf[c_sec].fillna(df_wf[c_dept])

    # Bắt buộc ép Vận hành GXT về Giao Hàng Nặng (Vận hành B2B)
    mask_gxt = (
        df_wf.get("department_name_vn", pd.Series(dtype=str)).str.contains("Vận hành GXT", case=False, na=False) |
        df_wf.get("section_name_vn", pd.Series(dtype=str)).str.contains("Vận hành GXT", case=False, na=False) |
        df_wf.get("department_name", pd.Series(dtype=str)).str.contains("Vận hành GXT", case=False, na=False) |
        df_wf.get("section_name", pd.Series(dtype=str)).str.contains("Vận hành GXT", case=False, na=False) |
        df_wf.get("team_name_vn", pd.Series(dtype=str)).str.contains("Vận hành GXT", case=False, na=False) |
        df_wf.get("team_name", pd.Series(dtype=str)).str.contains("Vận hành GXT", case=False, na=False)
    )
    if "division_name" in df_wf.columns:
        df_wf.loc[mask_gxt, "division_name"] = "Giao Hàng Nặng (Vận hành B2B)"
    if "division_name_vn" in df_wf.columns:
        df_wf.loc[mask_gxt, "division_name_vn"] = "Giao Hàng Nặng (Vận hành B2B)"

    # Tách KTC Dương Xá ra khỏi KTC Đài Tư dựa trên group_name (Cho nhóm khảo sát 2A)
    if "group_name" in df_wf.columns:
        mask_duong_xa = df_wf["group_name"].astype(str).str.contains("Dương Xá", case=False, na=False)
        if "section_name_vn" in df_wf.columns:
            df_wf.loc[mask_duong_xa, "section_name_vn"] = "Cụm Kho Trung Chuyển Dương Xá"
        if "section_name" in df_wf.columns:
            df_wf.loc[mask_duong_xa, "section_name"] = "Cụm Kho Trung Chuyển Dương Xá"

    # Thêm 13 HC ảo cho nhóm Future Makers thuộc khối Freight (Khảo sát 3A)
    fm_rows = pd.DataFrame([{
        "division_name_vn": "Dự Án Freight",
        "division_name": "Freight Project",
        "department_name_vn": "Future Makers",
        "department_name": "Future Makers",
        "section_name_vn": "Future Makers",
        "section_name": "Future Makers",
        "survey_group": "3A",
        "status": 1
    }] * 13)
    df_wf = pd.concat([df_wf, fm_rows], ignore_index=True)

    # ── Parse Mapping sheet ──
    MAP_2AB: dict[str, tuple[str, str|None]] = {}  # sv_val → (wf_value, wf_col|None)
    MAP_3AB: dict[str, tuple[str,str]] = {}  # sv_val → (wf_col, wf_val)

    if len(df_map) > 0:
        cols = list(df_map.columns)
        
        idx_2ab = next((i for i, c in enumerate(cols) if '2A-2B' in str(c)), 0)
        if idx_2ab + 2 < len(cols):
            col_indices = [idx_2ab, idx_2ab+1, idx_2ab+2]
            has_wf_col = idx_2ab + 3 < len(cols)
            if has_wf_col:
                col_indices.append(idx_2ab+3)
            sub2 = df_map.iloc[:, col_indices].copy()
            if has_wf_col:
                sub2.columns = ["sv2a","sv2b","wf_val","wf_col"]
            else:
                sub2.columns = ["sv2a","sv2b","wf_val"]
                sub2["wf_col"] = None
            sub2 = sub2.dropna(subset=["wf_val"])
            sub2 = sub2[~sub2["sv2a"].astype(str).str.strip().isin(["Survey-2A",""])]
            for _, r in sub2.iterrows():
                wf = _clean(str(r["wf_val"]))
                if not wf: continue
                wf_col = _clean(str(r["wf_col"])) if pd.notna(r.get("wf_col")) else None
                for sv_raw in [r["sv2a"], r["sv2b"]]:
                    sv = _clean(str(sv_raw))
                    if sv: MAP_2AB[sv] = (wf, wf_col)

        idx_3ab = next((i for i, c in enumerate(cols) if '3A-3B' in str(c)), 4)
        if idx_3ab + 2 < len(cols):
            sub3 = df_map.iloc[:, [idx_3ab, idx_3ab+1, idx_3ab+2]].copy()
            sub3.columns = ["sv","wf_val","wf_col"]
            sub3 = sub3.dropna(subset=["sv","wf_val","wf_col"])
            sub3 = sub3[~sub3["sv"].astype(str).str.strip().isin(["Survey-3A-3B",""])]
            for _, r in sub3.iterrows():
                sv  = _clean(str(r["sv"]))
                wfv = _clean(str(r["wf_val"]))
                wfc = _clean(str(r["wf_col"]))
                if sv and wfv and wfc:
                    MAP_3AB[sv] = (wfc, wfv)

    return df_wf, MAP_2AB, MAP_3AB

# ══════════════════════════════════════════════════════════════
# BUILD WF LOOKUP — tìm trên TẤT CẢ cột string
# ══════════════════════════════════════════════════════════════
def build_wf_lookup(df_wf: pd.DataFrame) -> tuple[dict, dict, dict]:
    lookup_exact = {}
    lookup_fallback = {}
    emp_lookup = {}

    for row in df_wf.to_dict('records'):
        info = {
            "wf_division":   row.get("division_name"),
            "wf_division_vn": row.get("division_name_vn"),
            "wf_department": row.get("department_name"),
            "wf_department_vn": row.get("department_name_vn"),
            "wf_section":    row.get("section_name"),
            "wf_section_vn": row.get("section_name_vn"),
            "wf_team":       row.get("team_name"),
            "wf_jobtitle":   row.get("jobtitle_name"),
            "wf_jobtitle_vn": row.get("jobtitle_name_vn"),
            "survey_group":  row.get("survey_group"),
        }
        for c in ["employee_id", "emp_id", "emp_code", "mã nhân viên"]:
            if c in row:
                val = str(row[c]).strip()
                if val.endswith(".0"): val = val[:-2]
                if val and val.lower() not in ("nan", "none", ""):
                    emp_lookup[val] = info
                    emp_lookup[val.lower()] = info

    for col in WF_STR_COLS:
        if col not in df_wf.columns: continue
        grp = df_wf[df_wf[col].notna()].groupby(col, dropna=False)
        for val, rows in grp:
            v = str(val).strip()
            if not v or v in ("nan","None",""): continue
            
            most_freq_divs = rows["division_name_vn"].mode()
            if not most_freq_divs.empty and pd.notna(most_freq_divs.iloc[0]):
                r0 = rows[rows["division_name_vn"] == most_freq_divs.iloc[0]].iloc[0]
            else:
                r0 = rows.iloc[0]
                
            info = {
                "wf_division":   r0.get("division_name"),
                "wf_division_vn": r0.get("division_name_vn"),
                "wf_department": r0.get("department_name"),
                "wf_department_vn": r0.get("department_name_vn"),
                "wf_section":    r0.get("section_name"),
                "wf_section_vn": r0.get("section_name_vn"),
            }
            
            v_norm = _norm(v)
            if (col, v_norm) not in lookup_exact:
                lookup_exact[(col, v_norm)] = info
            if v_norm not in lookup_fallback:
                lookup_fallback[v_norm] = info

    return lookup_exact, lookup_fallback, emp_lookup

# ══════════════════════════════════════════════════════════════
# MAIN MAPPING LOGIC
# ══════════════════════════════════════════════════════════════
def extract_sv_label(row, group, df_columns):
    """
    Tái tạo logic extract sv_label của ees-tracking cho dashboard đã rename cột.
    Chúng ta dùng df_columns (cột gốc từ df_raw) nếu có thể, 
    nhưng thường row chứa keys là giá trị.
    """
    sv_label = None
    sv_vung = None
    is_appdriver = False
    
    # Hàm phụ trợ để quét key chứa keyword
    def _find_val(*keywords):
        for k, v in row.items():
            kl = str(k).lower()
            if any(kw in kl for kw in keywords):
                val = _clean(v)
                if val is not None:
                    return val
        return None

    if group in ["1A", "1B"]:
        is_appdriver = True
        sv_label = _find_val("id nhân viên", "employee id")
        sv_vung = _find_val("vùng")
    elif group in ["2A", "2B"]:
        pb = _find_val("phòng ban")
        ktc = _find_val("ktc", "ttct", "tttc")
        sme = _find_val("bưu cục kinh doanh")
        
        # Tìm col gxt, wh, vung
        col_gxt, col_wh, col_vung = None, None, None
        for c in row.keys():
            cl = str(c).lower()
            if "vùng" in cl and "phòng ban bạn đang" not in cl and col_vung is None: col_vung = c
            elif "bộ phận nào" in cl:
                if col_gxt is None: col_gxt = c
                elif col_wh is None: col_wh = c
            elif ("warehouse" in cl or "fulfillment" in cl or "khl" in cl or "kho vận" in cl) and col_wh is None:
                col_wh = c
        
        if pb:
            pl = pb.lower()
            if "warehouse" in pl or "fulfillment" in pl: sv_label = _clean(row[col_wh]) if col_wh else None
            elif "giao hàng nặng" in pl or "b2b" in pl: sv_label = _clean(row[col_gxt]) if col_gxt else None
            elif "sme" in pl or "bưu cục kinh doanh" in pl: sv_label = sme
            elif ("kho trung chuyển" in pl or "ktc" in pl or "tttc" in pl) and "vùng" not in pl and "bưu cục" not in pl:
                sv_label = ktc
            elif "gxt" in pl: sv_label = pb
            else: sv_label = _clean(row[col_vung]) if col_vung else None
            
            if not sv_label: sv_label = pb
    elif group in ["3A", "3B"]:
        # Logic giống ees-tracking: scan TẤT CẢ cột "Bạn thuộc?" (col 8..13)
        # để tìm giá trị cụ thể nhất (phòng ban/section), không chỉ cột đầu tiên.
        thuoc_cols = [
            k for k in row.keys()
            if "bạn thuộc" in str(k).lower()
            and "gắn bó" not in str(k).lower()
            and "thuộc về" not in str(k).lower()
        ]
        for col in thuoc_cols:
            v = _clean(row[col])
            if v:
                sv_label = v
                break

        # Fallback: lấy Division lớn từ cột phòng ban / khối
        if not sv_label:
            pb_cols = [
                k for k in row.keys()
                if ("phòng ban" in str(k).lower() or "khối" in str(k).lower())
                and "cơ cấu" not in str(k).lower()
                and "khối lượng" not in str(k).lower()
            ]
            for c_pb in pb_cols:
                v = _clean(row[c_pb])
                if v:
                    sv_label = v
                    break

    return sv_label, sv_vung, is_appdriver

_REGION_CODE_MAP = {
    "hno": "Vùng HNO", "dsh": "Vùng DSH", "xbg": "Vùng XBG",
    "tnt": "Vùng TNT", "dbb": "Vùng DBB", "tbb": "Vùng TBB",
    "btb": "Vùng BTB", "ttb": "Vùng TTB", "tng": "Vùng TNG",
    "ntb": "Vùng NTB", "dnb": "Vùng DNB", "tnb": "Vùng TNB",
    "đcl": "Vùng ĐCL", "dcl": "Vùng ĐCL", "hcm": "Vùng HCM",
}

_VUNG_EXTENDED_MAP = {
    "freight operations - hcm": ("Bộ Phận Vận Hành HCM", "Bộ Phận Vận Hành HCM"),
    "freight operations - hn": ("Bộ Phận Vận Hành HN", "Bộ Phận Vận Hành HN"),
    "b2b operations department - central": ("Phòng Vận Hành B2B Miền Trung", "Giao Hàng Nặng (Vận hành B2B)"),
    "b2b operations department - eastern": ("Phòng Vận Hành B2B Miền Đông", "Giao Hàng Nặng (Vận hành B2B)"),
    "b2b operations department - western": ("Phòng Vận Hành B2B Miền Tây", "Giao Hàng Nặng (Vận hành B2B)"),
    "b2b operations department - north 1": ("Phòng Vận Hành B2B Miền Bắc 1", "Giao Hàng Nặng (Vận hành B2B)"),
    "b2b operations department - north 2": ("Phòng Vận Hành B2B Miền Bắc 2", "Giao Hàng Nặng (Vận hành B2B)"),
    "b2b operations department - north 3": ("Phòng Vận Hành B2B Miền Bắc 3", "Giao Hàng Nặng (Vận hành B2B)"),
    "b2b operations department - hcm": ("Phòng Vận Hành B2B HCM", "Giao Hàng Nặng (Vận hành B2B)"),
    "b2b operations department - hn": ("Phòng Vận Hành B2B HN", "Giao Hàng Nặng (Vận hành B2B)"),
    "project 2x": ("Chưa xác định", "Chưa xác định"),
}

def map_survey_to_org(df, group='1A', vung_col=None, id_col=None, raw_df=None):
    """
    Sử dụng df thô (raw_df) để lấy đúng column names cho mapping.
    """
    df_result = df.copy()
    
    # 1. Load data
    df_wf, MAP_2AB, MAP_3AB = load_workforce_and_mapping()
    if df_wf.empty:
        df_result['division'] = 'Chưa xác định'
        df_result['department'] = 'Chưa xác định'
        df_result['section'] = 'Chưa xác định'
        return df_result
        
    lookup_exact, lookup_fallback, emp_lookup = build_wf_lookup(df_wf)
    
    map2ab_norm = {_norm(k): v for k, v in MAP_2AB.items()}
    map3ab_norm = {_norm(k): v for k, v in MAP_3AB.items()}
    
    # Dùng raw_df để extract nếu có
    source_df = raw_df if raw_df is not None else df_result
    
    divs, depts, secs = [], [], []
    for i in range(len(df_result)):
        row_raw = source_df.iloc[i].to_dict()
        
        sv_val, sv_vung, is_app = extract_sv_label(row_raw, group, source_df.columns)
        
        # Nếu không extract được mà có id_col, fallback for 1A/1B
        if not sv_val and is_app and id_col and id_col in row_raw:
            sv_val = str(row_raw[id_col])
        if not sv_vung and is_app and vung_col and vung_col in row_raw:
            sv_vung = str(row_raw[vung_col])
            
        wf_info = {}
        
        if is_app:
            emp_id = sv_val
            wf_info = emp_lookup.get(emp_id) or emp_lookup.get(str(emp_id).lower()) or {}
            if not wf_info:
                if sv_vung:
                    sv_vung_lower = sv_vung.lower().replace(" region", "").strip()
                    mapped_vung = None
                    
                    import re
                    match = re.search(r'\((.*?)\)', sv_vung_lower)
                    if match:
                        code = match.group(1).strip()
                        mapped_vung = _REGION_CODE_MAP.get(code)
                        
                    if not mapped_vung:
                        mapped_vung = _REGION_CODE_MAP.get(sv_vung_lower)
                        
                    if not mapped_vung:
                        for k, v in _REGION_CODE_MAP.items():
                            if f" {k} " in f" {sv_vung_lower} ":
                                mapped_vung = v
                                break
                                
                    ext_match = _VUNG_EXTENDED_MAP.get(sv_vung.lower().strip())
                    
                    if mapped_vung:
                        vung_norm = _norm(mapped_vung)
                        wf_info = lookup_fallback.get(vung_norm, {})
                        if not wf_info:
                            wf_info = {"wf_division_vn": "Vùng", "wf_department_vn": mapped_vung, "wf_section_vn": mapped_vung}
                    elif ext_match:
                        dept_name, div_name = ext_match
                        dept_norm = _norm(dept_name)
                        wf_info = lookup_fallback.get(dept_norm, {})
                        if not wf_info:
                            wf_info = {"wf_division_vn": div_name, "wf_department_vn": dept_name, "wf_section_vn": dept_name}
                    else:
                        sv_vung_norm = _norm(sv_vung)
                        mapped_entry = map2ab_norm.get(sv_vung_norm)
                        if mapped_entry:
                            mapped_wf_val, mapped_wf_col = mapped_entry
                            if mapped_wf_col:
                                wf_info = lookup_exact.get((mapped_wf_col, _norm(mapped_wf_val)), {})
                            if not wf_info:
                                wf_info = lookup_fallback.get(_norm(mapped_wf_val), {})
                        else:
                            wf_info = lookup_fallback.get(sv_vung_norm, {})
        elif sv_val:
            sv_norm = _norm(sv_val)
            if group in ("1A", "1B", "2A", "2B"):
                mapped_entry = map2ab_norm.get(sv_norm)
                if mapped_entry:
                    wf_val, wf_col = mapped_entry
                    if wf_col:
                        wf_info = lookup_exact.get((wf_col, _norm(wf_val)), {})
                    if not wf_info:
                        wf_info = lookup_fallback.get(_norm(wf_val), {})
                else:
                    wf_info = lookup_fallback.get(sv_norm, {})
                    
            if not wf_info and group in ("2A", "2B"):
                if "sme" in sv_norm or "buucuckinhdoanh" in sv_norm:
                    wf_info = {"wf_division_vn": "Khối Thị Trường", "wf_department_vn": "Phòng Phát Triển Kinh Doanh Khách Hàng Vừa Và Nhỏ", "wf_section_vn": "Phòng Phát Triển Kinh Doanh Khách Hàng Vừa Và Nhỏ"}
                elif "gxt" in sv_norm or "giaohangnang" in sv_norm or "b2b" in sv_norm:
                    wf_info = {"wf_division_vn": "Giao Hàng Nặng (Vận hành B2B)", "wf_department_vn": "Phòng Vận Hành B2B", "wf_section_vn": "Phòng Vận Hành B2B"}
                elif "ktc" in sv_norm or "tttc" in sv_norm:
                    wf_info = {"wf_division_vn": "Khối Thị Trường", "wf_department_vn": "Kho Trung Chuyển", "wf_section_vn": sv_val}
                elif "warehouse" in sv_norm or "fulfillment" in sv_norm:
                    wf_info = {"wf_division_vn": "Khối Thị Trường", "wf_department_vn": "Warehouse/Fulfillment", "wf_section_vn": sv_val}
                elif sv_vung or ("vung" in sv_norm):
                    v_str = sv_vung if sv_vung else sv_val
                    import re
                    sv_vung_lower = v_str.lower().replace(" region", "").strip()
                    mapped_vung = None
                    match = re.search(r'\((.*?)\)', sv_vung_lower)
                    if match:
                        code = match.group(1).strip()
                        mapped_vung = _REGION_CODE_MAP.get(code)
                    if not mapped_vung:
                        mapped_vung = _REGION_CODE_MAP.get(sv_vung_lower)
                    if not mapped_vung:
                        for k, v in _REGION_CODE_MAP.items():
                            if f" {k} " in f" {sv_vung_lower} ":
                                mapped_vung = v
                                break
                    if mapped_vung:
                        wf_info = {"wf_division_vn": "Vùng", "wf_department_vn": mapped_vung, "wf_section_vn": mapped_vung}
                    else:
                        ext_match = _VUNG_EXTENDED_MAP.get(sv_vung_lower)
                        if ext_match:
                            dept_name, div_name = ext_match
                            wf_info = {"wf_division_vn": div_name, "wf_department_vn": dept_name, "wf_section_vn": dept_name}

            elif group in ("3A","3B"):
                base_cands = [sv_val]
                if "-" in sv_val:
                    for p in sv_val.split("-"): base_cands.append(p.strip())
                candidates = []
                for c in base_cands:
                    candidates.append(c)
                    if "(" in c: candidates.append(c.split("(")[0].strip())
                
                for cand in candidates:
                    c_norm = _norm(cand)
                    mapping = map3ab_norm.get(c_norm)
                    if mapping:
                        wf_col, wf_val = mapping
                        wf_col_norm = wf_col.strip()
                        wf_info = lookup_exact.get((wf_col_norm, _norm(wf_val)))
                        if not wf_info:
                            wf_info = lookup_fallback.get(_norm(wf_val), {})
                    else:
                        wf_info = lookup_fallback.get(c_norm, {})
                    if wf_info: break
                
                # Hardcoded fallback cho các giá trị 3A/3B không có trong MAP_3AB
                if not wf_info and sv_val:
                    _3AB_HARDCODED = {
                        "hrbp freight": {"wf_division_vn": "Khối Nhân Lực", "wf_department_vn": "Phòng Đối Tác Nhân Sự", "wf_section_vn": "HRBP Freight"},
                        "hrbp market": {"wf_division_vn": "Khối Nhân Lực", "wf_department_vn": "Phòng Đối Tác Nhân Sự", "wf_section_vn": "HRBP Market"},
                        "hrbp customer": {"wf_division_vn": "Khối Nhân Lực", "wf_department_vn": "Phòng Đối Tác Nhân Sự", "wf_section_vn": "HRBP Customer"},
                        "hrbp technology": {"wf_division_vn": "Khối Nhân Lực", "wf_department_vn": "Phòng Đối Tác Nhân Sự", "wf_section_vn": "HRBP Technology"},
                        "technology operations department": {"wf_division_vn": "Khối Công Nghệ", "wf_department_vn": "Technology Operations Department", "wf_section_vn": "Technology Operations Department"},
                    }
                    wf_info = _3AB_HARDCODED.get(sv_val.strip().lower(), {})
                    
        # Gán default là Chưa xác định nếu map fail
        div_val = wf_info.get("wf_division_vn")
        dept_val = wf_info.get("wf_department_vn")
        sec_val = wf_info.get("wf_section_vn")
        
        divs.append(div_val if div_val and str(div_val).lower() not in ["", "nan", "none"] else 'Chưa xác định')
        depts.append(dept_val if dept_val and str(dept_val).lower() not in ["", "nan", "none"] else 'Chưa xác định')
        secs.append(sec_val if sec_val and str(sec_val).lower() not in ["", "nan", "none"] else 'Chưa xác định')
        
    df_result['division'] = divs
    df_result['department'] = depts
    df_result['section'] = secs

    # ── Post-process: chuẩn hóa section theo từng nhóm ──

    # Các dòng không map được (Chưa xác định) → set None để groupby tự bỏ qua.
    _BAD_MAP = {'Chưa xác định', 'Không xác định', 'Khác', 'nan', 'None', ''}
    for col in ['division', 'department', 'section']:
        df_result[col] = df_result[col].replace({v: None for v in _BAD_MAP})
        df_result[col] = df_result[col].where(df_result[col].notna(), None)

    # Nhóm 2A/2B: lọc bỏ section cấp KTC quá chi tiết nếu department đã là KTC tổng
    if group in ('2A', '2B'):
        def _clean_2ab_section(row):
            sec = row.get('section', '')
            dept = row.get('department', '')
            if not sec or not dept:
                return sec
            sec_l = str(sec).lower()
            dept_l = str(dept).lower()
            # Nếu section = tên cụm KTC cụ thể nhưng dept đã là "Kho Trung Chuyển" → dùng dept
            if ('cụm' in sec_l or 'cum' in sec_l) and 'kho trung chuyển' in dept_l:
                return dept
            return sec
        df_result['section'] = df_result.apply(_clean_2ab_section, axis=1)

    # ── Nhóm 1A / 1B: loại bỏ các department không thuộc scope Shipper/Tài xế ──
    # Nguyên nhân: employee lookup WF trả về HR classification thực tế của người đó
    # nhưng họ điền form khảo sát nhầm nhóm (1A = Shipper, 1B = Tài xế).
    # Department "Kho Trung Chuyển" không thuộc nhóm Shipper/Tài xế → set về None.
    if group in ('1A', '1B'):
        _WRONG_DEPTS_1AB = {'Kho Trung Chuyển'}
        mask_wrong = df_result['department'].isin(_WRONG_DEPTS_1AB)
        if mask_wrong.any():
            df_result.loc[mask_wrong, 'department'] = None
            df_result.loc[mask_wrong, 'section'] = None

    return df_result

def get_org_summary(df):
    """Tạo summary table: Division > Department > Section > N."""
    summary = []
    for div, g_div in df.groupby('division'):
        for dept, g_dept in g_div.groupby('department'):
            for sec, g_sec in g_dept.groupby('section'):
                summary.append({
                    'Division': div, 'Department': dept, 'Section': sec,
                    'N': len(g_sec),
                })
    return pd.DataFrame(summary).sort_values(['Division', 'Department', 'Section'])
