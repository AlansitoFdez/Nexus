"""Tests for the Approval model's default status behavior and its
status CheckConstraint."""

import pytest
from sqlalchemy.exc import IntegrityError

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


def test_invalid_status_violates_check_constraint(db_session):
    """ck_approvals_valid_status (Fase 4.2 review) — writing directly
    via the ORM, bypassing ApprovalUpdate's plain str, to prove the
    guarantee lives at the database level, not only wherever a caller
    happens to validate first."""
    analysis_request = AnalysisRequest(
        source_type="pasted_code", pasted_code="def foo(): pass", review_request="revisa seguridad"
    )
    db_session.add(analysis_request)
    db_session.commit()

    approval = Approval(
        analysis_request_id=analysis_request.id,
        proposed_action="publicar comentario en el PR",
        status="not_a_real_status",
    )
    db_session.add(approval)

    with pytest.raises(IntegrityError):
        db_session.commit()
