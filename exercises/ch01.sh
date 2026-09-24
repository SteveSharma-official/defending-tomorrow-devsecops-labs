#!/usr/bin/env bash
# Defending Tomorrow — Chapter 1: Why Cybersecurity Is Still Losing
# AWS and Azure in Practice exercise (§1.10). Run the AWS block in AWS CloudShell and the
# Azure block in Azure Cloud Shell (Bash). Do not run this file as one script: copy each block
# into the shell for its platform, read the output, then run the cleanup lines.
# Prerequisite: ~/dt-env.sh from exercises/ch00.sh. Costs and cleanup are described in the book.

# --- AWS: run in AWS CloudShell (or a terminal with AWS CLI v2) ---
source ~/dt-env.sh
aws accessanalyzer create-analyzer --analyzer-name dt-ch01-external --type ACCOUNT
sleep 60   # the first analysis takes about a minute
ANALYZER=$(aws accessanalyzer list-analyzers \
  --query "analyzers[?name=='dt-ch01-external'].arn" --output text)
aws accessanalyzer list-findings-v2 --analyzer-arn "$ANALYZER" \
  --query "findings[].{resource:resource,type:resourceType,status:status}" --output table
aws accessanalyzer delete-analyzer --analyzer-name dt-ch01-external   # cleanup

# --- Azure: run in Azure Cloud Shell, Bash (or a terminal with Azure CLI) ---
source ~/dt-env.sh
az role assignment list --all \
  --query "[].{principal:principalName,type:principalType,role:roleDefinitionName,scope:scope}" \
  --output table
