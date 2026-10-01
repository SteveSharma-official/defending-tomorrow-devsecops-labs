#!/usr/bin/env python3
"""LAB-30 — compute Chapter 35 operational metrics from evidence, refusing evidence that has been gamed.

Integrity (fails the build): every record's record_sha256 matches its content; pipeline run IDs are
contiguous (deleting "flaky" failed runs is how control-failure rates get prettier).
Metrics (Table 35.2): Platform Security Adoption, Policy-as-Code Enforcement Rate, Supply Chain Integrity
Rate, control failure rate per control, deployment lead time, MTTD, Mean Time to Triage, MTTC, MTTR,
False-Positive Rate. Targets in metrics-targets.yaml are reported as met / missed (a missed target is a
finding for the programme, not a build failure — only untrustworthy evidence fails the build).
Usage: python tools/metrics.py evidence metrics-targets.yaml out/
"""
import hashlib
import json
import pathlib
import statistics
import sys
from datetime import datetime

import yaml


def load(p):
    return [json.loads(x) for x in p.read_text(encoding="utf-8").splitlines() if x.strip()]


def t(s):
    return datetime.fromisoformat(s.replace("Z", "+00:00"))


def minutes(a, b):
    return (t(b) - t(a)).total_seconds() / 60


def integrity(runs, incidents):
    problems = []
    for r in runs + incidents:
        body = {k: v for k, v in r.items() if k != "record_sha256"}
        if hashlib.sha256(json.dumps(body, sort_keys=True).encode()).hexdigest() != r.get("record_sha256"):
            problems.append(f"record {r.get('run_id', r.get('incident_id'))} was modified after it was sealed")
    ids = sorted(r["run_id"] for r in runs)
    missing = sorted(set(range(ids[0], ids[-1] + 1)) - set(ids)) if ids else []
    if missing:
        problems.append(f"pipeline run IDs missing from the evidence: {missing}")
    return problems


def compute(runs, incidents):
    n = len(runs)
    pct = lambda k: round(100 * sum(bool(r[k]) for r in runs) / n, 1)  # noqa: E731
    deployed = [r for r in runs if r["deployed"]]
    cf = {}
    for r in runs:
        for c in r["controls"]:
            cf.setdefault(c["id"], [0, 0])
            cf[c["id"]][0] += c["result"] == "fail"
            cf[c["id"]][1] += 1
    tp = [i for i in incidents if i["classification"] == "true_positive"]
    mean = lambda xs: round(statistics.mean(xs), 1) if xs else None  # noqa: E731
    return {
        "pipeline_runs": n,
        "platform_security_adoption_pct": pct("golden_path"),
        "policy_as_code_enforcement_pct": pct("policy_evaluated"),
        "supply_chain_integrity_pct": round(100 * sum(r["signed_and_attested"] for r in deployed) / len(deployed), 1),
        "control_failure_rate_pct": {k: round(100 * f / tot, 1) for k, (f, tot) in sorted(cf.items())},
        "lead_time_minutes_median": statistics.median(minutes(r["commit_at"], r["deployed_at"]) for r in deployed),
        "mttd_minutes": mean([minutes(i["earliest_indicator_at"], i["alert_at"]) for i in tp]),
        "mean_time_to_triage_minutes": mean([minutes(i["alert_at"], i["triage_at"]) for i in incidents]),
        "mttc_minutes": mean([minutes(i["triage_at"], i["contain_at"]) for i in tp]),
        "mttr_hours": mean([minutes(i["contain_at"], i["remediate_at"]) / 60 for i in tp]),
        "false_positive_rate_pct": round(100 * sum(i["classification"] == "false_positive" for i in incidents) / len(incidents), 1),
    }


def against(m, targets):
    checks = {
        "platform_security_adoption_pct": ("min", targets["platform_security_adoption_pct_min"]),
        "policy_as_code_enforcement_pct": ("min", targets["policy_as_code_enforcement_pct_min"]),
        "supply_chain_integrity_pct": ("min", targets["supply_chain_integrity_pct_min"]),
        "mttd_minutes": ("max", targets["mttd_minutes_max"]),
        "mttc_minutes": ("max", targets["mttc_minutes_max"]),
        "false_positive_rate_pct": ("max", targets["false_positive_rate_pct_max"]),
    }
    return {k: {"value": m[k], "target": f"{'≥' if d == 'min' else '≤'} {v}",
                "met": m[k] >= v if d == "min" else m[k] <= v} for k, (d, v) in checks.items()}


def main(ev_dir, targets_p, out_dir) -> int:
    ev = pathlib.Path(ev_dir)
    runs, incidents = load(ev / "pipeline-runs.jsonl"), load(ev / "incidents.jsonl")
    problems = integrity(runs, incidents)
    for p in problems:
        print(f"::error::untrustworthy evidence: {p}")
    if problems:
        return 1
    m = compute(runs, incidents)
    status = against(m, yaml.safe_load(open(targets_p, encoding="utf-8")))
    out = pathlib.Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    (out / "metrics.json").write_text(json.dumps({"metrics": m, "targets": status}, indent=2), encoding="utf-8")
    lines = ["# Security metrics from evidence (Chapter 35, Table 35.2)", "", "| Metric | Value | Target | Met |",
             "|---|---|---|---|"]
    lines += [f"| {k} | {v['value']} | {v['target']} | {'yes' if v['met'] else '**no**'} |" for k, v in status.items()]
    lines += ["", f"Control failure rate (%): {m['control_failure_rate_pct']}",
              f"Median deployment lead time: {m['lead_time_minutes_median']} min · MTTR: {m['mttr_hours']} h"]
    (out / "metrics.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    sys.exit(main(*sys.argv[1:4]))
