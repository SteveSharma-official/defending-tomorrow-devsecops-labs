#!/usr/bin/env bash
# Defending Tomorrow — Chapter 2: The Evolution of Enterprise Technology
# AWS and Azure in Practice exercise (§2.10). Run the AWS block in AWS CloudShell and the
# Azure block in Azure Cloud Shell (Bash). Do not run this file as one script: copy each block
# into the shell for its platform, read the output, then run the cleanup lines.
# Prerequisite: ~/dt-env.sh from exercises/ch00.sh. Costs and cleanup are described in the book.

# --- AWS: run in AWS CloudShell (or a terminal with AWS CLI v2) ---
source ~/dt-env.sh
aws cloudtrail lookup-events --max-results 10 \
  --query "Events[].{time:EventTime,event:EventName,user:Username,source:EventSource}" \
  --output table

# --- Azure: run in Azure Cloud Shell, Bash (or a terminal with Azure CLI) ---
source ~/dt-env.sh
az group create --name rg-dt-ch02 --location "$DT_LOCATION" --tags project=defending-tomorrow
sleep 120   # Activity Log entries arrive within a few minutes
az monitor activity-log list --resource-group rg-dt-ch02 --offset 1h \
  --query "[].{time:eventTimestamp,operation:operationName.localizedValue,caller:caller,status:status.value}" \
  --output table
az group delete --name rg-dt-ch02 --yes --no-wait   # cleanup
