#!/usr/bin/env bash
# Creates the four custom policy definitions at subscription scope and assigns them to ONE resource group.
# Usage: bash scripts/deploy-policies.sh <resource-group> [Audit|Deny]
set -euo pipefail
RG="$1"; EFFECT="${2:-Deny}"
SCOPE=$(az group show -n "$RG" --query id -o tsv)
for f in policies/*.json; do
  name="dt-$(basename "$f" .json)"
  az policy definition create --name "$name" \
    --display-name "$(jq -r .properties.displayName "$f")" \
    --description "$(jq -r .properties.description "$f")" \
    --mode "$(jq -r .properties.mode "$f")" \
    --params "$(jq -c .properties.parameters "$f")" \
    --rules "$(jq -c .properties.policyRule "$f")" --output none
  az policy assignment create --name "${name:0:64}" --scope "$SCOPE" --policy "$name" \
    --params "{\"effect\":{\"value\":\"${EFFECT}\"}}" --output none
  echo "assigned ${name} (${EFFECT}) to ${RG}"
done
