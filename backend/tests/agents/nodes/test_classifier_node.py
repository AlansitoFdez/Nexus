"""Tests for classifier_node, mocking the Groq LLM call."""

from unittest.mock import AsyncMock, patch

import pytest

from app.agents.nodes.classifier_node import classifier_node
from app.agents.schemas import TicketClassification


@pytest.mark.asyncio
async def test_classifier_node_returns_classification_on_success():
    """A successful LLM call should populate classification, urgency and confidence."""
    fake_result = TicketClassification(category="bug", urgency="high", confidence=0.9)

    with patch("app.agents.nodes.classifier_node.ChatGroq") as MockChatGroq:
        mock_structured_llm = MockChatGroq.return_value.with_structured_output.return_value
        mock_structured_llm.ainvoke = AsyncMock(return_value=fake_result)

        state = {"cleaned_text": "no puedo iniciar sesión"}
        result = await classifier_node(state)

    assert result["classification"] == "bug"
    assert result["urgency"] == "high"
    assert result["confidence"] == 0.9
    assert result["node_history"] == ["classifier"]


@pytest.mark.asyncio
async def test_classifier_node_returns_error_on_llm_failure():
    """A failed LLM call should populate error instead of raising."""
    with patch("app.agents.nodes.classifier_node.ChatGroq") as MockChatGroq:
        mock_structured_llm = MockChatGroq.return_value.with_structured_output.return_value
        mock_structured_llm.ainvoke = AsyncMock(side_effect=Exception("rate limit exceeded"))

        state = {"cleaned_text": "no puedo iniciar sesión"}
        result = await classifier_node(state)

    assert "rate limit exceeded" in result["error"]
    assert result["node_history"] == ["classifier"]