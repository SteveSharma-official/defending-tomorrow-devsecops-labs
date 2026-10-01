# LAB-23 — Verified Recovery: Restore the Last Known-Good, Signed and Attested Image

| Chapter | Level | Difficulty | Estimated time | Cloud required? |
|---|---|---|---|---|
| Chapter 26 — Cyber Resilience Engineering (§26.4 Recovery Engineering, §26.4.2 Recovery Automation and Runbook-as-Code) · builds on LAB-13 | 3 — Advanced | Advanced | 45–60 minutes | No (GHCR) |

## What You Will Build
A recovery decision pipeline with three parts:
1. **Target selection.** Pick the newest release that is signed, has verified provenance, passed the vulnerability gate **and was built before the compromise window began**.
2. **A runbook gate.** Recovery must isolate traffic, verify the signature and provenance, deploy **by digest**, and pass a health gate before traffic returns.
3. **A manual verify job.** Prove the chosen digest with `cosign verify` and `gh attestation verify` against the image you built in LAB-13.

## What You Will Learn
- Why "roll back to the latest signed image" can restore the attacker's build.
- How to express runbook-as-code ordering rules (§26.4.2) as a testable gate.
- How to verify a restore target cryptographically before it receives traffic.

## Prerequisites
**Required:** LAB-00; **LAB-13** completed (for the verify job); Chapter 26 §26.4.
**Optional:** Python 3.12+ to run the gate locally.

## Estimated Time
**45–60 minutes**

## Difficulty
Advanced

## Architecture
```
recovery/incident.yaml (compromise_window_start) ─┐
recovery/release-ledger.json ─────────────────────┼─▶ select_recovery_target.py ─▶ 1.4.1 @ sha256:…
recovery/recovery-policy.yaml ────────────────────┘                                   │
recovery/recovery-runbook.yaml ─▶ check_runbook.py (R1 verify→deploy, R2 digest, R3 health, R4 isolate)
manual run ─▶ cosign verify <image>@<digest> + gh attestation verify ─▶ "restore target approved"
```

## Step 1 — Create or Open the Repository
```bash
bash shared/scripts/start-lab.sh chapter-26/lab-23-verified-recovery ~/dt-labs/dt-lab-23
```
Create an empty **public** repository named `dt-lab-23`.

## Step 2 — Clone the Repository
```bash
cd ~/dt-labs/dt-lab-23
git remote add origin https://github.com/<your-username>/dt-lab-23.git
git push -u origin main
```

## Step 3 — Build the Lab
Read `recovery/incident.yaml`. In this scenario a stolen CI credential let the attacker push a change that the pipeline **built, signed and attested normally** as release 1.5.0. Then read the ledger and the policy. To run the verify job later, replace the synthetic digests in the ledger with real digests from your LAB-13 image: **GitHub → your profile → Packages → dt-lab-13 → versions**.

**Why it matters for DevSecOps:** a signature and provenance prove *where and how* an image was built. They don't prove the source was trustworthy. Recovery has to use the incident timeline as well.

## Step 4 — Implement the Security Control
`.github/workflows/recovery.yml`:
- `gate` (every pull request): the runbook check, target selection and unit tests.
- `verify-target` (manual): selects the target, installs cosign by pinned SHA, and verifies both the signature (identity bound to your LAB-13 workflow) and the SLSA provenance.

## Step 5 — Run the Pipeline
Push to `main`. Expected: `0 finding(s)`; `rejected 1.5.0: built inside the compromise window`; `rejected 1.4.2: signature not verified, provenance not verified`; chosen `1.4.1`; `4 passed`.

## Step 6 — Inspect the Result
After putting real digests in the ledger, run **Actions → recovery → Run workflow** with your image and source repository. The log shows `signature verified`, the provenance verification output, and `Restore target approved — 1.4.1 (sha256:…)`.

## Step 7 — Introduce a Deliberate Security Failure
On a branch named `quick-restore`, apply `lab-changes/apply-failures.md` (INTENTIONALLY INSECURE). It turns off the compromise-window rule, removes both verify steps and deploys `:latest`. Push and open a pull request.

## Step 8 — Observe the Security Control
Verified locally:
- `R1 deploy-known-good: deploys before signature and provenance are verified`
- `R2 deploy-known-good: image referenced by tag (…:latest) — use the verified digest`
- Target selection now returns **1.5.0, the attacker's build**, and `test_restore_target_is_last_verified_build_before_compromise` fails (`3 failed, 1 passed`).

Threat → Detection → Finding → Decision: re-infection through recovery → runbook and selection tests → named findings → pull request blocked.

## Step 9 — Remediate the Finding
Restore `exclude_builds_after_compromise_start: true`, both verify steps and the digest reference.

## Step 10 — Validate the Fix
### Expected Result
- `0 finding(s)`, target `1.4.1` and `4 passed`. With real digests, the manual verify job ends with `Restore target approved`.

## Step 11 — Cleanup
No resources are created. Delete the branch and, if you want, the repository. Keep your LAB-13 images if you plan to do LAB-27.

## What You Should Have Learned
Recovery is a security decision. A restore target must be cryptographically verified **and** predate the compromise. Runbooks should make that order impossible to skip.

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
Add an RTO check. Record timestamps for detection, decision, verification and traffic restoration in a `recovery-log.json`, then fail the gate if the measured recovery time exceeds the RTO in `recovery-policy.yaml`. Section 26.4.1 says detection time must be included.

---
**Validation status:** gate executed locally on 1 Oct 2026 (Python 3.11, pytest 9.0.3): 4/4 tests pass and the Step 8 findings are reproduced. actionlint and zizmor report no findings. **EXECUTION VALIDATION REQUIRED** for the `verify-target` job against a real LAB-13 image (cosign and `gh attestation verify` were not run in the validation environment).
