#!/usr/bin/env python3
"""Generate LAB-30's synthetic evidence (deterministic). Each record carries record_sha256 over its
canonical JSON, the way LAB-16 hashes evidence, so edits after the fact are detectable."""
import hashlib
import json
import pathlib
import random
from datetime import datetime, timedelta, timezone

random.seed(35)
OUT = pathlib.Path(__file__).resolve().parents[1] / "evidence"
T0 = datetime(2026, 9, 1, tzinfo=timezone.utc)


def iso(d):
    return d.strftime("%Y-%m-%dT%H:%M:%SZ")


def seal(rec):
    rec["record_sha256"] = hashlib.sha256(json.dumps(rec, sort_keys=True).encode()).hexdigest()
    return rec


def runs():
    out = []
    for n in range(1, 41):
        commit = T0 + timedelta(hours=17 * n)
        golden = n % 10 != 0
        controls = [{"id": c, "blocking": True, "result": "pass"} for c in ("SAST", "SCA", "SECRETS", "IAC")]
        if n in (7, 19, 26):
            controls[1]["result"] = "fail"
        if n == 33:
            controls[2]["result"] = "fail"
        failed = any(c["result"] == "fail" for c in controls)
        rec = {"run_id": n, "commit_at": iso(commit), "golden_path": golden,
               "policy_evaluated": golden, "signed_and_attested": golden and not failed,
               "controls": controls, "deployed": not failed,
               "deployed_at": None if failed else iso(commit + timedelta(minutes=random.randint(25, 140)))}
        out.append(seal(rec))
    return out


def incidents():
    out = []
    for n, cls in enumerate(["true_positive", "false_positive", "true_positive", "false_positive",
                             "false_positive", "true_positive", "benign_true_positive", "true_positive"], 1):
        ind = T0 + timedelta(days=3 * n, hours=2)
        alert = ind + timedelta(minutes=random.randint(3, 40))
        triage = alert + timedelta(minutes=random.randint(5, 30))
        rec = {"incident_id": f"INC-{n:03d}", "classification": cls, "earliest_indicator_at": iso(ind),
               "alert_at": iso(alert), "triage_at": iso(triage)}
        if cls == "true_positive":
            contain = triage + timedelta(minutes=random.randint(10, 60))
            rec.update(contain_at=iso(contain), remediate_at=iso(contain + timedelta(hours=random.randint(2, 20))))
        out.append(seal(rec))
    return out


if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    for name, rows in (("pipeline-runs.jsonl", runs()), ("incidents.jsonl", incidents())):
        (OUT / name).write_text("".join(json.dumps(r, sort_keys=True) + "\n" for r in rows), encoding="utf-8")
    print("evidence written to", OUT)
