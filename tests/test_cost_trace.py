
import json
from pathlib import Path
from unittest.mock import MagicMock, patch

from crewai.types.usage_metrics import UsageMetrics
from multi_agent_sales_intelligence import main as main_module


def main():
    trace_dir = Path("traces")
    trace_dir.mkdir(exist_ok=True)

    before = set(trace_dir.glob("*.json"))

    mock_result = MagicMock()
    mock_result.token_usage = UsageMetrics(
        prompt_tokens=10000,
        cached_prompt_tokens=4000,
        completion_tokens=2000,
        total_tokens=12000,
        successful_requests=2,
    )

    mock_crew = MagicMock()
    mock_crew.kickoff.return_value = mock_result

    mock_builder = MagicMock()
    mock_builder.crew.return_value = mock_crew

    with patch.object(
        main_module,
        "MultiAgentSalesIntelligence",
        return_value=mock_builder,
    ):
        main_module.run()

    after = set(trace_dir.glob("*.json"))
    new_files = after - before

    assert len(new_files) == 1, (
        f"Expected one new trace file, found {len(new_files)}"
    )

    trace_path = new_files.pop()
    trace = json.loads(trace_path.read_text(encoding="utf-8"))

    assert trace["status"] == "SUCCESS"
    assert trace["token_usage"]["prompt_tokens"] == 10000
    assert trace["token_usage"]["cached_prompt_tokens"] == 4000

    cost = trace["estimated_cost"]

    assert cost["model"] == "deepseek-flash"
    assert cost["input_cost"] == 0.001824
    assert cost["output_cost"] == 0.0024
    assert cost["total_estimated_cost"] == 0.004224

    print("Cost Trace integration test: PASS")
    print("Trace file:", trace_path)
    print("Estimated cost:", cost["total_estimated_cost"], "USD")


if __name__ == "__main__":
    main()
