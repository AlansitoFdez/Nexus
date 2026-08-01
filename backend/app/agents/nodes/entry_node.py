"""Entry node: first stop for every analysis request entering the graph.

Deterministic, no LLM involved. Resolves `code_content` from whichever
of the two source paths is active — pasted code is used as-is, a
GitHub repo is read through the `read_repository_files` MCP tool
(pending, Fase 3.1) — updates the request's status to "running", and
notifies the dashboard that processing has begun.

code_content itself is never persisted to the analysis_requests row:
unlike a ticket's short cleaned_text, this can be an entire repo's
worth of content, so it only lives in the graph state for the
duration of this run.
"""

from fastmcp import Client

from app.agents.state import CodeReviewState
from app.database import SessionLocal
from app.repositories.analysis_request_repository import (
    AnalysisRequestRepository,
    AnalysisRequestNotFoundError,
)
from app.schemas.analysis_request import AnalysisRequestUpdate
from app.api.websocket import manager
from app.config import settings


async def entry_node(state: CodeReviewState) -> dict:
    if state["source_type"] == "pasted_code":
        code_content = state["pasted_code"]
    else:
        try:
            async with Client(settings.MCP_SERVER_URL) as client:
                result = await client.call_tool(
                    "read_repository_files", {"repo_url": state["repo_url"]}
                )
            code_content = result.data
        except Exception as exc:
            return {
                "error": f"Failed to read repository {state['repo_url']}: {exc}",
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
    finally:
        db.close()

    await manager.send_to_analysis_request(state["analysis_request_id"], "Procesando análisis...")

    return {
        "code_content": code_content,
        "node_history": ["entry"],
    }