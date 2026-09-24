# LAB-09 — Container Hardening and Image Scanning

| Chapter | Level | Difficulty | Estimated time | Cloud required? |
|---|---|---|---|---|
| Chapter 14 — Container Security Engineering (§14.2 Docker Image Hardening) | 2 — Practitioner | Intermediate | 45–60 minutes | No (Docker runs on the GitHub-hosted runner) |

## What You Will Build
A container pipeline that lints the Dockerfile, builds the image, enforces two **runtime-property gates** (non-root user; no credential-like environment variables), smoke-tests the container with a read-only root filesystem and dropped capabilities, and scans the image for fixable HIGH/CRITICAL vulnerabilities and embedded secrets.

## What You Will Learn
- Read a hardened multi-stage Dockerfile and explain each hardening decision.
- Show why a Dockerfile linter alone is insufficient (it misses root execution and baked-in secrets).
- Gate on *properties of the built artefact*, not only on source.
- Interpret an image vulnerability report and remediate by changing the base image.

## Prerequisites
**Required:** LAB-00; Chapter 14 §14.1–14.2.
**Optional:** Docker Desktop or Docker Engine to build locally; Trivy ≥ 0.69.2 (not 0.69.4–0.69.6).

## Estimated Time
**45–60 minutes**

## Difficulty
Intermediate

## Architecture
```
app/Dockerfile ─▶ hadolint ─▶ docker build ─▶ [gate] USER ≠ root ─▶ [gate] no *TOKEN/SECRET/PASSWORD* ENV
                                              ─▶ smoke test: --read-only --cap-drop ALL --no-new-privileges
                                              ─▶ trivy image (vuln + secret, HIGH/CRITICAL, fixable) ─▶ pass / fail
```

### Implementation note (Chapter 14 Dockerfile listing)
The Chapter 14 Dockerfile listing is condensed for print and does not build as shown: `COPY go.mod go.sum go.mod` and `COPY --chmod=644 /app/service` are malformed, `READONLY_ROOTFS` is not a Dockerfile instruction, the distroless digest is truncated, `HEALTHCHECK` calls `curl` (absent from distroless) with an unexpanded `${APP_PORT}` in exec form, and `chmod 644` would remove the binary's execute bit. hadolint 2.12.0 stops at line 15 with a parse error. `app/Dockerfile` in this lab is a working replacement pattern for the Python sample service; the same hardening decisions apply to a Go service on a distroless base.

## Step 1 — Create or Open the Repository
```bash
bash shared/scripts/start-lab.sh chapter-14/lab-09-container-hardening-scanning ~/dt-labs/dt-lab-09
```
Create an empty **public** repository `dt-lab-09`.

## Step 2 — Clone the Repository
```bash
cd ~/dt-labs/dt-lab-09
git remote add origin https://github.com/<your-username>/dt-lab-09.git
git push -u origin main
```

## Step 3 — Build the Lab
Read `app/Dockerfile`:

| Decision | Why it matters |
|---|---|
| Multi-stage build | Build tooling never reaches the runtime image |
| Fixed UID/GID `10001`, `USER 10001:10001` | Container process is not root; numeric IDs work with `runAsNonRoot` in Kubernetes |
| App files owned by root, mode `0444` | The process cannot modify its own code |
| `ORDERS_DB=/tmp/...` | Only `/tmp` needs to be writable → enables a read-only root filesystem |
| Python-based `HEALTHCHECK` | No `curl` needed in the image |
| Base image by tag | **EXECUTION VALIDATION REQUIRED:** replace with a digest: `docker buildx imagetools inspect python:3.13-slim` |

Optional local build: `docker build -t dt-orders-api:local app && docker run --rm -p 8080:8080 dt-orders-api:local`.

## Step 4 — Implement the Security Control
`.github/workflows/container.yml` contains five controls: lint, non-root gate, secrets-in-ENV gate, constrained smoke test, image scan. Make `build-and-scan` a required check.

## Step 5 — Run the Pipeline
Expected on the hardened baseline: hadolint clean (verified locally), `Configured user: '10001:10001'`, smoke test returns `{"status":"ok"}`, Trivy completes. **Note:** a newly disclosed base-image CVE can fail the scan on any day — that is the control working; the remedy is a base-image rebuild, not a gate exception.

## Step 6 — Inspect the Result
**Actions → container → build-and-scan** — expand each step. Record the Trivy summary table (target, vulnerability count) as your baseline.

## Step 7 — Introduce a Deliberate Security Failure
> **Intentionally insecure image definition — lab use only.** `ADMIN_TOKEN` is a synthetic, meaningless value.
```bash
git switch -c insecure-image
cp lab-changes/Dockerfile.insecure app/Dockerfile
git commit -am "LAB-09: insecure Dockerfile" && git push -u origin insecure-image
```
Open a pull request.

## Step 8 — Observe the Security Control
| Control | Expected observation |
|---|---|
| hadolint | **Fails**, but only on `DL3042` (pip cache) — verified locally. It does **not** flag the root user, the EOL base or the token. |
| hadolint-only mindset | Would conclude "one warning" — this is the lesson |
| Runtime identity gate | **Fails:** `Configured user: ''` → *Image runs as root* (the job stops here) |

Fix only the lint warning and the root user (add `USER 10001` after creating a user) in a scratch commit to see the later gates: the **secrets gate** fails on `ADMIN_TOKEN=…`, and **Trivy** reports HIGH/CRITICAL findings for the end-of-life `python:3.8` base (EXECUTION VALIDATION REQUIRED — findings depend on the vulnerability database on the day).

Threat → Detection → Finding → Decision: privileged, secret-bearing, vulnerable artefact → artefact-property gates + scanner → specific failing property → image never leaves the pipeline.

## Step 9 — Remediate the Finding
Restore the hardened Dockerfile: `git checkout main -- app/Dockerfile`. Supply runtime secrets through the platform (Kubernetes Secret/CSI, cloud secret manager), never through `ENV`. Commit and push.

## Step 10 — Validate the Fix
### Expected Result
- All five steps pass on the PR.
- `docker image inspect` shows user `10001:10001`; no credential-like variables.
- Trivy shows no fixable HIGH/CRITICAL findings (or the job fails only on newly disclosed base-image CVEs — rebuild on a patched base).

## Step 11 — Cleanup
No images were pushed. Delete branches. Locally: `docker image rm dt-orders-api:local` and `docker system prune` if you built images.

## What You Should Have Learned
Harden the image definition, then verify the *built artefact*: user, environment, filesystem and vulnerability posture. Linters check syntax conventions; gates check security properties.

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
Pin the base image by digest, then add a scheduled workflow that rebuilds weekly and opens an issue when Trivy finds new fixable vulnerabilities.

---
**Validation status:** hadolint 2.12.0 executed on the hardened (pass) and insecure (DL3042 only) Dockerfiles; workflow checked with actionlint/zizmor; Trivy checksum verified. Docker build, runtime gates and Trivy image scan **not** executed (no container runtime in the validation environment). **EXECUTION VALIDATION REQUIRED.**
