# AWS-LAB-02 — Gated Terraform Delivery to AWS with Plan-Time Policy and Drift Detection

| Chapter | Level | Difficulty | Estimated time | Cloud required? |
|---|---|---|---|---|
| Chapter 12 — IaC Security (§12.5 Policy Validation Pre-Apply, §12.6 State, §12.7 Drift); Chapter 8 (KMS); Chapter 17 | 3 — Advanced | Advanced | 75–90 minutes | **Yes — AWS account** |

> **Cost note:** This lab may use cloud resources that can incur charges (a customer-managed KMS key is billed monthly, pro-rated; S3 storage and requests). Follow the cleanup instructions at the end of the lab and verify current pricing and free-tier eligibility before starting. KMS keys enter a 7-day pending-deletion window after cleanup.

## What You Will Build
A Terraform pipeline that deploys the LAB-07 evidence bucket (KMS-encrypted, TLS-only, non-public) to a sandbox account using **OIDC credentials only**, with remote **S3 state and native locking**, **Checkov and Conftest on the resolved plan**, **human approval** through a GitHub Environment, `apply` of **exactly the reviewed plan**, and a **scheduled drift check**.

## What You Will Learn
- Scan the *plan* (resolved values) rather than only the source.
- Apply organisational policy (LAB-08) to a real plan before any change.
- Bind apply rights to an approved environment via the OIDC `sub` claim (`environment:aws-sandbox`).
- Detect and remediate out-of-band changes (drift) — Chapter 12 §12.7.

## Prerequisites
**Required:** AWS-LAB-01 completed (GitHub OIDC provider exists in the account); LAB-07 and LAB-08; AWS CLI v2 signed in to a **sandbox** account.
**Optional:** Terraform ≥ 1.10 locally.

## Estimated Time
**75–90 minutes**

## Difficulty
Advanced

## Architecture
```
PR / push / every 6 h ─▶ plan job (OIDC: pull_request | ref main) ─▶ init (S3 backend, use_lockfile)
                          ├─ fmt + validate ─▶ plan -detailed-exitcode ─▶ show -json
                          ├─ Checkov (terraform_plan) ─▶ Conftest (policy/terraform.rego)
                          └─ schedule + exit 2 ⇒ DRIFT alarm
main + changes ─▶ apply job ─▶ environment aws-sandbox (required reviewer) ─▶ OIDC sub=environment:aws-sandbox
                              └─ terraform apply tf.plan (the reviewed artefact)
```

## Step 1 — Create or Open the Repository
```bash
bash shared/scripts/start-lab.sh cloud/aws/aws-lab-02-terraform-drift-gate ~/dt-labs/dt-aws-lab-02
```
Create an empty **private** or public repository named **`dt-aws-lab-02`** (no AWS secrets are stored, but the plan artifact reveals resource names — private is reasonable here).

## Step 2 — Clone the Repository
```bash
cd ~/dt-labs/dt-aws-lab-02
git remote add origin https://github.com/<your-username>/dt-aws-lab-02.git
```

## Step 3 — Build the Lab: Bootstrap Role and State Bucket
```bash
export AWS_REGION=ap-southeast-2
aws cloudformation deploy --stack-name dt-aws-lab-02-bootstrap \
  --template-file cloudformation/terraform-role.yaml --capabilities CAPABILITY_NAMED_IAM \
  --parameter-overrides GitHubOrg=<your-username> GitHubRepo=dt-aws-lab-02
aws cloudformation describe-stacks --stack-name dt-aws-lab-02-bootstrap --query 'Stacks[0].Outputs' --output table
```
The role can manage only buckets named `dt-aws-lab-02-evidence-*` and KMS keys tagged `Lab=dt-aws-lab-02`. **EXECUTION VALIDATION REQUIRED:** Terraform's AWS provider may call additional read APIs; if `apply` reports `AccessDenied`, add the specific action named in the error (use CloudTrail or IAM Access Analyzer policy generation) rather than widening to `*`.

## Step 4 — Implement the Security Control
GitHub **Settings → Secrets and variables → Actions → Variables**:
`AWS_ROLE_ARN` (RoleArn output), `AWS_REGION`, `TF_STATE_BUCKET` (StateBucket output), `EVIDENCE_BUCKET_NAME` = `dt-aws-lab-02-evidence-<your-initials>-<random-digits>`.
**Settings → Environments → New environment** `aws-sandbox` → **Required reviewers**: you; **Deployment branches**: `main` only.

## Step 5 — Run the Pipeline
```bash
git push -u origin main
```
Expected: `plan` passes Checkov and Conftest (`3 tests, 3 passed` style output) with exit code 2 (changes); `apply` waits for approval → approve → bucket and key created.

## Step 6 — Inspect the Result
- S3 console: the bucket shows *Block all public access: On*, default encryption *SSE-KMS*, versioning *Enabled*, tags `CostCenter`, `DataClassification`, `Lab`.
- State bucket: `dt-aws-lab-02/terraform.tfstate` plus a transient `.tflock` object during runs.
- GitHub **Deployments**: one approved deployment to `aws-sandbox`.

## Step 7 — Introduce Deliberate Security Failures
1. **Policy failure (change-time):** on branch `no-classification`, remove `DataClassification` from `default_tags` in `infra/main.tf`, push, open a PR.
2. **Drift (run-time):** simulate an engineer "quickly fixing" something in the console:
```bash
aws s3api delete-public-access-block --bucket <EVIDENCE_BUCKET_NAME>
```
Then run **Actions → terraform → Run workflow** on `main` (or wait for the 6-hourly schedule).

## Step 8 — Observe the Security Control
1. Conftest fails: `POL-TAG-001 aws_s3_bucket.evidence is missing required tags: ["DataClassification"]` — no apply is possible from the PR.
2. The plan exits **2** and shows `aws_s3_bucket_public_access_block.evidence will be created` (the out-of-band deletion). On a scheduled run the job fails with `DRIFT DETECTED`; on a manual run on `main` the plan goes to the approval gate.
Threat → Detection → Finding → Decision: untagged/unclassified data store, or a bucket silently opened → plan-time policy / scheduled plan → specific resource diff → block, or reviewed re-convergence.

## Step 9 — Remediate the Finding
1. Restore the tag; the PR passes.
2. Review the plan for the drifted resource in the run log; approve the `aws-sandbox` deployment to re-apply the public access block. Record who made the console change (CloudTrail `DeletePublicAccessBlock` event) — drift is an incident signal, not only a config diff.

## Step 10 — Validate the Fix
### Expected Result
- A subsequent run shows `No changes` (exit code 0).
- `aws s3api get-public-access-block --bucket <name>` shows all four settings `true`.

## Step 11 — Cleanup
```bash
cd infra
terraform init -backend-config="bucket=<TF_STATE_BUCKET>" -backend-config="region=$AWS_REGION"
TF_VAR_region=$AWS_REGION TF_VAR_bucket_name=<EVIDENCE_BUCKET_NAME> terraform destroy
cd ..
aws s3 rm s3://<TF_STATE_BUCKET> --recursive
aws s3api delete-objects --bucket <TF_STATE_BUCKET> --delete "$(aws s3api list-object-versions --bucket <TF_STATE_BUCKET> --query '{Objects: Versions[].{Key:Key,VersionId:VersionId}}' --output json)"
aws cloudformation delete-stack --stack-name dt-aws-lab-02-bootstrap
```
If `delete-objects` reports no versions, skip it; delete-markers may also need removal before the stack can delete the state bucket. Confirm in the KMS console that the lab key shows *Pending deletion*. Delete the GitHub environment and variables.

## What You Should Have Learned
Infrastructure changes become safe when the reviewed plan — scanned, policy-checked and approved — is exactly what is applied, and when the pipeline keeps comparing reality with the code afterwards.

## Lab Completion Checklist
- [ ] Repository created
- [ ] Code committed
- [ ] Pipeline executed
- [ ] Security control triggered (policy and drift)
- [ ] Finding identified
- [ ] Finding remediated
- [ ] Pipeline passed
- [ ] Resources cleaned up (bucket, key scheduled for deletion, state bucket, stack)

## Further Challenge
Add an AWS Config managed rule (`s3-bucket-level-public-access-prohibited`) through Terraform and compare its detection latency with the scheduled plan. **Cost note:** AWS Config bills per configuration item recorded.

---
**Validation status:** CloudFormation validated with cfn-lint 1.57.0 and Checkov (16 passed, 2 documented skips); Terraform formatted with OpenTofu 1.10.6 and scanned with Checkov (30 passed, 4 documented skips); Conftest policies reused from LAB-08 (tested). `terraform validate/plan/apply` and IAM permission sufficiency **not** executed. **EXECUTION VALIDATION REQUIRED.**
