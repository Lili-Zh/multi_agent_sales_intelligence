from multi_agent_sales_intelligence.approval_manager import require_approval
import json
import re
from pathlib import Path
from datetime import datetime, timezone

from multi_agent_sales_intelligence.models import CRMLead


CRM_DIR = Path("crm_data")


def save_lead(lead: CRMLead) -> CRMLead:
    """Save a CRM lead to a local JSON file."""

    if not re.fullmatch(r"[A-Za-z0-9_-]{1,100}", lead.lead_id):
        raise ValueError("Invalid lead_id.")

    CRM_DIR.mkdir(parents=True, exist_ok=True)

    lead.updated_at = datetime.now(timezone.utc).isoformat()

    file_path = CRM_DIR / f"{lead.lead_id}.json"

    with file_path.open("w", encoding="utf-8") as file:
        json.dump(
            lead.model_dump(),
            file,
            indent=2,
            ensure_ascii=False,
        )

    return lead



def get_lead(lead_id: str) -> CRMLead:
    """Read a CRM lead from a local JSON file."""

    if not re.fullmatch(r"[A-Za-z0-9_-]{1,100}", lead_id):
        raise ValueError("Invalid lead_id.")

    file_path = CRM_DIR / f"{lead_id}.json"

    if not file_path.is_file():
        raise FileNotFoundError(
            f"CRM lead not found: {lead_id}"
        )

    with file_path.open("r", encoding="utf-8") as file:
        data = json.load(file)

    return CRMLead.model_validate(data)



def update_lead_after_approval(
    lead_id: str,
    run_id: str,
    new_status: str,
    next_action: str,
) -> CRMLead:
    """Update a CRM lead only after human approval."""

    # 1. Check human approval
    require_approval(run_id)

    # 2. Load existing CRM lead
    lead = get_lead(lead_id)

    # 3. Ensure the approval belongs to this Agent run
    if lead.run_id != run_id:
        raise ValueError(
            "CRM lead run_id does not match the approved run_id."
        )

    # 4. Validate and update the CRM lead
    updated_lead = lead.model_copy(
        update={
            "status": new_status,
            "next_action": next_action,
        }
    )

    updated_lead = CRMLead.model_validate(
        updated_lead.model_dump()
    )

    # 5. Save updated lead
    return save_lead(updated_lead)
