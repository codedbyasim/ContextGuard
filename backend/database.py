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
import json
from datetime import datetime, timedelta, timezone

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
            alert_message   TEXT,
            metadata        TEXT
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
        datetime.now(timezone.utc).isoformat()
    ))

    conn.commit()
    conn.close()
    print("[DATABASE] Initialized — all tables ready.")


# ═══════════════════════════════════════════
# OAUTH APPS
# ═══════════════════════════════════════════


def save_app(app: dict):
    """Insert or update an OAuth app record with risk score."""
    conn = get_connection()
    cursor = conn.cursor()

    scopes_str = json.dumps(app.get("scopes", [])) if isinstance(app.get("scopes"), list) else app.get("scopes", "")

    cursor.execute("""
        INSERT INTO oauth_apps (app_id, name, publisher, scopes, user_count, risk_score, risk_category, explanation, is_ioc, last_scanned)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(app_id) DO UPDATE SET
            name = excluded.name,
            publisher = excluded.publisher,
            scopes = excluded.scopes,
            user_count = excluded.user_count,
            risk_score = excluded.risk_score,
            risk_category = excluded.risk_category,
            explanation = excluded.explanation,
            is_ioc = excluded.is_ioc,
            last_scanned = excluded.last_scanned
    """, (
        app["app_id"],
        app["name"],
        app.get("publisher", "Unknown"),
        scopes_str,
        app.get("user_count", 0),
        app.get("risk_score", 0),
        app.get("risk_category", "UNKNOWN"),
        app.get("explanation", ""),
        1 if app.get("is_ioc", False) else 0,
        datetime.now(timezone.utc).isoformat()
    ))

    conn.commit()
    conn.close()


def get_apps() -> list:
    """Return all scanned OAuth apps with current risk scores."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM oauth_apps ORDER BY risk_score DESC")
    rows = cursor.fetchall()
    conn.close()

    apps = []
    for row in rows:
        app = dict(row)
        # Parse scopes back to list if stored as JSON string
        if app.get("scopes"):
            try:
                app["scopes"] = json.loads(app["scopes"])
            except (json.JSONDecodeError, TypeError):
                app["scopes"] = app["scopes"].split(",") if app["scopes"] else []
        app["is_ioc"] = bool(app.get("is_ioc", 0))
        apps.append(app)

    return apps


# ═══════════════════════════════════════════
# DPI EVENTS
# ═══════════════════════════════════════════


def save_event(event: dict):
    """Insert a DPI event from Lobster Trap webhook into the database."""
    conn = get_connection()
    cursor = conn.cursor()

    metadata_str = json.dumps(event.get("metadata", {})) if isinstance(event.get("metadata"), dict) else event.get("metadata", "{}")

    cursor.execute("""
        INSERT INTO dpi_events (timestamp, policy_triggered, action_taken, prompt_hash, intent_category, severity, alert_message, metadata)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        event.get("timestamp", datetime.now(timezone.utc).isoformat()),
        event.get("policy_triggered", "unknown"),
        event.get("action_taken", "UNKNOWN"),
        event.get("prompt_hash", ""),
        event.get("intent_category", ""),
        event.get("severity", "UNKNOWN"),
        event.get("alert_message", ""),
        metadata_str
    ))

    event_id = cursor.lastrowid
    conn.commit()
    conn.close()

    return event_id


def get_events(hours: int = 24) -> list:
    """Fetch DPI events from the last N hours."""
    conn = get_connection()
    cursor = conn.cursor()

    cutoff = (datetime.now(timezone.utc) - timedelta(hours=hours)).isoformat()

    cursor.execute("""
        SELECT * FROM dpi_events
        WHERE timestamp >= ?
        ORDER BY timestamp DESC
    """, (cutoff,))

    rows = cursor.fetchall()
    conn.close()

    events = []
    for row in rows:
        event = dict(row)
        # Parse metadata back to dict if stored as JSON string
        if event.get("metadata"):
            try:
                event["metadata"] = json.loads(event["metadata"])
            except (json.JSONDecodeError, TypeError):
                pass
        events.append(event)

    return events


def get_event_count_by_severity() -> dict:
    """Get count of events grouped by severity for the last 24 hours."""
    conn = get_connection()
    cursor = conn.cursor()

    cutoff = (datetime.now(timezone.utc) - timedelta(hours=24)).isoformat()

    cursor.execute("""
        SELECT severity, COUNT(*) as count
        FROM dpi_events
        WHERE timestamp >= ?
        GROUP BY severity
    """, (cutoff,))

    rows = cursor.fetchall()
    conn.close()

    return {row["severity"]: row["count"] for row in rows}


# ═══════════════════════════════════════════
# IOC LIST
# ═══════════════════════════════════════════


def save_ioc(ioc: dict):
    """Add a new IOC entry to the local list."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT OR IGNORE INTO ioc_list (app_client_id, source, severity, description, date_added)
        VALUES (?, ?, ?, ?, ?)
    """, (
        ioc["app_client_id"],
        ioc.get("source", "Manual Entry"),
        ioc.get("severity", "CRITICAL"),
        ioc.get("description", ""),
        datetime.now(timezone.utc).isoformat()
    ))

    conn.commit()
    conn.close()


def get_iocs() -> list:
    """Return all IOC entries."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM ioc_list ORDER BY date_added DESC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def check_ioc(app_client_id: str) -> bool:
    """Check if an OAuth app ID is in the IOC list."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) as cnt FROM ioc_list WHERE app_client_id = ?", (app_client_id,))
    row = cursor.fetchone()
    conn.close()
    return row["cnt"] > 0


# ═══════════════════════════════════════════
# AUDIT LOG
# ═══════════════════════════════════════════


def save_audit_log(actor: str, action: str, resource: str = "", outcome: str = ""):
    """Append an entry to the immutable audit log."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO audit_log (timestamp, actor, action, resource, outcome)
        VALUES (?, ?, ?, ?, ?)
    """, (
        datetime.now(timezone.utc).isoformat(),
        actor,
        action,
        resource,
        outcome
    ))

    conn.commit()
    conn.close()


def get_audit_log(limit: int = 100) -> list:
    """Return the most recent audit log entries."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM audit_log ORDER BY timestamp DESC LIMIT ?", (limit,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]
