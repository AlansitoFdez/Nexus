"""Tests for entry_node — deterministic entry point to the code review graph."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.agents.nodes.entry_node import entry_node
from app.config import settings
from app.repositories.analysis_request_repository import AnalysisRequestRepository
from app.schemas.analysis_request import AnalysisRequestCreate

TEST_DATABASE_URL = "postgresql://user:password@localhost:5434/nexus_test"
engine = create_engine(TEST_DATABASE_URL)
TestSessionLocal = sessionmaker(bind=engine)


@pytest.mark.asyncio
async def test_entry_node_uses_pasted_code_directly(db_session):
    repo = AnalysisRequestRepository(db_session)
    request = repo.create(AnalysisRequestCreate(
        source_type="pasted_code", pasted_code="def foo(): pass", review_request="revisa seguridad"
    ))

    state = {
        "analysis_request_id": request.id,
        "source_type": "pasted_code",
        "repo_url": None,
        "pasted_code": "def foo(): pass",
        "review_request": "revisa seguridad",
    }

    with patch("app.agents.nodes.entry_node.SessionLocal", TestSessionLocal):
        result = await entry_node(state)

    assert result["code_content"] == "def foo(): pass"
    assert result["node_history"] == ["entry"]


@pytest.mark.asyncio
async def test_entry_node_reads_github_repo_via_mcp_tool(db_session):
    repo = AnalysisRequestRepository(db_session)
    request = repo.create(AnalysisRequestCreate(
        source_type="github_repo", repo_url="https://github.com/alan/nexus", review_request="revisa seguridad"
    ))

    state = {
        "analysis_request_id": request.id,
        "source_type": "github_repo",
        "repo_url": "https://github.com/alan/nexus",
        "pasted_code": None,
        "review_request": "revisa seguridad",
    }

    mock_client = MagicMock()
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=None)
    mock_result = MagicMock()
    mock_result.data = {"content": "print('hola')"}
    mock_client.call_tool = AsyncMock(return_value=mock_result)

    with patch("app.agents.nodes.entry_node.Client", return_value=mock_client) as mock_client_cls, \
         patch("app.agents.nodes.entry_node.SessionLocal", TestSessionLocal):
        result = await entry_node(state)

    assert result["code_content"] == {"content": "print('hola')"}
    # Regression: MCP_API_KEY must actually reach the client, or every
    # github_repo analysis fails with 401 the moment it hits a real
    # StaticTokenVerifier-protected server, not just the in-memory
    # test double this mock stands in for.
    mock_client_cls.assert_called_once_with(settings.MCP_SERVER_URL, auth=settings.MCP_API_KEY)
    mock_client.call_tool.assert_awaited_once_with(
        "read_repository_files", {"repo_url": "https://github.com/alan/nexus"}
    )


@pytest.mark.asyncio
async def test_entry_node_returns_error_when_repo_read_fails(db_session):
    repo = AnalysisRequestRepository(db_session)
    request = repo.create(AnalysisRequestCreate(
        source_type="github_repo", repo_url="https://github.com/alan/broken", review_request="revisa seguridad"
    ))

    state = {
        "analysis_request_id": request.id,
        "source_type": "github_repo",
        "repo_url": "https://github.com/alan/broken",
        "pasted_code": None,
        "review_request": "revisa seguridad",
    }

    mock_client = MagicMock()
    mock_client.__aenter__ = AsyncMock(side_effect=ConnectionError("no se pudo conectar"))
    mock_client.__aexit__ = AsyncMock(return_value=None)

    with patch("app.agents.nodes.entry_node.Client", return_value=mock_client), \
         patch("app.agents.nodes.entry_node.SessionLocal", TestSessionLocal):
        result = await entry_node(state)

    assert "error" in result
    assert result["node_history"] == ["entry"]


@pytest.mark.asyncio
async def test_entry_node_returns_error_when_analysis_request_not_found(db_session):
    state = {
        "analysis_request_id": 999,
        "source_type": "pasted_code",
        "repo_url": None,
        "pasted_code": "def foo(): pass",
        "review_request": "revisa seguridad",
    }

    with patch("app.agents.nodes.entry_node.SessionLocal", TestSessionLocal):
        result = await entry_node(state)

    assert "error" in result
    assert result["node_history"] == ["entry"]


@pytest.mark.asyncio
async def test_entry_node_returns_error_on_unexpected_database_failure(db_session):
    """AnalysisRequestNotFoundError isn't the only way this status update
    can fail — a real database outage or a truncated column must still
    land in state["error"], not propagate uncaught out of the node and
    leave the AnalysisRequest stuck at "running" forever."""
    repo = AnalysisRequestRepository(db_session)
    request = repo.create(AnalysisRequestCreate(
        source_type="pasted_code", pasted_code="def foo(): pass", review_request="revisa seguridad"
    ))

    state = {
        "analysis_request_id": request.id,
        "source_type": "pasted_code",
        "repo_url": None,
        "pasted_code": "def foo(): pass",
        "review_request": "revisa seguridad",
    }

    with patch("app.agents.nodes.entry_node.SessionLocal", TestSessionLocal), \
         patch.object(AnalysisRequestRepository, "update", side_effect=RuntimeError("connection lost")):
        result = await entry_node(state)

    assert "connection lost" in result["error"]
    assert result["node_history"] == ["entry"]