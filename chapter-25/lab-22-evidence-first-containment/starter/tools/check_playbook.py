#!/usr/bin/env python3
"""LAB-22 — enforce the containment sequence model on a playbook (Chapter 25 §25.3, §25.5).

P1  no destructive step (class destroy) before logs, spec, events and filesystem are preserved
P2  evidence is hashed (manifest) before the first isolate/revoke/destroy step
P3  only reversible, single-entity steps may run with approval: auto (§25.5 blast radius × reversibility)
P4  isolation comes before credential revocation and destruction (lowest blast radius first)
Usage: python tools/check_playbook.py playbooks/*.yaml
"""
import sys

import yaml

REQUIRED_EVIDENCE = {"spec", "events", "logs", "filesystem"}
LOW_BLAST = {"none", "single_workload", "single_entity"}


def check(pb: dict) -> list[str]:
    findings, preserved, hashed, isolated = [], set(), False, False
    for n, step in enumerate(pb.get("steps", []), 1):
        sid, cls = step.get("id", f"step{n}"), step.get("class")
        if cls == "preserve":
            preserved |= set(step.get("evidence", []))
            hashed = hashed or "manifest" in step.get("evidence", [])
        if cls in ("isolate", "revoke", "destroy") and not hashed:
            findings.append(f"P2 {sid}: runs before evidence is hashed into a manifest")
        if cls == "destroy" and not REQUIRED_EVIDENCE <= preserved:
            missing = ", ".join(sorted(REQUIRED_EVIDENCE - preserved))
            findings.append(f"P1 {sid}: destroys the workload before preserving: {missing}")
        if step.get("approval") == "auto" and (not step.get("reversible") or step.get("blast_radius") not in LOW_BLAST):
            findings.append(f"P3 {sid}: auto-approved but irreversible or wide blast radius")
        if cls == "isolate":
            isolated = True
        if cls in ("revoke", "destroy") and not isolated:
            findings.append(f"P4 {sid}: runs before the entity is isolated")
    return findings


def main(paths: list[str]) -> int:
    total = 0
    for p in paths:
        for f in check(yaml.safe_load(open(p, encoding="utf-8"))):
            print(f"::error file={p}::{f}")
            total += 1
    print(f"{len(paths)} playbook(s), {total} finding(s)")
    return 1 if total else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
