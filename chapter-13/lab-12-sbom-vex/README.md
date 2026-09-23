# LAB-12 — SBOM and VEX: Know What You Ship, Record What Actually Affects You

| Chapter | Level | Difficulty | Estimated time | Cloud required? |
|---|---|---|---|---|
| Chapter 13 — Software Supply Chain Security (§13.3 SBOM, §13.3.2 VEX) | 3 — Advanced | Advanced | 45–60 minutes | No |

## What You Will Build
A pipeline that builds the container image, generates **CycloneDX** and **SPDX** SBOMs with Syft, retains them as build evidence, and scans the SBOM with Grype — failing on fixable HIGH/CRITICAL vulnerabilities while honouring reviewed **OpenVEX** statements stored in the repository.

## What You Will Learn
- Generate SBOMs in both major formats from a built artefact (not just from a manifest).
- Scan an SBOM rather than re-scanning the image, and explain why that matters for incident response ("are we affected by CVE-X?").
- Write an OpenVEX `not_affected` statement with a valid justification and an impact statement.
- Judge when VEX is appropriate and when upgrading is the only acceptable answer.

## Prerequisites
**Required:** LAB-06 and LAB-09 recommended; Chapter 13 §13.3.
**Optional:** Syft and Grype locally (verify release checksums).

## Estimated Time
**45–60 minutes**

## Difficulty
Advanced

## Architecture
```
app/ ─▶ docker build ─▶ image ─▶ Syft ─┬─ sbom.cdx.json (CycloneDX)
                                       └─ sbom.spdx.json (SPDX) ─▶ artifact "sbom-<sha>" (30 days)
sbom.cdx.json ─▶ Grype --only-fixed --fail-on high --vex vex/*.json ─▶ pass / fail
vex/*.json  ◀── reviewed in PRs like code (CODEOWNERS: security team)
```

## Step 1 — Create or Open the Repository
```bash
bash shared/scripts/start-lab.sh chapter-13/lab-12-sbom-vex ~/dt-labs/dt-lab-12
```
Create an empty **public** repository `dt-lab-12`.

## Step 2 — Clone the Repository
```bash
cd ~/dt-labs/dt-lab-12
git remote add origin https://github.com/<your-username>/dt-lab-12.git
git push -u origin main
```

## Step 3 — Build the Lab
Read `.github/workflows/sbom.yml`. **Why SBOMs from the image:** a requirements file lists what you *asked for*; the image contains what you *ship* — transitive packages and OS packages included. (Validation note: Syft 1.52.0 on `requirements.txt` alone produced a CycloneDX 1.7 SBOM containing only the three direct dependencies.)

## Step 4 — Implement the Security Control
Two controls: (1) SBOM generation and retention as evidence for every build; (2) an SBOM-based vulnerability gate that consults `vex/`.

## Step 5 — Run the Pipeline
Expected: job passes; artifact `sbom-<commit-sha>` contains `sbom.cdx.json` and `sbom.spdx.json`.

## Step 6 — Inspect the Result
Download the artifact. Search `sbom.cdx.json` for `"pkg:pypi/flask@3.1.3"` and for Debian packages from the base image. Count components — this is your inventory for the next zero-day.

## Step 7 — Introduce a Deliberate Security Failure
> **Intentionally vulnerable dependency — lab use only.**
```bash
git switch -c old-yaml
sed -i 's/^PyYAML==.*/PyYAML==5.3.1/' app/requirements.txt
git commit -am "LAB-12: vulnerable PyYAML" && git push -u origin old-yaml
```
Open a pull request.

## Step 8 — Observe the Security Control
Expected: Grype fails (exit code 2) listing `pyyaml 5.3.1 … 5.4 … GHSA-8q59-q68h-6hv4 / CVE-2020-14343 … Critical` (EXECUTION VALIDATION REQUIRED — identifiers and severity as published by the advisory databases on the day).
Threat → Detection → Finding → Decision: exploitable library in the shipped artefact → SBOM match → CVE + fix version → block unless proven not affected.

## Step 9 — Remediate the Finding
**Path A (preferred): upgrade.** `sed -i 's/^PyYAML==.*/PyYAML==6.0.3/' app/requirements.txt`, commit, push.

**Path B (learn VEX, then revert):** the app only calls `yaml.safe_load`, so the vulnerable `full_load` path is not executed.
```bash
cp lab-changes/pyyaml-not-affected.openvex.json vex/
git add vex && git commit -m "LAB-12: VEX not_affected for CVE-2020-14343" && git push
```
Observe that Grype now suppresses the CVE for that product (VERIFY CURRENT PRODUCT BEHAVIOUR — Grype matches VEX `products` by package URL / image identity; adjust `@id` if it does not match). Then **revert the VEX and upgrade anyway**: a VEX statement is a reviewed, expiring engineering claim, not a way to keep a critical, easily-fixed dependency.

## Step 10 — Validate the Fix
### Expected Result
- With PyYAML 6.0.3 and no VEX file, Grype passes.
- The SBOM artifact for the fixed build lists `pkg:pypi/pyyaml@6.0.3`.
- You can explain in one sentence why Path A was chosen over Path B.

## Step 11 — Cleanup
Delete branches; artifacts expire after 30 days (or delete them from the run page). No cloud resources used.

## What You Should Have Learned
SBOMs turn "are we affected?" from a scramble into a query; VEX records *why* a listed vulnerability does not matter, with evidence and an expiry. Both are only credible when generated automatically from the shipped artefact.

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
Attach the CycloneDX SBOM to the image as a signed attestation in LAB-13 using `actions/attest-sbom`, then verify it with `gh attestation verify --predicate-type https://cyclonedx.org/bom`.

---
**Validation status:** Syft 1.52.0 executed locally (CycloneDX 1.7 output); Grype 0.119.0 and Syft checksums verified; OpenVEX document is valid JSON. Grype scan not executed (vulnerability database unreachable from the validation environment). **EXECUTION VALIDATION REQUIRED.**
