# LAB-11 — DAST in the Pipeline: OWASP ZAP Baseline Against a Running Build

| Chapter | Level | Difficulty | Estimated time | Cloud required? |
|---|---|---|---|---|
| Chapter 19 — Security Testing at Scale (**to be completed**; introduced in Chapter 11 §11.4 meanwhile); Chapter 3 (shift everywhere) | 2 — Practitioner | Intermediate | 35–45 minutes | No |

## What You Will Build
A workflow that starts the sample API on the GitHub-hosted runner and runs the **OWASP ZAP baseline scan** against it. A rules file promotes selected findings (missing security headers) to build-breaking failures, while documented, expected findings are ignored.

## What You Will Learn
- Explain what DAST observes that SAST and SCA cannot (runtime behaviour, headers, configuration).
- Run a passive ZAP baseline scan in CI safely, against an ephemeral target you own.
- Tune DAST with a rules file: `FAIL`, `WARN`, `IGNORE` — and justify each decision.
- Remediate a runtime finding in code and verify it dynamically.

## Prerequisites
**Required:** LAB-00; LAB-05 recommended.
**Optional:** Docker to run ZAP locally (`ghcr.io/zaproxy/zaproxy:stable`).

> **Legal and ethical note.** Scan only applications you own or are explicitly authorised to test. This lab scans a copy of the sample app running on your own disposable runner.

## Estimated Time
**35–45 minutes**

## Difficulty
Intermediate

## Architecture
```
runner VM ─┬─ gunicorn dt-orders-api :8080 (ephemeral)
           └─ ZAP baseline container ──spider + passive rules──▶ http://localhost:8080
                    │ .zap/rules.tsv: 10020/10021/10038 → FAIL, 10049 → IGNORE (with reason)
                    ▼
           job result + HTML/JSON/MD report artifact "zap-baseline-report"
```

## Step 1 — Create or Open the Repository
```bash
bash shared/scripts/start-lab.sh chapter-19/lab-11-dast-zap-baseline ~/dt-labs/dt-lab-11
```
Create an empty **public** repository `dt-lab-11`.

## Step 2 — Clone the Repository
```bash
cd ~/dt-labs/dt-lab-11
git remote add origin https://github.com/<your-username>/dt-lab-11.git
git push -u origin main
```

## Step 3 — Build the Lab
Read `.github/workflows/dast.yml` and `.zap/rules.tsv`. **Why it matters:** DAST tests the deployed behaviour — the thing an attacker actually touches. A header set in code but stripped by a proxy is invisible to SAST and obvious to DAST.

## Step 4 — Implement the Security Control
The control is the ZAP baseline step with `fail_action: true` plus the rules file. `allow_issue_writing: false` keeps the job read-only (the action can otherwise open GitHub issues, which would need `issues: write`).

## Step 5 — Run the Pipeline
Expected on the baseline app: ZAP reports `FAIL-NEW: 0` and the job passes (EXECUTION VALIDATION REQUIRED — the exact PASS/WARN counts depend on the ZAP version).

## Step 6 — Inspect the Result
**Actions → dast → zap-baseline** → log summary. Download the **zap-baseline-report** artifact (bottom of the run page) and open the HTML report.

## Step 7 — Introduce a Deliberate Security Failure
> **Intentionally weakened code — lab use only.**
```bash
git switch -c drop-headers
```
In `app/app.py`, comment out the `@app.after_request` decorator line above `def security_headers(...)` so the headers are no longer applied. Commit, push, open a pull request.

## Step 8 — Observe the Security Control
Expected: the job fails with `FAIL-NEW` entries for **10021** *X-Content-Type-Options Header Missing*, **10038** *Content Security Policy (CSP) Header Not Set* and, where ZAP classifies the response as HTML-framable, **10020** *Missing Anti-clickjacking Header*.
Threat → Detection → Finding → Decision: MIME-sniffing / clickjacking / content-injection exposure → passive response analysis → alert IDs with URLs → build fails per the rules file.

`[SCREENSHOT REQUIRED — ZAP BASELINE HTML REPORT SHOWING FAIL-NEW ALERTS 10021 AND 10038]`

## Step 9 — Remediate the Finding
Restore the `@app.after_request` decorator. Commit and push.

## Step 10 — Validate the Fix
### Expected Result
- The job passes; the report shows the headers present.
- Locally: `curl -sI http://127.0.0.1:8080/health` lists `X-Content-Type-Options: nosniff` and `Content-Security-Policy: default-src 'none'; frame-ancestors 'none'`.

## Step 11 — Cleanup
The target existed only on the runner. Delete branches; optionally delete the repository and downloaded reports.

## What You Should Have Learned
DAST closes the gap between "the code says" and "the service does". Rules files make DAST a gate without drowning teams in informational alerts — every IGNORE needs a reason.

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
Generate an OpenAPI description for the API and run `zaproxy/action-api-scan` (active API scan) against the ephemeral target. Compare its findings with the baseline scan.

---
**Validation status:** workflow checked with actionlint/zizmor; action SHA resolved from the upstream tag. ZAP scan **not** executed; alert IDs are ZAP's documented passive-rule IDs (VERIFY CURRENT PRODUCT BEHAVIOUR). **EXECUTION VALIDATION REQUIRED.**
