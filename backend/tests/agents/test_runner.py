"""Tests for runner.py's last-resort failure handling — the safety net
for exceptions that escape run_analysis/resume_analysis entirely,
instead of being caught as a domain error inside a specific node
(entry_node/synthesizer_node/failure_node's own AnalysisRequestNotFoundError
handling covers those separately).
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from tests.db import TestSessionLocal

from app.agents.runner import run_analysis
from app.repositories.analysis_request_repository import AnalysisRequestRepository
from app.schemas.analysis_request import AnalysisRequestCreate, AnalysisRequestUpdate


async def _broken_astream(*args, **kwargs):
    """Models a bug inside the graph's own execution that isn't one of
    the domain errors individual nodes already catch — the exact gap
    the last-resort handler exists to close. The `raise` before the
    unreachable `yield` still makes this an async generator function,
    matching what graph.astream() itself returns."""
    raise RuntimeError("unexpected bug inside the graph")
    yield


@pytest.mark.asyncio
async def test_run_analysis_marks_failed_as_last_resort_on_unhandled_error(db_session):
    repo = AnalysisRequestRepository(db_session)
    request = repo.create(AnalysisRequestCreate(
        source_type="pasted_code", pasted_code="def foo(): pass", review_request="revisa seguridad"
    ))

    fake_graph = MagicMock()
    fake_graph.astream = MagicMock(side_effect=_broken_astream)

    with patch("app.agents.runner.SessionLocal", TestSessionLocal), \
         patch("app.agents.runner.manager.send_to_analysis_request", AsyncMock()) as mock_notify:
        await run_analysis(fake_graph, {"analysis_request_id": request.id})

    db_session.expire_all()
    assert repo.get_by_id(request.id).status == "failed"
    mock_notify.assert_awaited_once()


@pytest.mark.asyncio
async def test_last_resort_handler_does_not_overwrite_a_terminal_status(db_session):
    """If the unhandled error happens after synthesizer_node (or
    post_comment_node) already reached a terminal, successful status,
    forcing "failed" here would misreport a review that actually
    completed — the same principle that already keeps
    failed_specialists/post_comment_node's own error handling from
    overwriting a correct status (Fase 2.5/3.3)."""
    repo = AnalysisRequestRepository(db_session)
    request = repo.create(AnalysisRequestCreate(
        source_type="pasted_code", pasted_code="def foo(): pass", review_request="revisa seguridad"
    ))
    repo.update(request.id, AnalysisRequestUpdate(status="completed"))

    fake_graph = MagicMock()
    fake_graph.astream = MagicMock(side_effect=_broken_astream)

    with patch("app.agents.runner.SessionLocal", TestSessionLocal), \
         patch("app.agents.runner.manager.send_to_analysis_request", AsyncMock()) as mock_notify:
        await run_analysis(fake_graph, {"analysis_request_id": request.id})

    db_session.expire_all()
    assert repo.get_by_id(request.id).status == "completed"
    mock_notify.assert_not_awaited()
