# INTENTIONALLY INSECURE — lab use only (Step 7)

On a branch named `quick-restore`, make the changes a team under pressure might make ("just roll back to
the latest signed image"):

1. `recovery/recovery-policy.yaml` — set `exclude_builds_after_compromise_start: false`.
2. `recovery/recovery-runbook.yaml` — delete the `verify-signature` and `verify-provenance` steps, and change
   the deploy step to `image_ref: "ghcr.io/<your-username>/dt-lab-13:latest"`.
