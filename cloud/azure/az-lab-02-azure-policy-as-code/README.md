# AZ-LAB-02 — Azure Policy as Code: Non-Bypassable Guardrails at the Control Plane

| Chapter | Level | Difficulty | Estimated time | Cloud required? |
|---|---|---|---|---|
| Chapter 17 — Policy as Code (§17.4.5 Control-Plane Policy, §17.5.3 Admission, §17.6.1 Exceptions as Code); Chapter 3 secure-by-default; Appendix B.1 | 3 — Advanced | Advanced | 50–65 minutes | **Yes — Azure subscription** |

> **Cost note:** Azure Policy definitions and assignments are not charged; the test storage account is low-cost and deleted within the lab. Follow the cleanup instructions at the end of the lab and verify current pricing and free-tier eligibility before starting. Use a sandbox subscription.

## What You Will Build
Four version-controlled **custom Azure Policy definitions** (no anonymous blob access; TLS ≥ 1.2 and HTTPS-only; Key Vault RBAC permission model; mandatory `DataClassification` tag), a CI job that validates them structurally, a script that deploys and assigns them to **one resource group** in **Audit** or **Deny** mode, and test fixtures that prove a compliant deployment succeeds and a non-compliant one is refused by Azure Resource Manager.

## What You Will Learn
- Author Azure Policy rules with correct aliases and a parameterised effect.
- Stage a guardrail safely: `Audit` → review compliance → `Deny`.
- Show that control-plane policy applies to *every* path — portal, CLI, pipeline — unlike a CI-only scan.
- Reason about privilege: who may create definitions (subscription scope) versus who deploys resources (resource group).

## Prerequisites
**Required:** Azure subscription where you hold *Resource Policy Contributor* (or Owner) at subscription scope — sandbox only; Azure CLI ≥ 2.60 and `jq`; AZ-LAB-01 recommended.
**Optional:** Bicep CLI (`az bicep install`).

## Estimated Time
**50–65 minutes**

## Difficulty
Advanced

## Architecture
```
policies/*.json ─PR─▶ policy-ci (structure checks, fixture compile, shellcheck)
        │ merge + human run of scripts/deploy-policies.sh (subscription-scoped rights)
        ▼
Azure Policy definitions (subscription) ─▶ assignments (scope: rg-dt-az-lab-02, effect Audit|Deny)
        ▼
ANY write to the RG (portal / CLI / pipeline) ─▶ ARM evaluates policy ─▶ allowed | RequestDisallowedByPolicy
```

## Step 1 — Create or Open the Repository
```bash
bash shared/scripts/start-lab.sh cloud/azure/az-lab-02-azure-policy-as-code ~/dt-labs/dt-az-lab-02
```
Create an empty repository **`dt-az-lab-02`**.

## Step 2 — Clone the Repository
```bash
cd ~/dt-labs/dt-az-lab-02
git remote add origin https://github.com/<your-username>/dt-az-lab-02.git
git push -u origin main
```
Expected: `policy-ci` passes (verified locally: 4 definitions checked, fixtures compile with Bicep 0.47.16, shellcheck clean).

## Step 3 — Build the Lab
Read the four definitions. Each uses `"effect": "[parameters('effect')]"` with `Disabled` allowed — so a faulty guardrail can be switched off by assignment change without deleting code.
```bash
RG=rg-dt-az-lab-02
az group create -n $RG -l australiaeast --tags DataClassification=internal
```

## Step 4 — Implement the Security Control (Audit first)
```bash
bash scripts/deploy-policies.sh $RG Audit
az policy assignment list --scope $(az group show -n $RG --query id -o tsv) -o table
```
Wait for evaluation (up to ~30 minutes after assignment, or trigger it: `az policy state trigger-scan -g $RG`). Audit mode shows what *would* be denied — the evidence you need before switching to Deny.

## Step 5 — Run the Pipeline (switch to Deny)
```bash
bash scripts/deploy-policies.sh $RG Deny          # re-running updates definitions and assignments
SUFFIX=$RANDOM
az deployment group create -g $RG -f tests/compliant-storage.bicep -p suffix=$SUFFIX
```
Expected: the compliant storage account deploys.

## Step 6 — Inspect the Result
Portal → **Policy → Compliance** → filter scope `rg-dt-az-lab-02`: four assignments; the compliant account shows *Compliant*.
`[SCREENSHOT REQUIRED — AZURE POLICY COMPLIANCE VIEW FOR THE LAB RESOURCE GROUP (REDACT SUBSCRIPTION ID)]`

## Step 7 — Introduce a Deliberate Security Failure
```bash
az deployment group create -g $RG -f tests/noncompliant-storage.bicep -p suffix=$SUFFIX
```
Then try the same through the **portal** (create a storage account in the RG with *Allow Blob anonymous access* enabled) — a path no CI scan can see.

## Step 8 — Observe the Security Control
Expected: `RequestDisallowedByPolicy` naming `DT: Storage accounts must disallow anonymous blob access` and, because the fixture has no tag, `DT: Resources must carry a DataClassification tag` (EXECUTION VALIDATION REQUIRED — exact error format from ARM). The portal creation is refused at *Review + create* / deployment.
Threat → Detection → Finding → Decision: publicly readable storage created by any route → ARM policy evaluation → named policy assignments → request denied.

## Step 9 — Remediate the Finding
Deploy a compliant configuration instead (`allowBlobPublicAccess: false`, tag present). If a genuine exception is required, create a **policy exemption** with `--expires-on` and a justification rather than weakening the definition.

## Step 10 — Validate the Fix
### Expected Result
- Compliant deployment succeeds; non-compliant attempts are denied from CLI and portal.
- `az policy state summarize -g $RG` reports no non-compliant resources (after the next evaluation cycle).

## Step 11 — Cleanup
```bash
for a in $(az policy assignment list --scope $(az group show -n $RG --query id -o tsv) --query "[?starts_with(name,'dt-')].name" -o tsv); do
  az policy assignment delete --name "$a" --scope $(az group show -n $RG --query id -o tsv); done
for d in $(az policy definition list --query "[?starts_with(name,'dt-')].name" -o tsv); do az policy definition delete --name "$d"; done
az group delete -n $RG --yes
```

## What You Should Have Learned
Policy at the control plane is the non-bypassable backstop to pipeline scanning: it applies to every actor and every tool. Stage it (Audit → Deny), parameterise it, and manage exceptions as expiring exemptions.

## Lab Completion Checklist
- [ ] Repository created
- [ ] Code committed
- [ ] Pipeline executed
- [ ] Security control triggered
- [ ] Finding identified
- [ ] Finding remediated
- [ ] Pipeline passed
- [ ] Resources cleaned up (assignments, definitions, resource group)

## Further Challenge
Group the four definitions into a **policy initiative** (policy set definition) and assign the initiative instead; compare the compliance reporting experience.

---
**Validation status:** definitions validated structurally (4/4) and fixtures compiled with Bicep 0.47.16; deploy script passes shellcheck. Aliases and ARM denial behaviour **not** executed. **EXECUTION VALIDATION REQUIRED.**
