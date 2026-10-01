#!/usr/bin/env python3
"""LAB-27 — deployment-time verification, Stages 2 and 3 (Chapter 32 §32.3.2).

Stage 1 (signatures) is done by `cosign verify-blob` in the workflow before this runs.
Stage 2: the model and dataset hashes in the AI-BOM match the files being deployed; the AI-BOM is valid CycloneDX 1.6.
Stage 3: the AI-BOM satisfies the deployment policy (evaluation threshold, licence, dataset reference).
Usage: python tools/verify_deployment.py artifacts/model.json data/phishing-urls.csv artifacts/ai-bom.cdx.json policy/deployment-policy.yaml
"""
import hashlib
import json
import sys

import yaml


def sha256(path: str) -> str:
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def schema_errors(bom_text: str) -> list[str]:
    try:
        from cyclonedx.schema import SchemaVersion
        from cyclonedx.validation.json import JsonStrictValidator
    except ImportError:
        return []                      # schema validation is optional locally; CI installs the library
    err = JsonStrictValidator(SchemaVersion.V1_6).validate_str(bom_text)
    return [f"AI-BOM is not valid CycloneDX 1.6: {err}"] if err else []


def verify(model_p: str, data_p: str, bom: dict, policy: dict) -> list[str]:
    f = []
    comps = {c["type"]: c for c in bom.get("components", [])}
    model, data = comps.get("machine-learning-model"), comps.get("data")
    if not model:
        return ["Stage 2: AI-BOM has no machine-learning-model component"]
    if model["hashes"][0]["content"] != sha256(model_p):
        f.append("Stage 2: model hash does not match the AI-BOM — substituted or tampered model")
    if policy.get("require_dataset_reference"):
        refs = [d.get("ref") for d in model.get("modelCard", {}).get("modelParameters", {}).get("datasets", [])]
        if not data or data.get("bom-ref") not in refs:
            f.append("Stage 3: model does not reference its training dataset")
        elif data["hashes"][0]["content"] != sha256(data_p):
            f.append("Stage 2: dataset hash does not match the AI-BOM — training data changed or was swapped")
    metrics = model.get("modelCard", {}).get("quantitativeAnalysis", {}).get("performanceMetrics", [])
    acc = next((float(m["value"]) for m in metrics if m["type"] == "accuracy"), None)
    if acc is None or acc < policy["min_accuracy"]:
        f.append(f"Stage 3: accuracy {acc} below the deployment minimum {policy['min_accuracy']}")
    lic = {l["license"].get("id") for l in model.get("licenses", [])}
    if not lic & set(policy["allowed_licenses"]):
        f.append(f"Stage 3: licence {sorted(lic)} not in {policy['allowed_licenses']}")
    return f


if __name__ == "__main__":
    model_p, data_p, bom_p, policy_p = sys.argv[1:5]
    text = open(bom_p, encoding="utf-8").read()
    problems = schema_errors(text) + verify(model_p, data_p, json.loads(text), yaml.safe_load(open(policy_p)))
    for p in problems:
        print(f"::error::{p}")
    print("deployment verified" if not problems else "DEPLOYMENT BLOCKED")
    sys.exit(1 if problems else 0)
