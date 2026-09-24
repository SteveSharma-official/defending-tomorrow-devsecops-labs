#!/usr/bin/env bash
# Defending Tomorrow — Chapter 14: Container Security Engineering
# AWS and Azure in Practice exercise (§14.7). Run the AWS block in AWS CloudShell and the
# Azure block in Azure Cloud Shell (Bash). Do not run this file as one script: copy each block
# into the shell for its platform, read the output, then run the cleanup lines.
# Prerequisite: ~/dt-env.sh from exercises/ch00.sh. Costs and cleanup are described in the book.

# --- Azure: run in Azure Cloud Shell, Bash (or a terminal with Azure CLI) ---
source ~/dt-env.sh
# OPTIONAL, BILLED: one small node. Delete it within the hour.
az aks create --resource-group "$DT_RG" --name aks-dt-ch14 --tier free \
  --node-count 1 --node-vm-size Standard_B2s --generate-ssh-keys \
  --enable-aad --enable-azure-rbac --enable-oidc-issuer --enable-workload-identity \
  --enable-addons azure-policy
az aks show --resource-group "$DT_RG" --name aks-dt-ch14 \
  --query "{oidc:oidcIssuerProfile.enabled,workloadIdentity:securityProfile.workloadIdentity.enabled,azurePolicy:addonProfiles.azurepolicy.enabled,localAccounts:disableLocalAccounts}"
az aks delete --resource-group "$DT_RG" --name aks-dt-ch14 --yes --no-wait   # cleanup

# --- AWS: run in AWS CloudShell (or a terminal with AWS CLI v2) ---
source ~/dt-env.sh
aws eks describe-addon-versions --addon-name eks-pod-identity-agent \
  --query "addons[0].addonVersions[0:3].{version:addonVersion,compatible:compatibilities[0].clusterVersion}" \
  --output table
