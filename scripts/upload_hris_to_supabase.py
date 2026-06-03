"""
Upload HRIS_data.xlsx lên Supabase (bảng hris_data).
"""
import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pandas as pd
from sqlalchemy import create_engine, text

DB_URL = "postgresql://postgres:Titus%40lqp22101407@db.iwclnbnfxefwpduvwqiv.supabase.co:5432/postgres"
HRIS_FILE = os.path.join(os.path.dirname(__file__), '..', 'data', 'HRIS_data.xlsx')
TABLE_NAME = "hris_data"
CHUNK_SIZE = 5000

def main():
    print(f"📂 Đang đọc file: {HRIS_FILE}")
    df = pd.read_excel(HRIS_FILE)
    df.columns = df.columns.str.strip()
    print(f"✅ Đọc xong: {len(df):,} dòng × {len(df.columns)} cột")

    print(f"\n🔌 Đang kết nối Supabase...")
    engine = create_engine(DB_URL)

    with engine.begin() as conn:
        conn.execute(text(f"DROP TABLE IF EXISTS {TABLE_NAME} CASCADE"))
    print(f"   Đã xóa bảng cũ (nếu có)")

    total_chunks = (len(df) // CHUNK_SIZE) + 1
    print(f"\n📤 Đang upload {len(df):,} dòng ({total_chunks} batches)...")

    for i in range(0, len(df), CHUNK_SIZE):
        chunk = df.iloc[i:i+CHUNK_SIZE]
        if_exists = 'append' if i > 0 else 'replace'
        chunk.to_sql(TABLE_NAME, engine, if_exists=if_exists, index=False)
        batch_num = (i // CHUNK_SIZE) + 1
        print(f"   Batch {batch_num}/{total_chunks}: {len(chunk)} dòng ✓")

    with engine.connect() as conn:
        result = conn.execute(text(f"SELECT COUNT(*) FROM {TABLE_NAME}"))
        count = result.scalar()
    print(f"\n✅ Upload hoàn tất! Tổng {count:,} dòng trên Supabase.")
    engine.dispose()

if __name__ == '__main__':
    main()
