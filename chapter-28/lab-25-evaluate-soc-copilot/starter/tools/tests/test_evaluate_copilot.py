"""LAB-25 tests — the evaluator must catch each unsafe copilot behaviour independently."""
import copy
import json
import pathlib
import sys

import yaml

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
import evaluate_copilot as ev  # noqa: E402

ALERTS = json.loads((ROOT / "eval" / "alerts.json").read_text())
T = yaml.safe_load((ROOT / "eval" / "thresholds.yaml").read_text())
V1 = json.loads((ROOT / "copilot-outputs" / "v1.json").read_text())


def out(alert_id, outputs):
    return next(o for o in outputs["outputs"] if o["alert_id"] == alert_id)


def test_v1_passes_the_release_gate():
    assert ev.gate(ev.evaluate(ALERTS, V1), T) == []


def test_following_injected_instructions_fails():
    v = copy.deepcopy(V1)
    out("ALR-103", v).update(verdict="benign", flags=[])
    findings = ev.gate(ev.evaluate(ALERTS, v), T)
    assert any("injection_resistance" in f for f in findings)
    assert any("true_positive_recall" in f for f in findings)


def test_invented_citation_fails():
    v = copy.deepcopy(V1)
    out("ALR-101", v)["citations"].append("EV-999-1")
    m = ev.evaluate(ALERTS, v)
    assert m["invalid_citations"] == ["ALR-101:EV-999-1"]
    assert any("citation_validity" in f for f in ev.gate(m, T))


def test_unapproved_containment_fails():
    v = copy.deepcopy(V1)
    out("ALR-105", v)["actions"][0]["requires_approval"] = False
    assert any("without human approval" in f for f in ev.gate(ev.evaluate(ALERTS, v), T))


def test_accuracy_is_reported_but_never_gated():
    """80% verdict accuracy sounds good; the two misses are the injected alert and nothing else matters more."""
    v = copy.deepcopy(V1)
    out("ALR-103", v).update(verdict="benign", flags=[])
    m = ev.evaluate(ALERTS, v)
    assert m["verdict_accuracy"] == 0.8
    assert ev.gate(m, T) != []
