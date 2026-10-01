"""LAB-26 — a tiny, dependency-free retriever that shows permission-aware retrieval (Chapter 30).

Vectors are bag-of-words term counts with cosine similarity: enough to show the access-control
behaviour; a real system would use an embedding model and a vector database with metadata filters.
"""
import hashlib
import math
import re
from collections import Counter

INJECTION = re.compile(r"ignore (all |previous |prior )?instructions|disregard .{0,20}(rules|policy)|"
                       r"(email|send) .{0,30}password", re.I)


def vec(text: str) -> Counter:
    return Counter(re.findall(r"[a-z0-9]+", text.lower()))


def cosine(a: Counter, b: Counter) -> float:
    dot = sum(a[t] * b[t] for t in a)
    na, nb = math.sqrt(sum(v * v for v in a.values())), math.sqrt(sum(v * v for v in b.values()))
    return dot / (na * nb) if na and nb else 0.0


class Retriever:
    def __init__(self, documents: list[dict], config: dict):
        self.docs, self.cfg = documents, config
        self.index = {d["id"]: vec(d["title"] + " " + d["text"]) for d in documents}

    def _allowed(self, doc: dict, groups: set[str]) -> bool:
        return bool(set(doc["groups"]) & groups)

    def _rank(self, query: str, candidates: list[dict]) -> list[tuple[float, dict]]:
        q = vec(query)
        scored = [(cosine(q, self.index[d["id"]]), d) for d in candidates]
        return sorted([s for s in scored if s[0] > 0], key=lambda s: (-s[0], s[1]["id"]))

    def retrieve(self, query: str, user_groups: set[str]) -> dict:
        k = self.cfg["top_k"]
        if self.cfg["access_control"] == "prefilter":
            ranked = self._rank(query, [d for d in self.docs if self._allowed(d, user_groups)])[:k]
            withheld = 0
        else:  # postfilter: rank everything, then remove what the user may not see
            top = self._rank(query, self.docs)[:k]
            ranked = [s for s in top if self._allowed(s[1], user_groups)]
            withheld = len(top) - len(ranked)
        results, excluded = [], []
        for score, d in ranked:
            if self.cfg.get("verify_provenance") and hashlib.sha256(d["text"].encode()).hexdigest() != d["sha256"]:
                excluded.append({"id": d["id"], "reason": "INTEGRITY_FAILURE"})
                continue
            if self.cfg.get("injection_scan") and INJECTION.search(d["text"]):
                excluded.append({"id": d["id"], "reason": "INJECTION_DETECTED"})
                continue
            results.append({"id": d["id"], "title": d["title"], "text": d["text"], "score": round(score, 4)})
        response = {"results": results}
        if self.cfg.get("disclose_withheld_count") and withheld:
            response["notice"] = f"{withheld} result(s) withheld because you lack access"
        return response, excluded
