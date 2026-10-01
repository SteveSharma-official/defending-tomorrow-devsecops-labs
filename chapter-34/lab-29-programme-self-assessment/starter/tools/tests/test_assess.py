"""LAB-29 tests: scoring follows the Chapter 34 guide, and unsupported claims are rejected."""
import copy
import datetime
import pathlib
import sys

import yaml

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
import assess  # noqa: E402

CHECK = yaml.safe_load((ROOT / "assessment" / "checklist-34.1.yaml").read_text(encoding="utf-8"))
SA = yaml.safe_load((ROOT / "assessment" / "self-assessment.yaml").read_text(encoding="utf-8"))


def test_checklist_has_the_twelve_book_items():
    assert [i["id"] for i in CHECK["items"]] == [f"C34-{n:02d}" for n in range(1, 13)]


def test_sample_scores_as_transitioning(tmp_path):
    rows, score, level, errors = assess.assess(CHECK, SA)
    assert errors == [] and score == 4 and level == "Transitioning"
    assess.write(rows, score, level, SA, tmp_path)
    assert "Score: 4/12 — Transitioning" in (tmp_path / "workbook.md").read_text(encoding="utf-8")


def test_claim_without_evidence_is_rejected():
    sa = copy.deepcopy(SA)
    sa["answers"]["C34-07"] = {"status": "implemented", "owner": "Priya Raman", "reviewed_on": datetime.date(2026, 9, 1)}
    assert any(e.startswith("V2 C34-07") for e in assess.assess(CHECK, sa)[3])


def test_team_owner_is_the_accountability_gap():
    sa = copy.deepcopy(SA)
    sa["answers"]["C34-07"]["owner"] = "Security team"
    assert any(e.startswith("V3 C34-07") for e in assess.assess(CHECK, sa)[3])


def test_stale_evidence_is_rejected():
    sa = copy.deepcopy(SA)
    sa["answers"]["C34-11"]["reviewed_on"] = datetime.date(2025, 1, 15)
    assert any(e.startswith("V4 C34-11") for e in assess.assess(CHECK, sa)[3])


def test_scoring_bands_match_the_book():
    assert [next(n for top, n in assess.LEVELS if s <= top) for s in (0, 3, 4, 6, 7, 9, 10, 12)] == \
        ["Traditional", "Traditional", "Transitioning", "Transitioning", "Operational", "Operational", "Advanced", "Advanced"]
