
from multi_agent_sales_intelligence.models import CRMLead
from multi_agent_sales_intelligence.approval_manager import (
    create_pending_review,
)
from multi_agent_sales_intelligence.mock_crm import save_lead


def prepare_demo_workflow(
    run_id: str,
    company_name: str,
    lead_id: str,
) -> None:
    """Prepare a simulated Agent run for human review."""

    # Step 1: Simulate a completed Agent run
    print(f"Agent run completed for: {company_name}")

    # Step 2: Create a pending human review
    review = create_pending_review(
        run_id,
        company_name,
    )

    # Step 3: Create a CRM lead
    lead = CRMLead(
        lead_id=lead_id,
        company_name=company_name,
        run_id=run_id,
    )

    save_lead(lead)

    print(f"Review status: {review.status}")
    print(f"CRM lead status: {lead.status}")
    print("Waiting for human approval.")
