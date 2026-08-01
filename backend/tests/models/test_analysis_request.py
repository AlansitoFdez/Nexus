"""Tests for the AnalysisRequest model's post_to_pr default."""

from app.models.analysis_request import AnalysisRequest


def test_post_to_pr_defaults_to_false(db_session):
    request = AnalysisRequest(source_type="pasted_code", pasted_code="x", review_request="y")
    db_session.add(request)
    db_session.commit()
    db_session.refresh(request)

    assert request.post_to_pr is False


def test_analysis_request_approvals_relationship_returns_related_approvals(db_session):
    from app.models.approval import Approval

    request = AnalysisRequest(source_type="pasted_code", pasted_code="x", review_request="y")
    db_session.add(request)
    db_session.commit()

    approval = Approval(analysis_request_id=request.id, proposed_action="publicar en el PR")
    db_session.add(approval)
    db_session.commit()
    db_session.refresh(request)

    assert len(request.approvals) == 1
    assert request.approvals[0].proposed_action == "publicar en el PR"
    assert request.approvals[0].analysis_request.id == request.id