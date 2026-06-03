from sqlalchemy import create_engine, text

url = "postgresql://postgres:Titus%40lqp22101407@db.iwclnbnfxefwpduvwqiv.supabase.co:5432/postgres"
engine = create_engine(url)
with engine.connect() as conn:
    result = conn.execute(text("SELECT 1"))
    print("✅ Kết nối Supabase thành công!")
    tables = conn.execute(text("SELECT tablename FROM pg_tables WHERE schemaname='public'"))
    for t in tables:
        print(f"  📋 {t[0]}")
engine.dispose()
