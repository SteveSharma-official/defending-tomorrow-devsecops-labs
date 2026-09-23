import os

import pytest
import yaml

from sigma_eval import matches

HERE = os.path.dirname(os.path.abspath(__file__))
RULES = os.path.join(os.path.dirname(HERE), "rules")
CASES = yaml.safe_load(open(os.path.join(HERE, "events", "cases.yaml"), encoding="utf-8"))


@pytest.mark.parametrize("case", CASES, ids=[c["name"] for c in CASES])
def test_rule_behaviour(case):
    result = matches(os.path.join(RULES, case["rule"]), case["event"])
    assert result == (case["expect"] == "match"), f"{case['rule']}: {case['name']}"


def test_every_rule_has_a_true_positive_case():
    covered = {c["rule"] for c in CASES if c["expect"] == "match"}
    assert covered == set(os.listdir(RULES))
