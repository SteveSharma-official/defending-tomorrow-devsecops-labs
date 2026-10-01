"""Ground-truth tests: each hunt must find the planted activity and nothing legitimate.

These protect hunts from well-meaning "noise reduction" that removes the attacker along with the noise.
"""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
import run_hunts  # noqa: E402

CON = run_hunts.connect()


def run(name):
    result, errors = run_hunts.run_hunt(CON, ROOT / "hunts" / name)
    assert errors == [], errors
    return result


def test_cloud_hunt_confirms_the_stolen_key_activity():
    r = run("HUNT-CLOUD-001.yaml")
    assert r["disposition"] == "confirmed"
    assert {row["sourceIPAddress"] for row in r["rows"]} == {"198.51.100.66"}
    assert "GetSecretValue" in {row["eventName"] for row in r["rows"]}
    assert len(r["rows"]) == 6          # the complete attacker sequence, including the denied call


def test_agent_hunt_finds_the_propagated_instruction_only():
    r = run("HUNT-AGENT-003.yaml")
    assert r["disposition"] == "confirmed"
    assert [(x["sender_agent_id"], x["receiver_agent_id"]) for x in r["rows"]] == [("summariser-bot", "payments-agent")]


def test_orchestrator_instructions_are_not_flagged():
    r = run("HUNT-AGENT-003.yaml")
    assert all(x["sender_agent_id"] != "orchestrator" for x in r["rows"])


def test_every_hunt_definition_is_complete():
    for path in (ROOT / "hunts").glob("*.yaml"):
        _, errors = run_hunts.run_hunt(CON, path)
        assert errors == [], errors
