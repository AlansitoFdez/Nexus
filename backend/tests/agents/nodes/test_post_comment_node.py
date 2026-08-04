"""Tests for post_comment_node — the real GitHub write action gated by
human_approval_node (Fase 3.3), now also persisting pr_comment_url on
success (Fase 4).
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from tests.db import TestSessionLocal

from app.agents.nodes.post_comment_node import post_comment_node
from app.config import settings
from app.repositories.analysis_request_repository import AnalysisRequestRepository
from app.schemas.analysis_request import AnalysisRequestCreate


def _state(analysis_request_id: int, **overrides) -> dict:
    base = {
        "analysis_request_id": analysis_request_id,
        "repo_url": "https://github.com/alan/nexus",
        "pr_number": 42,
        "post_to_pr": True,
        "final_report": "## Hallazgos completos\nNo se encontraron hallazgos.",
    }
    base.update(overrides)
    return base


@pytest.mark.asyncio
async def test_no_ops_when_post_to_pr_is_false():
    with patch("app.agents.nodes.post_comment_node.Client") as mock_client_cls:
        result = await post_comment_node(_state(1, post_to_pr=False))

    mock_client_cls.assert_not_called()
    assert result == {"node_history": ["post_comment"]}


@pytest.mark.asyncio
async def test_posts_comment_persists_url_and_notifies_on_success(db_session):
    repo = AnalysisRequestRepository(db_session)
    request = repo.create(AnalysisRequestCreate(
        source_type="github_repo",
        repo_url="https://github.com/alan/nexus",
        review_request="revisa seguridad",
        post_to_pr=True,
        pr_number=42,
    ))

    mock_client = MagicMock()
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=None)
    mock_result = MagicMock()
    mock_result.data = "https://github.com/alan/nexus/pull/42#issuecomment-1"
    mock_client.call_tool = AsyncMock(return_value=mock_result)

    with patch("app.agents.nodes.post_comment_node.Client", return_value=mock_client) as mock_client_cls, \
         patch("app.agents.nodes.post_comment_node.SessionLocal", TestSessionLocal), \
         patch("app.agents.nodes.post_comment_node.manager.send_to_analysis_request", AsyncMock()) as mock_notify:
        result = await post_comment_node(_state(request.id))

    # Regression: same MCP_API_KEY requirement as entry_node — without
    # it, this node can never actually post the approved comment.
    mock_client_cls.assert_called_once_with(settings.MCP_SERVER_URL, auth=settings.MCP_API_KEY)
    mock_client.call_tool.assert_awaited_once_with(
        "post_pr_comment",
        {
            "repo_url": "https://github.com/alan/nexus",
            "pr_number": 42,
            "comment_body": "## Hallazgos completos\nNo se encontraron hallazgos.",
        },
    )
    mock_notify.assert_awaited_once_with(
        request.id, "Comentario publicado en el PR: https://github.com/alan/nexus/pull/42#issuecomment-1"
    )
    assert result == {"node_history": ["post_comment"]}

    db_session.expire_all()
    persisted = repo.get_by_id(request.id)
    assert persisted.pr_comment_url == "https://github.com/alan/nexus/pull/42#issuecomment-1"


@pytest.mark.asyncio
async def test_failure_does_not_persist_url_set_error_but_notifies(db_session):
    """A failed post is a failed side-action, not a failed review —
    synthesizer_node already persisted a successful status by the time
    this node runs, so this must never write state["error"] (which
    would route to failure_node and overwrite that status)."""
    repo = AnalysisRequestRepository(db_session)
    request = repo.create(AnalysisRequestCreate(
        source_type="github_repo",
        repo_url="https://github.com/alan/nexus",
        review_request="revisa seguridad",
        post_to_pr=True,
        pr_number=42,
    ))

    mock_client = MagicMock()
    mock_client.__aenter__ = AsyncMock(side_effect=ConnectionError("no se pudo conectar al MCP server"))
    mock_client.__aexit__ = AsyncMock(return_value=None)

    with patch("app.agents.nodes.post_comment_node.Client", return_value=mock_client), \
         patch("app.agents.nodes.post_comment_node.SessionLocal", TestSessionLocal), \
         patch("app.agents.nodes.post_comment_node.manager.send_to_analysis_request", AsyncMock()) as mock_notify:
        result = await post_comment_node(_state(request.id))

    assert "error" not in result
    assert result == {"node_history": ["post_comment"]}
    mock_notify.assert_awaited_once_with(request.id, "No se pudo publicar el comentario en el PR.")

    db_session.expire_all()
    persisted = repo.get_by_id(request.id)
    assert persisted.pr_comment_url is None
