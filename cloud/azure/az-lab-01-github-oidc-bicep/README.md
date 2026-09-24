# AZ-LAB-01 — Keyless CI to Azure: GitHub OIDC, a Managed Identity and a Scanned Bicep Deployment

| Chapter | Level | Difficulty | Estimated time | Cloud required? |
|---|---|---|---|---|
| Chapter 6 — Identity Is the New Control Plane; Chapter 12 (IaC, Bicep); Appendix B.2–B.3 | 3 — Advanced | Advanced | 60–75 minutes | **Yes — Azure subscription** |

> **Cost note:** This lab may use cloud resources that can incur charges (a Standard_LRS storage account and a Key Vault are low-cost but not free; the user-assigned managed identity is not charged). Follow the cleanup instructions at the end of the lab and verify current pricing and free-tier eligibility before starting. Use a sandbox subscription.

## What You Will Build
A **user-assigned managed identity** with a **federated identity credential** that trusts exactly one GitHub repository *environment*, scoped by Azure RBAC to one resource group; a Bicep template for a hardened storage account and an RBAC-mode Key Vault; and a workflow that **scans** the template on every change and, on `main`, runs **what-if** and deploys after environment approval — with **no client secret anywhere**.

## What You Will Learn
- Configure workload identity federation for GitHub Actions without an app-registration secret.
- Scope the federated subject to an environment (`repo:<owner>/<repo>:environment:azure-sandbox`) so approval is part of identity.
- Scan Bicep with Checkov and record exceptions inline with reasons.
- Read an ARM what-if as the change record a reviewer approves.

## Prerequisites
**Required:** Azure subscription where you can create resource groups and role assignments (Owner or User Access Administrator on the lab resource group); Azure CLI ≥ 2.60 (`az version`) signed in (`az login`); LAB-07 recommended.
**Optional:** Bicep CLI locally (`az bicep install`).

> **Book alignment.** Appendix B's identity listings follow this lab's patterns: the AKS workload-identity issuer is read from the cluster (`az aks show --query oidcIssuerProfile.issuerUrl`), the Key Vault uses the Azure RBAC permission model only, custom roles replace non-existent built-in roles, and Azure DevOps federation subjects take the form `sc://<org>/<project>/<service-connection-name>`. Appendix B's storage policy uses the `supportsHttpsTrafficOnly` alias, as AZ-LAB-02 does. NSG flow logs can no longer be newly created (since 30 June 2025) and retire on 30 September 2027; use virtual network flow logs — VERIFY CURRENT PRODUCT BEHAVIOUR.

## Estimated Time
**60–75 minutes**

## Difficulty
Advanced

## Architecture
```
GitHub job (environment azure-sandbox, approved) ──OIDC JWT (sub=repo:you/dt-az-lab-01:environment:azure-sandbox,
                                                              aud=api://AzureADTokenExchange)──▶ Microsoft Entra ID
      federated credential on user-assigned managed identity id-dt-az-lab-01 ──▶ access token
      └─▶ Azure RBAC: Contributor on rg-dt-az-lab-01 ONLY ──▶ what-if ──▶ deployment (storage + Key Vault)
PR ──▶ scan job (no Azure access): bicep build + lint + Checkov
```

## Step 1 — Create or Open the Repository
```bash
bash shared/scripts/start-lab.sh cloud/azure/az-lab-01-github-oidc-bicep ~/dt-labs/dt-az-lab-01
```
Create an empty repository **`dt-az-lab-01`** (public or private).

## Step 2 — Clone the Repository
```bash
cd ~/dt-labs/dt-az-lab-01
git remote add origin https://github.com/<your-username>/dt-az-lab-01.git
```

## Step 3 — Build the Lab: Identity and Scope
```bash
LOC=australiaeast
RG=rg-dt-az-lab-01
GH=<your-username>
az group create -n $RG -l $LOC
az identity create -g $RG -n id-dt-az-lab-01
CLIENT_ID=$(az identity show -g $RG -n id-dt-az-lab-01 --query clientId -o tsv)
PRINCIPAL_ID=$(az identity show -g $RG -n id-dt-az-lab-01 --query principalId -o tsv)
az identity federated-credential create -g $RG --identity-name id-dt-az-lab-01 -n github-azure-sandbox \
  --issuer https://token.actions.githubusercontent.com \
  --subject "repo:${GH}/dt-az-lab-01:environment:azure-sandbox" \
  --audiences api://AzureADTokenExchange
az role assignment create --assignee-object-id $PRINCIPAL_ID --assignee-principal-type ServicePrincipal \
  --role Contributor --scope $(az group show -n $RG --query id -o tsv)
echo "CLIENT_ID=$CLIENT_ID TENANT_ID=$(az account show --query tenantId -o tsv) SUBSCRIPTION_ID=$(az account show --query id -o tsv)"
```
**Why it matters:** the identity can act only in one resource group, and only when GitHub presents a token for the approved environment of one repository.

## Step 4 — Implement the Security Control
GitHub **Settings → Secrets and variables → Actions → Variables**: `AZURE_CLIENT_ID`, `AZURE_TENANT_ID`, `AZURE_SUBSCRIPTION_ID`, `AZURE_RESOURCE_GROUP` = `rg-dt-az-lab-01`, `LAB_SUFFIX` = 3–8 lowercase letters/digits (must make storage and vault names globally unique).
**Settings → Environments → New environment** `azure-sandbox` → required reviewer: you; deployment branches: `main`.
No secrets are created — the identifiers are not credentials.

## Step 5 — Run the Pipeline
```bash
git push -u origin main
```
Expected: `scan` passes (verified locally: Bicep 0.47.16 builds and lints cleanly; Checkov `8 passed, 4 skipped`); `deploy` waits for approval → approve → what-if lists two resources to create → deployment succeeds.

## Step 6 — Inspect the Result
- Azure portal → **rg-dt-az-lab-01**: storage account (`Secure transfer required: Enabled`, `Allow Blob anonymous access: Disabled`, `Minimum TLS version: 1.2`, `Public network access: Disabled`) and Key Vault (`Permission model: Azure role-based access control`).
- **Microsoft Entra ID → Sign-in logs → Managed identity sign-ins**: the federated sign-in by `id-dt-az-lab-01`.
`[SCREENSHOT REQUIRED — ENTRA MANAGED-IDENTITY SIGN-IN LOG ENTRY FOR THE FEDERATED LOGIN (REDACT TENANT AND SUBSCRIPTION IDS)]`

## Step 7 — Introduce Deliberate Security Failures
1. **Insecure template:** on branch `weaken-storage`, apply the edits in `lab-changes/insecure-edits.md` to the storage account in `infra/main.bicep`; push; open a PR.
2. **Identity outside scope:** temporarily remove `environment: azure-sandbox` from the `deploy` job on a branch named `no-env`, allow it to run (change the `if:` to `github.ref == 'refs/heads/no-env'`) and trigger it manually.

## Step 8 — Observe the Security Control
1. Checkov fails the PR (verified locally): `CKV_AZURE_3` HTTPS-only, `CKV_AZURE_44` TLS version, `CKV_AZURE_59` public access, `CKV_AZURE_35` default network rule. (Azure may also reject TLS 1.0 at deployment time following its retirement for Storage — VERIFY CURRENT PRODUCT BEHAVIOUR.)
2. `azure/login` fails with an Entra error similar to `AADSTS700213: No matching federated identity record found for presented assertion subject 'repo:<you>/dt-az-lab-01:ref:refs/heads/no-env'` (EXECUTION VALIDATION REQUIRED).
Threat → Detection → Finding → Decision: insecure storage configuration / workflow running without approval → IaC scan / federated-subject match → named checks / Entra denial → no deployment.

## Step 9 — Remediate the Finding
Close both branches without merging. The fix for (2) is procedural: only the approved environment can obtain an Azure token; keep the federated credential's subject exact.

## Step 10 — Validate the Fix
### Expected Result
- `main` runs: scan passes, what-if shows `No change` on a re-run, deployment succeeds.
- `az role assignment list --assignee $PRINCIPAL_ID --all -o table` shows exactly one assignment, scoped to the lab resource group.

## Step 11 — Cleanup
```bash
az group delete -n rg-dt-az-lab-01 --yes
az keyvault list-deleted --query "[?name=='kv-dtazlab01-<suffix>']" -o table
az keyvault purge -n kv-dtazlab01-<suffix>        # possible because purge protection was not enabled
```
Deleting the resource group removes the identity, its federated credential and role assignment. Delete the GitHub environment and variables.

## What You Should Have Learned
Azure access for pipelines should be a federated, environment-bound, resource-group-scoped identity with nothing to steal — and the template it deploys should be scanned before that identity is ever used.

## Lab Completion Checklist
- [ ] Repository created
- [ ] Code committed
- [ ] Pipeline executed
- [ ] Security control triggered (scan and identity)
- [ ] Finding identified
- [ ] Finding remediated
- [ ] Pipeline passed
- [ ] Resources cleaned up (resource group deleted, vault purged)

## Further Challenge
Enable **Microsoft Defender for Cloud** foundational CSPM (free tier) on the sandbox subscription and compare its recommendations for the deployed resources with the Checkov findings. Do **not** enable paid Defender plans without checking pricing.

---
**Validation status:** Bicep 0.47.16 build and lint clean; Checkov 3.3.19 (8 passed, 4 documented skips; insecure variant fails 4 checks as listed); workflow checked with actionlint/zizmor. Not deployed. **EXECUTION VALIDATION REQUIRED.**
