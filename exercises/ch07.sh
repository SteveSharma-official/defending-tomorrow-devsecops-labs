#!/usr/bin/env bash
# Defending Tomorrow — Chapter 7: Networkless Security
# AWS and Azure in Practice exercise (§7.8). Run the AWS block in AWS CloudShell and the
# Azure block in Azure Cloud Shell (Bash). Do not run this file as one script: copy each block
# into the shell for its platform, read the output, then run the cleanup lines.
# Prerequisite: ~/dt-env.sh from exercises/ch00.sh. Costs and cleanup are described in the book.

# --- AWS: run in AWS CloudShell (or a terminal with AWS CLI v2) ---
source ~/dt-env.sh
VPC=$(aws ec2 describe-vpcs --filters Name=is-default,Values=true --query "Vpcs[0].VpcId" --output text)
WEB=$(aws ec2 create-security-group --group-name dt-ch07-web --description "web tier" \
  --vpc-id "$VPC" --query GroupId --output text)
APP=$(aws ec2 create-security-group --group-name dt-ch07-app --description "app tier" \
  --vpc-id "$VPC" --query GroupId --output text)
aws ec2 authorize-security-group-ingress --group-id "$APP" --protocol tcp --port 8080 --source-group "$WEB"
aws ec2 describe-security-group-rules --filters Name=group-id,Values="$APP" --output table
aws ec2 delete-security-group --group-id "$APP"; aws ec2 delete-security-group --group-id "$WEB"   # cleanup

# --- Azure: run in Azure Cloud Shell, Bash (or a terminal with Azure CLI) ---
source ~/dt-env.sh
az network asg create --resource-group "$DT_RG" --name asg-dt-web
az network asg create --resource-group "$DT_RG" --name asg-dt-app
az network nsg create --resource-group "$DT_RG" --name nsg-dt-ch07
az network nsg rule create --resource-group "$DT_RG" --nsg-name nsg-dt-ch07 --name web-to-app \
  --priority 100 --direction Inbound --access Allow --protocol Tcp \
  --source-asgs asg-dt-web --destination-asgs asg-dt-app --destination-port-ranges 8080
az network nsg rule list --resource-group "$DT_RG" --nsg-name nsg-dt-ch07 --output table
