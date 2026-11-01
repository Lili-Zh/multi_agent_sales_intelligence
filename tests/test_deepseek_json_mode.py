
import json

from multi_agent_sales_intelligence.crew import deepseek_research_llm


def main():
    print("Testing DeepSeek Flash JSON Mode...")

    response = deepseek_research_llm.call(
        [
            {
                "role": "user",
                "content": (
                    "Return a JSON object with one field named "
                    "status and value OK. Reply in JSON only."
                ),
            }
        ]
    )

    print("Model response:", response)

    parsed = json.loads(response)
    print("JSON validation: PASS")
    print("Parsed result:", parsed)


if __name__ == "__main__":
    main()
