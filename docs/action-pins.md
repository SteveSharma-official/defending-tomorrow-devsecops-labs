# Pinned GitHub Actions and Tool Versions

All workflows reference third-party actions by **full commit SHA** with the release tag in a comment.
SHAs below were resolved from the upstream repositories' tags on **23 September 2026** (`git ls-remote`,
annotated tags peeled to their commit). Re-verify periodically and keep them current with Dependabot
(`package-ecosystem: github-actions`).

| Action | Tag | Commit SHA |
|---|---|---|
| actions/checkout | v7.0.1 | 3d3c42e5aac5ba805825da76410c181273ba90b1 |
| actions/setup-python | v7.0.0 | 5fda3b95a4ea91299a34e894583c3862153e4b97 |
| actions/upload-artifact | v7.0.1 | 043fb46d1a93c77aae656e7c1c64a875d1fc6a0a |
| actions/download-artifact | v8.0.1 | 3e5f45b2cfb9172054b4087a40e8e0b5a5461e7c |
| actions/dependency-review-action | v5.0.0 | a1d282b36b6f3519aa1f3fc636f609c47dddb294 |
| actions/attest | v4.2.2 | 1e69f48acb82d1966a394da916b4c1698aa569d6 |
| github/codeql-action (init, analyze, upload-sarif) | v4.38.1 | 1c5b675653bb5c22dbe9b12b556ec555138e09fd |
| docker/setup-buildx-action | v4.4.1 | f87e5991a6d7451dcb8d9637bfbc97413f497069 |
| docker/login-action | v4.6.0 | dbcb813823bdd20940b903addbd779551569679f |
| docker/build-push-action | v7.4.0 | c3c9e263c25d99ce0380d002d59b67737d91b0dc |
| sigstore/cosign-installer | v4.1.2 | 6f9f17788090df1f26f669e9d70d6ae9567deba6 |
| anchore/sbom-action | v0.24.2 | 3ad7283483fc7af8ff2b4ea19663c2d5ca935e26 |
| zaproxy/action-baseline | v0.15.0 | de8ad967d3548d44ef623df22cf95c3b0baf8b25 |
| open-policy-agent/setup-opa | v2.4.0 | b2b258e089860efaadaaf71bf6e3aecb4a3eeff1 |
| hadolint/hadolint-action | v3.5.0 | 06be81baf89a55ffd0e24b8f04a4185738dd3387 |
| aws-actions/configure-aws-credentials | v6.3.0 | e1253824e5c10ff9df46874f81ed3ec929e19cfd |
| aws-actions/amazon-ecr-login | v2.1.7 | 03f1aad4c6c7ffd436567f42f9384779290529bd |
| azure/login | v3.1.0 | a641126d1b8aa4d1fa005f4f92df94a3a4c4c906 |
| hashicorp/setup-terraform | v4.0.1 | dfe3c3f87815947d99a8997f908cb6525fc44e9e |
| ossf/scorecard-action (challenge only) | v2.4.4 | 2d1146689b8cda280b9bc96326124645441f03bc |

## Downloaded binaries (SHA-256 verified against each project's published checksums file)
| Tool | Version | Archive | SHA-256 |
|---|---|---|---|
| gitleaks | 8.28.0 | gitleaks_8.28.0_linux_x64.tar.gz | a65b5253807a68ac0cafa4414031fd740aeb55f54fb7e55f386acb52e6a840eb |
| Trivy | 0.70.0 | trivy_0.70.0_Linux-64bit.tar.gz | 8b4376d5d6befe5c24d503f10ff136d9e0c49f9127a4279fd110b727929a5aa9 |
| Conftest | 0.62.0 | conftest_0.62.0_Linux_x86_64.tar.gz | 284231908e4cf66d156e5577c3eee2f67d9f2edf2521fa2309e0df1969f871e5 |
| Kyverno CLI | 1.15.2 | kyverno-cli_v1.15.2_linux_x86_64.tar.gz | c90520ba24fb8b8df003ec22d6d2621e4a3d3c7497665fdcf84e9eab4ff1dfe0 |
| Grype | 0.119.0 | grype_0.119.0_linux_amd64.tar.gz | 3fa2dc4b924621ab65404cf08d0b8438d896d80ab949c9d5a4ca283c36004c9b |

> **Why Trivy is pinned with a checksum:** Trivy release v0.69.4 and Docker Hub images v0.69.5–v0.69.6 were malicious, and 76 of 77 `aquasecurity/trivy-action` tags were hijacked (19–22 March 2026, advisory GHSA-69fq-xp46-6x23). Never install security tooling by mutable tag.

## Python packages (pinned in workflows)
checkov 3.3.19 · semgrep 1.177.0 · pip-audit 2.10.1 · zizmor 1.30.1 · actionlint-py 1.7.12.25 · sigma-cli 3.1.0 · pySigma-backend-splunk 2.1.0 · pytest 9.1.1 · PyYAML 6.0.3
