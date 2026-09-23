# LAB-16 — Compliance as Code: A Hashed, Attested, Framework-Mapped Evidence Pipeline

| Chapter | Level | Difficulty | Estimated time | Cloud required? |
|---|---|---|---|---|
| Chapter 18 — Compliance as Code (§18.4 Unified Control Mapping, §18.7 Evidence Pipeline) | 3 — Advanced | Advanced | 50–60 minutes | No |

## What You Will Build
A pipeline that runs four technical controls (dependency audit, secret scan, IaC scan, security regression tests), maps each result to **NIST CSF 2.0**, **ISO/IEC 27001:2022 Annex A** and the **Essential Eight**, writes a single evidence record with a **SHA-256 integrity hash**, **attests** it with Sigstore-backed GitHub artifact attestations, retains it for 90 days — and then gates on the blocking controls.

## What You Will Learn
- Implement "one control, many frameworks" as a version-controlled mapping.
- Produce evidence even when a control fails — auditors need the failures too.
- Detect evidence tampering by recomputing the hash; bind evidence to the producing workflow with an attestation.
- Explain the difference between a *compliance gate* and *compliance evidence*.

## Prerequisites
**Required:** LAB-03, LAB-06, LAB-07; Chapter 18 §18.1, §18.4, §18.7.
**Optional:** Python 3.12+ locally.

> **Mapping caution.** Framework references in `controls/mapping.yaml` are the author's interpretive mappings (NIST CSF 2.0 `ID.RA-01`, `PR.AA-01`, `PR.PS-01`, `PR.PS-06`; ISO/IEC 27001:2022 `A.5.17`, `A.8.8`, `A.8.9`, `A.8.28`, `A.8.29`; Essential Eight *Patch applications*). Confirm them with your GRC function before using the evidence in an audit. A passing pipeline control does not by itself demonstrate an Essential Eight maturity level.

## Estimated Time
**50–60 minutes**

## Difficulty
Advanced

## Architecture
```
push / PR / weekly ─▶ pip-audit ─┐
                     gitleaks  ──┤ raw results/ ─▶ build_evidence.py + controls/mapping.yaml
                     checkov   ──┤                   └▶ evidence.json {controls[], frameworks, commit, run_url, sha256}
                     pytest    ──┘                          ├─ verify_evidence.py (hash)
                                                            ├─ actions/attest (Sigstore, workflow identity)  [not on PRs]
                                                            ├─ artifact "evidence-<run>" (90 days)
                                                            └─ gate: blocking controls must PASS
```

## Step 1 — Create or Open the Repository
```bash
bash shared/scripts/start-lab.sh chapter-18/lab-16-compliance-evidence-pipeline ~/dt-labs/dt-lab-16
```
Create an empty **public** repository `dt-lab-16` (attestations on private repositories require GitHub Enterprise Cloud).

## Step 2 — Clone the Repository
```bash
cd ~/dt-labs/dt-lab-16
git remote add origin https://github.com/<your-username>/dt-lab-16.git
git push -u origin main
```

## Step 3 — Build the Lab
Read `controls/mapping.yaml` and `tools/build_evidence.py`. Note: a control whose tool produced no output is `NOT_RUN` and **fails** — silence is not compliance.

## Step 4 — Implement the Security Control
The workflow `evidence.yml` is the control. Its ordering is deliberate: collect → record → verify → attest → retain → **then** gate.

## Step 5 — Run the Pipeline
Expected (verified locally against a fresh lab repository):
```
DT-VULN-01    PASS  findings=0 {'nist_csf_2': ['ID.RA-01'], 'iso27001_2022': ['A.8.8'], 'essential_eight': ['Patch applications']}
DT-SECRET-01  PASS  findings=0 ...
DT-IAC-01     PASS  findings=0 ...
DT-TEST-01    PASS  findings=0 ...
OVERALL: PASS  sha256=<64 hex characters>
```

## Step 6 — Inspect the Result
Download artifact `evidence-<run id>`; open `evidence.json`. On `main`, open the attestation linked from the run summary and note the subject digest. Verify locally:
```bash
gh attestation verify evidence.json --repo <you>/dt-lab-16
python tools/verify_evidence.py evidence.json
```

## Step 7 — Introduce Deliberate Failures
> **Intentionally non-compliant change — lab use only.**
1. **Control failure:** on branch `old-yaml`, set `PyYAML==5.3.1` in `app/requirements.txt`, push, open a PR.
2. **Evidence tampering:** download a passing `evidence.json`, change `"overall": "PASS"` to anything else — or change a finding count — and run `python tools/verify_evidence.py evidence.json`.

## Step 8 — Observe the Security Control
- Control failure: `DT-VULN-01  FAIL  findings=2 …` and `OVERALL: FAIL` (verified locally); the artifact **is still uploaded**; the final gate step fails.
- Tampering: `::error::EVIDENCE INTEGRITY FAILURE — record modified after generation` (verified locally); `gh attestation verify` also fails because the file digest no longer matches the attested subject.
Threat → Detection → Finding → Decision: non-compliant build or falsified evidence → mapped control / hash + attestation → specific control ID and framework references → block and investigate.

## Step 9 — Remediate the Finding
Upgrade PyYAML to `6.0.3`, push, and let the pipeline regenerate evidence. Never edit evidence — regenerate it.

## Step 10 — Validate the Fix
### Expected Result
- `OVERALL: PASS`; integrity verified; attestation verifies on `main`.
- The failed run's evidence remains in the run history — the audit trail shows the failure *and* the fix.

## Step 11 — Cleanup
Artifacts expire after 90 days (delete sooner from the run page if you wish). Delete branches; optionally delete the repository.

## What You Should Have Learned
Continuous compliance is a data pipeline: controls produce results, mappings translate them, hashes and attestations make them trustworthy, and gates act on them. Point-in-time screenshots become unnecessary.

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
Add an `evidence-index.json` job on `main` that appends each run's `sha256` to the previous index entry's hash (a simple hash chain) and publishes it to a separate, write-protected branch.

---
**Validation status:** 4/4 builder unit tests pass; end-to-end executed locally with pip-audit 2.10.1, gitleaks 8.28.0, Checkov 3.3.19 and pytest (PASS, then FAIL with PyYAML 5.3.1); tamper detection verified. Attestation step not executed. **EXECUTION VALIDATION REQUIRED.**
