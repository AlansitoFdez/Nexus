from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.agents.nodes.specialists.best_practices_agent import best_practices_agent
from app.agents.schemas import SpecialistFinding, SpecialistOutput
from app.repositories.analysis_request_repository import AnalysisRequestRepository
from app.repositories.finding_repository import FindingRepository
from app.schemas.analysis_request import AnalysisRequestCreate

TEST_DATABASE_URL = "postgresql://user:password@localhost:5434/nexus_test"
engine = create_engine(TEST_DATABASE_URL)
TestSessionLocal = sessionmaker(bind=engine)


@pytest.mark.asyncio
async def test_best_practices_agent_persists_findings_from_llm_output(db_session):
    analysis_repo = AnalysisRequestRepository(db_session)
    request = analysis_repo.create(AnalysisRequestCreate(
        source_type="pasted_code", pasted_code="def f(x,y,z): return x+y+z", review_request="revisa buenas prácticas"
    ))

    payload = {
        "code_content": "def f(x,y,z): return x+y+z",
        "review_request": "revisa buenas prácticas",
        "analysis_request_id": request.id,
    }

    mock_llm = MagicMock()
    mock_structured = MagicMock()
    mock_structured.ainvoke = AsyncMock(return_value=SpecialistOutput(findings=[
        SpecialistFinding(severity="low", description="Nombres de parámetros poco descriptivos")
    ]))
    mock_llm.with_structured_output.return_value = mock_structured

    with patch("app.agents.nodes.specialists.best_practices_agent.ChatGroq", return_value=mock_llm), \
         patch("app.agents.nodes.specialists.best_practices_agent.SessionLocal", TestSessionLocal):
        result = await best_practices_agent(payload)

    assert len(result["findings"]) == 1
    assert result["findings"][0]["specialist"] == "best_practices"
    assert result["node_history"] == ["best_practices_agent"]


@pytest.mark.asyncio
async def test_best_practices_agent_returns_empty_findings_when_no_issues_found(db_session):
    analysis_repo = AnalysisRequestRepository(db_session)
    request = analysis_repo.create(AnalysisRequestCreate(
        source_type="pasted_code", pasted_code="def add(a, b): return a + b", review_request="revisa buenas prácticas"
    ))

    payload = {"code_content": "def add(a, b): return a + b", "review_request": "revisa buenas prácticas", "analysis_request_id": request.id}

    mock_llm = MagicMock()
    mock_structured = MagicMock()
    mock_structured.ainvoke = AsyncMock(return_value=SpecialistOutput(findings=[]))
    mock_llm.with_structured_output.return_value = mock_structured

    with patch("app.agents.nodes.specialists.best_practices_agent.ChatGroq", return_value=mock_llm), \
         patch("app.agents.nodes.specialists.best_practices_agent.SessionLocal", TestSessionLocal):
        result = await best_practices_agent(payload)

    assert result["findings"] == []


@pytest.mark.asyncio
async def test_best_practices_agent_returns_failed_specialist_when_llm_call_fails(db_session):
    payload = {"code_content": "def foo(): pass", "review_request": "revisa buenas prácticas", "analysis_request_id": 999}

    mock_llm = MagicMock()
    mock_structured = MagicMock()
    mock_structured.ainvoke = AsyncMock(side_effect=Exception("groq unavailable"))
    mock_llm.with_structured_output.return_value = mock_structured

    with patch("app.agents.nodes.specialists.best_practices_agent.ChatGroq", return_value=mock_llm), \
         patch("app.agents.nodes.specialists.best_practices_agent.SessionLocal", TestSessionLocal):
        result = await best_practices_agent(payload)

    assert result["failed_specialists"] == ["best_practices"]
    assert "error" not in result


@pytest.mark.asyncio
async def test_best_practices_agent_returns_failed_specialist_when_analysis_request_missing(db_session):
    payload = {"code_content": "def foo(): pass", "review_request": "revisa buenas prácticas", "analysis_request_id": 999}

    mock_llm = MagicMock()
    mock_structured = MagicMock()
    mock_structured.ainvoke = AsyncMock(return_value=SpecialistOutput(findings=[
        SpecialistFinding(severity="low", description="algo menor")
    ]))
    mock_llm.with_structured_output.return_value = mock_structured

    with patch("app.agents.nodes.specialists.best_practices_agent.ChatGroq", return_value=mock_llm), \
         patch("app.agents.nodes.specialists.best_practices_agent.SessionLocal", TestSessionLocal):
        result = await best_practices_agent(payload)

    assert result["failed_specialists"] == ["best_practices"]