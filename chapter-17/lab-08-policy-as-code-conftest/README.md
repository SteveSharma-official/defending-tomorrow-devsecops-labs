# LAB-08 — Policy as Code: Evaluate a Terraform Plan Against Organisational Guardrails

| Chapter | Level | Difficulty | Estimated time | Cloud required? |
|---|---|---|---|---|
| Chapter 17 — Policy as Code (§17.3 Open Policy Agent and Rego, §17.5.2 Pre-Apply, §17.6.1 Exceptions as Code); Chapter 12 §12.5 Policy Validation Pre-Apply | 2 — Practitioner | Intermediate | 45–55 minutes | No |

## What You Will Build
Three organisational guardrails in **Rego (OPA 1.x syntax)** — mandatory data-classification and cost tags, no internet-exposed administrative ports, mandatory KMS key rotation — with **unit tests**, evaluated by **Conftest** against a Terraform plan in JSON form on every pull request.

## What You Will Learn
- Write deny rules over `terraform show -json` output (`resource_changes[].change.after`).
- Handle provider `default_tags` (`tags_all`) correctly — a common false-negative/false-positive source.
- Test policies before trusting them (`conftest verify`), including edge cases such as port ranges.
- Distinguish scanners (generic best practice, LAB-07) from policy-as-code (your organisation's rules).

## Prerequisites
**Required:** LAB-07; Chapter 12 §12.5.
**Optional:** OPA ≥ 1.0 and Conftest ≥ 0.56 locally; Terraform/OpenTofu to produce your own plan JSON.

> **Book alignment.** Chapter 12 (§12.5) and Chapter 17 (§17.3, §17.5.2) print this lab's policy style in Rego v1 syntax, the syntax used throughout the book. Chapter 17 §17.6.1 shows the solution pattern for this lab's Further Challenge (governed, expiring exceptions for `POL-NET-002`).

## Estimated Time
**45–55 minutes**

## Difficulty
Intermediate

## Architecture
```
infra change ─▶ terraform plan -out tf.plan ─▶ terraform show -json > plans/plan.json
                                                     │
PR ─▶ policy-gate.yml ─▶ conftest verify (8 unit tests) ─▶ conftest test plans/plan.json
                                                              ├ POL-TAG-001 required tags (tags ∪ tags_all)
                                                              ├ POL-NET-002 no 0.0.0.0/0 to 22/3389 (incl. ranges)
                                                              └ POL-KMS-003 key rotation
```

## Step 1 — Create or Open the Repository
```bash
bash shared/scripts/start-lab.sh chapter-17/lab-08-policy-as-code-conftest ~/dt-labs/dt-lab-08
```
Create an empty **public** repository `dt-lab-08`.

## Step 2 — Clone the Repository
```bash
cd ~/dt-labs/dt-lab-08
git remote add origin https://github.com/<your-username>/dt-lab-08.git
git push -u origin main
```

## Step 3 — Build the Lab
Read `policy/terraform.rego` and `policy/terraform_test.rego`. `plans/plan.json` is a trimmed, synthetic plan in the real JSON shape, so no cloud account is needed. (AWS-LAB-02 runs the same policies against a real plan.)

## Step 4 — Implement the Security Control
`.github/workflows/policy-gate.yml`: installs Conftest with checksum verification, runs `conftest verify` (policy unit tests), then `conftest test` with `--output github` so failures appear as annotations.

## Step 5 — Run the Pipeline
Expected (verified locally, Conftest 0.62.0 / OPA 1.20.2): `8 tests, 8 passed` then `3 tests, 3 passed`.

## Step 6 — Inspect the Result
**Actions → policy-gate → conftest**. Read the unit-test names: they are the policy's specification.

## Step 7 — Introduce a Deliberate Security Failure
On branch `non-compliant`, apply the three edits in `lab-changes/violating-changes.md` to `plans/plan.json` (remove `DataClassification`, open port 22, disable key rotation). Commit, push, open a PR.

## Step 8 — Observe the Security Control
Observed locally:
```
FAIL - plans/plan.json - main - POL-KMS-003 aws_kms_key.evidence must set enable_key_rotation = true
FAIL - plans/plan.json - main - POL-NET-002 aws_security_group.web exposes admin port 22 to 0.0.0.0/0
FAIL - plans/plan.json - main - POL-TAG-001 aws_s3_bucket.evidence is missing required tags: ["DataClassification"]
3 tests, 0 passed, 3 failures
```
Threat → Detection → Finding → Decision: unclassified data, exposed admin access, static keys → policy rules → policy ID + resource address → merge blocked before `apply`.

## Step 9 — Remediate the Finding
Revert the three edits (`git checkout main -- plans/plan.json`) — in a real pipeline you fix the Terraform and regenerate the plan. Commit and push.

## Step 10 — Validate the Fix
### Expected Result
- `8 tests, 8 passed` and `3 tests, 3 passed`.
- Write one more unit test proving that SSH from `0.0.0.0/0` via a port range `20–25` is denied, and see it pass.

## Step 11 — Cleanup
No cloud resources. Delete branches; optionally delete the repository.

## What You Should Have Learned
Policy-as-code encodes *your* rules, is tested like code, and evaluates the resolved plan — the last point where a change can be stopped cheaply.

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
Add an exceptions mechanism: a `data.exceptions` JSON file listing resource addresses, policy IDs, approver and expiry; the deny rule must skip only unexpired, approved exceptions — with tests for expired ones.

---
**Validation status:** `opa check --strict`, `conftest verify` (8/8) and `conftest test` on compliant and violating plans executed locally (results above). **EXECUTION VALIDATION REQUIRED** on a GitHub-hosted runner.
