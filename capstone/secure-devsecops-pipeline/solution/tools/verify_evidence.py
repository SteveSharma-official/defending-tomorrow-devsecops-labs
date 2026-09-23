#!/usr/bin/env python3
"""verify_evidence.py — recompute an evidence record's SHA-256 to detect tampering (LAB-16)."""
import hashlib
import json
import sys

with open(sys.argv[1], encoding="utf-8") as handle:
    record = json.load(handle)
claimed = record.pop("sha256", None)
actual = hashlib.sha256(json.dumps(record, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
print(f"claimed={claimed}\nactual ={actual}")
if claimed != actual:
    print("::error::EVIDENCE INTEGRITY FAILURE — record modified after generation")
    sys.exit(1)
print("Evidence integrity verified")
