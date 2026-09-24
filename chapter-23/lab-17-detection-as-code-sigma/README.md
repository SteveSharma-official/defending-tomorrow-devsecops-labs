# LAB-17 — Detection as Code: Lint, Test and Convert Sigma Rules in CI

| Chapter | Level | Difficulty | Estimated time | Cloud required? |
|---|---|---|---|---|
| Chapter 23 — Detection Engineering (§23.2 Detection-as-Code Lifecycle, §23.7 Coverage) | 3 — Advanced | Advanced | 45–60 minutes | No |

## What You Will Build
A detection repository with two Sigma rules (CloudTrail logging disabled; GitHub ruleset/branch protection removed), **true- and false-positive unit tests**, schema and ATT&CK-tag validation with `sigma check`, and conversion to a SIEM query language on every pull request.

## What You Will Learn
- Write Sigma rules with a valid lifecycle status, ATT&CK tags and documented false positives.
- Unit-test detection *logic* with sample events before a rule reaches a SIEM.
- Require that every rule has at least one true-positive test (coverage as a gate).
- Convert rules for a target backend and review the generated query in the PR.

## Prerequisites
**Required:** LAB-00; Chapter 23 §23.2.
**Optional:** Python 3.12+ with `pip install sigma-cli pySigma-backend-splunk pytest` locally.

> **Book alignment.** Chapter 23's rule listings use valid Sigma status values and no legacy `groupby`/`timeframe` keys, and pass `sigma check` — the same validation this lab runs in CI. As Chapter 23 notes, velocity-based detections such as "impossible travel" and new-value detections need a Sigma **correlation** rule or SIEM analytics; a single-event rule cannot express them.

## Estimated Time
**45–60 minutes**

## Difficulty
Advanced

## Architecture
```
rules/*.yml ─PR─▶ detections.yml ─▶ sigma check (schema, status, condition, tags)
                                 ─▶ pytest tests/ (cases.yaml: match / no_match events; every rule needs a true positive)
                                 ─▶ sigma convert -t splunk ─▶ detections.spl artifact ─▶ reviewer reads the real query
```

## Step 1 — Create or Open the Repository
```bash
bash shared/scripts/start-lab.sh chapter-23/lab-17-detection-as-code-sigma ~/dt-labs/dt-lab-17
```
Create an empty **public** repository `dt-lab-17`.

## Step 2 — Clone the Repository
```bash
cd ~/dt-labs/dt-lab-17
git remote add origin https://github.com/<your-username>/dt-lab-17.git
git push -u origin main
```

## Step 3 — Build the Lab
Read both rules and `tests/events/cases.yaml`. The CloudTrail rule filters Control Tower automation — the same exception Appendix A's SCP makes — so a legitimate change is not an alert. `tests/sigma_eval.py` is a deliberately small evaluator for logic tests; the converted SPL is what runs in production.

## Step 4 — Implement the Security Control
The control is the `detections` workflow: a rule cannot merge unless it validates, its tests pass, every rule has a true-positive case and it converts cleanly.

## Step 5 — Run the Pipeline
Expected (verified locally, sigma-cli 3.1.0 / pySigma 1.5.1): `6 passed` and the converted queries:
```
eventSource="cloudtrail.amazonaws.com" eventName IN ("StopLogging", "DeleteTrail", "UpdateTrail") NOT userIdentity.arn="*:assumed-role/AWSControlTowerExecution"
action IN ("protected_branch.destroy", "repository_ruleset.destroy")
```

## Step 6 — Inspect the Result
Download the `converted-detections` artifact. Reviewers approve the *query*, not only the YAML.

## Step 7 — Introduce Deliberate Failures
1. **Invalid metadata:** in `rules/github_ruleset_or_protection_removed.yml`, change `status: test` to `status: production` (not a valid Sigma status — `sigma check` must reject it).
2. **Logic regression:** in `rules/aws_cloudtrail_logging_disabled.yml`, change the filter modifier from `|endswith` to `|contains` and the value to `:assumed-role/` — a "quick fix" for noisy alerts.
Commit both on branch `tune-rules`, push, open a PR.

## Step 8 — Observe the Security Control
- `sigma check` fails with `SigmaStatusError` (verified locally).
- After fixing the status only, `pytest` fails `attacker stops logging` (verified locally: `1 failed, 5 passed`): the widened filter now suppresses **every** assumed-role session — including the attacker's. The tuning change created a detection blind spot.
Threat → Detection → Finding → Decision: defence evasion hidden by rule "tuning" → unit test with a true-positive event → failing test names the case → PR blocked.

## Step 9 — Remediate the Finding
Restore `status: test` and the precise `|endswith: ':assumed-role/AWSControlTowerExecution'` filter. If alert volume is the real problem, add a *specific* filter and a new `no_match` test for the legitimate source.

## Step 10 — Validate the Fix
### Expected Result
- `sigma check`: no errors; `pytest`: all cases pass; SPL artifact produced.

## Step 11 — Cleanup
Delete branches and optionally the repository. No cloud resources.

## What You Should Have Learned
Detections are software: they need schema validation, tests that prove they fire, tests that prove they stay quiet, and review of the compiled query. Coverage gaps often come from well-meaning tuning.

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
Write a rule for the agent tool-scope expansion scenario from Chapter 23 §23.6 using a Sigma **correlation** rule (`type: value_count` or `event_count`) and add tests for it.

---
**Validation status:** unit tests 6/6 pass; `sigma check` passes (validated with ATT&CK/D3FEND tag validators excluded because their data sources were unreachable from the validation environment); Splunk conversion output shown above. **EXECUTION VALIDATION REQUIRED** for full `sigma check` with tag validators on a GitHub-hosted runner.
