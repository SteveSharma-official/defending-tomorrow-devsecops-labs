#!/usr/bin/env bash
# Defending Tomorrow — Chapter 23: Detection Engineering
# AWS and Azure in Practice exercise (§23.11). Run the AWS block in AWS CloudShell and the
# Azure block in Azure Cloud Shell (Bash). Do not run this file as one script: copy each block
# into the shell for its platform, read the output, then run the cleanup lines.
# Prerequisite: ~/dt-env.sh from exercises/ch00.sh. Costs and cleanup are described in the book.

# --- AWS: run in AWS CloudShell (or a terminal with AWS CLI v2) ---
source ~/dt-env.sh
DET=$(aws guardduty create-detector --enable --query DetectorId --output text)
aws guardduty create-sample-findings --detector-id "$DET"
sleep 30
IDS=$(aws guardduty list-findings --detector-id "$DET" --max-results 5 --query FindingIds --output text)
aws guardduty get-findings --detector-id "$DET" --finding-ids $IDS \
  --query "Findings[].{type:Type,severity:Severity,resource:Resource.ResourceType}" --output table
aws guardduty delete-detector --detector-id "$DET"   # cleanup: ends the free trial for this Region

# --- Azure: run in Azure Cloud Shell, Bash (or a terminal with Azure CLI) ---
source ~/dt-env.sh
az extension add --name log-analytics --only-show-errors
CUSTOMER_ID=$(az monitor log-analytics workspace show --resource-group "$DT_RG" \
  --workspace-name law-dt-labs --query customerId --output tsv)
az monitor log-analytics query --workspace "$CUSTOMER_ID" --analytics-query '
AzureActivity
| where TimeGenerated > ago(7d)
| where OperationNameValue =~ "Microsoft.Authorization/roleAssignments/write"
| where hourofday(TimeGenerated) !between (8 .. 18)
| project TimeGenerated, Caller, CallerIpAddress, ResourceGroup' --output table
