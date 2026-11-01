
from multi_agent_sales_intelligence.cost_calculator import calculate_llm_cost


def main():
    mock_usage = {
        "prompt_tokens": 10000,
        "cached_prompt_tokens": 4000,
        "completion_tokens": 2000,
    }

    result = calculate_llm_cost(mock_usage)

    print("Cost calculation result:", result)

    # 6000 uncached input tokens * $0.30 / 1M = $0.0018
    # 4000 cached input tokens * $0.006 / 1M = $0.000024
    # 2000 output tokens * $1.20 / 1M = $0.0024
    # Total = $0.004224

    assert result["input_cost"] == 0.001824
    assert result["output_cost"] == 0.0024
    assert result["total_estimated_cost"] == 0.004224

    print("Cost calculation test: PASS")


if __name__ == "__main__":
    main()
