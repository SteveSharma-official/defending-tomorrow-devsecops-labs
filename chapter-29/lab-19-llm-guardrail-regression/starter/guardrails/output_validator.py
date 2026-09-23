"""Output validation before an LLM response reaches a user or downstream system (LAB-19).

Corrects the Chapter 29/30 listings: dictionary keys are strings (the Chapter 30 listing uses bare
names such as {type: ...}, a NameError), `context` is accessed consistently as a dict, and the
PII redaction happens before hashing so logs never hold raw PII.
"""
import hashlib
import json
import re

from guardrails.scanner import scan

PII = {
    "email": re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"),
    "au_phone": re.compile(r"(?:\+61|0)4\d{2}[ ]?\d{3}[ ]?\d{3}"),
}
ACTION_INTENT = re.compile(r"\b(delete|drop|transfer|refund|grant|revoke|disable)\b", re.IGNORECASE)


def validate(response: str, context: dict) -> dict:
    if ACTION_INTENT.search(response) and not context.get("actions_permitted", False):
        return {"approved": False, "reason": "action-intent requires human review", "route": "human_review"}
    redacted, found = response, []
    for kind, rx in PII.items():
        if rx.search(redacted):
            found.append(kind)
            redacted = rx.sub(f"[REDACTED-{kind.upper()}]", redacted)
    schema = context.get("expected_keys")
    if schema:
        try:
            payload = json.loads(redacted)
        except json.JSONDecodeError:
            return {"approved": False, "reason": "response is not valid JSON", "route": "quarantine"}
        missing = [k for k in schema if k not in payload]
        if missing:
            return {"approved": False, "reason": f"schema violation: missing {missing}", "route": "quarantine"}
    injection = scan(redacted)
    if injection["flagged"]:
        return {"approved": False, "reason": f"injection indicators {injection['indicators']}",
                "route": "security_review", "response_sha256": hashlib.sha256(redacted.encode()).hexdigest()}
    return {"approved": True, "response": redacted, "pii_redacted": found}
