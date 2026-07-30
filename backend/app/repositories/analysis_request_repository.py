"""Repository for AnalysisRequest database operations."""

from sqlalchemy.orm import Session

from app.models.analysis_request import AnalysisRequest
from app.schemas.analysis_request import AnalysisRequestCreate, AnalysisRequestUpdate


class AnalysisRequestNotFoundError(Exception):
    """Raised when an operation targets an AnalysisRequest that doesn't exist.

    Only raised by methods that act on an existing request (e.g. update);
    methods that search (get_by_id) return None instead, per the
    project's established domain-error convention.
    """


class AnalysisRequestRepository:
    """Handles persistence operations for AnalysisRequest entities."""

    def __init__(self, db: Session):
        self.db = db

    def create(self, data: AnalysisRequestCreate) -> AnalysisRequest:
        """Creates and persists a new AnalysisRequest from validated input data."""
        analysis_request = AnalysisRequest(**data.model_dump())
        self.db.add(analysis_request)
        self.db.commit()
        self.db.refresh(analysis_request)
        return analysis_request

    def get_by_id(self, analysis_request_id: int) -> AnalysisRequest | None:
        """Retrieves an AnalysisRequest by its ID, or None if it doesn't exist."""
        return self.db.query(AnalysisRequest).filter(AnalysisRequest.id == analysis_request_id).first()

    def get_all(self) -> list[AnalysisRequest]:
        """Retrieves all analysis requests."""
        return self.db.query(AnalysisRequest).all()

    def update(self, analysis_request_id: int, data: AnalysisRequestUpdate) -> AnalysisRequest:
        """Applies a partial update to an existing analysis request.

        Only fields explicitly provided in `data` are modified; omitted
        fields are left untouched.

        Raises:
            AnalysisRequestNotFoundError: if analysis_request_id doesn't
                match any existing request — update() acts on a target,
                so a missing target is a domain error, not a None result.
        """
        analysis_request = self.get_by_id(analysis_request_id)
        if analysis_request is None:
            raise AnalysisRequestNotFoundError(f"AnalysisRequest {analysis_request_id} does not exist")

        update_fields = data.model_dump(exclude_unset=True)
        for field, value in update_fields.items():
            setattr(analysis_request, field, value)

        self.db.commit()
        self.db.refresh(analysis_request)
        return analysis_request