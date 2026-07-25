"""Conditional edges routing tickets between nodes based on state.

Kept together in a single file (not split per edge) since all edges
share the same reason to change: graph routing logic, best understood
as a whole rather than scattered across files.
"""

from app.agents.state import TicketState


def route_after_entry(state: TicketState) -> str:
    """Routes to classifier, unless entry_node failed."""
    if state.get("error"):
        return "error"
    return "classifier"


def route_after_classifier(state: TicketState) -> str:
    """Decides which node processes the ticket next, based on its category.

    Returns "error" if the classifier failed, otherwise routes urgent
    tickets straight to escalation, and everything else (bug, usage
    questions, configuration issues) to the knowledge base searcher —
    every category benefits from checking the KB before proceeding.
    """
    error = state.get("error")

    if error is None:
        classification = state["classification"]

        if classification == "urgent":
            return "escalation"
        elif classification == "bug":
            return "kb_searcher"
        elif classification == "usage_question":
            return "kb_searcher"
        elif classification == "configuration":
            return "kb_searcher"
    else:
        return "error"


def route_after_kb_searcher(state: TicketState) -> str:
    """Routes bugs to full diagnosis; usage/configuration go straight to response."""
    if state.get("error"):
        return "error"
    if state["classification"] == "bug":
        return "diagnosis"
    return "response"


def route_after_diagnosis(state: TicketState) -> str:
    """Routes to human approval only when high-impact actions were proposed."""
    if state.get("error"):
        return "error"
    if state["pending_actions"]:
        return "human_approval"
    return "response"


def route_after_human_approval(state: TicketState) -> str:
    """Routes to escalation if rejected, otherwise proceeds to the response."""
    if state.get("escalated"):
        return "escalation"
    return "response"