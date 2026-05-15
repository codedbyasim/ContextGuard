"""
ContextGuard — FastAPI Backend
Owner: Maira
Endpoints:
  GET  /api/apps            → All OAuth apps with risk scores
  POST /api/scan            → Trigger OAuth scan
  GET  /api/events          → DPI events (last 24h)
  POST /api/webhook/lobster → Receive Lobster Trap events
  GET  /api/report          → Generate Gemini compliance report
  POST /api/ioc             → Add new IOC entry
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
import os

load_dotenv()

app = FastAPI(title="ContextGuard API", version="1.0.0")

# Allow React frontend to call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── TODO: import database and gemini modules ──
# from database import get_apps, get_events, save_event
# from gemini import score_oauth_app, classify_event, generate_report


@app.get("/")
def root():
    return {"status": "ContextGuard API running", "version": "1.0.0"}


@app.get("/api/apps")
def get_apps():
    """Return all scanned OAuth apps with current risk scores."""
    # TODO: return database.get_apps()
    return {"apps": [], "message": "TODO: connect database"}


@app.post("/api/scan")
def trigger_scan():
    """Trigger an on-demand OAuth app scan."""
    # TODO: call google_workspace.scan_oauth_apps()
    # TODO: for each app, call gemini.score_oauth_app()
    # TODO: save results to database
    return {"status": "scan triggered", "message": "TODO: implement scan"}


@app.get("/api/events")
def get_events():
    """Return DPI events from the last 24 hours."""
    # TODO: return database.get_events(hours=24)
    return {"events": [], "message": "TODO: connect database"}


@app.post("/api/webhook/lobster")
def lobster_webhook(payload: dict):
    """
    Receive flagged event from Lobster Trap.
    Lobster Trap sends here when a policy is triggered.
    """
    # TODO: call gemini.classify_event(payload)
    # TODO: save to database
    # TODO: add to alert queue
    print(f"Lobster Trap event received: {payload}")
    return {"status": "received"}


@app.get("/api/report")
def get_report():
    """Generate Gemini compliance report from last 24h events."""
    # TODO: fetch last 24h events from database
    # TODO: call gemini.generate_report(events)
    return {"report": "TODO: implement report generation"}


@app.post("/api/ioc")
def add_ioc(ioc: dict):
    """Add a new IOC entry to the local list."""
    # TODO: validate and save to database
    return {"status": "ioc added", "ioc": ioc}
