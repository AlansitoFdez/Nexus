"""Tests for make_specialist_node — the shared factory every specialist
node is built from (Fase 4.1 review).

Parametrized over every entry in SPECIALISTS rather than duplicated per
specialist (security_agent.py, performance_agent.py, design_patterns_agent.py
and best_practices_agent.py used to each have their own near-identical
test file): all four specialists run through the exact same factory, so
a per-specialist test file would just be testing the same logic four
times under a different name.
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from tests.db import TestSessionLocal

from app.agents.nodes.specialist_node import make_specialist_node
from app.agents.schemas import SpecialistFinding, SpecialistOutput
from app.agents.specialists import SPECIALISTS
from app.repositories.analysis_request_repository import AnalysisRequestRepository
from app.repositories.finding_repository import FindingRepository
from app.schemas.analysis_request import AnalysisRequestCreate


@pytest.mark.asyncio
@pytest.mark.parametrize("name", list(SPECIALISTS.keys()))
async def test_specialist_persists_findings_from_llm_output(name, db_session):
    node = make_specialist_node(name, SPECIALISTS[name])
    analysis_repo = AnalysisRequestRepository(db_session)
    request = analysis_repo.create(AnalysisRequestCreate(
        source_type="pasted_code", pasted_code="def foo(): pass", review_request=f"revisa {name}"
    ))

    payload = {
        "code_content": "def foo(): pass",
        "review_request": f"revisa {name}",
        "analysis_request_id": request.id,
    }

    mock_llm = MagicMock()
    mock_structured = MagicMock()
    mock_structured.ainvoke = AsyncMock(return_value=SpecialistOutput(findings=[
        SpecialistFinding(severity="high", description="hallazgo real", suggestion="arréglalo")
    ]))
    mock_llm.with_structured_output.return_value = mock_structured

    with patch("app.agents.nodes.specialist_node.ChatGroq", return_value=mock_llm), \
         patch("app.agents.nodes.specialist_node.SessionLocal", TestSessionLocal):
        result = await node(payload)

    assert len(result["findings"]) == 1
    assert result["findings"][0]["specialist"] == name
    assert result["findings"][0]["severity"] == "high"
    assert result["node_history"] == [f"{name}_agent"]

    finding_repo = FindingRepository(db_session, analysis_repo)
    persisted = finding_repo.get_by_analysis_request_id(request.id)
    assert len(persisted) == 1
    assert persisted[0].description == "hallazgo real"


@pytest.mark.asyncio
@pytest.mark.parametrize("name", list(SPECIALISTS.keys()))
async def test_specialist_returns_empty_findings_when_no_issues_found(name, db_session):
    node = make_specialist_node(name, SPECIALISTS[name])
    analysis_repo = AnalysisRequestRepository(db_session)
    request = analysis_repo.create(AnalysisRequestCreate(
        source_type="pasted_code", pasted_code="def add(a, b): return a + b", review_request=f"revisa {name}"
    ))

    payload = {
        "code_content": "def add(a, b): return a + b",
        "review_request": f"revisa {name}",
        "analysis_request_id": request.id,
    }

    mock_llm = MagicMock()
    mock_structured = MagicMock()
    mock_structured.ainvoke = AsyncMock(return_value=SpecialistOutput(findings=[]))
    mock_llm.with_structured_output.return_value = mock_structured

    with patch("app.agents.nodes.specialist_node.ChatGroq", return_value=mock_llm), \
         patch("app.agents.nodes.specialist_node.SessionLocal", TestSessionLocal):
        result = await node(payload)

    assert result["findings"] == []
    assert result["node_history"] == [f"{name}_agent"]


@pytest.mark.asyncio
@pytest.mark.parametrize("name", list(SPECIALISTS.keys()))
async def test_specialist_returns_failed_specialist_when_llm_call_fails(name, db_session, caplog):
    node = make_specialist_node(name, SPECIALISTS[name])
    payload = {"code_content": "def foo(): pass", "review_request": f"revisa {name}", "analysis_request_id": 999}

    mock_llm = MagicMock()
    mock_structured = MagicMock()
    mock_structured.ainvoke = AsyncMock(side_effect=Exception("groq unavailable"))
    mock_llm.with_structured_output.return_value = mock_structured

    with patch("app.agents.nodes.specialist_node.ChatGroq", return_value=mock_llm), \
         patch("app.agents.nodes.specialist_node.SessionLocal", TestSessionLocal):
        result = await node(payload)

    assert result["failed_specialists"] == [name]
    assert result["node_history"] == [f"{name}_agent"]
    assert "error" not in result

    # Fase 5.1 review: before this, a specialist's LLM failure vanished
    # completely — only its bare name showed up in failed_specialists,
    # with no record anywhere of what actually went wrong.
    assert any(name in record.message and "LLM call" in record.message for record in caplog.records)


@pytest.mark.asyncio
@pytest.mark.parametrize("name", list(SPECIALISTS.keys()))
async def test_specialist_returns_failed_specialist_when_analysis_request_missing(name, db_session, caplog):
    node = make_specialist_node(name, SPECIALISTS[name])
    payload = {"code_content": "def foo(): pass", "review_request": f"revisa {name}", "analysis_request_id": 999}

    mock_llm = MagicMock()
    mock_structured = MagicMock()
    mock_structured.ainvoke = AsyncMock(return_value=SpecialistOutput(findings=[
        SpecialistFinding(severity="low", description="algo menor")
    ]))
    mock_llm.with_structured_output.return_value = mock_structured

    with patch("app.agents.nodes.specialist_node.ChatGroq", return_value=mock_llm), \
         patch("app.agents.nodes.specialist_node.SessionLocal", TestSessionLocal):
        result = await node(payload)

    assert result["failed_specialists"] == [name]
    # Fase 5.1 review: same as the LLM-failure case above, but for a
    # persistence failure (here, the analysis request doesn't exist).
    assert any(name in record.message and "persist" in record.message for record in caplog.records)
