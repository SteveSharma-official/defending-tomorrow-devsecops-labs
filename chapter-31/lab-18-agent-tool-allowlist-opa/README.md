# LAB-18 — Govern Agent Tool Access: A Per-Agent Allowlist as Tested Policy

| Chapter | Level | Difficulty | Estimated time | Cloud required? |
|---|---|---|---|---|
| Chapter 31 — Agent Security Engineering (§31.2 Agent Identity, §31.5 Tool Security and Allowlisting); Chapter 0 policy listing; Chapter 3 secure-by-default | 3 — Advanced | Advanced | 45–60 minutes | No — no LLM or API key required |

## What You Will Build
The policy core of an MCP gateway: an OPA/Rego policy that decides whether a named agent may call a named tool with given parameters, enforcing **default deny**, **per-agent allowlists**, **parameter constraints**, **rate limits** and **human approval for write actions**, plus a governance invariant that **no binding may use wildcards**. CI formats, strictly compiles, unit-tests (≥ 90 % coverage) and replays recorded tool calls — including one produced by an indirect prompt injection — which must all be denied.

## What You Will Learn
- Model agent authorisation as identity → tool → parameters → context, not as a system prompt.
- Return *reasons* with every denial for decision logs (Chapter 22 agent telemetry).
- Treat the allowlist itself as governed configuration with invariants and tests.
- Show that prompt injection cannot expand an agent's authority when enforcement sits outside the model.

## Prerequisites
**Required:** LAB-08 (Rego basics); Chapter 31 §31.1–31.5.
**Optional:** OPA ≥ 1.0 locally.

> **Correction to the manuscript (Chapter 0 listing).** `import data.agent.bindings[agent_id].allowlist` is not valid Rego — imports cannot contain variables (OPA 1.20.2: `rego_parse_error: unexpected var token`), and the listing references undefined `satisfies`. The Chapter 15 policies use Python-style `"…%s" % x` formatting and pre-1.0 syntax, and fail to parse under both OPA 1.x and `--v0-compatible`. `policy/agent_tools.rego` is a working replacement.

## Estimated Time
**45–60 minutes**

## Difficulty
Advanced

## Architecture
```
agent (LLM) ──tool call {agent_id, tool, params, session, approval}──▶ MCP gateway ──▶ OPA: data.agent.tools
                                                                            │ allow → forward to tool server
                                                                            └ deny  → reasons → decision log / SIEM
data/bindings.json (per-agent allowlists) ── reviewed via PR + CODEOWNERS ── invariant: no wildcards
CI: opa fmt → opa check --strict → opa test (≥90 % coverage) → replay requests/*.json (must deny)
```

## Step 1 — Create or Open the Repository
```bash
bash shared/scripts/start-lab.sh chapter-31/lab-18-agent-tool-allowlist-opa ~/dt-labs/dt-lab-18
```
Create an empty **public** repository `dt-lab-18`.

## Step 2 — Clone the Repository
```bash
cd ~/dt-labs/dt-lab-18
git remote add origin https://github.com/<your-username>/dt-lab-18.git
git push -u origin main
```

## Step 3 — Build the Lab
Read `data/bindings.json`, then `policy/agent_tools.rego`. Map each `deny_reasons` rule to an OWASP Agentic Top 10 risk discussed in Chapter 31 (tool misuse, identity abuse, excessive agency).

## Step 4 — Implement the Security Control
Two controls: the runtime policy (what the gateway enforces) and the CI workflow `agent-policy.yml` (what the organisation enforces on changes to the policy and bindings).

## Step 5 — Run the Pipeline
Expected (verified locally with OPA 1.20.2): `PASS: 10/10`, coverage ≈ 96 %, and
```
requests/poisoned-tool-call.json -> allow=false
[ "tool 'orders.export_all' is not in the allowlist for support-agent-v1" ]
```

## Step 6 — Inspect the Result
Open `requests/poisoned-tool-call.json`: the agent was manipulated by content in an order note, yet the call is denied because authority is decided by identity and policy, not by the model's intent.

## Step 7 — Introduce a Deliberate Security Failure
A "friction reduction" change request asks for broader access. On branch `broaden-access`, edit `data/bindings.json` and add to `support-agent-v1.tools`:
```json
"orders.*": {"max_calls_per_hour": 1000, "params": {}}
```
Commit, push, open a PR.

## Step 8 — Observe the Security Control
- `opa test` fails: `test_no_wildcard_bindings: FAIL`.
- Threat → Detection → Finding → Decision: silent privilege expansion of an agent → governance invariant test → named failing test → change blocked pending an explicit, least-privilege request.
Then try the subtler variant: instead of a wildcard, add `"orders.export_all": {"max_calls_per_hour": 10, "params": {"format": {"allowed": ["csv"]}}}`. Tests pass — but the replay step fails because the recorded poisoned call is now **allowed**. The regression corpus caught what the invariant could not.

## Step 9 — Remediate the Finding
Remove both additions. If bulk export is a genuine business need, give it to a *separate* agent identity, mark it `"write": true` so human approval is mandatory, and add a new recorded request proving the support agent still cannot call it.

## Step 10 — Validate the Fix
### Expected Result
- `PASS: 10/10`, coverage ≥ 90 %, every replayed request `allow=false`.

## Step 11 — Cleanup
Delete branches; optionally delete the repository. No cloud resources, models or API keys were used.

## What You Should Have Learned
Agent security is enforced outside the model: identity-bound allowlists, parameter constraints and approvals, all as tested policy — with a regression corpus of real attack attempts.

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
Run the policy as a service (`opa run --server policy data`) and put a 30-line HTTP proxy in front of a mock MCP tool server that calls `POST /v1/data/agent/tools` before forwarding — the containment step of the Chapter 31 in-text lab.

---
**Validation status:** `opa fmt`, `opa check --strict`, `opa test` (10/10, 95.9 % coverage, threshold 90 met) and the replay executed locally with OPA 1.20.2; Step 8 reproduced locally: wildcard → `test_no_wildcard_bindings: FAIL`; explicit `orders.export_all` → tests 10/10 pass but the poisoned request returns `allow=true` (replay fails). Workflow checked with actionlint. **EXECUTION VALIDATION REQUIRED** on a GitHub-hosted runner.
