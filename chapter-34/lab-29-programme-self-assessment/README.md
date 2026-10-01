# LAB-29 — Programme Maturity Self-Assessment as Code (Checklist 34.1)

| Chapter | Level | Difficulty | Estimated time | Cloud required? |
|---|---|---|---|---|
| Chapter 34 — Building a Modern Security Program (§34.2 SPOM, §34.6 Agent Governance Ownership, Checklist 34.1 and Maturity Scoring Guide) | 2 — Practitioner | Beginner | 30–40 minutes | No |

## What You Will Build
A version-controlled self-assessment against **Checklist 34.1**, transcribed from the book (12 items). CI scores it with the chapter's Maturity Scoring Guide (Traditional / Transitioning / Operational / Advanced) and produces a **workbook** (Markdown summary plus CSV) as an artifact and on the run page. It also **rejects unsupported claims**:
- "Implemented" with no evidence in the repository.
- A team instead of a named owner.
- Evidence that hasn't been reviewed within 12 months.

## What You Will Learn
- Treat a leadership assessment like any other control: data, rules, review, history.
- Why "Security team" as an owner is the accountability gap §34.6 warns about.
- How to produce a board-ready gap list that can be traced to evidence.

This is the chapter's non-technical exercise. No security tooling is needed, only a repository.

## Prerequisites
**Required:** a free GitHub account; Chapter 34 §34.2, §34.6 and Checklist 34.1. LAB-00 helps but isn't required.
**Optional:** Python 3.12+ to run the assessment locally.

## Estimated Time
**30–40 minutes**

## Difficulty
Beginner

## Architecture
```
assessment/checklist-34.1.yaml (12 book items) ─┐
assessment/self-assessment.yaml (your answers) ─┼─▶ tools/assess.py ─▶ V1 status · V2 evidence exists ·
evidence/*.md ──────────────────────────────────┘                     V3 named owner · V4 reviewed ≤12 months
                                                                  ─▶ out/workbook.md + workbook.csv (score, level, gaps)
```

## Step 1 — Create or Open the Repository
```bash
bash shared/scripts/start-lab.sh chapter-34/lab-29-programme-self-assessment ~/dt-labs/dt-lab-29
```
Create an empty **private** repository named `dt-lab-29`. A real assessment of your own organisation should never be public.

## Step 2 — Clone the Repository
```bash
cd ~/dt-labs/dt-lab-29
git remote add origin https://github.com/<your-username>/dt-lab-29.git
git push -u origin main
```

## Step 3 — Build the Lab
Read the checklist file and the fictional sample answers. Then replace the sample with your **own** organisation's answers, or a team you know well. Add one evidence file for each item you mark `implemented`, describing the evidence rather than copying confidential documents.

**Why it matters for DevSecOps:** maturity scores that aren't backed by evidence create the false confidence §34.2 describes ("worse than no SPOM at all").

## Step 4 — Implement the Security Control
`.github/workflows/assessment.yml` runs the unit tests, validates every claim, builds the workbook and writes the summary to the run page.

## Step 5 — Run the Pipeline
Push to `main`. Expected for the sample: `Score 4/12 — Transitioning; workbook written to out` and `6 passed`.

## Step 6 — Inspect the Result
Open **Actions → assessment → (run) → Summary** to see the score and the gap table. Download `maturity-workbook` and open `workbook.csv` in Excel.

## Step 7 — Introduce a Deliberate Failure
On a branch named `board-pack`, apply `lab-changes/apply-failures.md`. It inflates the score before a board meeting. Push and open a pull request.

## Step 8 — Observe the Control
Verified locally:
```
V2 C34-04: marked implemented without evidence in the repository
V3 C34-07: owner 'Security team' is not a named individual
V2 C34-07: marked implemented without evidence in the repository
V4 C34-11: evidence not reviewed within 12 months
```
Threat → Detection → Finding → Decision: governance misreporting → evidence and ownership rules → named findings → the inflated score can't be published.

## Step 9 — Remediate the Finding
Revert to honest statuses. For C34-07, name an individual for every row of Table 34.4 before claiming it. Re-review the board charter evidence and update `reviewed_on`.

## Step 10 — Validate the Fix
### Expected Result
- The workflow passes and the workbook shows the true score.

## Step 11 — Cleanup
Keep the repository private. Delete the branch. Archive the repository after the next annual review if you no longer need it.

## What You Should Have Learned
A programme assessment is evidence, not opinion. Named owners, dated evidence and a reproducible score turn Checklist 34.1 into a roadmap the board can rely on.

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
Add Table 34.4 (agent governance ownership) as `assessment/agent-ownership.yaml`, and make C34-07 count as implemented **only** when every row names an individual. Then link this lab to LAB-30, so that metric owners must match the owners named here.

---
**Validation status:** executed locally on 1 Oct 2026 (Python 3.11, pytest 9.0.3): 6/6 tests pass, the sample scores 4/12 (Transitioning) and the Step 8 findings are reproduced. actionlint and zizmor report no findings. **EXECUTION VALIDATION REQUIRED** on a GitHub-hosted runner.
