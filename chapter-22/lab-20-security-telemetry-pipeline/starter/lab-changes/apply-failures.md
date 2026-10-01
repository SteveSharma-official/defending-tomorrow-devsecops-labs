# INTENTIONALLY INSECURE — lab use only (Step 7)

Make these three edits on a branch named `cost-cutting`:

1. `collector/security-collector.yaml` — "reduce ingestion cost" by sampling logs. Add a processor:
   ```yaml
     probabilistic_sampler:
       sampling_percentage: 10
   ```
   and change the logs pipeline to `processors: [k8sattributes, attributes/security, probabilistic_sampler, batch]`.
2. `collector/security-collector.yaml` — replace `Bearer ${env:DATA_PLANE_TOKEN}` with `Bearer ${DATA_PLANE_TOKEN}`.
3. `samples/events.jsonl` — replace the file with `lab-changes/events-without-outcome.jsonl` (an application team
   "simplified" its auth log and dropped the outcome field).
