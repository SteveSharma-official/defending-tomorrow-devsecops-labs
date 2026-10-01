#!/usr/bin/env python3
"""LAB-22 — create and verify a SHA-256 evidence manifest (Chapter 25 §25.3.2 Immutable Forensic Storage).

create <dir> --case ID --collector NAME   writes <dir>/MANIFEST.json (hash of every file + manifest digest)
verify <dir>                               recomputes every hash; exit 1 on any added, missing or altered file
"""
import argparse
import datetime
import hashlib
import json
import pathlib
import sys

NAME = "MANIFEST.json"


def sha256(p: pathlib.Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def files(d: pathlib.Path) -> dict:
    return {str(p.relative_to(d)).replace("\\", "/"): sha256(p)
            for p in sorted(d.rglob("*")) if p.is_file() and p.name != NAME}


def create(d: pathlib.Path, case: str, collector: str, now: str | None = None) -> dict:
    body = {"case_id": case, "collector": collector,
            "collected_at": now or datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
            "algorithm": "sha256", "files": files(d)}
    body["manifest_digest"] = hashlib.sha256(json.dumps(body, sort_keys=True).encode()).hexdigest()
    (d / NAME).write_text(json.dumps(body, indent=2, sort_keys=True), encoding="utf-8")
    return body


def verify(d: pathlib.Path) -> list[str]:
    m = json.loads((d / NAME).read_text(encoding="utf-8"))
    digest = m.pop("manifest_digest")
    problems = []
    if hashlib.sha256(json.dumps(m, sort_keys=True).encode()).hexdigest() != digest:
        problems.append("manifest itself has been modified")
    actual = files(d)
    for name, h in m["files"].items():
        if name not in actual:
            problems.append(f"missing: {name}")
        elif actual[name] != h:
            problems.append(f"altered: {name}")
    problems += [f"added after collection: {n}" for n in actual if n not in m["files"]]
    return problems


def main() -> int:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("create")
    c.add_argument("dir")
    c.add_argument("--case", required=True)
    c.add_argument("--collector", required=True)
    v = sub.add_parser("verify")
    v.add_argument("dir")
    a = ap.parse_args()
    d = pathlib.Path(a.dir)
    if a.cmd == "create":
        m = create(d, a.case, a.collector)
        print(f"{len(m['files'])} file(s) hashed; manifest digest {m['manifest_digest']}")
        return 0
    problems = verify(d)
    for p in problems:
        print(f"::error::{p}")
    print("evidence intact" if not problems else f"{len(problems)} integrity problem(s)")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
