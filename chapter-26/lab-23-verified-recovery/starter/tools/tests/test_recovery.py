"""LAB-23 tests: restore-target selection and the runbook gate."""
import json
import pathlib
import sys

import yaml

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
import check_runbook  # noqa: E402
import select_recovery_target as sel  # noqa: E402

LEDGER = json.loads((ROOT / "recovery" / "release-ledger.json").read_text())
INCIDENT = yaml.safe_load((ROOT / "recovery" / "incident.yaml").read_text())
POLICY = yaml.safe_load((ROOT / "recovery" / "recovery-policy.yaml").read_text())
RUNBOOK = yaml.safe_load((ROOT / "recovery" / "recovery-runbook.yaml").read_text())


def test_restore_target_is_last_verified_build_before_compromise():
    chosen, rejected = sel.select(LEDGER, INCIDENT, POLICY)
    assert chosen["version"] == "1.4.1"
    assert rejected["1.5.0"] == ["built inside the compromise window"]
    assert "signature not verified" in rejected["1.4.2"]


def test_latest_signed_is_not_good_enough():
    """1.5.0 is signed and attested — it was built by the abused pipeline. It must never be chosen."""
    policy = dict(POLICY, exclude_builds_after_compromise_start=False)
    chosen, _ = sel.select(LEDGER, INCIDENT, policy)
    assert chosen["version"] == "1.5.0"           # what a naive policy would restore
    chosen, _ = sel.select(LEDGER, INCIDENT, POLICY)
    assert chosen["version"] != "1.5.0"


def test_baseline_runbook_passes():
    assert check_runbook.check(RUNBOOK) == []


def test_tag_deploy_and_skipped_verification_fail():
    steps = [dict(s) for s in RUNBOOK["steps"] if s["kind"] != "verify"]
    for step in steps:
        if step["kind"] == "deploy":
            step["image_ref"] = "ghcr.io/example/dt-lab-13:latest"
    findings = check_runbook.check({"steps": steps})
    assert any(f.startswith("R1") for f in findings)
    assert any(f.startswith("R2") for f in findings)
