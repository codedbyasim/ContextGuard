"""Delete all dashboard users so you can re-register. Run from backend folder:
    python scripts/reset_users.py
"""
import os
import sqlite3

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "contextguard.db")


def main():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT id, email FROM users")
    rows = cur.fetchall()
    if not rows:
        print("No users in database.")
        return
    print("Removing users:")
    for row in rows:
        print(f"  - {row[1]} (id={row[0]})")
    cur.execute("DELETE FROM users")
    conn.commit()
    conn.close()
    print("Done. You can sign up again with any email.")


if __name__ == "__main__":
    main()
