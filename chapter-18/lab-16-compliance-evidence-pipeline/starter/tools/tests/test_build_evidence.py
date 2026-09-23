import json
import os
import sys

import yaml

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import build_evidence  # noqa: E402

MAPPING = {"controls": {
    "A": {"title": "vuln", "tool": "pip-audit", "blocking": True, "frameworks": {}},
    "B": {"title": "secrets", "tool": "gitleaks", "blocking": True, "frameworks": {}},
}}


def write(tmp, name, obj):
    (tmp / name).write_text(json.dumps(obj))


def test_all_clean_passes(tmp_path):
    write(tmp_path, "pip-audit.json", {"dependencies": [{"name": "flask", "vulns": []}]})
    write(tmp_path, "gitleaks.json", [])
    assert build_evidence.build(str(tmp_path), MAPPING)["overall"] == "PASS"


def test_vulnerability_fails_blocking_control(tmp_path):
    write(tmp_path, "pip-audit.json", {"dependencies": [{"name": "pyyaml", "vulns": [{"id": "PYSEC-2021-142"}]}]})
    write(tmp_path, "gitleaks.json", [])
    record = build_evidence.build(str(tmp_path), MAPPING)
    assert record["overall"] == "FAIL" and record["controls"][0]["findings"] == 1


def test_missing_tool_output_is_not_run_and_fails(tmp_path):
    write(tmp_path, "gitleaks.json", [])
    record = build_evidence.build(str(tmp_path), MAPPING)
    assert record["controls"][0]["status"] == "NOT_RUN" and record["overall"] == "FAIL"


def test_mapping_file_is_valid():
    path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
                        "controls", "mapping.yaml")
    mapping = yaml.safe_load(open(path, encoding="utf-8"))
    for spec in mapping["controls"].values():
        assert spec["tool"] in build_evidence.COLLECTORS
