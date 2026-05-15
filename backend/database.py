"""
ContextGuard — SQLite Database Layer
Owner: Maira
Tables:
  oauth_apps  → Scanned OAuth apps + risk scores
  dpi_events  → Lobster Trap flagged events
  audit_log   → Immutable append-only log
  ioc_list    → Known malicious OAuth app IDs
"""

import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "data", "contextguard.db")


def get_connection():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Create all tables if they don't exist. Call on startup."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.executescript("""
        CREATE TABLE IF NOT EXISTS oauth_apps (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            app_id          TEXT UNIQUE NOT NULL,
            name            TEXT NOT NULL,
            publisher       TEXT,
            scopes          TEXT,
            user_count      INTEGER DEFAULT 0,
            risk_score      INTEGER DEFAULT 0,
            risk_category   TEXT DEFAULT 'UNKNOWN',
            explanation     TEXT,
            is_ioc          INTEGER DEFAULT 0,
            last_scanned    TEXT
        );

        CREATE TABLE IF NOT EXISTS dpi_events (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp       TEXT NOT NULL,
            policy_triggered TEXT NOT NULL,
            action_taken    TEXT NOT NULL,
            prompt_hash     TEXT,
            intent_category TEXT,
            severity        TEXT,
            alert_message   TEXT
        );

        CREATE TABLE IF NOT EXISTS audit_log (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp       TEXT NOT NULL,
            actor           TEXT,
            action          TEXT NOT NULL,
            resource        TEXT,
            outcome         TEXT
        );

        CREATE TABLE IF NOT EXISTS ioc_list (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            app_client_id   TEXT UNIQUE NOT NULL,
            source          TEXT,
            severity        TEXT DEFAULT 'CRITICAL',
            description     TEXT,
            date_added      TEXT
        );
    """)

    # Seed with the Vercel breach IOC
    cursor.execute("""
        INSERT OR IGNORE INTO ioc_list (app_client_id, source, severity, description, date_added)
        VALUES (?, ?, ?, ?, ?)
    """, (
        "110671459871-30f1spbu0hptbs60cb4vsmv79i7bbvqj.apps.googleusercontent.com",
        "Vercel Security Bulletin April 2026",
        "CRITICAL",
        "OAuth app involved in the April 2026 Vercel supply-chain breach via Context.ai compromise.",
        datetime.utcnow().isoformat()
    ))

    conn.commit()
    conn.close()
    print("Database initialized.")


# ── TODO: Add get_apps(), save_app(), get_events(), save_event() functions ──
