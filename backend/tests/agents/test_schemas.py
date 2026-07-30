"""Tests for agent-internal Pydantic schemas (LLM structured output)."""

import pytest
from pydantic import ValidationError

from app.agents.schemas import RouterDecision


def test_router_decision_accepts_valid_agents():
    decision = RouterDecision(agents_to_run=["security", "performance"], reasoning="pidió ambos")
    assert decision.agents_to_run == ["security", "performance"]


def test_router_decision_rejects_invalid_agent_name():
    with pytest.raises(ValidationError):
        RouterDecision(agents_to_run=["nonexistent_agent"], reasoning="motivo")