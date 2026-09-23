#!/usr/bin/env python3
"""Static checks for Azure Policy definitions (AZ-LAB-02). Azure itself validates aliases at
creation time; this catches structural mistakes in the pull request before anyone runs az."""
import glob
import json
import sys

errors = []
for path in sorted(glob.glob("policies/*.json")):
    with open(path, encoding="utf-8") as handle:
        props = json.load(handle)["properties"]
    for key in ("displayName", "description", "mode", "policyRule", "parameters", "metadata"):
        if key not in props:
            errors.append(f"{path}: missing properties.{key}")
    rule = props.get("policyRule", {})
    if set(rule) != {"if", "then"}:
        errors.append(f"{path}: policyRule must contain exactly 'if' and 'then'")
    if rule.get("then", {}).get("effect") != "[parameters('effect')]":
        errors.append(f"{path}: effect must be parameterised so it can be staged Audit → Deny")
    if props.get("mode") not in {"All", "Indexed"}:
        errors.append(f"{path}: unexpected mode {props.get('mode')}")
    allowed = props.get("parameters", {}).get("effect", {}).get("allowedValues", [])
    if "Disabled" not in allowed:
        errors.append(f"{path}: effect should allow 'Disabled' for emergency rollback")
    print(f"checked {path}")
for e in errors:
    print(f"::error::{e}")
sys.exit(1 if errors else 0)
