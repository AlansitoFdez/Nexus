"""Tests for synthesizer_node — combines specialist findings into the final report."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from tests.db import TestSessionLocal

from app.agents.nodes.synthesizer_node import synthesizer_node
from app.repositories.analysis_request_repository import AnalysisRequestRepository
from app.schemas.analysis_request import AnalysisRequestCreate


@pytest.mark.asyncio
async def test_synthesizer_includes_all_findings_sorted_by_severity(db_session):
    repo = AnalysisRequestRepository(db_session)
    request = repo.create(AnalysisRequestCreate(
        source_type="pasted_code", pasted_code="def foo(): pass", review_request="revisa todo"
    ))

    state = {
        "analysis_request_id": request.id,
        "findings": [
            {"specialist": "best_practices", "severity": "low", "description": "nombre poco claro", "file_path": None, "suggestion": None},
            {"specialist": "security", "severity": "critical", "description": "inyección SQL", "file_path": "db.py", "suggestion": "usar parámetros"},
        ],
        "failed_specialists": [],
    }

    mock_llm = MagicMock()
    mock_llm.ainvoke = AsyncMock(return_value=MagicMock(content="Resumen: hay un problema crítico de seguridad que debe atacarse primero."))

    with patch("app.agents.nodes.synthesizer_node.ChatGroq", return_value=mock_llm), \
         patch("app.agents.nodes.synthesizer_node.SessionLocal", TestSessionLocal):
        result = await synthesizer_node(state)

    assert "[CRITICAL]" in result["final_report"]
    assert "[LOW]" in result["final_report"]
    assert result["final_report"].index("[CRITICAL]") < result["final_report"].index("[LOW]")
    assert result["node_history"] == ["synthesizer"]

    db_session.expire_all()
    updated = repo.get_by_id(request.id)
    assert updated.status == "completed"
    assert updated.final_report == result["final_report"]


@pytest.mark.asyncio
async def test_synthesizer_sets_completed_with_errors_when_specialist_failed(db_session):
    repo = AnalysisRequestRepository(db_session)
    request = repo.create(AnalysisRequestCreate(
        source_type="pasted_code", pasted_code="def foo(): pass", review_request="revisa todo"
    ))

    state = {
        "analysis_request_id": request.id,
        "findings": [{"specialist": "security", "severity": "high", "description": "x", "file_path": None, "suggestion": None}],
        "failed_specialists": ["performance"],
    }

    mock_llm = MagicMock()
    mock_llm.ainvoke = AsyncMock(return_value=MagicMock(content="Resumen breve."))

    with patch("app.agents.nodes.synthesizer_node.ChatGroq", return_value=mock_llm), \
         patch("app.agents.nodes.synthesizer_node.SessionLocal", TestSessionLocal):
        result = await synthesizer_node(state)

    assert "performance" in result["final_report"]

    db_session.expire_all()
    updated = repo.get_by_id(request.id)
    assert updated.status == "completed_with_errors"


@pytest.mark.asyncio
async def test_synthesizer_falls_back_to_deterministic_section_when_llm_fails(db_session):
    repo = AnalysisRequestRepository(db_session)
    request = repo.create(AnalysisRequestCreate(
        source_type="pasted_code", pasted_code="def foo(): pass", review_request="revisa todo"
    ))

    state = {
        "analysis_request_id": request.id,
        "findings": [{"specialist": "security", "severity": "critical", "description": "problema real", "file_path": None, "suggestion": None}],
        "failed_specialists": [],
    }

    mock_llm = MagicMock()
    mock_llm.ainvoke = AsyncMock(side_effect=Exception("groq unavailable"))

    with patch("app.agents.nodes.synthesizer_node.ChatGroq", return_value=mock_llm), \
         patch("app.agents.nodes.synthesizer_node.SessionLocal", TestSessionLocal):
        result = await synthesizer_node(state)

    assert "problema real" in result["final_report"]
    assert "no se pudo generar el resumen narrativo" in result["final_report"].lower()

    db_session.expire_all()
    updated = repo.get_by_id(request.id)
    assert updated.status == "completed"


@pytest.mark.asyncio
async def test_synthesizer_handles_empty_findings_gracefully(db_session):
    repo = AnalysisRequestRepository(db_session)
    request = repo.create(AnalysisRequestCreate(
        source_type="pasted_code", pasted_code="def foo(): pass", review_request="revisa todo"
    ))

    state = {"analysis_request_id": request.id, "findings": [], "failed_specialists": []}

    mock_llm = MagicMock()
    mock_llm.ainvoke = AsyncMock(return_value=MagicMock(content="No se detectaron problemas."))

    with patch("app.agents.nodes.synthesizer_node.ChatGroq", return_value=mock_llm), \
         patch("app.agents.nodes.synthesizer_node.SessionLocal", TestSessionLocal):
        result = await synthesizer_node(state)

    assert "no se encontraron hallazgos" in result["final_report"].lower()


@pytest.mark.asyncio
async def test_synthesizer_returns_error_when_analysis_request_not_found(db_session):
    state = {"analysis_request_id": 999, "findings": [], "failed_specialists": []}

    mock_llm = MagicMock()
    mock_llm.ainvoke = AsyncMock(return_value=MagicMock(content="Resumen."))

    with patch("app.agents.nodes.synthesizer_node.ChatGroq", return_value=mock_llm), \
         patch("app.agents.nodes.synthesizer_node.SessionLocal", TestSessionLocal):
        result = await synthesizer_node(state)

    assert "error" in result
    assert "final_report" in result


@pytest.mark.asyncio
async def test_synthesizer_returns_error_on_unexpected_database_failure(db_session):
    """Same widened except as entry_node — not every failure persisting
    the final report is AnalysisRequestNotFoundError."""
    repo = AnalysisRequestRepository(db_session)
    request = repo.create(AnalysisRequestCreate(
        source_type="pasted_code", pasted_code="def foo(): pass", review_request="revisa todo"
    ))

    state = {"analysis_request_id": request.id, "findings": [], "failed_specialists": []}

    mock_llm = MagicMock()
    mock_llm.ainvoke = AsyncMock(return_value=MagicMock(content="Resumen."))

    with patch("app.agents.nodes.synthesizer_node.ChatGroq", return_value=mock_llm), \
         patch("app.agents.nodes.synthesizer_node.SessionLocal", TestSessionLocal), \
         patch.object(AnalysisRequestRepository, "update", side_effect=RuntimeError("connection lost")):
        result = await synthesizer_node(state)

    assert "error" in result
    # The raw exception must not reach state["error"] (Fase 3 review,
    # 3.4) — it's forwarded verbatim to the browser over WebSocket.
    assert "connection lost" not in result["error"]
    assert "final_report" in result
