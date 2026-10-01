#!/usr/bin/env python3
"""LAB-23 — choose the restore target: the newest release that satisfies the recovery policy.

Usage: python tools/select_recovery_target.py recovery/release-ledger.json recovery/incident.yaml recovery/recovery-policy.yaml
Prints the chosen release as JSON (and writes it to $GITHUB_OUTPUT as digest=… when running in Actions).
"""
import datetime
import json
import os
import sys

import yaml


def ts(s: str) -> datetime.datetime:
    return datetime.datetime.fromisoformat(s.replace("Z", "+00:00"))


def eligible(rel: dict, incident: dict, policy: dict) -> list[str]:
    reasons = []
    if policy.get("require_signature") and not rel["signature_verified"]:
        reasons.append("signature not verified")
    if policy.get("require_provenance") and not rel["provenance_verified"]:
        reasons.append("provenance not verified")
    if rel["vulnerability_gate"] != policy.get("require_vulnerability_gate", "pass"):
        reasons.append("vulnerability gate not passed")
    if policy.get("exclude_builds_after_compromise_start") and \
            ts(rel["built_at"]) >= ts(incident["compromise_window_start"]):
        reasons.append("built inside the compromise window")
    return reasons


def select(ledger: dict, incident: dict, policy: dict) -> tuple[dict | None, dict]:
    rejected = {}
    for rel in sorted(ledger["releases"], key=lambda r: r["built_at"], reverse=True):
        reasons = eligible(rel, incident, policy)
        if not reasons:
            return rel, rejected
        rejected[rel["version"]] = reasons
    return None, rejected


def main(ledger_p: str, incident_p: str, policy_p: str) -> int:
    ledger = json.load(open(ledger_p, encoding="utf-8"))
    incident = yaml.safe_load(open(incident_p, encoding="utf-8"))
    policy = yaml.safe_load(open(policy_p, encoding="utf-8"))
    chosen, rejected = select(ledger, incident, policy)
    for v, why in rejected.items():
        print(f"rejected {v}: {', '.join(why)}")
    if not chosen:
        print("::error::no release satisfies the recovery policy — rebuild from verified source instead")
        return 1
    print(json.dumps(chosen, indent=2))
    if os.environ.get("GITHUB_OUTPUT"):
        with open(os.environ["GITHUB_OUTPUT"], "a", encoding="utf-8") as f:
            f.write(f"digest={chosen['digest']}\nversion={chosen['version']}\n")
    return 0


if __name__ == "__main__":
    sys.exit(main(*sys.argv[1:4]))
