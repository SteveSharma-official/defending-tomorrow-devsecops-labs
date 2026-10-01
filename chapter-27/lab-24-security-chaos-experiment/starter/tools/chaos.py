#!/usr/bin/env python3
"""LAB-24 — security chaos experiment checks (Chapter 27, SCEF).

check <experiment.yaml>              Define/Guard gate: four-element hypothesis with measurable limits,
                                     bounded blast radius, abort conditions, rollback, approver.
evaluate <experiment.yaml> <run.json> Execute/Learn: compare measured times with the hypothesis; every
                                     failed expectation must be recorded under learn.findings.
"""
import datetime
import json
import sys

import yaml

EXPECTATIONS = (("detection", "detected_at"), ("response", "responded_at"), ("recovery", "recovered_at"))


def check(exp: dict) -> list[str]:
    f = []
    define, guard = exp.get("define", {}), exp.get("guard", {})
    if not define.get("condition"):
        f.append("DEFINE condition is missing")
    for name, _ in EXPECTATIONS:
        if not isinstance((define.get(name) or {}).get("max_seconds"), int):
            f.append(f"DEFINE {name} expectation has no measurable max_seconds — the hypothesis cannot pass or fail")
    namespaces = (guard.get("blast_radius") or {}).get("namespaces", [])
    if not namespaces or any(n in ("*", "all") or not n.startswith("lab24-") for n in namespaces):
        f.append(f"GUARD blast radius {namespaces or 'unset'} is not limited to lab24-* namespaces")
    if guard.get("environment") != "kind":
        f.append("GUARD experiment must target the disposable kind environment in this lab")
    if not guard.get("abort_conditions"):
        f.append("GUARD no abort conditions")
    if not guard.get("rollback"):
        f.append("GUARD no rollback command")
    if not isinstance(guard.get("max_duration_minutes"), int) or guard["max_duration_minutes"] > 30:
        f.append("GUARD max_duration_minutes must be set and ≤ 30")
    if not guard.get("approved_by"):
        f.append("GUARD no named approver")
    return f


def ts(s: str) -> datetime.datetime:
    return datetime.datetime.fromisoformat(s.replace("Z", "+00:00"))


def evaluate(exp: dict, run: dict) -> tuple[dict, list[str]]:
    start, results, problems = ts(run["injection_at"]), {}, []
    for name, field in EXPECTATIONS:
        limit = exp["define"][name]["max_seconds"]
        if field not in run:
            results[name] = {"limit_s": limit, "measured_s": None, "result": "FAIL (never observed)"}
        else:
            measured = (ts(run[field]) - start).total_seconds()
            results[name] = {"limit_s": limit, "measured_s": measured,
                             "result": "PASS" if measured <= limit else "FAIL"}
    recorded = {fd.get("expectation") for fd in (exp.get("learn") or {}).get("findings", [])}
    for name, r in results.items():
        if r["result"] != "PASS" and name not in recorded:
            problems.append(f"LEARN {name} failed ({r['result']}) but no finding is recorded in learn.findings")
    return results, problems


def main() -> int:
    cmd, exp = sys.argv[1], yaml.safe_load(open(sys.argv[2], encoding="utf-8"))
    if cmd == "check":
        problems = check(exp)
    else:
        results, problems = evaluate(exp, json.load(open(sys.argv[3], encoding="utf-8")))
        print(json.dumps(results, indent=2))
    for p in problems:
        print(f"::error::{p}")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
