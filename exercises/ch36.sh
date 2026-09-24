#!/usr/bin/env bash
# Defending Tomorrow — Chapter 36: Defending Tomorrow
# AWS and Azure in Practice exercise (§36.8). Run the AWS block in AWS CloudShell and the
# Azure block in Azure Cloud Shell (Bash). Do not run this file as one script: copy each block
# into the shell for its platform, read the output, then run the cleanup lines.
# Prerequisite: ~/dt-env.sh from exercises/ch00.sh. Costs and cleanup are described in the book.

# --- AWS: run in AWS CloudShell (or a terminal with AWS CLI v2) ---
source ~/dt-env.sh
echo "S3 Block Public Access:";  aws s3control get-public-access-block --account-id "$DT_ACCOUNT" \
  --query "PublicAccessBlockConfiguration" --output text 2>/dev/null || echo "  not set"
echo "EBS default encryption:";  aws ec2 get-ebs-encryption-by-default --query EbsEncryptionByDefault
echo "CloudTrail trails:";       aws cloudtrail describe-trails --query "trailList[].Name" --output text
echo "GuardDuty detectors:";     aws guardduty list-detectors --query DetectorIds --output text
echo "IAM users with keys:";     aws iam list-users --query "length(Users)"
# teardown: delete remaining lab trails, buckets, detectors and budgets you created

# --- Azure: run in Azure Cloud Shell, Bash (or a terminal with Azure CLI) ---
source ~/dt-env.sh
echo "Policy assignments:";     az policy assignment list --query "length(@)"
echo "Secure score:";           az security secure-scores list --query "[0].score.percentage"
echo "Diagnostic settings:";    az monitor diagnostic-settings subscription list --query "value[].name" --output tsv
# teardown: remove the subscription diagnostic setting and every lab resource group
az monitor diagnostic-settings subscription delete --name dt-ch22 --yes
az group delete --name "$DT_RG" --yes --no-wait
