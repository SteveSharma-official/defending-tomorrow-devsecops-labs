#!/usr/bin/env python3
"""LAB-23 — recovery runbook gate (Chapter 26 §26.4.2).

R1  signature AND provenance verification run before any deploy step
R2  deploy steps reference images by digest (@sha256 or <digest>), never by tag
R3  a health gate runs between deploy and traffic restoration
R4  traffic is isolated before the target is deployed
Usage: python tools/check_runbook.py recovery/recovery-runbook.yaml
"""
import sys

import yaml


def check(rb: dict) -> list[str]:
    findings, seen = [], []
    for step in rb["steps"]:
        kind, sid = step["kind"], step["id"]
        if kind == "deploy":
            verified = {s["id"] for s in rb["steps"][:len(seen)] if s["kind"] == "verify"}
            if not {"verify-signature", "verify-provenance"} <= verified:
                findings.append(f"R1 {sid}: deploys before signature and provenance are verified")
            ref = str(step.get("image_ref", ""))
            if "@" not in ref:
                findings.append(f"R2 {sid}: image referenced by tag ({ref}) — use the verified digest")
            if not any(s["kind"] == "traffic" for s in rb["steps"][:len(seen)]):
                findings.append(f"R4 {sid}: deploys while compromised traffic is still flowing")
        if kind == "traffic" and any(s["kind"] == "deploy" for s in rb["steps"][:len(seen)]):
            if not any(s["kind"] == "health" for s in rb["steps"][:len(seen)]):
                findings.append(f"R3 {sid}: restores traffic without a health gate")
        seen.append(sid)
    return findings


if __name__ == "__main__":
    path = sys.argv[1]
    fs = check(yaml.safe_load(open(path, encoding="utf-8")))
    for f in fs:
        print(f"::error file={path}::{f}")
    print(f"{len(fs)} finding(s)")
    sys.exit(1 if fs else 0)
