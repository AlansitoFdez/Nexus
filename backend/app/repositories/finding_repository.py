"""Repository for Finding database operations."""

from sqlalchemy.orm import Session

from app.models.finding import Finding
from app.repositories.analysis_request_repository import (
    AnalysisRequestNotFoundError,
    AnalysisRequestRepository,
)
from app.schemas.finding import FindingCreate


class FindingRepository:
    """Handles persistence operations for Finding entities.

    Receives an AnalysisRequestRepository (Dependency Inversion, same
    pattern as ApprovalRepository/TicketRepository) to validate that a
    finding's analysis_request_id refers to a request that actually
    exists before persisting it.
    """

    def __init__(self, db: Session, analysis_request_repository: AnalysisRequestRepository):
        self.db = db
        self.analysis_request_repository = analysis_request_repository

    def create(self, data: FindingCreate) -> Finding:
        """Creates and persists a new finding for an existing analysis request.

        Raises:
            AnalysisRequestNotFoundError: if data.analysis_request_id
                doesn't match any existing request.
        """
        analysis_request = self.analysis_request_repository.get_by_id(data.analysis_request_id)
        if analysis_request is None:
            raise AnalysisRequestNotFoundError(
                f"AnalysisRequest {data.analysis_request_id} does not exist"
            )

        finding = Finding(**data.model_dump())
        self.db.add(finding)
        self.db.commit()
        self.db.refresh(finding)
        return finding

    def get_by_analysis_request_id(self, analysis_request_id: int) -> list[Finding]:
        """Retrieves all findings belonging to a given analysis request."""
        return (
            self.db.query(Finding)
            .filter(Finding.analysis_request_id == analysis_request_id)
            .all()
        )
