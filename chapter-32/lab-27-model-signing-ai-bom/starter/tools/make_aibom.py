#!/usr/bin/env python3
"""LAB-27 — generate a CycloneDX 1.6 AI-BOM (ML-BOM) binding the model to its dataset and evaluation (§32.4).

Usage: python tools/make_aibom.py artifacts/model.json data/phishing-urls.csv artifacts/evaluation.json artifacts/ai-bom.cdx.json
"""
import datetime
import hashlib
import json
import os
import sys
import uuid


def sha256(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def build(model_p: str, data_p: str, eval_p: str) -> dict:
    model_hash, data_hash = sha256(model_p), sha256(data_p)
    evaluation = json.load(open(eval_p, encoding="utf-8"))
    epoch = int(os.environ.get("SOURCE_DATE_EPOCH", "0")) or None
    when = datetime.datetime.fromtimestamp(epoch, datetime.timezone.utc) if epoch else datetime.datetime.now(datetime.timezone.utc)
    return {
        "bomFormat": "CycloneDX",
        "specVersion": "1.6",
        "serialNumber": f"urn:uuid:{uuid.uuid5(uuid.NAMESPACE_URL, 'dt-lab-27/' + model_hash)}",
        "version": 1,
        "metadata": {
            "timestamp": when.isoformat(timespec="seconds").replace("+00:00", "Z"),
            "component": {"type": "application", "bom-ref": "app:dt-phishing-filter", "name": "dt-phishing-filter"},
        },
        "components": [
            {
                "type": "machine-learning-model",
                "bom-ref": "model:phishing-url-classifier",
                "name": "phishing-url-classifier",
                "version": "1.0.0",
                "hashes": [{"alg": "SHA-256", "content": model_hash}],
                "licenses": [{"license": {"id": "MIT"}}],
                "modelCard": {
                    "modelParameters": {
                        "task": "classification",
                        "architectureFamily": "nearest-centroid",
                        "datasets": [{"ref": "data:phishing-urls"}],
                    },
                    "quantitativeAnalysis": {
                        "performanceMetrics": [{"type": "accuracy", "value": str(evaluation["accuracy"]),
                                                "slice": f"held-out {evaluation['test_rows']} rows"}]
                    },
                },
            },
            {
                "type": "data",
                "bom-ref": "data:phishing-urls",
                "name": "phishing-urls",
                "hashes": [{"alg": "SHA-256", "content": data_hash}],
                "data": [{"type": "dataset", "name": "phishing-urls", "classification": "synthetic, public"}],
            },
        ],
        "dependencies": [{"ref": "model:phishing-url-classifier", "dependsOn": ["data:phishing-urls"]}],
    }


if __name__ == "__main__":
    bom = build(*sys.argv[1:4])
    with open(sys.argv[4], "w", encoding="utf-8") as f:
        json.dump(bom, f, indent=2)
    print(f"AI-BOM written: model {bom['components'][0]['hashes'][0]['content'][:12]}…, dataset {bom['components'][1]['hashes'][0]['content'][:12]}…")
