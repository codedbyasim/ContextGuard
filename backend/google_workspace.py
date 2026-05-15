"""
ContextGuard — Google Workspace OAuth Scanner
Owner: Maira
Scans Google Workspace for connected third-party OAuth applications.
"""

# TODO: implement scan_oauth_apps()
# For hackathon demo: load from demo/synthetic_apps.json if no real credentials

import json
import os

DEMO_DATA_PATH = os.path.join(
    os.path.dirname(__file__), "..", "demo", "synthetic_apps.json"
)


def scan_oauth_apps() -> list:
    """
    Return list of connected OAuth apps.
    Uses real Google Workspace API if credentials available,
    otherwise falls back to synthetic demo data.
    """
    creds_path = os.getenv("GOOGLE_WORKSPACE_CREDS")

    if creds_path and os.path.exists(creds_path):
        # TODO: implement real Google Workspace Admin SDK call
        pass
    else:
        print("No Workspace credentials found — using demo data.")
        return _load_demo_data()


def _load_demo_data() -> list:
    with open(DEMO_DATA_PATH, "r") as f:
        return json.load(f)
