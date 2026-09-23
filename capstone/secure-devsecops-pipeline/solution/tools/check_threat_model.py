#!/usr/bin/env python3
"""check_threat_model.py — validates a threat model written as code (LAB-01).

Rules enforced (each maps to Chapter 4's method):
  R1  Every data flow that crosses a trust boundary has at least one threat.
  R2  Every threat names a STRIDE category (S, T, R, I, D, E) or the book's agent
      extension category "A" (agency / tool misuse).
  R3  Every threat has at least one mitigation with an owner and a status.
  R4  High-risk threats must be mitigated ("implemented") or formally accepted
      with an approver and an expiry date that has not passed.
Exit code 0 = model complete; 1 = gaps found (the CI gate fails).
"""
import datetime
import sys

import yaml

VALID_CATEGORIES = {"S", "T", "R", "I", "D", "E", "A"}


def check(model: dict) -> list[str]:
    errors: list[str] = []
    boundaries = {b["id"] for b in model.get("trust_boundaries", [])}
    threats = model.get("threats", [])
    threats_by_flow: dict[str, list[dict]] = {}
    for threat in threats:
        threats_by_flow.setdefault(threat.get("flow", ""), []).append(threat)

    for flow in model.get("data_flows", []):
        crossed = flow.get("crosses")
        if crossed and crossed not in boundaries:
            errors.append(f"R1 flow {flow['id']} crosses unknown boundary '{crossed}'")
        if crossed and not threats_by_flow.get(flow["id"]):
            errors.append(f"R1 flow {flow['id']} ({flow.get('from')} -> {flow.get('to')}) crosses "
                          f"{crossed} but has no threats recorded")

    today = datetime.date.today()
    for threat in threats:
        tid = threat.get("id", "<no id>")
        if threat.get("category") not in VALID_CATEGORIES:
            errors.append(f"R2 {tid} has invalid category '{threat.get('category')}'")
        mitigations = threat.get("mitigations") or []
        if not mitigations:
            errors.append(f"R3 {tid} has no mitigations")
        for m in mitigations:
            if not m.get("owner") or not m.get("status"):
                errors.append(f"R3 {tid} mitigation '{m.get('control', '?')}' lacks owner or status")
        if threat.get("risk") == "high":
            implemented = any(m.get("status") == "implemented" for m in mitigations)
            acceptance = threat.get("risk_acceptance") or {}
            expiry = acceptance.get("expires")
            accepted = bool(acceptance.get("approver")) and bool(expiry) and \
                datetime.date.fromisoformat(str(expiry)) >= today
            if not (implemented or accepted):
                errors.append(f"R4 {tid} is high risk but has no implemented mitigation "
                              f"or valid risk acceptance")
    return errors


def main(path: str) -> int:
    with open(path, encoding="utf-8") as handle:
        model = yaml.safe_load(handle)
    errors = check(model)
    flows = len(model.get("data_flows", []))
    print(f"Threat model: {model.get('system')} — {flows} data flows, "
          f"{len(model.get('threats', []))} threats")
    for e in errors:
        print(f"::error file={path}::{e}")
    print("RESULT:", "FAIL" if errors else "PASS", f"({len(errors)} gaps)")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else "threat-model/threat-model.yaml"))
