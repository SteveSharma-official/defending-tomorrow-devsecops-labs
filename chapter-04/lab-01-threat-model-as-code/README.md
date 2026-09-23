# LAB-01 — Threat Model as Code: Gate the Pipeline on an Incomplete Threat Model

| Chapter | Level | Difficulty | Estimated time | Cloud required? |
|---|---|---|---|---|
| Chapter 4 — Threat Modeling for Modern Enterprises | 1 — Foundations | Beginner | 40–50 minutes | No |

## What You Will Build
A version-controlled threat model (YAML) of Chapter 4's three-tier application and a CI gate that fails whenever a data flow crosses a trust boundary without recorded threats and owned mitigations. You then add the chapter's MCP-connected AI agent and watch the gate force the threat model to keep pace with the architecture.

## What You Will Learn
- Express trust boundaries, data flows, STRIDE threats and mitigations as reviewable code.
- Apply the book's agent extension (category **A** — agency / tool misuse) alongside STRIDE.
- Enforce threat-model completeness automatically on every pull request.
- Distinguish an *implemented* mitigation from a *planned* one and from a time-bound risk acceptance.

## Prerequisites
**Required:** LAB-00 completed (GitHub account, Git, editor); Chapter 4 read to the end of the hands-on lab.
**Optional:** Python 3.12+ with `pip install PyYAML` to run the checker locally.

## Estimated Time
**40–50 minutes**

## Difficulty
Beginner

## Architecture
```
Chapter 4 diagram ──▶ threat-model/threat-model.yaml ──PR──▶ GitHub Actions: threat-model-gate
                                                                    │ R1 boundary flows have threats
                                                                    │ R2 valid STRIDE(+A) category
                                                                    │ R3 mitigations have owner+status
                                                                    │ R4 high risk = implemented or accepted (unexpired)
                                                                    ▼
                                                         PASS → merge   FAIL → annotated errors
```

## Step 1 — Create or Open the Repository
```bash
bash shared/scripts/start-lab.sh chapter-04/lab-01-threat-model-as-code ~/dt-labs/dt-lab-01
```
Create an empty **public** repository named `dt-lab-01` on GitHub (same settings as LAB-00, Step 2).

## Step 2 — Clone the Repository
The working copy already exists locally; connect and push it:
```bash
cd ~/dt-labs/dt-lab-01
git remote add origin https://github.com/<your-username>/dt-lab-01.git
git push -u origin main
```

## Step 3 — Build the Lab
Open `threat-model/threat-model.yaml` and compare it with Chapter 4, Step 1 (five baseline trust boundaries).
- **What you are doing:** reviewing a threat model that lives next to the code it describes.
- **Why it matters:** a threat model in a slide deck is stale the day after it is presented; one in the repository is reviewed in the same pull request as the architecture change.

Run the checker locally (optional):
```bash
pip install PyYAML==6.0.3
python tools/check_threat_model.py threat-model/threat-model.yaml
# Expected: RESULT: PASS (0 gaps)
```

## Step 4 — Implement the Security Control
The control is **threat-model completeness as a pipeline gate** (`.github/workflows/threat-model-gate.yml`). It runs on pull requests that touch the model and on `main`. Read rules R1–R4 at the top of `tools/check_threat_model.py`.

## Step 5 — Run the Pipeline
The initial push ran the gate. **Actions → threat-model-gate → latest run → validate → Check threat model completeness** shows `RESULT: PASS (0 gaps)`.

## Step 6 — Inspect the Result
Note that T-003 and T-005 are `planned`, not `implemented`, yet the gate passes: they are **medium** risk. Rule R4 applies only to high-risk threats. Discuss: is that the right threshold for your organisation?

## Step 7 — Introduce a Deliberate Security Failure
You will change the architecture without updating the threats — the most common real-world failure.
```bash
git switch -c add-support-agent
```
Copy the two trust boundaries (TB6, TB7) and two data flows (DF6, DF7) from `threat-model/agent-extension.yaml.txt` into the matching sections of `threat-model.yaml`. Do **not** add threats.
```bash
git commit -am "LAB-01: add AI support agent and MCP tool to the architecture"
git push -u origin add-support-agent
```
Open a pull request into `main`.

## Step 8 — Observe the Security Control
- **Threat:** a new trust boundary (agent → tool) enters production unanalysed.
- **Detection:** rule R1.
- **Finding:** the check fails with two annotations: `R1 flow DF6 … has no threats recorded` and `R1 flow DF7 …`.
- **Decision:** the architecture change cannot merge until it is threat-modelled.

## Step 9 — Remediate the Finding
Apply Chapter 4's agent extension. Add at least these threats (compare with `solution/threat-model/threat-model.yaml`):
- **T-006** (DF6, `T`) indirect prompt injection through order notes — mitigated by output validation (Chapter 29).
- **T-007** (DF7, `A`) excessive agency / tool misuse — mitigated by a per-agent tool allowlist (LAB-18, Chapter 31) and human approval for write actions.
- **T-008** (DF7, `S`) shared service-account identity — dedicated agent workload identity (Chapter 6).

Commit and push to the same branch.

## Step 10 — Validate the Fix
### Expected Result
- The pull request check passes: `Threat model: dt-three-tier-orders — 7 data flows, 8 threats` and `RESULT: PASS (0 gaps)`.
- Try one more failure: set T-007's mitigation statuses to `planned`. R4 fails. Then add a `risk_acceptance` with `approver` and a future `expires` date; R4 passes. Revert before merging.

## Step 11 — Cleanup
No cloud resources. Delete the feature branch after merging. Optionally delete the repository.

## What You Should Have Learned
Threat modelling becomes continuous when the model is code, reviewed in the same pull request as the design change and enforced by a gate. The agent extension shows that AI components fit the same method — they add a boundary and a threat category, not a separate discipline.

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
Add a rule R5 that fails when any `planned` mitigation on a medium-risk threat is older than 90 days (add a `planned_on` date field). Write a unit test for the rule.

---
**Validation status:** checker executed locally against the starter (PASS), the Step 7 state (FAIL, 2 gaps) and the solution (PASS). Workflow checked with actionlint and zizmor. **EXECUTION VALIDATION REQUIRED** on a GitHub-hosted runner.
