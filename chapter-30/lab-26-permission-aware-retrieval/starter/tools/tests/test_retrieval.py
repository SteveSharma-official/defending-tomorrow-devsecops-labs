"""LAB-26 — security tests for permission-aware retrieval.

The key property (§30.3.1): for a user without access, the response must be identical whether or not
restricted documents exist in the index. Anything else leaks their existence.
"""
import json
import pathlib
import sys

import pytest
import yaml

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "rag"))
from retriever import Retriever  # noqa: E402

DOCS = json.loads((ROOT / "corpus" / "knowledge-base.json").read_text())["documents"]
CFG = yaml.safe_load((ROOT / "rag" / "rag-config.yaml").read_text())
STAFF = {"all-staff"}
EXEC = {"all-staff", "exec"}
PROBES = ["Project Kestrel acquisition target valuation", "acquisition due diligence risks",
          "salary bands payroll", "what is the acquisition target name"]


def restricted_ids(groups):
    return {d["id"] for d in DOCS if not set(d["groups"]) & groups}


@pytest.mark.parametrize("query", PROBES)
def test_restricted_content_never_reaches_unauthorised_user(query):
    response, _ = Retriever(DOCS, CFG).retrieve(query, STAFF)
    assert not {r["id"] for r in response["results"]} & restricted_ids(STAFF)


@pytest.mark.parametrize("query", PROBES)
def test_existence_of_restricted_documents_is_not_inferable(query):
    with_restricted, _ = Retriever(DOCS, CFG).retrieve(query, STAFF)
    visible_only = [d for d in DOCS if set(d["groups"]) & STAFF]
    without_restricted, _ = Retriever(visible_only, CFG).retrieve(query, STAFF)
    assert with_restricted == without_restricted


def test_authorised_user_still_gets_restricted_answer():
    response, _ = Retriever(DOCS, CFG).retrieve("Project Kestrel acquisition valuation", EXEC)
    assert response["results"][0]["id"] in {"KB-004", "KB-005"}


def test_tampered_and_injected_document_is_excluded():
    _, excluded = Retriever(DOCS, CFG).retrieve("VPN fails troubleshooting", STAFF)
    assert {"id": "KB-009", "reason": "INTEGRITY_FAILURE"} in excluded


def test_injection_scan_catches_instructions_even_with_valid_hash():
    docs = [dict(d) for d in DOCS]
    kb9 = next(d for d in docs if d["id"] == "KB-009")
    import hashlib
    kb9["sha256"] = hashlib.sha256(kb9["text"].encode()).hexdigest()     # attacker also re-hashed it
    _, excluded = Retriever(docs, CFG).retrieve("VPN fails troubleshooting", STAFF)
    assert {"id": "KB-009", "reason": "INJECTION_DETECTED"} in excluded
