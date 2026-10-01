"""Unit tests for LAB-20's collector and telemetry checks."""
import json
import pathlib
import sys

import yaml

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
import check_collector  # noqa: E402
import check_telemetry  # noqa: E402

CFG = ROOT / "collector" / "security-collector.yaml"
SCHEMA = yaml.safe_load((ROOT / "schema" / "minimum-security-log-schema.yaml").read_text())
EVENTS = [json.loads(x) for x in (ROOT / "samples" / "events.jsonl").read_text().splitlines() if x]


def findings(raw):
    return check_collector.check(yaml.safe_load(raw), raw)


def test_baseline_collector_is_clean():
    assert findings(CFG.read_text()) == []


def test_sampling_on_logs_pipeline_is_rejected():
    raw = CFG.read_text().replace("processors: [k8sattributes, attributes/security, batch]",
                                  "processors: [k8sattributes, attributes/security, probabilistic_sampler, batch]")
    assert any(f.startswith("C2") for f in findings(raw))


def test_bare_placeholder_and_literal_token_are_rejected():
    raw = CFG.read_text().replace("${env:DATA_PLANE_TOKEN}", "dp_live_0000000000000000")
    assert any(f.startswith("C4") for f in findings(raw))
    raw = CFG.read_text().replace("${env:DATA_PLANE_TOKEN}", "${DATA_PLANE_TOKEN}")
    assert any(f.startswith("C3") for f in findings(raw))


def test_enrichment_order_matters():
    raw = CFG.read_text().replace("[k8sattributes, attributes/security, batch]", "[attributes/security, k8sattributes, batch]")
    assert any(f.startswith("C1") for f in findings(raw))


def test_sample_events_meet_schema():
    report, errors = check_telemetry.evaluate(SCHEMA, EVENTS)
    assert errors == []
    assert all(v["completeness_pct"] == 100.0 for v in report.values())


def test_missing_outcome_breaks_completeness():
    events = [dict(e) for e in EVENTS]
    for e in events:
        if e["event_type"] == "authentication":
            e.pop("outcome")
    _, errors = check_telemetry.evaluate(SCHEMA, events)
    assert any(e.startswith("authentication: completeness") for e in errors)


def test_invalid_outcome_value_is_rejected():
    events = [dict(EVENTS[0], outcome="ok")]
    _, errors = check_telemetry.evaluate(SCHEMA, events)
    assert any("outcome='ok'" in e for e in errors)
