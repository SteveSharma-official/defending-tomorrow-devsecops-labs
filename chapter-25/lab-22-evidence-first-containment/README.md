# LAB-22 — Evidence-First Containment: Preserve, Hash, Isolate, Then Destroy

| Chapter | Level | Difficulty | Estimated time | Cloud required? |
|---|---|---|---|---|
| Chapter 25 — Incident Response Engineering (§25.3 Evidence Preservation Architecture, §25.4.2 Container Forensics Without Disk Images, §25.5 Containment Sequence Model) | 3 — Advanced | Advanced | 45–60 minutes (+20 for the optional kind exercise) | No (optional kind) |

## What You Will Build
- A containment playbook as code (`PB-POD-CONTAIN-001`), plus a gate that enforces Chapter 25's sequence: **preserve → hash → isolate → revoke → destroy**. Only reversible, single-entity steps may run automatically.
- A SHA-256 evidence manifest tool that detects any altered, missing or added file.
- An optional **kind** exercise that runs the playbook on a disposable cluster: it captures a "compromised" pod's spec, events, logs and `/tmp` filesystem, hashes them, quarantines the pod with a deny-all NetworkPolicy, deletes it, and proves the evidence still verifies.

## What You Will Learn
- Why ephemeral workloads make "collect evidence later" impossible (§25.1.1).
- How to encode blast radius and reversibility as approval rules.
- How to make evidence tamper-evident with a hashed manifest.

## Prerequisites
**Required:** LAB-00; Chapter 25 §25.3–25.5.
**Optional:** Docker, kind and kubectl to run `scripts/contain-pod.sh` on your own machine.

## Estimated Time
**45–60 minutes**, plus about 20 minutes for the kind exercise.

## Difficulty
Advanced

## Architecture
```
playbooks/PB-POD-CONTAIN-001.yaml ──▶ tools/check_playbook.py  P1 no destroy before spec/events/logs/filesystem
                                                                P2 hash before isolate/revoke/destroy
                                                                P3 auto only if reversible + single entity
                                                                P4 isolate before revoke/destroy
scripts/contain-pod.sh (kind) ──▶ evidence/<case>/ ──▶ tools/evidence_manifest.py create ──▶ MANIFEST.json
                              ──▶ quarantine NetworkPolicy ──▶ delete pod ──▶ evidence_manifest.py verify ✔
```

## Step 1 — Create or Open the Repository
```bash
bash shared/scripts/start-lab.sh chapter-25/lab-22-evidence-first-containment ~/dt-labs/dt-lab-22
```
Create an empty **public** repository named `dt-lab-22`.

## Step 2 — Clone the Repository
```bash
cd ~/dt-labs/dt-lab-22
git remote add origin https://github.com/<your-username>/dt-lab-22.git
git push -u origin main
```

## Step 3 — Build the Lab
Read the playbook. Each step declares `class`, `reversible`, `blast_radius` and `approval`, which are the two axes of the §25.5 model. Then read `scripts/contain-pod.sh`. It stops before any irreversible step unless a human sets `CONFIRM_DESTRUCTIVE=yes`.

**Why it matters for DevSecOps:** when an incident hits, the fastest action ("delete the pod") also destroys the only evidence. Encoding the order as code takes that decision out of a stressful moment.

## Step 4 — Implement the Security Control
`.github/workflows/containment.yml` has two jobs:
- `gate` runs on every pull request: the playbook check, a manifest check on the sample case, and the unit tests.
- `kind-exercise` runs on manual dispatch: the whole containment on a disposable cluster.

## Step 5 — Run the Pipeline
Push to `main`. Expected: `1 playbook(s), 0 finding(s)`, `evidence intact` and `5 passed`. Then run **Actions → containment → Run workflow** to start the kind exercise.

## Step 6 — Inspect the Result
Download the `evidence` artifact from the kind run. It holds `pod.yaml`, `events.txt`, `logs.txt`, `filesystem-tmp.tar` (with the simulated `/tmp/x.sh`) and `MANIFEST.json`. The step log ends with `evidence intact`, recorded **after** the pod was deleted.

## Step 7 — Introduce a Deliberate Security Failure
On a branch named `fast-containment`, apply `lab-changes/apply-failures.md` (INTENTIONALLY INSECURE). It moves `delete_pod` up to step 2, auto-approves it, and appends a line to the sample evidence log. Push and open a pull request.

## Step 8 — Observe the Security Control
Verified locally:
```
P2 delete_pod: runs before evidence is hashed into a manifest
P1 delete_pod: destroys the workload before preserving: filesystem, logs
P3 delete_pod: auto-approved but irreversible or wide blast radius
P4 delete_pod: runs before the entity is isolated
altered: logs.txt
```
Threat → Detection → Finding → Decision: evidence destroyed or tampered with → sequence and integrity gates → four sequence findings and one integrity finding → pull request blocked.

## Step 9 — Remediate the Finding
Restore the step order and `approval: human`. Revert `logs.txt`. Evidence is never edited: if you need annotations, add them to a separate case-notes file **outside** the hashed folder.

## Step 10 — Validate the Fix
### Expected Result
- `0 finding(s)`, `evidence intact` and `5 passed`; the pull request can merge.

## Step 11 — Cleanup
The kind job deletes its cluster. Locally, run `kind delete cluster --name lab22`. Delete the branch and, if you want, the repository.

## What You Should Have Learned
In cloud-native incident response, containment order is a security control. Preserve and hash first, isolate with the smallest reversible action, and destroy last, with a human decision. A hashed manifest makes evidence tamper-evident.

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
Add `PB-AGENT-CONTAIN-001` from §25.5.1 as a second playbook: halt the agent session, preserve the decision trace, revoke the agent's credentials, then quarantine its configuration. Extend `check_playbook.py` so an agent playbook must preserve `decision_trace` before `revoke`.

---
**Validation status:** gate executed locally on 1 Oct 2026 (Python 3.11, pytest 9.0.3): 5/5 tests pass and the Step 8 findings are reproduced. `contain-pod.sh` passes shellcheck. actionlint and zizmor report no findings. The kind binary SHA-256 matches the project's published `.sha256sum` file. Whether the quarantine NetworkPolicy is enforced depends on the cluster's CNI. **EXECUTION VALIDATION REQUIRED** for the `kind-exercise` job: kind could not pull its node image in the validation environment.
