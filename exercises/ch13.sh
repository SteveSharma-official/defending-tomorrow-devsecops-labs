#!/usr/bin/env bash
# Defending Tomorrow — Chapter 13: Software Supply Chain Security
# AWS and Azure in Practice exercise (§13.9). Run the AWS block in AWS CloudShell and the
# Azure block in Azure Cloud Shell (Bash). Do not run this file as one script: copy each block
# into the shell for its platform, read the output, then run the cleanup lines.
# Prerequisite: ~/dt-env.sh from exercises/ch00.sh. Costs and cleanup are described in the book.

# --- AWS: run in AWS CloudShell (or a terminal with AWS CLI v2) ---
source ~/dt-env.sh
aws signer put-signing-profile --profile-name dt_ch13 --platform-id Notation-OCI-SHA384-ECDSA
aws signer list-signing-profiles \
  --query "profiles[].{name:profileName,platform:platformId,status:status}" --output table
aws signer cancel-signing-profile --profile-name dt_ch13   # cleanup

# --- Azure: run in Azure Cloud Shell, Bash (or a terminal with Azure CLI) ---
source ~/dt-env.sh
KV="kv-dt-ch13-$RANDOM"
az keyvault create --name "$KV" --resource-group "$DT_RG" --location "$DT_LOCATION" \
  --enable-rbac-authorization true --retention-days 7
az role assignment create --assignee "$(az ad signed-in-user show --query id --output tsv)" \
  --role "Key Vault Certificates Officer" --scope "$(az keyvault show --name "$KV" --query id --output tsv)"
sleep 60
cat > signing-policy.json <<'JSON'
{"issuerParameters":{"name":"Self"},
 "keyProperties":{"exportable":false,"keyType":"EC","curve":"P-384","reuseKey":true},
 "x509CertificateProperties":{"subject":"CN=dt-ch13-signing,O=Defending Tomorrow Labs",
   "ekus":["1.3.6.1.5.5.7.3.3"],"keyUsage":["digitalSignature"],"validityInMonths":12}}
JSON
az keyvault certificate create --vault-name "$KV" --name dt-ch13-signing --policy @signing-policy.json
az keyvault certificate show --vault-name "$KV" --name dt-ch13-signing --query "policy.x509CertificateProperties"
