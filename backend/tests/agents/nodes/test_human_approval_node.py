"""Tests for human_approval_node.

interrupt() itself is patched directly rather than exercised for real —
verifying that it actually pauses graph execution requires a compiled
graph with a real Redis checkpointer (Fase 2.12, still pending per the
roadmap even in the ticket domain). These tests cover this node's own
logic: creating/updating the Approval record and building the correct
state delta given whatever decision comes back.
"""

from unittest.mock import patch

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.agents.nodes.human_approval_node import human_approval_node
from app.repositories.analysis_request_repository import AnalysisRequestRepository
from app.repositories.approval_repository import ApprovalRepository
from app.schemas.analysis_request import AnalysisRequestCreate

TEST_DATABASE_URL = "postgresql://user:password@localhost:5434/nexus_test"
engine = create_engine(TEST_DATABASE_URL)
TestSessionLocal = sessionmaker(bind=engine)


@pytest.mark.asyncio
async def test_human_approval_node_skips_when_post_to_pr_is_false(db_session):
    state = {"analysis_request_id": 1, "post_to_pr": False, "final_report": "informe"}

    with patch("app.agents.nodes.human_approval_node.interrupt") as mock_interrupt:
        result = await human_approval_node(state)

    mock_interrupt.assert_not_called()
    assert result == {"node_history": ["human_approval"]}


@pytest.mark.asyncio
async def test_human_approval_node_persists_approved_decision(db_session):
    analysis_repo = AnalysisRequestRepository(db_session)
    request = analysis_repo.create(AnalysisRequestCreate(
        source_type="github_repo",
        repo_url="https://github.com/alan/nexus",
        review_request="revisa seguridad",
        post_to_pr=True,
        pr_number=42,
    ))

    state = {"analysis_request_id": request.id, "post_to_pr": True, "final_report": "informe completo"}

    with patch("app.agents.nodes.human_approval_node.interrupt", return_value="approved"), \
         patch("app.agents.nodes.human_approval_node.SessionLocal", TestSessionLocal):
        result = await human_approval_node(state)

    assert result == {"node_history": ["human_approval"]}

    approval_repo = ApprovalRepository(db_session, analysis_repo)
    db_session.expire_all()
    approvals = approval_repo.get_all()
    assert len(approvals) == 1
    assert approvals[0].status == "approved"
    assert approvals[0].decided_at is not None


@pytest.mark.asyncio
async def test_human_approval_node_reuses_pending_approval_on_reexecution(db_session):
    """interrupt() makes LangGraph re-run this node's entire function
    from the top on resume — only the interrupt() call itself "remembers"
    it was already answered. Calling the node twice for the same
    analysis_request_id models exactly that replay. Without the
    idempotent lookup, this created a second Approval row on the second
    call, leaving the first stuck at "pending" forever."""
    analysis_repo = AnalysisRequestRepository(db_session)
    request = analysis_repo.create(AnalysisRequestCreate(
        source_type="github_repo",
        repo_url="https://github.com/alan/nexus",
        review_request="revisa seguridad",
        post_to_pr=True,
        pr_number=42,
    ))

    state = {"analysis_request_id": request.id, "post_to_pr": True, "final_report": "informe completo"}

    with patch("app.agents.nodes.human_approval_node.interrupt", return_value="approved"), \
         patch("app.agents.nodes.human_approval_node.SessionLocal", TestSessionLocal):
        await human_approval_node(state)
        result = await human_approval_node(state)

    assert result == {"node_history": ["human_approval"]}

    approval_repo = ApprovalRepository(db_session, analysis_repo)
    db_session.expire_all()
    approvals = approval_repo.get_all()
    assert len(approvals) == 1
    assert approvals[0].status == "approved"


@pytest.mark.asyncio
async def test_human_approval_node_rejects_and_cancels_post_to_pr(db_session):
    analysis_repo = AnalysisRequestRepository(db_session)
    request = analysis_repo.create(AnalysisRequestCreate(
        source_type="github_repo",
        repo_url="https://github.com/alan/nexus",
        review_request="revisa seguridad",
        post_to_pr=True,
        pr_number=42,
    ))

    state = {"analysis_request_id": request.id, "post_to_pr": True, "final_report": "informe completo"}

    with patch("app.agents.nodes.human_approval_node.interrupt", return_value="rejected"), \
         patch("app.agents.nodes.human_approval_node.SessionLocal", TestSessionLocal):
        result = await human_approval_node(state)

    assert result == {"post_to_pr": False, "node_history": ["human_approval"]}

    approval_repo = ApprovalRepository(db_session, analysis_repo)
    db_session.expire_all()
    approvals = approval_repo.get_all()
    assert approvals[0].status == "rejected"


@pytest.mark.asyncio
async def test_human_approval_node_returns_error_when_analysis_request_missing(db_session):
    state = {"analysis_request_id": 999, "post_to_pr": True, "final_report": "informe"}

    with patch("app.agents.nodes.human_approval_node.interrupt") as mock_interrupt, \
         patch("app.agents.nodes.human_approval_node.SessionLocal", TestSessionLocal):
        result = await human_approval_node(state)

    mock_interrupt.assert_not_called()
    assert "error" in result