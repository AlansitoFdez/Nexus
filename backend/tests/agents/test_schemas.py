"""Tests for agent-internal Pydantic schemas (LLM structured output)."""

import pytest
from pydantic import ValidationError

from app.agents.schemas import RouterDecision
from app.agents.schemas import SpecialistFinding, SpecialistOutput


def test_router_decision_accepts_valid_agents():
    decision = RouterDecision(agents_to_run=["security", "performance"], reasoning="pidió ambos")
    assert decision.agents_to_run == ["security", "performance"]


def test_router_decision_rejects_invalid_agent_name():
    with pytest.raises(ValidationError):
        RouterDecision(agents_to_run=["nonexistent_agent"], reasoning="motivo")


def test_specialist_finding_accepts_valid_severity():
    finding = SpecialistFinding(severity="high", description="inyección SQL")
    assert finding.severity == "high"
    assert finding.file_path is None


def test_specialist_finding_rejects_invalid_severity():
    with pytest.raises(ValidationError):
        SpecialistFinding(severity="catastrophic", description="algo")


def test_specialist_output_accepts_empty_findings_list():
    output = SpecialistOutput(findings=[])
    assert output.findings == []