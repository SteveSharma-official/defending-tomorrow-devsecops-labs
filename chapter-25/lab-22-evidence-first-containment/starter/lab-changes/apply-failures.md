# INTENTIONALLY INSECURE — lab use only (Step 7)

On a branch named `fast-containment`, edit `playbooks/PB-POD-CONTAIN-001.yaml` the way a responder under
pressure might ("just kill the pod, we'll look at it later"):

1. Move the whole `delete_pod` step so that it is the **second** step, directly after `preserve_pod_spec`.
2. In `delete_pod`, change `approval: human` to `approval: auto`.

Then, to see what tampering looks like, append one line to `evidence-sample/case-2026-0931/logs.txt`:
```
2026-09-30T02:15:00Z nothing to see here
```
