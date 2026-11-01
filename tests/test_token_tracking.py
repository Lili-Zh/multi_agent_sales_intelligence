
import json
from pathlib import Path
from unittest.mock import Mock, patch

from crewai.types.usage_metrics import UsageMetrics
from multi_agent_sales_intelligence.main import run


def test_token_tracking():
    trace_dir = Path("traces")
    trace_dir.mkdir(exist_ok=True)

    existing_files = set(trace_dir.glob("*.json"))

    mock_usage = UsageMetrics(
        prompt_tokens=1200,
        completion_tokens=300,
        total_tokens=1500,
        successful_requests=2,
    )

    mock_result = Mock()
    mock_result.token_usage = mock_usage

    with patch(
        "multi_agent_sales_intelligence.main.MultiAgentSalesIntelligence"
    ) as mock_crew_class:
        mock_crew_class.return_value.crew.return_value.kickoff.return_value = (
            mock_result
        )

        run()

    new_files = set(trace_dir.glob("*.json")) - existing_files

    assert len(new_files) == 1, (
        f"Expected one new trace file, found {len(new_files)}"
    )

    trace_path = new_files.pop()

    with trace_path.open("r", encoding="utf-8") as file:
        trace = json.load(file)

    assert trace["status"] == "SUCCESS"
    assert trace["token_usage"]["prompt_tokens"] == 1200
    assert trace["token_usage"]["completion_tokens"] == 300
    assert trace["token_usage"]["total_tokens"] == 1500
    assert trace["token_usage"]["successful_requests"] == 2

    print("Token Usage extraction test: PASS")
    print("Token Usage JSON persistence test: PASS")
    print(f"Trace file: {trace_path}")


if __name__ == "__main__":
    test_token_tracking()
