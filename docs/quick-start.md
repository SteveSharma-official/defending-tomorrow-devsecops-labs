# GitHub Lab Quick Start

This page teaches only the Git and GitHub you need for the labs. (It is reproduced in the book before LAB-00.)

## 1. Create a free GitHub account
Sign up at https://github.com/signup and enable two-factor authentication (**Settings → Password and authentication**). A single free personal account is sufficient for every GitHub-only lab — GitHub's terms allow one free personal account per person, so do not create extra accounts for the review exercises.

## 2. Install the tools
| Tool | Check | Notes |
|---|---|---|
| Git ≥ 2.40 | `git --version` | Windows: install *Git for Windows* and use **Git Bash** for all lab commands |
| Editor | — | VS Code recommended (YAML and Python extensions) |
| Python ≥ 3.12 (optional) | `python --version` | Only to run tests locally |
| GitHub CLI (optional) | `gh --version` | `gh auth login` avoids credential prompts |
| Docker (optional) | `docker --version` | Only for local container work; CI runners already have Docker |

Tell Git who you are (once per computer):
```bash
git config --global user.name  "Your Name"
git config --global user.email "ID+username@users.noreply.github.com"   # from GitHub → Settings → Emails
```

## 3. The five Git commands used in every lab
| Command | Meaning |
|---|---|
| `git switch -c <branch>` | Start a new branch for a change |
| `git add -A` | Stage all changes |
| `git commit -m "message"` | Record a snapshot |
| `git push -u origin <branch>` | Upload the branch to GitHub |
| `git switch main && git pull` | Return to `main` and fetch the latest |

## 4. Start any lab
```bash
git clone https://github.com/SteveSharma-official/defending-tomorrow-devsecops-labs          # the labs repository — once
cd defending-tomorrow-devsecops-labs
bash shared/scripts/start-lab.sh <lab-folder> ~/dt-labs/dt-lab-NN
```
Then on GitHub: **+ → New repository → name `dt-lab-NN` → Public → do not add README/.gitignore/licence → Create**, and:
```bash
cd ~/dt-labs/dt-lab-NN
git remote add origin https://github.com/<your-username>/dt-lab-NN.git
git push -u origin main
```

## 5. Reading a workflow (YAML in 60 seconds)
```yaml
name: example              # shown in the Actions tab
on: [push, pull_request]   # events that start it
permissions:               # rights of the automatic GITHUB_TOKEN — keep minimal
  contents: read
jobs:
  check:                   # a job = one fresh virtual machine
    runs-on: ubuntu-latest
    steps:                 # steps run in order; any failure stops the job
      - uses: actions/checkout@<40-character SHA> # vX.Y.Z   ← a reusable action, pinned
      - run: echo "a shell command"
```
Indentation is meaning in YAML: use spaces, never tabs.

## 6. Where to look
- **Actions tab** → workflow → run → job → step: logs.
- **Pull request → Checks**: pass/fail per job; red ✗ blocks merging when the check is required.
- **Security tab → Code scanning**: SARIF findings from CodeQL, Semgrep, gitleaks, Checkov, zizmor.
- **Settings → Rules / Environments / Secrets and variables**: where controls are configured.

## 7. Public repositories and safety
Most labs use **public** repositories because several controls are free only on public repositories under GitHub Free. Therefore: never commit real secrets, personal data or employer code to a lab repository; use only the synthetic values the labs generate.
