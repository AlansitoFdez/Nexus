"""Tests for failure_node — the terminal path for pre-fanout failures."""

import pytest

from app.agents.nodes.failure_node import failure_node
from app.repositories.analysis_request_repository import AnalysisRequestRepository
from app.schemas.analysis_request import AnalysisRequestCreate
from tests.db import TestSessionLocal


@pytest.mark.asyncio
async def test_failure_node_persists_failed_status(db_session):
    from unittest.mock import patch

    repo = AnalysisRequestRepository(db_session)
    request = repo.create(AnalysisRequestCreate(
        source_type="pasted_code", pasted_code="def foo(): pass", review_request="revisa seguridad"
    ))

    state = {"analysis_request_id": request.id}

    with patch("app.agents.nodes.failure_node.SessionLocal", TestSessionLocal):
        result = await failure_node(state)

    assert result == {"node_history": ["failure"]}

    db_session.expire_all()
    updated = repo.get_by_id(request.id)
    assert updated.status == "failed"


@pytest.mark.asyncio
async def test_failure_node_does_not_raise_when_analysis_request_missing(db_session):
    from unittest.mock import patch

    state = {"analysis_request_id": 999}

    with patch("app.agents.nodes.failure_node.SessionLocal", TestSessionLocal):
        result = await failure_node(state)

    assert result == {"node_history": ["failure"]}


@pytest.mark.asyncio
async def test_failure_node_does_not_raise_on_unexpected_database_failure(db_session):
    """failure_node is already the graph's own terminal error handler —
    its only edge goes straight to END, so if its own write fails for a
    reason other than "not found", there's no further node to hand off
    to. Must be logged, never raised."""
    from unittest.mock import patch

    repo = AnalysisRequestRepository(db_session)
    request = repo.create(AnalysisRequestCreate(
        source_type="pasted_code", pasted_code="def foo(): pass", review_request="revisa seguridad"
    ))

    state = {"analysis_request_id": request.id}

    with patch("app.agents.nodes.failure_node.SessionLocal", TestSessionLocal), \
         patch.object(AnalysisRequestRepository, "update", side_effect=RuntimeError("connection lost")):
        result = await failure_node(state)

    assert result == {"node_history": ["failure"]}
