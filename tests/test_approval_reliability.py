
import pytest

from multi_agent_sales_intelligence import approval_manager


def test_duplicate_review_creation(tmp_path, monkeypatch):
    """Duplicate run IDs must not overwrite existing reviews."""

    monkeypatch.setattr(
        approval_manager,
        "APPROVALS_DIR",
        tmp_path / "approvals",
    )

    run_id = "test-duplicate-001"

    # Create the first review
    first = approval_manager.create_pending_review(
        run_id,
        "Test Company",
    )

    assert first.status == "PENDING"

    # Attempt to create the same review again
    with pytest.raises(FileExistsError):
        approval_manager.create_pending_review(
            run_id,
            "Another Company",
        )

    # Verify the original review was not overwritten
    saved = approval_manager.get_review(run_id)

    assert saved.company_name == "Test Company"
    assert saved.status == "PENDING"



def test_duplicate_review_submission(tmp_path, monkeypatch):
    """An approved review cannot be overwritten."""

    monkeypatch.setattr(
        approval_manager,
        "APPROVALS_DIR",
        tmp_path / "approvals",
    )

    run_id = "test-duplicate-submission-001"

    approval_manager.create_pending_review(
        run_id,
        "Test Company",
    )

    first = approval_manager.submit_review(
        run_id,
        "First Reviewer",
        "APPROVED",
        "Approved for testing.",
    )

    assert first.status == "APPROVED"

    # Attempt to overwrite the existing approval
    with pytest.raises(ValueError, match="Cannot review"):
        approval_manager.submit_review(
            run_id,
            "Second Reviewer",
            "REJECTED",
            "Trying to overwrite the approval.",
        )

    # Verify the original approval is unchanged
    saved = approval_manager.get_review(run_id)

    assert saved.status == "APPROVED"
    assert saved.reviewer == "First Reviewer"
    assert saved.review_comment == "Approved for testing."
    assert saved.reviewed_at == first.reviewed_at
