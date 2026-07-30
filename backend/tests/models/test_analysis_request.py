"""Tests for the AnalysisRequest model's post_to_pr default."""

from app.models.analysis_request import AnalysisRequest


def test_post_to_pr_defaults_to_false(db_session):
    request = AnalysisRequest(source_type="pasted_code", pasted_code="x", review_request="y")
    db_session.add(request)
    db_session.commit()
    db_session.refresh(request)

    assert request.post_to_pr is False