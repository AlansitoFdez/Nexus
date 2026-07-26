"""Tests for escalation_node, mocking the two MCP tool calls."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.agents.nodes.escalation_node import escalation_node


@pytest.mark.asyncio
async def test_escalation_node_marks_ticket_as_escalated():
    mock_client_instance = AsyncMock()

    mock_context_manager = MagicMock()
    mock_context_manager.__aenter__ = AsyncMock(return_value=mock_client_instance)
    mock_context_manager.__aexit__ = AsyncMock(return_value=False)

    with patch("app.agents.nodes.escalation_node.Client", return_value=mock_context_manager):
        state = {"ticket_id": 1, "diagnosis": "Facturación duplicada", "urgency": "high"}
        result = await escalation_node(state)

    assert result["escalated"] is True
    assert result["node_history"] == ["escalation"]
    assert mock_client_instance.call_tool.call_count == 2