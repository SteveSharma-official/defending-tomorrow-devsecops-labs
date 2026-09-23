# LAB-06 — Software Composition Analysis: Stop Vulnerable Dependencies at the Pull Request

| Chapter | Level | Difficulty | Estimated time | Cloud required? |
|---|---|---|---|---|
| Chapter 19 — Security Testing at Scale (**to be completed**; introduced in Chapter 11 §11.4 meanwhile); Chapter 13 | 2 — Practitioner | Intermediate | 35–45 minutes | No |

## What You Will Build
A dependency-security pipeline with a **diff-aware PR gate** (GitHub dependency review), a **full-inventory audit** (pip-audit against the PyPI/OSV advisory data) on push, PR and weekly schedule, and **Dependabot** updates for both Python packages and pinned GitHub Actions.

## What You Will Learn
- Explain the difference between blocking *newly introduced* vulnerable dependencies and auditing the *whole* dependency set.
- Configure `fail-on-severity` and read a dependency-review summary.
- Use a scheduled scan to catch vulnerabilities disclosed after code was merged.
- Remediate by upgrading to the fixed version identified by the advisory.

## Prerequisites
**Required:** LAB-00; Chapter 13 §13.1.
**Optional:** `pip install pip-audit` locally.

## Estimated Time
**35–45 minutes**

## Difficulty
Intermediate

## Architecture
```
PR adds PyYAML==5.3.1 ──▶ dependency-review (diff: base vs head manifest) ──▶ FAIL (critical, fixed in 5.4)
                      └─▶ pip-audit (all pinned requirements)             ──▶ FAIL (PYSEC-2021-142)
main (weekly cron) ────▶ pip-audit ──▶ newly disclosed CVEs surface without a code change
Dependabot ────────────▶ upgrade PRs (pip + github-actions SHA pins) ──▶ same gates
```

## Step 1 — Create or Open the Repository
```bash
bash shared/scripts/start-lab.sh chapter-19/lab-06-sca-dependency-security ~/dt-labs/dt-lab-06
```
Create an empty **public** repository `dt-lab-06`. Dependency review is available for all public repositories; on private repositories it requires GitHub Code Security (VERIFY CURRENT PRODUCT BEHAVIOUR).

## Step 2 — Clone the Repository
```bash
cd ~/dt-labs/dt-lab-06
git remote add origin https://github.com/<your-username>/dt-lab-06.git
git push -u origin main
```
Then **Settings → Advanced Security** → confirm **Dependency graph** and **Dependabot alerts** are enabled; enable **Dependabot security updates**.

## Step 3 — Build the Lab
Review `.github/workflows/sca.yml` and `.github/dependabot.yml`.
- **What:** two complementary scans and an update bot.
- **Why:** dependency review prevents *new* risk entering; the scheduled audit detects *new disclosures* against old code; Dependabot shortens time-to-fix.

## Step 4 — Implement the Security Control
The control is the **dependency-review gate** with `fail-on-severity: high`, plus `pip-audit` failing on any known vulnerability. Add both job names (`dependency-review`, `pip-audit`) as required status checks in a ruleset (LAB-02 pattern).

## Step 5 — Run the Pipeline
The push to `main` runs `pip-audit` only (dependency review runs on PRs). Expected: `No known vulnerabilities found`.

## Step 6 — Inspect the Result
**Actions → sca → pip-audit**: clean. **Insights → Dependency graph**: Flask, PyYAML, gunicorn and their transitive dependencies are listed.

## Step 7 — Introduce a Deliberate Security Failure
> **Intentionally vulnerable dependency — lab use only.**
```bash
git switch -c old-yaml
sed -i 's/^PyYAML==.*/PyYAML==5.3.1/' app/requirements.txt    # macOS: sed -i '' ...
git commit -am "LAB-06: pin a vulnerable PyYAML"
git push -u origin old-yaml
```
Open a pull request.

## Step 8 — Observe the Security Control
| Check | Expected result |
|---|---|
| `dependency-review` | Fails; summary lists `pyyaml 5.3.1` with a critical advisory (arbitrary code execution via `full_load`, CVE-2020-14343), patched in 5.4 |
| `pip-audit` | Fails with `PYSEC-2021-142`, fix version `5.4` (verified locally with pip-audit 2.10.1) |

Threat → Detection → Finding → Decision: a known-exploitable library enters the build → advisory match → CVE with fix version → PR blocked.
Note: the application uses `yaml.safe_load`, so the vulnerable code path may be **unreachable**. The gate still blocks, and that is the correct default; reachability-based exceptions are recorded with VEX (LAB-12), not by silently lowering the gate.

## Step 9 — Remediate the Finding
```bash
sed -i 's/^PyYAML==.*/PyYAML==6.0.3/' app/requirements.txt
git commit -am "LAB-06: upgrade PyYAML to a fixed version"
git push
```

## Step 10 — Validate the Fix
### Expected Result
- Both checks pass on the PR; the dependency-review summary reports no vulnerable additions.
- Locally: `pip-audit -r app/requirements.txt` → `No known vulnerabilities found`.
- Within a week, Dependabot may open PRs for newer versions of pinned actions — review and merge them through the same gates.

## Step 11 — Cleanup
Close/merge the PR, delete the branch; disable Dependabot or delete the repository if you no longer need it. No cloud resources used.

## What You Should Have Learned
SCA needs two clocks: at change time (block new vulnerable components) and continuously (catch new disclosures). Upgrading to the advisory's fixed version is the default remediation; exceptions require evidence.

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
Add `deny-licenses: GPL-3.0-only, AGPL-3.0-only` (or `allow-licenses`) to the dependency-review step and test it with a dependency under a disallowed licence.

---
**Validation status:** pip-audit 2.10.1 executed locally: secure requirements → no findings; PyYAML 5.3.1 → PYSEC-2021-142 (fix 5.4). Dependency-review output not executed. Workflow checked with actionlint/zizmor. **EXECUTION VALIDATION REQUIRED.**
