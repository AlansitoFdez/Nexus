"""REST endpoint for the Fase 4 dashboard's aggregated metrics."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.repositories.metrics_repository import MetricsRepository
from app.schemas.metrics import MetricsResponse

router = APIRouter(prefix="/metrics", tags=["metrics"])


@router.get("/", response_model=MetricsResponse)
def get_metrics(db: Session = Depends(get_db)):
    """Returns a snapshot of aggregated stats across every analysis
    request and finding — a point-in-time read, not something that
    needs to live-update over WebSocket the way an in-progress run does.
    """
    repo = MetricsRepository(db)
    by_status = repo.count_by_status()

    return MetricsResponse(
        total_analysis_requests=sum(by_status.values()),
        by_status=by_status,
        findings_by_specialist=repo.count_findings_by_specialist(),
        findings_by_severity=repo.count_findings_by_severity(),
        pr_comments_posted=repo.count_pr_comments_posted(),
        average_analysis_seconds=repo.average_analysis_seconds(),
    )
