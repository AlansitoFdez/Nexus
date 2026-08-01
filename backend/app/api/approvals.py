"""REST endpoints for approval creation and retrieval.

Approving or rejecting a pending approval is not implemented here;
that logic belongs to the human-in-the-loop graph node (Fase 2.10).
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.repositories.approval_repository import ApprovalRepository
from app.repositories.analysis_request_repository import AnalysisRequestRepository, AnalysisRequestNotFoundError
from app.schemas.approval import ApprovalCreate, ApprovalResponse

router = APIRouter(prefix="/approvals", tags=["approvals"])


@router.post("/", response_model=ApprovalResponse, status_code=201)
def create_approval(data: ApprovalCreate, db: Session = Depends(get_db)):
    """Creates a new approval request for an analysis request."""
    analysis_request_repository = AnalysisRequestRepository(db)
    repo = ApprovalRepository(db, analysis_request_repository)
    try:
        return repo.create(data)
    except AnalysisRequestNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"AnalysisRequest {data.analysis_request_id} not found",
        )


@router.get("/{approval_id}", response_model=ApprovalResponse)
def get_approval(approval_id: int, db: Session = Depends(get_db)):
    """Retrieves a single approval by its ID, or 404 if it doesn't exist."""
    repo = ApprovalRepository(db, AnalysisRequestRepository(db))
    approval = repo.get_by_id(approval_id)

    if approval is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Approval not found")

    return approval


@router.get("/", response_model=list[ApprovalResponse])
def list_approvals(db: Session = Depends(get_db)):
    """Retrieves all approvals."""
    repo = ApprovalRepository(db, AnalysisRequestRepository(db))
    return repo.get_all()