# INTENTIONALLY INSECURE — lab use only (Step 7)

On a branch named `bigger-experiment`, edit `experiments/EXP-001-psa-enforcement-removed.yaml` the way an
enthusiastic team might ("let's test it everywhere, it'll be fine"):

1. `guard.blast_radius.namespaces: ["*"]`
2. Delete the whole `abort_conditions` list.
3. Delete `max_seconds: 60` under `define.detection` ("we'll see how long it takes").

Then replace `results/sample-run.json` with `lab-changes/slow-detection-run.json` — a real-looking run where
detection took 148 seconds.
