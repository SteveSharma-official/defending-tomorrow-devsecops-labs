#!/usr/bin/env bash
# Defending Tomorrow — Chapter 31: Agent Security Engineering
# AWS and Azure in Practice exercise (§31.9). Run the AWS block in AWS CloudShell and the
# Azure block in Azure Cloud Shell (Bash). Do not run this file as one script: copy each block
# into the shell for its platform, read the output, then run the cleanup lines.
# Prerequisite: ~/dt-env.sh from exercises/ch00.sh. Costs and cleanup are described in the book.

# --- AWS: run in AWS CloudShell (or a terminal with AWS CLI v2) ---
source ~/dt-env.sh
PS=$(aws verifiedpermissions create-policy-store --validation-settings mode=OFF \
  --query policyStoreId --output text)
aws verifiedpermissions create-policy --policy-store-id "$PS" --definition \
  '{"static":{"description":"triage agent may read tickets","statement":"permit(principal == Agent::\"triage-bot\", action == Action::\"read_ticket\", resource);"}}'
for TOOL in read_ticket delete_ticket; do
  echo -n "$TOOL: "
  aws verifiedpermissions is-authorized --policy-store-id "$PS" \
    --principal entityType=Agent,entityId=triage-bot \
    --action actionType=Action,actionId=$TOOL \
    --resource entityType=Ticket,entityId=T-1001 --query decision --output text
done
aws verifiedpermissions delete-policy-store --policy-store-id "$PS"   # cleanup

# --- Azure: run in Azure Cloud Shell, Bash (or a terminal with Azure CLI) ---
source ~/dt-env.sh
az identity create --name id-agent-triage --resource-group "$DT_RG" --tags role=agent owner=secops
PID=$(az identity show --name id-agent-triage --resource-group "$DT_RG" --query principalId --output tsv)
az role assignment create --assignee-object-id "$PID" --assignee-principal-type ServicePrincipal \
  --role Reader --scope "$(az group show --name "$DT_RG" --query id --output tsv)"
az role assignment list --assignee "$PID" --all --query "[].{role:roleDefinitionName,scope:scope}" --output table
