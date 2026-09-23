# Defending Tomorrow — DevSecOps Book Labs

Hands-on GitHub laboratories for **_Defending Tomorrow: Building Secure Cloud-Native Enterprises with DevSecOps, Platform Engineering and AI_** by **Steve Sharma** (Cybersecurity Link).

The book explains *why* and *how* security becomes a property of the software factory. These labs let you **READ → UNDERSTAND → PRACTICE → VALIDATE → APPLY**: every lab introduces one control, has you break it safely, observe the detection, remediate, and prove the fix — with cleanup instructions so nothing is left running.

> **Status: pre-publication (September 2026) — repository is private until the book is released; make it public at publication so readers can clone it.** Workflows and code have been statically validated and, where marked, executed locally. Each lab states its validation status; items marked **EXECUTION VALIDATION REQUIRED** have not yet been run end-to-end on GitHub or in a cloud account.

## Who This Repository Is For
- **Students and career changers** who understand security concepts and want practical pipeline experience.
- **Cybersecurity professionals** moving from assessment to engineering controls.
- **DevOps, platform and security engineers** implementing gates, policy-as-code and supply-chain controls.
- **Architects** who need reference implementations to evaluate designs.
- **CISOs and GRC practitioners** who want to see how controls produce evidence (LAB-14, LAB-16, CAPSTONE).

No prior GitHub Actions experience is assumed — start with the [GitHub Lab Quick Start](docs/quick-start.md).

## How to Use This Repository
1. **Create a free GitHub account** and read [docs/quick-start.md](docs/quick-start.md).
2. **Clone this repository** (fork it only if you want to propose changes):
   ```bash
   git clone https://github.com/SteveSharma-official/defending-tomorrow-devsecops-labs
   cd defending-tomorrow-devsecops-labs
   ```
3. **Select the chapter** you are reading — each chapter's *Hands-On Lab* callout names the lab.
4. **Select the lab** folder and open its `README.md`.
5. **Create your own lab repository** from the lab's starter:
   ```bash
   bash shared/scripts/start-lab.sh chapter-10/lab-03-secret-detection-in-depth ~/dt-labs/dt-lab-03
   ```
   then create an empty **public** repository with the same name on GitHub and push.
6. **Complete the exercise** — every lab follows the same 11 steps, including a deliberate, safe failure.
7. **Validate the result** against the lab's *Expected Result* and *Completion Checklist*.
8. **Clean up** — especially for cloud labs (see [docs/cost-and-cleanup.md](docs/cost-and-cleanup.md)).

Workflows inside `starter/` folders do **not** run in this repository; they run only in the lab repository you create, so each lab is isolated.

## Repository Layout
```
defending-tomorrow-devsecops-labs/
├── README.md · LICENSE · CONTRIBUTING.md · SECURITY.md
├── docs/                 quick-start, lab-roadmap, cost-and-cleanup, troubleshooting, lab-template, action-pins
├── shared/
│   ├── sample-apps/dt-orders-api/   secure baseline Flask + SQLite service used by most labs
│   └── scripts/                     start-lab.sh, make-test-secret.sh (synthetic credentials only)
├── chapter-00/ … chapter-31/        one folder per lab: README.md, starter/, (solution/), lab-changes/
├── cloud/aws/ · cloud/azure/        labs that need a cloud account (clearly marked)
├── capstone/secure-devsecops-pipeline/
└── .github/workflows/validate-labs.yml   keeps this repository's own lab code honest
```

## Prerequisites
**Common (all labs):** free GitHub account · Git ≥ 2.40 (Windows: Git Bash) · a code editor.
**Frequently useful (optional):** Python ≥ 3.12 · GitHub CLI · Docker.
**Cloud labs only:** AWS CLI v2 and a sandbox AWS account (AWS-LAB-01/02) · Azure CLI ≥ 2.60 and a sandbox subscription (AZ-LAB-01/02).
Exact prerequisites, **Required** versus **Optional**, are listed in every lab.

## Cloud Cost Warning
LAB-00 to LAB-19 and the CAPSTONE are designed to run on **GitHub Free with public repositories**. That reflects GitHub's published plan features in September 2026 and may change — verify before relying on it.
The **AWS-LAB** and **AZ-LAB** labs create real cloud resources. **They can incur charges.** Use a sandbox account, set a budget alert first, follow each lab's cleanup section in full, and verify current pricing and free-tier eligibility before starting. Nothing in this repository is promised to remain free.

## Lab Index
| Lab | Chapter | Topic | Difficulty | Cloud | Folder |
|---|---|---|---|---|---|
| [LAB-00](chapter-00/lab-00-github-quick-start/README.md) | Ch 0 | GitHub Lab Quick Start: Your First Security-Aware Pipeline | Beginner | No | `chapter-00/lab-00-github-quick-start` |
| [LAB-01](chapter-04/lab-01-threat-model-as-code/README.md) | Ch 4 | Threat Model as Code | Beginner | No | `chapter-04/lab-01-threat-model-as-code` |
| [LAB-02](chapter-10/lab-02-rulesets-codeowners-signing/README.md) | Ch 10 | Protect the Source Surface: Rulesets, CODEOWNERS and Signed Commits | Beginner | No | `chapter-10/lab-02-rulesets-codeowners-signing` |
| [LAB-03](chapter-10/lab-03-secret-detection-in-depth/README.md) | Ch 10 | Secret Detection in Depth | Beginner | No | `chapter-10/lab-03-secret-detection-in-depth` |
| [LAB-04](chapter-11/lab-04-harden-github-actions/README.md) | Ch 11 | Harden GitHub Actions: Injection, Permissions and Pinning | Intermediate | No | `chapter-11/lab-04-harden-github-actions` |
| [LAB-05](chapter-19/lab-05-sast-codeql-semgrep/README.md) | Ch 19* (interim: Ch 11) | SAST in the Pull Request: CodeQL and Custom Semgrep Rules | Intermediate | No | `chapter-19/lab-05-sast-codeql-semgrep` |
| [LAB-06](chapter-19/lab-06-sca-dependency-security/README.md) | Ch 19* (interim: Ch 11), 13 | Software Composition Analysis | Intermediate | No | `chapter-19/lab-06-sca-dependency-security` |
| [LAB-07](chapter-12/lab-07-iac-scanning/README.md) | Ch 12 | Infrastructure as Code Scanning | Intermediate | No | `chapter-12/lab-07-iac-scanning` |
| [LAB-08](chapter-17/lab-08-policy-as-code-conftest/README.md) | Ch 12, 17* | Policy as Code: Evaluate a Terraform Plan | Intermediate | No | `chapter-17/lab-08-policy-as-code-conftest` |
| [LAB-09](chapter-14/lab-09-container-hardening-scanning/README.md) | Ch 14 | Container Hardening and Image Scanning | Intermediate | No | `chapter-14/lab-09-container-hardening-scanning` |
| [LAB-10](chapter-14/lab-10-k8s-admission-kyverno/README.md) | Ch 14 | Kubernetes Admission Control as Code with Kyverno | Intermediate | No (optional kind) | `chapter-14/lab-10-k8s-admission-kyverno` |
| [LAB-11](chapter-19/lab-11-dast-zap-baseline/README.md) | Ch 19* (interim: Ch 11) | DAST in the Pipeline: OWASP ZAP Baseline | Intermediate | No | `chapter-19/lab-11-dast-zap-baseline` |
| [LAB-12](chapter-13/lab-12-sbom-vex/README.md) | Ch 13 | SBOM and VEX | Advanced | No | `chapter-13/lab-12-sbom-vex` |
| [LAB-13](chapter-13/lab-13-provenance-signing/README.md) | Ch 13, 11 | Build Provenance and Keyless Signing | Advanced | No (GHCR) | `chapter-13/lab-13-provenance-signing` |
| [LAB-14](chapter-11/lab-14-security-gates-environments/README.md) | Ch 15, 11 | Security Gates and Deployment Environments | Advanced | No | `chapter-11/lab-14-security-gates-environments` |
| [LAB-15](chapter-16/lab-15-ai-assisted-pr-gate/README.md) | Ch 16 | Govern AI-Assisted Code: Tiered Review Gate | Advanced | No | `chapter-16/lab-15-ai-assisted-pr-gate` |
| [LAB-16](chapter-18/lab-16-compliance-evidence-pipeline/README.md) | Ch 18 | Compliance as Code: Evidence Pipeline | Advanced | No | `chapter-18/lab-16-compliance-evidence-pipeline` |
| [LAB-17](chapter-23/lab-17-detection-as-code-sigma/README.md) | Ch 23 | Detection as Code with Sigma | Advanced | No | `chapter-23/lab-17-detection-as-code-sigma` |
| [LAB-18](chapter-31/lab-18-agent-tool-allowlist-opa/README.md) | Ch 31 | Govern Agent Tool Access with Policy | Advanced | No | `chapter-31/lab-18-agent-tool-allowlist-opa` |
| [LAB-19](chapter-29/lab-19-llm-guardrail-regression/README.md) | Ch 29, 30 | LLM Guardrail Regression Testing | Advanced | No | `chapter-29/lab-19-llm-guardrail-regression` |
| [AWS-LAB-01](cloud/aws/aws-lab-01-github-oidc-ecr/README.md) | Ch 6, 11; App A | Keyless CI to AWS: GitHub OIDC and ECR | Advanced | Yes — AWS | `cloud/aws/aws-lab-01-github-oidc-ecr` |
| [AWS-LAB-02](cloud/aws/aws-lab-02-terraform-drift-gate/README.md) | Ch 12, 8, 17* | Gated Terraform Delivery to AWS with Drift Detection | Advanced | Yes — AWS | `cloud/aws/aws-lab-02-terraform-drift-gate` |
| [AZ-LAB-01](cloud/azure/az-lab-01-github-oidc-bicep/README.md) | Ch 6, 12; App B | Keyless CI to Azure: OIDC, Managed Identity, Bicep | Advanced | Yes — Azure | `cloud/azure/az-lab-01-github-oidc-bicep` |
| [AZ-LAB-02](cloud/azure/az-lab-02-azure-policy-as-code/README.md) | App B, Ch 17* | Azure Policy as Code | Advanced | Yes — Azure | `cloud/azure/az-lab-02-azure-policy-as-code` |
| [CAPSTONE](capstone/secure-devsecops-pipeline/README.md) | Parts I–IV | Build a Secure DevSecOps Pipeline | Advanced | No (optional cloud) | `capstone/secure-devsecops-pipeline` |

Full roadmap with chapter sections, skills and progression: [docs/lab-roadmap.md](docs/lab-roadmap.md).

## Safety Rules for Every Lab
- Only synthetic data and generated, meaningless credentials are used. **Never** place real secrets, customer data or employer code in a lab repository.
- Intentionally insecure files are labelled *INTENTIONALLY INSECURE — lab use only* and live in `lab-changes/` until you apply them in Step 7.
- Scan and attack **only** repositories and resources you own.
- Pin actions by SHA and verify downloaded tools by checksum — the labs model this, because security tooling is itself a supply-chain target (see [docs/action-pins.md](docs/action-pins.md)).

## Troubleshooting
Common Git, GitHub and pipeline problems and fixes: [docs/troubleshooting.md](docs/troubleshooting.md). Quick fixes:
- **Push rejected, "fetch first"** → the GitHub repository was not created empty: `git pull --rebase origin main`.
- **Workflow never starts** → the file must be in `.github/workflows/` on the branch you pushed; check *Settings → Actions*.
- **`Resource not accessible by integration`** → the job lacks a specific permission; add it to that job only.
- **Checksum mismatch** → stop and investigate; do not bypass.

## About the Author
Steve Sharma — Founder and Principal Cybersecurity Architect, Cybersecurity Link (Melbourne). Author page: https://amazon.com/author/stevesharma · LinkedIn: https://linkedin.com/in/stevesharma-cybersecuritylink

## Licence
Lab code and configuration: MIT (see [LICENSE](LICENSE)). The book's text, figures and diagrams are © Steve Sharma and are **not** licensed by this repository.
