"""Entry node: first stop for every analysis request entering the graph.

Deterministic, no LLM involved. Resolves `code_content` from whichever
of the two source paths is active — pasted code is used as-is, a
GitHub repo is read through the `read_repository_files` MCP tool —
updates the request's status to "running", and notifies the dashboard
that processing has begun.

code_content itself is never persisted to the analysis_requests row:
unlike a ticket's short cleaned_text, this can be an entire repo's
worth of content, so it only lives in the graph state for the
duration of this run.
"""

import logging

from fastmcp import Client

from app.agents.state import CodeReviewState
from app.api.websocket import manager
from app.config import settings
from app.database import SessionLocal
from app.repositories.analysis_request_repository import (
    AnalysisRequestNotFoundError,
    AnalysisRequestRepository,
)
from app.schemas.analysis_request import AnalysisRequestUpdate

logger = logging.getLogger(__name__)


async def entry_node(state: CodeReviewState) -> dict:
    if state["source_type"] == "pasted_code":
        code_content = state["pasted_code"]
    else:
        try:
            async with Client(settings.MCP_SERVER_URL, auth=settings.MCP_API_KEY) as client:
                result = await client.call_tool(
                    "read_repository_files", {"repo_url": state["repo_url"]}
                )
            code_content = result.data
        except Exception as exc:
            # The raw exception text isn't safe to hand to the client —
            # ws_events.build_event forwards state["error"] verbatim as a
            # "run_failed" event over the websocket, and unlike
            # GitHubAPIError's own deliberately clean messages, this
            # branch also catches things like a raw connection error,
            # which could carry internal detail (host, ports, headers).
            # The repo_url itself is safe to keep: it's the user's own input.
            logger.error("Failed to read repository %s: %s", state["repo_url"], exc)
            return {
                "error": f"Failed to read repository {state['repo_url']}",
                "node_history": ["entry"],
            }

    db = SessionLocal()
    try:
        repo = AnalysisRequestRepository(db)
        repo.update(state["analysis_request_id"], AnalysisRequestUpdate(status="running"))
    except AnalysisRequestNotFoundError:
        return {
            "error": f"AnalysisRequest {state['analysis_request_id']} not found during entry_node",
            "node_history": ["entry"],
        }
    except Exception as exc:
        # Anything else the database can throw here (connection drop,
        # a truncated column, ...) must still land in state["error"] —
        # AnalysisRequestNotFoundError alone doesn't cover it, and an
        # uncaught exception would propagate out of this node with
        # nothing left to mark the AnalysisRequest as failed. Same
        # sanitization reasoning as above: log the real exception,
        # keep the client-facing message free of internal detail.
        logger.error(
            "Failed to update AnalysisRequest %s status during entry_node: %s",
            state["analysis_request_id"], exc,
        )
        return {
            "error": (
                f"Failed to update AnalysisRequest {state['analysis_request_id']} "
                f"status during entry_node"
            ),
            "node_history": ["entry"],
        }
    finally:
        db.close()

    await manager.send_to_analysis_request(state["analysis_request_id"], "Procesando análisis...")

    return {
        "code_content": code_content,
        "node_history": ["entry"],
    }
