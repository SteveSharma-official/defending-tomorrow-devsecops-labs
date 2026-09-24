#!/usr/bin/env bash
# Defending Tomorrow — Chapter 16: AI-Assisted Software Development
# AWS and Azure in Practice exercise (§16.7). Run the AWS block in AWS CloudShell and the
# Azure block in Azure Cloud Shell (Bash). Do not run this file as one script: copy each block
# into the shell for its platform, read the output, then run the cleanup lines.
# Prerequisite: ~/dt-env.sh from exercises/ch00.sh. Costs and cleanup are described in the book.

# --- AWS: run in AWS CloudShell (or a terminal with AWS CLI v2) ---
source ~/dt-env.sh
aws bedrock get-model-invocation-logging-configuration
aws bedrock list-guardrails --query "guardrails[].{name:name,status:status,version:version}" --output table

# --- Azure: run in Azure Cloud Shell, Bash (or a terminal with Azure CLI) ---
source ~/dt-env.sh
az cognitiveservices account list \
  --query "[].{name:name,kind:kind,publicNetwork:properties.publicNetworkAccess,keysDisabled:properties.disableLocalAuth}" \
  --output table
