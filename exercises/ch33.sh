#!/usr/bin/env bash
# Defending Tomorrow — Chapter 33: Autonomous Remediation
# AWS and Azure in Practice exercise (§33.9). Run the AWS block in AWS CloudShell and the
# Azure block in Azure Cloud Shell (Bash). Do not run this file as one script: copy each block
# into the shell for its platform, read the output, then run the cleanup lines.
# Prerequisite: ~/dt-env.sh from exercises/ch00.sh. Costs and cleanup are described in the book.

# --- AWS: run in AWS CloudShell (or a terminal with AWS CLI v2) ---
source ~/dt-env.sh
BUCKET="dt-ch33-$DT_ACCOUNT"; aws s3 mb "s3://$BUCKET"
cat > dt-approve.yaml <<'YAML'
schemaVersion: '0.3'
description: Stage 3 remediation - a named human approves before the change runs
parameters:
  Approver: {type: String}
  BucketName: {type: String}
mainSteps:
  - name: approve
    action: aws:approve
    inputs:
      Approvers: ['{{ Approver }}']
      MinRequiredApprovals: 1
      Message: 'Block public access on {{ BucketName }}?'
  - name: remediate
    action: aws:executeAwsApi
    inputs:
      Service: s3
      Api: PutPublicAccessBlock
      Bucket: '{{ BucketName }}'
      PublicAccessBlockConfiguration: {BlockPublicAcls: true, IgnorePublicAcls: true, BlockPublicPolicy: true, RestrictPublicBuckets: true}
YAML
aws ssm create-document --name DT-Ch33-ApprovedRemediation --document-type Automation \
  --document-format YAML --content file://dt-approve.yaml
ME=$(aws sts get-caller-identity --query Arn --output text)
EXEC=$(aws ssm start-automation-execution --document-name DT-Ch33-ApprovedRemediation \
  --parameters '{"Approver":["'"$ME"'"],"BucketName":["'"$BUCKET"'"]}' --query AutomationExecutionId --output text)
sleep 20
aws ssm send-automation-signal --automation-execution-id "$EXEC" --signal-type Approve \
  --payload Comment="approved during the chapter 33 exercise"
# cleanup
aws ssm delete-document --name DT-Ch33-ApprovedRemediation; aws s3 rb "s3://$BUCKET" --force

# --- Azure: run in Azure Cloud Shell, Bash (or a terminal with Azure CLI) ---
source ~/dt-env.sh
RGID=$(az group show --name "$DT_RG" --query id --output tsv)
DEF=$(az policy definition list \
  --query "[?displayName=='Inherit a tag from the resource group if missing'].name" --output tsv)
az policy assignment create --name dt-ch33-inherit-tag --scope "$RGID" --policy "$DEF" \
  --params '{"tagName":{"value":"project"}}' --mi-system-assigned --location "$DT_LOCATION" \
  --role "Tag Contributor" --identity-scope "$RGID"
az policy remediation create --name dt-ch33-fix --resource-group "$DT_RG" \
  --policy-assignment dt-ch33-inherit-tag --resource-discovery-mode ReEvaluateCompliance
az policy remediation show --name dt-ch33-fix --resource-group "$DT_RG" \
  --query "{state:provisioningState,summary:deploymentSummary}"
