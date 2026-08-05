"""Repository for Approval database operations."""

from datetime import datetime, timezone

from sqlalchemy import func, update
from sqlalchemy.orm import Session

from app.models.approval import Approval
from app.repositories.analysis_request_repository import (
    AnalysisRequestNotFoundError,
    AnalysisRequestRepository,
)
from app.schemas.approval import ApprovalCreate, ApprovalUpdate


class ApprovalNotFoundError(Exception):
    """Raised when an operation targets an Approval that doesn't exist."""


class ApprovalRepository:
    """Handles persistence operations for Approval entities."""

    def __init__(self, db: Session, analysis_request_repo: AnalysisRequestRepository):
        self.db = db
        self.analysis_request_repo = analysis_request_repo

    def create(self, data: ApprovalCreate) -> Approval:
        """Creates a new Approval for an existing AnalysisRequest.

        Raises:
            AnalysisRequestNotFoundError: propagated from
                AnalysisRequestRepository.get_by_id if analysis_request_id
                doesn't match any existing request.
        """
        analysis_request = self.analysis_request_repo.get_by_id(data.analysis_request_id)
        if analysis_request is None:
            raise AnalysisRequestNotFoundError(
                f"AnalysisRequest {data.analysis_request_id} does not exist"
            )

        approval = Approval(**data.model_dump())
        self.db.add(approval)
        self.db.commit()
        self.db.refresh(approval)
        return approval

    def get_by_id(self, approval_id: int) -> Approval | None:
        """Retrieves an Approval by its ID, or None if it doesn't exist."""
        return self.db.query(Approval).filter(Approval.id == approval_id).first()

    def get_all(self) -> list[Approval]:
        """Retrieves all approvals."""
        return self.db.query(Approval).all()

    def get_by_analysis_request_id(self, analysis_request_id: int) -> list[Approval]:
        """Retrieves every Approval tied to one AnalysisRequest.

        In practice this returns at most one row: human_approval_node
        creates exactly one Approval per graph run, and each
        AnalysisRequest maps to exactly one run. Still returns a list,
        not Approval | None, because nothing at this layer enforces that
        cardinality — it's just how the current graph happens to behave,
        not a database constraint.
        """
        return (
            self.db.query(Approval)
            .filter(Approval.analysis_request_id == analysis_request_id)
            .all()
        )

    def claim_pending(self, approval_id: int) -> bool:
        """Atomically marks a pending approval as claimed, so a second
        concurrent request against the same approval_id can't also pass
        the "is this still decidable" check.

        A plain read-then-check (approval.status == "pending") leaves a
        real gap: the actual decision status is only written later, by
        human_approval_node, once the graph wakes up and resumes — not
        by this call — so two requests could both read "pending" before
        either had written anything. This single UPDATE ... WHERE
        status='pending' AND claimed_at IS NULL closes that gap: only
        one concurrent caller can be the one whose WHERE clause still
        matches by the time its UPDATE actually runs.

        Deliberately doesn't touch status itself — claimed_at is a
        narrower concept ("a decision is already in flight"), not the
        decision's outcome, which stays human_approval_node's exclusive
        responsibility.

        Returns:
            True if this call is the one that won the claim, False if
            the approval was already claimed or already decided.
        """
        result = self.db.execute(
            update(Approval)
            .where(
                Approval.id == approval_id,
                Approval.status == "pending",
                Approval.claimed_at.is_(None),
            )
            .values(claimed_at=func.now())
        )
        self.db.commit()
        return result.rowcount > 0

    def update(self, approval_id: int, data: ApprovalUpdate) -> Approval:
        """Applies a decision (approved/rejected) to a pending approval.

        Raises:
            ApprovalNotFoundError: if approval_id doesn't match any
                existing approval.
        """
        approval = self.get_by_id(approval_id)
        if approval is None:
            raise ApprovalNotFoundError(f"Approval {approval_id} does not exist")

        approval.status = data.status
        approval.decided_at = datetime.now(timezone.utc)
        self.db.commit()
        self.db.refresh(approval)
        return approval
