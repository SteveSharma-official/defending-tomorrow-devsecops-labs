#!/usr/bin/env bash
# Defending Tomorrow — Chapter 24: Threat Hunting
# AWS and Azure in Practice exercise (§24.9). Run the AWS block in AWS CloudShell and the
# Azure block in Azure Cloud Shell (Bash). Do not run this file as one script: copy each block
# into the shell for its platform, read the output, then run the cleanup lines.
# Prerequisite: ~/dt-env.sh from exercises/ch00.sh. Costs and cleanup are described in the book.

# --- AWS: run in AWS CloudShell (or a terminal with AWS CLI v2) ---
source ~/dt-env.sh
aws cloudtrail lookup-events --lookup-attributes AttributeKey=EventName,AttributeValue=ConsoleLogin \
  --max-results 20 --query "Events[].CloudTrailEvent" --output text \
  | jq -r '[.eventTime, .userIdentity.arn, .sourceIPAddress, .additionalEventData.MFAUsed] | @tsv'

# --- Azure: run in Azure Cloud Shell, Bash (or a terminal with Azure CLI) ---
source ~/dt-env.sh
az extension add --name log-analytics --only-show-errors
CUSTOMER_ID=$(az monitor log-analytics workspace show --resource-group "$DT_RG" \
  --workspace-name law-dt-labs --query customerId --output tsv)
az monitor log-analytics query --workspace "$CUSTOMER_ID" --analytics-query '
AzureActivity
| where TimeGenerated > ago(7d) and CategoryValue == "Administrative"
| summarize operations = count(), first = min(TimeGenerated), last = max(TimeGenerated) by Caller, CallerIpAddress
| order by operations desc' --output table
