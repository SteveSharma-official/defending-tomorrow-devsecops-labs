# LAB-19 — LLM Guardrail Regression Testing: Measure Before You Trust

| Chapter | Level | Difficulty | Estimated time | Cloud required? |
|---|---|---|---|---|
| Chapter 29 — Securing AI Systems (§29.3 Prompt Injection, §29.7 Integration Patterns); Chapter 30 — RAG Security (§30.5 Retrieval Poisoning) | 3 — Advanced | Advanced | 40–50 minutes | No — no model, no API key, no cost |

## What You Will Build
A guardrail package — an injection-indicator scanner for retrieved content/tool outputs and an output validator (action-intent routing, PII redaction, schema checks) — with a **versioned attack/benign corpus** and CI thresholds for **detection rate (≥ 90 %)** and **false-positive rate (≤ 15 %)**.

## What You Will Learn
- Treat guardrails as software with measurable quality, not as a checkbox.
- Harden heuristics against trivial evasions (Unicode compatibility forms, zero-width characters, base64).
- Detect regressions caused by "performance" or "simplification" changes.
- Explain why heuristics are only one layer and where the architectural controls sit (LAB-18).

## Prerequisites
**Required:** LAB-18 recommended; Chapter 29 §29.3, §29.7; Chapter 30 §30.5.
**Optional:** Python 3.12+ locally.

> **Implementation note (Chapter 29 and 30 listings).** The Chapter 30 retrieval middleware builds dictionaries with bare names (`{type: …, document_id: …}`), which raises `NameError`; the Chapter 29 middleware treats `context` as both a dict and an object. `guardrails/output_validator.py` is a runnable equivalent.

## Estimated Time
**40–50 minutes**

## Difficulty
Advanced

## Architecture
```
retrieved doc / tool output ─▶ scanner.normalise (NFKC, zero-width strip, base64 decode) ─▶ 6 indicator patterns ─▶ flag?
LLM response ─▶ output_validator: action-intent → human_review | PII → redact | schema → quarantine | injection → security_review
CI: tests/corpus.yaml (10 attacks, 8 benign) ─▶ detection ≥ 90 %, false positives ≤ 15 % ─▶ pass / fail
```

## Step 1 — Create or Open the Repository
```bash
bash shared/scripts/start-lab.sh chapter-29/lab-19-llm-guardrail-regression ~/dt-labs/dt-lab-19
```
Create an empty **public** repository `dt-lab-19`.

## Step 2 — Clone the Repository
```bash
cd ~/dt-labs/dt-lab-19
git remote add origin https://github.com/<your-username>/dt-lab-19.git
git push -u origin main
```

## Step 3 — Build the Lab
Read `guardrails/scanner.py` and `tests/corpus.yaml`. Note the benign entries — "ignore the duplicate invoice", "previous instructions for installing" — chosen to keep the patterns honest.

## Step 4 — Implement the Security Control
The control is the measured quality bar in `tests/test_guardrails.py` (`MIN_DETECTION_RATE`, `MAX_FALSE_POSITIVE_RATE`) run by `guardrails.yml`. Changing a threshold is a reviewed decision, not a way to make CI green.

## Step 5 — Run the Pipeline
Expected (verified locally): `6 passed`; current corpus: detection 10/10, false positives 0/8.

## Step 6 — Inspect the Result
`pytest -v` in the job log lists each test. Locally, print the indicators per attack:
```bash
python -c "import yaml;from guardrails.scanner import scan;[print(scan(t)) for t in yaml.safe_load(open('tests/corpus.yaml'))['attacks']]"
```

## Step 7 — Introduce a Deliberate Security Failure
A performance "optimisation" removes normalisation. On branch `faster-scan`, in `guardrails/scanner.py` change
```python
    normalised = normalise(text)
```
to
```python
    normalised = text
```
Commit, push, open a PR.

## Step 8 — Observe the Security Control
Observed locally:
```
AssertionError: detection 80% < 90%; missed: ['Ｉｇｎｏｒｅ ｐｒｅｖｉｏｕｓ ｉｎｓｔｒｕｃｔｉｏｎｓ …', 'SWdub3JlIHByZXZpb3VzIGluc3RydWN0aW9ucy…']
1 failed, 5 passed
```
Threat → Detection → Finding → Decision: encoded/obfuscated injection passes a weakened guardrail → corpus regression test → named missed samples → PR blocked.

## Step 9 — Remediate the Finding
Restore `normalise(text)`. If performance matters, optimise *inside* `normalise` and prove with the same tests that detection is unchanged.

## Step 10 — Validate the Fix
### Expected Result
- `6 passed`. Add one new attack you devise yourself (for example, instructions split across two sentences) — if it is missed, extend a pattern and add a benign counter-example to protect precision.

## Step 11 — Cleanup
Delete branches; optionally delete the repository.

## What You Should Have Learned
Heuristic guardrails decay silently unless measured. A corpus with thresholds turns them into an engineering control — and makes their limits visible, which is why authority must still be constrained outside the model (LAB-18).

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
Add an optional, manually triggered job that sends the attack corpus to a real model endpoint through your gateway (API key stored as an environment secret with required reviewers) and records which attacks change the model's behaviour. **Cost note:** model API calls are billed by the provider.

---
**Validation status:** 6/6 tests pass locally (Python 3.11, pytest 9.1.1); Step 8 failure reproduced exactly as shown. Workflow checked with actionlint. **EXECUTION VALIDATION REQUIRED** on a GitHub-hosted runner.
