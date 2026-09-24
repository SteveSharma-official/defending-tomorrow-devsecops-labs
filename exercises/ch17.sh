#!/usr/bin/env bash
# Defending Tomorrow — Chapter 17: Policy as Code
# AWS and Azure in Practice exercise (§17.10). Run the AWS block in AWS CloudShell and the
# Azure block in Azure Cloud Shell (Bash). Do not run this file as one script: copy each block
# into the shell for its platform, read the output, then run the cleanup lines.
# Prerequisite: ~/dt-env.sh from exercises/ch00.sh. Costs and cleanup are described in the book.

# --- Azure: run in Azure Cloud Shell, Bash (or a terminal with Azure CLI) ---
source ~/dt-env.sh
RGID=$(az group show --name "$DT_RG" --query id --output tsv)
DEF=$(az policy definition list \
  --query "[?displayName=='Storage accounts should prevent shared key access'].name" --output tsv)
az policy assignment create --name dt-ch17-no-shared-key --scope "$RGID" --policy "$DEF" \
  --params '{"effect":{"value":"Deny"}}'
sleep 300   # new assignments can take several minutes to take effect
az storage account create --name "stdtch17$RANDOM" --resource-group "$DT_RG" --sku Standard_LRS
#   expected: RequestDisallowedByPolicy
az policy exemption create --name dt-ch17-waiver --scope "$RGID" \
  --policy-assignment "$RGID/providers/Microsoft.Authorization/policyAssignments/dt-ch17-no-shared-key" \
  --exemption-category Waiver --expires-on "$(date -u -d '+7 days' +%Y-%m-%dT%H:%M:%SZ)" \
  --description "Chapter 17 exercise: expires in 7 days"
# cleanup
az policy exemption delete --name dt-ch17-waiver --scope "$RGID"
az policy assignment delete --name dt-ch17-no-shared-key --scope "$RGID"

# --- AWS: run in AWS CloudShell (or a terminal with AWS CLI v2) ---
source ~/dt-env.sh
aws accessanalyzer validate-policy --policy-type IDENTITY_POLICY --policy-document \
  '{"Version":"2012-10-17","Statement":[{"Effect":"Allow","Action":"s3:*","NotResource":"arn:aws:s3:::audit-*"}]}' \
  --query "findings[].{type:findingType,issue:issueCode}" --output table
