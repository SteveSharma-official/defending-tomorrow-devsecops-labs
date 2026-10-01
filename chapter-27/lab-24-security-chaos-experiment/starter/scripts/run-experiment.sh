#!/usr/bin/env bash
# run-experiment.sh — execute EXP-001 on a disposable kind cluster and write results/run.json.
set -euo pipefail
ns="lab24-orders"
[[ "$(kubectl config current-context)" == kind-* ]] || { echo "Guard rail: refusing to run outside a kind cluster" >&2; exit 2; }
mkdir -p results; : > results/run.env
kubectl apply -f k8s/namespace.yaml
if kubectl apply -f k8s/privileged-probe-pod.yaml --dry-run=server >/dev/null 2>&1; then
  echo "Baseline is wrong: privileged pod admitted before injection" >&2; exit 3
fi
bash scripts/drift-watch.sh & watcher=$!
sleep 2
echo "injection_at=$(date -u +%FT%TZ)" >> results/run.env
kubectl label namespace "${ns}" pod-security.kubernetes.io/enforce-          # the injected failure
wait "${watcher}"
until ! kubectl apply -f k8s/privileged-probe-pod.yaml --dry-run=server >/dev/null 2>&1; do sleep 2; done
echo "recovered_at=$(date -u +%FT%TZ)" >> results/run.env
python3 - <<'PY'
import json
d = dict(line.strip().split("=", 1) for line in open("results/run.env") if "=" in line)
json.dump({"experiment": "EXP-001", **d}, open("results/run.json", "w"), indent=2)
print(json.dumps(d, indent=2))
PY
