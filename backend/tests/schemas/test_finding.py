"""Tests for FindingCreate — the write-path schema graph nodes use via
FindingRepository (Fase 4.2 review: specialist/severity became Literals
here, matching SpecialistFinding's own severity Literal in
agents/schemas.py)."""

import pytest
from pydantic import ValidationError

from app.schemas.finding import FindingCreate


def test_finding_create_accepts_valid_specialist_and_severity():
    finding = FindingCreate(
        analysis_request_id=1, specialist="security", severity="high", description="inyección SQL"
    )
    assert finding.specialist == "security"
    assert finding.severity == "high"


def test_finding_create_rejects_invalid_specialist():
    with pytest.raises(ValidationError):
        FindingCreate(analysis_request_id=1, specialist="nonexistent", severity="high", description="x")


def test_finding_create_rejects_invalid_severity():
    with pytest.raises(ValidationError):
        FindingCreate(analysis_request_id=1, specialist="security", severity="catastrophic", description="x")
