"""REST endpoints for analysis request creation and retrieval."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.repositories.analysis_request_repository import (
    AnalysisRequestRepository,
    AnalysisRequestNotFoundError,
)
from app.schemas.analysis_request import AnalysisRequestCreate, AnalysisRequestResponse, AnalysisRequestUpdate

router = APIRouter(prefix="/analysis-requests", tags=["analysis-requests"])


@router.post("/", response_model=AnalysisRequestResponse, status_code=status.HTTP_201_CREATED)
def create_analysis_request(data: AnalysisRequestCreate, db: Session = Depends(get_db)):
    """Creates a new code analysis request."""
    repo = AnalysisRequestRepository(db)
    return repo.create(data)


@router.get("/{analysis_request_id}", response_model=AnalysisRequestResponse)
def get_analysis_request(analysis_request_id: int, db: Session = Depends(get_db)):
    """Retrieves a single analysis request by its ID, or 404 if it doesn't exist."""
    repo = AnalysisRequestRepository(db)
    analysis_request = repo.get_by_id(analysis_request_id)

    if analysis_request is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Analysis request not found")

    return analysis_request


@router.get("/", response_model=list[AnalysisRequestResponse])
def list_analysis_requests(db: Session = Depends(get_db)):
    """Retrieves all analysis requests."""
    repo = AnalysisRequestRepository(db)
    return repo.get_all()


@router.patch("/{analysis_request_id}", response_model=AnalysisRequestResponse)
def update_analysis_request(analysis_request_id: int, data: AnalysisRequestUpdate, db: Session = Depends(get_db)):
    """Partially updates an existing analysis request."""
    repo = AnalysisRequestRepository(db)
    try:
        return repo.update(analysis_request_id, data)
    except AnalysisRequestNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Analysis request not found")