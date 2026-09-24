# Toolchain reference (Appendix D)

This is the living version of Appendix D of *Defending Tomorrow*. It is updated when service or tool names change. Last reviewed: September 2026.

## D.1 AWS and Azure service equivalence

| Capability | AWS | Microsoft Azure | Chapters |
|---|---|---|---|
| Organisation hierarchy | AWS Organizations (OUs, accounts) | Management groups, subscriptions | 5 |
| Landing-zone baseline | AWS Control Tower | Azure landing zone accelerator | 5 |
| Preventive guardrails | SCPs and RCPs | Azure Policy (deny) | 5, 17 |
| Workforce identity | IAM Identity Center | Microsoft Entra ID | 6 |
| Privileged access | Permission sets; temporary elevated access | Privileged Identity Management | 6, 15 |
| Workload identity | IAM roles; EKS Pod Identity | Managed identities; Entra Workload ID | 6, 14 |
| CI/CD federation | IAM OIDC provider | Federated identity credentials | 6, 10, 11 |
| Segmentation | Security groups; VPC Lattice | NSGs with application security groups | 7 |
| Private access | PrivateLink; Verified Access | Private Link; Entra Private Access | 7 |
| Keys and HSM | AWS KMS; CloudHSM | Key Vault; Managed HSM | 8 |
| Secrets | Secrets Manager | Key Vault secrets | 10 |
| Data discovery | Amazon Macie | Microsoft Purview | 8, 30 |
| Build and deploy | CodeBuild; CodePipeline | Azure Pipelines | 9, 11 |
| Artefact registry | Amazon ECR; CodeArtifact | Azure Container Registry; Azure Artifacts | 9, 13 |
| Signing | AWS Signer | Notation with Key Vault | 13 |
| Native IaC | CloudFormation; CDK | Bicep; ARM | 12 |
| Managed Kubernetes | Amazon EKS | AKS | 14 |
| Detective policy | AWS Config | Azure Policy (audit) | 17, 18 |
| Compliance mapping | Security Hub CSPM standards; Audit Manager | Defender for Cloud regulatory compliance; Purview Compliance Manager | 18 |
| Posture and exposure | Security Hub | Defender for Cloud (CSPM) | 20, 35 |
| Threat detection | Amazon GuardDuty | Defender for Cloud workload plans | 23 |
| SIEM and data lake | Security Lake; CloudTrail Lake | Microsoft Sentinel; Log Analytics | 22–24 |
| Control-plane audit | AWS CloudTrail | Activity Log; Entra audit logs | 2, 22 |
| Automation and SOAR | EventBridge; Step Functions; Systems Manager Automation | Event Grid; Logic Apps; Sentinel playbooks | 21, 33 |
| Incident response | AWS Security Incident Response | Defender XDR; Sentinel incidents | 25 |
| Backup and recovery | AWS Backup (Vault Lock); Elastic Disaster Recovery | Azure Backup (immutable vaults); Site Recovery | 26 |
| Fault injection | AWS Fault Injection Service | Azure Chaos Studio | 27 |
| Model platform | Amazon Bedrock | Microsoft Foundry | 16, 28 |
| LLM guardrails | Bedrock Guardrails | Azure AI Content Safety | 29, 30 |
| RAG and vector search | Bedrock Knowledge Bases; OpenSearch Serverless | Azure AI Search | 30 |
| Agents | Bedrock AgentCore (Runtime, Identity, Gateway, Policy) | Foundry Agent Service; Entra Agent ID; API Management AI gateway | 31 |
| Model registry | SageMaker Model Registry | Azure Machine Learning registries | 32 |

## D.2 Open-source tools used in the labs

| Tool | Purpose | Chapters | Labs |
|---|---|---|---|
| Gitleaks | Secret detection in commits and history | 10, 11, 18 | LAB-03, LAB-14, LAB-16 |
| actionlint and zizmor | GitHub Actions linting and workflow security analysis | 11 | LAB-00, LAB-01, LAB-03, LAB-04, LAB-14 |
| CodeQL | Semantic SAST in pull requests | 10–12, 19 | LAB-00, LAB-03, LAB-04, LAB-05, LAB-07 |
| Semgrep | Custom SAST rules with rule tests | 19 | LAB-05, LAB-12, LAB-14 |
| pip-audit and dependency-review-action | Software composition analysis | 19 | LAB-06, LAB-14, LAB-16 |
| OWASP ZAP | Baseline DAST against an ephemeral target | 19 | LAB-11 |
| Checkov | IaC scanning (Terraform, Bicep, CloudFormation) | 12, 18 | LAB-07, LAB-16, AWS-LAB-01, AWS-LAB-02, AZ-LAB-01 |
| Trivy | Image, file-system and IaC scanning | 12, 14 | LAB-00, LAB-04, LAB-07, LAB-09 |
| Syft, Grype and CycloneDX | SBOM generation, vulnerability matching and VEX | 13 | LAB-12 |
| Sigstore cosign and artifact attestations | Keyless signing and build provenance | 13, 14 | LAB-10, LAB-13 |
| Kyverno | Kubernetes admission policy (Gatekeeper covered as an alternative) | 14, 17 | LAB-10 |
| OPA and Conftest | Policy as code for IaC, pipelines and agent tool calls | 17, 31 | LAB-08, LAB-14, LAB-18, AWS-LAB-02 |
| Sigma | Detection as code | 23 | LAB-17 |

Exact tool versions are pinned in each lab's workflow; see [action-pins.md](action-pins.md).
