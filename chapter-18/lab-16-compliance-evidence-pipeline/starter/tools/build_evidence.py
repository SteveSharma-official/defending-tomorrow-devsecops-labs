#!/usr/bin/env python3
"""build_evidence.py — turn raw tool output into a hashed, framework-mapped evidence record (LAB-16).

Usage: build_evidence.py <results-dir> <mapping.yaml> <out.json>
Expects in <results-dir>: pip-audit.json, gitleaks.json, checkov.json, pytest.xml
Exit code 1 if any *blocking* control failed (the pipeline gate); the evidence is written either way.
"""
import datetime
import hashlib
import json
import os
import sys
import xml.etree.ElementTree as ET

import yaml


def _load_json(path):
    if not os.path.exists(path):
        return None
    with open(path, encoding="utf-8") as handle:
        text = handle.read().strip()
    return json.loads(text) if text else None


def pip_audit_findings(results):
    data = _load_json(os.path.join(results, "pip-audit.json"))
    if data is None:
        return None
    return sum(len(dep.get("vulns", [])) for dep in data.get("dependencies", []))


def gitleaks_findings(results):
    data = _load_json(os.path.join(results, "gitleaks.json"))
    return None if data is None else len(data)


def checkov_findings(results):
    data = _load_json(os.path.join(results, "checkov.json"))
    if data is None:
        return None
    reports = data if isinstance(data, list) else [data]
    return sum(r.get("summary", {}).get("failed", 0) for r in reports)


def pytest_findings(results):
    path = os.path.join(results, "pytest.xml")
    if not os.path.exists(path):
        return None
    root = ET.parse(path).getroot()
    suites = [root] if root.tag == "testsuite" else list(root)
    return sum(int(s.get("failures", 0)) + int(s.get("errors", 0)) for s in suites)


COLLECTORS = {"pip-audit": pip_audit_findings, "gitleaks": gitleaks_findings,
              "checkov": checkov_findings, "pytest": pytest_findings}


def build(results_dir, mapping):
    controls = []
    for control_id, spec in mapping["controls"].items():
        findings = COLLECTORS[spec["tool"]](results_dir)
        status = "NOT_RUN" if findings is None else ("PASS" if findings == 0 else "FAIL")
        controls.append({"control_id": control_id, "title": spec["title"], "tool": spec["tool"],
                         "blocking": spec.get("blocking", False), "status": status,
                         "findings": findings, "frameworks": spec["frameworks"]})
    record = {
        "schema": "dt-evidence/v1",
        "generated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
        "repository": os.environ.get("GITHUB_REPOSITORY", "local"),
        "commit": os.environ.get("GITHUB_SHA", "local"),
        "run_url": (f"{os.environ.get('GITHUB_SERVER_URL', '')}/{os.environ.get('GITHUB_REPOSITORY', '')}"
                    f"/actions/runs/{os.environ.get('GITHUB_RUN_ID', '')}"),
        "controls": controls,
    }
    record["overall"] = "FAIL" if any(c["blocking"] and c["status"] != "PASS" for c in controls) else "PASS"
    canonical = json.dumps(record, sort_keys=True, separators=(",", ":")).encode()
    record["sha256"] = hashlib.sha256(canonical).hexdigest()
    return record


def main(argv):
    results_dir, mapping_path, out_path = argv[1], argv[2], argv[3]
    with open(mapping_path, encoding="utf-8") as handle:
        mapping = yaml.safe_load(handle)
    record = build(results_dir, mapping)
    with open(out_path, "w", encoding="utf-8") as handle:
        json.dump(record, handle, indent=2, sort_keys=True)
    for c in record["controls"]:
        print(f"{c['control_id']:<13} {c['status']:<8} findings={c['findings']} {c['frameworks']}")
    print(f"OVERALL: {record['overall']}  sha256={record['sha256']}")
    return 0 if record["overall"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
