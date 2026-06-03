"""
Upload HRIS_data.xlsx lên NeonDB (bảng hris_data).
Chạy 1 lần duy nhất: python scripts/upload_hris_to_neondb.py
"""
import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pandas as pd
from sqlalchemy import create_engine, text

# -- Config --
DB_URL = "postgresql://neondb_owner:npg_4jFwKhNSEU6C@ep-round-cloud-aovgstxi.c-2.ap-southeast-1.aws.neon.tech/neondb?sslmode=require"
HRIS_FILE = os.path.join(os.path.dirname(__file__), '..', 'data', 'HRIS_data.xlsx')
TABLE_NAME = "hris_data"
CHUNK_SIZE = 5000  # upload theo từng batch để tránh timeout

def main():
    print(f"📂 Đang đọc file: {HRIS_FILE}")
    if not os.path.exists(HRIS_FILE):
        print("❌ Không tìm thấy file HRIS_data.xlsx!")
        return

    df = pd.read_excel(HRIS_FILE)
    df.columns = df.columns.str.strip()
    print(f"✅ Đọc xong: {len(df):,} dòng × {len(df.columns)} cột")
    print(f"   Columns: {list(df.columns[:10])}...")

    print(f"\n🔌 Đang kết nối NeonDB...")
    engine = create_engine(DB_URL)

    # Drop bảng cũ nếu có
    with engine.begin() as conn:
        conn.execute(text(f"DROP TABLE IF EXISTS {TABLE_NAME} CASCADE"))
    print(f"   Đã xóa bảng cũ (nếu có)")

    # Upload theo chunk
    total_chunks = (len(df) // CHUNK_SIZE) + 1
    print(f"\n📤 Đang upload {len(df):,} dòng ({total_chunks} batches)...")

    for i in range(0, len(df), CHUNK_SIZE):
        chunk = df.iloc[i:i+CHUNK_SIZE]
        if_exists = 'append' if i > 0 else 'replace'
        chunk.to_sql(TABLE_NAME, engine, if_exists=if_exists, index=False)
        batch_num = (i // CHUNK_SIZE) + 1
        print(f"   Batch {batch_num}/{total_chunks}: {len(chunk)} dòng ✓")

    # Verify
    with engine.connect() as conn:
        result = conn.execute(text(f"SELECT COUNT(*) FROM {TABLE_NAME}"))
        count = result.scalar()
    print(f"\n✅ Upload hoàn tất! Tổng {count:,} dòng trên NeonDB.")

    engine.dispose()

if __name__ == '__main__':
    main()
