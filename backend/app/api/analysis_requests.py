"""REST endpoints for analysis request creation and retrieval.

No PATCH endpoint here on purpose: AnalysisRequestUpdate exists for
graph nodes to use internally (entry_node/synthesizer_node/
post_comment_node/failure_node writing status, final_report and
pr_comment_url as the pipeline progresses) — it was never meant for
direct client-side use, and nothing in the frontend actually calls it
(confirmed by grep). Exposing it publicly let any client overwrite
status mid-run or forge pr_comment_url (the only source of the
"PRs comentados" metric) with a plain PATCH request, for zero real
benefit today. Same YAGNI criterion already applied to list_open_prs
(Fase 3.4) — reconstruct this the day there's a genuine client-safe use
case (e.g. cancelling a pending analysis), scoped to only what a client
should actually be allowed to touch.
"""

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.agents.runner import run_analysis
from app.database import get_db
from app.repositories.analysis_request_repository import AnalysisRequestRepository
from app.schemas.analysis_request import AnalysisRequestCreate, AnalysisRequestResponse

router = APIRouter(prefix="/analysis-requests", tags=["analysis-requests"])


@router.post("/", response_model=AnalysisRequestResponse, status_code=status.HTTP_201_CREATED)
def create_analysis_request(
    data: AnalysisRequestCreate,
    background_tasks: BackgroundTasks,
    request: Request,
    db: Session = Depends(get_db),
):
    """Creates a new code analysis request and starts its graph run in
    the background.

    The response carries the freshly created record; entry_node,
    router_node and the specialist fan-out all run afterwards via
    run_analysis(), so the client isn't left waiting on however long
    the full pipeline (LLM calls, GitHub reads) actually takes.
    """
    repo = AnalysisRequestRepository(db)
    analysis_request = repo.create(data)

    initial_state = {
        "analysis_request_id": analysis_request.id,
        "source_type": analysis_request.source_type,
        "repo_url": analysis_request.repo_url,
        "pasted_code": analysis_request.pasted_code,
        "review_request": analysis_request.review_request,
        "post_to_pr": analysis_request.post_to_pr,
        "pr_number": analysis_request.pr_number,
    }
    background_tasks.add_task(run_analysis, request.app.state.graph, initial_state)

    return analysis_request


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