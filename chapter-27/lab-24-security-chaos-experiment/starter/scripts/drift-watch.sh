#!/usr/bin/env bash
# drift-watch.sh — detection + response for EXP-001. Polls the namespace's PSA label; on drift it records
# detected_at, re-applies the desired state and records responded_at. Writes timestamps to results/run.env.
set -euo pipefail
ns="lab24-orders"; out="results/run.env"; interval="${INTERVAL:-5}"; deadline=$(( $(date +%s) + 900 ))
while (( $(date +%s) < deadline )); do
  level=$(kubectl get namespace "${ns}" -o jsonpath='{.metadata.labels.pod-security\.kubernetes\.io/enforce}')
  if [[ "${level}" != "restricted" ]]; then
    echo "detected_at=$(date -u +%FT%TZ)" >> "${out}"
    echo "::warning::control drift: ${ns} enforce='${level:-<none>}' (desired: restricted)"
    kubectl label namespace "${ns}" pod-security.kubernetes.io/enforce=restricted --overwrite
    echo "responded_at=$(date -u +%FT%TZ)" >> "${out}"
    exit 0
  fi
  sleep "${interval}"
done
echo "::error::no drift observed before the deadline"
exit 1
