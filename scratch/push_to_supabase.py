import sys
import os

# Add root directory to sys.path so it can find 'config' module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import toml
import pandas as pd
from sqlalchemy import create_engine
from config.groups import GROUP_REGISTRY

# Đọc file secrets.toml
secrets_path = os.path.join(os.path.dirname(__file__), '..', '.streamlit', 'secrets.toml')
try:
    with open(secrets_path, 'r', encoding='utf-8') as f:
        secrets = toml.load(f)
    db_url = secrets['connections']['supabase']['url']
except Exception as e:
    print(f"Lỗi: Không tìm thấy file secrets.toml hoặc chưa cấu hình URL Supabase.\nChi tiết: {e}")
    sys.exit(1)

# SQLAlchemy engine
# Sửa lại postgresql:// thành postgresql+psycopg2:// để SQLAlchemy hiểu
if db_url.startswith("postgresql://"):
    db_url = db_url.replace("postgresql://", "postgresql+psycopg2://", 1)

print("Đang kết nối tới Supabase...")
engine = create_engine(db_url)

print("\nBắt đầu tải và đẩy dữ liệu lên Supabase:")

# --- 1. Đẩy dữ liệu HRIS (Workforce & Mapping) ---
wf_sheet_id = "1wiv9c12jnSe7QFbqD-SHQo2tOWMD5My0pyE5JbmtYkU"
export_url = f"https://docs.google.com/spreadsheets/d/{wf_sheet_id}/export?format=xlsx"
print(f"\n[HRIS] Đang tải file Excel nặng từ Google Sheets...")
try:
    # Workforce Data
    df_wf = pd.read_excel(export_url, sheet_name="Workforce Data")
    df_wf.columns = [str(c).strip().replace('\n', ' ') for c in df_wf.columns]
    print(f"[HRIS] Đang đẩy {len(df_wf)} dòng lên bảng 'hris_workforce'...")
    df_wf.to_sql('hris_workforce', con=engine, if_exists='replace', index=False)
    
    # Mapping Data
    df_map = pd.read_excel(export_url, sheet_name="Mapping")
    df_map.columns = [str(c).strip().replace('\n', ' ') for c in df_map.columns]
    print(f"[HRIS] Đang đẩy {len(df_map)} dòng lên bảng 'hris_mapping'...")
    df_map.to_sql('hris_mapping', con=engine, if_exists='replace', index=False)
    print(f"[HRIS] ✅ Đã đẩy HRIS thành công!")
except Exception as e:
    print(f"[HRIS] ❌ Lỗi khi đẩy HRIS: {e}")

# --- 2. Đẩy dữ liệu Survey Groups ---
for group_id, cfg in GROUP_REGISTRY.items():
    url = cfg.get('url')
    if not url:
        continue
    
    table_name = f"survey_{group_id.lower()}"
    print(f"\n[{group_id}] Đang tải dữ liệu từ Google Sheets...")
    try:
        df = pd.read_csv(url)
        # Làm sạch tên cột để tương thích PostgreSQL (tránh lỗi ký tự lạ)
        df.columns = [str(c).strip().replace('\n', ' ') for c in df.columns]
        
        print(f"[{group_id}] Bắt đầu đẩy {len(df)} dòng lên bảng '{table_name}' trong Supabase...")
        # Đẩy vào Database
        df.to_sql(table_name, con=engine, if_exists='replace', index=False)
        print(f"[{group_id}] ✅ Đã đẩy thành công!")
    except Exception as e:
        print(f"[{group_id}] ❌ Lỗi: {e}")

print("\n🎉 Hoàn thành quá trình đồng bộ toàn bộ dữ liệu!")
