#!/usr/bin/env python3
"""pipeline_evidence.py — CAPSTONE evidence record built from the workflow's own job results.

Usage: NEEDS_JSON='${{ toJSON(needs) }}' python tools/pipeline_evidence.py controls/pipeline-controls.yaml evidence.json
Every mapped job must appear with result 'success' for overall PASS. Missing jobs are NOT_RUN (fail).
"""
import datetime
import hashlib
import json
import os
import sys

import yaml


def build(needs: dict, mapping: dict) -> dict:
    controls = []
    for job, spec in mapping.items():
        result = needs.get(job, {}).get("result", "not_run")
        controls.append({"job": job, "control_id": spec["control"], "title": spec["title"],
                         "result": result, "status": "PASS" if result == "success" else "FAIL",
                         "frameworks": {k: v for k, v in spec.items() if k not in {"control", "title"}}})
    record = {
        "schema": "dt-pipeline-evidence/v1",
        "generated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
        "repository": os.environ.get("GITHUB_REPOSITORY", "local"),
        "commit": os.environ.get("GITHUB_SHA", "local"),
        "ref": os.environ.get("GITHUB_REF", "local"),
        "run_id": os.environ.get("GITHUB_RUN_ID", "local"),
        "image_digest": os.environ.get("IMAGE_DIGEST", ""),
        "controls": controls,
    }
    record["overall"] = "PASS" if all(c["status"] == "PASS" for c in controls) else "FAIL"
    record["sha256"] = hashlib.sha256(json.dumps(record, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    return record


def main(argv: list[str]) -> int:
    needs = json.loads(os.environ.get("NEEDS_JSON", "{}"))
    with open(argv[1], encoding="utf-8") as handle:
        mapping = yaml.safe_load(handle)
    record = build(needs, mapping)
    with open(argv[2], "w", encoding="utf-8") as handle:
        json.dump(record, handle, indent=2, sort_keys=True)
    lines = ["| Control | Job | Result | NIST CSF 2.0 | ISO 27001:2022 |", "|---|---|---|---|---|"]
    for c in record["controls"]:
        f = c["frameworks"]
        lines.append(f"| {c['control_id']} | {c['job']} | {c['status']} | {', '.join(f.get('nist_csf_2', []))} "
                     f"| {', '.join(f.get('iso27001_2022', []))} |")
    lines.append(f"\n**Overall: {record['overall']}** — evidence sha256 `{record['sha256']}`")
    summary = "\n".join(lines)
    print(summary)
    if os.environ.get("GITHUB_STEP_SUMMARY"):
        with open(os.environ["GITHUB_STEP_SUMMARY"], "a", encoding="utf-8") as handle:
            handle.write("## Security evidence\n\n" + summary + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
