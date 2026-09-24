#!/usr/bin/env bash
# Defending Tomorrow — Chapter 5: Cloud-Native Reference Architectures
# AWS and Azure in Practice exercise (§5.8). Run the AWS block in AWS CloudShell and the
# Azure block in Azure Cloud Shell (Bash). Do not run this file as one script: copy each block
# into the shell for its platform, read the output, then run the cleanup lines.
# Prerequisite: ~/dt-env.sh from exercises/ch00.sh. Costs and cleanup are described in the book.

# --- Azure: run in Azure Cloud Shell, Bash (or a terminal with Azure CLI) ---
source ~/dt-env.sh
az account management-group create --name mg-dt-platform --display-name "DT Platform"
az account management-group create --name mg-dt-landingzones \
  --display-name "DT Landing Zones" --parent mg-dt-platform
az account management-group show --name mg-dt-platform --expand --recurse --output json
# cleanup (children first)
az account management-group delete --name mg-dt-landingzones
az account management-group delete --name mg-dt-platform

# --- AWS: run in AWS CloudShell (or a terminal with AWS CLI v2) ---
source ~/dt-env.sh
# PAID ACCOUNT PLAN ONLY: creating an organisation upgrades a free-plan account.
aws organizations create-organization --feature-set ALL
ROOT=$(aws organizations list-roots --query "Roots[0].Id" --output text)
OU=$(aws organizations create-organizational-unit --parent-id "$ROOT" --name Workloads \
  --query OrganizationalUnit.Id --output text)
aws organizations list-organizational-units-for-parent --parent-id "$ROOT" --output table
# cleanup
aws organizations delete-organizational-unit --organizational-unit-id "$OU"
aws organizations delete-organization
