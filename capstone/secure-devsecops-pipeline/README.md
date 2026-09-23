# CAPSTONE LAB — Build a Secure DevSecOps Pipeline

| Chapters | Level | Difficulty | Estimated time | Cloud required? |
|---|---|---|---|---|
| Parts I–IV integrated (Ch. 4, 9–14, 16–19) with evidence for Part VII (Ch. 35) | 4 — Capstone | Advanced | 3–4 hours (can be split into three sessions) | No (GitHub + GHCR). Optional AWS/Azure extensions |

## Scenario
You are the platform security lead for *dt-orders-api*, a customer-facing orders service. After an audit finding ("security checks exist but are not enforced, not evidenced and can be bypassed"), the CISO asks you to deliver **one governed pipeline** that a regulator, an auditor and an engineer can all trust:
- no change reaches production without passing defined security controls;
- the artefact that runs is provably the artefact that was built and scanned;
- every run produces tamper-evident evidence mapped to NIST CSF 2.0 and ISO/IEC 27001:2022;
- AI-assisted changes and agent tooling are governed by the same machinery (optional extension).

## Objectives
By the end you will have a repository in which:
1. Seven independent PR-stage controls run in parallel (threat model, workflow lint, secrets, SAST, SCA, tests, Kubernetes policy).
2. A build stage verifies artefact properties, runs DAST against the running container, scans the image and generates an SBOM.
3. On `main`, the image is published **by digest**, with **provenance and SBOM attestations** and a **keyless signature**.
4. A **policy decision** (OPA) over all job results authorises release.
5. Staging deployment **verifies** attestations and signature before proceeding; production requires **human approval**.
6. An **evidence record** is produced for every run, hashed, attested and retained for 90 days.

## Architecture
```
Developer ─▶ GitHub (ruleset: PR + required checks + signed commits)
   └─ Pull request
        ├─ threat_model   (LAB-01)   ├─ sast       (LAB-05)   ├─ k8s_policy (LAB-10)
        ├─ workflow_lint  (LAB-04)   ├─ sca        (LAB-06)
        ├─ secrets        (LAB-03)   └─ tests      (LAB-00)
        ▼
   build_scan (LAB-09/11/12/13): build → non-root & no-secret gates → run hardened container → ZAP baseline
                                 → Trivy (vuln+secret) → SBOM → [main] push by digest → attest provenance + SBOM → cosign sign
        ▼
   release_decision (LAB-14): OPA over toJSON(needs) ─▶ allow?
        ├─ evidence (LAB-16, always): mapped controls → sha256 → attestation → artifact (90 days)
        ▼
   deploy_staging  : gh attestation verify (provenance, SBOM) + cosign verify identity ─▶ deploy (simulated)
   deploy_production: environment approval (main only) ─▶ deploy (simulated)
        ▼
   Security feedback: Code scanning alerts, job summary evidence table, Dependabot PRs, run history
```
`[FIGURE REQUIRED — CREATE ORIGINAL: Capstone pipeline swimlane mapped to the four SFRA control surfaces (Chapter 9)]`

## Prerequisites
**Required:** LAB-00 to LAB-16 completed or understood (each task reuses one); a free GitHub account; Git; an editor.
**Optional:** Docker locally; `gh` CLI ≥ 2.49 and Cosign for manual verification; a collaborator for review steps.

## Repository
```bash
bash shared/scripts/start-lab.sh capstone/secure-devsecops-pipeline ~/dt-labs/dt-capstone
cd ~/dt-labs/dt-capstone
git remote add origin https://github.com/<your-username>/dt-capstone.git
git push -u origin main
```
Create the repository as **public** (attestations, rulesets and dependency review are free on public repositories). The starter contains every policy, rule, test and tool from earlier labs; `.github/workflows/secure-pipeline.yml` contains Task 1 and a task list.

**Repository settings to configure**
- **Environments:** `staging` (no rules), `production` (required reviewer: you; deployment branches: `main`).
- **Ruleset on `main`** (LAB-02): PR required, required checks = all seven PR-stage jobs + `build_scan` + `release_decision`, signed commits, no force push, no deletion, empty bypass list.
- **Advanced Security:** secret scanning + push protection on; Dependabot alerts and security updates on.
- Edit `.github/CODEOWNERS` with your username.

## Tasks
| Task | Build | Reference |
|---|---|---|
| 1 | `threat_model` job (provided) | LAB-01 |
| 2 | `workflow_lint`: actionlint + zizmor, fail on medium+ | LAB-04 |
| 3 | `secrets`: checksum-verified gitleaks, full history | LAB-03 |
| 4 | `sast`: Semgrep with `.semgrep/` | LAB-05 |
| 5 | `sca`: dependency-review (PR) + pip-audit | LAB-06 |
| 6 | `tests`: pytest | LAB-00 |
| 7 | `k8s_policy`: Kyverno test + apply | LAB-10 |
| 8 | `build_scan` as in the architecture | LAB-09, 11, 12, 13 |
| 9 | `release_decision` with `policy/release` | LAB-14 |
| 10 | `evidence` with `tools/pipeline_evidence.py` | LAB-16 |
| 11 | `deploy_staging` (verify-before-deploy) and `deploy_production` (approval) | LAB-13, LAB-14 |

Rules for your implementation: every third-party action pinned to a full SHA; `permissions: {}` at workflow level and minimal per job; no secrets other than the automatic `GITHUB_TOKEN`; every downloaded binary checksum-verified.

## Security Controls Implemented
| Control | Threat addressed | Chapter |
|---|---|---|
| Threat-model completeness gate | Unanalysed trust boundaries | 4 |
| Rulesets, signed commits, CODEOWNERS | Unreviewed/unattributable change | 10 |
| Workflow lint | Pipeline injection, excessive token rights, mutable dependencies | 11 |
| Secret scanning (3 layers) | Credential exposure | 10 |
| SAST, SCA, tests | Vulnerable code and components | 13, 19 |
| Kubernetes admission policy (shift-left) | Privileged / mutable workloads | 14 |
| Artefact gates, DAST, image scan, SBOM | Insecure runtime artefact | 13, 14, 19 |
| Digest + provenance + SBOM attestation + signature | Artefact substitution / tampering | 11, 13 |
| Policy decision + environments | Unauthorised release | 11, 17 |
| Evidence record + attestation | Unprovable compliance | 18, 35 |

## Expected Results
On a clean push to `main` (EXECUTION VALIDATION REQUIRED — the complete workflow has been statically validated and its PR-stage controls executed locally; the build, publish, attestation and deploy stages have not been run on GitHub):
- All seven PR-stage jobs green; `build_scan` green with a pushed digest; `release_decision` prints `[]` violations and `allow=true`.
- `evidence` job summary shows an 8-row table, **Overall: PASS**, and an evidence SHA-256.
- `deploy_staging` verifies two attestations and one signature, then deploys; `deploy_production` waits for your approval.

## Failure Conditions (run each; each must stop the release)
| # | Inject | Expected stop point |
|---|---|---|
| F1 | Add DF6/DF7 agent flows without threats (LAB-01 Step 7) | `threat_model` fails → decision `required check 'threat_model' is failure` |
| F2 | Put `${{ github.event.pull_request.title }}` in a `run:` step | `workflow_lint` fails (template-injection) |
| F3 | `bash scripts/make-test-secret.sh` then commit the file with `--no-verify` | push protection and/or `secrets` job |
| F4 | f-string SQL in `app/app.py` | `sast` and `tests` fail |
| F5 | `PyYAML==5.3.1` | `sca` fails |
| F6 | `hostNetwork: true` in `k8s/deployment.yaml` | `k8s_policy` fails (PSS restricted) |
| F7 | Remove `USER 10001:10001` from `app/Dockerfile` | `build_scan` fails at the non-root gate |
| F8 | Comment out `@app.after_request` | `build_scan` fails at ZAP (10021/10038) |
| F9 | Verify an image digest not produced by this workflow | `deploy_staging` verification fails |
| F10 | Edit a downloaded `evidence.json` | `verify_evidence.py` integrity failure |

For every failure the `evidence` job still runs and records `FAIL` for the relevant control — failures are evidence too.

## Remediation
Revert each injected change using the remediation steps of the referenced lab; never weaken a gate, threshold or policy to make a run pass. Genuine exceptions go through a reviewed, expiring mechanism (VEX for vulnerabilities, Kyverno `PolicyException`, Azure/AWS policy exemptions).

## Validation
| Check | Pass criterion |
|---|---|
| Pipeline integrity | All actions SHA-pinned; `zizmor --min-severity medium` clean |
| Enforcement | F1–F10 each blocked at the stated point |
| Provenance | `gh attestation verify oci://ghcr.io/<you>/dt-capstone@<digest> --repo <you>/dt-capstone` succeeds |
| Signature identity | `cosign verify … --certificate-identity https://github.com/<you>/dt-capstone/.github/workflows/secure-pipeline.yml@refs/heads/main --certificate-oidc-issuer https://token.actions.githubusercontent.com` succeeds |
| Evidence | Latest `evidence.json` verifies (`verify_evidence.py` and `gh attestation verify evidence.json`) |
| Approval | Production deployment shows your approval in **Deployments** |

## Cleanup
- **Profile → Packages → dt-capstone → Delete package** (image, signatures, attestations).
- Delete environments and the ruleset if reusing the repository; delete the repository when finished.
- If you completed a cloud extension, run that lab's cleanup section in full.

## Extension Challenges
1. **Real deployment:** add a `kind` cluster to `deploy_staging` (`helm/kind-action`), install Kyverno with a `verifyImages` rule for your workflow identity, and deploy the verified digest.
2. **Cloud target:** replace the simulated deploy with AWS-LAB-01's OIDC role (push to ECR) or AZ-LAB-01's managed identity (deploy Bicep).
3. **AI governance:** add LAB-15's AI-assisted PR gate and LAB-18's agent allowlist tests as required checks.
4. **Metrics for the board (Chapter 35):** aggregate 30 days of evidence artefacts into lead time, change-failure rate by control, and mean time to remediate.

## Capstone Completion Checklist
- [ ] Repository created and settings configured
- [ ] Tasks 1–11 implemented
- [ ] Pipeline executed end to end on `main`
- [ ] Failure conditions F1–F10 triggered and observed
- [ ] Findings remediated
- [ ] Pipeline passed with evidence Overall: PASS
- [ ] Provenance, SBOM attestation and signature verified manually
- [ ] Resources cleaned up
