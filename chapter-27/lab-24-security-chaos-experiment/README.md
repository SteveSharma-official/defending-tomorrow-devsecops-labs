# LAB-24 — Security Chaos Experiment: Prove Detection of a Silently Disabled Control

| Chapter | Level | Difficulty | Estimated time | Cloud required? |
|---|---|---|---|---|
| Chapter 27 — Chaos Security Engineering (§27.2 SCEF: Define, Design, Guard, Execute, Learn; §27.5 Injected Failure in Cloud-Native Environments) | 3 — Advanced | Advanced | 45–60 minutes (+20 for the kind run) | No (optional kind) |

## What You Will Build
A security chaos experiment as code (`EXP-001`). It silently removes the Pod Security Admission `restricted` enforcement label from a namespace, then measures whether a control-drift watcher **detects** it, **responds** by restoring the label, and whether admission **recovers** (a privileged pod is rejected again). Each is measured against the time limits in a four-element hypothesis. A gate refuses experiments that aren't measurable or aren't guarded, and refuses failed results that haven't been turned into findings.

## What You Will Learn
- Write the §27.2.1 four-element hypothesis: condition, detection, response and recovery, each with a time limit.
- Guard an experiment with blast radius, abort conditions, rollback, maximum duration and a named approver, so the experiment doesn't become the incident.
- Turn measured failures into tracked findings (the Learn phase).

## Prerequisites
**Required:** LAB-00; LAB-10 recommended (admission control); Chapter 27 §27.2.
**Optional:** Docker, kind and kubectl to run `scripts/run-experiment.sh` locally.

## Estimated Time
**45–60 minutes**, plus about 20 minutes for the kind run.

## Difficulty
Advanced

## Architecture
```
experiments/EXP-001.yaml ──▶ tools/chaos.py check     (DEFINE: 4 measurable expectations · GUARD: lab24-* only,
                                                      abort, rollback, ≤30 min, approver)
kind ─▶ run-experiment.sh: baseline (privileged pod rejected) ─▶ inject: remove enforce label
        drift-watch.sh: detect ─▶ re-label (respond) ─▶ privileged pod rejected again (recover) ─▶ results/run.json
results/*.json ─▶ tools/chaos.py evaluate   (PASS/FAIL per expectation; FAIL ⇒ learn.findings must record it)
```

## Step 1 — Create or Open the Repository
```bash
bash shared/scripts/start-lab.sh chapter-27/lab-24-security-chaos-experiment ~/dt-labs/dt-lab-24
```
Create an empty **public** repository named `dt-lab-24`.

## Step 2 — Clone the Repository
```bash
cd ~/dt-labs/dt-lab-24
git remote add origin https://github.com/<your-username>/dt-lab-24.git
git push -u origin main
```

## Step 3 — Build the Lab
Read `experiments/EXP-001-psa-enforcement-removed.yaml` section by section: `define`, `design`, `guard`, `learn`. Then read `scripts/run-experiment.sh`. It refuses to run unless the kube context is a kind cluster, and it checks the baseline (the privileged probe is rejected) before injecting anything.

**Why it matters for DevSecOps:** "we would notice if admission control were switched off" is a belief. This experiment turns it into a measured result.

## Step 4 — Implement the Security Control
`.github/workflows/chaos.yml`:
- `gate` (every pull request): `chaos.py check` on every experiment, an evaluation of the recorded sample run, and the unit tests.
- `execute-on-kind` (manual): runs EXP-001 on a disposable cluster and evaluates the measured times.

## Step 5 — Run the Pipeline
Push to `main`. Expected: no `::error::` lines, every expectation `PASS` for the sample run, and `5 passed`. Then run **Actions → chaos → Run workflow**.

## Step 6 — Inspect the Result
Download the `experiment-results` artifact. `run.json` holds the four timestamps, and the evaluation step prints `measured_s` against `limit_s` for detection, response and recovery.

## Step 7 — Introduce a Deliberate Security Failure
On a branch named `bigger-experiment`, apply `lab-changes/apply-failures.md` (INTENTIONALLY INSECURE). It widens the blast radius to `*`, removes the abort conditions and the detection limit, and swaps in a slow run. Push and open a pull request.

## Step 8 — Observe the Security Control
Verified locally:
```
DEFINE detection expectation has no measurable max_seconds — the hypothesis cannot pass or fail
GUARD blast radius ['*'] is not limited to lab24-* namespaces
GUARD no abort conditions
LEARN detection failed (FAIL) but no finding is recorded in learn.findings
LEARN response failed (FAIL) but no finding is recorded in learn.findings
```
Response fails too, because it is measured from the moment of injection (§27.2.1). Slow detection delays everything after it.

## Step 9 — Remediate the Finding
Restore the guard rails and the 60-second limit. For the slow run, don't relax the hypothesis to make it pass. Record a finding, for example:
```yaml
learn:
  findings:
    - {expectation: detection, owner: detection-engineering, action: "run drift-watch every 5 s; alert on PSA label changes from the audit log"}
    - {expectation: response,  owner: platform-engineering,  action: "follows from the detection fix; re-test"}
```

## Step 10 — Validate the Fix
### Expected Result
- The gate passes. Failed expectations are allowed **only** when they are recorded as findings with an owner.

## Step 11 — Cleanup
The kind job deletes its cluster. Locally, run `kind delete cluster --name lab24`. Delete the branch.

## What You Should Have Learned
A chaos experiment is a measurable hypothesis with guard rails. A failed experiment is useful only when it becomes an owned finding that feeds back into detection, response and architecture.

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
Write EXP-002 from §27.7, an agent misbehaviour scenario. Simulate an agent tool call outside its allow-list against your LAB-18 policy, and measure whether the deny decision and the alert arrive within the hypothesis limits.

---
**Validation status:** gate executed locally on 1 Oct 2026 (Python 3.11, pytest 9.0.3): 5/5 tests pass and the Step 8 findings are reproduced. Scripts pass shellcheck; actionlint and zizmor report no findings. **EXECUTION VALIDATION REQUIRED** for `execute-on-kind`: kind could not pull its node image in the validation environment.
