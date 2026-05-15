"""
ContextGuard — FastAPI Backend
Owner: Maira
SRS Reference: System Architecture §6.2

Endpoints:
  GET  /api/apps            → All OAuth apps with risk scores
  POST /api/scan            → Trigger OAuth scan
  GET  /api/events          → DPI events (last 24h)
  POST /api/webhook/lobster → Receive Lobster Trap events
  GET  /api/report          → Generate Gemini compliance report
  POST /api/ioc             → Add new IOC entry
  GET  /api/stats           → Dashboard statistics
"""

import hashlib
import logging
import re
from datetime import datetime, timezone

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

from database import (
    init_db,
    save_app,
    get_apps,
    save_event,
    get_events,
    get_event_count_by_severity,
    save_ioc,
    get_iocs,
    check_ioc,
    save_audit_log,
    get_audit_log,
)
from gemini import score_oauth_app, classify_event, generate_report
from google_workspace import scan_oauth_apps

# ═══════════════════════════════════════════
# LOGGING
# ═══════════════════════════════════════════

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [CONTEXTGUARD] %(levelname)s %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S",
)
logger = logging.getLogger("contextguard")

# ═══════════════════════════════════════════
# APP SETUP
# ═══════════════════════════════════════════

app = FastAPI(
    title="ContextGuard API",
    version="1.0.0",
    description="Enterprise AI Security Platform — Third-Party AI Tool Risk Monitor",
)

# Allow React frontend to call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ═══════════════════════════════════════════
# STARTUP
# ═══════════════════════════════════════════


@app.on_event("startup")
def startup_event():
    """Initialize database on server startup."""
    init_db()
    logger.info("ContextGuard API started on :3000")
    save_audit_log("system", "startup", "api", "ContextGuard API initialized")


# ═══════════════════════════════════════════
# SCHEMAS
# ═══════════════════════════════════════════


class LobsterWebhookPayload(BaseModel):
    """Schema for incoming Lobster Trap webhook events."""
    timestamp: str = Field(..., description="ISO 8601 timestamp of the event")
    policy_triggered: str = Field(..., description="Name of the policy rule that triggered")
    action_taken: str = Field(..., description="Action taken: DENY, QUARANTINE, LOG, HUMAN_REVIEW")
    prompt_hash: str = Field(..., description="SHA-256 hash of the inspected prompt")
    metadata: dict = Field(default_factory=dict, description="DPI metadata and inspection results")


class IOCEntry(BaseModel):
    """Schema for adding a new IOC entry."""
    app_client_id: str = Field(..., description="OAuth App Client ID to flag")
    source: str = Field(default="Manual Entry", description="Source of the IOC intelligence")
    severity: str = Field(default="CRITICAL", description="Severity level: LOW, MEDIUM, HIGH, CRITICAL")
    description: str = Field(default="", description="Description of the threat")


# ═══════════════════════════════════════════
# PII REDACTION (for prompt content in metadata)
# ═══════════════════════════════════════════

PII_PATTERNS = [
    (re.compile(r"\b\d{3}-\d{2}-\d{4}\b"), "[SSN-REDACTED]"),
    (re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"), "[EMAIL-REDACTED]"),
    (re.compile(r"\b\d{3}[-.\s]\d{3}[-.\s]\d{4}\b"), "[PHONE-REDACTED]"),
    (re.compile(r"(?:sk|pk)[-_](?:live|test)[-_][a-zA-Z0-9]{20,}"), "[API-KEY-REDACTED]"),
    (re.compile(r"AKIA[0-9A-Z]{16}"), "[AWS-KEY-REDACTED]"),
    (re.compile(r"(?:password|passwd|pwd)\s*[=:]\s*\S+", re.IGNORECASE), "[PASSWORD-REDACTED]"),
]


def redact_text(text: str) -> str:
    """Redact PII and credentials from text."""
    if not text:
        return text
    for pattern, replacement in PII_PATTERNS:
        text = pattern.sub(replacement, text)
    return text


# ═══════════════════════════════════════════
# ENDPOINTS
# ═══════════════════════════════════════════


@app.get("/")
def root():
    return {
        "status": "ContextGuard API running",
        "version": "1.0.0",
        "endpoints": [
            "GET /api/apps",
            "POST /api/scan",
            "GET /api/events",
            "POST /api/webhook/lobster",
            "GET /api/report",
            "POST /api/ioc",
            "GET /api/stats",
        ],
    }


# ──────────────────────────────────────────
# F1: OAuth Risk Scanner
# ──────────────────────────────────────────


@app.get("/api/apps")
def list_apps():
    """Return all scanned OAuth apps with current risk scores."""
    apps = get_apps()
    save_audit_log("api", "list_apps", "oauth_apps", f"Returned {len(apps)} apps")
    return {"apps": apps, "count": len(apps)}


@app.post("/api/scan")
def trigger_scan():
    """
    Trigger an on-demand OAuth app scan.
    SRS FR-1.1: Connect to Google Workspace OAuth API and retrieve apps.
    SRS FR-1.3: Match against IOC list and flag CRITICAL.
    SRS FR-1.4: Send each app to Gemini Risk Engine for scoring.
    """
    logger.info("OAuth scan triggered")
    save_audit_log("api", "scan_triggered", "oauth_apps", "On-demand scan started")

    # Get apps from Google Workspace (or demo data if no credentials)
    raw_apps = scan_oauth_apps()
    if not raw_apps:
        raise HTTPException(status_code=500, detail="Failed to retrieve OAuth apps")

    scored_apps = []
    for app_data in raw_apps:
        # Check IOC list (SRS FR-1.3)
        is_ioc = check_ioc(app_data.get("app_id", ""))

        # Score with Gemini (SRS FR-1.4)
        try:
            score_result = score_oauth_app(
                name=app_data["name"],
                publisher=app_data.get("publisher", "Unknown"),
                scopes=app_data.get("scopes", []),
            )
        except Exception as e:
            logger.error("Gemini scoring failed for %s: %s", app_data["name"], e)
            score_result = {
                "risk_score": 95 if is_ioc else 0,
                "risk_category": "CRITICAL" if is_ioc else "UNKNOWN",
                "explanation": f"IOC match — known compromised app" if is_ioc else f"Scoring error: {e}",
            }

        # If IOC match, override to CRITICAL (SRS FR-1.3)
        if is_ioc:
            score_result["risk_score"] = max(score_result.get("risk_score", 0), 95)
            score_result["risk_category"] = "CRITICAL"
            score_result["explanation"] = (
                f"IOC MATCH: {score_result.get('explanation', '')} "
                "This app ID matches the Vercel breach indicator."
            )

        # Merge and save
        app_record = {
            **app_data,
            "risk_score": score_result.get("risk_score", 0),
            "risk_category": score_result.get("risk_category", "UNKNOWN"),
            "explanation": score_result.get("explanation", ""),
            "is_ioc": is_ioc,
        }
        save_app(app_record)
        scored_apps.append(app_record)

        logger.info(
            "Scored: %s → %d (%s)%s",
            app_data["name"],
            score_result.get("risk_score", 0),
            score_result.get("risk_category", "?"),
            " [IOC!]" if is_ioc else "",
        )

    save_audit_log(
        "api", "scan_completed", "oauth_apps",
        f"Scanned {len(scored_apps)} apps"
    )

    return {
        "status": "scan_complete",
        "apps_scanned": len(scored_apps),
        "apps": scored_apps,
    }


# ──────────────────────────────────────────
# F2: Lobster Trap DPI Events
# ──────────────────────────────────────────


@app.get("/api/events")
def list_events(hours: int = 24):
    """Return DPI events from the last N hours."""
    events = get_events(hours=hours)
    return {"events": events, "count": len(events)}


@app.post("/api/webhook/lobster")
def lobster_webhook(payload: LobsterWebhookPayload):
    """
    Receive flagged event from Lobster Trap.
    SRS F2: Lobster Trap sends here when a policy is triggered.

    Flow:
    1. Validate payload
    2. Classify with Gemini AI
    3. Redact sensitive data
    4. Store in database
    5. Log to audit trail
    6. Return safe response
    """
    logger.info(
        "Lobster Trap event: policy=%s action=%s",
        payload.policy_triggered,
        payload.action_taken,
    )

    # Step 1: Classify the event with Gemini (SRS F3)
    try:
        classification = classify_event({
            "policy_triggered": payload.policy_triggered,
            "action_taken": payload.action_taken,
            "metadata": payload.metadata,
        })
    except Exception as e:
        logger.error("Gemini classification failed: %s", e)
        # Use metadata severity as fallback
        severity_map = {
            "QUARANTINE": "CRITICAL",
            "DENY": "HIGH",
            "LOG": "MEDIUM",
            "HUMAN_REVIEW": "MEDIUM",
        }
        classification = {
            "intent_category": payload.metadata.get("intent_category", "UNKNOWN"),
            "severity": severity_map.get(payload.action_taken, "UNKNOWN"),
            "alert_message": f"Policy {payload.policy_triggered} triggered — action: {payload.action_taken}",
        }

    # Step 2: Build the event record
    event_record = {
        "timestamp": payload.timestamp,
        "policy_triggered": payload.policy_triggered,
        "action_taken": payload.action_taken,
        "prompt_hash": payload.prompt_hash,
        "intent_category": classification.get("intent_category", "UNKNOWN"),
        "severity": classification.get("severity", "UNKNOWN"),
        "alert_message": redact_text(classification.get("alert_message", "")),
        "metadata": payload.metadata,
    }

    # Step 3: Store in database
    event_id = save_event(event_record)

    # Step 4: Audit log
    save_audit_log(
        "lobster_trap",
        f"dpi_event_{payload.action_taken.lower()}",
        f"event_{event_id}",
        f"Policy: {payload.policy_triggered}, Severity: {classification.get('severity', 'UNKNOWN')}",
    )

    logger.info(
        "Event stored: id=%d severity=%s intent=%s",
        event_id,
        classification.get("severity", "?"),
        classification.get("intent_category", "?"),
    )

    return {
        "status": "received",
        "event_id": event_id,
        "classification": {
            "intent_category": classification.get("intent_category"),
            "severity": classification.get("severity"),
            "alert_message": classification.get("alert_message"),
        },
    }


# ──────────────────────────────────────────
# F3: Gemini Compliance Report
# ──────────────────────────────────────────


@app.get("/api/report")
def get_compliance_report():
    """
    Generate Gemini compliance report from last 24h events.
    SRS FR: Compliance report generation < 15 seconds.
    """
    logger.info("Generating compliance report")
    events = get_events(hours=24)

    # Prepare events for Gemini (strip raw metadata to save tokens)
    simplified_events = []
    for event in events:
        simplified_events.append({
            "timestamp": event.get("timestamp"),
            "policy": event.get("policy_triggered"),
            "action": event.get("action_taken"),
            "severity": event.get("severity"),
            "intent": event.get("intent_category"),
            "alert": event.get("alert_message"),
        })

    report_text = generate_report(simplified_events)

    save_audit_log("api", "report_generated", "compliance", f"Report covers {len(events)} events")

    return {
        "report": report_text,
        "event_count": len(events),
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }


# ──────────────────────────────────────────
# IOC Management
# ──────────────────────────────────────────


@app.post("/api/ioc")
def add_ioc(ioc: IOCEntry):
    """
    Add a new IOC entry to the local list.
    SRS FR-1.6: Allow administrator to manually add new IOC entries.
    """
    save_ioc(ioc.model_dump())
    save_audit_log("admin", "ioc_added", ioc.app_client_id, f"Severity: {ioc.severity}")
    logger.info("IOC added: %s (%s)", ioc.app_client_id, ioc.severity)
    return {"status": "ioc_added", "ioc": ioc.model_dump()}


@app.get("/api/iocs")
def list_iocs():
    """Return all IOC entries."""
    iocs = get_iocs()
    return {"iocs": iocs, "count": len(iocs)}


# ──────────────────────────────────────────
# Dashboard Statistics
# ──────────────────────────────────────────


@app.get("/api/stats")
def get_stats():
    """
    Dashboard statistics for the frontend.
    Returns aggregated counts for display.
    """
    apps = get_apps()
    events = get_events(hours=24)
    severity_counts = get_event_count_by_severity()

    critical_apps = [a for a in apps if a.get("risk_category") == "CRITICAL"]
    high_apps = [a for a in apps if a.get("risk_category") == "HIGH"]

    return {
        "total_apps": len(apps),
        "critical_apps": len(critical_apps),
        "high_risk_apps": len(high_apps),
        "total_events_24h": len(events),
        "events_by_severity": severity_counts,
        "ioc_matches": len([a for a in apps if a.get("is_ioc")]),
    }


# ──────────────────────────────────────────
# Audit Log
# ──────────────────────────────────────────


@app.get("/api/audit")
def list_audit_log(limit: int = 100):
    """Return the most recent audit log entries."""
    logs = get_audit_log(limit=limit)
    return {"audit_log": logs, "count": len(logs)}
