import os
import psycopg2
from dotenv import load_dotenv

load_dotenv(os.path.join("backend", ".env"))
db_url = os.getenv("DATABASE_URL")

conn = psycopg2.connect(db_url)
conn.autocommit = True
cursor = conn.cursor()

try:
    cursor.execute("DROP TABLE IF EXISTS oauth_app_snapshots;")
    print("Successfully dropped oauth_app_snapshots. It will be recreated cleanly on restart.")
except Exception as e:
    print("Error dropping oauth_app_snapshots:", e)

try:
    cursor.execute("ALTER TABLE risk_score_history ADD COLUMN IF NOT EXISTS recorded_at TEXT;")
    print("Successfully added recorded_at to risk_score_history.")
except Exception as e:
    print("Error on risk_score_history:", e)

cursor.close()
conn.close()
