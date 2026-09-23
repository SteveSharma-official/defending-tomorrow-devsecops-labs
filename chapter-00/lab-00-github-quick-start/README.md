# LAB-00 — GitHub Lab Quick Start: Your First Security-Aware Pipeline

| Chapter | Level | Difficulty | Estimated time | Cloud required? |
|---|---|---|---|---|
| Chapter 0 — How to Read This Book | 1 — Foundations | Beginner | 30–40 minutes | No |

## What You Will Build
A personal lab repository on GitHub containing the book's sample application and a GitHub Actions workflow that runs its unit tests — including a security regression test — on every push and pull request.

## What You Will Learn
- Create a public GitHub repository and push code to it from the command line.
- Read a GitHub Actions workflow: triggers, `permissions`, jobs and steps.
- Explain why the workflow's `GITHUB_TOKEN` is restricted to `contents: read` and why actions are pinned to a commit SHA.
- Find a workflow run, open its logs and interpret a pass or fail.

## Prerequisites
**Required**
- A free GitHub account (https://github.com/signup).
- Git 2.40 or later (`git --version`). Windows users: install *Git for Windows* and use **Git Bash** for every command in these labs.
- A text editor (VS Code recommended).
- A clone of this labs repository: `git clone https://github.com/SteveSharma-official/defending-tomorrow-devsecops-labs`

**Optional**
- Python 3.12+ to run the tests locally.
- GitHub CLI (`gh --version`) — every step also has a web-UI path.

## Estimated Time
**30–40 minutes**

## Difficulty
Beginner

## Architecture
```
You (laptop) ──git push──▶ GitHub repository (public) ──event──▶ GitHub Actions runner (ephemeral VM)
                                                               ├─ checkout (read-only token)
                                                               ├─ install dependencies
                                                               └─ pytest (incl. SQL-injection regression test)
                                                                    │
                                              Actions tab ◀──── pass / fail result
```

## Step 1 — Create the Lab Repository Locally
**What you are doing:** generating a clean working copy that contains only this lab's files.
**Why it matters:** each lab runs in its own repository so that one lab's workflows, findings and settings never interfere with another's.

```bash
cd defending-tomorrow-devsecops-labs
bash shared/scripts/start-lab.sh chapter-00/lab-00-github-quick-start ~/dt-labs/dt-lab-00
cd ~/dt-labs/dt-lab-00
ls -a            # expect: .git  .github  app
```

## Step 2 — Create the GitHub Repository and Push
1. In GitHub, select **+ → New repository**.
2. **Repository name:** `dt-lab-00` (convention for every lab: `dt-lab-NN`).
3. **Visibility:** **Public**. On the GitHub Free plan several controls used later (rulesets, CodeQL code scanning, dependency review, artifact attestations) are available only on public repositories. Never place real secrets or confidential data in a lab repository.
4. Leave *Add a README*, *.gitignore* and *license* **unticked** (the repository must be empty).
5. Select **Create repository**, then push:

```bash
git remote add origin https://github.com/<your-username>/dt-lab-00.git
git push -u origin main
```
If Git asks for a password, use the browser sign-in prompt (Git Credential Manager) or `gh auth login`; GitHub no longer accepts account passwords for Git operations.

## Step 3 — Read the Workflow
Open `.github/workflows/hello-security.yml`.

| Line | What it does | Why it matters for DevSecOps |
|---|---|---|
| `on: push / pull_request` | Runs on every change | Security checks must run on every change, not on request |
| `permissions: contents: read` | Restricts the automatic `GITHUB_TOKEN` | A compromised step cannot push code or tamper with releases |
| `uses: actions/checkout@3d3c…b1 # v7.0.1` | Pins the action to an immutable commit | Tags can be moved by an attacker (see the March 2026 `trivy-action` compromise discussed in LAB-04) |
| `persist-credentials: false` | Does not leave the token in `.git/config` | Later steps cannot reuse it |
| `pytest -q` | Runs tests incl. `test_sql_injection_payload_returns_nothing` | Security behaviour is tested like any other behaviour |

## Step 4 — Implement the Security Control
The control in this lab is a **least-privilege, SHA-pinned CI workflow with a security regression test**. It is already in place; confirm it by searching the file for `permissions:` and `@` followed by 40 hexadecimal characters.

## Step 5 — Run the Pipeline
The push in Step 2 already triggered the workflow. Expected sequence: push → GitHub receives commit → `hello-security` queued → runner starts → tests run → job reports success.

## Step 6 — Inspect the Result
**GitHub → your repository → Actions → hello-security → latest run → test job**
Expand *Run unit and security regression tests*: you should see `4 passed`.

`[SCREENSHOT REQUIRED — GITHUB ACTIONS: SUCCESSFUL hello-security RUN SHOWING "4 passed"]` (optional — the text output is sufficient evidence)

## Step 7 — Introduce a Deliberate Security Failure
> **Intentionally insecure change — lab use only.** You will re-introduce a SQL-injection flaw to see the regression test catch it.

Create a branch and edit `app/app.py`, replacing the parameterised query in `list_orders()` with string formatting:
```bash
git switch -c break-the-query
```
```python
    rows = get_db().execute(
        f"SELECT id, customer, item, qty FROM orders WHERE customer = '{customer}' LIMIT {limit}"
    ).fetchall()
```
```bash
git commit -am "LAB-00: deliberately introduce SQL injection"
git push -u origin break-the-query
```
Open a pull request: **Pull requests → New pull request → base: main ← compare: break-the-query → Create pull request**.

## Step 8 — Observe the Security Control
**Threat:** attacker-controlled input changes the meaning of a SQL statement.
**Detection:** `test_sql_injection_payload_returns_nothing` sends `x' OR '1'='1` and receives every row.
**Finding:** the `test` check on the pull request shows a red ✗ and `1 failed`.
**Decision:** the change must not be merged. (LAB-02 turns this into an enforced rule.)

## Step 9 — Remediate the Finding
Restore the parameterised query (`git checkout main -- app/app.py` or re-type it), commit and push to the same branch. The pull request re-runs automatically.

## Step 10 — Validate the Fix
### Expected Result
- The pull request check shows a green ✓ and `4 passed`.
- Merge the pull request (**Merge pull request → Confirm merge**); the run on `main` also passes.

## Step 11 — Cleanup
- No cloud resources were created and public-repository Actions minutes on standard runners are not billed (VERIFY CURRENT PRODUCT BEHAVIOUR on GitHub's billing page).
- Delete the `break-the-query` branch (the pull request page offers **Delete branch**).
- Keep `dt-lab-00` if you want a record; otherwise **Settings → General → Danger Zone → Delete this repository**.

## What You Should Have Learned
A pipeline is a security control only when it runs on every change, holds the least privilege it needs, depends on immutable components and fails when security behaviour regresses.

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
Add a second job that runs only on `pull_request` and prints the list of changed files (`git diff --name-only origin/main...HEAD`). Keep the workflow's permissions at `contents: read`.

---
**Validation status:** workflow syntax checked with actionlint 1.7.12 and zizmor 1.30.1; tests executed locally (4 passed, Python 3.11). **EXECUTION VALIDATION REQUIRED** on a GitHub-hosted runner before publication.
