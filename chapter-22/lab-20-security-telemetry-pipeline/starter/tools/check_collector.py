#!/usr/bin/env python3
"""LAB-20 — static security checks on an OpenTelemetry Collector config (Chapter 22).

`otelcol-contrib validate` proves the config is *loadable*. These checks prove it is *security-fit*:
  C1  the logs pipeline enriches with k8sattributes, then attributes/security, and batches last
  C2  no sampling processor on the logs pipeline (Table 22.2 Fidelity: zero sampling on critical events)
  C3  every ${...} reference uses the explicit ${env:NAME} form
  C4  no literal credential in exporter headers
  C5  exporters send over HTTPS only
  C6  the pipeline stamps provenance (security.telemetry_source)
Usage: python tools/check_collector.py collector/security-collector.yaml
"""
import re
import sys

import yaml

SAMPLERS = ("probabilistic_sampler", "tail_sampling", "sampling")


def check(cfg: dict, raw: str) -> list[str]:
    findings = []
    logs = cfg.get("service", {}).get("pipelines", {}).get("logs")
    if not logs:
        return ["C1 no logs pipeline defined in service.pipelines"]
    procs = logs.get("processors", [])
    names = [p.split("/")[0] for p in procs]
    if "k8sattributes" not in names or "attributes/security" not in procs:
        findings.append("C1 logs pipeline must include k8sattributes and attributes/security")
    elif procs.index("attributes/security") < names.index("k8sattributes"):
        findings.append("C1 attributes/security runs before k8sattributes — the attributes it copies do not exist yet")
    if procs and names[-1] != "batch":
        findings.append("C1 batch must be the last processor in the logs pipeline")
    for p in procs:
        if p.split("/")[0].startswith(SAMPLERS):
            findings.append(f"C2 sampling processor '{p}' on the logs pipeline destroys low-frequency attack signals")
    for ref in re.findall(r"\$\{([^}]*)\}", raw):
        if not ref.startswith("env:"):
            findings.append(f"C3 '${{{ref}}}' — use ${{env:NAME}}; bare placeholders are treated as environment variables")
    for name, exp in (cfg.get("exporters") or {}).items():
        exp = exp or {}
        for header, value in (exp.get("headers") or {}).items():
            if header.lower() in ("authorization", "x-api-key") and "${" not in str(value):
                findings.append(f"C4 exporter '{name}' header '{header}' contains a literal credential")
        endpoint = str(exp.get("endpoint", ""))
        if endpoint and not endpoint.startswith("https://"):
            findings.append(f"C5 exporter '{name}' endpoint is not HTTPS: {endpoint}")
    actions = ((cfg.get("processors") or {}).get("attributes/security") or {}).get("actions", [])
    if not any(a.get("key") == "security.telemetry_source" for a in actions):
        findings.append("C6 attributes/security does not stamp security.telemetry_source (provenance)")
    return findings


def main(path: str) -> int:
    raw = open(path, encoding="utf-8").read()
    findings = check(yaml.safe_load(raw), raw)
    for f in findings:
        print(f"::error file={path}::{f}")
    print(f"{path}: {len(findings)} finding(s)")
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
