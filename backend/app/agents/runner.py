"""Helpers for invoking the compiled code-review graph from API endpoints.

Both starting a fresh analysis and resuming one paused at
human_approval_node ultimately do the same thing: drive `graph.astream()`
to completion against a `thread_id` derived from the analysis_request_id,
forwarding every translated event over the websocket for each chunk
that matters — a single chunk can translate to more than one event,
since the Send() fan-out (Fase 2.4) can finish several specialists in
the same superstep (see ws_events.build_event). astream() is used instead of a
plain ainvoke() specifically so the dashboard's live agent trace
(Fase 4) has something to render as the run progresses — iterating it
to exhaustion has the same end-state effects ainvoke() would (every
node still runs exactly once), the only difference is we also get to
see each node finish along the way.

Both functions are meant to be scheduled via FastAPI's BackgroundTasks:
the HTTP response that triggered them has already gone out by the time
they run, so there's no caller left to propagate an exception to —
unhandled errors are logged instead of raised, so a bug here doesn't
just vanish silently.
"""

import json
import logging

from langgraph.types import Command

from app.agents.ws_events import build_event
from app.api.websocket import manager
from app.database import SessionLocal
from app.logging_config import analysis_request_id_var
from app.repositories.analysis_request_repository import AnalysisRequestRepository
from app.schemas.analysis_request import AnalysisRequestUpdate

logger = logging.getLogger(__name__)

NON_TERMINAL_STATUSES = ("pending", "running")


def _config_for(analysis_request_id: int) -> dict:
    """Builds the LangGraph config carrying this analysis's thread_id.

    Using the analysis_request_id itself (not a random UUID, unlike
    test_graph.py's isolation workaround) is what lets a later request —
    the approval decision — find and resume the same run.
    """
    return {"configurable": {"thread_id": str(analysis_request_id)}}


async def _stream_and_broadcast(graph, analysis_request_id: int, run_input) -> None:
    """Shared core of run_analysis/resume_analysis: drives the graph and
    relays each meaningful step to whichever dashboard clients are
    watching this analysis_request_id.

    Sets analysis_request_id_var (Fase 5.1) before the graph starts
    running, not inside each individual node: this is the one choke
    point both run_analysis and resume_analysis funnel through, and
    every node's own logging picks the value up automatically for the
    rest of this run — including inside the Send() fan-out, since a new
    asyncio Task copies the current context at creation time.
    """
    analysis_request_id_var.set(analysis_request_id)
    config = _config_for(analysis_request_id)
    async for chunk in graph.astream(run_input, config=config, stream_mode="updates"):
        for event in build_event(chunk):
            await manager.send_to_analysis_request(analysis_request_id, json.dumps(event))


async def _mark_failed_as_last_resort(analysis_request_id: int) -> None:
    """Safety net for exceptions that escape _stream_and_broadcast
    entirely — a bug that isn't one of the domain errors individual
    nodes already catch (entry_node/synthesizer_node/failure_node only
    handle AnalysisRequestNotFoundError plus a few known failure modes).
    Without this, that kind of unexpected error leaves the
    AnalysisRequest stuck at "running" forever with nothing telling the
    dashboard why.

    Only overwrites the status when it's still "pending"/"running": if
    the exception happened after synthesizer_node (or post_comment_node)
    already reached a terminal, successful status, forcing "failed"
    here would misreport a review that actually completed — the same
    principle that already keeps failed_specialists and post_comment_node's
    own error handling from overwriting a correct status (Fase 2.5/3.3).

    Wrapped in its own try/except: this is the last line of defense, so
    a failure here must not raise either — it would otherwise escape
    into the BackgroundTasks machinery with no caller left to catch it.
    """
    try:
        should_notify = False
        db = SessionLocal()
        try:
            repo = AnalysisRequestRepository(db)
            analysis_request = repo.get_by_id(analysis_request_id)
            if analysis_request is not None and analysis_request.status in NON_TERMINAL_STATUSES:
                repo.update(analysis_request_id, AnalysisRequestUpdate(status="failed"))
                should_notify = True
        finally:
            db.close()

        if should_notify:
            event = {"type": "run_failed", "node": "runner", "message": "Unhandled internal error"}
            await manager.send_to_analysis_request(analysis_request_id, json.dumps(event))
    except Exception:
        logger.exception(
            "Last-resort failure handler itself failed for analysis_request_id=%s",
            analysis_request_id,
        )


async def run_analysis(graph, initial_state: dict) -> None:
    """Starts a fresh graph run for a newly created AnalysisRequest."""
    analysis_request_id = initial_state["analysis_request_id"]
    try:
        await _stream_and_broadcast(graph, analysis_request_id, initial_state)
    except Exception:
        logger.exception(
            "Unhandled error running graph for analysis_request_id=%s",
            analysis_request_id,
        )
        await _mark_failed_as_last_resort(analysis_request_id)


async def resume_analysis(graph, analysis_request_id: int, decision: str) -> None:
    """Resumes a graph paused at human_approval_node with the human's decision.

    human_approval_node itself is what persists the Approval row's final
    status once it wakes up (Fase 2.10) — this function's only job is
    handing the decision to the paused thread.
    """
    try:
        await _stream_and_broadcast(graph, analysis_request_id, Command(resume=decision))
    except Exception:
        logger.exception(
            "Unhandled error resuming graph for analysis_request_id=%s",
            analysis_request_id,
        )
        await _mark_failed_as_last_resort(analysis_request_id)
