# LAB-27 — Model Signing and AI-BOM: Verify a Model Before It Is Deployed

| Chapter | Level | Difficulty | Estimated time | Cloud required? |
|---|---|---|---|---|
| Chapter 32 — AI Supply Chain Security (§32.2 Model Provenance, §32.3 Model Signing and Deployment Verification, §32.4 The AI-BOM, §32.5 Dataset Security and Lineage) · extends LAB-13 | 3 — Advanced | Advanced | 50–60 minutes | No |

## What You Will Build
A model supply chain for a small, deterministic phishing-URL classifier:
1. **Pre-merge gate (every pull request).** Train the model, generate a **CycloneDX 1.6 AI-BOM** that binds the model hash to its dataset hash and evaluation result, and apply the deployment policy (accuracy ≥ 0.95, allowed licence, dataset referenced).
2. **Build and sign (main only).** **Keyless** `cosign sign-blob` for the model and the AI-BOM, with Sigstore bundles. The signing certificate is bound to this workflow's identity.
3. **Deploy-verify.** Run the three §32.3.2 stages: verify both signatures and the signer identity, cross-check the AI-BOM hashes against the files, then apply the policy.

## What You Will Learn
- Sign model artefacts like container images, with the identity bound to the build workflow.
- Use an AI-BOM to make dataset lineage and evaluation results verifiable at deployment.
- Why signing can't catch poisoning *before* signing, and why the evaluation gate can.

## Prerequisites
**Required:** LAB-00; **LAB-13** recommended; Chapter 32 §32.2–32.5.
**Optional:** Python 3.12+ with `pip install pytest PyYAML "cyclonedx-python-lib[json-validation]"` locally.

## Estimated Time
**50–60 minutes**

## Difficulty
Advanced

## Architecture
```
data/phishing-urls.csv ─▶ tools/train.py ─▶ artifacts/model.json + evaluation.json
                                         ─▶ tools/make_aibom.py ─▶ ai-bom.cdx.json (model ⇄ dataset ⇄ accuracy)
main: cosign sign-blob --bundle (keyless, OIDC) ─▶ model.sigstore.json, ai-bom.sigstore.json ─▶ artifact
deploy-verify: Stage 1 cosign verify-blob (identity = this workflow on main)
               Stage 2 hashes in AI-BOM = files deployed       Stage 3 policy: accuracy, licence, dataset ref
```

## Step 1 — Create or Open the Repository
```bash
bash shared/scripts/start-lab.sh chapter-32/lab-27-model-signing-ai-bom ~/dt-labs/dt-lab-27
```
Create an empty **public** repository named `dt-lab-27`.

## Step 2 — Clone the Repository
```bash
cd ~/dt-labs/dt-lab-27
git remote add origin https://github.com/<your-username>/dt-lab-27.git
git push -u origin main
```

## Step 3 — Build the Lab
Read `tools/make_aibom.py`. The model is a `machine-learning-model` component. Its `modelCard.modelParameters.datasets` references a `data` component, and both carry SHA-256 hashes. `.gitattributes` keeps the CSV byte-identical on Windows, so the hashes match everywhere.

**Why it matters for DevSecOps:** the deployment system should accept a model only if it can prove which data trained it, how it scored and who built it.

## Step 4 — Implement the Security Control
`.github/workflows/model-supply-chain.yml` runs `pre-merge-gate` on every change, then `build-and-sign` → `deploy-verify` on `main`. Signing uses `id-token: write` in that job only, and never runs for pull requests.

## Step 5 — Run the Pipeline
Push to `main`. Expected: `5 passed`; `{"test_rows": 40, "accuracy": 0.975}`; `deployment verified`; and `Verified OK` from `cosign verify-blob` for both files.

## Step 6 — Inspect the Result
Download the `model-release` artifact. Open `ai-bom.cdx.json` and find the two hashes and the accuracy. Each `.sigstore.json` bundle contains the signing certificate, whose subject is your workflow's path on `refs/heads/main`, and the Rekor transparency-log entry.

## Step 7 — Introduce Deliberate Security Failures
Follow `lab-changes/apply-failures.md` (INTENTIONALLY INSECURE):
- **A.** Run the workflow manually with `simulate_tamper` ticked. This alters the model *after* signing.
- **B.** On branch `data-refresh`, replace the dataset with the poisoned copy, in which 29 phishing rows are relabelled benign, and open a pull request. This poisons the data *before* anything is signed.

## Step 8 — Observe the Security Control
- **A:** Stage 1 fails, because `cosign verify-blob` rejects `model.json` (the signature no longer matches). If Stage 1 were skipped, Stage 2 would also block with `model hash does not match the AI-BOM`, as the unit tests show.
- **B:** Signing would have succeeded, since the pipeline is legitimate. The **pre-merge gate** blocks instead: `Stage 3: accuracy 0.9 below the deployment minimum 0.95` (verified locally) and `test_clean_release_verifies` fails.

Threat → Detection → Finding → Decision: model substitution and data poisoning → signature, hash and evaluation gates → named failure → deployment or merge blocked.

## Step 9 — Remediate the Finding
- **A:** No code change is needed. Re-run without the tamper flag, and investigate the artifact store.
- **B:** Close the pull request. Restore the dataset from its last approved hash, and find out how the relabelled rows got into the data pipeline (§32.5).

## Step 10 — Validate the Fix
### Expected Result
- `pre-merge-gate`, `build-and-sign` and `deploy-verify` all pass on `main`.

## Step 11 — Cleanup
Delete the branch and, if you want, the repository. Signatures remain in the public Rekor log, which is expected and contains no secrets.

## What You Should Have Learned
Signing proves who built a model and that it hasn't changed since. The AI-BOM proves what it was built from and how it scored. You need both, plus an evaluation gate, because a poisoned dataset produces a perfectly signed bad model.

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
Add a SLSA build-provenance attestation for `model.json` with `actions/attest` (pinned in `docs/action-pins.md`), and verify it in `deploy-verify` with `gh attestation verify --repo <you>/dt-lab-27`. That closes the provenance gap described in §32.2.

---
**Validation status:** executed locally on 1 Oct 2026 (Python 3.11, pytest 9.0.3, cyclonedx-python-lib 11.12.0): 5/5 tests pass; the AI-BOM validates against CycloneDX 1.6 (strict); scenario B reproduces `accuracy 0.9`. actionlint and zizmor report no findings. **EXECUTION VALIDATION REQUIRED** for keyless `cosign sign-blob`/`verify-blob` on a GitHub-hosted runner (needs GitHub OIDC).
