#!/usr/bin/env bash
# Defending Tomorrow — Chapter 6: Identity Is the New Control Plane
# AWS and Azure in Practice exercise (§6.9). Run the AWS block in AWS CloudShell and the
# Azure block in Azure Cloud Shell (Bash). Do not run this file as one script: copy each block
# into the shell for its platform, read the output, then run the cleanup lines.
# Prerequisite: ~/dt-env.sh from exercises/ch00.sh. Costs and cleanup are described in the book.

# --- AWS: run in AWS CloudShell (or a terminal with AWS CLI v2) ---
source ~/dt-env.sh
aws iam generate-credential-report
sleep 10
aws iam get-credential-report --query Content --output text | base64 --decode \
  | cut -d, -f1,8,9,11 | column -t -s,
# columns: user, mfa_active, access_key_1_active, access_key_1_last_used_date

# --- Azure: run in Azure Cloud Shell, Bash (or a terminal with Azure CLI) ---
source ~/dt-env.sh
az identity create --name id-dt-ch06 --resource-group "$DT_RG"
PRINCIPAL=$(az identity show --name id-dt-ch06 --resource-group "$DT_RG" --query principalId --output tsv)
az role assignment create --assignee-object-id "$PRINCIPAL" --assignee-principal-type ServicePrincipal \
  --role Reader --scope "$(az group show --name "$DT_RG" --query id --output tsv)"
az role assignment list --assignee "$PRINCIPAL" --all --output table
