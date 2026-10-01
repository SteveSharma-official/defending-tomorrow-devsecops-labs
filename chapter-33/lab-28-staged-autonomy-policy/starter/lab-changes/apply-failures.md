# INTENTIONALLY INSECURE — lab use only (Step 7)

On a branch named `faster-remediation`, make two changes a team under incident pressure might propose:

1. `policy/remediation.rego` — promote two action classes ("we keep approving these anyway"):
   ```rego
   "network_segment_isolation": 3,
   "data_deletion": 3,
   ```
   and add `"network_segment_isolation": 20,` to `blast_radius_limits`.
2. `policy/remediation.rego` — delete the line `input.action.rollback_verified == true` ("rollback testing slows us down").
