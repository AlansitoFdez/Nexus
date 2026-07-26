"""Tests for response_node, mocking the Groq LLM call."""

from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

import pytest

from app.agents.nodes.response_node import response_node


@pytest.mark.asyncio
async def test_response_node_stores_llm_text_as_proposed_response():
    """The AIMessage's .content should be stored as-is, no structured output involved."""
    fake_message = SimpleNamespace(content="Aquí tienes los pasos para resolverlo...")

    with patch("app.agents.nodes.response_node.ChatGroq") as MockChatGroq:
        MockChatGroq.return_value.ainvoke = AsyncMock(return_value=fake_message)

        state = {
            "cleaned_text": "no puedo iniciar sesión",
            "diagnosis": "Token expirado",
            "kb_documents": [],
            "pending_actions": [],
        }
        result = await response_node(state)

    assert result["proposed_response"] == "Aquí tienes los pasos para resolverlo..."
    assert result["node_history"] == ["response"]