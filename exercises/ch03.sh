#!/usr/bin/env bash
# Defending Tomorrow — Chapter 3: Security Engineering Principles
# AWS and Azure in Practice exercise (§3.11). Run the AWS block in AWS CloudShell and the
# Azure block in Azure Cloud Shell (Bash). Do not run this file as one script: copy each block
# into the shell for its platform, read the output, then run the cleanup lines.
# Prerequisite: ~/dt-env.sh from exercises/ch00.sh. Costs and cleanup are described in the book.

# --- AWS: run in AWS CloudShell (or a terminal with AWS CLI v2) ---
source ~/dt-env.sh
aws s3control get-public-access-block --account-id "$DT_ACCOUNT"
# If the call above returns NoSuchPublicAccessBlockConfiguration, turn it on:
aws s3control put-public-access-block --account-id "$DT_ACCOUNT" \
  --public-access-block-configuration \
  BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true
aws ec2 get-ebs-encryption-by-default
aws ec2 enable-ebs-encryption-by-default   # per Region; free

# --- Azure: run in Azure Cloud Shell, Bash (or a terminal with Azure CLI) ---
source ~/dt-env.sh
az storage account create --name "stdtch03$RANDOM" --resource-group "$DT_RG" \
  --location "$DT_LOCATION" --sku Standard_LRS
az storage account list --resource-group "$DT_RG" \
  --query "[].{name:name,anonymousBlob:allowBlobPublicAccess,minTls:minimumTlsVersion,httpsOnly:enableHttpsTrafficOnly,sharedKey:allowSharedKeyAccess}" \
  --output table
