#!/usr/bin/env bash
# Defending Tomorrow — Chapter 32: AI Supply Chain Security
# AWS and Azure in Practice exercise (§32.8). Run the AWS block in AWS CloudShell and the
# Azure block in Azure Cloud Shell (Bash). Do not run this file as one script: copy each block
# into the shell for its platform, read the output, then run the cleanup lines.
# Prerequisite: ~/dt-env.sh from exercises/ch00.sh. Costs and cleanup are described in the book.

# --- AWS: run in AWS CloudShell (or a terminal with AWS CLI v2) ---
source ~/dt-env.sh
MB="dt-ch32-models-$DT_ACCOUNT"
if [ "$AWS_REGION" = "us-east-1" ]; then
  aws s3api create-bucket --bucket "$MB" --object-lock-enabled-for-bucket
else
  aws s3api create-bucket --bucket "$MB" --object-lock-enabled-for-bucket \
    --create-bucket-configuration LocationConstraint="$AWS_REGION"
fi
aws s3api put-object-lock-configuration --bucket "$MB" --object-lock-configuration \
  '{"ObjectLockEnabled":"Enabled","Rule":{"DefaultRetention":{"Mode":"GOVERNANCE","Days":1}}}'
head -c 1048576 /dev/urandom > model.bin      # stand-in for a model file
aws s3api put-object --bucket "$MB" --key models/triage/1.0/model.bin --body model.bin \
  --metadata sha256="$(sha256sum model.bin | cut -d' ' -f1)"
aws s3api head-object --bucket "$MB" --key models/triage/1.0/model.bin \
  --query "{lock:ObjectLockMode,until:ObjectLockRetainUntilDate,sha256:Metadata.sha256}"

# --- Azure: run in Azure Cloud Shell, Bash (or a terminal with Azure CLI) ---
source ~/dt-env.sh
SA="stdtmodels$RANDOM"
az storage account create --name "$SA" --resource-group "$DT_RG" --location "$DT_LOCATION" \
  --sku Standard_LRS --allow-blob-public-access false --allow-shared-key-access false
az role assignment create --assignee "$(az ad signed-in-user show --query id --output tsv)" \
  --role "Storage Blob Data Owner" --scope "$(az storage account show --name "$SA" --query id --output tsv)"
sleep 60
az storage container-rm create --storage-account "$SA" --resource-group "$DT_RG" --name models \
  --enable-vlw true
az storage container immutability-policy create --account-name "$SA" --resource-group "$DT_RG" \
  --container-name models --period 1
head -c 1048576 /dev/urandom > model.bin
az storage blob upload --account-name "$SA" --container-name models --name triage/1.0/model.bin \
  --file model.bin --metadata sha256="$(sha256sum model.bin | cut -d' ' -f1)" --auth-mode login
