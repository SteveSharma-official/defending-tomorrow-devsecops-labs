# LAB-13 — Build Provenance and Keyless Signing: Prove Where an Artefact Came From

| Chapter | Level | Difficulty | Estimated time | Cloud required? |
|---|---|---|---|---|
| Chapter 13 — Software Supply Chain Security (§13.2 SLSA, §13.4 Sigstore/Cosign); Chapter 11 §11.5 Integrity Chain | 3 — Advanced | Advanced | 50–70 minutes | No (uses GitHub Container Registry) |

## What You Will Build
A release workflow that builds the image once, pushes it to **GHCR** under an immutable commit-SHA tag, creates a **Sigstore-signed build-provenance attestation** with `actions/attest`, adds a **Cosign keyless signature** by digest, and then — in a separate job with no write permissions — **verifies both exactly as a deployer would**.

## What You Will Learn
- Explain why artefacts are referenced and signed **by digest**, never by tag.
- Generate SLSA build provenance on GitHub-hosted runners (SLSA Build L2; L3 properties depend on using an isolated reusable workflow — VERIFY against slsa.dev v1.2).
- Use OIDC-based keyless signing: no private key exists on the runner or in secrets.
- Verify provenance (`gh attestation verify`) and signer identity (`cosign verify --certificate-identity … --certificate-oidc-issuer …`).

## Prerequisites
**Required:** LAB-09; GitHub CLI ≥ 2.49 locally for manual verification (`gh attestation`); Chapter 13 §13.2–13.4.
**Optional:** Cosign ≥ 2.x locally.

> **Plan availability.** Artifact attestations are available for **public** repositories on all current plans; private/internal repositories require GitHub Enterprise Cloud (GitHub Docs, September 2026 — VERIFY CURRENT PRODUCT BEHAVIOUR). Cosign keyless signing records an entry in the **public** Rekor transparency log, including your repository and workflow identity. Do not use keyless public-good signing for confidential projects.

> **Correction to the manuscript.** The Chapter 11 and Chapter 13 listings sign `image:${{ github.sha }}` / `image@${{ github.sha }}`: a Git commit SHA is not an image digest, and `cosign sign` does not take `--certificate-identity`, `--certificate-oidc-issuer` or `--attestation` (those are verification or `cosign attest` flags). `slsa-github-generator` is a reusable workflow invoked at job level, not a CLI or step. This workflow shows a working pattern.

## Estimated Time
**50–70 minutes**

## Difficulty
Advanced

## Architecture
```
push to main ─▶ build-attest-sign (contents:read, packages:write, id-token:write, attestations:write)
                 ├─ build + push ghcr.io/<you>/dt-lab-13:<commit-sha>  → digest sha256:…
                 ├─ actions/attest  → SLSA provenance, signed via Sigstore (Fulcio cert bound to workflow identity)
                 └─ cosign sign <image>@<digest> (keyless, OIDC)
              ─▶ verify (contents:read, packages:read)
                 ├─ gh attestation verify oci://<image>@<digest> --repo <you>/dt-lab-13
                 └─ cosign verify … --certificate-identity https://github.com/<you>/dt-lab-13/.github/workflows/release.yml@refs/heads/main
```

## Step 1 — Create or Open the Repository
```bash
bash shared/scripts/start-lab.sh chapter-13/lab-13-provenance-signing ~/dt-labs/dt-lab-13
```
Create an empty **public** repository `dt-lab-13`.

## Step 2 — Clone the Repository
```bash
cd ~/dt-labs/dt-lab-13
git remote add origin https://github.com/<your-username>/dt-lab-13.git
git push -u origin main
```

## Step 3 — Build the Lab
Read `.github/workflows/release.yml`. Note `permissions: {}` at workflow level and the separate `verify` job with read-only permissions — the verifier must not be able to create what it verifies.

## Step 4 — Implement the Security Control
The controls are: immutable digest reference, provenance attestation, keyless signature, independent verification. No secret is configured anywhere — confirm under **Settings → Secrets and variables → Actions** (empty).

## Step 5 — Run the Pipeline
The push to `main` runs `release`. Expected: both jobs green; the `verify` log ends with `Provenance and signature verified for ghcr.io/<you>/dt-lab-13@sha256:…`.

## Step 6 — Inspect the Result
- **Actions → release → build-attest-sign → Summary:** attestation link.
- **Repository → Attestations** (or the link in the summary): the provenance record, subject digest, workflow and commit.
- **Your profile → Packages → dt-lab-13:** the image and its signature/attestation artefacts.
- Locally:
```bash
gh attestation verify oci://ghcr.io/<you>/dt-lab-13:<commit-sha> --repo <you>/dt-lab-13
```
`[SCREENSHOT REQUIRED — GITHUB ATTESTATION DETAIL PAGE SHOWING SUBJECT DIGEST, WORKFLOW AND COMMIT]`

## Step 7 — Introduce a Deliberate Security Failure
Simulate a deployer being handed an artefact that did **not** come from your pipeline.
```bash
gh attestation verify oci://docker.io/library/python:3.13-slim --repo <you>/dt-lab-13
cosign verify ghcr.io/<you>/dt-lab-13:<commit-sha> \
  --certificate-identity "https://github.com/<you>/dt-lab-13/.github/workflows/release.yml@refs/heads/feature" \
  --certificate-oidc-issuer https://token.actions.githubusercontent.com
```
The first command asks for provenance your repository never produced; the second asserts the wrong signer identity (a different branch).

## Step 8 — Observe the Security Control
- `gh attestation verify` fails: no attestations found for the subject from your repository.
- `cosign verify` fails: no signature matches the expected identity (the certificate's subject is `…@refs/heads/main`).
Threat → Detection → Finding → Decision: substituted or rebuilt artefact / build from an unapproved branch → provenance and identity checks → verification failure → **do not deploy** (enforce at admission with LAB-10's `verifyImages` challenge).

## Step 9 — Remediate the Finding
There is nothing to "fix" in the pipeline — the control worked. The remediation is procedural: deployments must reference `image@sha256:<digest>` produced by `release.yml` on `main`, and admission policy must reject anything else.

## Step 10 — Validate the Fix
### Expected Result
- Verification succeeds for the pipeline's digest with the correct identity and fails for any other image or identity.
- You can state the image digest, the workflow file, the ref and the commit that produced it — from the attestation alone.

## Step 11 — Cleanup
- **Profile → Packages → dt-lab-13 → Package settings → Delete this package** (removes image, signatures and stored attestations from GHCR).
- Delete the repository if no longer needed. Transparency-log entries in Rekor are permanent by design.
- GHCR storage for public packages is free at the time of writing (VERIFY CURRENT PRODUCT BEHAVIOUR).

## What You Should Have Learned
Integrity is established by *verification*, not by signing. Digest references, provenance and identity-bound signatures let a deployer prove an artefact's origin without trusting the registry or the tag.

## Lab Completion Checklist
- [ ] Repository created
- [ ] Code committed
- [ ] Pipeline executed
- [ ] Security control triggered
- [ ] Finding identified
- [ ] Finding remediated (procedure documented)
- [ ] Pipeline passed
- [ ] Resources cleaned up (package deleted)

## Further Challenge
Sign a model file (`cosign sign-blob --bundle model.sigstore.json model.onnx`) in the same workflow and verify it with `cosign verify-blob` — the Chapter 32 AI supply-chain pattern.

---
**Validation status:** workflow checked with actionlint 1.7.12 and zizmor 1.30.1; action SHAs resolved from upstream tags on 23 Sep 2026; `actions/attest` inputs and permissions taken from its README (September 2026). Not executed on GitHub. **EXECUTION VALIDATION REQUIRED.**
