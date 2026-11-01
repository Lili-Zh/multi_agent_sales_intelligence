
import pytest

from multi_agent_sales_intelligence.approval_manager import (
    create_pending_review,
    submit_review,
)
from multi_agent_sales_intelligence.sales_action import (
    execute_sales_action,
)


@pytest.mark.parametrize(
    "status",
    [
        "APPROVED",
        "REJECTED",
        "REVISION_REQUESTED",
        "PENDING",
    ],
)
def test_sales_action_approval_states(tmp_path, monkeypatch, status):
    from multi_agent_sales_intelligence import approval_manager

    monkeypatch.setattr(
        approval_manager,
        "APPROVALS_DIR",
        tmp_path,
    )

    run_id = f"test-{status.lower()}"
    create_pending_review(run_id, "Test Company")

    if status != "PENDING":
        submit_review(
            run_id,
            "Test Reviewer",
            status,
            "Test review decision.",
        )

    if status == "APPROVED":
        result = execute_sales_action(run_id)
        assert "Sales action executed" in result
    else:
        with pytest.raises(PermissionError):
            execute_sales_action(run_id)


def test_sales_action_missing_review(tmp_path, monkeypatch):
    from multi_agent_sales_intelligence import approval_manager

    monkeypatch.setattr(
        approval_manager,
        "APPROVALS_DIR",
        tmp_path,
    )

    with pytest.raises(FileNotFoundError):
        execute_sales_action("nonexistent-run")
