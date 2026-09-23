# Contributing

Thank you for improving the labs. Corrections from readers make them better for everyone.

## Good contributions
- A command, workflow or policy that no longer works because a tool or platform changed — include the error text and tool version.
- Updated action SHAs or tool checksums (with the upstream source you verified them against).
- Clarifications for readers new to GitHub.

## Rules
1. **Never** include real credentials, personal data or customer data — not even in issues. Synthetic values must be generated at runtime (see `shared/scripts/make-test-secret.sh`).
2. Pin every third-party action to a full commit SHA with the tag in a comment; verify every downloaded binary by checksum.
3. Keep each lab's 11-step structure (see `docs/lab-template.md`) and its *Validation status* line truthful: state what you actually executed.
4. Intentionally insecure material stays in `lab-changes/` and is labelled *INTENTIONALLY INSECURE — lab use only*.
5. Run `.github/workflows/validate-labs.yml` checks locally where possible before opening a pull request.

## Reporting a problem
Open an issue with: lab ID, step number, operating system, tool versions, and the exact output (redact account IDs).
