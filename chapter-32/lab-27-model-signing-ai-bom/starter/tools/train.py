#!/usr/bin/env python3
"""LAB-27 — train a tiny, deterministic phishing-URL classifier (nearest centroid) and evaluate it.

Usage: python tools/train.py data/phishing-urls.csv artifacts/
Writes artifacts/model.json (the model artefact to be signed) and artifacts/evaluation.json.
"""
import csv
import json
import pathlib
import sys

FEATURES = ["url_length", "num_digits", "has_at_sign", "subdomain_depth"]


def load(path):
    with open(path, encoding="utf-8") as f:
        return [{k: float(v) for k, v in r.items()} for r in csv.DictReader(f)]


def train(rows):
    split = int(len(rows) * 0.8)
    tr, te = rows[:split], rows[split:]
    scale = {f: max(r[f] for r in tr) or 1.0 for f in FEATURES}
    cent = {}
    for label in (0.0, 1.0):
        sub = [r for r in tr if r["label"] == label]
        cent[str(int(label))] = {f: round(sum(r[f] for r in sub) / len(sub) / scale[f], 6) for f in FEATURES}
    model = {"type": "nearest-centroid", "features": FEATURES, "scale": scale, "centroids": cent,
             "labels": {"0": "benign", "1": "phishing"}}
    correct = sum(predict(model, r) == int(r["label"]) for r in te)
    return model, {"test_rows": len(te), "accuracy": round(correct / len(te), 4)}


def predict(model, row):
    def dist(c):
        return sum((row[f] / model["scale"][f] - c[f]) ** 2 for f in model["features"])
    return min((dist(c), int(k)) for k, c in model["centroids"].items())[1]


if __name__ == "__main__":
    out = pathlib.Path(sys.argv[2])
    out.mkdir(parents=True, exist_ok=True)
    model, evaluation = train(load(sys.argv[1]))
    (out / "model.json").write_text(json.dumps(model, indent=2, sort_keys=True), encoding="utf-8")
    (out / "evaluation.json").write_text(json.dumps(evaluation, indent=2), encoding="utf-8")
    print(json.dumps(evaluation))
