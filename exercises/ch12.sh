#!/usr/bin/env bash
# Defending Tomorrow — Chapter 12: Infrastructure as Code Security
# AWS and Azure in Practice exercise (§12.9). Run the AWS block in AWS CloudShell and the
# Azure block in Azure Cloud Shell (Bash). Do not run this file as one script: copy each block
# into the shell for its platform, read the output, then run the cleanup lines.
# Prerequisite: ~/dt-env.sh from exercises/ch00.sh. Costs and cleanup are described in the book.

# --- AWS: run in AWS CloudShell (or a terminal with AWS CLI v2) ---
source ~/dt-env.sh
STATE="dt-tfstate-$DT_ACCOUNT"
aws s3 mb "s3://$STATE"
aws s3api put-bucket-versioning --bucket "$STATE" --versioning-configuration Status=Enabled
aws s3api put-public-access-block --bucket "$STATE" --public-access-block-configuration \
  BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true
# backend "s3" { bucket = "dt-tfstate-<account>"  key = "ch12/terraform.tfstate"
#                region = "<region>"  encrypt = true  use_lockfile = true }

# --- Azure: run in Azure Cloud Shell, Bash (or a terminal with Azure CLI) ---
source ~/dt-env.sh
SA="sttfdt$RANDOM"
az storage account create --name "$SA" --resource-group "$DT_RG" --location "$DT_LOCATION" \
  --sku Standard_LRS --min-tls-version TLS1_2 --allow-blob-public-access false --allow-shared-key-access false
az storage account blob-service-properties update --account-name "$SA" --resource-group "$DT_RG" \
  --enable-versioning true --enable-delete-retention true --delete-retention-days 7
az role assignment create --assignee "$(az ad signed-in-user show --query id --output tsv)" \
  --role "Storage Blob Data Contributor" --scope "$(az storage account show --name "$SA" --query id --output tsv)"
sleep 60
az storage container create --name tfstate --account-name "$SA" --auth-mode login
# backend "azurerm" { storage_account_name = "<name>"  container_name = "tfstate"
#                     key = "ch12.tfstate"  use_azuread_auth = true }
