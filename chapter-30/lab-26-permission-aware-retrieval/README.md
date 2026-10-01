# LAB-26 — Permission-Aware Retrieval: Stop RAG Exfiltration and Existence Leaks

| Chapter | Level | Difficulty | Estimated time | Cloud required? |
|---|---|---|---|---|
| Chapter 30 — RAG Security Engineering (§30.3.1 Access Control for Vector Stores, §30.4 Knowledge Base Exfiltration Through Retrieval, §30.5 Retrieval Poisoning, §30.7 Retrieval Validation Model) | 3 — Advanced | Advanced | 40–50 minutes | No |

## What You Will Build
A small, dependency-free retriever over a synthetic knowledge base. Documents carry access groups and an ingestion hash. A security test suite proves four things:
- A staff user can **never** retrieve board-only or finance-only content.
- The response is **byte-identical** whether or not restricted documents exist, so nobody can infer they're there.
- A document altered after ingestion is excluded (`INTEGRITY_FAILURE`).
- A document carrying instructions aimed at the model is excluded (`INJECTION_DETECTED`), even when an attacker has re-hashed it.

## What You Will Learn
- Why "retrieve first, filter after" leaks through rankings and result counts (§30.3.1).
- How pre-filtering enforces document-level access at Trust Boundary 2.
- How to test the **non-inferability** property directly.
- How the Retrieval Validation Model's stages (provenance → access → injection) work as code.

## Prerequisites
**Required:** LAB-00; LAB-19 recommended; Chapter 30 §30.3–30.7.
**Optional:** Python 3.12+ to run the tests locally.

## Estimated Time
**40–50 minutes**

## Difficulty
Advanced

## Architecture
```
corpus/knowledge-base.json (text, groups, sha256 at ingestion; KB-009 altered later)
query + user groups ─▶ rag/retriever.py ─▶ prefilter by groups ─▶ rank (cosine) ─▶ top_k
                                       ─▶ Stage 1 provenance hash ─▶ Stage 3 injection scan ─▶ results
tools/tests: no restricted IDs · identical response with/without restricted docs · tampered/injected excluded
```
The bag-of-words similarity stands in for an embedding model. The access-control behaviour, which is the point of the lab, is the same.

## Step 1 — Create or Open the Repository
```bash
bash shared/scripts/start-lab.sh chapter-30/lab-26-permission-aware-retrieval ~/dt-labs/dt-lab-26
```
Create an empty **public** repository named `dt-lab-26`.

## Step 2 — Clone the Repository
```bash
cd ~/dt-labs/dt-lab-26
git remote add origin https://github.com/<your-username>/dt-lab-26.git
git push -u origin main
```

## Step 3 — Build the Lab
Read `corpus/knowledge-base.json`. KB-004 and KB-005 (Project Kestrel) are `exec`/`legal` only. KB-006 is `finance` only. KB-009 was edited after ingestion to tell users to email their password. Then read `rag/retriever.py` and `rag/rag-config.yaml`.

**Why it matters for DevSecOps:** a RAG system is a semantic query interface over your knowledge. Without retrieval-stage access control it becomes a knowledge-extraction tool for anyone with a login (§30.4).

## Step 4 — Implement the Security Control
The control is the test suite, run by `.github/workflows/retrieval.yml` on every change to the retriever, the configuration or the corpus.

## Step 5 — Run the Pipeline
Push to `main`. Expected: `11 passed`.

## Step 6 — Inspect the Result
Open **Actions → retrieval → rag-security → Retrieval security tests**. Each probe query, such as "what is the acquisition target name", appears as its own test case for both the content check and the non-inferability check.

## Step 7 — Introduce a Deliberate Security Failure
On a branch named `simpler-retrieval`, apply `lab-changes/apply-failures.md` (INTENTIONALLY INSECURE). It switches to post-filtering, discloses the withheld count and turns off provenance verification. Push and open a pull request.

## Step 8 — Observe the Security Control
Verified locally: `5 failed, 6 passed`. Restricted *content* is still filtered out, so the naive test passes. But all four non-inferability tests fail. For "Project Kestrel acquisition target valuation", a staff user now gets one FAQ result plus `"notice": "2 result(s) withheld because you lack access"`. That confirms the acquisition exists. Without provenance checks, KB-009 is caught only by the injection scan, so the integrity test fails.

Threat → Detection → Finding → Decision: existence leak and poisoned content → property tests → named failures → pull request blocked.

## Step 9 — Remediate the Finding
Restore `access_control: prefilter`, `disclose_withheld_count: false` and `verify_provenance: true`. If relevance suffers, improve the index for each permission group. Don't search across groups the user can't see.

## Step 10 — Validate the Fix
### Expected Result
- `11 passed`; the pull request can merge.

## Step 11 — Cleanup
Delete the branch and, if you want, the repository. No cloud resources.

## What You Should Have Learned
Filtering what users see isn't enough. What they can **infer** must not change either. Enforce access before ranking, verify provenance, and scan retrieved content before it reaches the model's context.

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
Add query-scope limitation (§30.4). Refuse queries that fall outside the assistant's designed domain, such as "list every document about acquisitions", and log the refusal in the minimum security log schema from LAB-20 (`event_type: authorization`, `outcome: denied`).

---
**Validation status:** executed locally on 1 Oct 2026 (Python 3.11, pytest 9.0.3): 11/11 tests pass on the baseline and the Step 8 failures are reproduced. actionlint and zizmor report no findings. **EXECUTION VALIDATION REQUIRED** on a GitHub-hosted runner.
