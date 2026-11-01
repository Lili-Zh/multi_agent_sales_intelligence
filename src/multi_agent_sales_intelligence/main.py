from multi_agent_sales_intelligence.tracing import set_run_id, reset_run_id
import json
from pathlib import Path

from multi_agent_sales_intelligence.cost_calculator import calculate_llm_cost

import time

#!/usr/bin/env python
import sys
import warnings

from datetime import datetime, timezone
from uuid import uuid4

from multi_agent_sales_intelligence.crew import MultiAgentSalesIntelligence

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")


def run():
    """
    Run the sales intelligence crew.
    """
    inputs = {
        "company_name": "Anthropic",
        "industry": "Artificial Intelligence",
        "solution_name": "AI Sales Intelligence Platform",
        "solution_description": (
            "A B2B sales intelligence platform that automates account research, "
            "evidence collection, lead qualification, sales opportunity analysis, "
            "and personalized outreach planning."
        ),
    }
   
    
    
    run_id = str(uuid4())
    token = set_run_id(run_id)

    started_at = datetime.now(timezone.utc).isoformat()

    start_time = time.perf_counter()
    status = "FAILED"
    error_message = None
    token_usage = None
    estimated_cost = None

    print("Crew execution started.")

    try:
        result = MultiAgentSalesIntelligence().crew().kickoff(inputs=inputs)

      
        usage = getattr(result, "token_usage", None)
        if usage is not None:
            token_usage = usage.model_dump()
            estimated_cost = calculate_llm_cost(token_usage)

        status = "SUCCESS"
        print("Crew execution completed.")
        print(result)

    except Exception as e:
        error_message = str(e)
        print("Crew execution failed.")
        raise

  
    finally:
        elapsed_time = time.perf_counter() - start_time
        finished_at = datetime.now(timezone.utc).isoformat()

        trace = {
            "run_id": run_id,
            "company_name": inputs["company_name"],
            "status": status,
            "started_at": started_at,
            "finished_at": finished_at,
            "duration_seconds": round(elapsed_time, 2),
            "error": error_message,
            "token_usage": token_usage,
            "estimated_cost": estimated_cost,
        }

        output_dir = Path("traces")
        output_dir.mkdir(parents=True, exist_ok=True)

        output_path = output_dir / f"{run_id}.json"

        output_path.write_text(
            json.dumps(trace, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

        print(f"Execution duration: {elapsed_time:.2f} seconds")
        print(f"Execution trace saved to: {output_path}")

        reset_run_id(token)


def train():
    """
    Train the crew for a given number of iterations.
    """
    inputs = {
        "topic": "AI LLMs",
        'current_year': str(datetime.now().year)
    }
    try:
        MultiAgentSalesIntelligence().crew().train(n_iterations=int(sys.argv[1]), filename=sys.argv[2], inputs=inputs)

    except Exception as e:
        raise Exception(f"An error occurred while training the crew: {e}")

def replay():
    """
    Replay the crew execution from a specific task.
    """
    try:
        MultiAgentSalesIntelligence().crew().replay(task_id=sys.argv[1])

    except Exception as e:
        raise Exception(f"An error occurred while replaying the crew: {e}")

def test():
    """
    Test the crew execution and returns the results.
    """
    inputs = {
        "topic": "AI LLMs",
        "current_year": str(datetime.now().year)
    }

    try:
        MultiAgentSalesIntelligence().crew().test(n_iterations=int(sys.argv[1]), eval_llm=sys.argv[2], inputs=inputs)

    except Exception as e:
        raise Exception(f"An error occurred while testing the crew: {e}")

def run_with_trigger():
    """
    Run the crew with trigger payload.
    """
    import json

    if len(sys.argv) < 2:
        raise Exception("No trigger payload provided. Please provide JSON payload as argument.")

    try:
        trigger_payload = json.loads(sys.argv[1])
    except json.JSONDecodeError:
        raise Exception("Invalid JSON payload provided as argument")

    inputs = {
        "crewai_trigger_payload": trigger_payload,
        "topic": "",
        "current_year": ""
    }

    try:
        result = MultiAgentSalesIntelligence().crew().kickoff(inputs=inputs)
        return result
    except Exception as e:
        raise Exception(f"An error occurred while running the crew with trigger: {e}")
