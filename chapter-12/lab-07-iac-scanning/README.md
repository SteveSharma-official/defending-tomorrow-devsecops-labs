# LAB-07 — Infrastructure as Code Scanning: Catch Misconfigurations Before Apply

| Chapter | Level | Difficulty | Estimated time | Cloud required? |
|---|---|---|---|---|
| Chapter 12 — Infrastructure as Code Security (§12.3 Control Framework, §12.4 IaC Scanning) | 2 — Practitioner | Intermediate | 40–50 minutes | **No** — Terraform is scanned, never applied |

## What You Will Build
A pipeline that scans Terraform with two engines — **Checkov** and **Trivy (config mode)** — on every pull request touching `infra/`, publishes findings to code scanning and blocks misconfigurations. The starter Terraform describes a hardened, KMS-encrypted, TLS-only, non-public S3 bucket with documented, reviewable suppressions.

## What You Will Learn
- Run IaC scanners in CI and read their findings against the Terraform source.
- Record risk-accepted exceptions **in code** with rationale (`#checkov:skip=ID:reason`) so they are reviewed like any change.
- Verify a security tool's binary before running it (Trivy's own 2026 compromise makes this concrete).
- Remediate an internet-exposed security group and a weakened public-access block.

## Prerequisites
**Required:** LAB-00; Chapter 12 §12.1–12.4.
**Optional:** `pip install checkov`; Trivy ≥ 0.69.2 (avoid 0.69.4–0.69.6); OpenTofu or Terraform to run `fmt`/`validate` locally. **No AWS account is needed** — nothing is deployed.

## Estimated Time
**40–50 minutes**

## Difficulty
Intermediate

## Architecture
```
PR touching infra/*.tf ─▶ iac-scan.yml ─┬─ checkov (pip, pinned)  ─▶ SARIF ─▶ Security → Code scanning
                                        └─ trivy config (sha256-verified binary) ─▶ HIGH/CRITICAL gate
                          suppressions live in main.tf next to the resource, with a reason → reviewed in the PR
```

## Step 1 — Create or Open the Repository
```bash
bash shared/scripts/start-lab.sh chapter-12/lab-07-iac-scanning ~/dt-labs/dt-lab-07
```
Create an empty **public** repository `dt-lab-07`.

## Step 2 — Clone the Repository
```bash
cd ~/dt-labs/dt-lab-07
git remote add origin https://github.com/<your-username>/dt-lab-07.git
git push -u origin main
```

## Step 3 — Build the Lab
Read `infra/main.tf`. Map each resource to a control: public access block (exposure), ownership controls (ACL abuse), KMS encryption with rotation (confidentiality — Chapter 8), versioning + lifecycle (integrity and cost), TLS-only bucket policy (transport).
Find the four `#checkov:skip` comments. **Why it matters:** an exception that lives in a spreadsheet is invisible to reviewers; one that lives beside the resource is reviewed, diffed and auditable.

## Step 4 — Implement the Security Control
The control is `.github/workflows/iac-scan.yml` — note the Trivy checksum step and the pinned Checkov version. Add `checkov` and `trivy-config` as required status checks (LAB-02 pattern).

## Step 5 — Run the Pipeline
The initial push runs both jobs. Expected (verified locally): Checkov `Passed checks: 30, Failed checks: 0, Skipped checks: 4`; Trivy reports `0` findings for `main.tf`.

## Step 6 — Inspect the Result
**Actions → iac-scan → checkov**: the four skipped checks are listed with your rationale. **Security → Code scanning → Tool: checkov**: no open alerts.

## Step 7 — Introduce a Deliberate Security Failure
> **Intentionally insecure IaC — never apply it.**
```bash
git switch -c temporary-admin
cp lab-changes/admin-access.tf.txt infra/admin-access.tf
sed -i 's/block_public_policy     = true/block_public_policy     = false/' infra/main.tf
git add -A && git commit -m "LAB-07: temporary admin access"
git push -u origin temporary-admin
```
Open a pull request.

## Step 8 — Observe the Security Control
Observed locally with Checkov 3.3.19 and Trivy 0.70.0:

| Scanner | Findings |
|---|---|
| Checkov (6 failed) | `CKV_AWS_24` SSH open to 0.0.0.0/0 · `CKV_AWS_382` unrestricted egress · `CKV_AWS_23` rule without description · `CKV_AWS_54` block public policy disabled · `CKV2_AWS_6` public access block incomplete · `CKV2_AWS_5` security group not attached |
| Trivy (3) | `AWS-0107` (HIGH) unrestricted ingress · `AWS-0104` (CRITICAL) unrestricted egress · `AWS-0087` (HIGH) public policies not blocked |

Threat → Detection → Finding → Decision: internet-reachable admin port and a bucket that could be made public → policy rules → file/line findings → PR blocked before any `apply`.

## Step 9 — Remediate the Finding
- Delete `infra/admin-access.tf` — administrative access should use a keyless, identity-based path (for example AWS Systems Manager Session Manager), not an open port (Chapter 7).
- Restore `block_public_policy = true`.
```bash
git rm infra/admin-access.tf
sed -i 's/block_public_policy     = false/block_public_policy     = true/' infra/main.tf
git commit -am "LAB-07: remove open SSH, restore public access block" && git push
```

## Step 10 — Validate the Fix
### Expected Result
- Both jobs pass; Checkov returns to `Failed checks: 0`, Trivy to `0` findings.
- Code-scanning alerts created by the PR are closed as fixed.

## Step 11 — Cleanup
Nothing was deployed. Delete branches and optionally the repository. If you experimented with `terraform apply`, run `terraform destroy` and confirm in the AWS console that the bucket and KMS key (scheduled deletion, 7 days) are gone.

## What You Should Have Learned
IaC scanning moves cloud misconfiguration findings from production to the pull request. Two engines disagree on detail but agree on the material risks; exceptions belong in code with reasons.

## Lab Completion Checklist
- [ ] Repository created
- [ ] Code committed
- [ ] Pipeline executed
- [ ] Security control triggered
- [ ] Finding identified
- [ ] Finding remediated
- [ ] Pipeline passed
- [ ] Resources cleaned up

## Further Challenge
Add a third job that runs `tofu fmt -check` and `tofu validate` (install OpenTofu with a checksum-verified download) so syntax errors fail before scanning.

---
**Validation status:** Checkov 3.3.19 and Trivy 0.70.0 (embedded checks) executed locally on starter (clean) and Step 7 state (findings above). Tool download checksums verified against official release files. `terraform/tofu validate` **not** executed (provider registry unavailable in the validation environment). **EXECUTION VALIDATION REQUIRED.**
