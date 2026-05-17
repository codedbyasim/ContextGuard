import re
import os

db_path = os.path.join("backend", "database.py")
if not os.path.exists(db_path):
    print("Not found")
    exit(1)

with open(db_path, "r", encoding="utf-8") as f:
    content = f.read()

content = content.replace("import sqlite3", "import psycopg2\nfrom psycopg2.pool import SimpleConnectionPool\nimport psycopg2.extras\nimport os\nfrom dotenv import load_dotenv\nload_dotenv()")
content = re.sub(r'DB_PATH = .*?def get_connection\(\):.*?return conn\n+', '''DB_URL = os.getenv("DATABASE_URL", "")

pool = None
def get_connection():
    global pool
    if pool is None:
        if not DB_URL:
            raise ValueError("DATABASE_URL is not set.")
        pool = SimpleConnectionPool(1, 10, DB_URL)
    return pool.getconn()

def release_connection(conn):
    if pool and conn:
        pool.putconn(conn)

''', content, flags=re.DOTALL)

content = content.replace("conn.row_factory = sqlite3.Row", "")
content = content.replace("conn.cursor()", "conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)")

# executescript -> execute
content = content.replace("cursor.executescript(", "cursor.execute(")

# AUTOINCREMENT -> SERIAL
content = content.replace("INTEGER PRIMARY KEY AUTOINCREMENT", "SERIAL PRIMARY KEY")
content = content.replace("INTEGER PRIMARY KEY", "SERIAL PRIMARY KEY")

# Parameters ? -> %s
def replace_params(m):
    return m.group(0).replace("?", "%s")
content = re.sub(r'"""[\s\S]*?"""', replace_params, content)
content = re.sub(r'"[^"]*"', replace_params, content)
content = re.sub(r"'[^']*'", replace_params, content)

# Error handling
content = content.replace("sqlite3.IntegrityError", "psycopg2.IntegrityError")
content = content.replace("sqlite3.Error", "psycopg2.Error")

# Handle returning ID: postgres needs RETURNING id, and fetchone
# e.g., cursor.lastrowid
content = re.sub(r'(cursor\.execute\(.*%s.*\))\n\s*app_id_pk = cursor\.lastrowid', r'\1 RETURNING id")\n        app_id_pk = cursor.fetchone()["id"]', content)
content = re.sub(r'return cursor\.lastrowid', r'return cursor.fetchone()["id"] if cursor.rowcount > 0 else None', content)
content = content.replace("conn.close()", "release_connection(conn)")

with open(os.path.join("backend", "database.py"), "w", encoding="utf-8") as f:
    f.write(content)

print("success!")
