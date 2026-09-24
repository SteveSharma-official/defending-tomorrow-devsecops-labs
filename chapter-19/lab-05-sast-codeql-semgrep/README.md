# LAB-05 — SAST in the Pull Request: CodeQL and Custom Semgrep Rules

| Chapter | Level | Difficulty | Estimated time | Cloud required? |
|---|---|---|---|---|
| Chapter 19 — Security Testing at Scale (§19.3 SAST in the Pull Request); Chapter 11 §11.4 Hardening the Build Environment | 2 — Practitioner | Intermediate | 45–60 minutes | No |

## What You Will Build
A two-engine SAST pipeline: **CodeQL** (semantic data-flow analysis, free for public repositories) and **Semgrep** running an organisation-specific rule stored in the repository. Findings appear in **Security → Code scanning** and a **ruleset** blocks merging when high-severity results exist.

## What You Will Learn
- Configure CodeQL "advanced setup" for Python with the `security-extended` query suite.
- Write and test a custom Semgrep rule that encodes a secure-coding standard.
- Turn SAST results into a merge gate with a code-scanning ruleset rule.
- Triage an alert: trace source → sink, fix, and confirm closure.

## Prerequisites
**Required:** LAB-00 and LAB-02 (rulesets); Chapter 19 §19.2–19.3.
**Optional:** Python 3.12+ and `pip install semgrep` to test rules locally.

## Estimated Time
**45–60 minutes** (CodeQL analysis takes 3–8 minutes per run)

## Difficulty
Intermediate

## Architecture
```
PR ──▶ sast.yml ─┬─ codeql job   : init(python, security-extended) → analyze → SARIF (category codeql-python)
                 └─ semgrep job  : .semgrep/ custom rules → SARIF (category semgrep) + ERROR gate
                          │
                          ▼
            Security → Code scanning ──▶ ruleset "Require code scanning results" ──▶ merge allowed / blocked
```

## Step 1 — Create or Open the Repository
```bash
bash shared/scripts/start-lab.sh chapter-19/lab-05-sast-codeql-semgrep ~/dt-labs/dt-lab-05
```
Create an empty **public** repository `dt-lab-05`.

## Step 2 — Clone the Repository
```bash
cd ~/dt-labs/dt-lab-05
git remote add origin https://github.com/<your-username>/dt-lab-05.git
git push -u origin main
```
If GitHub offers CodeQL **default setup**, leave it **off** — this lab uses the advanced (workflow) setup and the two cannot run together.

## Step 3 — Build the Lab
Read `.semgrep/dt-sql-injection.yml` and its tests in `.semgrep/tests/dt-sql-injection.py`: every line marked `# ruleid:` must be flagged and every `# ok:` line must not. The workflow runs `semgrep --test` before the scan, so a rule change that breaks its own tests stops the pipeline. The `# todoruleid:` case — a query assembled in a variable first — is a known limit of pattern matching that CodeQL's data-flow analysis covers (Chapter 19 §19.3.1).
- **What you are doing:** codifying the rule "never build SQL from strings" as a machine-checkable pattern.
- **Why it matters:** CodeQL finds *tainted flows* it can prove; a custom rule enforces *your standard* even where no taint is provable (for example, internal callers), and runs in seconds on every PR.

## Step 4 — Implement the Security Control
1. The workflow `.github/workflows/sast.yml` is already present.
2. Add the gate: **Settings → Rules → Rulesets → New branch ruleset** → name `sast-gate`, target `Default branch`, enforcement **Active** → enable **Require code scanning results** → add tool **CodeQL** with *Security alerts* = **High or higher** and *Alerts* = **Errors** → also add tool **semgrep** → **Create**. (VERIFY CURRENT PRODUCT BEHAVIOUR — the rule name and thresholds are as documented in September 2026.)
3. Also require the status checks `codeql` and `semgrep` (from LAB-02's pattern) so the gate cannot be satisfied by a skipped run.

## Step 5 — Run the Pipeline
The first push runs both jobs. Expected: `semgrep` passes (`0 findings`); `codeql` completes and uploads results.

## Step 6 — Inspect the Result
**Security → Code scanning → Tool: CodeQL** — no open alerts on the secure baseline. **Actions → sast → semgrep** — log shows `Ran 1 rule on 1 file: 0 findings.`

## Step 7 — Introduce a Deliberate Security Failure
> **Intentionally vulnerable code — lab use only.**
```bash
git switch -c sqli
```
Replace `list_orders()` in `app/app.py` with the version in `lab-changes/vulnerable-list-orders.py.txt` (an f-string SQL query). Commit, push and open a pull request.

## Step 8 — Observe the Security Control
| Engine | Expected finding |
|---|---|
| Semgrep | `dt-python-sql-built-from-string` at `app/app.py`, job fails at the gate step (verified locally: `1 finding`, exit code 1) |
| CodeQL | `py/sql-injection` — *SQL query built from user-controlled sources*, with a data-flow path from `request.args.get` to `execute` (EXECUTION VALIDATION REQUIRED — expected, not observed) |
| Ruleset | PR merge box: *Code scanning results … must be resolved* |

Open the CodeQL alert and select **Show paths**: this is the **threat → detection → finding** chain. The **decision** is enforced by the ruleset.

`[SCREENSHOT REQUIRED — CODE SCANNING ALERT py/sql-injection WITH DATA-FLOW PATH]`

## Step 9 — Remediate the Finding
Restore the parameterised query:
```python
    rows = get_db().execute(
        "SELECT id, customer, item, qty FROM orders WHERE customer = ? LIMIT ?",
        (customer, limit),
    ).fetchall()
```
Commit and push to the same branch.

## Step 10 — Validate the Fix
### Expected Result
- Both jobs pass; the PR shows *Code scanning results: no new alerts*.
- The alert status becomes **Fixed** in the PR and after merge.
- Local check: `semgrep scan --config .semgrep/ --error --severity ERROR app/` → `0 findings`.

## Step 11 — Cleanup
Delete the branch, disable or delete the `sast-gate` ruleset if you reuse the repository, optionally delete the repository. No cloud resources used; CodeQL on public repositories is free (VERIFY CURRENT PRODUCT BEHAVIOUR).

## What You Should Have Learned
Two complementary engines — semantic taint analysis and fast organisation-specific rules — plus an enforced gate turn SAST from a report into a control. False-positive handling (dismiss with a reason) is part of the control's evidence.

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
Write a second Semgrep rule that flags `subprocess` calls with `shell=True`, add a test file under `.semgrep/tests/` with `# ruleid:` / `# ok:` annotations and run `semgrep --test .semgrep/`.

---
**Validation status:** custom Semgrep rule executed with Semgrep 1.177.0 against the secure app (0 findings) and the Step 7 variant (1 finding, exit 1); the app's own SQL-injection regression test also fails on the variant. CodeQL results not executed. Workflow checked with actionlint/zizmor. **EXECUTION VALIDATION REQUIRED.**
