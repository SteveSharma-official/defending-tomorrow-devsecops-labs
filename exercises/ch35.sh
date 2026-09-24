#!/usr/bin/env bash
# Defending Tomorrow — Chapter 35: Security Metrics That Matter
# AWS and Azure in Practice exercise (§35.8). Run the AWS block in AWS CloudShell and the
# Azure block in Azure Cloud Shell (Bash). Do not run this file as one script: copy each block
# into the shell for its platform, read the output, then run the cleanup lines.
# Prerequisite: ~/dt-env.sh from exercises/ch00.sh. Costs and cleanup are described in the book.

# --- AWS: run in AWS CloudShell (or a terminal with AWS CLI v2) ---
source ~/dt-env.sh
aws securityhub get-findings \
  --filters '{"RecordState":[{"Value":"ACTIVE","Comparison":"EQUALS"}],"ComplianceStatus":[{"Value":"FAILED","Comparison":"EQUALS"}]}' \
  --query "Findings[].Severity.Label" --output text | tr '\t' '\n' | sort | uniq -c
aws securityhub disable-security-hub   # when you no longer need the trial

# --- Azure: run in Azure Cloud Shell, Bash (or a terminal with Azure CLI) ---
source ~/dt-env.sh
az security secure-scores list --query "[].{current:score.current,max:score.max,percentage:score.percentage}" --output table
az policy state summarize --query "results.{nonCompliantResources:nonCompliantResources,nonCompliantPolicies:nonCompliantPolicies}"
