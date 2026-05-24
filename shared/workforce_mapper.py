"""
Workforce Mapper — EES 2026
Map survey data → Division / Department / Section
bằng cách khớp Employee ID hoặc Vùng → Workforce Google Sheets.
"""
import pandas as pd
import os
import unicodedata
import re

# ══════════════════════════════════════════════════════════════
# CONSTANTS
# ══════════════════════════════════════════════════════════════
WF_SHEET_ID = '1pyNwximXg0aZzahEroGdenxnUIRe1XWbnMy_YRULAn0'
WF_EXPORT_URL = f'https://docs.google.com/spreadsheets/d/{WF_SHEET_ID}/export?format=xlsx'

CACHE_DIR = os.path.join(os.path.dirname(__file__), '..', 'Data', 'Cache')

# Vùng → Section/Division mapping cho nhóm 1A (shipper theo vùng)
VUNG_TO_ORG = {
    # 14 Vùng vận hành chính
    'HNO Region': {'division': 'Vùng Vận Hành', 'department': 'Miền Bắc', 'section': 'Vùng HNO'},
    'HNO': {'division': 'Vùng Vận Hành', 'department': 'Miền Bắc', 'section': 'Vùng HNO'},
    'DSH Region': {'division': 'Vùng Vận Hành', 'department': 'Miền Bắc', 'section': 'Vùng DSH'},
    'DSH': {'division': 'Vùng Vận Hành', 'department': 'Miền Bắc', 'section': 'Vùng DSH'},
    'XBG Region': {'division': 'Vùng Vận Hành', 'department': 'Miền Bắc', 'section': 'Vùng XBG'},
    'XBG': {'division': 'Vùng Vận Hành', 'department': 'Miền Bắc', 'section': 'Vùng XBG'},
    'DBB Region': {'division': 'Vùng Vận Hành', 'department': 'Miền Bắc', 'section': 'Vùng DBB'},
    'DBB': {'division': 'Vùng Vận Hành', 'department': 'Miền Bắc', 'section': 'Vùng DBB'},
    'TBB Region': {'division': 'Vùng Vận Hành', 'department': 'Miền Bắc', 'section': 'Vùng TBB'},
    'TBB': {'division': 'Vùng Vận Hành', 'department': 'Miền Bắc', 'section': 'Vùng TBB'},
    'TNT Region': {'division': 'Vùng Vận Hành', 'department': 'Miền Trung', 'section': 'Vùng TNT'},
    'TNT': {'division': 'Vùng Vận Hành', 'department': 'Miền Trung', 'section': 'Vùng TNT'},
    'BTB Region': {'division': 'Vùng Vận Hành', 'department': 'Miền Trung', 'section': 'Vùng BTB'},
    'BTB': {'division': 'Vùng Vận Hành', 'department': 'Miền Trung', 'section': 'Vùng BTB'},
    'TTB Region': {'division': 'Vùng Vận Hành', 'department': 'Miền Trung', 'section': 'Vùng TTB'},
    'TTB': {'division': 'Vùng Vận Hành', 'department': 'Miền Trung', 'section': 'Vùng TTB'},
    'NTB Region': {'division': 'Vùng Vận Hành', 'department': 'Miền Nam', 'section': 'Vùng NTB'},
    'NTB': {'division': 'Vùng Vận Hành', 'department': 'Miền Nam', 'section': 'Vùng NTB'},
    'TNG Region': {'division': 'Vùng Vận Hành', 'department': 'Miền Nam', 'section': 'Vùng TNG'},
    'TNG': {'division': 'Vùng Vận Hành', 'department': 'Miền Nam', 'section': 'Vùng TNG'},
    'HCM Region': {'division': 'Vùng Vận Hành', 'department': 'Miền Nam', 'section': 'Vùng HCM'},
    'HCM': {'division': 'Vùng Vận Hành', 'department': 'Miền Nam', 'section': 'Vùng HCM'},
    'DNB Region': {'division': 'Vùng Vận Hành', 'department': 'Miền Nam', 'section': 'Vùng DNB'},
    'DNB': {'division': 'Vùng Vận Hành', 'department': 'Miền Nam', 'section': 'Vùng DNB'},
    'TNB Region': {'division': 'Vùng Vận Hành', 'department': 'Miền Tây', 'section': 'Vùng TNB'},
    'TNB': {'division': 'Vùng Vận Hành', 'department': 'Miền Tây', 'section': 'Vùng TNB'},
    'ĐCL Region': {'division': 'Vùng Vận Hành', 'department': 'Miền Tây', 'section': 'Vùng ĐCL'},
    'ĐCL': {'division': 'Vùng Vận Hành', 'department': 'Miền Tây', 'section': 'Vùng ĐCL'},

    # B2B Operations
    'B2B Operations Department - Central': {'division': 'Giao Hàng Nặng (B2B)', 'department': 'VH B2B Miền Trung', 'section': 'B2B Central'},
    'B2B Operations Department - Eastern': {'division': 'Giao Hàng Nặng (B2B)', 'department': 'VH B2B Miền Đông', 'section': 'B2B Eastern'},
    'B2B Operations Department - Western': {'division': 'Giao Hàng Nặng (B2B)', 'department': 'VH B2B Miền Tây', 'section': 'B2B Western'},
    'B2B Operations Department - North 1': {'division': 'Giao Hàng Nặng (B2B)', 'department': 'VH B2B Miền Bắc', 'section': 'B2B North 1'},
    'B2B Operations Department - North 2': {'division': 'Giao Hàng Nặng (B2B)', 'department': 'VH B2B Miền Bắc', 'section': 'B2B North 2'},
    'B2B Operations Department - North 3': {'division': 'Giao Hàng Nặng (B2B)', 'department': 'VH B2B Miền Bắc', 'section': 'B2B North 3'},

    # Freight
    'Freight Operations - HCM': {'division': 'Dự Án Freight', 'department': 'Freight HCM', 'section': 'Freight HCM'},
    'Freight Operations - HN': {'division': 'Dự Án Freight', 'department': 'Freight HN', 'section': 'Freight HN'},

    # Project 2X
    'Project 2X': {'division': 'Dự Án Đặc Biệt', 'department': 'Project 2X', 'section': 'Project 2X'},
}

# 1B mapping (Tài xế — theo linehaul team)
VUNG_TO_ORG_1B = {
    # Sẽ được populate từ dữ liệu thực tế
}


def _norm(s):
    """Normalize string for matching."""
    s = unicodedata.normalize('NFD', str(s).strip().lower())
    return re.sub(r'[^a-z0-9]', '', ''.join(c for c in s if unicodedata.category(c) != 'Mn'))


def load_workforce(cache=True):
    """Download Workforce data from Google Sheets, with caching."""
    os.makedirs(CACHE_DIR, exist_ok=True)
    cache_file = os.path.join(CACHE_DIR, 'workforce.parquet')

    if cache and os.path.exists(cache_file):
        # Check if cache is fresh (< 24h)
        import time
        age = time.time() - os.path.getmtime(cache_file)
        if age < 86400:
            return pd.read_parquet(cache_file)

    try:
        df = pd.read_excel(WF_EXPORT_URL, sheet_name='Workforce Data', engine='openpyxl')
        df.columns = [str(c).strip() for c in df.columns]
        try:
            df.to_parquet(cache_file)
        except Exception:
            pass
        return df
    except Exception as e:
        print(f'⚠️ Không tải được Workforce: {e}')
        if os.path.exists(cache_file):
            return pd.read_parquet(cache_file)
        return pd.DataFrame()


def normalize_vung(raw_value):
    """
    Normalize Vùng gốc → chuẩn hóa.
    'HCM Region' → 'HCM', 'HCM' → 'HCM', NaN → None.
    """
    if raw_value is None or (isinstance(raw_value, float) and pd.isna(raw_value)):
        return None
    v = str(raw_value).strip()
    if v.lower() in ('nan', 'none', ''):
        return None
    # Remove trailing " Region" (case insensitive)
    if v.lower().endswith(' region'):
        v = v[:-len(' Region')].strip()
    return v


# Tạo lookup nhanh từ VUNG_TO_ORG — key đã normalize
_VUNG_LOOKUP = {}
for raw_key, org_info in VUNG_TO_ORG.items():
    # Lưu cả raw key và key đã bỏ " Region"
    _VUNG_LOOKUP[raw_key.strip()] = org_info
    if raw_key.strip().endswith(' Region'):
        _VUNG_LOOKUP[raw_key.strip()[:-len(' Region')].strip()] = org_info


def map_survey_to_org(df, group='1A', vung_col=None, id_col=None):
    """
    Map survey DataFrame → thêm cột division, department, section.

    Bước 1: Normalize cột Vùng (HCM Region → HCM, loại whitespace, NaN)
    Bước 2: Map qua VUNG_TO_ORG → Division/Department/Section
    Bước 3: Fallback qua Employee ID → Workforce lookup
    """
    df = df.copy()

    # Detect vùng column
    if vung_col is None:
        for c in df.columns:
            if 'vùng' in str(c).lower() or 'vung' in str(c).lower():
                vung_col = c
                break
        if vung_col is None:
            vung_col = df.columns[10] if len(df.columns) > 10 else None

    mapping = _VUNG_LOOKUP if group == '1A' else VUNG_TO_ORG_1B

    if vung_col and vung_col in df.columns:
        # Bước 1: Normalize
        df['_vung_norm'] = df[vung_col].apply(normalize_vung)

        # Bước 2: Map
        df['division'] = df['_vung_norm'].map(
            lambda v: mapping.get(v, {}).get('division', 'Chưa xác định') if v else 'Chưa xác định')
        df['department'] = df['_vung_norm'].map(
            lambda v: mapping.get(v, {}).get('department', 'Chưa xác định') if v else 'Chưa xác định')
        df['section'] = df['_vung_norm'].map(
            lambda v: mapping.get(v, {}).get('section', v or 'Chưa xác định') if v else 'Chưa xác định')

        # Log unmapped
        unmapped = df[df['division'] == 'Chưa xác định']['_vung_norm'].dropna().unique()
        if len(unmapped) > 0:
            print(f'⚠️ {len(unmapped)} giá trị Vùng chưa được map: {list(unmapped)[:10]}')

        df.drop(columns=['_vung_norm'], inplace=True)
    else:
        df['division'] = 'Chưa xác định'
        df['department'] = 'Chưa xác định'
        df['section'] = 'Chưa xác định'

    # Bước 3: Employee ID fallback cho rows chưa map
    if id_col and id_col in df.columns:
        try:
            df_wf = load_workforce()
            if len(df_wf) > 0:
                wf_id_col = None
                for c in df_wf.columns:
                    if 'employee_id' in c.lower() or 'emp_id' in c.lower():
                        wf_id_col = c
                        break
                if wf_id_col:
                    # Drop duplicate employee IDs to prevent ValueError in to_dict('index')
                    df_wf_clean = df_wf.drop_duplicates(subset=[wf_id_col])
                    wf_lookup = df_wf_clean.set_index(wf_id_col)[
                        ['division_name_vn', 'department_name_vn', 'section_name_vn']
                    ].to_dict('index')
                    
                    mask = df['division'] == 'Chưa xác định'
                    for idx in df[mask].index:
                        emp_id = df.loc[idx, id_col]
                        if pd.notna(emp_id):
                            try:
                                # Convert float or string representations of integers safely
                                emp_id_int = int(float(emp_id))
                                info = wf_lookup.get(emp_id_int) or wf_lookup.get(str(emp_id_int))
                            except (ValueError, TypeError):
                                info = wf_lookup.get(emp_id) or wf_lookup.get(str(emp_id))
                                
                            if info:
                                df.loc[idx, 'division'] = info.get('division_name_vn', 'Chưa xác định')
                                df.loc[idx, 'department'] = info.get('department_name_vn', 'Chưa xác định')
                                df.loc[idx, 'section'] = info.get('section_name_vn', 'Chưa xác định')
        except Exception as e:
            print(f'⚠️ Employee lookup failed: {e}')

    return df


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
