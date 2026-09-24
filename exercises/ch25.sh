#!/usr/bin/env bash
# Defending Tomorrow — Chapter 25: Incident Response Engineering
# AWS and Azure in Practice exercise (§25.8). Run the AWS block in AWS CloudShell and the
# Azure block in Azure Cloud Shell (Bash). Do not run this file as one script: copy each block
# into the shell for its platform, read the output, then run the cleanup lines.
# Prerequisite: ~/dt-env.sh from exercises/ch00.sh. Costs and cleanup are described in the book.

# --- AWS: run in AWS CloudShell (or a terminal with AWS CLI v2) ---
source ~/dt-env.sh
aws iam create-user --user-name dt-ch25-suspect
KEYID=$(aws iam create-access-key --user-name dt-ch25-suspect --query AccessKey.AccessKeyId --output text)
# containment: disable the key, then deny everything the identity could still do
aws iam update-access-key --user-name dt-ch25-suspect --access-key-id "$KEYID" --status Inactive
aws iam put-user-policy --user-name dt-ch25-suspect --policy-name dt-quarantine \
  --policy-document '{"Version":"2012-10-17","Statement":[{"Effect":"Deny","Action":"*","Resource":"*"}]}'
aws iam list-access-keys --user-name dt-ch25-suspect --output table
# cleanup
aws iam delete-user-policy --user-name dt-ch25-suspect --policy-name dt-quarantine
aws iam delete-access-key --user-name dt-ch25-suspect --access-key-id "$KEYID"
aws iam delete-user --user-name dt-ch25-suspect

# --- Azure: run in Azure Cloud Shell, Bash (or a terminal with Azure CLI) ---
source ~/dt-env.sh
az identity create --name id-dt-ch25 --resource-group "$DT_RG"
PID=$(az identity show --name id-dt-ch25 --resource-group "$DT_RG" --query principalId --output tsv)
RGID=$(az group show --name "$DT_RG" --query id --output tsv)
az role assignment create --assignee-object-id "$PID" --assignee-principal-type ServicePrincipal \
  --role Contributor --scope "$RGID"
# containment: remove every role assignment the identity holds
az role assignment delete --assignee "$PID" --scope "$RGID"
# evidence: export and hash the Activity Log for the incident window
az monitor activity-log list --resource-group "$DT_RG" --offset 2h --output json > evidence-ch25.json
sha256sum evidence-ch25.json | tee evidence-ch25.json.sha256
