# LAB-04 — Harden GitHub Actions: Injection, Permissions and Pinning

| Chapter | Level | Difficulty | Estimated time | Cloud required? |
|---|---|---|---|---|
| Chapter 11 — Secure CI/CD Architectures (§11.1 Threat Model, §11.4 Hardening the Build Environment) | 2 — Practitioner | Intermediate | 45–60 minutes | No |

## What You Will Build
A repository containing a deliberately weak workflow and a **workflow security linter gate** (actionlint + zizmor) that reports findings to code scanning and blocks merges. You will exploit the weakness with nothing more than a pull-request title, then harden the workflow until the gate passes.

## What You Will Learn
- Recognise and exploit **template (script) injection** in a GitHub Actions `run:` block.
- Replace `permissions: write-all` with job-scoped least privilege.
- Pin third-party actions to full commit SHAs and explain why tags are insufficient.
- Operate a CI gate that lints the pipeline itself.

## Prerequisites
**Required:** LAB-00; Chapter 11 §11.1–11.4.
**Optional:** `pip install zizmor actionlint-py` to lint locally.

## Estimated Time
**45–60 minutes**

## Difficulty
Intermediate

## Architecture
```
PR title (attacker-controlled) ──▶ pr-greeter.yml  run: echo "${{ github.event.pull_request.title }}"
                                                   └─ expression expanded BEFORE bash parses → code execution
workflow-lint.yml ──▶ actionlint + zizmor ──▶ SARIF ──▶ Security → Code scanning
                                           └─ gate: fail on medium+ findings
```

### Why pinning matters — a 2026 case
Between 19 and 20 March 2026, 76 of 77 version tags of `aquasecurity/trivy-action` and all tags of `setup-trivy` were force-pushed to credential-stealing commits (GitHub advisory GHSA-69fq-xp46-6x23). Workflows referencing those actions **by tag** executed attacker code with their secrets; workflows pinned to a full commit SHA did not change. A security scanner became the attack vector — exactly the build-surface threat Chapter 11 describes.

## Step 1 — Create or Open the Repository
```bash
bash shared/scripts/start-lab.sh chapter-11/lab-04-harden-github-actions ~/dt-labs/dt-lab-04
```
Create an empty **public** repository `dt-lab-04`.

## Step 2 — Clone the Repository
```bash
cd ~/dt-labs/dt-lab-04
git remote add origin https://github.com/<your-username>/dt-lab-04.git
git push -u origin main
```

## Step 3 — Build the Lab
Open `.github/workflows/pr-greeter.yml`. Before reading further, list every weakness you can find. Then compare with the table:

| Weakness | Line | Risk |
|---|---|---|
| Template injection | `${{ github.event.pull_request.title }}` and `${{ github.head_ref }}` inside `run:` | Anyone who can open a PR can run shell commands on the runner |
| Excessive permissions | `permissions: write-all` | An injected command gets a token that can push code, create releases, modify issues |
| Mutable references | `actions/checkout@v7`, `actions/setup-python@v7` | The tag can be moved to malicious code (see case above) |
| Persisted credentials | checkout without `persist-credentials: false` | Token left in `.git/config` for later steps |

## Step 4 — Implement the Security Control
`.github/workflows/workflow-lint.yml` is the control. It installs pinned versions of **actionlint** (correctness and some injection checks) and **zizmor** (GitHub Actions security audit), uploads SARIF and fails on medium-or-higher findings.

## Step 5 — Run the Pipeline
Your initial push ran `workflow-lint`. **Expected: it fails** — the insecure workflow is already in the repository.

## Step 6 — Inspect the Result
**Actions → workflow-lint → lint**:
- *actionlint* reports `"github.event.pull_request.title" is potentially untrusted … pass it through an environment variable`.
- *zizmor gate* reports high-severity findings. Observed locally with zizmor 1.30.1: `template-injection` ×2, `unpinned-uses` ×2; with `--persona auditor` also `excessive-permissions`.
**Security → Code scanning** lists the same findings, category `zizmor`.

## Step 7 — Introduce a Deliberate Security Failure (Exploit It)
> **Intentionally insecure demonstration in your own repository only.** The payload prints a warning; it does not exfiltrate anything.
```bash
git switch -c injection-demo
git commit --allow-empty -m "LAB-04: trigger pr-greeter"
git push -u origin injection-demo
```
Open a pull request with this **title** (copy exactly):
```
demo"; echo "::warning::INJECTED command ran as $(whoami) on $(uname -n)"; echo "
```

## Step 8 — Observe the Security Control
Open **Actions → pr-greeter → greet → Greet the contributor**. A yellow **warning annotation** shows `INJECTED command ran as runner on …`: your title was executed as shell code.
- **Threat:** untrusted event data executed on a runner holding a write-all token.
- **Detection:** `workflow-lint` flagged it before exploitation.
- **Finding:** `template-injection` (high).
- **Decision:** the workflow must not remain on `main` in this form.

## Step 9 — Remediate the Finding
Replace `.github/workflows/pr-greeter.yml` with the hardened version in `solution/.github/workflows/pr-greeter.yml` (copy it from the labs repository) on your `injection-demo` branch. Key changes: untrusted values move to `env:` and are quoted as `"$PR_TITLE"`; `permissions: {}` at workflow level and `contents: read` at job level; both actions pinned to full SHAs with the tag in a comment; `persist-credentials: false`; `timeout-minutes`.
```bash
git add .github/workflows/pr-greeter.yml
git commit -m "LAB-04: harden pr-greeter"
git push
```
Edit the PR title (any edit re-triggers `pr-greeter`) — keep the malicious title to prove the fix.

## Step 10 — Validate the Fix
### Expected Result
- `pr-greeter` prints the title **literally**, including `$(whoami)`; no warning annotation appears.
- `workflow-lint` passes: zizmor reports no findings at medium or higher.
- The code-scanning alerts close automatically once `main` is fixed (merge the PR).

## Step 11 — Cleanup
Merge or close the PR, delete the branch and optionally the repository. No cloud resources were used.

## What You Should Have Learned
The pipeline is code with an attack surface. Treat event data as untrusted input, grant the token the least privilege per job, pin dependencies immutably and lint workflows as rigorously as application code.

## Lab Completion Checklist
- [ ] Repository created
- [ ] Code committed
- [ ] Pipeline executed
- [ ] Security control triggered
- [ ] Finding identified (and exploited safely)
- [ ] Finding remediated
- [ ] Pipeline passed
- [ ] Resources cleaned up

## Further Challenge
Add a Dependabot configuration (`.github/dependabot.yml`, ecosystem `github-actions`) so SHA pins are updated through reviewed pull requests, and add the OpenSSF Scorecard action (`ossf/scorecard-action@2d1146689b8cda280b9bc96326124645441f03bc # v2.4.4`) on a weekly schedule.

---
**Validation status:** starter and solution workflows executed through actionlint 1.7.12 and zizmor 1.30.1 (offline); findings listed above are the observed output. The injection result in Step 8 is the expected behaviour of expression expansion and was **not** executed on a live runner. **EXECUTION VALIDATION REQUIRED.**
