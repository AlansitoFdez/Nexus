"""Tests for FindingRepository database operations."""

import pytest

from app.repositories.analysis_request_repository import AnalysisRequestRepository, AnalysisRequestNotFoundError
from app.repositories.finding_repository import FindingRepository
from app.schemas.analysis_request import AnalysisRequestCreate
from app.schemas.finding import FindingCreate


def test_create_persists_a_new_finding_for_an_existing_request(db_session):
    """create() should save a new finding when the analysis request exists."""
    analysis_repo = AnalysisRequestRepository(db_session)
    request = analysis_repo.create(AnalysisRequestCreate(source_type="pasted_code", pasted_code="a", review_request="x"))

    finding_repo = FindingRepository(db_session, analysis_repo)
    finding = finding_repo.create(FindingCreate(
        analysis_request_id=request.id,
        specialist="security",
        severity="high",
        description="SQL injection risk",
    ))

    assert finding.id is not None
    assert finding.analysis_request_id == request.id


def test_create_raises_error_when_analysis_request_does_not_exist(db_session):
    """create() should raise AnalysisRequestNotFoundError when analysis_request_id doesn't exist."""
    analysis_repo = AnalysisRequestRepository(db_session)
    finding_repo = FindingRepository(db_session, analysis_repo)

    with pytest.raises(AnalysisRequestNotFoundError):
        finding_repo.create(FindingCreate(
            analysis_request_id=999,
            specialist="security",
            severity="high",
            description="SQL injection risk",
        ))


def test_get_by_analysis_request_id_returns_only_matching_findings(db_session):
    """get_by_analysis_request_id() should return only findings for the given request."""
    analysis_repo = AnalysisRequestRepository(db_session)
    request_a = analysis_repo.create(AnalysisRequestCreate(source_type="pasted_code", pasted_code="a", review_request="x"))
    request_b = analysis_repo.create(AnalysisRequestCreate(source_type="pasted_code", pasted_code="b", review_request="y"))

    finding_repo = FindingRepository(db_session, analysis_repo)
    finding_repo.create(FindingCreate(analysis_request_id=request_a.id, specialist="security", severity="high", description="issue A"))
    finding_repo.create(FindingCreate(analysis_request_id=request_b.id, specialist="performance", severity="low", description="issue B"))

    results = finding_repo.get_by_analysis_request_id(request_a.id)

    assert len(results) == 1
    assert results[0].description == "issue A"