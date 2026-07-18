"""REST endpoints for approval creation and retrieval.

Approving or rejecting a pending approval is not implemented here;
that logic belongs to the human-in-the-loop graph node (phase 2.7).
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.repositories.approval_repository import ApprovalRepository, TicketNotFoundError
from app.schemas.approval import ApprovalCreate, ApprovalResponse

router = APIRouter(prefix="/approvals", tags=["approvals"])


@router.post("/", response_model=ApprovalResponse, status_code=201)
def create_approval(data: ApprovalCreate, db: Session = Depends(get_db)):
    """Creates a new approval request for a ticket."""
    repo = ApprovalRepository(db)
    try:
        return repo.create(data)
    except TicketNotFoundError:
        raise HTTPException(status_code=404, detail=f"Ticket {data.ticket_id} not found")


@router.get("/{approval_id}", response_model=ApprovalResponse)
def get_approval(approval_id: int, db: Session = Depends(get_db)):
    """Retrieves a single approval by its ID, or 404 if it doesn't exist."""
    repo = ApprovalRepository(db)
    approval = repo.get_by_id(approval_id)

    if approval is None:
        raise HTTPException(status_code=404, detail="Approval not found")

    return approval


@router.get("/", response_model=list[ApprovalResponse])
def list_approvals(db: Session = Depends(get_db)):
    """Retrieves all approvals."""
    repo = ApprovalRepository(db)
    return repo.get_all()