"""Helpers for invoking the compiled code-review graph from API endpoints.

Both starting a fresh analysis and resuming one paused at
human_approval_node ultimately do the same thing: call `graph.ainvoke()`
against a `thread_id` derived from the analysis_request_id. This module
is the one place that owns that thread_id convention, so the endpoints
that trigger these runs don't each reinvent it.

Both functions are meant to be scheduled via FastAPI's BackgroundTasks:
the HTTP response that triggered them has already gone out by the time
they run, so there's no caller left to propagate an exception to —
unhandled errors are logged instead of raised, so a bug here doesn't
just vanish silently.
"""

import logging

from langgraph.types import Command

logger = logging.getLogger(__name__)


def _config_for(analysis_request_id: int) -> dict:
    """Builds the LangGraph config carrying this analysis's thread_id.

    Using the analysis_request_id itself (not a random UUID, unlike
    test_graph.py's isolation workaround) is what lets a later request —
    the approval decision — find and resume the same run.
    """
    return {"configurable": {"thread_id": str(analysis_request_id)}}


async def run_analysis(graph, initial_state: dict) -> None:
    """Starts a fresh graph run for a newly created AnalysisRequest."""
    analysis_request_id = initial_state["analysis_request_id"]
    try:
        await graph.ainvoke(initial_state, config=_config_for(analysis_request_id))
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
        await graph.ainvoke(
            Command(resume=decision),
            config=_config_for(analysis_request_id),
        )
    except Exception:
        logger.exception(
            "Unhandled error resuming graph for analysis_request_id=%s",
            analysis_request_id,
        )
