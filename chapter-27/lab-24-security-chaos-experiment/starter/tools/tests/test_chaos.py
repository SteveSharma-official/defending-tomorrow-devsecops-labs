"""LAB-24 tests: the SCEF Define/Guard gate and the Execute/Learn evaluator."""
import copy
import json
import pathlib
import sys

import yaml

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
import chaos  # noqa: E402

EXP = yaml.safe_load((ROOT / "experiments" / "EXP-001-psa-enforcement-removed.yaml").read_text())
RUN = json.loads((ROOT / "results" / "sample-run.json").read_text())


def test_baseline_experiment_is_well_formed_and_guarded():
    assert chaos.check(EXP) == []


def test_unbounded_blast_radius_is_rejected():
    exp = copy.deepcopy(EXP)
    exp["guard"]["blast_radius"]["namespaces"] = ["*"]
    exp["guard"].pop("abort_conditions")
    found = chaos.check(exp)
    assert any(f.startswith("GUARD blast radius") for f in found)
    assert "GUARD no abort conditions" in found


def test_unmeasurable_hypothesis_is_rejected():
    exp = copy.deepcopy(EXP)
    exp["define"]["detection"].pop("max_seconds")
    assert any("detection expectation has no measurable" in f for f in chaos.check(exp))


def test_sample_run_passes_every_expectation():
    results, problems = chaos.evaluate(EXP, RUN)
    assert problems == [] and all(r["result"] == "PASS" for r in results.values())


def test_slow_detection_must_become_a_finding():
    run = dict(RUN, detected_at="2026-09-30T04:12:30Z")        # 148 s against a 60 s hypothesis
    results, problems = chaos.evaluate(EXP, run)
    assert results["detection"]["result"] == "FAIL"
    assert problems and problems[0].startswith("LEARN detection failed")
    exp = copy.deepcopy(EXP)
    exp["learn"]["findings"].append({"expectation": "detection", "owner": "detection-engineering",
                                     "action": "reduce drift-watch interval"})
    assert chaos.evaluate(exp, run)[1] == []
