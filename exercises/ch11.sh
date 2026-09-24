#!/usr/bin/env bash
# Defending Tomorrow — Chapter 11: Secure CI/CD Architectures
# AWS and Azure in Practice exercise (§11.9). Run the AWS block in AWS CloudShell and the
# Azure block in Azure Cloud Shell (Bash). Do not run this file as one script: copy each block
# into the shell for its platform, read the output, then run the cleanup lines.
# Prerequisite: ~/dt-env.sh from exercises/ch00.sh. Costs and cleanup are described in the book.

# --- AWS: run in AWS CloudShell (or a terminal with AWS CLI v2) ---
source ~/dt-env.sh
for u in $(aws iam list-users --query "Users[].UserName" --output text); do
  aws iam list-access-keys --user-name "$u" \
    --query "AccessKeyMetadata[?Status=='Active'].[UserName,AccessKeyId,CreateDate]" --output text
done

# --- Azure: run in Azure Cloud Shell, Bash (or a terminal with Azure CLI) ---
source ~/dt-env.sh
az ad app list --show-mine \
  --query "[?length(passwordCredentials) > \`0\`].{app:displayName,secrets:length(passwordCredentials),federated:length(keyCredentials)}" \
  --output table
