from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.agents.nodes.specialists.performance_agent import performance_agent
from app.agents.schemas import SpecialistFinding, SpecialistOutput
from app.repositories.analysis_request_repository import AnalysisRequestRepository
from app.repositories.finding_repository import FindingRepository
from app.schemas.analysis_request import AnalysisRequestCreate

TEST_DATABASE_URL = "postgresql://user:password@localhost:5434/nexus_test"
engine = create_engine(TEST_DATABASE_URL)
TestSessionLocal = sessionmaker(bind=engine)


@pytest.mark.asyncio
async def test_performance_agent_persists_findings_from_llm_output(db_session):
    analysis_repo = AnalysisRequestRepository(db_session)
    request = analysis_repo.create(AnalysisRequestCreate(
        source_type="pasted_code", pasted_code="for i in range(n):\n    query_db(i)", review_request="revisa rendimiento"
    ))

    payload = {
        "code_content": "for i in range(n):\n    query_db(i)",
        "review_request": "revisa rendimiento",
        "analysis_request_id": request.id,
    }

    mock_llm = MagicMock()
    mock_structured = MagicMock()
    mock_structured.ainvoke = AsyncMock(return_value=SpecialistOutput(findings=[
        SpecialistFinding(severity="medium", description="Consulta N+1 dentro del bucle", suggestion="batch query")
    ]))
    mock_llm.with_structured_output.return_value = mock_structured

    with patch("app.agents.nodes.specialists.performance_agent.ChatGroq", return_value=mock_llm), \
         patch("app.agents.nodes.specialists.performance_agent.SessionLocal", TestSessionLocal):
        result = await performance_agent(payload)

    assert len(result["findings"]) == 1
    assert result["findings"][0]["specialist"] == "performance"
    assert result["node_history"] == ["performance_agent"]

    finding_repo = FindingRepository(db_session, analysis_repo)
    persisted = finding_repo.get_by_analysis_request_id(request.id)
    assert len(persisted) == 1


@pytest.mark.asyncio
async def test_performance_agent_returns_empty_findings_when_no_issues_found(db_session):
    analysis_repo = AnalysisRequestRepository(db_session)
    request = analysis_repo.create(AnalysisRequestCreate(
        source_type="pasted_code", pasted_code="def add(a, b): return a + b", review_request="revisa rendimiento"
    ))

    payload = {"code_content": "def add(a, b): return a + b", "review_request": "revisa rendimiento", "analysis_request_id": request.id}

    mock_llm = MagicMock()
    mock_structured = MagicMock()
    mock_structured.ainvoke = AsyncMock(return_value=SpecialistOutput(findings=[]))
    mock_llm.with_structured_output.return_value = mock_structured

    with patch("app.agents.nodes.specialists.performance_agent.ChatGroq", return_value=mock_llm), \
         patch("app.agents.nodes.specialists.performance_agent.SessionLocal", TestSessionLocal):
        result = await performance_agent(payload)

    assert result["findings"] == []


@pytest.mark.asyncio
async def test_performance_agent_returns_failed_specialist_when_llm_call_fails(db_session):
    payload = {"code_content": "def foo(): pass", "review_request": "revisa rendimiento", "analysis_request_id": 999}

    mock_llm = MagicMock()
    mock_structured = MagicMock()
    mock_structured.ainvoke = AsyncMock(side_effect=Exception("groq unavailable"))
    mock_llm.with_structured_output.return_value = mock_structured

    with patch("app.agents.nodes.specialists.performance_agent.ChatGroq", return_value=mock_llm), \
         patch("app.agents.nodes.specialists.performance_agent.SessionLocal", TestSessionLocal):
        result = await performance_agent(payload)

    assert result["failed_specialists"] == ["performance"]
    assert "error" not in result


@pytest.mark.asyncio
async def test_performance_agent_returns_failed_specialist_when_analysis_request_missing(db_session):
    payload = {"code_content": "def foo(): pass", "review_request": "revisa rendimiento", "analysis_request_id": 999}

    mock_llm = MagicMock()
    mock_structured = MagicMock()
    mock_structured.ainvoke = AsyncMock(return_value=SpecialistOutput(findings=[
        SpecialistFinding(severity="low", description="algo menor")
    ]))
    mock_llm.with_structured_output.return_value = mock_structured

    with patch("app.agents.nodes.specialists.performance_agent.ChatGroq", return_value=mock_llm), \
         patch("app.agents.nodes.specialists.performance_agent.SessionLocal", TestSessionLocal):
        result = await performance_agent(payload)

    assert result["failed_specialists"] == ["performance"]