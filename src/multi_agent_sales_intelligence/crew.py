from multi_agent_sales_intelligence.tracing import get_run_id

from pathlib import Path

import json

from crewai import Agent, Crew, Process, Task, LLM, TaskOutput
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from crewai_tools import SerperDevTool, ScrapeWebsiteTool
from pydantic import ValidationError

from multi_agent_sales_intelligence.models import LeadResearchReport

deepseek_research_llm = LLM(
    model="deepseek/deepseek-flash",
    response_format={"type": "json_object"},
    max_tokens=16384,
)

deepseek_strategy_llm = LLM(
    model="deepseek/deepseek-flash",
    max_tokens=8192,
)


from datetime import datetime, timezone


def record_task_completion(task_output: TaskOutput):
    """
    Record a task completion event.
    """
    completed_at = datetime.now(timezone.utc).isoformat()

    trace = {
        "run_id": get_run_id(),
        "event_type": "TASK_COMPLETED",
        "task_description": task_output.description[:100],
        "completed_at": completed_at,
    }

    output_dir = Path("traces")
    output_dir.mkdir(parents=True, exist_ok=True)

    output_path = output_dir / "task_events.jsonl"

    with output_path.open("a", encoding="utf-8") as file:
        file.write(json.dumps(trace, ensure_ascii=False) + "\n")

    print("\n--- Task Trace ---")
    print(f"Task completed at: {completed_at}")
    print(f"Task description: {task_output.description[:100]}")
    print(f"Task trace saved to: {output_path}")
    print("------------------\n")



def validate_lead_research_output(result: TaskOutput):
    """Validate the Lead Research Agent output against our Pydantic schema."""

    try:
        data = json.loads(result.raw)
        validated_report = LeadResearchReport.model_validate(data)

        return True, validated_report.model_dump_json(indent=2)

    except json.JSONDecodeError as e:
        return False, (
            "Your output is not valid JSON. "
            f"Please return only valid JSON matching the required schema. Error: {e}"
        )

    except ValidationError as e:
        return False, (
            "Your JSON does not match the required LeadResearchReport schema. "
            f"Please correct the structure and values. Validation error: {e}"
        )

@CrewBase
class MultiAgentSalesIntelligence:
    """Multi-Agent Sales Intelligence crew"""

    agents: list[BaseAgent]
    tasks: list[Task]

    @agent
    def lead_research_agent(self) -> Agent:
        return Agent(
            config=self.agents_config["lead_research_agent"],  # type: ignore[index]
            llm=deepseek_research_llm,
            tools=[
                SerperDevTool(),
                ScrapeWebsiteTool(),
            ],
            verbose=True,
        )

    @agent
    def sales_strategy_agent(self) -> Agent:
        return Agent(
            config=self.agents_config["sales_strategy_agent"],  # type: ignore[index]
            llm=deepseek_strategy_llm,
            verbose=True,
        )

    @task
    def lead_research_task(self) -> Task:
        return Task(
            config=self.tasks_config["lead_research_task"],  # type: ignore[index]
            agent=self.lead_research_agent(),
            guardrail=validate_lead_research_output,
            guardrail_max_retries=2,
            output_file="lead_research_report.md",
            callback=record_task_completion,
        )

    @task
    def sales_strategy_task(self) -> Task:
        return Task(
            config=self.tasks_config["sales_strategy_task"],  # type: ignore[index]
            agent=self.sales_strategy_agent(),
            context=[self.lead_research_task()],
            output_file="sales_strategy_report.md",
            callback=record_task_completion,
        )

    @crew
    def crew(self) -> Crew:
        """Creates the Multi-Agent Sales Intelligence crew"""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )