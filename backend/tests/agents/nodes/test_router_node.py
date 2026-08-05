"""Tests for router_node — decides which specialists analyze the code."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.agents.nodes.router_node import router_node
from app.agents.schemas import RouterDecision


@pytest.mark.asyncio
async def test_router_node_selects_agents_from_llm_decision():
    state = {"review_request": "revisa seguridad y rendimiento"}

    mock_llm = MagicMock()
    mock_structured = MagicMock()
    mock_structured.ainvoke = AsyncMock(
        return_value=RouterDecision(agents_to_run=["security", "performance"], reasoning="pidió ambos explícitamente")
    )
    mock_llm.with_structured_output.return_value = mock_structured

    with patch("app.agents.nodes.router_node.ChatGroq", return_value=mock_llm):
        result = await router_node(state)

    assert result["agents_to_run"] == ["security", "performance"]
    assert result["node_history"] == ["router"]


@pytest.mark.asyncio
async def test_router_node_selects_all_agents_for_generic_request():
    state = {"review_request": "revisa el código"}

    mock_llm = MagicMock()
    mock_structured = MagicMock()
    mock_structured.ainvoke = AsyncMock(
        return_value=RouterDecision(
            agents_to_run=["security", "performance", "design_patterns", "best_practices"],
            reasoning="petición genérica, se activan todos",
        )
    )
    mock_llm.with_structured_output.return_value = mock_structured

    with patch("app.agents.nodes.router_node.ChatGroq", return_value=mock_llm):
        result = await router_node(state)

    assert len(result["agents_to_run"]) == 4


@pytest.mark.asyncio
async def test_router_node_returns_error_when_llm_call_fails():
    state = {"review_request": "revisa seguridad"}

    mock_llm = MagicMock()
    mock_structured = MagicMock()
    mock_structured.ainvoke = AsyncMock(side_effect=Exception("groq unavailable"))
    mock_llm.with_structured_output.return_value = mock_structured

    with patch("app.agents.nodes.router_node.ChatGroq", return_value=mock_llm):
        result = await router_node(state)

    assert "error" in result
    # The raw exception must not reach state["error"] (Fase 3 review,
    # 3.4) — it's forwarded verbatim to the browser over WebSocket.
    assert "groq unavailable" not in result["error"]
    assert result["node_history"] == ["router"]
