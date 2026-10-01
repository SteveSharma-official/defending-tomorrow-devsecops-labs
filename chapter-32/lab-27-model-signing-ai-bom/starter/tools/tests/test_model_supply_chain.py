"""LAB-27 tests: AI-BOM generation and deployment-time verification (Stages 2–3)."""
import json
import pathlib
import shutil
import sys

import yaml

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
import make_aibom  # noqa: E402
import train  # noqa: E402
import verify_deployment as vd  # noqa: E402

DATA = ROOT / "data" / "phishing-urls.csv"
POLICY = yaml.safe_load((ROOT / "policy" / "deployment-policy.yaml").read_text())


def release(tmp, data=DATA):
    model, evaluation = train.train(train.load(data))
    (tmp / "model.json").write_text(json.dumps(model, indent=2, sort_keys=True))
    (tmp / "evaluation.json").write_text(json.dumps(evaluation))
    shutil.copy(data, tmp / "data.csv")
    bom = make_aibom.build(str(tmp / "model.json"), str(tmp / "data.csv"), str(tmp / "evaluation.json"))
    return bom


def test_clean_release_verifies(tmp_path):
    bom = release(tmp_path)
    assert vd.schema_errors(json.dumps(bom)) == []
    assert vd.verify(str(tmp_path / "model.json"), str(tmp_path / "data.csv"), bom, POLICY) == []


def test_substituted_model_is_blocked(tmp_path):
    bom = release(tmp_path)
    m = json.loads((tmp_path / "model.json").read_text())
    m["centroids"]["1"]["has_at_sign"] = 0.0           # quietly blind the model to one phishing signal
    (tmp_path / "model.json").write_text(json.dumps(m, indent=2, sort_keys=True))
    problems = vd.verify(str(tmp_path / "model.json"), str(tmp_path / "data.csv"), bom, POLICY)
    assert any("model hash does not match" in p for p in problems)


def test_swapped_dataset_is_detected(tmp_path):
    bom = release(tmp_path)
    (tmp_path / "data.csv").write_text((tmp_path / "data.csv").read_text().replace("\n1,", "\n1, ", 1))
    problems = vd.verify(str(tmp_path / "model.json"), str(tmp_path / "data.csv"), bom, POLICY)
    assert any("dataset hash does not match" in p for p in problems)


def test_poisoned_training_data_fails_the_evaluation_gate(tmp_path):
    bom = release(tmp_path, ROOT / "lab-changes" / "phishing-urls-poisoned.csv")
    problems = vd.verify(str(tmp_path / "model.json"), str(tmp_path / "data.csv"), bom, POLICY)
    assert any(p.startswith("Stage 3: accuracy") for p in problems)


def test_disallowed_licence_is_blocked(tmp_path):
    bom = release(tmp_path)
    bom["components"][0]["licenses"] = [{"license": {"id": "CC-BY-NC-4.0"}}]
    problems = vd.verify(str(tmp_path / "model.json"), str(tmp_path / "data.csv"), bom, POLICY)
    assert any("licence" in p for p in problems)
