#!/usr/bin/env bash
# Defending Tomorrow — Chapter 34: Building a Modern Security Program
# AWS and Azure in Practice exercise (§34.9). Run the AWS block in AWS CloudShell and the
# Azure block in Azure Cloud Shell (Bash). Do not run this file as one script: copy each block
# into the shell for its platform, read the output, then run the cleanup lines.
# Prerequisite: ~/dt-env.sh from exercises/ch00.sh. Costs and cleanup are described in the book.

# --- AWS: run in AWS CloudShell (or a terminal with AWS CLI v2) ---
source ~/dt-env.sh
WL=$(aws wellarchitected create-workload --workload-name dt-ch34-programme \
  --description "Security programme baseline" --environment PREPRODUCTION \
  --lenses wellarchitected --aws-regions "$AWS_REGION" --review-owner security@example.com \
  --query WorkloadId --output text)
aws wellarchitected list-answers --workload-id "$WL" --lens-alias wellarchitected --pillar-id security \
  --query "AnswerSummaries[].QuestionTitle" --output text | tr '\t' '\n'
aws wellarchitected delete-workload --workload-id "$WL"   # cleanup

# --- Azure: run in Azure Cloud Shell, Bash (or a terminal with Azure CLI) ---
source ~/dt-env.sh
az advisor recommendation list --category Security \
  --query "[].{impact:impact,problem:shortDescription.problem}" --output table
