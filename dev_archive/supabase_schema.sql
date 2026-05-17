-- Supabase Postgres Schema for ContextGuard
-- Run this in your Supabase SQL Editor to initialize your application backend

-- 1. OAuth Apps
CREATE TABLE IF NOT EXISTS oauth_apps (
    id SERIAL PRIMARY KEY,
    app_id TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    publisher TEXT,
    scopes TEXT,
    user_count INTEGER DEFAULT 0,
    risk_score INTEGER DEFAULT 0,
    risk_category TEXT DEFAULT 'UNKNOWN',
    explanation TEXT,
    is_ioc INTEGER DEFAULT 0,
    last_scanned TEXT,
    contributing_factors TEXT,
    threat_intel TEXT
);

-- 2. Risk Score History
CREATE TABLE IF NOT EXISTS risk_score_history (
    id SERIAL PRIMARY KEY,
    app_id TEXT NOT NULL,
    risk_score INTEGER NOT NULL,
    risk_category TEXT,
    contributing_factors TEXT,
    trigger_reason TEXT,
    recorded_at TEXT NOT NULL
);

-- 3. DPI Events
CREATE TABLE IF NOT EXISTS dpi_events (
    id SERIAL PRIMARY KEY,
    timestamp TEXT NOT NULL,
    policy_triggered TEXT NOT NULL,
    action_taken TEXT NOT NULL,
    prompt_hash TEXT,
    intent_category TEXT,
    severity TEXT,
    alert_message TEXT,
    metadata TEXT
);

-- 4. Audit Log
CREATE TABLE IF NOT EXISTS audit_log (
    id SERIAL PRIMARY KEY,
    timestamp TEXT NOT NULL,
    actor TEXT,
    action TEXT NOT NULL,
    resource TEXT,
    outcome TEXT
);

-- 5. IOC List
CREATE TABLE IF NOT EXISTS ioc_list (
    id SERIAL PRIMARY KEY,
    app_client_id TEXT UNIQUE NOT NULL,
    source TEXT,
    severity TEXT DEFAULT 'CRITICAL',
    description TEXT,
    date_added TEXT
);

-- 6. OAuth Whitelist
CREATE TABLE IF NOT EXISTS oauth_whitelist (
    id SERIAL PRIMARY KEY,
    app_client_id TEXT UNIQUE NOT NULL,
    reason TEXT,
    added_by TEXT DEFAULT 'admin',
    added_at TEXT NOT NULL
);

-- 7. Environment Variables
CREATE TABLE IF NOT EXISTS env_variables (
    id SERIAL PRIMARY KEY,
    var_name TEXT UNIQUE NOT NULL,
    classification TEXT DEFAULT 'NON-SENSITIVE',
    value_hash TEXT,
    last_rotated TEXT,
    last_accessed TEXT,
    accessing_agents TEXT,
    updated_at TEXT
);

-- 8. Env Alerts
CREATE TABLE IF NOT EXISTS env_alerts (
    id SERIAL PRIMARY KEY,
    var_name TEXT NOT NULL,
    alert_type TEXT NOT NULL,
    severity TEXT,
    message TEXT,
    timestamp TEXT NOT NULL,
    status TEXT DEFAULT 'OPEN'
);

-- 9. Incidents
CREATE TABLE IF NOT EXISTS incidents (
    id SERIAL PRIMARY KEY,
    incident_id TEXT UNIQUE NOT NULL,
    title TEXT NOT NULL,
    description TEXT,
    severity TEXT,
    status TEXT DEFAULT 'OPEN',
    source TEXT,
    assignee TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT
);

-- 10. Redteam Runs
CREATE TABLE IF NOT EXISTS redteam_runs (
    id SERIAL PRIMARY KEY,
    run_id TEXT UNIQUE NOT NULL,
    target TEXT NOT NULL,
    status TEXT DEFAULT 'RUNNING',
    score INTEGER,
    findings TEXT,
    started_at TEXT NOT NULL,
    completed_at TEXT
);

-- 11. OAuth App Snapshots
CREATE TABLE IF NOT EXISTS oauth_app_snapshots (
    id SERIAL PRIMARY KEY,
    app_id TEXT NOT NULL,
    snapshot_date TEXT NOT NULL,
    data TEXT NOT NULL
);

-- 12. Agent Baselines
CREATE TABLE IF NOT EXISTS agent_baselines (
    id SERIAL PRIMARY KEY,
    agent_id TEXT UNIQUE NOT NULL,
    agent_name TEXT,
    normal_activity_profile TEXT,
    status TEXT DEFAULT 'ACTIVE',
    last_updated TEXT
);

-- 13. Rotation Tickets
CREATE TABLE IF NOT EXISTS rotation_tickets (
    id SERIAL PRIMARY KEY,
    ticket_id TEXT UNIQUE NOT NULL,
    var_name TEXT NOT NULL,
    status TEXT DEFAULT 'PENDING',
    priority TEXT,
    requestor TEXT,
    created_at TEXT NOT NULL,
    resolved_at TEXT
);

-- Note: The users table is intentionally omitted.
-- User data is inherently managed by Supabase via the `auth.users` schema.
