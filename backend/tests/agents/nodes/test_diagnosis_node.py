"""Tests for diagnosis_node, mocking both the MCP client and the LLM call."""

from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.agents.nodes.diagnosis_node import diagnosis_node
from app.agents.schemas import DiagnosisOutput


def _make_mock_client(call_tool_return):
    mock_client_instance = AsyncMock()
    mock_client_instance.call_tool.return_value = call_tool_return

    mock_context_manager = MagicMock()
    mock_context_manager.__aenter__ = AsyncMock(return_value=mock_client_instance)
    mock_context_manager.__aexit__ = AsyncMock(return_value=False)
    return mock_context_manager


@pytest.mark.asyncio
async def test_diagnosis_node_combines_sources_into_diagnosis():
    """A successful run should merge probable_cause + proposed_solution."""
    fake_tickets = SimpleNamespace(data=[{"id": 42, "solution": "restart service"}])
    fake_diagnosis = DiagnosisOutput(
        probable_cause="Session token expired",
        proposed_solution="Ask the user to log in again",
        confidence=0.85,
        actions_required=None,
    )

    with patch(
        "app.agents.nodes.diagnosis_node.Client", return_value=_make_mock_client(fake_tickets)
    ), patch("app.agents.nodes.diagnosis_node.ChatGroq") as MockChatGroq:
        mock_structured_llm = MockChatGroq.return_value.with_structured_output.return_value
        mock_structured_llm.ainvoke = AsyncMock(return_value=fake_diagnosis)

        state = {
            "cleaned_text": "no puedo iniciar sesión",
            "classification": "bug",
            "kb_documents": [],
        }
        result = await diagnosis_node(state)

    assert "Session token expired" in result["diagnosis"]
    assert "Ask the user to log in again" in result["diagnosis"]
    assert result["pending_actions"] == []
    assert result["diagnosis_confidence"] == 0.85