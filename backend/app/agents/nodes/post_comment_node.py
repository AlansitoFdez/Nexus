"""post_comment_node: executes the real GitHub write action approved
via human_approval_node — posting the analysis's final_report as a
comment on the target PR (Fase 3.3).

Runs unconditionally right after human_approval_node, and gates itself
internally on post_to_pr, the same idiom human_approval_node itself
uses — not a conditional edge, since this is a data check, not a
routing decision between different node types. post_to_pr is False
here either because the user never asked for this in the first place,
or because a human just rejected it (human_approval_node flips it back
to False on rejection).

Deliberately never writes state["error"] on failure. By the time this
node runs, synthesizer_node has already persisted a final status
("completed" or "completed_with_errors") — the review itself already
succeeded. A failed PR comment is a failure of a downstream
side-action, not of the review; routing to failure_node would
overwrite that already-correct status with "failed", which would
misreport what actually happened (same reasoning already applied to
failed_specialists vs. error in Fase 2.5, extended to a new kind of
partial failure).

Persists the comment's URL on success (pr_comment_url, Fase 4) — closes
what used to be a conscious deferral: this used to be surfaced only
transiently via WebSocket, with nothing queryable after the fact. Still
never touched on failure, and still never routes through
state["error"] — same reasoning as before, this is a side-action outcome,
not the review's own result.
"""

import logging

from fastmcp import Client

from app.agents.state import CodeReviewState
from app.api.websocket import manager
from app.config import settings
from app.database import SessionLocal
from app.repositories.analysis_request_repository import (
    AnalysisRequestRepository,
    AnalysisRequestNotFoundError,
)
from app.schemas.analysis_request import AnalysisRequestUpdate

logger = logging.getLogger("nexus.post_comment")


async def post_comment_node(state: CodeReviewState) -> dict:
    if not state.get("post_to_pr"):
        return {"node_history": ["post_comment"]}

    try:
        async with Client(settings.MCP_SERVER_URL) as client:
            result = await client.call_tool(
                "post_pr_comment",
                {
                    "repo_url": state["repo_url"],
                    "pr_number": state["pr_number"],
                    "comment_body": state["final_report"],
                },
            )
    except Exception as exc:
        logger.error(
            "Failed to post PR comment for analysis_request_id=%s: %s",
            state["analysis_request_id"], exc,
        )
        await manager.send_to_analysis_request(
            state["analysis_request_id"], "No se pudo publicar el comentario en el PR."
        )
        return {"node_history": ["post_comment"]}

    db = SessionLocal()
    try:
        repo = AnalysisRequestRepository(db)
        repo.update(state["analysis_request_id"], AnalysisRequestUpdate(pr_comment_url=result.data))
    except AnalysisRequestNotFoundError:
        # Shouldn't happen by this point in the graph — the row has
        # already been read and written to by every earlier node — but
        # this is a side-action's own persistence, not the review's
        # result, so a miss here still must not touch state["error"].
        logger.error(
            "AnalysisRequest %s vanished before pr_comment_url could be persisted",
            state["analysis_request_id"],
        )
    finally:
        db.close()

    await manager.send_to_analysis_request(
        state["analysis_request_id"], f"Comentario publicado en el PR: {result.data}"
    )
    return {"node_history": ["post_comment"]}
