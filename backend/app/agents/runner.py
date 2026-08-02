"""Helpers for invoking the compiled code-review graph from API endpoints.

Both starting a fresh analysis and resuming one paused at
human_approval_node ultimately do the same thing: drive `graph.astream()`
to completion against a `thread_id` derived from the analysis_request_id,
forwarding a translated event over the websocket for every chunk that
matters (see ws_events.build_event). astream() is used instead of a
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

logger = logging.getLogger(__name__)


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
    watching this analysis_request_id."""
    config = _config_for(analysis_request_id)
    async for chunk in graph.astream(run_input, config=config, stream_mode="updates"):
        event = build_event(chunk)
        if event is not None:
            await manager.send_to_analysis_request(analysis_request_id, json.dumps(event))


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
