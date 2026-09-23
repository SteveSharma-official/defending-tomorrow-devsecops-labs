# Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| `start-lab.sh: Permission denied` | Script run as `./start-lab.sh` without the executable bit (files uploaded via the GitHub web UI lose it) | Always run scripts as `bash shared/scripts/start-lab.sh …` |
| `Author identity unknown` during `start-lab.sh` | Git user not configured | `git config --global user.name …` and `user.email …`, delete the target folder, re-run |
| `remote: Repository not found` on push | Repository not created, typo, or wrong account | Create the empty repository; check `git remote -v` |
| Git asks for a password and rejects it | Passwords are not accepted for Git over HTTPS | Use Git Credential Manager browser sign-in or `gh auth login` |
| `! [rejected] main -> main (fetch first)` | You added a README when creating the repository | `git pull --rebase origin main` then push, or recreate the repository empty |
| Workflow does not start | File not under `.github/workflows/` on the pushed branch; Actions disabled | Check path; **Settings → Actions → General → Allow all actions** (or allow the listed actions) |
| `Resource not accessible by integration` | Job lacks a permission (e.g. `security-events: write`) | Add the minimal permission to that job only |
| SARIF upload fails on a private repository | Code scanning not licensed for private repos on Free | Use a public lab repository |
| `The action … is not allowed` | Organisation policy restricts actions | Allow-list the specific SHA-pinned actions |
| `sha256sum: WARNING: 1 computed checksum did NOT match` | Download corrupted or tampered, or version changed | Stop. Re-download; if it persists, compare with the project's published checksums and investigate |
| YAML error `mapping values are not allowed here` | Indentation or a missing space after `:` | Use an editor with YAML validation; spaces, not tabs |
| OIDC: `Not authorized to perform sts:AssumeRoleWithWebIdentity` / `AADSTS700213` | Trust policy / federated credential subject does not match repository, branch or environment | Compare the `sub` claim with the trust configuration (exact case) |
| CodeQL "default setup" conflicts | Default and advanced setup both enabled | Disable default setup when using the workflow |
