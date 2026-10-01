#!/usr/bin/env bash
# contain-pod.sh — evidence-first containment of one pod, following PB-POD-CONTAIN-001 (Chapter 25).
# Usage: bash scripts/contain-pod.sh <namespace> <pod> <case-id>
# Requires kubectl pointed at a cluster you own (the lab uses kind). Steps that are irreversible stop for
# a human decision unless CONFIRM_DESTRUCTIVE=yes is set (the CI exercise sets it).
set -euo pipefail
ns="$1"; pod="$2"; case_id="$3"
out="evidence/${case_id}"
mkdir -p "${out}"

echo "== 1-3 preserve: spec, events, logs, filesystem (nothing has been changed yet)"
kubectl -n "${ns}" get pod "${pod}" -o yaml > "${out}/pod.yaml"
kubectl -n "${ns}" get events --field-selector "involvedObject.name=${pod}" -o wide > "${out}/events.txt"
kubectl -n "${ns}" logs "${pod}" --all-containers --timestamps > "${out}/logs.txt"
kubectl -n "${ns}" logs "${pod}" --all-containers --previous > "${out}/logs-previous.txt" 2>/dev/null || true
kubectl -n "${ns}" exec "${pod}" -- tar cf - /tmp 2>/dev/null > "${out}/filesystem-tmp.tar"
kubectl -n "${ns}" exec "${pod}" -- ls -la /tmp > "${out}/filesystem-listing.txt"

echo "== 4 hash evidence"
python3 tools/evidence_manifest.py create "${out}" --case "${case_id}" --collector "${USER:-ci}"

echo "== 5 isolate (reversible: remove the label to undo)"
kubectl apply -f k8s/quarantine-networkpolicy.yaml
kubectl -n "${ns}" label pod "${pod}" quarantine=true --overwrite

if [[ "${CONFIRM_DESTRUCTIVE:-no}" != "yes" ]]; then
  echo "Stopping before irreversible steps. Review the evidence, then re-run with CONFIRM_DESTRUCTIVE=yes."
  exit 0
fi
echo "== 7 destroy (irreversible, human-approved)"
kubectl -n "${ns}" delete pod "${pod}" --wait=true

echo "== evidence still verifies after the workload is gone"
python3 tools/evidence_manifest.py verify "${out}"
