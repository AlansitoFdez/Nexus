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

There's no persisted field yet for "did the PR comment succeed, and
what's its URL" — surfaced only transiently via WebSocket for now.
Noted here as a conscious deferral, not left implicit: a real dashboard
(Fase 4) would likely want this queryable after the fact, not just
live.
"""

import logging

from fastmcp import Client

from app.agents.state import CodeReviewState
from app.api.websocket import manager
from app.config import settings

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

    await manager.send_to_analysis_request(
        state["analysis_request_id"], f"Comentario publicado en el PR: {result.data}"
    )
    return {"node_history": ["post_comment"]}
