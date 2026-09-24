#!/usr/bin/env bash
# Defending Tomorrow — Chapter 21: SOAR and Automated Remediation
# AWS and Azure in Practice exercise (§21.10). Run the AWS block in AWS CloudShell and the
# Azure block in Azure Cloud Shell (Bash). Do not run this file as one script: copy each block
# into the shell for its platform, read the output, then run the cleanup lines.
# Prerequisite: ~/dt-env.sh from exercises/ch00.sh. Costs and cleanup are described in the book.

# --- AWS: run in AWS CloudShell (or a terminal with AWS CLI v2) ---
source ~/dt-env.sh
BUCKET="dt-ch21-$DT_ACCOUNT"
aws s3 mb "s3://$BUCKET"
EXEC=$(aws ssm start-automation-execution --document-name AWS-DisableS3BucketPublicReadWrite \
  --parameters "S3BucketName=$BUCKET" --query AutomationExecutionId --output text)
sleep 30
aws ssm get-automation-execution --automation-execution-id "$EXEC" \
  --query "AutomationExecution.{status:AutomationExecutionStatus,steps:StepExecutions[].StepName}"
aws s3api get-public-access-block --bucket "$BUCKET"
aws s3 rb "s3://$BUCKET" --force   # cleanup

# --- Azure: run in Azure Cloud Shell, Bash (or a terminal with Azure CLI) ---
source ~/dt-env.sh
az monitor action-group create --resource-group "$DT_RG" --name ag-dt-ch21 --short-name dtch21 \
  --action email secops you@example.com
az monitor activity-log alert create --resource-group "$DT_RG" --name al-dt-ch21-role-assignment \
  --scope "/subscriptions/$DT_SUB" \
  --condition "category=Administrative and operationName=Microsoft.Authorization/roleAssignments/write" \
  --action-group ag-dt-ch21
# Trigger it: create any role assignment (for example, rerun the Chapter 6 exercise) and check your email.
