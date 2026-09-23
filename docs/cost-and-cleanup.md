# Cost, Free-Tier Expectations and Cleanup

The labs are designed so that **LAB-00 to LAB-19 and the CAPSTONE need only a free GitHub account and public repositories**. This is an expectation based on GitHub's published plan features in September 2026, **not a guarantee**: plans, included minutes and feature availability change. VERIFY CURRENT PRODUCT BEHAVIOUR before relying on it.

| What | Expected on GitHub Free (public repository) | Notes |
|---|---|---|
| GitHub Actions on standard GitHub-hosted runners | No charge for public repositories | Private repositories consume included minutes, then bill |
| Rulesets / branch protection | Available | Private repos need Pro/Team/Enterprise |
| CodeQL code scanning, SARIF upload | Available | Private repos need GitHub Code Security |
| Secret scanning + push protection | Available | Private repos need GitHub Secret Protection |
| Dependency review action | Available | Private repos need Code Security |
| Artifact attestations | Available | Private/internal repos need Enterprise Cloud |
| Environments with required reviewers | Available | Private repos need a paid plan |
| GitHub Container Registry (public packages) | No charge at time of writing | Delete packages after LAB-13/CAPSTONE |

## Labs that use a cloud provider
| Lab | Provider | Resources that can incur charges | Cleanup |
|---|---|---|---|
| AWS-LAB-01 | AWS | ECR storage/transfer | Delete the CloudFormation stack (ECR repository empties on delete) |
| AWS-LAB-02 | AWS | KMS customer-managed key (monthly, pro-rated), S3 | `terraform destroy`, empty & delete state bucket, delete stack; key enters 7-day pending deletion |
| AZ-LAB-01 | Azure | Storage account, Key Vault operations | Delete the resource group; purge the soft-deleted vault |
| AZ-LAB-02 | Azure | Test storage account | Delete assignments, definitions and the resource group |

> **Cost note:** Cloud labs may use resources that can incur charges. Follow each lab's cleanup instructions and verify current pricing and free-tier eligibility before starting. Never use a production account or subscription. Set a **budget alert** first (AWS Budgets; Azure Cost Management → Budgets).

## Universal cleanup checklist
- [ ] Cloud stacks/resource groups deleted and confirmed deleted
- [ ] KMS keys scheduled for deletion / Key Vaults purged
- [ ] GHCR packages deleted
- [ ] Lab repository variables, environments and collaborators removed
- [ ] Signing keys created only for labs removed from your GitHub account
- [ ] Local synthetic secret files deleted
