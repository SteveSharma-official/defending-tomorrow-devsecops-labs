# LAB-03 — Secret Detection in Depth: Workstation, Platform and Pipeline

| Chapter | Level | Difficulty | Estimated time | Cloud required? |
|---|---|---|---|---|
| Chapter 10 — Git Security Engineering (§10.5 Secret Scanning Defence in Depth) | 1 — Foundations | Beginner | 40–50 minutes | No |

## What You Will Build
The three secret-scanning layers of Chapter 10, Figure 10.4 on one repository: a **pre-commit hook** (Layer 1, bypassable), **GitHub push protection** (Layer 2, server-side) and a **CI history scan** with results in code scanning (Layer 3, catches what the first two miss).

## What You Will Learn
- Install and operate a gitleaks pre-commit hook and demonstrate how `--no-verify` bypasses it.
- Enable GitHub secret scanning and push protection on a public repository.
- Scan full git history in CI, verify the scanner's download checksum and publish SARIF findings.
- Explain why deleting a secret in a later commit is not remediation.

## Prerequisites
**Required:** LAB-00; Python 3.9+ with `pip install pre-commit`.
**Optional:** gitleaks installed locally (`gitleaks version`).

> **Safety note.** The lab uses `scripts/make-test-secret.sh`, which generates a **random, synthetic** AWS-format key pair that is not associated with any account. Never use a real credential. The widely published AWS documentation example key (`AKIAIOSFODNN7EXAMPLE`) is allow-listed by gitleaks and will **not** trigger detection — verified with gitleaks 8.28.0 — so the Chapter 10 manuscript lab's Attack 4 does not behave as described with that value.

## Estimated Time
**40–50 minutes**

## Difficulty
Beginner

## Architecture
```
Layer 1  workstation   git commit ──▶ pre-commit: gitleaks --staged     (bypass: --no-verify)
Layer 2  platform      git push   ──▶ GitHub push protection            (server-side block, supported patterns)
Layer 3  pipeline      push / PR  ──▶ Actions: gitleaks git (full history) ──▶ SARIF ──▶ Security → Code scanning
```

## Step 1 — Create or Open the Repository
```bash
bash shared/scripts/start-lab.sh chapter-10/lab-03-secret-detection-in-depth ~/dt-labs/dt-lab-03
```
Create an empty **public** repository `dt-lab-03`.

## Step 2 — Clone the Repository
```bash
cd ~/dt-labs/dt-lab-03
git remote add origin https://github.com/<your-username>/dt-lab-03.git
git push -u origin main
```

## Step 3 — Build the Lab
**Layer 1 — install the hook**
```bash
pip install pre-commit
pre-commit install          # writes .git/hooks/pre-commit
pre-commit run --all-files  # expect: Detect hardcoded secrets.....Passed
```
*Why it matters:* the cheapest place to stop a secret is before it is ever written to history.

**Layer 2 — enable push protection**
**Repository → Settings → Advanced Security** (older UI: *Code security and analysis*) → enable **Secret Protection / Secret scanning** and **Push protection**. Both are available at no cost on public repositories (VERIFY CURRENT PRODUCT BEHAVIOUR — GitHub renamed and repackaged these features in 2025).

## Step 4 — Implement the Security Control
Layer 3 is `.github/workflows/secret-scan.yml`. Note three deliberate design choices:
1. `fetch-depth: 0` — history, not just the tip, is scanned.
2. The gitleaks binary is verified against its published SHA-256 before it runs — the scanner is itself part of your supply chain.
3. Findings are uploaded as SARIF to **Security → Code scanning**, so they are tracked, not buried in logs.

## Step 5 — Run the Pipeline
The initial push already ran `secret-scan`. Expected: *Scan git history* reports `no leaks found`.

## Step 6 — Inspect the Result
**Actions → secret-scan → gitleaks** (green). **Security → Code scanning**: no gitleaks alerts.

## Step 7 — Introduce a Deliberate Security Failure
> **Intentionally insecure — synthetic value only.**
```bash
git switch -c leak-test
bash scripts/make-test-secret.sh config/test-credentials.env
git add config/test-credentials.env
git commit -m "LAB-03: add synthetic credential"      # Layer 1 should BLOCK this
git commit --no-verify -m "LAB-03: bypass the hook"  # simulates a developer bypass
git push -u origin leak-test                         # Layer 2 may block this
```
If push protection blocks the push, read the message, then (for the purpose of observing Layer 3 only) follow the link it provides and choose **It's used in tests** to allow it. Then push again and open a pull request.

## Step 8 — Observe the Security Control
| Layer | Expected observation |
|---|---|
| 1 | `Detect hardcoded secrets....Failed` with the file and rule `aws-access-token` |
| 1 bypass | `--no-verify` commit succeeds locally — the hook is advisory |
| 2 | Push rejected with `GH013` / "Push cannot contain secrets" **if** GitHub recognises the pattern. Synthetic keys may not be classified as high-confidence; record what you observe (VERIFY CURRENT PRODUCT BEHAVIOUR) |
| 3 | `secret-scan` fails with `leaks found`; **Security → Code scanning** lists the finding with file and commit |

Threat → Detection → Finding → Decision: exposed credential → gitleaks rule → alert with location → block merge and treat the credential as compromised.

## Step 9 — Remediate the Finding
1. **Assume compromise.** For a real secret: revoke and rotate it at the provider *first*. Removing it from Git does not un-leak it.
2. Remove the file from the branch history. Because the leak exists only on your feature branch, rebuild the branch without it:
```bash
git switch main
git branch -D leak-test
git push origin --delete leak-test
```
3. Close the pull request. In **Security → Code scanning**, dismiss the alert as *Used in tests* with a comment.
If a secret ever reaches `main`, history rewriting (for example `git filter-repo`) and contacting GitHub Support to purge cached views may be required — rotation remains mandatory.

## Step 10 — Validate the Fix
### Expected Result
- `main` is clean: a manual run of `secret-scan` (**Actions → secret-scan → Run workflow**) passes.
- `pre-commit run --all-files` passes.
- No open secret-scanning or code-scanning alerts remain (or they are dismissed with justification).

## Step 11 — Cleanup
Delete `config/test-credentials.env` locally, delete test branches and optionally the repository. No cloud resources were used.

## What You Should Have Learned
Each layer fails differently: the hook can be skipped, push protection covers only supported patterns, and history scanning finds leaks after the fact. Defence in depth plus rotation — not deletion — is the control.

## Lab Completion Checklist
- [ ] Repository created
- [ ] Code committed
- [ ] Pipeline executed
- [ ] Security control triggered (all three layers attempted)
- [ ] Finding identified
- [ ] Finding remediated (credential treated as compromised)
- [ ] Pipeline passed
- [ ] Resources cleaned up

## Further Challenge
Add a custom gitleaks rule (`.gitleaks.toml`, extending the default config) that detects your organisation's internal token format, for example `dtl_[a-z0-9]{32}`, and prove it with a synthetic value.

---
**Validation status:** gitleaks 8.28.0 executed locally: synthetic key → 2 findings, SARIF produced; AWS documentation key → 0 findings. Download checksum matched the official release checksums file. Workflow checked with actionlint and zizmor. Push-protection behaviour not verified. **EXECUTION VALIDATION REQUIRED.**
