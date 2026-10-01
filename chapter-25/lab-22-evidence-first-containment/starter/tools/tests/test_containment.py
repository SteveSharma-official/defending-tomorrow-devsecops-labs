"""Tests for LAB-22: the playbook gate and the evidence manifest."""
import copy
import pathlib
import shutil
import sys

import yaml

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
import check_playbook  # noqa: E402
import evidence_manifest  # noqa: E402

PB = yaml.safe_load((ROOT / "playbooks" / "PB-POD-CONTAIN-001.yaml").read_text())
SAMPLE = ROOT / "evidence-sample" / "case-2026-0931"


def test_baseline_playbook_is_evidence_first():
    assert check_playbook.check(PB) == []


def test_delete_before_filesystem_capture_is_rejected():
    pb = copy.deepcopy(PB)
    steps = pb["steps"]
    delete = next(s for s in steps if s["id"] == "delete_pod")
    steps.remove(delete)
    steps.insert(1, delete)
    findings = check_playbook.check(pb)
    assert any(f.startswith("P1 delete_pod") for f in findings)


def test_auto_approved_irreversible_step_is_rejected():
    pb = copy.deepcopy(PB)
    next(s for s in pb["steps"] if s["id"] == "delete_pod")["approval"] = "auto"
    assert any(f.startswith("P3 delete_pod") for f in check_playbook.check(pb))


def test_sample_evidence_verifies():
    assert evidence_manifest.verify(SAMPLE) == []


def test_tampered_evidence_is_detected(tmp_path):
    case = tmp_path / "case"
    shutil.copytree(SAMPLE, case)
    (case / "logs.txt").write_text("2026-09-30T02:13:44Z GET /orders 200\n", encoding="utf-8")
    (case / "notes.txt").write_text("added later", encoding="utf-8")
    problems = evidence_manifest.verify(case)
    assert "altered: logs.txt" in problems
    assert "added after collection: notes.txt" in problems
