"""Tests for the Finding model's severity CheckConstraint."""

import pytest
from sqlalchemy.exc import IntegrityError

from app.models.analysis_request import AnalysisRequest
from app.models.finding import Finding


def test_invalid_severity_violates_check_constraint(db_session):
    """ck_findings_valid_severity (Fase 4.2 review) — writing directly
    via the ORM, bypassing FindingCreate's Literal, to prove the
    guarantee lives at the database level too. Without this, a garbage
    severity wouldn't fail loudly: synthesizer_node's
    SEVERITY_ORDER.get(severity, 99) would just silently sort it last."""
    analysis_request = AnalysisRequest(
        source_type="pasted_code", pasted_code="def foo(): pass", review_request="revisa seguridad"
    )
    db_session.add(analysis_request)
    db_session.commit()

    finding = Finding(
        analysis_request_id=analysis_request.id,
        specialist="security",
        severity="not_a_real_severity",
        description="algo",
    )
    db_session.add(finding)

    with pytest.raises(IntegrityError):
        db_session.commit()
