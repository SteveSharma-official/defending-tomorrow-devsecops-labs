"""LAB-30 tests: metrics follow Table 35.2 definitions, and gamed evidence is refused."""
import json
import pathlib
import sys

import yaml

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
import metrics  # noqa: E402

RUNS = metrics.load(ROOT / "evidence" / "pipeline-runs.jsonl")
INC = metrics.load(ROOT / "evidence" / "incidents.jsonl")
TARGETS = yaml.safe_load((ROOT / "metrics-targets.yaml").read_text())


def test_evidence_is_intact():
    assert metrics.integrity(RUNS, INC) == []


def test_baseline_metrics():
    m = metrics.compute(RUNS, INC)
    assert m["platform_security_adoption_pct"] == 90.0
    assert m["control_failure_rate_pct"]["SCA"] == 7.5
    assert m["false_positive_rate_pct"] == 37.5
    assert all(v["met"] for v in metrics.against(m, TARGETS).values())


def test_deleting_failed_runs_is_detected():
    kept = [r for r in RUNS if r["run_id"] not in (7, 19, 26)]
    assert metrics.compute(kept, INC)["control_failure_rate_pct"]["SCA"] == 0.0     # the prettier number…
    assert any("missing" in p for p in metrics.integrity(kept, INC))               # …is refused


def test_editing_a_timestamp_is_detected():
    inc = [dict(i) for i in INC]
    inc[0]["alert_at"] = inc[0]["earliest_indicator_at"]
    assert any("INC-001 was modified" in p for p in metrics.integrity(RUNS, inc))


def test_missed_target_is_reported_not_hidden():
    m = dict(metrics.compute(RUNS, INC), mttc_minutes=95.0)
    assert metrics.against(m, TARGETS)["mttc_minutes"]["met"] is False
