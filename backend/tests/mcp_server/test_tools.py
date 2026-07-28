"""Tests for placeholder MCP tools, using FastMCP's in-memory client."""

from unittest.mock import patch

import pytest
from fastmcp import Client
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.mcp_server.instance import mcp
from app.mcp_server import tools
from app.repositories.knowledge_base_repository import KnowledgeBaseRepository
from app.schemas.knowledge_base import KnowledgeBaseEntryCreate
from app.repositories.ticket_repository import TicketRepository, TicketUpdate
from app.schemas.ticket import TicketCreate

TEST_DATABASE_URL = "postgresql://user:password@localhost:5434/nexus_test"
engine = create_engine(TEST_DATABASE_URL)
TestSessionLocal = sessionmaker(bind=engine)

@pytest.mark.asyncio
async def test_search_knowledge_base_returns_relevant_entries(db_session):
    repo = KnowledgeBaseRepository(db_session)
    repo.create(KnowledgeBaseEntryCreate(title="Cómo resetear tu contraseña", content="Pasos para restablecer el acceso"))
    repo.create(KnowledgeBaseEntryCreate(title="Cómo cambiar tu foto de perfil", content="Sube una imagen desde ajustes"))

    with patch.object(tools, "SessionLocal", TestSessionLocal):
        async with Client(mcp) as client:
            result = await client.call_tool("search_knowledge_base", {"query": "contraseña"})

    assert result.data[0]["title"] == "Cómo resetear tu contraseña"


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
async def test_create_external_ticket_returns_external_id(db_session):
    ticket = TicketRepository(db_session).create(TicketCreate(original_text="fallo crítico"))

    with patch.object(tools, "SessionLocal", TestSessionLocal):
        async with Client(mcp) as client:
            result = await client.call_tool(
                "create_external_ticket", {"ticket_id": ticket.id, "summary": "fallo de login"}
            )

    assert result.data["status"] == "created"
    assert result.data["external_ticket_id"].startswith("EXT-")


@pytest.mark.asyncio
async def test_notify_team_confirms_notification_sent(db_session):
    with patch.object(tools, "SessionLocal", TestSessionLocal):
        async with Client(mcp) as client:
            result = await client.call_tool("notify_team", {"message": "ticket urgente"})

    assert result.data["notified"] is True
    assert result.data["channel"] == "log"


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