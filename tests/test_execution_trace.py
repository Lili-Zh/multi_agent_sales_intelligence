
import json
from pathlib import Path
from unittest.mock import patch

from multi_agent_sales_intelligence.main import run


def simulate_failure(*args, **kwargs):
    raise RuntimeError("Simulated Crew failure")


def get_trace_files():
    return set(Path("traces").glob("*.json"))


def test_failed_execution_trace():
    before = get_trace_files()

    with patch(
        "multi_agent_sales_intelligence.main.MultiAgentSalesIntelligence"
    ) as mock_crew_class:
        mock_crew_class.return_value.crew.return_value.kickoff.side_effect = (
            simulate_failure
        )

        try:
            run()
        except RuntimeError as error:
            print(f"Expected test error: {error}")
        else:
            raise AssertionError("Expected Crew failure was not raised.")

    new_files = get_trace_files() - before
    assert len(new_files) == 1, "Expected exactly one new trace file."

    trace = json.loads(
        new_files.pop().read_text(encoding="utf-8")
    )

    assert trace["status"] == "FAILED"
    assert trace["company_name"] == "Anthropic"
    assert "Simulated Crew failure" in trace["error"]
    assert trace["duration_seconds"] >= 0
    assert trace["run_id"]
    assert trace["started_at"]
    assert trace["finished_at"]

    print("Execution trace failure test: PASS")


def test_successful_execution_trace():
    before = get_trace_files()

    with patch(
        "multi_agent_sales_intelligence.main.MultiAgentSalesIntelligence"
    ) as mock_crew_class:
        mock_crew_class.return_value.crew.return_value.kickoff.return_value = (
            "Simulated successful Crew result"
        )

        run()

    new_files = get_trace_files() - before
    assert len(new_files) == 1, "Expected exactly one new trace file."

    trace = json.loads(
        new_files.pop().read_text(encoding="utf-8")
    )

    assert trace["status"] == "SUCCESS"
    assert trace["company_name"] == "Anthropic"
    assert trace["error"] is None
    assert trace["duration_seconds"] >= 0
    assert trace["run_id"]
    assert trace["started_at"]
    assert trace["finished_at"]

    print("Execution trace success test: PASS")


if __name__ == "__main__":
    test_failed_execution_trace()
    test_successful_execution_trace()
