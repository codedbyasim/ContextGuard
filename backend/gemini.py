"""
ContextGuard — Gemini Risk Engine (via AIMLAPI)
Owner: Asim
Functions:
  score_oauth_app(name, publisher, scopes) → risk score + explanation
  classify_event(event)                    → intent + severity + alert
  generate_report(events)                  → compliance summary
"""

import os
import json
import time
import requests
from dotenv import load_dotenv

load_dotenv()

AIMLAPI_KEY = os.getenv("GEMINI_API_KEY")
AIMLAPI_URL = "https://api.aimlapi.com/v1/chat/completions"
# Using google/gemini-2.0-flash as the model identifier on AIMLAPI
MODEL_NAME = "google/gemini-2.0-flash"

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
    """Call Gemini via AIMLAPI with exponential backoff retry logic."""
    headers = {
        "Authorization": f"Bearer {AIMLAPI_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.1,
        "max_tokens": 1024
    }

    for attempt in range(max_retries):
        try:
            response = requests.post(AIMLAPI_URL, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"]
        except Exception as e:
            if attempt == max_retries - 1:
                response_text = response.text if 'response' in locals() else 'No response body'
                raise Exception(f"AIMLAPI failed after {max_retries} attempts: {e} - Response: {response_text}")
            time.sleep(2 ** attempt)
    return ""


def score_oauth_app(name: str, publisher: str, scopes: list) -> dict:
    formatted_prompt = SCORE_PROMPT.format(
        name=name,
        publisher=publisher,
        scopes=json.dumps(scopes)
    )
    
    try:
        response_text = call_gemini_with_retry(formatted_prompt)
        if response_text.startswith("```json"):
            response_text = response_text[7:-3]
        elif response_text.startswith("```"):
            response_text = response_text[3:-3]
            
        return json.loads(response_text.strip())
    except Exception as e:
        print(f"Error scoring app {name}: {e}")
        return {
            "risk_score": 0,
            "risk_category": "UNKNOWN",
            "explanation": f"Failed to score app due to error: {e}"
        }


def classify_event(event: dict) -> dict:
    formatted_prompt = CLASSIFY_PROMPT.format(
        event=json.dumps(event)
    )
    
    try:
        response_text = call_gemini_with_retry(formatted_prompt)
        if response_text.startswith("```json"):
            response_text = response_text[7:-3]
        elif response_text.startswith("```"):
            response_text = response_text[3:-3]
            
        return json.loads(response_text.strip())
    except Exception as e:
        print(f"Error classifying event: {e}")
        return {
            "intent_category": "UNKNOWN",
            "severity": "LOW",
            "alert_message": "Failed to classify event."
        }


def generate_report(events: list) -> str:
    if not events:
        return "No security events recorded in the last 24 hours. The environment is currently secure."
        
    formatted_prompt = REPORT_PROMPT.format(
        events=json.dumps(events, indent=2)
    )
    
    try:
        response_text = call_gemini_with_retry(formatted_prompt)
        return response_text.strip()
    except Exception as e:
        print(f"Error generating report: {e}")
        return f"Error generating compliance report: {e}"
