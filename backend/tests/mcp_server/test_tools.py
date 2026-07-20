"""Tests for placeholder MCP tools, using FastMCP's in-memory client."""

import pytest
from fastmcp import Client

from app.mcp_server.instance import mcp
from app.mcp_server import tools  


@pytest.mark.asyncio
async def test_search_knowledge_base_returns_relevant_entries():
    async with Client(mcp) as client:
        result = await client.call_tool("search_knowledge_base", {"query": "contraseña"})

    assert result.data[0]["title"] == "Cómo resetear tu contraseña"


@pytest.mark.asyncio
async def test_query_tickets_db_returns_similar_resolved_tickets():
    async with Client(mcp) as client:
        result = await client.call_tool("query_tickets_db", {"category": "bug"})

    assert result.data[0]["classification"] == "bug"


@pytest.mark.asyncio
async def test_create_external_ticket_returns_external_id():
    async with Client(mcp) as client:
        result = await client.call_tool(
            "create_external_ticket", {"ticket_id": 1, "summary": "fallo de login"}
        )

    assert result.data["status"] == "created"


@pytest.mark.asyncio
async def test_notify_team_confirms_notification_sent():
    async with Client(mcp) as client:
        result = await client.call_tool("notify_team", {"message": "ticket urgente"})

    assert result.data["notified"] is True


@pytest.mark.asyncio
async def test_server_exposes_all_four_placeholder_tools():
    async with Client(mcp) as client:
        tools_list = await client.list_tools()

    tool_names = {tool.name for tool in tools_list}
    assert tool_names == {
        "search_knowledge_base",
        "query_tickets_db",
        "create_external_ticket",
        "notify_team",
    }