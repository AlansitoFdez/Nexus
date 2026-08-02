"""Repository for cross-cutting metrics (Fase 4 dashboard).

Deliberately its own repository rather than extra methods bolted onto
AnalysisRequestRepository/FindingRepository: those two each already have
a clear single responsibility (persistence of one entity at a time);
aggregating across both is a different job, not a variation of either.

Aggregation happens in SQL (func.count/group_by) rather than loading
every row into Python and counting there — the difference doesn't
matter at this project's scale, but it's the right default so this
doesn't become an accidental full-table scan once there are thousands
of rows instead of dozens.
"""

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.analysis_request import AnalysisRequest
from app.models.finding import Finding

TERMINAL_STATUSES = ("completed", "completed_with_errors", "failed")


class MetricsRepository:
    def __init__(self, db: Session):
        self.db = db

    def count_by_status(self) -> dict[str, int]:
        """Counts analysis requests grouped by their current status."""
        rows = (
            self.db.query(AnalysisRequest.status, func.count(AnalysisRequest.id))
            .group_by(AnalysisRequest.status)
            .all()
        )
        return {status: count for status, count in rows}

    def count_findings_by_specialist(self) -> dict[str, int]:
        """Counts findings grouped by which specialist produced them."""
        rows = (
            self.db.query(Finding.specialist, func.count(Finding.id))
            .group_by(Finding.specialist)
            .all()
        )
        return {specialist: count for specialist, count in rows}

    def count_findings_by_severity(self) -> dict[str, int]:
        """Counts findings grouped by severity."""
        rows = (
            self.db.query(Finding.severity, func.count(Finding.id))
            .group_by(Finding.severity)
            .all()
        )
        return {severity: count for severity, count in rows}

    def count_pr_comments_posted(self) -> int:
        """Counts analysis requests that actually got a PR comment posted.

        pr_comment_url is only ever set by post_comment_node on a
        successful post (Fase 4) — never on failure, never when
        post_to_pr was false — so its mere presence is the signal.
        """
        return (
            self.db.query(func.count(AnalysisRequest.id))
            .filter(AnalysisRequest.pr_comment_url.isnot(None))
            .scalar()
        )

    def average_analysis_seconds(self) -> float | None:
        """Average wall-clock time from created_at to updated_at, over
        requests that reached a terminal status.

        A proxy, not an exact measurement: there's no dedicated
        completed_at column, so this leans on updated_at's onupdate
        trigger instead, on the assumption that nothing touches the row
        again after synthesizer_node/failure_node set its terminal
        status — true today, not enforced by anything. Returns None
        instead of 0 when there's no terminal data yet, since "0 seconds
        average" would misleadingly read as "instant," not "no data."
        """
        rows = (
            self.db.query(AnalysisRequest.created_at, AnalysisRequest.updated_at)
            .filter(AnalysisRequest.status.in_(TERMINAL_STATUSES))
            .filter(AnalysisRequest.updated_at.isnot(None))
            .all()
        )
        if not rows:
            return None

        durations = [(updated_at - created_at).total_seconds() for created_at, updated_at in rows]
        return sum(durations) / len(durations)
