# LAB-30 — Metrics from Evidence: Compute Chapter 35 Metrics You Can Defend

| Chapter | Level | Difficulty | Estimated time | Cloud required? |
|---|---|---|---|---|
| Chapter 35 — Security Metrics That Matter (§35.2 Metrics Translation Framework, §35.3 Core Operational Metrics Catalog, §35.6 Metrics Anti-Pattern Reference) · builds on LAB-16 and the CAPSTONE | 3 — Advanced | Intermediate | 35–45 minutes | No |

## What You Will Build
A metrics pipeline that computes the Table 35.2 operational metrics from **sealed evidence records**: 40 pipeline runs and 8 incidents, each carrying a SHA-256 over its own content, as LAB-16 hashes evidence. The metrics are:
- Platform Security Adoption.
- Policy-as-Code Enforcement Rate.
- Supply Chain Integrity Rate.
- Control failure rate for each control.
- Deployment lead time.
- MTTD, Mean Time to Triage, MTTC and MTTR.
- False-Positive Rate.

The pipeline **refuses untrustworthy evidence**: edited records, or gaps in run IDs. It **reports**, rather than hides, any target that is missed.

## What You Will Learn
- Turn pipeline evidence into Layer 2 metrics with the book's definitions.
- Spot the most common gaming patterns, deleting "flaky" failures and editing timestamps, and make them fail loudly.
- Separate *evidence integrity* (a build failure) from *missed targets* (a programme finding).

## Prerequisites
**Required:** LAB-00; LAB-16 recommended; Chapter 35 §35.2–35.3.
**Optional:** Python 3.12+ to run the pipeline locally.

## Estimated Time
**35–45 minutes**

## Difficulty
Intermediate

## Architecture
```
evidence/pipeline-runs.jsonl ─┐                ┌─ integrity: record_sha256 matches · run IDs contiguous ─▶ FAIL if not
evidence/incidents.jsonl ─────┼─▶ tools/metrics.py
metrics-targets.yaml ─────────┘                └─ Table 35.2 metrics ─▶ targets met / missed ─▶ out/metrics.md + .json
```

## Step 1 — Create or Open the Repository
```bash
bash shared/scripts/start-lab.sh chapter-35/lab-30-metrics-from-evidence ~/dt-labs/dt-lab-30
```
Create an empty **public** repository named `dt-lab-30`.

## Step 2 — Clone the Repository
```bash
cd ~/dt-labs/dt-lab-30
git remote add origin https://github.com/<your-username>/dt-lab-30.git
git push -u origin main
```

## Step 3 — Build the Lab
Read one pipeline-run record and one incident record. `tools/make_evidence.py` shows how they were generated and sealed. Compare each metric in `tools/metrics.py` with its Table 35.2 definition. For example, MTTD runs from the *earliest indicator* to the alert, and only true positives count.

**Why it matters for DevSecOps:** a metric is only as credible as its evidence. If the numbers can be edited, the board is reading opinions.

## Step 4 — Implement the Security Control
`.github/workflows/metrics.yml` runs the tests, verifies the evidence, computes the metrics and publishes them to the run summary and as an artifact.

## Step 5 — Run the Pipeline
Push to `main`. Expected: `5 passed`, and every target met. Adoption is 90.0%, supply chain integrity 88.9%, MTTD 21.0 minutes, MTTC 36.2 minutes and the false-positive rate 37.5%. The SCA control failure rate is 7.5%.

## Step 6 — Inspect the Result
Open **Actions → metrics → (run) → Summary**. Download `security-metrics` and look at `metrics.json`. Its structure suits a dashboard or the §35.2 translation to outcome and risk metrics.

## Step 7 — Introduce a Deliberate Failure
On a branch named `quarterly-report`, apply `lab-changes/apply-failures.md` (INTENTIONALLY MISLEADING). It deletes the three failed SCA runs and makes INC-001's detection look instant. Push and open a pull request.

## Step 8 — Observe the Control
Verified locally:
```
untrustworthy evidence: record INC-001 was modified after it was sealed
untrustworthy evidence: pipeline run IDs missing from the evidence: [7, 19, 26]
```
Without these checks, the SCA failure rate would have dropped from 7.5% to 0.0%, as the unit test `test_deleting_failed_runs_is_detected` shows. That is the "metric gaming" anti-pattern in §35.6.

## Step 9 — Remediate the Finding
Restore the original evidence files. If runs really were flaky, record the root cause as a *new* field in a *new* run. Never delete or edit sealed history.

## Step 10 — Validate the Fix
### Expected Result
- Evidence verifies and the metrics are published. Any missed target appears as **no** in the summary for the programme to act on.

## Step 11 — Cleanup
Delete the branch and, if you want, the repository. No cloud resources.

## What You Should Have Learned
Compute metrics from sealed evidence, make gaming fail the build, and publish missed targets honestly. Credible metrics come from evidence integrity, not from good-looking numbers.

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
A self-hash stops casual edits, but not someone who re-seals a record. Close that gap the way LAB-16 does. Attest each day's evidence file in CI with `actions/attest` (pinned in `docs/action-pins.md`), and verify the attestations with `gh attestation verify` before computing the metrics.

---
**Validation status:** executed locally on 1 Oct 2026 (Python 3.11, pytest 9.0.3): 5/5 tests pass, baseline metrics as stated, and the Step 8 findings are reproduced. actionlint and zizmor report no findings. **EXECUTION VALIDATION REQUIRED** on a GitHub-hosted runner.
