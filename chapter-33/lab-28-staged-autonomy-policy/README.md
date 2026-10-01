# LAB-28 — Staged Autonomy as Policy: Govern What a Remediation Agent May Do Alone

| Chapter | Level | Difficulty | Estimated time | Cloud required? |
|---|---|---|---|---|
| Chapter 33 — Autonomous Remediation (§33.2 Staged Autonomy Model, §33.4.3 Governance-Containment Maturity Matrix, §33.6.2 Policy as Guardrails, §33.6.3 Blast Radius Engineering) | 3 — Advanced | Advanced | 45–60 minutes | No |

## What You Will Build
The §33.6.2 remediation policy (OPA/Rego v1, as printed in the chapter) plus a decision layer that adds the §33.4.3 prerequisite: **Level 3 autonomy is allowed only when every containment dimension (visibility, revocation, preservation, validation) is at least level 2.** The CI pipeline has three parts:
- Ten unit tests, including two **invariants** that no edit may break.
- A coverage threshold.
- A replay of recorded remediation requests whose expected decisions are part of the evidence.

## What You Will Learn
- Encode per-action-class autonomy levels, blast-radius limits, escalation triggers and rollback verification as default-deny policy.
- Tie autonomy to demonstrated containment ability rather than to confidence.
- Use invariants and replayed decisions to catch "small" policy edits with large effects.

## Prerequisites
**Required:** LAB-00; LAB-18 recommended (OPA); Chapter 33 §33.2, §33.4 and §33.6.
**Optional:** OPA 1.x locally (`opa test policy data -v`).

## Estimated Time
**45–60 minutes**

## Difficulty
Advanced

## Architecture
```
requests/*.json (action + expected_allow) ─▶ data.remediation.decision.allow
   policy/remediation.rego   §33.6.2: level per class · blast radius · rollback verified · escalations (default deny)
   policy/containment.rego   §33.4.3: Level ≥3 needs every containment dimension ≥2   ◀── data/data.json
   policy/decision.rego      allow + human-readable reasons
CI: opa fmt · opa check --strict · opa test (10 tests incl. invariants) · coverage ≥90% · replay vs expected
```

## Step 1 — Create or Open the Repository
```bash
bash shared/scripts/start-lab.sh chapter-33/lab-28-staged-autonomy-policy ~/dt-labs/dt-lab-28
```
Create an empty **public** repository named `dt-lab-28`.

## Step 2 — Clone the Repository
```bash
cd ~/dt-labs/dt-lab-28
git remote add origin https://github.com/<your-username>/dt-lab-28.git
git push -u origin main
```

## Step 3 — Build the Lab
Read `policy/remediation.rego` alongside the §33.6.2 listing, then `policy/containment.rego` and `data/data.json` (the organisation's current containment maturity). Read the six requests and their `expected_allow` values. Request 04 (isolate a whole network segment at Level 3) is denied because that class is assigned Level 2.

**Why it matters for DevSecOps:** an agent's authority should be as reviewable as a firewall rule. Every change to it goes through a pull request, tests and recorded evidence.

## Step 4 — Implement the Security Control
`.github/workflows/autonomy-policy.yml` checks formatting and strict compilation, runs the tests with coverage, and replays every request against its expected decision. If a decision changes, the step prints the reasons.

## Step 5 — Run the Pipeline
Push to `main`. Expected: `PASS: 10/10`, the coverage threshold met, and all six requests matching their expected decisions.

## Step 6 — Inspect the Result
Run `opa eval -f pretty -d policy -d data -i requests/04-isolate-whole-segment.json 'data.remediation.decision.reasons'`. Output: `["requested level exceeds the level assigned to this action class"]`. Then set `"validation": 1` in `data/data.json` and evaluate request 01 again. Level 3 isolation is now denied with `containment not ready for Level 3: validation is at level 1 (minimum 2)`. Revert the change.

## Step 7 — Introduce a Deliberate Security Failure
On a branch named `faster-remediation`, apply `lab-changes/apply-failures.md` (INTENTIONALLY INSECURE). It promotes network-segment isolation and data deletion to Level 3, allows 20 segments, and drops the rollback check. Push and open a pull request.

## Step 8 — Observe the Security Control
Verified locally:
- `test_invariant_data_deletion_never_autonomous: FAIL` and `test_unverified_rollback_denied: FAIL` (`PASS: 8/10`).
- Replay: `requests/04-isolate-whole-segment.json expected=false actual=true`, so the agent could now isolate whole network segments on its own.

Threat → Detection → Finding → Decision: expanded machine authority → invariants and recorded decisions → named failures → pull request blocked.

## Step 9 — Remediate the Finding
Revert both edits. To promote an action class legitimately, follow §33.2: run it at Level 1, then Level 2, with evidence, a tested rollback and a named approver. Then change the level **and** the affected request's expected decision in the same reviewed pull request.

## Step 10 — Validate the Fix
### Expected Result
- `PASS: 10/10`, coverage ≥ 90%, and every replayed decision matches.

## Step 11 — Cleanup
Delete the branch and, if you want, the repository. No cloud resources.

## What You Should Have Learned
Autonomy is assigned per action class, bounded by blast radius, overridden by escalation triggers and earned through containment maturity. Writing that as policy, with invariants and replayed decisions, makes every expansion of machine authority visible and reviewable.

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
Add the §33.5 checkpoint model. Pass `input.action.checkpoint_due` when accumulated actions reach a governance interval, deny until `input.action.checkpoint_approved_by` names a human, and add tests and a recorded request for it.

---
**Validation status:** executed locally on 1 Oct 2026 with OPA 1.20.2: `opa check --strict` passes, 10/10 tests pass, coverage ≥ 90%, and all six replayed decisions match. The Step 8 failures are reproduced. actionlint and zizmor report no findings. **EXECUTION VALIDATION REQUIRED** on a GitHub-hosted runner.
