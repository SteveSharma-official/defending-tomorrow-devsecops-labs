#!/usr/bin/env python3
"""LAB-29 — score a Checklist 34.1 self-assessment and generate the workbook (Chapter 34).

Validation (fails the build):
  V1 every checklist item has an answer with a valid status
  V2 "implemented" requires evidence that exists in the repository
  V3 every answer names an individual owner — teams and "everyone" are the accountability gap (§34.6)
  V4 "implemented" evidence must have been reviewed within 12 months of assessed_on
Outputs: workbook.md (summary, maturity level, gap list) and workbook.csv (opens in Excel).
Usage: python tools/assess.py assessment/checklist-34.1.yaml assessment/self-assessment.yaml out/
"""
import csv
import datetime
import pathlib
import re
import sys

import yaml

ROOT = pathlib.Path(__file__).resolve().parents[1]
STATUSES = {"implemented", "partial", "not_implemented"}
LEVELS = [(3, "Traditional"), (6, "Transitioning"), (9, "Operational"), (12, "Advanced")]
TEAM_WORDS = re.compile(r"\b(team|everyone|all|security|it|dept|department|tbd|n/?a)\b", re.I)


def as_date(v):
    return v if isinstance(v, datetime.date) else datetime.date.fromisoformat(str(v))


def assess(checklist: dict, sa: dict) -> tuple[list[dict], int, str, list[str]]:
    rows, errors = [], []
    assessed = as_date(sa["assessed_on"])
    answers = sa.get("answers", {})
    for item in checklist["items"]:
        a = answers.get(item["id"])
        if not a or a.get("status") not in STATUSES:
            errors.append(f"V1 {item['id']}: missing or invalid status")
            continue
        owner = str(a.get("owner", ""))
        if not owner or TEAM_WORDS.search(owner) or len(owner.split()) < 2:
            errors.append(f"V3 {item['id']}: owner '{owner}' is not a named individual")
        if a["status"] == "implemented":
            ev = a.get("evidence")
            if not ev or not (ROOT / ev).is_file():
                errors.append(f"V2 {item['id']}: marked implemented without evidence in the repository")
            rv = a.get("reviewed_on")
            if not rv or (assessed - as_date(rv)).days > 365:
                errors.append(f"V4 {item['id']}: evidence not reviewed within 12 months")
        rows.append({**item, **{k: a.get(k, "") for k in ("status", "owner", "evidence", "note")}})
    score = sum(r["status"] == "implemented" for r in rows)
    level = next(name for top, name in LEVELS if score <= top)
    return rows, score, level, errors


def write(rows, score, level, sa, out: pathlib.Path):
    out.mkdir(parents=True, exist_ok=True)
    with open(out / "workbook.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["id", "control", "reference", "status", "owner", "evidence", "note"])
        w.writeheader()
        w.writerows(rows)
    gaps = [r for r in rows if r["status"] != "implemented"]
    md = [f"# Security Program Maturity — {sa['organisation']}", "",
          f"Assessed {sa['assessed_on']} by {sa['assessor']} against Checklist 34.1.", "",
          f"**Score: {score}/12 — {level}**", "", "## Gaps (owner, then book reference)", "",
          "| Item | Control | Status | Owner | Reference |", "|---|---|---|---|---|"]
    md += [f"| {r['id']} | {r['control']} | {r['status']} | {r['owner']} | {r['reference']} |" for r in gaps]
    (out / "workbook.md").write_text("\n".join(md) + "\n", encoding="utf-8")


def main(checklist_p, sa_p, out_p) -> int:
    checklist = yaml.safe_load(open(checklist_p, encoding="utf-8"))
    sa = yaml.safe_load(open(sa_p, encoding="utf-8"))
    rows, score, level, errors = assess(checklist, sa)
    for e in errors:
        print(f"::error file={sa_p}::{e}")
    if not errors:
        write(rows, score, level, sa, pathlib.Path(out_p))
        print(f"Score {score}/12 — {level}; workbook written to {out_p}")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main(*sys.argv[1:4]))
