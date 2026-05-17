import psycopg2
import urllib.parse
pw = urllib.parse.quote('ftcalex4rAOYifLW')

# Test Transaction Mode Pooler (Port 6543)
url_6543 = f'postgresql://postgres.wfkilhwghdkddxgcljyq:{pw}@aws-1-ap-northeast-1.pooler.supabase.com:6543/postgres?sslmode=require'
try:
    conn = psycopg2.connect(url_6543)
    print("Success on port 6543 (Transaction Mode)")
except Exception as e:
    print("Port 6543 failed:", e)

# Test Session Mode Pooler (Port 5432)
url_5432 = f'postgresql://postgres.wfkilhwghdkddxgcljyq:{pw}@aws-1-ap-northeast-1.pooler.supabase.com:5432/postgres?sslmode=require'
try:
    conn2 = psycopg2.connect(url_5432)
    print("Success on port 5432 (Session Mode)")
except Exception as e:
    print("Port 5432 failed:", e)



