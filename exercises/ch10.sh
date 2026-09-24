#!/usr/bin/env bash
# Defending Tomorrow — Chapter 10: Git Security Engineering
# AWS and Azure in Practice exercise (§10.9). Run the AWS block in AWS CloudShell and the
# Azure block in Azure Cloud Shell (Bash). Do not run this file as one script: copy each block
# into the shell for its platform, read the output, then run the cleanup lines.
# Prerequisite: ~/dt-env.sh from exercises/ch00.sh. Costs and cleanup are described in the book.

# --- AWS: run in AWS CloudShell (or a terminal with AWS CLI v2) ---
source ~/dt-env.sh
aws secretsmanager create-secret --name dt/ch10/db-password \
  --secret-string "$(aws secretsmanager get-random-password --password-length 32 --query RandomPassword --output text)" \
  --tags Key=project,Value=defending-tomorrow
aws secretsmanager describe-secret --secret-id dt/ch10/db-password \
  --query "{name:Name,rotation:RotationEnabled,created:CreatedDate}"
aws secretsmanager delete-secret --secret-id dt/ch10/db-password --force-delete-without-recovery   # cleanup

# --- Azure: run in Azure Cloud Shell, Bash (or a terminal with Azure CLI) ---
source ~/dt-env.sh
KV="kv-dt-ch10-$RANDOM"
az keyvault create --name "$KV" --resource-group "$DT_RG" --location "$DT_LOCATION" \
  --enable-rbac-authorization true --retention-days 7
az role assignment create --assignee "$(az ad signed-in-user show --query id --output tsv)" \
  --role "Key Vault Secrets Officer" --scope "$(az keyvault show --name "$KV" --query id --output tsv)"
sleep 60
az keyvault secret set --vault-name "$KV" --name db-password --value "$(openssl rand -base64 24)" \
  --query "{id:id,enabled:attributes.enabled}"
az keyvault secret show --vault-name "$KV" --name db-password --query "attributes.created"
