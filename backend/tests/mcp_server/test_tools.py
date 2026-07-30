"""Tests for MCP tools, using FastMCP's in-memory client."""

from unittest.mock import patch

import pytest
from fastmcp import Client
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.mcp_server.instance import mcp
from app.mcp_server import tools
from app.repositories.ticket_repository import TicketRepository, TicketUpdate
from app.schemas.ticket import TicketCreate

TEST_DATABASE_URL = "postgresql://user:password@localhost:5434/nexus_test"
engine = create_engine(TEST_DATABASE_URL)
TestSessionLocal = sessionmaker(bind=engine)


@pytest.mark.asyncio
async def test_query_tickets_db_returns_similar_resolved_tickets(db_session):
    ticket_repo = TicketRepository(db_session)
    ticket = ticket_repo.create(TicketCreate(original_text="no puedo iniciar sesión"))
    ticket_repo.update(ticket.id, TicketUpdate(classification="bug", proposed_response="Reinicia el servicio"))

    with patch.object(tools, "SessionLocal", TestSessionLocal):
        async with Client(mcp) as client:
            result = await client.call_tool("query_tickets_db", {"category": "bug"})

    assert result.data[0]["classification"] == "bug"
    assert result.data[0]["solution"] == "Reinicia el servicio"


@pytest.mark.asyncio
async def test_server_exposes_only_query_tickets_db():
    async with Client(mcp) as client:
        tools_list = await client.list_tools()

    tool_names = {tool.name for tool in tools_list}
    assert tool_names == {"query_tickets_db"}