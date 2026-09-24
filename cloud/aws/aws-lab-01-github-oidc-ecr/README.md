# AWS-LAB-01 — Keyless CI to AWS: GitHub OIDC, a Branch-Scoped Role and ECR

| Chapter | Level | Difficulty | Estimated time | Cloud required? |
|---|---|---|---|---|
| Chapter 6 — Identity Is the New Control Plane (non-human identity, federation); Chapter 11 §11.3/11.6; Appendix A.2 | 3 — Advanced | Advanced | 50–70 minutes | **Yes — AWS account** |

> **Cost note:** This lab may use cloud resources that can incur charges (ECR storage and data transfer; the IAM role and OIDC provider are not charged). Follow the cleanup instructions at the end of the lab and verify current pricing and free-tier eligibility before starting. Use a sandbox account, never a production account.

## What You Will Build
A CloudFormation stack that federates GitHub Actions with AWS IAM through OIDC and grants **one repository, one branch** permission to push to **one** immutable, scan-on-push ECR repository. The workflow uses no stored AWS credentials at all.

## What You Will Learn
- Replace long-lived CI access keys with short-lived, federated credentials.
- Scope a trust policy with the `sub` claim (`repo:<owner>/<repo>:ref:refs/heads/main`) and `aud`.
- Apply least privilege to ECR, including the `ecr:GetAuthorizationToken` exception (it only supports `Resource: "*"`).
- Prove the scoping by being denied from another branch.

## Prerequisites
**Required:** an AWS account you control (sandbox), with permissions to create IAM roles, an IAM OIDC provider and ECR repositories; AWS CLI v2 (`aws --version`) signed in (`aws sts get-caller-identity`); LAB-09 completed.
**Optional:** Docker locally.

> **Book alignment.** Appendix A's IAM and SCP listings follow this lab's patterns: `ecr:GetAuthorizationToken` is granted on `Resource: "*"` in its own statement (it cannot be scoped to a repository); workload deployment to EKS is authorised through EKS access entries and Kubernetes RBAC, not `eks:UpdateClusterVersion` (which upgrades the control plane); and SCP exclusions for wildcard role ARNs use `ArnNotLike`. AWS CodeCommit, referenced in Appendix A, was closed to new customers in July 2024 and returned to general availability in November 2025 — VERIFY CURRENT PRODUCT BEHAVIOUR before relying on it.

## Estimated Time
**50–70 minutes**

## Difficulty
Advanced

## Architecture
```
GitHub Actions job (repo X, branch main) ──OIDC JWT (aud=sts.amazonaws.com, sub=repo:you/X:ref:refs/heads/main)──▶ AWS STS
     AssumeRoleWithWebIdentity ── trust policy: exact aud + exact sub ──▶ 1-hour credentials
     └─▶ ecr:GetAuthorizationToken (*) + push/scan-read on ONE repository ──▶ ECR (IMMUTABLE tags, scan on push)
other branch / other repo / fork ──▶ STS: AccessDenied
```

## Step 1 — Create or Open the Repository
```bash
bash shared/scripts/start-lab.sh cloud/aws/aws-lab-01-github-oidc-ecr ~/dt-labs/dt-aws-lab-01
```
Create an empty **public** (or private) repository **`dt-aws-lab-01`** — the name must match the stack parameter.

## Step 2 — Clone the Repository
```bash
cd ~/dt-labs/dt-aws-lab-01
git remote add origin https://github.com/<your-username>/dt-aws-lab-01.git
# Do not push yet — the workflow would run before AWS is ready.
```

## Step 3 — Build the Lab: Deploy the Stack
```bash
export AWS_REGION=ap-southeast-2         # choose your region
aws cloudformation deploy \
  --stack-name dt-aws-lab-01 \
  --template-file cloudformation/github-oidc-ecr.yaml \
  --capabilities CAPABILITY_NAMED_IAM \
  --parameter-overrides GitHubOrg=<your-username> GitHubRepo=dt-aws-lab-01 CreateOidcProvider=true
aws cloudformation describe-stacks --stack-name dt-aws-lab-01 --query 'Stacks[0].Outputs' --output table
```
If the account already has the `token.actions.githubusercontent.com` provider, set `CreateOidcProvider=false`. The template omits `ThumbprintList`: AWS no longer requires thumbprints for GitHub's OIDC endpoint (VERIFY CURRENT PRODUCT BEHAVIOUR; add the thumbprint if your deployment rejects the template).
**Why it matters:** the trust policy is the security boundary. Read it in the template before deploying.

## Step 4 — Implement the Security Control
In GitHub: **Settings → Secrets and variables → Actions → Variables → New repository variable**
- `AWS_ROLE_ARN` = the `RoleArn` output
- `AWS_REGION` = your region
These are **variables**, not secrets: a role ARN is an identifier, not a credential. No AWS secret is stored anywhere.

## Step 5 — Run the Pipeline
```bash
git push -u origin main
```
Expected: `aws sts get-caller-identity` prints an `assumed-role/dt-aws-lab-01-github-push-…/dt-aws-lab-01-<run id>` ARN; the image is pushed; the scan completes; the job passes if there are no CRITICAL findings.

## Step 6 — Inspect the Result
- AWS console → **ECR → dt-aws-lab-01/dt-orders-api → Images**: one image tagged with the commit SHA; open **Vulnerabilities**.
- AWS console → **CloudTrail → Event history**, filter *Event name* = `AssumeRoleWithWebIdentity`: the event records the GitHub repository and ref in the web-identity claims — your audit evidence.
`[SCREENSHOT REQUIRED — CLOUDTRAIL AssumeRoleWithWebIdentity EVENT SHOWING THE GITHUB SUBJECT CLAIM (REDACT ACCOUNT ID)]`

## Step 7 — Introduce a Deliberate Security Failure
Try to use the role from an unapproved branch:
```bash
git switch -c feature-x && git push -u origin feature-x
```
Then **Actions → push-to-ecr → Run workflow → Use workflow from: feature-x**.

## Step 8 — Observe the Security Control
The *Assume the lab role* step fails with `Not authorized to perform sts:AssumeRoleWithWebIdentity` (EXECUTION VALIDATION REQUIRED — exact wording from the action may differ). The token's `sub` is `repo:<you>/dt-aws-lab-01:ref:refs/heads/feature-x`, which does not equal the trust policy's value.
Threat → Detection → Finding → Decision: code on an unreviewed branch attempting to publish production artefacts → STS trust-policy evaluation → denial logged in CloudTrail → no credentials issued.

## Step 9 — Remediate the Finding
Nothing to fix in AWS — the control worked. Merge `feature-x` through a pull request (with LAB-02 rulesets) so the change reaches `main` legitimately. For pull-request builds that need AWS read access, create a *separate* read-only role trusting `repo:<you>/dt-aws-lab-01:pull_request`.

## Step 10 — Validate the Fix
### Expected Result
- Workflow on `main` passes; on any other branch it fails at role assumption.
- IAM → Roles → the role → **Last activity** shows use only from the OIDC provider.
- Repository **Settings → Secrets** contains no AWS keys.

## Step 11 — Cleanup
```bash
aws cloudformation delete-stack --stack-name dt-aws-lab-01
aws cloudformation wait stack-delete-complete --stack-name dt-aws-lab-01
aws ecr describe-repositories --repository-names dt-aws-lab-01/dt-orders-api 2>&1 | grep -q RepositoryNotFound && echo "ECR repository removed"
```
`EmptyOnDelete: true` lets CloudFormation delete the repository with its images. If you set `CreateOidcProvider=false`, the pre-existing provider is untouched. Delete the GitHub variables and, optionally, the repository.

## What You Should Have Learned
Pipeline identity should be federated, short-lived and scoped to exactly the repository and branch that are allowed to act. The denial from another branch is the evidence that the scope is real.

## Lab Completion Checklist
- [ ] Repository created
- [ ] Code committed
- [ ] Pipeline executed
- [ ] Security control triggered
- [ ] Finding identified
- [ ] Finding remediated
- [ ] Pipeline passed
- [ ] Resources cleaned up (stack deleted, ECR repository gone)

## Further Challenge
Enable **Amazon Inspector** enhanced scanning for ECR in the sandbox account, compare its findings with basic scanning, and then disable it. **Cost note:** Inspector is billed per image scanned after any free trial — verify current pricing first.

---
**Validation status:** template validated with cfn-lint 1.57.0 (no errors) and Checkov 3.3.19 (12 passed, 1 documented skip); workflow checked with actionlint/zizmor. Not deployed. **EXECUTION VALIDATION REQUIRED.**
