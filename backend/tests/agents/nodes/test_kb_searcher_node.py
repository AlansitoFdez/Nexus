"""Tests for kb_searcher_node, mocking the MCP client call."""

from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.agents.nodes.kb_searcher_node import kb_searcher_node


def _make_mock_client(call_tool_return):
    """Builds a mock that behaves like `async with Client(...) as client:`."""
    mock_client_instance = AsyncMock()
    mock_client_instance.call_tool.return_value = call_tool_return

    mock_context_manager = MagicMock()
    mock_context_manager.__aenter__ = AsyncMock(return_value=mock_client_instance)
    mock_context_manager.__aexit__ = AsyncMock(return_value=False)
    return mock_context_manager


@pytest.mark.asyncio
async def test_kb_searcher_node_stores_documents_returned_by_the_tool():
    """The node no longer filters by relevance — that now happens in the DB query."""
    fake_docs = SimpleNamespace(
        data=[{"id": 1, "title": "Reset password", "relevance_score": 0.06}]
    )

    with patch(
        "app.agents.nodes.kb_searcher_node.Client",
        return_value=_make_mock_client(fake_docs),
    ):
        state = {"cleaned_text": "no puedo iniciar sesión"}
        result = await kb_searcher_node(state)

    assert result["kb_documents"] == fake_docs.data
    assert result["node_history"] == ["kb_searcher"]


@pytest.mark.asyncio
async def test_kb_searcher_node_returns_error_on_mcp_failure():
    """A failed MCP call should populate error instead of raising."""
    mock_context_manager = MagicMock()
    mock_context_manager.__aenter__ = AsyncMock(side_effect=Exception("connection refused"))

    with patch("app.agents.nodes.kb_searcher_node.Client", return_value=mock_context_manager):
        state = {"cleaned_text": "no puedo iniciar sesión"}
        result = await kb_searcher_node(state)

    assert "connection refused" in result["error"]
    assert result["node_history"] == ["kb_searcher"]