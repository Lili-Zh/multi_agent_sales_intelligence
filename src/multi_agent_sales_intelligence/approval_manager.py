from datetime import datetime, timezone

import json
import re
from pathlib import Path

from multi_agent_sales_intelligence.models import HumanReviewRecord


APPROVALS_DIR = Path("approvals")


def validate_run_id(run_id: str) -> str:
    """Validate a run ID before using it in a file path."""

    if not isinstance(run_id, str):
        raise ValueError("run_id must be a string.")

    if not re.fullmatch(r"[A-Za-z0-9_-]{1,100}", run_id):
        raise ValueError(
            "run_id must contain only letters, numbers, "
            "underscores, or hyphens (1-100 characters)."
        )

    return run_id


def create_pending_review(
    run_id: str,
    company_name: str,
) -> HumanReviewRecord:
    """Create and save a pending human review."""

    run_id = validate_run_id(run_id)

    if not company_name or not company_name.strip():
        raise ValueError("company_name cannot be empty.")

    APPROVALS_DIR.mkdir(parents=True, exist_ok=True)

    review_path = APPROVALS_DIR / f"{run_id}.json"

    if review_path.exists():
        raise FileExistsError(
            f"Review already exists for run_id: {run_id}"
        )

    review = HumanReviewRecord(
        run_id=run_id,
        company_name=company_name,
    )

    with review_path.open("x", encoding="utf-8") as file:
        json.dump(
            review.model_dump(),
            file,
            indent=2,
            ensure_ascii=False,
        )

    return review


def get_review(run_id: str) -> HumanReviewRecord:
    """Load an existing human review by run ID."""

      
    run_id = validate_run_id(run_id)

    review_path = APPROVALS_DIR / f"{run_id}.json"

    if not review_path.is_file():
        raise FileNotFoundError(
            f"No review found for run_id: {run_id}"
        )

    with review_path.open("r", encoding="utf-8") as file:
        data = json.load(file)

    return HumanReviewRecord.model_validate(data)


def submit_review(
    run_id: str,
    reviewer: str,
    decision: str,
    comment: str,
) -> HumanReviewRecord:
    """Submit a human review decision."""

    run_id = validate_run_id(run_id)

    if not reviewer or not reviewer.strip():
        raise ValueError("Reviewer is required.")

    if not comment or not comment.strip():
        raise ValueError("Review comment is required.")

    allowed_decisions = {
        "APPROVED",
        "REJECTED",
        "REVISION_REQUESTED",
    }

    if decision not in allowed_decisions:
        raise ValueError(
            f"Invalid review decision: {decision}"
        )

    review = get_review(run_id)

    if review.status != "PENDING":
        raise ValueError(
            f"Cannot review a record with status: {review.status}"
        )

    review.status = decision
    review.reviewer = reviewer.strip()
    review.review_comment = comment.strip()
    review.reviewed_at = datetime.now(
        timezone.utc
    ).isoformat()

    review_path = APPROVALS_DIR / f"{run_id}.json"

    with review_path.open("w", encoding="utf-8") as file:
        json.dump(
            review.model_dump(),
            file,
            indent=2,
            ensure_ascii=False,
        )

    return review


def require_approval(run_id: str) -> HumanReviewRecord:
    """Allow downstream actions only for approved reviews."""

    review = get_review(run_id)

    if review.status != "APPROVED":
        raise PermissionError(
            f"Sales action blocked: review status is {review.status}"
        )

    return review
