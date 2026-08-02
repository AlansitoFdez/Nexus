"""Repository for Approval database operations."""

from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.approval import Approval
from app.repositories.analysis_request_repository import AnalysisRequestRepository
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
            from app.repositories.analysis_request_repository import AnalysisRequestNotFoundError
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