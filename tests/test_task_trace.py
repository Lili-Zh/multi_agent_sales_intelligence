
import json
from pathlib import Path
from unittest.mock import Mock

from multi_agent_sales_intelligence.crew import record_task_completion
from multi_agent_sales_intelligence.tracing import (
    set_run_id,
    get_run_id,
    reset_run_id,
)


def test_task_completion_callback():
    # Simulate a Crew execution
    test_run_id = "test-run-123"
    token = set_run_id(test_run_id)

    try:
        # Create a simulated TaskOutput
        mock_output = Mock()
        mock_output.description = "Research Anthropic and collect evidence."
        mock_output.raw = "Simulated research result"

        # Trigger the task completion callback
        record_task_completion(mock_output)

        # Verify that the event was saved with the correct Run ID
        output_path = Path("traces/task_events.jsonl")

        with output_path.open("r", encoding="utf-8") as file:
            last_line = file.readlines()[-1]

        event = json.loads(last_line)

        assert event["run_id"] == test_run_id
        assert event["event_type"] == "TASK_COMPLETED"
        assert event["task_description"] == mock_output.description

        print("Task Run ID correlation test: PASS")

    finally:
        # Restore the previous execution context
        reset_run_id(token)

    assert get_run_id() is None
    print("Run ID context reset test: PASS")


if __name__ == "__main__":
    test_task_completion_callback()
