# Book Lab Roadmap

**Numbering convention.** Cloud-neutral labs that run on GitHub (and optionally locally) are `LAB-00` … `LAB-30`, numbered by progression level (Foundations → Practitioner → Advanced); each chapter's Hands-On Lab callout shows where a lab is introduced in reading order. Labs that require a cloud account carry the provider prefix — `AWS-LAB-NN`, `AZ-LAB-NN` — so readers can see the cost and account requirement from the identifier alone. The integrated final lab is `CAPSTONE`.

Where a lab lists more than one chapter, the first is the chapter whose Hands-On Lab callout introduces it; the others reinforce it.

| Chapter | Lesson / section | Lab ID | Lab title | Skill | Level | Difficulty | Est. time | Cloud required? | Repository path |
|---|---|---|---|---|---|---|---|---|---|
| Ch 0 | §0.4.2 Structural Elements — Hands-On Labs | **LAB-00** | GitHub Lab Quick Start: Your First Security-Aware Pipeline | Least-privilege, SHA-pinned CI with a security regression test | 1 Foundations | Beginner | 30–40 min | No | `chapter-00/lab-00-github-quick-start` |
| Ch 4 | Integrating Threat Modeling into the Software Factory | **LAB-01** | Threat Model as Code | Threat-model completeness gate (STRIDE + agent extension) | 1 Foundations | Beginner | 40–50 min | No | `chapter-04/lab-01-threat-model-as-code` |
| Ch 10 | §10.3 Branch Protection / §10.4 Commit Signing | **LAB-02** | Protect the Source Surface: Rulesets, CODEOWNERS and Signed Commits | Rulesets, SSH commit signing, red-team of source controls | 1 Foundations | Beginner | 45–60 min | No | `chapter-10/lab-02-rulesets-codeowners-signing` |
| Ch 10 | §10.5 Secret Scanning Defence in Depth | **LAB-03** | Secret Detection in Depth | Pre-commit hook, push protection, CI history scan with SARIF | 1 Foundations | Beginner | 40–50 min | No | `chapter-10/lab-03-secret-detection-in-depth` |
| Ch 11 | §11.4 Hardening the Build Environment | **LAB-04** | Harden GitHub Actions: Injection, Permissions and Pinning | Workflow security linting (actionlint, zizmor), SHA pinning, least-privilege tokens | 2 Practitioner | Intermediate | 45–60 min | No | `chapter-11/lab-04-harden-github-actions` |
| Ch 19, 11 | §19.3 SAST in the Pull Request: CodeQL and Custom Semgrep Rules | **LAB-05** | SAST in the Pull Request: CodeQL and Custom Semgrep Rules | SAST, custom rules, code-scanning merge gate | 2 Practitioner | Intermediate | 45–60 min | No | `chapter-19/lab-05-sast-codeql-semgrep` |
| Ch 19, 13 | §19.4 SCA and Dependency Governance | **LAB-06** | Software Composition Analysis | Dependency review gate, pip-audit, Dependabot | 2 Practitioner | Intermediate | 35–45 min | No | `chapter-19/lab-06-sca-dependency-security` |
| Ch 12 | §12.4 IaC Scanning | **LAB-07** | Infrastructure as Code Scanning | Checkov + Trivy config on Terraform, in-code exceptions | 2 Practitioner | Intermediate | 40–50 min | No | `chapter-12/lab-07-iac-scanning` |
| Ch 17, 12 | §17.5.2 Pre-Apply (IaC Deployment); §12.5 Policy Validation Pre-Apply | **LAB-08** | Policy as Code: Evaluate a Terraform Plan | OPA/Rego v1, Conftest, policy unit tests | 2 Practitioner | Intermediate | 45–55 min | No | `chapter-17/lab-08-policy-as-code-conftest` |
| Ch 14 | §14.2 Docker Image Hardening | **LAB-09** | Container Hardening and Image Scanning | Hardened Dockerfile, artefact-property gates, Trivy image scan | 2 Practitioner | Intermediate | 45–60 min | No | `chapter-14/lab-09-container-hardening-scanning` |
| Ch 14 | §14.5 Admission Control | **LAB-10** | Kubernetes Admission Control as Code with Kyverno | PSS restricted, immutable images, limits; kyverno test/apply | 2 Practitioner | Intermediate | 40–50 min | No (optional kind) | `chapter-14/lab-10-k8s-admission-kyverno` |
| Ch 19 | §19.5 DAST Against Ephemeral Targets and API Security Testing | **LAB-11** | DAST in the Pipeline: OWASP ZAP Baseline | DAST against an ephemeral target, rules-file tuning | 2 Practitioner | Intermediate | 35–45 min | No | `chapter-19/lab-11-dast-zap-baseline` |
| Ch 13 | §13.3 SBOM / §13.3.2 VEX | **LAB-12** | SBOM and VEX | CycloneDX + SPDX SBOMs, SBOM scanning, OpenVEX | 3 Advanced | Advanced | 45–60 min | No | `chapter-13/lab-12-sbom-vex` |
| Ch 13, 11, 32 | §13.4 Sigstore and Cosign; §32.3.2 Deployment-Time Verification | **LAB-13** | Build Provenance and Keyless Signing | Digest references, SLSA provenance attestation, Cosign keyless, verification | 3 Advanced | Advanced | 50–70 min | No (GHCR) | `chapter-13/lab-13-provenance-signing` |
| Ch 15, 11 | §15.3 Golden Paths as Security Controls (builds on §11.6) | **LAB-14** | Security Gates and Deployment Environments | OPA release decision, environments, required reviewers | 3 Advanced | Advanced | 50–70 min | No | `chapter-11/lab-14-security-gates-environments` |
| Ch 16 | §16.4 Secure SDLC Adaptations for AI-Assisted Development | **LAB-15** | Govern AI-Assisted Code: Tiered Review Gate | AI-tagged PR gate, trustworthy PR facts, two-person rule | 3 Advanced | Advanced | 45–60 min | No | `chapter-16/lab-15-ai-assisted-pr-gate` |
| Ch 18 | §18.7 Building the Evidence Pipeline | **LAB-16** | Compliance as Code: Evidence Pipeline | Framework-mapped, hashed, attested evidence | 3 Advanced | Advanced | 50–60 min | No | `chapter-18/lab-16-compliance-evidence-pipeline` |
| Ch 23 | §23.2 Detection-as-Code Lifecycle | **LAB-17** | Detection as Code with Sigma | Sigma validation, detection unit tests, SIEM conversion | 3 Advanced | Advanced | 45–60 min | No | `chapter-23/lab-17-detection-as-code-sigma` |
| Ch 31 | §31.5 Tool Security and Allowlisting | **LAB-18** | Govern Agent Tool Access with Policy | Per-agent tool allowlist in OPA, invariants, replay corpus | 3 Advanced | Advanced | 45–60 min | No | `chapter-31/lab-18-agent-tool-allowlist-opa` |
| Ch 29, 30 | §29.3 Prompt Injection / §29.7 Integration Patterns | **LAB-19** | LLM Guardrail Regression Testing | Measured guardrails: detection and false-positive thresholds | 3 Advanced | Advanced | 40–50 min | No | `chapter-29/lab-19-llm-guardrail-regression` |
| Ch 22 | §22.4.2 Instrumenting for Security Attributes / §22.5.2 Minimum Security Log Schema / §22.6 Telemetry Quality | **LAB-20** | Security Telemetry Pipeline: Validate and Gate an OpenTelemetry Collector Config | Collector config validation, security-fitness checks, schema completeness | 3 Advanced | Intermediate | 40–50 min | No | `chapter-22/lab-20-security-telemetry-pipeline` |
| Ch 24, 23 | §24.2 Hypothesis-Driven Hunting Framework / §24.6.1 Agent Hunting Query | **LAB-21** | Hypothesis-Driven Hunting as Code | DuckDB hunts, ground-truth tests, hunter-to-rule feedback gate | 3 Advanced | Advanced | 50–60 min | No | `chapter-24/lab-21-hypothesis-driven-hunt` |
| Ch 25 | §25.3 Evidence Preservation / §25.5 Containment Sequence Model | **LAB-22** | Evidence-First Containment | Containment playbook as code, hashed evidence manifest, kind exercise | 3 Advanced | Advanced | 45–60 min | No (optional kind) | `chapter-25/lab-22-evidence-first-containment` |
| Ch 26, 13 | §26.4 Recovery Engineering / §26.4.2 Runbook-as-Code | **LAB-23** | Verified Recovery | Compromise-aware restore target, cosign + provenance verification | 3 Advanced | Advanced | 45–60 min | No (GHCR) | `chapter-26/lab-23-verified-recovery` |
| Ch 27 | §27.2 Security Chaos Engineering Framework | **LAB-24** | Security Chaos Experiment | Four-element hypothesis, guard rails, measured detection/response/recovery | 3 Advanced | Advanced | 45–60 min | No (optional kind) | `chapter-27/lab-24-security-chaos-experiment` |
| Ch 28 | §28.4 Measuring AI SOC Value | **LAB-25** | Evaluate a SOC Copilot | Outcome-metric release gate, injection resistance, citation validity | 3 Advanced | Intermediate | 35–45 min | No | `chapter-28/lab-25-evaluate-soc-copilot` |
| Ch 30 | §30.3.1 Access Control for Vector Stores / §30.7 Retrieval Validation | **LAB-26** | Permission-Aware Retrieval | Pre-filtering, non-inferability tests, provenance and injection stages | 3 Advanced | Advanced | 40–50 min | No | `chapter-30/lab-26-permission-aware-retrieval` |
| Ch 32, 13 | §32.3 Model Signing / §32.4 AI-BOM / §32.5 Dataset Lineage | **LAB-27** | Model Signing and AI-BOM | CycloneDX 1.6 ML-BOM, cosign sign-blob keyless, three-stage deployment verification | 3 Advanced | Advanced | 50–60 min | No | `chapter-32/lab-27-model-signing-ai-bom` |
| Ch 33 | §33.2 Staged Autonomy Model / §33.4.3 Containment Maturity / §33.6.2 Policy as Guardrails | **LAB-28** | Staged Autonomy as Policy | Rego autonomy policy, containment prerequisite, invariants, decision replay | 3 Advanced | Advanced | 45–60 min | No | `chapter-33/lab-28-staged-autonomy-policy` |
| Ch 34 | Checklist 34.1 Security Program Maturity Assessment | **LAB-29** | Programme Maturity Self-Assessment as Code | Evidence-backed scoring, named ownership, board workbook | 2 Practitioner | Beginner | 30–40 min | No | `chapter-34/lab-29-programme-self-assessment` |
| Ch 35, 18 | §35.3 Core Operational Metrics Catalog / §35.6 Anti-Patterns | **LAB-30** | Metrics from Evidence | Table 35.2 metrics from sealed evidence, anti-gaming integrity checks | 3 Advanced | Intermediate | 35–45 min | No | `chapter-35/lab-30-metrics-from-evidence` |
| Ch 6, 11; App A | Identity Federation: Bridging Human and Machine Identity | **AWS-LAB-01** | Keyless CI to AWS: GitHub OIDC and ECR | OIDC federation, branch-scoped trust policy, least-privilege ECR | 3 Advanced | Advanced | 50–70 min | Yes — AWS | `cloud/aws/aws-lab-01-github-oidc-ecr` |
| Ch 12, 8, 17 | §12.6 State File Security / §12.7 Drift Detection | **AWS-LAB-02** | Gated Terraform Delivery to AWS with Drift Detection | Plan-time scanning and policy, approved apply, drift alarm | 3 Advanced | Advanced | 75–90 min | Yes — AWS | `cloud/aws/aws-lab-02-terraform-drift-gate` |
| Ch 6, 12; App B | Identity Federation / Conditional Access | **AZ-LAB-01** | Keyless CI to Azure: OIDC, Managed Identity, Bicep | Workload identity federation, environment-bound subject, Bicep scanning, what-if | 3 Advanced | Advanced | 60–75 min | Yes — Azure | `cloud/azure/az-lab-01-github-oidc-bicep` |
| Ch 17; App B | §17.5.3 Admission (control-plane policy); Appendix B.1 Azure Landing Zone Security Architecture | **AZ-LAB-02** | Azure Policy as Code | Custom policy definitions, Audit→Deny staging, exemptions | 3 Advanced | Advanced | 50–65 min | Yes — Azure | `cloud/azure/az-lab-02-azure-policy-as-code` |
| Parts I–IV; Ch 36 | End of Part IV (Chapter 21 bridge); referenced again in Chapter 36 §36.7 | **CAPSTONE** | Build a Secure DevSecOps Pipeline | Integrated software-factory pipeline with evidence | 4 Capstone | Advanced | 3–4 h | No (optional cloud) | `capstone/secure-devsecops-pipeline` |

## Progression
| Level | Labs | Focus |
|---|---|---|
| 1 — Foundations | LAB-00 to LAB-03 | Repository, Git basics, first workflow, threat model as code, source-surface controls |
| 2 — Practitioner | LAB-04 to LAB-11, LAB-29 | Pipeline hardening, SAST, SCA, IaC scanning, policy-as-code, containers, admission control, DAST |
| 3 — Advanced | LAB-12 to LAB-28, LAB-30, AWS-LAB-01/02, AZ-LAB-01/02 | Supply chain (SBOM, VEX, provenance, signing), release gates, AI governance, compliance evidence, detection-as-code, telemetry, hunting, containment, recovery, chaos, AI SOC evaluation, RAG and model supply chain, autonomy policy, metrics, cloud identity and policy |
| 4 — Capstone | CAPSTONE | Integrated, evidenced, verify-before-deploy pipeline |

## Chapters without a dedicated lab (by design)
| Chapter | Reason | Practical element instead |
|---|---|---|
| 1–3 | Diagnostic and principle chapters | Reflection questions; LAB-00 applies Chapter 3's secure-by-default principle |
| 5, 7, 8 | Architecture/reference chapters; hands-on elements covered by AWS/AZ labs (identity, KMS) | AWS-LAB-02 (KMS), AZ-LAB-01 (Key Vault) |
| 9 | Factory design | CAPSTONE implements the Software Factory Reference Architecture |
| 15 | Platform engineering operating model | LAB-14 golden-path gate pattern; CAPSTONE as a golden path |
| 20, 21 | Risk and SOAR programmes needing enterprise data | LAB-16 evidence; LAB-28 applies Chapter 21's checkpoint model to autonomous remediation |
| 36 | Closing synthesis | CAPSTONE (§36.7 Where to Begin) and the *AWS and Azure in Practice* baseline check in `exercises/ch36.sh` |

Every chapter, including those above, has an *AWS and Azure in Practice* exercise in [`exercises/`](../exercises/README.md).
