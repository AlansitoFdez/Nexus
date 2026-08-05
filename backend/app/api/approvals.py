"""REST endpoints for approval creation, retrieval and decision.

Deciding a pending approval (POST /{id}/decision) does not update the
Approval row itself here — that write happens inside human_approval_node
once the graph actually wakes up from interrupt() (Fase 2.10). This
endpoint's only job is finding which paused thread the decision belongs
to and handing it off via resume_analysis(); it returns the approval as
it stands right now (still "pending"), before the resume has run.
"""

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.agents.runner import resume_analysis
from app.database import get_db
from app.repositories.analysis_request_repository import (
    AnalysisRequestNotFoundError,
    AnalysisRequestRepository,
)
from app.repositories.approval_repository import ApprovalRepository
from app.schemas.approval import ApprovalCreate, ApprovalDecision, ApprovalResponse

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
def list_approvals(analysis_request_id: int | None = None, db: Session = Depends(get_db)):
    """Retrieves all approvals, or only the ones for a single analysis
    request when analysis_request_id is given.

    The filtered form exists for the dashboard: if a user reloads the
    page after human_approval_node already paused the graph but before
    they decide, the live "approval_required" WebSocket event that would
    normally carry the approval_id is gone — this is how the frontend
    recovers it instead.
    """
    repo = ApprovalRepository(db, AnalysisRequestRepository(db))
    if analysis_request_id is not None:
        return repo.get_by_analysis_request_id(analysis_request_id)
    return repo.get_all()


@router.post("/{approval_id}/decision", response_model=ApprovalResponse)
def decide_approval(
    approval_id: int,
    data: ApprovalDecision,
    background_tasks: BackgroundTasks,
    request: Request,
    db: Session = Depends(get_db),
):
    """Submits a human decision for a pending approval and resumes the
    paused graph in the background.

    Rejects deciding an approval that's already claimed or already
    decided (409). The claim itself (ApprovalRepository.claim_pending)
    is what makes this safe against two concurrent decisions on the
    same approval_id: reading approval.status here and then acting on
    it are two separate moments — resuming an already-resumed thread
    has no interrupt() left waiting for it, so without an atomic claim,
    both requests could read "pending" before either had written
    anything, and both would schedule a resume.
    """
    repo = ApprovalRepository(db, AnalysisRequestRepository(db))
    approval = repo.get_by_id(approval_id)

    if approval is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Approval not found")

    if not repo.claim_pending(approval_id):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Approval {approval_id} was already decided or is already being decided",
        )

    background_tasks.add_task(
        resume_analysis, request.app.state.graph, approval.analysis_request_id, data.decision
    )

    return approval
