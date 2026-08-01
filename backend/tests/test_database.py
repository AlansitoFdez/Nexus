"""Tests for the database engine and session configuration."""

from app.models.analysis_request import AnalysisRequest


def test_can_create_and_query_an_analysis_request(db_session):
    """An AnalysisRequest created through the session should be retrievable afterwards."""
    analysis_request = AnalysisRequest(
        source_type="pasted_code", pasted_code="def foo(): pass", review_request="revisa seguridad"
    )
    db_session.add(analysis_request)
    db_session.commit()

    result = db_session.query(AnalysisRequest).filter(
        AnalysisRequest.review_request == "revisa seguridad"
    ).first()

    assert result is not None
    assert result.id is not None
    assert result.status == "pending"