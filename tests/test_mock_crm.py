
import pytest

from multi_agent_sales_intelligence.models import CRMLead
from multi_agent_sales_intelligence import mock_crm, approval_manager


def test_approved_crm_update(tmp_path, monkeypatch):
    """Approved runs can update their own CRM lead."""

    monkeypatch.setattr(
        mock_crm, "CRM_DIR", tmp_path / "crm"
    )
    monkeypatch.setattr(
        approval_manager, "APPROVALS_DIR", tmp_path / "approvals"
    )

    run_id = "test-crm-approved"

    approval_manager.create_pending_review(
        run_id, "Test Company"
    )
    approval_manager.submit_review(
        run_id,
        "Test Reviewer",
        "APPROVED",
        "Approved for CRM testing.",
    )

    mock_crm.save_lead(
        CRMLead(
            lead_id="lead-test-001",
            company_name="Test Company",
            run_id=run_id,
        )
    )

    updated = mock_crm.update_lead_after_approval(
        "lead-test-001",
        run_id,
        "QUALIFIED",
        "Schedule a meeting.",
    )

    assert updated.status == "QUALIFIED"
    assert updated.next_action == "Schedule a meeting."

    saved = mock_crm.get_lead("lead-test-001")
    assert saved.status == "QUALIFIED"



def test_rejected_crm_update(tmp_path, monkeypatch):
    """Rejected runs cannot modify CRM data."""

    monkeypatch.setattr(
        mock_crm, "CRM_DIR", tmp_path / "crm"
    )
    monkeypatch.setattr(
        approval_manager, "APPROVALS_DIR", tmp_path / "approvals"
    )

    run_id = "test-crm-rejected"

    approval_manager.create_pending_review(
        run_id, "Test Company"
    )
    approval_manager.submit_review(
        run_id,
        "Test Reviewer",
        "REJECTED",
        "Insufficient evidence.",
    )

    mock_crm.save_lead(
        CRMLead(
            lead_id="lead-test-002",
            company_name="Test Company",
            run_id=run_id,
        )
    )

    original = mock_crm.get_lead("lead-test-002")

    with pytest.raises(PermissionError):
        mock_crm.update_lead_after_approval(
            "lead-test-002",
            run_id,
            "CONTACTED",
            "Send an outreach email.",
        )

    saved = mock_crm.get_lead("lead-test-002")

    assert saved.status == "NEW"
    assert saved.next_action is None
    assert saved.updated_at == original.updated_at



def test_pending_crm_update(tmp_path, monkeypatch):
    """Pending reviews cannot update CRM data."""

    monkeypatch.setattr(
        mock_crm, "CRM_DIR", tmp_path / "crm"
    )
    monkeypatch.setattr(
        approval_manager, "APPROVALS_DIR", tmp_path / "approvals"
    )

    run_id = "test-crm-pending"

    approval_manager.create_pending_review(
        run_id, "Test Company"
    )

    mock_crm.save_lead(
        CRMLead(
            lead_id="lead-test-003",
            company_name="Test Company",
            run_id=run_id,
        )
    )

    original = mock_crm.get_lead("lead-test-003")

    with pytest.raises(PermissionError):
        mock_crm.update_lead_after_approval(
            "lead-test-003",
            run_id,
            "CONTACTED",
            "Send an outreach email.",
        )

    saved = mock_crm.get_lead("lead-test-003")

    assert saved.status == "NEW"
    assert saved.next_action is None
    assert saved.updated_at == original.updated_at



def test_revision_requested_crm_update(tmp_path, monkeypatch):
    """Revision requests cannot modify CRM data."""

    monkeypatch.setattr(
        mock_crm, "CRM_DIR", tmp_path / "crm"
    )
    monkeypatch.setattr(
        approval_manager, "APPROVALS_DIR", tmp_path / "approvals"
    )

    run_id = "test-crm-revision"

    approval_manager.create_pending_review(
        run_id, "Test Company"
    )
    approval_manager.submit_review(
        run_id,
        "Test Reviewer",
        "REVISION_REQUESTED",
        "Please revise the sales strategy.",
    )

    mock_crm.save_lead(
        CRMLead(
            lead_id="lead-test-004",
            company_name="Test Company",
            run_id=run_id,
        )
    )

    original = mock_crm.get_lead("lead-test-004")

    with pytest.raises(PermissionError):
        mock_crm.update_lead_after_approval(
            "lead-test-004",
            run_id,
            "CONTACTED",
            "Send an outreach email.",
        )

    saved = mock_crm.get_lead("lead-test-004")

    assert saved.status == "NEW"
    assert saved.next_action is None
    assert saved.updated_at == original.updated_at



def test_missing_approval_crm_update(tmp_path, monkeypatch):
    """Missing approval records must block CRM updates."""

    monkeypatch.setattr(
        mock_crm, "CRM_DIR", tmp_path / "crm"
    )
    monkeypatch.setattr(
        approval_manager, "APPROVALS_DIR", tmp_path / "approvals"
    )

    mock_crm.save_lead(
        CRMLead(
            lead_id="lead-test-005",
            company_name="Test Company",
            run_id="test-crm-missing",
        )
    )

    original = mock_crm.get_lead("lead-test-005")

    with pytest.raises(FileNotFoundError):
        mock_crm.update_lead_after_approval(
            "lead-test-005",
            "test-crm-missing",
            "CONTACTED",
            "Send an outreach email.",
        )

    saved = mock_crm.get_lead("lead-test-005")

    assert saved.status == "NEW"
    assert saved.next_action is None
    assert saved.updated_at == original.updated_at


def test_crm_run_id_mismatch(tmp_path, monkeypatch):
    """An approved run cannot update another run's CRM lead."""

    monkeypatch.setattr(
        mock_crm, "CRM_DIR", tmp_path / "crm"
    )
    monkeypatch.setattr(
        approval_manager, "APPROVALS_DIR", tmp_path / "approvals"
    )

    # Create an approved review for a different run
    approved_run_id = "test-crm-other-approved"

    approval_manager.create_pending_review(
        approved_run_id, "Test Company"
    )
    approval_manager.submit_review(
        approved_run_id,
        "Test Reviewer",
        "APPROVED",
        "Approved for mismatch testing.",
    )

    # Create a CRM lead belonging to another run
    mock_crm.save_lead(
        CRMLead(
            lead_id="lead-test-006",
            company_name="Test Company",
            run_id="test-crm-original",
        )
    )

    original = mock_crm.get_lead("lead-test-006")

    with pytest.raises(
        ValueError,
        match="CRM lead run_id does not match",
    ):
        mock_crm.update_lead_after_approval(
            "lead-test-006",
            approved_run_id,
            "CONTACTED",
            "Send an outreach email.",
        )

    saved = mock_crm.get_lead("lead-test-006")

    assert saved.status == "NEW"
    assert saved.next_action is None
    assert saved.updated_at == original.updated_at



def test_invalid_crm_status(tmp_path, monkeypatch):
    """Invalid CRM statuses must not modify saved data."""

    from pydantic import ValidationError

    monkeypatch.setattr(
        mock_crm, "CRM_DIR", tmp_path / "crm"
    )
    monkeypatch.setattr(
        approval_manager, "APPROVALS_DIR", tmp_path / "approvals"
    )

    run_id = "test-crm-invalid-status"

    approval_manager.create_pending_review(
        run_id, "Test Company"
    )
    approval_manager.submit_review(
        run_id,
        "Test Reviewer",
        "APPROVED",
        "Approved for validation testing.",
    )

    mock_crm.save_lead(
        CRMLead(
            lead_id="lead-test-invalid",
            company_name="Test Company",
            run_id=run_id,
        )
    )

    original = mock_crm.get_lead("lead-test-invalid")

    with pytest.raises(ValidationError):
        mock_crm.update_lead_after_approval(
            "lead-test-invalid",
            run_id,
            "INVALID_STATUS",
            "Send an email.",
        )

    saved = mock_crm.get_lead("lead-test-invalid")

    assert saved.status == "NEW"
    assert saved.next_action is None
    assert saved.updated_at == original.updated_at
