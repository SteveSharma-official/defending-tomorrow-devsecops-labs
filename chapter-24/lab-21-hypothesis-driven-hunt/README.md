# LAB-21 — Hypothesis-Driven Hunting as Code: DuckDB Hunts with Ground-Truth Tests

| Chapter | Level | Difficulty | Estimated time | Cloud required? |
|---|---|---|---|---|
| Chapter 24 — Threat Hunting (§24.2 Hypothesis-Driven Hunting Framework, §24.3 Prioritisation, §24.4 Cloud-Native Patterns, §24.6.1 Agent Hunting Query) | 3 — Advanced | Advanced | 50–60 minutes | No |

## What You Will Build
A hunting repository where each hunt is a **versioned hypothesis** (YAML) plus a **query** (DuckDB SQL), run in CI against a synthetic CloudTrail and agent-communication dataset. **Ground-truth tests** prove each hunt finds the planted activity and nothing legitimate. A **feedback gate** blocks any confirmed hunt that does not hand a detection candidate to Chapter 23's pipeline, and that candidate must pass `sigma check`.

## What You Will Learn
- Write hunts with the six-phase structure from §24.2: hypothesis, query, execution, analysis, disposition and feedback.
- Run hunts reproducibly with DuckDB. There's no SIEM to install, and the SQL ports to most data platforms.
- Protect hunts from "noise reduction" that removes the attacker along with the noise.
- Enforce the hunter-to-rule pipeline in code.

## Prerequisites
**Required:** LAB-00; LAB-17 recommended (Sigma); Chapter 24 §24.2–24.6.
**Optional:** Python 3.12+ with `pip install duckdb pytest PyYAML sigma-cli` to run hunts locally.

## Estimated Time
**50–60 minutes**

## Difficulty
Advanced

## Architecture
```
hunts/HUNT-*.yaml (hypothesis, tier, technique, scope, time box, feedback)
hunts/HUNT-*.sql  ──▶ tools/run_hunts.py ──DuckDB──▶ data/*.jsonl, *.csv (synthetic, planted activity)
                          │                    └──▶ disposition: confirmed / cleared ──▶ hunt-report.json
                          ├──▶ tools/tests (ground truth: finds planted rows, not legitimate ones)
                          └──▶ confirmed ⇒ detections/*.yml must exist ──▶ sigma check
```

## Step 1 — Create or Open the Repository
```bash
bash shared/scripts/start-lab.sh chapter-24/lab-21-hypothesis-driven-hunt ~/dt-labs/dt-lab-21
```
Create an empty **public** repository named `dt-lab-21`.

## Step 2 — Clone the Repository
```bash
cd ~/dt-labs/dt-lab-21
git remote add origin https://github.com/<your-username>/dt-lab-21.git
git push -u origin main
```

## Step 3 — Build the Lab
Read the two hunts:
- **HUNT-CLOUD-001** (Tier 2, coverage gap): a CI access key used from an IP it has never used, moving from discovery calls to `GetSecretValue`.
- **HUNT-AGENT-003** (Tier 4, environmental change): the §24.6.1 agent-propagation hunt, ported from PostgreSQL to DuckDB (`regexp_matches` with `\b` word boundaries, and `NOT EXISTS` for the collaborator allow-list).

`tools/make_dataset.py` generates the data deterministically. Read its docstring to see exactly what was planted.

**Why it matters for DevSecOps:** an undocumented hunt can't be repeated, reviewed or turned into a rule. Treating hunts as code gives you all three.

## Step 4 — Implement the Security Control
`.github/workflows/hunts.yml` runs the ground-truth tests, runs every hunt, enforces the feedback rule and validates the detection candidates with `sigma check`.

## Step 5 — Run the Pipeline
Push to `main`. Expected (verified locally, DuckDB 1.5.6): `4 passed`, `HUNT-AGENT-003: confirmed (1 rows)` and `HUNT-CLOUD-001: confirmed (6 rows)`.

## Step 6 — Inspect the Result
Download the `hunt-report` artifact. The CLOUD hunt shows the full attacker sequence, from `GetCallerIdentity` through the denied `ListUsers` to `GetSecretValue`, all from `198.51.100.66`. The AGENT hunt shows one message, from `summariser-bot` to `payments-agent`, telling it to ignore the approval policy. The orchestrator's legitimate "Instead of batch 7…" message is not flagged.

## Step 7 — Introduce a Deliberate Security Failure
On a branch named `tune-hunts`, apply both edits in `lab-changes/apply-failures.md` (INTENTIONALLY INSECURE). The first is a "noise reduction" filter; the second removes a hunt's feedback link. Push and open a pull request.

## Step 8 — Observe the Security Control
- Ground-truth test fails: `assert 'GetSecretValue' in {'ListRoles', 'ListSecrets'}`. The filter cut the hunt from 6 rows to 2 and hid the secret theft (verified locally).
- Feedback gate fails: `HUNT-AGENT-003: confirmed hunt has no feedback.detection_candidate`.

Threat → Detection → Finding → Decision: a blind spot introduced by tuning, plus a lost finding → ground-truth and feedback tests → named failures → pull request blocked.

## Step 9 — Remediate the Finding
Remove the filter. If the volume of denied calls is the real concern, add a separate *triage* column rather than a WHERE clause. Restore the `feedback.detection_candidate` link.

## Step 10 — Validate the Fix
### Expected Result
- `4 passed`, both hunts confirmed, `sigma check` reports no errors, and the pull request can merge.

## Step 11 — Cleanup
Delete the branch and, if you want, the repository. No cloud resources.

## What You Should Have Learned
A hunt is a testable hypothesis, not a one-off query. Ground-truth tests keep hunts honest when they're tuned, and the feedback gate makes sure every confirmed hunt leaves a lasting detection behind.

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
Add HUNT-K8S-002, the escalation-through-patch hunt from §24.5. Generate synthetic Kubernetes audit events in which a non-admin identity patches a `MutatingWebhookConfiguration`, write the hunt and its ground-truth test, then express the detection candidate as a Sigma **correlation** rule.

---
**Validation status:** executed locally on 1 Oct 2026: DuckDB 1.5.6, pytest 9.0.3 (Python 3.11). Ground-truth tests 4/4 pass and the Step 8 failures are reproduced. `sigma check` 3.1.0 passes with the ATT&CK and D3FEND tag validators excluded, because their data sources were unreachable from the validation environment. actionlint and zizmor report no findings. **EXECUTION VALIDATION REQUIRED** on a GitHub-hosted runner, including the full `sigma check` with tag validators.
