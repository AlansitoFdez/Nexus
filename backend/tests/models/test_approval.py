"""Tests for the Approval model's default status behavior."""

from app.models.analysis_request import AnalysisRequest
from app.models.approval import Approval


def test_approval_defaults_to_pending_status(db_session):
    analysis_request = AnalysisRequest(
        source_type="pasted_code", pasted_code="def foo(): pass", review_request="revisa seguridad"
    )
    db_session.add(analysis_request)
    db_session.commit()

    approval = Approval(analysis_request_id=analysis_request.id, proposed_action="publicar comentario en el PR")
    db_session.add(approval)
    db_session.commit()
    db_session.refresh(approval)

    assert approval.status == "pending"
    assert approval.decided_at is None