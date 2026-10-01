#!/usr/bin/env python3
"""LAB-20 — measure sample telemetry against the minimum security log schema (Chapter 22, Table 22.2).

Reports completeness per event_type and fails if any event_type falls below the threshold,
if an outcome value is outside the allowed set, or if a timestamp is not UTC with sub-second precision.
Usage: python tools/check_telemetry.py schema/minimum-security-log-schema.yaml samples/events.jsonl
"""
import json
import re
import sys
from collections import defaultdict

import yaml

TS = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3,6}Z$")


def evaluate(schema: dict, events: list[dict]) -> tuple[dict, list[str]]:
    required = schema["required_fields"]
    allowed = schema.get("allowed_values", {})
    threshold = schema["thresholds"]["completeness_min_pct"]
    totals, complete = defaultdict(int), defaultdict(int)
    errors = []
    for n, e in enumerate(events, 1):
        etype = e.get("event_type") or "(missing event_type)"
        totals[etype] += 1
        if all(e.get(f) not in (None, "") for f in required):
            complete[etype] += 1
        for field, values in allowed.items():
            if field in e and e[field] not in values:
                errors.append(f"event {n}: {field}='{e[field]}' not in {values}")
        if "timestamp" in e and not TS.match(str(e["timestamp"])):
            errors.append(f"event {n}: timestamp '{e['timestamp']}' is not UTC with sub-second precision")
    report = {}
    for etype, total in sorted(totals.items()):
        pct = round(100 * complete[etype] / total, 1)
        report[etype] = {"events": total, "complete": complete[etype], "completeness_pct": pct}
        if pct < threshold:
            errors.append(f"{etype}: completeness {pct}% is below {threshold}%")
    return report, errors


def main(schema_path: str, events_path: str) -> int:
    schema = yaml.safe_load(open(schema_path, encoding="utf-8"))
    events = [json.loads(line) for line in open(events_path, encoding="utf-8") if line.strip()]
    report, errors = evaluate(schema, events)
    print(json.dumps(report, indent=2))
    for e in errors:
        print(f"::error::{e}")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1], sys.argv[2]))
