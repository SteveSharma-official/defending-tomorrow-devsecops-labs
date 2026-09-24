#!/usr/bin/env bash
# Defending Tomorrow — Chapter 4: Threat Modeling for Modern Enterprises
# AWS and Azure in Practice exercise (§4.9). Run the AWS block in AWS CloudShell and the
# Azure block in Azure Cloud Shell (Bash). Do not run this file as one script: copy each block
# into the shell for its platform, read the output, then run the cleanup lines.
# Prerequisite: ~/dt-env.sh from exercises/ch00.sh. Costs and cleanup are described in the book.

# --- AWS: run in AWS CloudShell (or a terminal with AWS CLI v2) ---
source ~/dt-env.sh
aws ec2 describe-security-group-rules \
  --query "SecurityGroupRules[?CidrIpv4=='0.0.0.0/0' && !IsEgress].{group:GroupId,protocol:IpProtocol,from:FromPort,to:ToPort}" \
  --output table

# --- Azure: run in Azure Cloud Shell, Bash (or a terminal with Azure CLI) ---
source ~/dt-env.sh
az network nsg list \
  --query "[].securityRules[] | [?access=='Allow' && direction=='Inbound' && (sourceAddressPrefix=='*' || sourceAddressPrefix=='Internet')].{rule:name,port:destinationPortRange,priority:priority}" \
  --output table
