
from multi_agent_sales_intelligence.crew import (
    MultiAgentSalesIntelligence,
    record_task_completion,
)


def test_callback_binding():
    project = MultiAgentSalesIntelligence()

    research_task = project.lead_research_task()
    strategy_task = project.sales_strategy_task()

    assert research_task.callback is record_task_completion
    print("Research Task callback binding: PASS")

    assert strategy_task.callback is record_task_completion
    print("Strategy Task callback binding: PASS")


if __name__ == "__main__":
    test_callback_binding()
