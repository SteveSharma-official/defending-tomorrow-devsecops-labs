#!/usr/bin/env bash
# Defending Tomorrow — Chapter 18: Compliance as Code
# AWS and Azure in Practice exercise (§18.9). Run the AWS block in AWS CloudShell and the
# Azure block in Azure Cloud Shell (Bash). Do not run this file as one script: copy each block
# into the shell for its platform, read the output, then run the cleanup lines.
# Prerequisite: ~/dt-env.sh from exercises/ch00.sh. Costs and cleanup are described in the book.

# --- AWS: run in AWS CloudShell (or a terminal with AWS CLI v2) ---
source ~/dt-env.sh
aws artifact list-reports --query "reports[?contains(name,'SOC')].{name:name,version:version}" --output table

# --- Azure: run in Azure Cloud Shell, Bash (or a terminal with Azure CLI) ---
source ~/dt-env.sh
az policy set-definition list \
  --query "[?policyType=='BuiltIn' && (contains(displayName,'ISM') || contains(displayName,'NIST SP 800-53') || contains(displayName,'ISO 27001'))].displayName" \
  --output tsv
az extension add --name resource-graph --only-show-errors
az graph query -q "policyresources
  | where type == 'microsoft.policyinsights/policystates'
  | summarize resources = count() by complianceState = tostring(properties.complianceState)"
