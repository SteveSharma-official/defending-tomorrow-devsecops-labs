#!/usr/bin/env bash
# Defending Tomorrow — Chapter 30: RAG Security Engineering
# AWS and Azure in Practice exercise (§30.9). Run the AWS block in AWS CloudShell and the
# Azure block in Azure Cloud Shell (Bash). Do not run this file as one script: copy each block
# into the shell for its platform, read the output, then run the cleanup lines.
# Prerequisite: ~/dt-env.sh from exercises/ch00.sh. Costs and cleanup are described in the book.

# --- AWS: run in AWS CloudShell (or a terminal with AWS CLI v2) ---
source ~/dt-env.sh
GR=$(aws bedrock create-guardrail --name dt-ch30 \
  --blocked-input-messaging "Blocked." --blocked-outputs-messaging "Answer withheld: not supported by the source." \
  --contextual-grounding-policy-config '{"filtersConfig":[{"type":"GROUNDING","threshold":0.8},{"type":"RELEVANCE","threshold":0.7}]}' \
  --query guardrailId --output text)
aws bedrock-runtime apply-guardrail --guardrail-identifier "$GR" --guardrail-version DRAFT --source OUTPUT \
  --content '[{"text":{"text":"Refunds are accepted within 30 days of purchase.","qualifiers":["grounding_source"]}},
              {"text":{"text":"What is the refund window?","qualifiers":["query"]}},
              {"text":{"text":"The refund window is 90 days.","qualifiers":["guard_content"]}}]' \
  --query "{action:action,output:outputs[0].text}"
aws bedrock delete-guardrail --guardrail-identifier "$GR"   # cleanup

# --- Azure: run in Azure Cloud Shell, Bash (or a terminal with Azure CLI) ---
source ~/dt-env.sh
az search service create --name "srch-dt-ch30-$RANDOM" --resource-group "$DT_RG" \
  --location "$DT_LOCATION" --sku free --disable-local-auth true
az search service list --resource-group "$DT_RG" \
  --query "[].{name:name,sku:sku.name,localAuthDisabled:disableLocalAuth,publicNetwork:publicNetworkAccess}" --output table
