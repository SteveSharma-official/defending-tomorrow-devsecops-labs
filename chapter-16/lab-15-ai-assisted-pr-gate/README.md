# LAB-15 — Govern AI-Assisted Code: A Tiered Review Gate for AI-Tagged Pull Requests

| Chapter | Level | Difficulty | Estimated time | Cloud required? |
|---|---|---|---|---|
| Chapter 16 — AI-Assisted Software Development (§16.4 Secure SDLC Adaptations, §16.5 Governance) | 3 — Advanced | Advanced | 45–60 minutes | No |

## What You Will Build
A pull-request gate that classifies changed files (security-critical / security-adjacent / standard) and, for PRs labelled `ai-assisted` or `ai-generated`, requires the review tier defined in Chapter 16: security-critical changes need **two approvals including one designated security reviewer, neither being the author**. The gate's own code is unit-tested and is loaded from the **base branch** so a PR cannot weaken its own gate.

## What You Will Learn
- Translate a governance rule ("AI-generated security-critical code needs expert review") into an enforceable, tested check.
- Collect trustworthy PR facts from the GitHub API rather than from PR-controlled content.
- Handle review semantics correctly: latest review per reviewer, no self-approval.
- Recognise the limits: labels are self-declared; pair the gate with detection (Chapter 16 §16.6).

## Prerequisites
**Required:** LAB-02 (rulesets and required checks); Chapter 16 §16.4–16.5.
**Optional:** a trusted collaborator (colleague or study partner with their own GitHub account) to perform real reviews. Do **not** create a second personal account for this — GitHub's terms allow one free personal account per person.

> **Corrections to the manuscript listing (Chapter 16).** The published gate builds `reviewers` as a list of author strings and then calls `r.get("is_security_expert")` on each string (an `AttributeError` at runtime); counts superseded approvals; allows the author to count toward the requirement; and matches substrings such as `token` in `tokenizer`. `tools/ai_pr_gate.py` fixes all four and is covered by seven unit tests.

## Estimated Time
**45–60 minutes**

## Difficulty
Advanced

## Architecture
```
PR (label ai-assisted) ─▶ ai-pr-gate.yml (checkout BASE sha — gate code cannot be changed by the PR)
                           ├─ pytest tools/tests (7 tests)
                           ├─ gh api: PR author, labels, files (paginated), reviews
                           └─ ai_pr_gate.py ─▶ critical? → ≥1 security reviewer + ≥2 approvals, author excluded
                                             adjacent? → ≥1 approval
ruleset: "gate" is a required status check on main
```

## Step 1 — Create or Open the Repository
```bash
bash shared/scripts/start-lab.sh chapter-16/lab-15-ai-assisted-pr-gate ~/dt-labs/dt-lab-15
```
Edit `.github/security-reviewers.txt`: replace `YOUR-GITHUB-USERNAME` with your collaborator's username (or your own, for the solo path). Commit. Create an empty **public** repository `dt-lab-15`.

## Step 2 — Clone the Repository
```bash
cd ~/dt-labs/dt-lab-15
git remote add origin https://github.com/<your-username>/dt-lab-15.git
git push -u origin main
```
Create the labels: **Issues → Labels → New label** → `ai-assisted` (and `ai-generated`).

## Step 3 — Build the Lab
Run the tests locally: `pip install pytest && pytest -q tools/tests` → `7 passed` (verified). Read `classify()` and `current_approvers()`.

## Step 4 — Implement the Security Control
Add `gate` as a required status check in a ruleset on `main` (LAB-02 pattern). Keep `.github/` under CODEOWNERS so changes to the reviewer list are themselves reviewed.

## Step 5 — Run the Pipeline
Open any small PR **without** the label. Expected: `AI_GATE: NOT_AI_TAGGED: standard review process applies` and a green check.

## Step 6 — Inspect the Result
**PR → Checks → ai-pr-gate / gate → Collect PR facts** prints the JSON the decision is based on — author, labels, files, reviews. This is your audit evidence.

## Step 7 — Introduce a Deliberate Security Failure
```bash
git switch -c ai-token-check
mkdir -p app/auth && cp lab-changes/auth_helper.py.txt app/auth/token_check.py
git add -A && git commit -m "LAB-15: AI-assisted token comparison helper" && git push -u origin ai-token-check
```
Open a PR and add the label **ai-assisted**.

## Step 8 — Observe the Security Control
Expected (verified locally with equivalent input):
```
::error::AI_GATE: SECURITY_EXPERT_REVIEW_REQUIRED for ['app/auth/token_check.py']
::error::AI_GATE: MINIMUM_REVIEWERS_NOT_MET: 0/2 approvals
```
Threat → Detection → Finding → Decision: plausible-looking AI-generated code in an authentication path → path classification + AI label → missing expert review → merge blocked.

## Step 9 — Remediate the Finding
- **With a collaborator:** ask them to review and approve (they must be in `security-reviewers.txt`); a second approval comes from another reviewer. The `pull_request_review` event re-runs the gate automatically.
- **Solo path:** you cannot approve your own PR, and the gate correctly refuses to count you. Validate the passing path with the unit test `test_ai_critical_with_security_and_second_approval_passes`, then close the PR. This is the honest outcome: a solo developer cannot satisfy a two-person rule.

## Step 10 — Validate the Fix
### Expected Result
- With two qualifying approvals: `AI_GATE: APPROVED: tiers met …` and the PR becomes mergeable.
- A later *Request changes* from the security reviewer turns the gate red again (latest-review semantics).

## Step 11 — Cleanup
Close or merge the PR, delete the branch, remove collaborators you added (**Settings → Collaborators**), optionally delete the repository.

## What You Should Have Learned
AI-assistance governance is enforceable when it is expressed as a tested gate over trustworthy facts. Its weakest input — the self-declared label — must be complemented by detection and culture, which Chapter 16 §16.6 addresses.

## Lab Completion Checklist
- [ ] Repository created
- [ ] Code committed
- [ ] Pipeline executed
- [ ] Security control triggered
- [ ] Finding identified
- [ ] Finding remediated (or two-person rule demonstrated)
- [ ] Pipeline passed
- [ ] Resources cleaned up

## Further Challenge
Add a heuristic job that *suggests* the `ai-assisted` label when commit trailers such as `Co-authored-by:` reference an AI coding agent's account, and discuss the privacy and accuracy trade-offs.

---
**Validation status:** 7/7 unit tests pass (pytest 9.1.1); gate executed locally on Step 7-equivalent input (exit 1, messages above); jq assembly tested with sample API shapes; workflow checked with actionlint/zizmor. Not executed on GitHub. **EXECUTION VALIDATION REQUIRED.**
