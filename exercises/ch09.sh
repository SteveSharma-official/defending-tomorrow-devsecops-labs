#!/usr/bin/env bash
# Defending Tomorrow — Chapter 9: Designing the Enterprise Software Factory
# AWS and Azure in Practice exercise (§9.8). Run the AWS block in AWS CloudShell and the
# Azure block in Azure Cloud Shell (Bash). Do not run this file as one script: copy each block
# into the shell for its platform, read the output, then run the cleanup lines.
# Prerequisite: ~/dt-env.sh from exercises/ch00.sh. Costs and cleanup are described in the book.

# --- AWS: run in AWS CloudShell (or a terminal with AWS CLI v2) ---
source ~/dt-env.sh
aws ecr create-repository --repository-name dt-factory/orders \
  --image-tag-mutability IMMUTABLE --image-scanning-configuration scanOnPush=true \
  --encryption-configuration encryptionType=KMS
aws ecr describe-repositories --repository-names dt-factory/orders \
  --query "repositories[0].{immutable:imageTagMutability,scanOnPush:imageScanningConfiguration.scanOnPush,encryption:encryptionConfiguration.encryptionType}"
aws ecr delete-repository --repository-name dt-factory/orders --force   # cleanup

# --- Azure: run in Azure Cloud Shell, Bash (or a terminal with Azure CLI) ---
source ~/dt-env.sh
ACR="acrdtch09$RANDOM"
az acr create --name "$ACR" --resource-group "$DT_RG" --location "$DT_LOCATION" \
  --sku Basic --admin-enabled false
az acr show --name "$ACR" --query "{admin:adminUserEnabled,anonymousPull:anonymousPullEnabled,sku:sku.name}"
az acr delete --name "$ACR" --yes   # cleanup
