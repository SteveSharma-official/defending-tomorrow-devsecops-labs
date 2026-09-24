#!/usr/bin/env bash
# Defending Tomorrow — Chapter 28: AI for Security Operations
# AWS and Azure in Practice exercise (§28.8). Run the AWS block in AWS CloudShell and the
# Azure block in Azure Cloud Shell (Bash). Do not run this file as one script: copy each block
# into the shell for its platform, read the output, then run the cleanup lines.
# Prerequisite: ~/dt-env.sh from exercises/ch00.sh. Costs and cleanup are described in the book.

# --- AWS: run in AWS CloudShell (or a terminal with AWS CLI v2) ---
source ~/dt-env.sh
# a cross-Region inference profile; outside the US use the eu. or apac. prefix
aws bedrock-runtime converse --model-id us.amazon.nova-lite-v1:0 \
  --messages '[{"role":"user","content":[{"text":"In three bullet points for a SOC analyst: what does a GuardDuty finding of type UnauthorizedAccess:IAMUser/InstanceCredentialExfiltration.OutsideAWS mean, and what are the first two checks?"}]}]' \
  --query "output.message.content[0].text" --output text

# --- Azure: run in Azure Cloud Shell, Bash (or a terminal with Azure CLI) ---
source ~/dt-env.sh
az cognitiveservices account create --name "ais-dt-ch28-$RANDOM" --resource-group "$DT_RG" \
  --location "$DT_LOCATION" --kind AIServices --sku S0 --yes
AIS=$(az cognitiveservices account list --resource-group "$DT_RG" --query "[?kind=='AIServices'].name | [0]" --output tsv)
az cognitiveservices account list-models --name "$AIS" --resource-group "$DT_RG" \
  --query "[?format=='OpenAI'].{model:name,version:version}" --output table
