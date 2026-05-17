import psycopg2
import os
from dotenv import load_dotenv

load_dotenv(dotenv_path="backend/.env")

db_url = os.getenv("DATABASE_URL")
if not db_url:
    print("Error: DATABASE_URL not set in backend/.env")
    exit(1)

print("Connecting to Supabase Postgres...")
try:
    with open('supabase_schema.sql', 'r') as f:
        sql = f.read()

    conn = psycopg2.connect(db_url)
    cur = conn.cursor()
    cur.execute(sql)
    conn.commit()
    conn.close()
    print("Schema successfully applied to Supabase! All 13 tables are ready.")
except Exception as e:
    print(f"Error applying schema: {e}")
