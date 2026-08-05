"""Conditional edges routing between nodes in the code-review graph.

route_after_entry and route_after_router both redirect to failure_node
on error (Fase 2.11) instead of ending the graph silently — this keeps
the AnalysisRequest's status honestly terminal instead of stuck at
"running" forever.

route_after_router implements Fase 2.4's dynamic fan-out: rather than a
fixed edge to one destination, this returns a list of Send objects, one
per specialist the router selected — LangGraph's mechanism for a
branch count that isn't known until the graph actually runs. The
Sends' deltas merge back into CodeReviewState through the reducers
defined in Fase 2.1 (operator.add on findings and node_history).

route_after_synthesizer skips human_approval_node if synthesizer_node
itself failed to persist — nothing meaningful to gate at that point.
"""

from langgraph.types import Send

from app.agents.specialists import SPECIALISTS
from app.agents.state import CodeReviewState

# Derived from SPECIALISTS (Fase 4.1 review) rather than listed by hand —
# every specialist's node name follows the same "{name}_agent" convention
# graph.py registers it under.
AGENT_TO_NODE_NAME = {name: f"{name}_agent" for name in SPECIALISTS}


def route_after_entry(state: CodeReviewState) -> str:
    """Routes to router_node normally, or to failure_node if entry_node
    couldn't resolve code_content."""
    if state.get("error"):
        return "failure_node"
    return "router_node"


def route_after_router(state: CodeReviewState) -> list[Send] | str:
    """Fans out to every specialist the router selected, or routes to
    failure_node if the router itself failed — or if it selected no
    one at all.

    RouterDecision.agents_to_run already requires at least one entry,
    so this should be unreachable in practice — but a Send() list of
    zero destinations would silently end the graph with the
    AnalysisRequest stuck at status="running" forever, so this is
    checked here too, the same "guarantee it where it can't be
    skipped" principle already applied at the schema/database layers.
    """
    if state.get("error"):
        return "failure_node"

    if not state.get("agents_to_run"):
        return "failure_node"

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


def route_after_synthesizer(state: CodeReviewState) -> str:
    """Routes to human_approval_node normally, or to failure_node if
    synthesizer_node itself failed to persist — the same terminal path
    every other pre-fanout failure already uses (route_after_entry,
    route_after_router).

    This used to go straight to END instead (Fase 4.5 review): when
    synthesizer_node's own DB write fails, nothing persists a status at
    all — the row stays at whatever it was before ("running") — so
    ending here directly left it stuck that way forever, exactly the
    failure_node was built to prevent for the other two pre-fanout
    paths.
    """
    if state.get("error"):
        return "failure_node"
    return "human_approval_node"
