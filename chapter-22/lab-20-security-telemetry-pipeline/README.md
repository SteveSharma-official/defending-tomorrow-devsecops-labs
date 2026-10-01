# LAB-20 — Security Telemetry Pipeline: Validate and Gate an OpenTelemetry Collector Config

| Chapter | Level | Difficulty | Estimated time | Cloud required? |
|---|---|---|---|---|
| Chapter 22 — Observability for Security (§22.4.2 Instrumenting for Security Attributes, §22.5.2 Minimum Security Log Schema, §22.6 Telemetry Quality Framework) | 3 — Advanced | Intermediate | 40–50 minutes | No |

## What You Will Build
A pull-request gate for the security data plane. It proves that the Collector configuration from §22.4.2 **loads** (`otelcol-contrib validate`), that it is **security-fit** (enrichment order, no sampling on logs, no literal credentials, HTTPS only, provenance stamped), and that sample events meet the **minimum security log schema** at the Table 22.2 completeness threshold of 95%.

## What You Will Learn
- Treat Collector configuration as code, validated on every change.
- Why "the config loads" and "the config is safe" are different questions.
- How to measure telemetry completeness per event type, as Table 22.2 defines it.
- Why the `outcome` field is non-negotiable for detection.

## Prerequisites
**Required:** LAB-00; Chapter 22 §22.4–22.6.
**Optional:** Python 3.12+ with `pip install pytest PyYAML` to run the checks locally.

## Estimated Time
**40–50 minutes**

## Difficulty
Intermediate

## Architecture
```
collector/security-collector.yaml ──PR──▶ telemetry.yml
   │                                        ├─▶ otelcol-contrib validate      (loads? component names, references)
   │                                        ├─▶ tools/check_collector.py      (security-fit? C1–C6)
samples/events.jsonl ───────────────────────┼─▶ tools/check_telemetry.py      (9-field schema, ≥95% per event_type)
schema/minimum-security-log-schema.yaml ────┘   tools/tests                    (the checks are themselves tested)
```

## Step 1 — Create or Open the Repository
```bash
bash shared/scripts/start-lab.sh chapter-22/lab-20-security-telemetry-pipeline ~/dt-labs/dt-lab-20
```
Create an empty **public** repository named `dt-lab-20` on GitHub.

## Step 2 — Clone the Repository
```bash
cd ~/dt-labs/dt-lab-20
git remote add origin https://github.com/<your-username>/dt-lab-20.git
git push -u origin main
```

## Step 3 — Build the Lab
Read `collector/security-collector.yaml`. It is the Chapter 22 listing. `k8sattributes` adds pod and namespace metadata, `attributes/security` copies it into `security.*` attributes with `from_attribute` and stamps `security.telemetry_source`, and `batch` runs last. Then read `schema/minimum-security-log-schema.yaml`, which holds the nine fields from §22.5.2 and the threshold from Table 22.2.

**Why it matters for DevSecOps:** detection rules, hunts and investigations all assume these attributes exist. If they don't, every downstream control quietly fails.

## Step 4 — Implement the Security Control
The control is `.github/workflows/telemetry.yml`. It downloads `otelcol-contrib` at a pinned version, **verifies its SHA-256** before running it, validates the config, then runs the two checkers and their unit tests.

## Step 5 — Run the Pipeline
Push to `main` and open **GitHub → Repository → Actions → telemetry**. Expected: `otelcol-contrib validate` exits 0; `0 finding(s)`; every event type reports `"completeness_pct": 100.0`; `7 passed`.

## Step 6 — Inspect the Result
Open **Actions → telemetry → collector → Sample telemetry meets the minimum security log schema** and read the per-event-type completeness report. These are the numbers Table 22.2 tells you to monitor in production.

## Step 7 — Introduce a Deliberate Security Failure
On a branch named `cost-cutting`, apply the three edits in `lab-changes/apply-failures.md` (labelled INTENTIONALLY INSECURE). They add a log sampler to "save ingestion cost", change the token reference to a bare `${DATA_PLANE_TOKEN}`, and swap in an authentication log without `outcome`. Push and open a pull request.

## Step 8 — Observe the Security Control
- `otelcol-contrib validate` **still passes**: the config is loadable (verified locally with 0.162.0).
- `check_collector.py` fails with `C2 sampling processor 'probabilistic_sampler' on the logs pipeline…` and `C3 '${DATA_PLANE_TOKEN}' — use ${env:NAME}…`.
- `check_telemetry.py` fails with `authentication: completeness 0.0% is below 95%`.

Threat → Detection → Finding → Decision → Remediation: blind spots created by cost cutting → config and data-quality gates → named findings → pull request blocked → restore the pipeline.

## Step 9 — Remediate the Finding
Remove the sampler from the logs pipeline. If cost is the real problem, sample high-volume, low-value **metrics** instead (Table 22.2, Fidelity). Restore `${env:DATA_PLANE_TOKEN}` and the `outcome` field.

## Step 10 — Validate the Fix
### Expected Result
- All steps in the `telemetry` workflow pass; the pull request can merge.

## Step 11 — Cleanup
Delete the branch and, if you want, the repository. No cloud resources are created.

## What You Should Have Learned
Validation proves a pipeline runs, not that it is safe. Security fitness — enrichment, fidelity, credential handling, provenance and schema completeness — needs its own tested checks.

## Lab Completion Checklist
- [ ] Repository created
- [ ] Code committed
- [ ] Pipeline executed
- [ ] Security control triggered
- [ ] Finding identified
- [ ] Finding remediated
- [ ] Pipeline passed
- [ ] Resources cleaned up

## Further Challenge
Add the agent telemetry schema from §22.7.1 as a second schema file, then extend `check_telemetry.py` so `event_type: agent_tool_call` events must also carry the agent ID, the tool name and the decision-trace ID.

---
**Validation status:** executed locally on 1 Oct 2026. `otelcol-contrib validate` 0.162.0 passes for the baseline and the Step 7 config; `check_collector.py` and `check_telemetry.py` produce the findings shown in Step 8; unit tests 7/7 pass (pytest 9.0.3, Python 3.11); actionlint 1.7.12 and zizmor 1.30.1 report no findings. The pinned SHA-256 was computed from the release archive downloaded on 1 Oct 2026; cross-check it against the project's published checksums. **EXECUTION VALIDATION REQUIRED** on a GitHub-hosted runner.
