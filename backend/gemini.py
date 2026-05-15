"""
ContextGuard — Gemini Risk Engine
Owner: Asim
Functions:
  score_oauth_app(name, publisher, scopes) → risk score + explanation
  classify_event(event)                    → intent + severity + alert
  generate_report(events)                  → compliance summary
"""

import google.generativeai as genai
from dotenv import load_dotenv
import os
import json
import time

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

model = genai.GenerativeModel("gemini-2.0-flash")

# ══════════════════════════════════════════
# PROMPTS — Edit here to tune AI behavior
# ══════════════════════════════════════════

SCORE_PROMPT = """
You are an enterprise security analyst evaluating third-party AI tools.

Analyze this OAuth application and return ONLY a JSON object (no markdown, no explanation outside JSON):

App Name: {name}
Publisher: {publisher}
Permission Scopes: {scopes}

Return this exact JSON format:
{{
  "risk_score": <integer 0-100>,
  "risk_category": "<LOW|MEDIUM|HIGH|CRITICAL>",
  "explanation": "<1-2 sentence plain English explanation>"
}}

Risk category mapping:
- LOW: 0-29
- MEDIUM: 30-59
- HIGH: 60-79
- CRITICAL: 80-100
"""

CLASSIFY_PROMPT = """
You are a security analyst reviewing an AI agent traffic event flagged by a DPI proxy.

Event details: {event}

Return ONLY a JSON object:
{{
  "intent_category": "<CREDENTIAL_EXFILTRATION|PROMPT_INJECTION|PII_LEAK|DATA_EXFILTRATION|LEGITIMATE>",
  "severity": "<LOW|MEDIUM|HIGH|CRITICAL>",
  "alert_message": "<1 sentence plain English alert for a security dashboard>"
}}
"""

REPORT_PROMPT = """
You are a security compliance officer writing a daily summary report.

Here are the security events from the last 24 hours:
{events}

Write a concise plain-text compliance summary (max 200 words) covering:
1. Total events and breakdown by severity
2. Most significant threats detected
3. Actions taken by the system
4. Recommended next steps for the security team
"""


# ══════════════════════════════════════════
# FUNCTIONS — Asim implements these
# ══════════════════════════════════════════

def call_gemini_with_retry(prompt: str, max_retries: int = 3) -> str:
    """Call Gemini with exponential backoff retry logic."""
    # TODO: Asim — implement retry logic
    # Hint: use time.sleep(2**attempt) between retries
    pass


def score_oauth_app(name: str, publisher: str, scopes: list) -> dict:
    """
    Score an OAuth app's risk level using Gemini.

    Args:
        name: App display name (e.g. "Context.ai")
        publisher: Developer/company name
        scopes: List of permission scopes (e.g. ["read_email", "manage_calendar"])

    Returns:
        {
            "risk_score": 87,
            "risk_category": "CRITICAL",
            "explanation": "This app requests admin-level access..."
        }
    """
    # TODO: Asim — implement this function
    # Steps:
    # 1. Format SCORE_PROMPT with name, publisher, scopes
    # 2. Call call_gemini_with_retry(prompt)
    # 3. Parse JSON from response
    # 4. Return the dict
    pass


def classify_event(event: dict) -> dict:
    """
    Classify a Lobster Trap DPI event using Gemini.

    Args:
        event: Raw event dict from Lobster Trap webhook

    Returns:
        {
            "intent_category": "CREDENTIAL_EXFILTRATION",
            "severity": "CRITICAL",
            "alert_message": "Agent attempted to send API keys to external endpoint."
        }
    """
    # TODO: Asim — implement this function
    pass


def generate_report(events: list) -> str:
    """
    Generate a compliance summary report from a list of events.

    Args:
        events: List of dpi_events dicts from the last 24 hours

    Returns:
        Plain text compliance summary string
    """
    # TODO: Asim — implement this function
    pass
