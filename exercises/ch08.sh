#!/usr/bin/env bash
# Defending Tomorrow — Chapter 8: Data-Centric Security
# AWS and Azure in Practice exercise (§8.11). Run the AWS block in AWS CloudShell and the
# Azure block in Azure Cloud Shell (Bash). Do not run this file as one script: copy each block
# into the shell for its platform, read the output, then run the cleanup lines.
# Prerequisite: ~/dt-env.sh from exercises/ch00.sh. Costs and cleanup are described in the book.

# --- AWS: run in AWS CloudShell (or a terminal with AWS CLI v2) ---
source ~/dt-env.sh
KEY=$(aws kms create-key --description dt-ch08 --tags TagKey=project,TagValue=defending-tomorrow \
  --query KeyMetadata.KeyId --output text)
aws kms enable-key-rotation --key-id "$KEY"
BUCKET="dt-ch08-$DT_ACCOUNT"
aws s3 mb "s3://$BUCKET"
aws s3api put-bucket-encryption --bucket "$BUCKET" --server-side-encryption-configuration \
  '{"Rules":[{"ApplyServerSideEncryptionByDefault":{"SSEAlgorithm":"aws:kms","KMSMasterKeyID":"'"$KEY"'"},"BucketKeyEnabled":true}]}'
aws s3api get-bucket-encryption --bucket "$BUCKET"
# cleanup
aws s3 rb "s3://$BUCKET" --force
aws kms schedule-key-deletion --key-id "$KEY" --pending-window-in-days 7

# --- Azure: run in Azure Cloud Shell, Bash (or a terminal with Azure CLI) ---
source ~/dt-env.sh
KV="kv-dt-ch08-$RANDOM"
az keyvault create --name "$KV" --resource-group "$DT_RG" --location "$DT_LOCATION" \
  --enable-rbac-authorization true --enable-purge-protection true --retention-days 7
az role assignment create --assignee "$(az ad signed-in-user show --query id --output tsv)" \
  --role "Key Vault Crypto Officer" --scope "$(az keyvault show --name "$KV" --query id --output tsv)"
sleep 60   # role assignments take a minute to apply
az keyvault key create --vault-name "$KV" --name dt-ch08 --kty RSA --size 3072
az keyvault key rotation-policy update --vault-name "$KV" --name dt-ch08 --value \
  '{"lifetimeActions":[{"trigger":{"timeAfterCreate":"P90D"},"action":{"type":"Rotate"}}],"attributes":{"expiryTime":"P1Y"}}'
az keyvault key rotation-policy show --vault-name "$KV" --name dt-ch08
