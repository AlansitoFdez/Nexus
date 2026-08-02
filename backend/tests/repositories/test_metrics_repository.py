"""Tests for MetricsRepository's aggregation queries."""

from app.repositories.analysis_request_repository import AnalysisRequestRepository
from app.repositories.finding_repository import FindingRepository
from app.repositories.metrics_repository import MetricsRepository
from app.schemas.analysis_request import AnalysisRequestCreate, AnalysisRequestUpdate
from app.schemas.finding import FindingCreate


def test_count_by_status_groups_correctly(db_session):
    analysis_repo = AnalysisRequestRepository(db_session)
    metrics_repo = MetricsRepository(db_session)

    request_a = analysis_repo.create(AnalysisRequestCreate(
        source_type="pasted_code", pasted_code="def a(): pass", review_request="revisa seguridad"
    ))
    analysis_repo.create(AnalysisRequestCreate(
        source_type="pasted_code", pasted_code="def b(): pass", review_request="revisa rendimiento"
    ))
    analysis_repo.update(request_a.id, AnalysisRequestUpdate(status="completed"))

    result = metrics_repo.count_by_status()

    assert result == {"pending": 1, "completed": 1}


def test_count_findings_by_specialist_and_severity(db_session):
    analysis_repo = AnalysisRequestRepository(db_session)
    finding_repo = FindingRepository(db_session, analysis_repo)
    metrics_repo = MetricsRepository(db_session)

    request = analysis_repo.create(AnalysisRequestCreate(
        source_type="pasted_code", pasted_code="def a(): pass", review_request="revisa todo"
    ))
    finding_repo.create(FindingCreate(
        analysis_request_id=request.id, specialist="security", severity="high", description="SQL injection"
    ))
    finding_repo.create(FindingCreate(
        analysis_request_id=request.id, specialist="security", severity="low", description="Missing docstring"
    ))
    finding_repo.create(FindingCreate(
        analysis_request_id=request.id, specialist="performance", severity="medium", description="N+1 query"
    ))

    assert metrics_repo.count_findings_by_specialist() == {"security": 2, "performance": 1}
    assert metrics_repo.count_findings_by_severity() == {"high": 1, "low": 1, "medium": 1}


def test_count_pr_comments_posted_only_counts_rows_with_a_url(db_session):
    analysis_repo = AnalysisRequestRepository(db_session)
    metrics_repo = MetricsRepository(db_session)

    with_comment = analysis_repo.create(AnalysisRequestCreate(
        source_type="github_repo", repo_url="https://github.com/alan/nexus",
        review_request="revisa seguridad", post_to_pr=True, pr_number=1,
    ))
    analysis_repo.create(AnalysisRequestCreate(
        source_type="pasted_code", pasted_code="def a(): pass", review_request="revisa seguridad"
    ))
    analysis_repo.update(with_comment.id, AnalysisRequestUpdate(
        pr_comment_url="https://github.com/alan/nexus/pull/1#issuecomment-1"
    ))

    assert metrics_repo.count_pr_comments_posted() == 1


def test_average_analysis_seconds_returns_none_when_no_terminal_requests(db_session):
    analysis_repo = AnalysisRequestRepository(db_session)
    metrics_repo = MetricsRepository(db_session)

    analysis_repo.create(AnalysisRequestCreate(
        source_type="pasted_code", pasted_code="def a(): pass", review_request="revisa seguridad"
    ))

    assert metrics_repo.average_analysis_seconds() is None


def test_average_analysis_seconds_only_considers_terminal_requests(db_session):
    analysis_repo = AnalysisRequestRepository(db_session)
    metrics_repo = MetricsRepository(db_session)

    request = analysis_repo.create(AnalysisRequestCreate(
        source_type="pasted_code", pasted_code="def a(): pass", review_request="revisa seguridad"
    ))
    analysis_repo.create(AnalysisRequestCreate(
        source_type="pasted_code", pasted_code="def b(): pass", review_request="revisa rendimiento"
    ))
    analysis_repo.update(request.id, AnalysisRequestUpdate(status="completed"))

    result = metrics_repo.average_analysis_seconds()

    assert result is not None
    assert result >= 0
