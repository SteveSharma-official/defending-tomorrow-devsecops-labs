# LAB-02 — Protect the Source Surface: Rulesets, CODEOWNERS and Signed Commits

| Chapter | Level | Difficulty | Estimated time | Cloud required? |
|---|---|---|---|---|
| Chapter 10 — Git Security Engineering (§10.3 Branch Protection, §10.4 Commit Signing) | 1 — Foundations | Beginner | 45–60 minutes | No |

> **Relationship to the Chapter 10 in-text lab.** The manuscript's lab assumes two reviewers and an organisation. This lab is designed so a **single reader on GitHub Free** can complete it; the two-reviewer and CODEOWNERS-approval variants are provided as optional steps for readers with a second account or a Team/Enterprise organisation.

## What You Will Build
A public repository whose `main` branch is protected by a **repository ruleset** (no deletion, no force push, linear history, pull request required, required status check, signed commits) and a `CODEOWNERS` file that assigns ownership of pipeline and infrastructure files. Commits are signed with an **SSH signing key** and show as *Verified*.

## What You Will Learn
- Create and import a GitHub repository ruleset and explain each rule's threat.
- Configure SSH commit signing and verify signatures locally and on GitHub.
- Show that a direct push, a force push and an unsigned commit are rejected server-side.
- Explain what signing does *not* prove (the author field can still be set arbitrarily).

## Prerequisites
**Required:** LAB-00; Git 2.34+ (SSH signing support); OpenSSH (`ssh-keygen`, included with Git for Windows).
**Optional:** GitHub CLI (`gh`) for the API import path; a second GitHub account to test review requirements; GPG if you prefer GPG signing (Chapter 10, §10.4).

## Estimated Time
**45–60 minutes**

## Difficulty
Beginner

## Architecture
```
developer ──signed commit──▶ feature branch ──PR──▶ ruleset "protect-main" on main
                                                     ├─ PR required (0 approvals solo / 1+ with a team)
                                                     ├─ status check "test" must pass (strict)
                                                     ├─ commits must carry verified signatures
                                                     ├─ linear history, no force push, no deletion
                                                     └─ bypass list: EMPTY
```

## Step 1 — Create or Open the Repository
```bash
bash shared/scripts/start-lab.sh chapter-10/lab-02-rulesets-codeowners-signing ~/dt-labs/dt-lab-02
cd ~/dt-labs/dt-lab-02
```
Edit `.github/CODEOWNERS` and replace `@YOUR-GITHUB-USERNAME` with your username. Commit (`git commit -am "Set code owner"`). Create an empty **public** repository `dt-lab-02`. Rulesets are available on public repositories with GitHub Free and on private repositories with Pro, Team and Enterprise Cloud (VERIFY CURRENT PRODUCT BEHAVIOUR).

## Step 2 — Clone the Repository
```bash
git remote add origin https://github.com/<your-username>/dt-lab-02.git
git push -u origin main
```
Wait for the `ci` workflow to pass once — the ruleset references its `test` check.

## Step 3 — Build the Lab: Configure SSH Commit Signing
**What you are doing:** creating a key used only for signing and telling Git and GitHub about it.
**Why it matters:** a signature binds a commit's content to a key you control, so tampering after signing is detectable (Chapter 10, §10.4).
```bash
ssh-keygen -t ed25519 -C "dt-lab signing key" -f ~/.ssh/dt_lab_signing
git config gpg.format ssh
git config user.signingkey ~/.ssh/dt_lab_signing.pub
git config commit.gpgsign true
# Optional local verification support:
echo "$(git config user.email) namespaces=\"git\" $(cat ~/.ssh/dt_lab_signing.pub)" >> ~/.ssh/allowed_signers
git config gpg.ssh.allowedSignersFile ~/.ssh/allowed_signers
```
On GitHub: **Settings (your profile) → SSH and GPG keys → New SSH key → Key type: Signing Key** → paste the contents of `~/.ssh/dt_lab_signing.pub`.
Your commit email must be a verified address on your GitHub account (or your `ID+username@users.noreply.github.com` address) for GitHub to show *Verified*.

These settings are applied to this repository only (no `--global`), so other work is unaffected.

## Step 4 — Implement the Security Control: Import the Ruleset
**Web UI:** **Repository → Settings → Rules → Rulesets → New ruleset → Import a ruleset** → choose `governance/main-ruleset.json` → review → **Create**.
**CLI alternative:**
```bash
gh api --method POST repos/<your-username>/dt-lab-02/rulesets --input governance/main-ruleset.json
```
| Rule | Threat it counters (Chapter 10) |
|---|---|
| `deletion` | Destroying protected history |
| `non_fast_forward` | History rewriting / force push |
| `required_linear_history` | Hidden changes in merge commits |
| `required_signatures` | Commit tampering and unattributable changes |
| `pull_request` | Unreviewed direct pushes |
| `required_status_checks` (strict) | Merging code that fails tests or security checks, or that is stale versus `main` |
| empty `bypass_actors` | Administrators silently skipping controls |

## Step 5 — Run the Pipeline
Make a signed change through a pull request:
```bash
git switch -c signed-change
echo "Signed change for LAB-02" >> app/README.md
git commit -am "LAB-02: signed change"
git log --show-signature -1     # expect: Good "git" signature ...
git push -u origin signed-change
```
Open a pull request. The `test` check runs; when it passes, **Squash and merge** or **Rebase and merge** is available (merge commits are blocked by linear history).

## Step 6 — Inspect the Result
- **Pull request → Commits:** each commit shows **Verified**.
- **Pull request → Checks:** `ci / test` passed.
- **Settings → Rules → Insights:** the ruleset evaluation for your merge is recorded.

`[SCREENSHOT REQUIRED — GITHUB PULL REQUEST SHOWING A "VERIFIED" COMMIT BADGE AND THE REQUIRED "test" CHECK]`

## Step 7 — Introduce Deliberate Security Failures (Red-Team the Controls)
> These attempts are made against your own lab repository only.

| # | Attempt | Command |
|---|---|---|
| A1 | Direct push to `main` | `git switch main && git pull && git commit --allow-empty -m "direct" && git push` |
| A2 | Unsigned commit via PR | `git switch -c unsigned && git commit --allow-empty --no-gpg-sign -m "unsigned" && git push -u origin unsigned` then open a PR |
| A3 | Spoofed author, valid signature | `git switch -c spoof && git commit --allow-empty --author="Chief Executive <ceo@example.com>" -m "spoofed" && git push -u origin spoof` then open a PR |
| A4 | Force push to `main` | `git switch main && git commit --amend --allow-empty -m "rewrite" && git push --force` |

## Step 8 — Observe the Security Control
| # | Expected result | Threat → Detection → Decision |
|---|---|---|
| A1 | Push **rejected**: changes must be made through a pull request | Unreviewed change → ruleset → blocked |
| A2 | PR **cannot merge**: commits must have verified signatures | Unattributable change → `required_signatures` → blocked |
| A3 | Signature **valid** (Verified shows your identity as signer) but the author field shows the spoofed name | Signing proves *who signed*, not *who is named as author* → reviewer must check signer vs author |
| A4 | Push **rejected**: cannot force-push | History rewrite → `non_fast_forward` → blocked |

Record the exact error text of A1 and A4 — they are your evidence that the control operates, not just that it is configured (Chapter 10, Takeaway 5).

## Step 9 — Remediate the Finding
- A1/A4: reset local `main` to the remote (`git fetch && git reset --hard origin/main`) and use pull requests.
- A2: re-sign the branch commits: `git rebase --exec 'git commit --amend --no-edit -S' main`, then `git push --force-with-lease` (force-push to your *feature* branch is permitted).
- A3: close the PR. Organisational control: require that the signer matches the author (a custom status check, or restricting merges to reviewers who check the *Verified* signer).

## Step 10 — Validate the Fix
### Expected Result
- A1 and A4 rejected with ruleset messages; A2 blocked until re-signed; A3 visibly inconsistent in the PR.
- `main` history contains only verified commits (`git log --show-signature main`).

**Optional (second account or Team plan):** set `required_approving_review_count` to `1` and `require_code_owner_review` to `true`, then modify `.github/workflows/ci.yml` in a PR. The PR now waits for a code-owner approval. You cannot approve your own pull request.

## Step 11 — Cleanup
- Delete feature branches; close unmerged PRs.
- Remove the signing key from GitHub (**Settings → SSH and GPG keys**) if you created it only for this lab, and delete `~/.ssh/dt_lab_signing*`.
- Optionally delete the repository.

## What You Should Have Learned
Branch protection is only as strong as its bypass list and its evidence. Rulesets block direct, unsigned and history-rewriting changes server-side; signing proves integrity and signer identity but not authorship claims.

## Lab Completion Checklist
- [ ] Repository created
- [ ] Code committed (signed)
- [ ] Pipeline executed
- [ ] Security control triggered (A1–A4)
- [ ] Finding identified
- [ ] Finding remediated
- [ ] Pipeline passed
- [ ] Resources cleaned up

## Further Challenge
Add a `.gitmodules` file pointing to an untrusted URL in a pull request (Chapter 10, Attack 5). With `require_code_owner_review` enabled on a Team/Enterprise organisation, confirm that the change waits for the code owner.

---
**Validation status:** ruleset JSON parsed successfully; field names checked against the GitHub REST rulesets schema as documented September 2026 (VERIFY CURRENT PRODUCT BEHAVIOUR). Rejection messages are not reproduced here because they were not captured from a live run. **EXECUTION VALIDATION REQUIRED.**
