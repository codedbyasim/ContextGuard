"""
ContextGuard — SQLite Database Layer
Owner: Maira
Tables:
  oauth_apps  → Scanned OAuth apps + risk scores
  dpi_events  → Lobster Trap flagged events
  audit_log   → Immutable append-only log
  ioc_list    → Known malicious OAuth app IDs
"""

import psycopg2
from psycopg2.pool import ThreadedConnectionPool
import psycopg2.extras
import os
from dotenv import load_dotenv
# Search for unified root .env first, then local .env
_env_file = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".env"))
if os.path.exists(_env_file):
    load_dotenv(_env_file)
else:
    load_dotenv(os.path.abspath(os.path.join(os.path.dirname(__file__), ".env")))
import os
import json
from datetime import datetime, timedelta, timezone
from typing import Optional

DB_URL = os.getenv("DATABASE_URL", "")

pool = None
def get_connection():
    global pool
    if pool is None:
        if not DB_URL:
            raise ValueError("DATABASE_URL is not set.")
        # Thread-safe pool with min 2 and max 20 connections
        pool = ThreadedConnectionPool(2, 20, DB_URL)
    
    # Attempt to retrieve a healthy connection (up to 3 retries)
    for i in range(3):
        conn = pool.getconn()
        try:
            # Execute a fast, lightweight ping query to verify SSL/TCP connection status
            with conn.cursor() as cursor:
                cursor.execute("SELECT 1")
            return conn
        except (psycopg2.OperationalError, psycopg2.InterfaceError) as e:
            print(f"⚠️ [DATABASE] Discarding stale/dead connection from pool (Attempt {i+1}/3): {e}")
            try:
                # Permanently close and discard the dead connection so the pool is cleaned
                pool.putconn(conn, close=True)
            except Exception:
                pass
                
    # Final fallback if all pool connections are dead: get a brand new one
    return pool.getconn()

def release_connection(conn):
    if pool and conn:
        try:
            pool.putconn(conn)
        except Exception:
            pass

def init_db():
    """Create all tables if they don't exist. Call on startup."""
    conn = get_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS oauth_apps (
            id              SERIAL PRIMARY KEY,
            app_id          TEXT UNIQUE NOT NULL,
            name            TEXT NOT NULL,
            publisher       TEXT,
            scopes          TEXT,
            user_count      INTEGER DEFAULT 0,
            risk_score      INTEGER DEFAULT 0,
            risk_category   TEXT DEFAULT 'UNKNOWN',
            explanation     TEXT,
            is_ioc          INTEGER DEFAULT 0,
            last_scanned    TEXT,
            contributing_factors TEXT,
            threat_intel    TEXT
        );

        CREATE TABLE IF NOT EXISTS risk_score_history (
            id              SERIAL PRIMARY KEY,
            app_id          TEXT NOT NULL,
            risk_score      INTEGER NOT NULL,
            risk_category   TEXT,
            contributing_factors TEXT,
            trigger_reason  TEXT,
            recorded_at     TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS dpi_events (
            id              SERIAL PRIMARY KEY,
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
            id              SERIAL PRIMARY KEY,
            timestamp       TEXT NOT NULL,
            actor           TEXT,
            action          TEXT NOT NULL,
            resource        TEXT,
            outcome         TEXT
        );

        CREATE TABLE IF NOT EXISTS ioc_list (
            id              SERIAL PRIMARY KEY,
            app_client_id   TEXT UNIQUE NOT NULL,
            source          TEXT,
            severity        TEXT DEFAULT 'CRITICAL',
            description     TEXT,
            date_added      TEXT
        );

        CREATE TABLE IF NOT EXISTS oauth_whitelist (
            id              SERIAL PRIMARY KEY,
            app_client_id   TEXT UNIQUE NOT NULL,
            reason          TEXT,
            added_by        TEXT DEFAULT 'admin',
            added_at        TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS env_variables (
            id              SERIAL PRIMARY KEY,
            var_name        TEXT UNIQUE NOT NULL,
            classification  TEXT DEFAULT 'NON-SENSITIVE',
            value_hash      TEXT,
            last_rotated    TEXT,
            last_accessed   TEXT,
            accessing_agents TEXT,
            updated_at      TEXT
        );

        CREATE TABLE IF NOT EXISTS env_alerts (
            id              SERIAL PRIMARY KEY,
            var_name        TEXT NOT NULL,
            severity        TEXT NOT NULL,
            message         TEXT,
            agent_id        TEXT,
            event_id        INTEGER,
            acknowledged    INTEGER DEFAULT 0,
            created_at      TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS incidents (
            id              SERIAL PRIMARY KEY,
            event_id        INTEGER,
            workflow_key    TEXT,
            title           TEXT,
            severity        TEXT,
            status          TEXT DEFAULT 'open',
            current_step    INTEGER DEFAULT 1,
            steps           TEXT,
            remediation     TEXT,
            event_summary   TEXT,
            created_at      TEXT NOT NULL,
            updated_at      TEXT
        );

        CREATE TABLE IF NOT EXISTS redteam_runs (
            id              SERIAL PRIMARY KEY,
            report          TEXT NOT NULL,
            detection_rate  REAL,
            started_at      TEXT,
            completed_at    TEXT
        );

        CREATE TABLE IF NOT EXISTS oauth_app_snapshots (
            id              SERIAL PRIMARY KEY,
            app_id          TEXT NOT NULL,
            scopes          TEXT NOT NULL,
            user_count      INTEGER,
            recorded_at     TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS agent_baselines (
            agent_id        TEXT PRIMARY KEY,
            intent_counts   TEXT,
            severity_counts TEXT,
            total_events    INTEGER DEFAULT 0,
            last_seen       TEXT
        );

        CREATE TABLE IF NOT EXISTS rotation_tickets (
            id              SERIAL PRIMARY KEY,
            incident_id     INTEGER,
            var_name        TEXT,
            service         TEXT,
            status          TEXT DEFAULT 'pending',
            playbook        TEXT,
            created_at      TEXT NOT NULL,
            completed_at    TEXT
        );

        CREATE TABLE IF NOT EXISTS users (
            id              SERIAL PRIMARY KEY,
            email           TEXT UNIQUE NOT NULL,
            password_hash   TEXT NOT NULL,
            name            TEXT NOT NULL,
            created_at      TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS system_config (
            key             TEXT PRIMARY KEY,
            value           TEXT NOT NULL
        );
    """)

    # Seed with a known supply-chain breach IOC
    cursor.execute("""
        INSERT INTO ioc_list (app_client_id, source, severity, description, date_added)
        VALUES (%s, %s, %s, %s, %s)
        ON CONFLICT (app_client_id) DO NOTHING
    """, (
        "110671459871-30f1spbu0hptbs60cb4vsmv79i7bbvqj.apps.googleusercontent.com",
        "Published security bulletin — AI supply-chain attack",
        "CRITICAL",
        "Known compromised OAuth app involved in an enterprise AI supply-chain attack via third-party tool.",
        datetime.now(timezone.utc).isoformat()
    ))

    _migrate_oauth_columns(cursor)
    _migrate_env_alerts_columns(cursor)
    conn.commit()
    release_connection(conn)
    print("[DATABASE] Initialized — all tables ready.")


def _migrate_oauth_columns(cursor):
    """Add M2 columns to existing databases."""
    cursor.execute("""
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name = 'oauth_apps'
    """)
    cols = {row['column_name'] for row in cursor.fetchall()}
    if "contributing_factors" not in cols:
        cursor.execute("ALTER TABLE oauth_apps ADD COLUMN contributing_factors TEXT")
    if "threat_intel" not in cols:
        cursor.execute("ALTER TABLE oauth_apps ADD COLUMN threat_intel TEXT")
    if "last_active" not in cols:
        cursor.execute("ALTER TABLE oauth_apps ADD COLUMN last_active TEXT")
    if "scope_drift" not in cols:
        cursor.execute("ALTER TABLE oauth_apps ADD COLUMN scope_drift TEXT")
    if "whitelisted" not in cols:
        cursor.execute("ALTER TABLE oauth_apps ADD COLUMN whitelisted INTEGER DEFAULT 0")


def _migrate_env_alerts_columns(cursor):
    """Add missing columns to env_alerts table in existing databases."""
    cursor.execute("""
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name = 'env_alerts'
    """)
    cols = {row['column_name'] for row in cursor.fetchall()}
    if "created_at" not in cols:
        cursor.execute("ALTER TABLE env_alerts ADD COLUMN created_at TEXT NOT NULL DEFAULT ''")


def set_system_config(key: str, value: str):
    """Set a system configuration key-value pair."""
    conn = get_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cursor.execute("""
        INSERT INTO system_config (key, value)
        VALUES (%s, %s)
        ON CONFLICT (key) DO UPDATE SET value = excluded.value
    """, (key, value))
    conn.commit()
    release_connection(conn)


def get_system_config(key: str, default: str = "") -> str:
    """Get a system configuration key-value pair."""
    conn = get_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cursor.execute("SELECT value FROM system_config WHERE key = %s", (key,))
    row = cursor.fetchone()
    release_connection(conn)
    return row["value"] if row else default


def delete_system_config(key: str):
    """Delete a system configuration key."""
    conn = get_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cursor.execute("DELETE FROM system_config WHERE key = %s", (key,))
    conn.commit()
    release_connection(conn)


# ═══════════════════════════════════════════
# OAUTH APPS
# ═══════════════════════════════════════════


def save_app(app: dict):
    """Insert or update an OAuth app record with risk score."""
    conn = get_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    scopes_str = json.dumps(app.get("scopes", [])) if isinstance(app.get("scopes"), list) else app.get("scopes", "")

    factors_str = json.dumps(app.get("contributing_factors", {})) if app.get("contributing_factors") else None
    intel_str = json.dumps(app.get("threat_intel", {})) if app.get("threat_intel") else None
    drift_str = json.dumps(app.get("scope_drift", {})) if app.get("scope_drift") else None

    cursor.execute("""
        INSERT INTO oauth_apps (app_id, name, publisher, scopes, user_count, risk_score, risk_category, explanation, is_ioc, last_scanned, contributing_factors, threat_intel, last_active, scope_drift, whitelisted)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT(app_id) DO UPDATE SET
            name = excluded.name,
            publisher = excluded.publisher,
            scopes = excluded.scopes,
            user_count = excluded.user_count,
            risk_score = excluded.risk_score,
            risk_category = excluded.risk_category,
            explanation = excluded.explanation,
            is_ioc = excluded.is_ioc,
            last_scanned = excluded.last_scanned,
            contributing_factors = excluded.contributing_factors,
            threat_intel = excluded.threat_intel,
            last_active = excluded.last_active,
            scope_drift = excluded.scope_drift,
            whitelisted = excluded.whitelisted
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
        datetime.now(timezone.utc).isoformat(),
        factors_str,
        intel_str,
        app.get("last_active"),
        drift_str,
        1 if app.get("whitelisted") else 0,
    ))

    conn.commit()
    release_connection(conn)


def clear_oauth_apps():
    """Clear all stored OAuth apps (used when connecting a new workspace)."""
    conn = get_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cursor.execute("DELETE FROM oauth_apps")
    cursor.execute("DELETE FROM risk_score_history")
    conn.commit()
    release_connection(conn)


def clear_all_workspace_data():
    """Wipe all sensitive data when the workspace is disconnected."""
    conn = get_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    
    tables_to_clear = [
        "oauth_apps",
        "risk_score_history",
        "dpi_events",
        "incidents",
        "env_variables",
        "env_alerts",
        "redteam_runs",
        "oauth_app_snapshots",
        "agent_baselines",
        "rotation_tickets"
    ]
    
    for table in tables_to_clear:
        cursor.execute(f"DELETE FROM {table}")
        
    conn.commit()
    release_connection(conn)



def get_apps() -> list:
    """Return all scanned OAuth apps with current risk scores."""
    conn = get_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cursor.execute("SELECT * FROM oauth_apps ORDER BY risk_score DESC")
    rows = cursor.fetchall()
    release_connection(conn)

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
        if app.get("contributing_factors"):
            try:
                app["contributing_factors"] = json.loads(app["contributing_factors"])
            except (json.JSONDecodeError, TypeError):
                pass
        if app.get("threat_intel"):
            try:
                app["threat_intel"] = json.loads(app["threat_intel"])
            except (json.JSONDecodeError, TypeError):
                pass
        if app.get("scope_drift"):
            try:
                app["scope_drift"] = json.loads(app["scope_drift"])
            except (json.JSONDecodeError, TypeError):
                pass
        app["whitelisted"] = bool(app.get("whitelisted", 0))
        apps.append(app)

    return apps


def get_app_by_id(app_id: str) -> dict | None:
    apps = get_apps()
    for app in apps:
        if app.get("app_id") == app_id:
            return app
    return None


def save_risk_score_history(
    app_id: str,
    risk_score: int,
    risk_category: str,
    contributing_factors: dict | None,
    trigger_reason: str,
):
    conn = get_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cursor.execute(
        """
        INSERT INTO risk_score_history (app_id, risk_score, risk_category, contributing_factors, trigger_reason, recorded_at)
        VALUES (%s, %s, %s, %s, %s, %s)
        """,
        (
            app_id,
            risk_score,
            risk_category,
            json.dumps(contributing_factors or {}),
            trigger_reason,
            datetime.now(timezone.utc).isoformat(),
        ),
    )
    conn.commit()
    release_connection(conn)


def get_risk_score_history(app_id: str, days: int = 90) -> list:
    conn = get_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cutoff = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
    cursor.execute(
        """
        SELECT * FROM risk_score_history
        WHERE app_id = %s AND recorded_at >= %s
        ORDER BY recorded_at ASC
        """,
        (app_id, cutoff),
    )
    rows = [dict(r) for r in cursor.fetchall()]
    release_connection(conn)
    for row in rows:
        if row.get("contributing_factors"):
            try:
                row["contributing_factors"] = json.loads(row["contributing_factors"])
            except (json.JSONDecodeError, TypeError):
                pass
    return rows


def recalculate_all_app_scores(score_fn, trigger_reason: str = "ioc_update") -> list:
    """FR-2.5: Recalculate risk scores for all stored apps."""
    updated = []
    for app in get_apps():
        is_ioc = check_ioc(app.get("app_id", ""))
        result = score_fn(
            name=app["name"],
            publisher=app.get("publisher", "Unknown"),
            scopes=app.get("scopes") or [],
            user_count=app.get("user_count", 0),
            is_ioc=is_ioc,
            prior_score=app.get("risk_score"),
        )
        if is_ioc:
            result["risk_score"] = max(int(result.get("risk_score", 0)), 95)
            result["risk_category"] = "CRITICAL"
        record = {
            **app,
            "risk_score": result.get("risk_score", 0),
            "risk_category": result.get("risk_category", "UNKNOWN"),
            "explanation": result.get("explanation", ""),
            "contributing_factors": result.get("contributing_factors", {}),
            "threat_intel": result.get("threat_intel", {}),
            "is_ioc": is_ioc,
        }
        save_app(record)
        save_risk_score_history(
            app["app_id"],
            record["risk_score"],
            record["risk_category"],
            record.get("contributing_factors"),
            trigger_reason,
        )
        updated.append(record)
    return updated


# ═══════════════════════════════════════════
# DPI EVENTS
# ═══════════════════════════════════════════


def save_event(event: dict):
    """Insert a DPI event from Lobster Trap webhook into the database."""
    conn = get_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    metadata_str = json.dumps(event.get("metadata", {})) if isinstance(event.get("metadata"), dict) else event.get("metadata", "{}")

    cursor.execute("""
        INSERT INTO dpi_events (timestamp, policy_triggered, action_taken, prompt_hash, intent_category, severity, alert_message, metadata)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING id
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

    event_id = cursor.fetchone()['id']
    conn.commit()
    release_connection(conn)

    return event_id


def get_events(hours: int = 24) -> list:
    """Fetch DPI events from the last N hours."""
    conn = get_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    cutoff = (datetime.now(timezone.utc) - timedelta(hours=hours)).isoformat()

    cursor.execute("""
        SELECT * FROM dpi_events
        WHERE timestamp >= %s
        ORDER BY timestamp DESC
    """, (cutoff,))

    rows = cursor.fetchall()
    release_connection(conn)

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
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    cutoff = (datetime.now(timezone.utc) - timedelta(hours=24)).isoformat()

    cursor.execute("""
        SELECT severity, COUNT(*) as count
        FROM dpi_events
        WHERE timestamp >= %s
        GROUP BY severity
    """, (cutoff,))

    rows = cursor.fetchall()
    release_connection(conn)

    return {row["severity"]: row["count"] for row in rows}


# ═══════════════════════════════════════════
# IOC LIST
# ═══════════════════════════════════════════


def save_ioc(ioc: dict):
    """Add a new IOC entry to the local list."""
    conn = get_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    cursor.execute("""
        INSERT INTO ioc_list (app_client_id, source, severity, description, date_added)
        VALUES (%s, %s, %s, %s, %s)
        ON CONFLICT (app_client_id) DO NOTHING
    """, (
        ioc["app_client_id"],
        ioc.get("source", "Manual Entry"),
        ioc.get("severity", "CRITICAL"),
        ioc.get("description", ""),
        datetime.now(timezone.utc).isoformat()
    ))

    conn.commit()
    release_connection(conn)


def get_iocs() -> list:
    """Return all IOC entries."""
    conn = get_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cursor.execute("SELECT * FROM ioc_list ORDER BY date_added DESC")
    rows = cursor.fetchall()
    release_connection(conn)
    return [dict(row) for row in rows]


def check_ioc(app_client_id: str) -> bool:
    """Check if an OAuth app ID is in the IOC list."""
    conn = get_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cursor.execute("SELECT COUNT(*) as cnt FROM ioc_list WHERE app_client_id = %s", (app_client_id,))
    row = cursor.fetchone()
    release_connection(conn)
    return row["cnt"] > 0


# ═══════════════════════════════════════════
# AUDIT LOG
# ═══════════════════════════════════════════


def save_audit_log(actor: str, action: str, resource: str = "", outcome: str = ""):
    """Append an entry to the immutable audit log."""
    conn = get_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    cursor.execute("""
        INSERT INTO audit_log (timestamp, actor, action, resource, outcome)
        VALUES (%s, %s, %s, %s, %s)
    """, (
        datetime.now(timezone.utc).isoformat(),
        actor,
        action,
        resource,
        outcome
    ))

    conn.commit()
    release_connection(conn)


def get_audit_log(limit: int = 100) -> list:
    """Return the most recent audit log entries."""
    conn = get_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cursor.execute("SELECT * FROM audit_log ORDER BY timestamp DESC LIMIT %s", (limit,))
    rows = cursor.fetchall()
    release_connection(conn)
    return [dict(row) for row in rows]


# ═══════════════════════════════════════════
# M1 WHITELIST (FR-1.7)
# ═══════════════════════════════════════════


def add_whitelist(app_client_id: str, reason: str = "", added_by: str = "admin"):
    conn = get_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cursor.execute(
        """
        INSERT INTO oauth_whitelist (app_client_id, reason, added_by, added_at)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (app_client_id) DO UPDATE SET
            reason = excluded.reason,
            added_by = excluded.added_by,
            added_at = excluded.added_at
        """,
        (app_client_id, reason, added_by, datetime.now(timezone.utc).isoformat()),
    )
    conn.commit()
    release_connection(conn)


def remove_whitelist(app_client_id: str):
    conn = get_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cursor.execute("DELETE FROM oauth_whitelist WHERE app_client_id = %s", (app_client_id,))
    conn.commit()
    release_connection(conn)


def is_whitelisted(app_client_id: str) -> bool:
    conn = get_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cursor.execute(
        "SELECT COUNT(*) as cnt FROM oauth_whitelist WHERE app_client_id = %s",
        (app_client_id,),
    )
    row = cursor.fetchone()
    release_connection(conn)
    return row["cnt"] > 0


def get_whitelist() -> list:
    conn = get_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cursor.execute("SELECT * FROM oauth_whitelist ORDER BY added_at DESC")
    rows = [dict(r) for r in cursor.fetchall()]
    release_connection(conn)
    return rows


# ═══════════════════════════════════════════
# M3 ENV GUARDIAN
# ═══════════════════════════════════════════


def save_env_variable(record: dict):
    conn = get_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    agents = record.get("accessing_agents", [])
    cursor.execute(
        """
        INSERT INTO env_variables (var_name, classification, value_hash, last_rotated, last_accessed, accessing_agents, updated_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT(var_name) DO UPDATE SET
            classification = excluded.classification,
            value_hash = excluded.value_hash,
            last_accessed = excluded.last_accessed,
            accessing_agents = excluded.accessing_agents,
            updated_at = excluded.updated_at
        """,
        (
            record["var_name"],
            record.get("classification", "NON-SENSITIVE"),
            record.get("value_hash"),
            record.get("last_rotated"),
            record.get("last_accessed"),
            json.dumps(agents) if isinstance(agents, list) else agents,
            datetime.now(timezone.utc).isoformat(),
        ),
    )
    conn.commit()
    release_connection(conn)


def get_env_variables() -> list:
    conn = get_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cursor.execute("SELECT * FROM env_variables ORDER BY var_name")
    rows = []
    for row in cursor.fetchall():
        r = dict(row)
        if r.get("accessing_agents"):
            try:
                r["accessing_agents"] = json.loads(r["accessing_agents"])
            except (json.JSONDecodeError, TypeError):
                pass
        rows.append(r)
    release_connection(conn)
    return rows


def save_env_alert(alert: dict) -> int:
    conn = get_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cursor.execute(
        """
        INSERT INTO env_alerts (var_name, severity, message, agent_id, event_id, created_at)
        VALUES (%s, %s, %s, %s, %s, %s)
        RETURNING id
        """,
        (
            alert["var_name"],
            alert.get("severity", "HIGH"),
            alert.get("message", ""),
            alert.get("agent_id", "lobster_trap"),
            alert.get("event_id"),
            datetime.now(timezone.utc).isoformat(),
        ),
    )
    alert_id = cursor.fetchone()["id"]
    conn.commit()
    release_connection(conn)
    return alert_id


def get_env_alerts(hours: int = 24, unacknowledged_only: bool = False) -> list:
    conn = get_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cutoff = (datetime.now(timezone.utc) - timedelta(hours=hours)).isoformat()
    sql = "SELECT * FROM env_alerts WHERE created_at >= %s"
    params: list = [cutoff]
    if unacknowledged_only:
        sql += " AND acknowledged = 0"
    sql += " ORDER BY created_at DESC"
    cursor.execute(sql, params)
    rows = [dict(r) for r in cursor.fetchall()]
    release_connection(conn)
    return rows


def mark_env_rotated(var_name: str):
    """FR-3.6: Record credential rotation timestamp."""
    conn = get_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    now = datetime.now(timezone.utc).isoformat()
    cursor.execute(
        """
        INSERT INTO env_variables (var_name, classification, last_rotated, updated_at)
        VALUES (%s, 'SENSITIVE', %s, %s)
        ON CONFLICT(var_name) DO UPDATE SET last_rotated = excluded.last_rotated, updated_at = excluded.updated_at
        """,
        (var_name, now, now),
    )
    conn.commit()
    release_connection(conn)


# ═══════════════════════════════════════════
# M7 INCIDENTS
# ═══════════════════════════════════════════


def get_event(event_id: int) -> dict | None:
    conn = get_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cursor.execute("SELECT * FROM dpi_events WHERE id = %s", (event_id,))
    row = cursor.fetchone()
    release_connection(conn)
    if not row:
        return None
    event = dict(row)
    if event.get("metadata"):
        try:
            event["metadata"] = json.loads(event["metadata"])
        except (json.JSONDecodeError, TypeError):
            pass
    return event


def save_incident(incident: dict) -> int:
    conn = get_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    now = datetime.now(timezone.utc).isoformat()
    cursor.execute(
        """
        INSERT INTO incidents (event_id, workflow_key, title, severity, status, current_step, steps, remediation, event_summary, created_at, updated_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING id
        """,
        (
            incident.get("event_id"),
            incident.get("workflow_key"),
            incident.get("title"),
            incident.get("severity"),
            incident.get("status", "open"),
            incident.get("current_step", 1),
            json.dumps(incident.get("steps", [])),
            json.dumps(incident.get("remediation_playbook")) if incident.get("remediation_playbook") else None,
            json.dumps(incident.get("event_summary", {})),
            now,
            now,
        ),
    )
    iid = cursor.fetchone()["id"]
    conn.commit()
    release_connection(conn)
    return iid


def get_incident(incident_id: int) -> dict | None:
    conn = get_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cursor.execute("SELECT * FROM incidents WHERE id = %s", (incident_id,))
    row = cursor.fetchone()
    release_connection(conn)
    if not row:
        return None
    inc = dict(row)
    for field in ("steps", "remediation", "event_summary"):
        if inc.get(field):
            try:
                inc[field] = json.loads(inc[field])
            except (json.JSONDecodeError, TypeError):
                pass
    return inc


def get_incidents(status: str | None = None) -> list:
    conn = get_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    if status:
        cursor.execute("SELECT * FROM incidents WHERE status = %s ORDER BY created_at DESC", (status,))
    else:
        cursor.execute("SELECT * FROM incidents ORDER BY created_at DESC")
    rows = []
    for row in cursor.fetchall():
        inc = dict(row)
        for field in ("steps", "remediation", "event_summary"):
            if inc.get(field):
                try:
                    inc[field] = json.loads(inc[field])
                except (json.JSONDecodeError, TypeError):
                    pass
        rows.append(inc)
    release_connection(conn)
    return rows


def update_incident(incident_id: int, updates: dict):
    conn = get_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    steps = json.dumps(updates.get("steps", []))
    cursor.execute(
        """
        UPDATE incidents SET status = %s, current_step = %s, steps = %s, updated_at = %s
        WHERE id = %s
        """,
        (
            updates.get("status"),
            updates.get("current_step"),
            steps,
            datetime.now(timezone.utc).isoformat(),
            incident_id,
        ),
    )
    conn.commit()
    release_connection(conn)


# ═══════════════════════════════════════════
# M6 RED-TEAM
# ═══════════════════════════════════════════


def save_redteam_run(report: dict) -> int:
    conn = get_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cursor.execute(
        """
        INSERT INTO redteam_runs (report, detection_rate, started_at, completed_at)
        VALUES (%s, %s, %s, %s)
        RETURNING id
        """,
        (
            json.dumps(report),
            report.get("detection_rate"),
            report.get("started_at"),
            report.get("completed_at"),
        ),
    )
    rid = cursor.fetchone()["id"]
    conn.commit()
    release_connection(conn)
    return rid


def get_redteam_runs(limit: int = 20) -> list:
    conn = get_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cursor.execute("SELECT * FROM redteam_runs ORDER BY id DESC LIMIT %s", (limit,))
    rows = []
    for row in cursor.fetchall():
        r = dict(row)
        try:
            r["report"] = json.loads(r["report"])
        except (json.JSONDecodeError, TypeError):
            pass
        rows.append(r)
    release_connection(conn)
    return rows


# ═══════════════════════════════════════════
# OAUTH SNAPSHOTS (FR-2.5 permission change)
# ═══════════════════════════════════════════


def get_latest_app_snapshot(app_id: str) -> dict | None:
    conn = get_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cursor.execute(
        """
        SELECT * FROM oauth_app_snapshots WHERE app_id = %s
        ORDER BY recorded_at DESC LIMIT 1
        """,
        (app_id,),
    )
    row = cursor.fetchone()
    release_connection(conn)
    if not row:
        return None
    snap = dict(row)
    try:
        snap["scopes"] = json.loads(snap["scopes"])
    except (json.JSONDecodeError, TypeError):
        pass
    return snap


def save_app_snapshot(app_id: str, scopes: list, user_count: int) -> bool:
    """Save snapshot; return True if permissions changed vs previous."""
    prev = get_latest_app_snapshot(app_id)
    scopes_sorted = sorted(str(s) for s in scopes)
    changed = False
    if prev:
        prev_scopes = sorted(str(s) for s in (prev.get("scopes") or []))
        changed = scopes_sorted != prev_scopes

    conn = get_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cursor.execute(
        """
        INSERT INTO oauth_app_snapshots (app_id, scopes, user_count, recorded_at)
        VALUES (%s, %s, %s, %s)
        """,
        (app_id, json.dumps(scopes), user_count, datetime.now(timezone.utc).isoformat()),
    )
    conn.commit()
    release_connection(conn)
    return changed


# ═══════════════════════════════════════════
# AGENT BASELINES (FR-2.2 behavioral)
# ═══════════════════════════════════════════


def get_agent_baseline(agent_id: str) -> dict | None:
    conn = get_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cursor.execute("SELECT * FROM agent_baselines WHERE agent_id = %s", (agent_id,))
    row = cursor.fetchone()
    release_connection(conn)
    if not row:
        return None
    b = dict(row)
    for field in ("intent_counts", "severity_counts"):
        if b.get(field):
            try:
                b[field] = json.loads(b[field])
            except (json.JSONDecodeError, TypeError):
                pass
    return b


def save_agent_baseline(baseline: dict):
    conn = get_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cursor.execute(
        """
        INSERT INTO agent_baselines (agent_id, intent_counts, severity_counts, total_events, last_seen)
        VALUES (%s, %s, %s, %s, %s)
        ON CONFLICT(agent_id) DO UPDATE SET
            intent_counts = excluded.intent_counts,
            severity_counts = excluded.severity_counts,
            total_events = excluded.total_events,
            last_seen = excluded.last_seen
        """,
        (
            baseline["agent_id"],
            json.dumps(baseline.get("intent_counts", {})),
            json.dumps(baseline.get("severity_counts", {})),
            baseline.get("total_events", 0),
            baseline.get("last_seen"),
        ),
    )
    conn.commit()
    release_connection(conn)


# ═══════════════════════════════════════════
# ROTATION TICKETS (M7)
# ═══════════════════════════════════════════


def save_rotation_ticket(incident_id: int, var_name: str, service: str, playbook: dict) -> int:
    conn = get_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cursor.execute(
        """
        INSERT INTO rotation_tickets (incident_id, var_name, service, status, playbook, created_at)
        VALUES (%s, %s, %s, 'in_progress', %s, %s)
        RETURNING id
        """,
        (
            incident_id,
            var_name,
            service,
            json.dumps(playbook),
            datetime.now(timezone.utc).isoformat(),
        ),
    )
    tid = cursor.fetchone()["id"]
    conn.commit()
    release_connection(conn)
    return tid


def complete_rotation_ticket(ticket_id: int):
    conn = get_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cursor.execute(
        """
        UPDATE rotation_tickets SET status = 'completed', completed_at = %s
        WHERE id = %s
        """,
        (datetime.now(timezone.utc).isoformat(), ticket_id),
    )
    conn.commit()
    release_connection(conn)


# ═══════════════════════════════════════════
# USERS (dashboard auth)
# ═══════════════════════════════════════════


def create_user(email: str, password_hash: str, name: str) -> dict:
    conn = get_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    now = datetime.now(timezone.utc).isoformat()
    try:
        cursor.execute(
            """
            INSERT INTO users (email, password_hash, name, created_at)
            VALUES (%s, %s, %s, %s)
            RETURNING id
            """,
            (email, password_hash, name.strip(), now),
        )
        user_id = cursor.fetchone()["id"]
        conn.commit()
    except psycopg2.IntegrityError:
        release_connection(conn)
        raise ValueError("email_taken")
    release_connection(conn)
    return {"id": user_id, "email": email, "name": name.strip(), "created_at": now}


def get_user_by_email(email: str) -> Optional[dict]:
    conn = get_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cursor.execute(
        "SELECT id, email, password_hash, name, created_at FROM users WHERE email = %s",
        (email,),
    )
    row = cursor.fetchone()
    release_connection(conn)
    if not row:
        return None
    return dict(row)


def get_user_by_id(user_id: int) -> Optional[dict]:
    conn = get_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cursor.execute(
        "SELECT id, email, name, created_at FROM users WHERE id = %s",
        (user_id,),
    )
    row = cursor.fetchone()
    release_connection(conn)
    if not row:
        return None
    return dict(row)
