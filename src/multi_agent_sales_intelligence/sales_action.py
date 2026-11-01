
from multi_agent_sales_intelligence.approval_manager import require_approval


def execute_sales_action(run_id: str) -> str:
    """Execute a mock sales action after human approval."""

    review = require_approval(run_id)

    message = (
        f"Sales action executed for {review.company_name} "
        f"(run_id={review.run_id})"
    )

    return message
