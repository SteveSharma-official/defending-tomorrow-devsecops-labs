# LAB-10 — Kubernetes Admission Control as Code with Kyverno

| Chapter | Level | Difficulty | Estimated time | Cloud required? |
|---|---|---|---|---|
| Chapter 14 — Container Security Engineering (§14.3, §14.5 Admission Control); Appendix C | 2 — Practitioner | Intermediate | 40–50 minutes (+30 optional cluster) | No |

## What You Will Build
Three Kyverno cluster policies — Pod Security Standards *restricted*, immutable image references, and mandatory resource limits — with **policy unit tests**, evaluated in CI against every manifest in the repository. The same policies can be installed in a local `kind` cluster to block the same objects at admission.

## What You Will Learn
- Express PSS *restricted* and supply-chain rules as Kyverno policies.
- Unit-test policies with `kyverno test` (good and bad fixtures).
- Shift admission decisions left: fail the PR before a manifest reaches a cluster.
- Read a PSS violation report and harden a workload accordingly.

## Prerequisites
**Required:** LAB-00; Chapter 14 §14.3–14.5.
**Optional (cluster path):** Docker, `kind` ≥ 0.23, `kubectl`, Helm 3. VERIFY CURRENT PRODUCT BEHAVIOUR for the Kyverno Helm chart version matching CLI 1.15.x.

> **Book alignment.** Appendix C (§C.1.2) prints this lab's `pod-security-restricted` policy. Pod Security **Admission** (PSA) is the built-in, generally available replacement for the *removed* PodSecurityPolicy — use PSA namespace labels as the baseline and Kyverno or Gatekeeper for richer policy, exceptions and reporting. PSS *restricted* permits projected volumes (they carry service-account tokens) and does not require `readOnlyRootFilesystem`, although a read-only root filesystem remains good practice.

## Estimated Time
**40–50 minutes**

## Difficulty
Intermediate

## Architecture
```
k8s/*.yaml ─PR─▶ admission-policy.yml ─▶ kyverno test (fixtures) ─▶ kyverno apply policies/ --resource k8s/
                                                                         │ pass → merge
                                                                         └ fail → PSS / image / limits violations
(optional) kind cluster + Kyverno ─▶ kubectl apply ─▶ admission webhook denies the same object
```

## Step 1 — Create or Open the Repository
```bash
bash shared/scripts/start-lab.sh chapter-14/lab-10-k8s-admission-kyverno ~/dt-labs/dt-lab-10
```
Create an empty **public** repository `dt-lab-10`.

## Step 2 — Clone the Repository
```bash
cd ~/dt-labs/dt-lab-10
git remote add origin https://github.com/<your-username>/dt-lab-10.git
git push -u origin main
```

## Step 3 — Build the Lab
Compare `k8s/deployment.yaml` with Appendix C.3. Each `securityContext` field maps to a PSS *restricted* control: `runAsNonRoot`, `allowPrivilegeEscalation: false`, `capabilities.drop: [ALL]`, `seccompProfile: RuntimeDefault`. `automountServiceAccountToken: false` removes an unneeded credential.

## Step 4 — Implement the Security Control
Policies live in `policies/` and use the current per-rule `validate.failureAction: Enforce` (the top-level `validationFailureAction` field is deprecated in recent Kyverno releases — VERIFY CURRENT PRODUCT BEHAVIOUR). `policy-tests/kyverno-test.yaml` declares the expected result for a good and a bad Pod.

## Step 5 — Run the Pipeline
Expected (verified locally with Kyverno CLI 1.15.2): `Test Summary: 6 tests passed and 0 tests failed`; `kyverno apply` → `pass: 4, fail: 0`. Kyverno auto-generates Deployment rules from Pod rules, which is why 12 rules are applied.

## Step 6 — Inspect the Result
**Actions → admission-policy → kyverno** — review the test table and apply summary.

## Step 7 — Introduce a Deliberate Security Failure
> **Intentionally insecure manifest — never apply it to a shared cluster.**
```bash
git switch -c debug-pod
cp lab-changes/deployment-insecure.yaml k8s/debug-pod.yaml
git add -A && git commit -m "LAB-10: add privileged debug pod" && git push -u origin debug-pod
```
Open a pull request.

## Step 8 — Observe the Security Control
Observed locally:
```
policy require-immutable-image-reference -> resource dt-lab/Pod/debug-toolbox failed: The ':latest' tag is not allowed.
policy pod-security-restricted -> ... violates PodSecurity "restricted:latest": allowPrivilegeEscalation != false,
    unrestricted capabilities, host namespaces (hostNetwork), privileged, runAsNonRoot != true, seccompProfile
policy require-resource-limits -> ... CPU and memory limits are required
pass: 1, fail: 3
```
Threat → Detection → Finding → Decision: a privileged, host-networked container is a node-compromise primitive → admission policy → six PSS violations plus two hygiene failures → PR blocked (and, in a cluster, the API server denies it).

## Step 9 — Remediate the Finding
Delete `k8s/debug-pod.yaml`. For legitimate debugging use `kubectl debug` with an ephemeral container under a time-bound, audited exception (Kyverno `PolicyException`) rather than a standing privileged pod. Commit and push.

## Step 10 — Validate the Fix
### Expected Result
- `admission-policy` passes (`pass: 4, fail: 0`).
- **Optional cluster validation:** `kind create cluster --name dt-lab-10`; install Kyverno with Helm; `kubectl create ns dt-lab`; `kubectl apply -f policies/`; `kubectl apply -f lab-changes/deployment-insecure.yaml` → *admission webhook "validate.kyverno.svc-fail" denied the request* (EXECUTION VALIDATION REQUIRED).

## Step 11 — Cleanup
`kind delete cluster --name dt-lab-10` if you created it. Delete branches and optionally the repository.

## What You Should Have Learned
Admission policy is most valuable when the same policy runs in the pull request (fast feedback) and at the API server (non-bypassable enforcement), with tests proving it allows good workloads and denies bad ones.

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
Add a `verifyImages` rule that requires a Cosign keyless signature from your GitHub repository's workflow identity, and combine it with LAB-13.

---
**Validation status:** `kyverno test` and `kyverno apply` executed with Kyverno CLI 1.15.2 (results above); checksum verified against the official release. Cluster path not executed. **EXECUTION VALIDATION REQUIRED** for the cluster path and GitHub-hosted run.
