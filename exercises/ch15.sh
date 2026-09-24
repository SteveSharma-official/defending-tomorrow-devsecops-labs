#!/usr/bin/env bash
# Defending Tomorrow — Chapter 15: Platform Engineering
# AWS and Azure in Practice exercise (§15.8). Run the AWS block in AWS CloudShell and the
# Azure block in Azure Cloud Shell (Bash). Do not run this file as one script: copy each block
# into the shell for its platform, read the output, then run the cleanup lines.
# Prerequisite: ~/dt-env.sh from exercises/ch00.sh. Costs and cleanup are described in the book.

# --- AWS: run in AWS CloudShell (or a terminal with AWS CLI v2) ---
source ~/dt-env.sh
aws iam create-policy --policy-name dt-ch15-boundary --policy-document \
  '{"Version":"2012-10-17","Statement":[{"Effect":"Allow","Action":["s3:*","logs:*"],"Resource":"*"},{"Effect":"Deny","Action":["iam:*","organizations:*"],"Resource":"*"}]}'
aws iam create-role --role-name dt-ch15-team \
  --permissions-boundary "arn:aws:iam::$DT_ACCOUNT:policy/dt-ch15-boundary" \
  --assume-role-policy-document '{"Version":"2012-10-17","Statement":[{"Effect":"Allow","Principal":{"AWS":"arn:aws:iam::'"$DT_ACCOUNT"':root"},"Action":"sts:AssumeRole"}]}'
aws iam attach-role-policy --role-name dt-ch15-team --policy-arn arn:aws:iam::aws:policy/AdministratorAccess
aws iam simulate-principal-policy --policy-source-arn "arn:aws:iam::$DT_ACCOUNT:role/dt-ch15-team" \
  --action-names s3:ListAllMyBuckets iam:CreateUser ec2:RunInstances \
  --query "EvaluationResults[].{action:EvalActionName,decision:EvalDecision}" --output table
# cleanup
aws iam detach-role-policy --role-name dt-ch15-team --policy-arn arn:aws:iam::aws:policy/AdministratorAccess
aws iam delete-role --role-name dt-ch15-team
aws iam delete-policy --policy-arn "arn:aws:iam::$DT_ACCOUNT:policy/dt-ch15-boundary"

# --- Azure: run in Azure Cloud Shell, Bash (or a terminal with Azure CLI) ---
source ~/dt-env.sh
az role definition create --role-definition '{
  "Name": "DT Golden Path Deployer",
  "Description": "Deploys the storage golden path only; cannot change access",
  "Actions": ["Microsoft.Storage/*", "Microsoft.Resources/deployments/*", "Microsoft.Insights/*"],
  "NotActions": ["Microsoft.Authorization/*"],
  "AssignableScopes": ["/subscriptions/'"$DT_SUB"'"]}'
az role definition list --name "DT Golden Path Deployer" --query "[].permissions[0]"
az role definition delete --name "DT Golden Path Deployer"   # cleanup
