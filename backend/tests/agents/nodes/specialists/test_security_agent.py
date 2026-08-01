"""Tests for security_agent — first specialist node in the ensemble."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.agents.nodes.specialists.security_agent import security_agent
from app.agents.schemas import SpecialistFinding, SpecialistOutput
from app.repositories.analysis_request_repository import AnalysisRequestRepository
from app.repositories.finding_repository import FindingRepository
from app.schemas.analysis_request import AnalysisRequestCreate

TEST_DATABASE_URL = "postgresql://user:password@localhost:5434/nexus_test"
engine = create_engine(TEST_DATABASE_URL)
TestSessionLocal = sessionmaker(bind=engine)


@pytest.mark.asyncio
async def test_security_agent_persists_findings_from_llm_output(db_session):
    analysis_repo = AnalysisRequestRepository(db_session)
    request = analysis_repo.create(AnalysisRequestCreate(
        source_type="pasted_code", pasted_code="query = f'SELECT * FROM users WHERE id={id}'", review_request="revisa seguridad"
    ))

    payload = {
        "code_content": "query = f'SELECT * FROM users WHERE id={id}'",
        "review_request": "revisa seguridad",
        "analysis_request_id": request.id,
    }

    mock_llm = MagicMock()
    mock_structured = MagicMock()
    mock_structured.ainvoke = AsyncMock(return_value=SpecialistOutput(findings=[
        SpecialistFinding(severity="high", description="Inyección SQL vía f-string", suggestion="usar parámetros")
    ]))
    mock_llm.with_structured_output.return_value = mock_structured

    with patch("app.agents.nodes.specialists.security_agent.ChatGroq", return_value=mock_llm), \
         patch("app.agents.nodes.specialists.security_agent.SessionLocal", TestSessionLocal):
        result = await security_agent(payload)

    assert len(result["findings"]) == 1
    assert result["findings"][0]["specialist"] == "security"
    assert result["findings"][0]["severity"] == "high"
    assert result["node_history"] == ["security_agent"]

    finding_repo = FindingRepository(db_session, analysis_repo)
    persisted = finding_repo.get_by_analysis_request_id(request.id)
    assert len(persisted) == 1
    assert persisted[0].description == "Inyección SQL vía f-string"


@pytest.mark.asyncio
async def test_security_agent_returns_empty_findings_when_no_issues_found(db_session):
    analysis_repo = AnalysisRequestRepository(db_session)
    request = analysis_repo.create(AnalysisRequestCreate(
        source_type="pasted_code", pasted_code="def add(a, b): return a + b", review_request="revisa seguridad"
    ))

    payload = {
        "code_content": "def add(a, b): return a + b",
        "review_request": "revisa seguridad",
        "analysis_request_id": request.id,
    }

    mock_llm = MagicMock()
    mock_structured = MagicMock()
    mock_structured.ainvoke = AsyncMock(return_value=SpecialistOutput(findings=[]))
    mock_llm.with_structured_output.return_value = mock_structured

    with patch("app.agents.nodes.specialists.security_agent.ChatGroq", return_value=mock_llm), \
         patch("app.agents.nodes.specialists.security_agent.SessionLocal", TestSessionLocal):
        result = await security_agent(payload)

    assert result["findings"] == []
    assert result["node_history"] == ["security_agent"]


@pytest.mark.asyncio
async def test_security_agent_returns_failed_specialist_when_llm_call_fails(db_session):
    payload = {
        "code_content": "def foo(): pass",
        "review_request": "revisa seguridad",
        "analysis_request_id": 999,
    }

    mock_llm = MagicMock()
    mock_structured = MagicMock()
    mock_structured.ainvoke = AsyncMock(side_effect=Exception("groq unavailable"))
    mock_llm.with_structured_output.return_value = mock_structured

    with patch("app.agents.nodes.specialists.security_agent.ChatGroq", return_value=mock_llm), \
         patch("app.agents.nodes.specialists.security_agent.SessionLocal", TestSessionLocal):
        result = await security_agent(payload)

    assert result["failed_specialists"] == ["security"]
    assert result["node_history"] == ["security_agent"]
    assert "error" not in result


@pytest.mark.asyncio
async def test_security_agent_returns_failed_specialist_when_analysis_request_missing(db_session):
    payload = {
        "code_content": "def foo(): pass",
        "review_request": "revisa seguridad",
        "analysis_request_id": 999,
    }

    mock_llm = MagicMock()
    mock_structured = MagicMock()
    mock_structured.ainvoke = AsyncMock(return_value=SpecialistOutput(findings=[
        SpecialistFinding(severity="low", description="algo menor")
    ]))
    mock_llm.with_structured_output.return_value = mock_structured

    with patch("app.agents.nodes.specialists.security_agent.ChatGroq", return_value=mock_llm), \
         patch("app.agents.nodes.specialists.security_agent.SessionLocal", TestSessionLocal):
        result = await security_agent(payload)

    assert result["failed_specialists"] == ["security"]