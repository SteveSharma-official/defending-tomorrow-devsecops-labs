import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ai_pr_gate import classify, current_approvers, evaluate  # noqa: E402

SEC = {"sec-lead"}


def pr(labels, files, reviews, author="dev"):
    return {"author": author, "labels": labels, "files": files, "reviews": reviews}


def review(user, state, ts="2026-09-01T00:00:00Z"):
    return {"user": user, "state": state, "submitted_at": ts}


def test_untagged_pr_passes():
    assert evaluate(pr([], ["app/auth/login.py"], []), SEC)[0]


def test_ai_critical_without_reviews_fails():
    ok, msgs = evaluate(pr(["ai-assisted"], ["app/auth/login.py"], []), SEC)
    assert not ok and any("SECURITY_EXPERT" in m for m in msgs)


def test_ai_critical_with_security_and_second_approval_passes():
    reviews = [review("sec-lead", "APPROVED"), review("peer", "APPROVED")]
    assert evaluate(pr(["ai-assisted"], ["app/auth/login.py"], reviews), SEC)[0]


def test_author_cannot_self_approve():
    reviews = [review("sec-lead", "APPROVED"), review("peer", "APPROVED")]
    ok, _ = evaluate(pr(["ai-assisted"], ["app/auth/login.py"], reviews, author="sec-lead"), SEC)
    assert not ok


def test_later_changes_requested_cancels_approval():
    reviews = [review("sec-lead", "APPROVED", "2026-09-01T00:00:00Z"),
               review("peer", "APPROVED"),
               review("sec-lead", "CHANGES_REQUESTED", "2026-09-02T00:00:00Z")]
    assert current_approvers(reviews, "dev") == {"peer"}


def test_workflow_and_terraform_are_critical():
    classes = classify([".github/workflows/ci.yml", "infra/main.tf", "app/tokenizer_utils.py"])
    assert classes["critical"] == [".github/workflows/ci.yml", "infra/main.tf"]
    assert classes["standard"] == ["app/tokenizer_utils.py"]


def test_adjacent_needs_one_approval():
    assert not evaluate(pr(["ai-generated"], ["app/middleware.py"], []), SEC)[0]
    assert evaluate(pr(["ai-generated"], ["app/middleware.py"], [review("peer", "APPROVED")]), SEC)[0]
