#!/usr/bin/env bash
# Defending Tomorrow — Chapter 0 (§0.10): budget alerts and the lab environment file.
# Run the AWS blocks in AWS CloudShell and the Azure blocks in Azure Cloud Shell (Bash).
# Replace you@example.com with your own address.

# --- AWS: run in AWS CloudShell ---
ACCOUNT=$(aws sts get-caller-identity --query Account --output text)
aws budgets create-budget --account-id "$ACCOUNT" \
  --budget '{"BudgetName":"dt-labs","BudgetLimit":{"Amount":"10","Unit":"USD"},"TimeUnit":"MONTHLY","BudgetType":"COST"}' \
  --notifications-with-subscribers '[{"Notification":{"NotificationType":"ACTUAL","ComparisonOperator":"GREATER_THAN","Threshold":50,"ThresholdType":"PERCENTAGE"},"Subscribers":[{"SubscriptionType":"EMAIL","Address":"you@example.com"}]}]'

# --- Azure: run in Azure Cloud Shell (Bash) ---
SUB=$(az account show --query id --output tsv)
az rest --method put \
  --url "https://management.azure.com/subscriptions/$SUB/providers/Microsoft.Consumption/budgets/dt-labs?api-version=2023-05-01" \
  --body '{"properties":{"category":"Cost","amount":10,"timeGrain":"Monthly",
    "timePeriod":{"startDate":"'"$(date -u +%Y-%m-01)"'T00:00:00Z"},
    "notifications":{"actual50":{"enabled":true,"operator":"GreaterThan","threshold":50,"contactEmails":["you@example.com"]}}}}'

# --- AWS CloudShell: create ~/dt-env.sh ---
cat > ~/dt-env.sh <<'ENV'
export AWS_REGION=${AWS_REGION:-us-east-1}   # CloudShell sets this to your console Region
export DT_ACCOUNT=$(aws sts get-caller-identity --query Account --output text)
ENV
source ~/dt-env.sh && echo "AWS account $DT_ACCOUNT in $AWS_REGION"

# --- Azure Cloud Shell (Bash): create ~/dt-env.sh ---
cat > ~/dt-env.sh <<'ENV'
export DT_LOCATION=${DT_LOCATION:-eastus}    # choose the region nearest to you
export DT_RG=rg-dt-labs
export DT_SUB=$(az account show --query id --output tsv)
az group create --name "$DT_RG" --location "$DT_LOCATION" --tags project=defending-tomorrow --output none
ENV
source ~/dt-env.sh && echo "Azure subscription $DT_SUB, resource group $DT_RG"

