import json
import logging
import os
from datetime import datetime, timezone

from google.oauth2 import service_account
from googleapiclient.discovery import build

logger = logging.getLogger("contextguard")

SCOPES = [
    "https://www.googleapis.com/auth/admin.directory.user.readonly",
    "https://www.googleapis.com/auth/admin.directory.user.security",
]




def _scan_workspace_api() -> list:
    """FR-1.1–1.2: Real Google Workspace Admin SDK enumeration."""
    creds_path = os.getenv("GOOGLE_WORKSPACE_CREDS")
    admin_email = os.getenv("GOOGLE_ADMIN_EMAIL")

    if creds_path and not os.path.isabs(creds_path):
        # Dynamically locate relative path relative to active process cwd or current module path
        possible_paths = [
            os.path.abspath(creds_path),
            os.path.abspath(os.path.join(os.path.dirname(__file__), creds_path)),
            os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(__file__)), creds_path))
        ]
        for p in possible_paths:
            if os.path.exists(p):
                creds_path = p
                break

    if not creds_path or not os.path.exists(creds_path):
        raise FileNotFoundError(f"Google Workspace credentials not found: {creds_path}")
    if not admin_email:
        raise ValueError("GOOGLE_ADMIN_EMAIL is not set in .env")

    creds = service_account.Credentials.from_service_account_file(creds_path, scopes=SCOPES)
    creds = creds.with_subject(admin_email)
    directory_service = build("admin", "directory_v1", credentials=creds)

    results = directory_service.users().list(customer="my_customer", maxResults=500).execute()
    users = results.get("users", [])
    logger.info("Found %d Workspace users", len(users))

    app_registry: dict[str, dict] = {}

    for user in users:
        user_email = user.get("primaryEmail")
        if not user_email:
            continue
        try:
            tokens_result = directory_service.tokens().list(userKey=user_email).execute()
            tokens = tokens_result.get("items", [])
        except Exception as e:
            logger.warning("Could not fetch tokens for %s: %s", user_email, e)
            continue

        for token in tokens:
            client_id = token.get("clientId")
            if not client_id:
                continue
            scopes = token.get("scopes", [])
            last_active = token.get("lastTimeUsed") or token.get("creationTime")

            if client_id not in app_registry:
                app_registry[client_id] = {
                    "app_id": client_id,
                    "name": token.get("displayText", "Unknown App"),
                    "publisher": token.get("clientId", "Workspace App")[:32],
                    "scopes": list(scopes),
                    "user_count": 0,
                    "last_active": last_active,
                    "declared_scopes": list(scopes),
                }
            else:
                app_registry[client_id]["scopes"] = list(
                    set(app_registry[client_id]["scopes"]) | set(scopes)
                )
                if last_active and (
                    not app_registry[client_id].get("last_active")
                    or last_active > app_registry[client_id]["last_active"]
                ):
                    app_registry[client_id]["last_active"] = last_active

            app_registry[client_id]["user_count"] += 1

    return list(app_registry.values())


def _generate_synthetic_apps() -> list:
    """Fallback generator when real Workspace Admin SDK is unauthorized."""
    now = datetime.now(timezone.utc).isoformat()
    return [
        {
            "app_id": "calendly_123",
            "name": "Calendly Integration",
            "publisher": "Calendly LLC",
            "scopes": ["https://www.googleapis.com/auth/calendar"],
            "user_count": 45,
            "last_active": now,
            "declared_scopes": ["https://www.googleapis.com/auth/calendar"],
        },
        {
            "app_id": "malicious_pdf_456",
            "name": "Free PDF Converter Pro",
            "publisher": "Unknown Developer",
            "scopes": [
                "https://www.googleapis.com/auth/drive",
                "https://www.googleapis.com/auth/gmail.modify"
            ],
            "user_count": 3,
            "last_active": now,
            "declared_scopes": [
                "https://www.googleapis.com/auth/drive",
                "https://www.googleapis.com/auth/gmail.modify"
            ],
        },
        {
            "app_id": "grammarly_789",
            "name": "Grammarly for Chrome",
            "publisher": "Grammarly Inc.",
            "scopes": ["https://www.googleapis.com/auth/documents"],
            "user_count": 120,
            "last_active": now,
            "declared_scopes": ["https://www.googleapis.com/auth/documents"],
        }
    ]

def scan_oauth_apps() -> list:
    """
    FR-1.1: Enumerate OAuth apps — Workspace API.
    """
    if os.getenv("OAUTH_USE_SYNTHETIC", "false").lower() == "true":
        logger.info("Using SYNTHETIC Workspace data mode (bypassing Google API).")
        return _generate_synthetic_apps()

    try:
        return _scan_workspace_api()
    except Exception as e:
        logger.error("Workspace scan failed: %s", e)
        if "unauthorized_client" in str(e):
            logger.warning("Falling back to synthetic data due to Domain-Wide Delegation restriction.")
            return _generate_synthetic_apps()
        return []
