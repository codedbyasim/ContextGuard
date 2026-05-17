import re

with open('backend/database.py', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace('import sqlite3', 'import psycopg2\nimport psycopg2.extras\nfrom psycopg2.pool import SimpleConnectionPool\nimport os\nfrom dotenv import load_dotenv\nload_dotenv()')

content = re.sub(
    r'DB_PATH.*?def get_connection\(\):.*?conn\.row_factory = sqlite3\.Row\n\s*return conn',
    '''
DB_URL = os.getenv("DATABASE_URL", "postgresql://user:pass@localhost:5432/contextguard")
pool = None

def get_connection():
    global pool
    if pool is None:
        pool = SimpleConnectionPool(1, 10, DB_URL)
    conn = pool.getconn()
    return conn

def release_connection(conn):
    if pool and conn:
        pool.putconn(conn)
''',
    content, flags=re.DOTALL
)

content = content.replace('cursor.executescript(', 'cursor.execute(')
content = content.replace('INTEGER PRIMARY KEY AUTOINCREMENT', 'SERIAL PRIMARY KEY')

def replace_in_string(m):
    return m.group(0).replace('?', '%s')
content = re.sub(r'"""[\s\S]*?"""', replace_in_string, content)
content = re.sub(r'"[^"]*"', replace_in_string, content)
content = re.sub(r"'[^']*'", replace_in_string, content)

content = content.replace('conn.cursor()', 'conn.cursor(cursor_factory=psycopg2.extras.DictCursor)')
content = content.replace('conn.close()', 'release_connection(conn)')

# In postgres, returning row id is different.
# sqlite: cursor.lastrowid
# postgres: RETURNING id
# Need to manually handle this if present. 

with open('backend/database_pg.py', 'w', encoding='utf-8') as f:
    f.write(content)
