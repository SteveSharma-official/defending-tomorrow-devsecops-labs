# Free AWS and Azure accounts for the labs

*Defending Tomorrow* is built on **AWS and Microsoft Azure**. The chapter exercises ([exercises/](../exercises/README.md)) and the four cloud labs (AWS-LAB-01/02, AZ-LAB-01/02) run on free accounts that you create yourself. Other clouds are outside the hands-on scope.

## Free offers (September 2026)

Check each provider's current terms before you sign up; offers change and vary by country.

| | AWS | Microsoft Azure |
|---|---|---|
| Sign-up credit | USD 100 at sign-up, plus up to USD 100 more for completing introductory activities | USD 200, in your billing currency, for the first 30 days |
| Duration | Free account plan: six months or until the credits are used, whichever comes first | Credit: 30 days. Selected services: free for 12 months |
| Always-free services | More than 30 services with monthly always-free allowances | A set of services with monthly always-free allowances |
| When the offer ends | Upgrade to the paid plan within 90 days, or the account closes and its resources are deleted | Upgrade to pay-as-you-go, or the subscription is disabled |
| Watch out for | Joining AWS Organizations or setting up AWS Control Tower upgrades a free-plan account to the paid plan automatically; Chapters 5 and 17 mark these steps | Some services and AI model deployments are not offered on free-trial subscriptions, and quotas are lower |

Sources: [AWS Free Tier announcement (July 2025)](https://aws.amazon.com/about-aws/whats-new/2025/07/aws-free-tier-credits-month-free-plan/), [AWS free and paid account plans](https://docs.aws.amazon.com/awsaccountbilling/latest/aboutv2/free-tier-plans.html), [Avoid charges with your Azure free account](https://learn.microsoft.com/en-us/azure/cost-management-billing/manage/avoid-charges-free-account).

Plan around the 30-day Azure credit: create the Azure account when you reach Part II (Chapter 5), because from there the exercises use it in every chapter. Most exercises use services that stay free after the offer ends (identity, policy, logs and role assignments), so they keep costing nothing if you upgrade an account to pay-as-you-go.

Use accounts you own and that hold nothing else. Never run the exercises in an employer's or client's account: several create identities, policies and log exports at account or subscription level. Do not use the AWS root user for the exercises; create an administrative user in IAM Identity Center with MFA, and turn on MFA for your Azure sign-in.

## Budget alerts (do this first)

Set a budget with an email alert on each account before anything else. All commands in this book run in the providers' browser-based shells, AWS CloudShell and Azure Cloud Shell, which come with the command-line tools installed and need no local setup. Replace you@example.com with your own address.

```bash
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
```

## Lab environment file

Each exercise starts with source ~/dt-env.sh. Create that file once in each shell with the block for that platform. AWS CloudShell keeps your home directory between sessions. Azure Cloud Shell keeps it only when you attach a storage account, so in an ephemeral session re-run the Azure block at the start of each chapter.

```bash
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

```

Every exercise ends with its own cleanup, and every Azure resource goes into the rg-dt-labs resource group, so deleting that group removes anything you missed. Chapter 36 ends with a final teardown of both accounts.
