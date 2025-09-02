# src/automation.py
import os
import json
import requests

def post_to_webhook(payload: dict, url: str) -> dict:
    """Send the analysis payload to a webhook (e.g., Slack, Notion, n8n)."""
    try:
        resp = requests.post(url, json=payload, timeout=10)
        return {"status": resp.status_code, "text": resp.text[:500]}
    except Exception as e:
        return {"status": 0, "error": str(e)}

def simulate_make_n8n_job(analysis: dict) -> dict:
    """Pretend to send the analysis to an automation node and get an ack."""
    # In a real demo, set WEBHOOK_URL in env and call post_to_webhook.
    url = os.environ.get("WEBHOOK_URL")
    payload = {"type": "financial_report", **analysis}
    if url:
        return post_to_webhook(payload, url)
    return {"status": "dry-run", "payload_preview": json.dumps(payload)[:300]}
