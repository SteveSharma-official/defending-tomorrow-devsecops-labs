#!/usr/bin/env python3
"""LAB-21 — run every hunt in hunts/ against the dataset and enforce the hypothesis-driven framework.

For each hunts/*.yaml:
  * the definition must carry a hypothesis, tier, ATT&CK/ATLAS technique, data sources, scope and time box (§24.2)
  * the query runs in DuckDB; rows → disposition "confirmed", none → "cleared" (§24.2 phase 5)
  * a confirmed hunt must name a detection candidate that exists (§24.2 phase 6, the hunter-to-rule pipeline)
Writes hunt-report.json. Exit code 1 if any hunt definition or feedback rule is violated.
Usage: python tools/run_hunts.py [--report hunt-report.json]
"""
import argparse
import json
import pathlib
import sys

import duckdb
import yaml

ROOT = pathlib.Path(__file__).resolve().parents[1]
COLUMNS = {
    "cloudtrail": "{eventTime: 'VARCHAR', userName: 'VARCHAR', sourceIPAddress: 'VARCHAR', "
                  "eventName: 'VARCHAR', errorCode: 'VARCHAR'}",
    "agent_communication_log": "{communication_timestamp: 'VARCHAR', sender_agent_id: 'VARCHAR', "
                               "receiver_agent_id: 'VARCHAR', sender_documented_function: 'VARCHAR', "
                               "message_content: 'VARCHAR', event_type: 'VARCHAR'}",
}
REQUIRED = ("id", "title", "tier", "attack_technique", "hypothesis", "data_sources", "scope", "query",
            "time_allocation_hours")


def connect() -> duckdb.DuckDBPyConnection:
    con = duckdb.connect()
    # Load every column as text, exactly as a raw log store would; each hunt parses what it needs.
    for table, fname in (("cloudtrail", "cloudtrail.jsonl"), ("agent_communication_log", "agent_communication_log.jsonl")):
        con.execute(f"CREATE TABLE {table} AS SELECT * FROM read_json_auto('{ROOT / 'data' / fname}', "
                    "auto_detect = false, columns = " + COLUMNS[table] + ")")
    con.execute("CREATE TABLE agent_collaboration_config AS SELECT * FROM "
                f"read_csv_auto('{ROOT / 'data' / 'agent_collaboration_config.csv'}')")
    return con


def run_hunt(con, path: pathlib.Path) -> tuple[dict, list[str]]:
    hunt = yaml.safe_load(path.read_text(encoding="utf-8"))
    errors = [f"{path.name}: missing '{k}'" for k in REQUIRED if not hunt.get(k)]
    if errors:
        return {"id": hunt.get("id", path.stem)}, errors
    sql = (path.parent / hunt["query"]).read_text(encoding="utf-8")
    cur = con.execute(sql)
    cols = [d[0] for d in cur.description]
    rows = [dict(zip(cols, map(str, r))) for r in cur.fetchall()]
    result = {"id": hunt["id"], "tier": hunt["tier"], "technique": hunt["attack_technique"],
              "disposition": "confirmed" if rows else "cleared", "rows": rows}
    if rows:
        candidate = (hunt.get("feedback") or {}).get("detection_candidate")
        if not candidate:
            errors.append(f"{hunt['id']}: confirmed hunt has no feedback.detection_candidate")
        elif not (ROOT / candidate).is_file():
            errors.append(f"{hunt['id']}: detection candidate {candidate} does not exist")
    return result, errors


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--report", default="hunt-report.json")
    args = ap.parse_args()
    con = connect()
    results, errors = [], []
    for path in sorted((ROOT / "hunts").glob("*.yaml")):
        r, e = run_hunt(con, path)
        results.append(r)
        errors += e
        print(f"{r['id']}: {r.get('disposition', 'invalid')} ({len(r.get('rows', []))} rows)")
    pathlib.Path(args.report).write_text(json.dumps(results, indent=2), encoding="utf-8")
    for e in errors:
        print(f"::error::{e}")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
