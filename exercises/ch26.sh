#!/usr/bin/env bash
# Defending Tomorrow — Chapter 26: Cyber Resilience Engineering
# AWS and Azure in Practice exercise (§26.8). Run the AWS block in AWS CloudShell and the
# Azure block in Azure Cloud Shell (Bash). Do not run this file as one script: copy each block
# into the shell for its platform, read the output, then run the cleanup lines.
# Prerequisite: ~/dt-env.sh from exercises/ch00.sh. Costs and cleanup are described in the book.

# --- AWS: run in AWS CloudShell (or a terminal with AWS CLI v2) ---
source ~/dt-env.sh
aws backup create-backup-vault --backup-vault-name dt-ch26
aws backup put-backup-vault-lock-configuration --backup-vault-name dt-ch26 \
  --min-retention-days 7 --max-retention-days 35      # no --changeable-for-days: governance mode
aws backup describe-backup-vault --backup-vault-name dt-ch26 \
  --query "{locked:Locked,minDays:MinRetentionDays,maxDays:MaxRetentionDays}"
# cleanup
aws backup delete-backup-vault-lock-configuration --backup-vault-name dt-ch26
aws backup delete-backup-vault --backup-vault-name dt-ch26

# --- Azure: run in Azure Cloud Shell, Bash (or a terminal with Azure CLI) ---
source ~/dt-env.sh
az backup vault create --resource-group "$DT_RG" --name rsv-dt-ch26 --location "$DT_LOCATION"
az backup vault update --resource-group "$DT_RG" --name rsv-dt-ch26 --immutability-state Unlocked
az backup vault show --resource-group "$DT_RG" --name rsv-dt-ch26 \
  --query "properties.securitySettings"
