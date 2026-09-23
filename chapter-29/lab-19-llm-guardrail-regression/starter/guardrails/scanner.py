"""Heuristic indirect-prompt-injection scanner for retrieved content and tool outputs (LAB-19).

This is ONE layer (Chapter 29 PIDF Layer 2/4, Chapter 30 retrieval gate). Heuristics are
bypassable by design; the architectural controls (least-privilege tools — LAB-18, output
validation, human approval) are what bound the impact. The value of this module is that its
behaviour is MEASURED on every change.
"""
import base64
import re
import unicodedata

PATTERNS: dict[str, str] = {
    "override_instructions": r"\b(ignore|disregard|forget|override)\b.{0,40}\b(previous|prior|above|earlier|system)\b.{0,20}\b(instructions?|prompts?|rules?|messages?)\b",
    "role_reassignment": r"\byou are (now|no longer)\b|\bact as (an? )?(admin|administrator|developer mode|system)\b",
    "privilege_claim": r"\b(the )?user (has|is granted|now has) (elevated|admin|root|full) (privileges?|access|rights)\b",
    "exfiltration_request": r"\b(send|post|upload|exfiltrate|forward|email)\b.{0,60}\b(https?://|all (customer|user)s?|credentials?|api keys?|secrets?)",
    "tool_coercion": r"\b(call|invoke|execute|run|use)\b.{0,20}\b(the )?(tool|function|command)\b.{0,40}\b(without|no|skip)\b.{0,15}\b(confirmation|approval|asking)\b",
    "hidden_markup": r"<\s*(system|assistant|im_start|\|im_start\|)\b|\[\s*(system|INST)\s*\]",
}
COMPILED = {name: re.compile(p, re.IGNORECASE | re.DOTALL) for name, p in PATTERNS.items()}
THRESHOLD = 1  # number of indicators required to flag


def normalise(text: str) -> str:
    """Defeat trivial evasions: Unicode confusables/compatibility forms, zero-width chars, base64 blobs."""
    text = unicodedata.normalize("NFKC", text)
    text = re.sub(r"[​-‏⁠﻿]", "", text)
    decoded = []
    for blob in re.findall(r"[A-Za-z0-9+/]{24,}={0,2}", text):
        try:
            decoded.append(base64.b64decode(blob, validate=True).decode("utf-8", "ignore"))
        except ValueError:
            continue
    return " ".join([text, *decoded])


def scan(text: str) -> dict:
    normalised = normalise(text)
    hits = sorted(name for name, rx in COMPILED.items() if rx.search(normalised))
    return {"flagged": len(hits) >= THRESHOLD, "indicators": hits}
