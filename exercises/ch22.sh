#!/usr/bin/env bash
# Defending Tomorrow — Chapter 22: Observability for Security
# AWS and Azure in Practice exercise (§22.10). Run the AWS block in AWS CloudShell and the
# Azure block in Azure Cloud Shell (Bash). Do not run this file as one script: copy each block
# into the shell for its platform, read the output, then run the cleanup lines.
# Prerequisite: ~/dt-env.sh from exercises/ch00.sh. Costs and cleanup are described in the book.

# --- AWS: run in AWS CloudShell (or a terminal with AWS CLI v2) ---
source ~/dt-env.sh
TRAIL_BUCKET="dt-ch22-trail-$DT_ACCOUNT"
aws s3 mb "s3://$TRAIL_BUCKET"
aws s3api put-bucket-policy --bucket "$TRAIL_BUCKET" --policy '{"Version":"2012-10-17","Statement":[
 {"Sid":"AclCheck","Effect":"Allow","Principal":{"Service":"cloudtrail.amazonaws.com"},"Action":"s3:GetBucketAcl","Resource":"arn:aws:s3:::'"$TRAIL_BUCKET"'"},
 {"Sid":"Write","Effect":"Allow","Principal":{"Service":"cloudtrail.amazonaws.com"},"Action":"s3:PutObject","Resource":"arn:aws:s3:::'"$TRAIL_BUCKET"'/AWSLogs/'"$DT_ACCOUNT"'/*","Condition":{"StringEquals":{"s3:x-amz-acl":"bucket-owner-full-control"}}}]}'
aws cloudtrail create-trail --name dt-ch22 --s3-bucket-name "$TRAIL_BUCKET" \
  --is-multi-region-trail --enable-log-file-validation
aws cloudtrail start-logging --name dt-ch22
aws cloudtrail get-trail-status --name dt-ch22 --query "{logging:IsLogging,latestDelivery:LatestDeliveryTime}"

# --- Azure: run in Azure Cloud Shell, Bash (or a terminal with Azure CLI) ---
source ~/dt-env.sh
az monitor log-analytics workspace create --resource-group "$DT_RG" --workspace-name law-dt-labs \
  --location "$DT_LOCATION" --retention-time 30
WS=$(az monitor log-analytics workspace show --resource-group "$DT_RG" --workspace-name law-dt-labs --query id --output tsv)
az monitor diagnostic-settings subscription create --name dt-ch22 --location "$DT_LOCATION" \
  --workspace "$WS" \
  --logs '[{"category":"Administrative","enabled":true},{"category":"Security","enabled":true},{"category":"Policy","enabled":true}]'
