# INTENTIONALLY INSECURE — lab use only (Step 7)

On a branch named `tune-hunts`:

1. **"Reduce noise" in HUNT-CLOUD-001.** In `hunts/HUNT-CLOUD-001.sql`, add this line before `ORDER BY`:
   ```sql
     AND e.errorCode IS NULL AND e.eventName NOT LIKE 'Get%'
   ```
   The analyst's reasoning: "denied calls and Get* calls are noisy."
2. **Break the feedback loop.** In `hunts/HUNT-AGENT-003.yaml`, delete the two `feedback:` lines.
