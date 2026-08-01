"""Conditional edges routing between nodes in the code-review graph.

route_after_router implements Fase 2.4's dynamic fan-out: rather than a
fixed edge to one destination (the pattern used for every conditional
edge in the ticket domain), this returns a list of Send objects, one
per specialist the router selected — LangGraph's mechanism for a
branch count that isn't known until the graph actually runs.

The Sends' deltas still merge back into CodeReviewState through the
same reducers defined in Fase 2.1 (operator.add on findings and
node_history) — Send() only decides who gets invoked and with what
payload, not how concurrent results get combined.
"""

from langgraph.graph import END
from langgraph.types import Send

from app.agents.state import CodeReviewState

AGENT_TO_NODE_NAME = {
    "security": "security_agent",
    "performance": "performance_agent",
    "design_patterns": "design_patterns_agent",
    "best_practices": "best_practices_agent",
}


def route_after_router(state: CodeReviewState) -> list[Send] | str:
    """Fans out to every specialist the router selected, or ends the
    graph if the router itself failed.

    Each Send carries only what a specialist node needs (code_content,
    review_request, analysis_request_id) rather than the full shared
    state, keeping each specialist's input surface minimal.
    """
    if state.get("error"):
        return END

    return [
        Send(
            AGENT_TO_NODE_NAME[agent_name],
            {
                "code_content": state["code_content"],
                "review_request": state["review_request"],
                "analysis_request_id": state["analysis_request_id"],
            },
        )
        for agent_name in state["agents_to_run"]
    ]