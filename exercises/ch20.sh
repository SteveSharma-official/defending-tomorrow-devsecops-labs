#!/usr/bin/env bash
# Defending Tomorrow — Chapter 20: Continuous Risk Management
# AWS and Azure in Practice exercise (§20.9). Run the AWS block in AWS CloudShell and the
# Azure block in Azure Cloud Shell (Bash). Do not run this file as one script: copy each block
# into the shell for its platform, read the output, then run the cleanup lines.
# Prerequisite: ~/dt-env.sh from exercises/ch00.sh. Costs and cleanup are described in the book.

# --- AWS: run in AWS CloudShell (or a terminal with AWS CLI v2) ---
source ~/dt-env.sh
aws securityhub enable-security-hub --enable-default-standards
sleep 900   # first control evaluations take up to a few hours; check back later
aws securityhub get-findings \
  --filters '{"RecordState":[{"Value":"ACTIVE","Comparison":"EQUALS"}],"ComplianceStatus":[{"Value":"FAILED","Comparison":"EQUALS"}]}' \
  --query "Findings[].Severity.Label" --output text | tr '\t' '\n' | sort | uniq -c

# --- Azure: run in Azure Cloud Shell, Bash (or a terminal with Azure CLI) ---
source ~/dt-env.sh
az security secure-scores list \
  --query "[].{scope:displayName,current:score.current,max:score.max,percentage:score.percentage}" --output table
