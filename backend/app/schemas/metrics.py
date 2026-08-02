"""Pydantic schema for the Fase 4 metrics endpoint's response."""

from pydantic import BaseModel


class MetricsResponse(BaseModel):
    """Aggregated stats for the dashboard: how many requests in each
    status, findings broken down by specialist and severity, how many
    PR comments actually got posted, and average analysis time.
    """

    total_analysis_requests: int
    by_status: dict[str, int]
    findings_by_specialist: dict[str, int]
    findings_by_severity: dict[str, int]
    pr_comments_posted: int
    average_analysis_seconds: float | None
