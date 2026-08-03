"""Translates LangGraph stream chunks into JSON-serializable WebSocket
events for the dashboard's live agent trace (Fase 4).

graph.astream(..., stream_mode="updates") yields one chunk per
superstep — {node_name: state_delta, ...} — or {"__interrupt__":
(Interrupt, ...)} when execution pauses at human_approval_node. A
chunk can carry more than one {node_name: delta} pair: that's exactly
what the Send() fan-out (Fase 2.4) means by "specialists run
concurrently" — several can finish in the same superstep. build_event
therefore returns a list of zero, one, or several events, not a single
optional one; runner.py forwards every event in that list over the
websocket. Kept separate from runner.py itself so this stays a pure,
directly-testable function with no async/mocking involved (same
reasoning already applied to the routing functions in edges.py).

Deriving "which specialists just started" from router_node's own delta
(agents_to_run), rather than inventing a separate start signal per
specialist, mirrors the real architecture: the fan-out in route_after_router
(Fase 2.4) *is* what starts them, and it fires right after router_node
completes — there's no earlier moment to report.

A node's delta carrying a truthy "error" key is treated as the general
failure signal, regardless of which node produced it — entry_node and
router_node are today's only sources of a pre-fanout error (Fase 2.11),
but this doesn't hardcode either name, so it keeps working if that ever
changes.
"""

from typing import Any

SPECIALIST_NODES = {
    "security_agent",
    "performance_agent",
    "design_patterns_agent",
    "best_practices_agent",
}

NODE_DISPLAY_NAMES = {
    "entry_node": "entry",
    "synthesizer_node": "synthesizer",
    "human_approval_node": "human_approval",
    "post_comment_node": "post_comment",
    "failure_node": "failure",
}


def build_event(chunk: dict[str, Any]) -> list[dict[str, Any]]:
    """Returns the JSON-serializable events this stream chunk produces —
    zero, one, or several, since a single superstep chunk can carry
    more than one {node_name: delta} pair (see module docstring)."""
    if "__interrupt__" in chunk:
        interrupts = chunk["__interrupt__"]
        if not interrupts:
            return []
        return [{"type": "approval_required", **interrupts[0].value}]

    events: list[dict[str, Any]] = []
    for node_name, delta in chunk.items():
        if delta.get("error"):
            events.append({"type": "run_failed", "node": node_name, "message": delta["error"]})
            continue

        if node_name == "router_node":
            events.append({"type": "specialists_started", "specialists": delta.get("agents_to_run", [])})
            continue

        if node_name in SPECIALIST_NODES:
            specialist = node_name.removesuffix("_agent")
            events.append({
                "type": "specialist_finished",
                "specialist": specialist,
                "findings_count": len(delta.get("findings", [])),
                "failed": specialist in delta.get("failed_specialists", []),
            })
            continue

        if node_name in NODE_DISPLAY_NAMES:
            events.append({"type": "node_finished", "node": NODE_DISPLAY_NAMES[node_name]})

    return events
