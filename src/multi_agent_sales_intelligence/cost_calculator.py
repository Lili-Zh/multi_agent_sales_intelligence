
import json
from pathlib import Path


def calculate_llm_cost(token_usage: dict) -> dict:
    """Estimate LLM cost from CrewAI token usage."""

    pricing_path = Path("model_pricing.json")

    with pricing_path.open("r", encoding="utf-8") as file:
        pricing = json.load(file)

    prompt_tokens = token_usage.get("prompt_tokens", 0)
    cached_tokens = token_usage.get("cached_prompt_tokens", 0)
    completion_tokens = token_usage.get("completion_tokens", 0)

    if not all(
        isinstance(value, int) and not isinstance(value, bool)
        for value in (prompt_tokens, cached_tokens, completion_tokens)
    ):
        raise ValueError("Token counts must be integers.")

    if min(prompt_tokens, cached_tokens, completion_tokens) < 0:
        raise ValueError("Token counts cannot be negative.")

    if cached_tokens > prompt_tokens:
        raise ValueError("Cached tokens cannot exceed prompt tokens.")

    uncached_tokens = prompt_tokens - cached_tokens

    input_cost = (
        uncached_tokens * pricing["input_price_per_1m"]
        + cached_tokens * pricing["cached_input_price_per_1m"]
    ) / 1_000_000

    output_cost = (
        completion_tokens * pricing["output_price_per_1m"]
    ) / 1_000_000

    return {
        "model": pricing["model"],
        "pricing_tier": pricing["pricing_tier"],
        "currency": pricing["currency"],
        "input_cost": round(input_cost, 8),
        "output_cost": round(output_cost, 8),
        "total_estimated_cost": round(input_cost + output_cost, 8),
    }
