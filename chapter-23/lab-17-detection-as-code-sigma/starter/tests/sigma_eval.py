"""Minimal, deliberately small Sigma evaluator for unit-testing rule LOGIC in CI (LAB-17).

Supports: named selections of field→value(s) maps, modifiers |contains |startswith |endswith,
nested fields via dot notation, and conditions composed of selection names with 'and', 'or', 'not'
and parentheses. It is a test harness, not a SIEM: production matching happens in the converted
backend query.
"""
import re

import yaml


def _get(event, dotted):
    node = event
    for part in dotted.split("."):
        if not isinstance(node, dict) or part not in node:
            return None
        node = node[part]
    return node


def _match_value(actual, expected, modifier):
    if actual is None:
        return False
    actual, expected = str(actual).lower(), str(expected).lower()
    return {"": actual == expected, "contains": expected in actual,
            "startswith": actual.startswith(expected), "endswith": actual.endswith(expected)}[modifier]


def _selection_matches(event, selection):
    for key, expected in selection.items():
        field, _, modifier = key.partition("|")
        values = expected if isinstance(expected, list) else [expected]
        if not any(_match_value(_get(event, field), v, modifier) for v in values):
            return False
    return True


def matches(rule_path, event):
    with open(rule_path, encoding="utf-8") as handle:
        rule = yaml.safe_load(handle)
    detection = dict(rule["detection"])
    condition = detection.pop("condition")
    results = {name: _selection_matches(event, sel) for name, sel in detection.items()}
    expr = re.sub(r"[A-Za-z_][A-Za-z0-9_]*",
                  lambda m: m.group(0) if m.group(0) in {"and", "or", "not"} else str(results[m.group(0)]),
                  condition)
    return bool(eval(expr, {"__builtins__": {}}, {}))  # noqa: S307 - expression built only from True/False/and/or/not
