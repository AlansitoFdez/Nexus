"""Tests for failure_node — the terminal path for pre-fanout failures."""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.agents.nodes.failure_node import failure_node
from app.repositories.analysis_request_repository import AnalysisRequestRepository
from app.schemas.analysis_request import AnalysisRequestCreate

TEST_DATABASE_URL = "postgresql://user:password@localhost:5434/nexus_test"
engine = create_engine(TEST_DATABASE_URL)
TestSessionLocal = sessionmaker(bind=engine)


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