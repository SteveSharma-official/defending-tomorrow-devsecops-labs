# LAB-14 — Security Gates and Deployment Environments: A Policy-Decided Release

| Chapter | Level | Difficulty | Estimated time | Cloud required? |
|---|---|---|---|---|
| Chapter 15 — Platform Engineering (§15.3 Golden Paths as Security Controls); Chapter 11 §11.6 Deploy Surface; Chapter 9 | 3 — Advanced | Advanced | 50–70 minutes | No (deployments are simulated) |

## What You Will Build
A multi-stage pipeline in which four security checks run in parallel, a **release-decision job evaluates an OPA policy** over their results, and deployment proceeds through **GitHub Environments**: `staging` automatically, `production` only from `main` and only after a **required reviewer** approves.

## What You Will Learn
- Separate *collecting* security evidence from *deciding* on a release.
- Express the release gate as tested policy-as-code (`opa test`) rather than scattered `if:` expressions.
- Configure environment protection rules (required reviewers, deployment branch policy).
- Show that a failed check, or a non-`main` ref, can never reach production.

## Prerequisites
**Required:** LAB-03, LAB-05, LAB-06 (the checks reused here); LAB-08 (Rego basics).
**Optional:** OPA ≥ 1.0 locally (`opa test policy -v`).

## Estimated Time
**50–70 minutes**

## Difficulty
Advanced

## Architecture
```
            ┌ tests ┐
push/PR ──▶ ├ sast  ┤──▶ release-decision (OPA: data.release.allow) ──▶ deploy-staging ──▶ deploy-production
            ├ sca   ┤          │ records violations even on failure        (env: staging)     (env: production:
            └ secrets┘          └ false → nothing deploys                                       reviewer + main only)
```

## Step 1 — Create or Open the Repository
```bash
bash shared/scripts/start-lab.sh chapter-11/lab-14-security-gates-environments ~/dt-labs/dt-lab-14
```
Create an empty **public** repository `dt-lab-14`. Environment required reviewers and branch policies are available for public repositories on GitHub Free (private repositories need a paid plan — VERIFY CURRENT PRODUCT BEHAVIOUR).

## Step 2 — Clone the Repository
```bash
cd ~/dt-labs/dt-lab-14
git remote add origin https://github.com/<your-username>/dt-lab-14.git
git push -u origin main
```

## Step 3 — Build the Lab: Create the Environments
**Settings → Environments → New environment**
1. `staging` — no protection rules.
2. `production` — tick **Required reviewers** and add yourself; under **Deployment branches and tags** choose **Selected branches and tags** → add rule `main`.
Why it matters: the environment is the deploy surface's control point (Chapter 11 §11.6); secrets scoped to an environment are released only after its rules pass.

## Step 4 — Implement the Security Control
Read `policy/release.rego` and `.github/workflows/pipeline.yml`. The gate is `release-decision`: it runs even when checks fail (`if: always()`), writes the decision input, prints violations and fails if `allow` is false. Locally: `opa test policy -v` → `PASS: 5/5` (verified with OPA 1.20.2).

## Step 5 — Run the Pipeline
Re-run the workflow on `main` (**Actions → pipeline → Run workflow**) now that environments exist. Expected: four checks pass → `Release allowed: true` → `deploy-staging` runs → `deploy-production` shows **Waiting for review**.

## Step 6 — Inspect the Result
Open the run graph. Select **Review deployments → production → Approve and deploy**. The approval, approver and timestamp are recorded under **Deployments** — this is change-approval evidence (Chapter 18).

## Step 7 — Introduce Deliberate Security Failures
> **Intentionally vulnerable change — lab use only.**
1. **Failed check:** on branch `sqli`, introduce the f-string query from LAB-05 (`app/app.py`), push, and also run the workflow manually on that branch (**Run workflow → Use workflow from: sqli**).
2. **Wrong ref:** on a clean branch `feature-x`, run the workflow manually.

## Step 8 — Observe the Security Control
| Attempt | Expected result |
|---|---|
| `sqli` | `sast` fails (and the regression test in `tests` fails); `release-decision` prints `required check 'sast' is failure` (verified locally with the policy) and `Release allowed: false`; no deployment job runs |
| `feature-x` | All checks pass but the decision reports `production releases must come from main, not refs/heads/feature-x`; even if the policy were bypassed, the `production` environment's branch rule rejects the job |

Threat → Detection → Finding → Decision: vulnerable or unapproved code heading to production → evidence jobs + policy → explicit violation list → release denied by two independent layers.

## Step 9 — Remediate the Finding
Fix the query on `sqli` (parameterised form), push, open a PR and merge to `main` after checks pass. Delete `feature-x`.

## Step 10 — Validate the Fix
### Expected Result
- On `main`: `Release allowed: true`, staging deployed, production waiting for your approval, then deployed.
- The **Deployments** page shows one production deployment, from `main`, approved by you.

## Step 11 — Cleanup
Delete branches. Optionally delete the environments (**Settings → Environments**) and the repository. Nothing was deployed anywhere.

## What You Should Have Learned
A release gate is a policy decision over evidence, backed by an environment the pipeline cannot bypass. Tested policy makes the rule reviewable; environments make it enforceable and auditable.

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
Add an input `change_ticket` to the decision (from a PR label or `workflow_dispatch` input) and require it for production — a policy test first, then the workflow change.

---
**Validation status:** `opa test` 5/5 passing and violation output verified with OPA 1.20.2; the sample app's tests, Semgrep rule and gitleaks executed locally against a fresh lab repository; workflow checked with actionlint/zizmor. Environment behaviour not executed. **EXECUTION VALIDATION REQUIRED.**
