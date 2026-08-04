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
from tests.db import TestSessionLocal

from app.agents.nodes.human_approval_node import human_approval_node
from app.repositories.analysis_request_repository import AnalysisRequestRepository
from app.repositories.approval_repository import ApprovalRepository
from app.schemas.analysis_request import AnalysisRequestCreate


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
    """interrupt() makes LangGraph re-run this node's entire function from
    the top on resume — but crucially, the FIRST run never gets past the
    interrupt() call at all, because that's what pausing means. This is
    modeled faithfully by making the first call's interrupt() raise
    (mirroring how real interrupt() pausing works via an exception
    LangGraph's runtime catches) instead of returning a value — a naive
    version of this test that just mocks interrupt() to return "approved"
    on both calls would let the first call run all the way through its
    own update(), leaving nothing "pending" for the second call to find,
    masking the exact bug this guards against. Only the second call (the
    resume) lets interrupt() return a decision and the function proceed.

    Without the idempotent lookup, the second call still created a
    second Approval row instead of reusing the first — caught by this
    test against a real Postgres, not by inspection."""
    analysis_repo = AnalysisRequestRepository(db_session)
    request = analysis_repo.create(AnalysisRequestCreate(
        source_type="github_repo",
        repo_url="https://github.com/alan/nexus",
        review_request="revisa seguridad",
        post_to_pr=True,
        pr_number=42,
    ))

    state = {"analysis_request_id": request.id, "post_to_pr": True, "final_report": "informe completo"}

    class _Paused(Exception):
        """Stands in for LangGraph's real interrupt mechanism, which
        pauses by raising internally — any exception serves the same
        purpose here: stopping execution exactly at interrupt()."""

    with patch("app.agents.nodes.human_approval_node.interrupt") as mock_interrupt, \
         patch("app.agents.nodes.human_approval_node.SessionLocal", TestSessionLocal):
        mock_interrupt.side_effect = _Paused()
        with pytest.raises(_Paused):
            await human_approval_node(state)

        mock_interrupt.side_effect = None
        mock_interrupt.return_value = "approved"
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