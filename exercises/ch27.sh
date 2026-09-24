#!/usr/bin/env bash
# Defending Tomorrow — Chapter 27: Chaos Security Engineering
# AWS and Azure in Practice exercise (§27.8). Run the AWS block in AWS CloudShell and the
# Azure block in Azure Cloud Shell (Bash). Do not run this file as one script: copy each block
# into the shell for its platform, read the output, then run the cleanup lines.
# Prerequisite: ~/dt-env.sh from exercises/ch00.sh. Costs and cleanup are described in the book.

# --- AWS: run in AWS CloudShell (or a terminal with AWS CLI v2) ---
source ~/dt-env.sh
aws fis list-actions \
  --query "actions[?contains(id,'network') || contains(id,'ssm') || contains(id,'iam')].{id:id,description:description}" \
  --output table

# --- Azure: run in Azure Cloud Shell, Bash (or a terminal with Azure CLI) ---
source ~/dt-env.sh
az provider register --namespace Microsoft.Chaos --wait
az rest --method get \
  --url "https://management.azure.com/subscriptions/$DT_SUB/providers/Microsoft.Chaos/locations/$DT_LOCATION/targetTypes?api-version=2023-11-01" \
  --query "value[].{target:name,description:properties.description}" --output table
