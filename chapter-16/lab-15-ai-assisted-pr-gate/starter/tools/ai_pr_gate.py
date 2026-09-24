#!/usr/bin/env python3
"""ai_pr_gate.py — pre-merge gate for AI-assisted pull requests (LAB-15, Chapter 16 §16.4).

Hardened, runnable version of the Chapter 16 AI-assisted PR gate listing:
  * reviewer identities are compared as strings (the original called .get() on a string);
  * only each reviewer's LATEST review counts (a later "CHANGES_REQUESTED" cancels an approval);
  * the PR author can never satisfy their own review requirement;
  * path classification matches whole path segments, reducing false positives;
  * input comes from the GitHub API (see workflow), not from a free-form environment variable.

Input: JSON file with {"author", "labels", "files", "reviews"} (see tests/fixtures).
Exit 0 = requirements met or not AI-tagged; exit 1 = requirements not met.
"""
import json
import re
import sys

AI_LABELS = {"ai-assisted", "ai-generated"}

CRITICAL = re.compile(
    r"(^|/)(auth|authn|authz|login|session|crypto|secrets?|credentials?|payments?|billing|pii|iam)(/|\.|_|$)"
    r"|(^|/)\.github/workflows/"
    r"|\.tf$",
    re.IGNORECASE,
)
ADJACENT = re.compile(
    r"(^|/)(validation|validators?|saniti[sz]e\w*|middleware|config|logging|rate_?limit\w*)(/|\.|_|$)",
    re.IGNORECASE,
)

MIN_APPROVALS_CRITICAL = 2
MIN_SECURITY_APPROVALS_CRITICAL = 1
MIN_APPROVALS_ADJACENT = 1


def classify(files: list[str]) -> dict[str, list[str]]:
    result: dict[str, list[str]] = {"critical": [], "adjacent": [], "standard": []}
    for path in files:
        if CRITICAL.search(path):
            result["critical"].append(path)
        elif ADJACENT.search(path):
            result["adjacent"].append(path)
        else:
            result["standard"].append(path)
    return result


def current_approvers(reviews: list[dict], author: str) -> set[str]:
    """Latest non-comment review state per reviewer; the author is excluded."""
    latest: dict[str, str] = {}
    for review in sorted(reviews, key=lambda r: r.get("submitted_at", "")):
        user = review.get("user", "")
        state = review.get("state", "")
        if user and user != author and state in {"APPROVED", "CHANGES_REQUESTED", "DISMISSED"}:
            latest[user] = state
    return {user for user, state in latest.items() if state == "APPROVED"}


def evaluate(pr: dict, security_reviewers: set[str]) -> tuple[bool, list[str]]:
    labels = {label.lower() for label in pr.get("labels", [])}
    if not labels & AI_LABELS:
        return True, ["NOT_AI_TAGGED: standard review process applies"]
    classes = classify(pr.get("files", []))
    approvers = current_approvers(pr.get("reviews", []), pr.get("author", ""))
    security_approvers = approvers & security_reviewers
    problems: list[str] = []
    if classes["critical"]:
        if len(security_approvers) < MIN_SECURITY_APPROVALS_CRITICAL:
            problems.append(f"SECURITY_EXPERT_REVIEW_REQUIRED for {classes['critical']}")
        if len(approvers) < MIN_APPROVALS_CRITICAL:
            problems.append(f"MINIMUM_REVIEWERS_NOT_MET: {len(approvers)}/{MIN_APPROVALS_CRITICAL} approvals")
    elif classes["adjacent"] and len(approvers) < MIN_APPROVALS_ADJACENT:
        problems.append(f"ENHANCED_REVIEW_REQUIRED for {classes['adjacent']}")
    return (not problems), problems or [f"APPROVED: tiers met ({classes})"]


def load_reviewers(path: str) -> set[str]:
    with open(path, encoding="utf-8") as handle:
        return {line.strip() for line in handle if line.strip() and not line.startswith("#")}


def main(argv: list[str]) -> int:
    pr_path, reviewers_path = argv[1], argv[2]
    with open(pr_path, encoding="utf-8") as handle:
        pr = json.load(handle)
    passed, messages = evaluate(pr, load_reviewers(reviewers_path))
    for message in messages:
        print(("AI_GATE: " if passed else "::error::AI_GATE: ") + message)
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
