"""Conditional edge that routes a ticket after classification.

Checks for a classifier failure first; only inspects the classification
itself once it's confirmed there was no error upstream.
"""

from app.agents.state import TicketState


def router_after_classifier(state: TicketState) -> str:
    """Decides which node processes the ticket next, based on its category.

    Returns "error" if the classifier failed, otherwise routes urgent
    tickets straight to escalation, bugs to diagnosis, and both usage
    questions and configuration issues to the knowledge base searcher.
    """
    error = state.get("error")

    if error is None:
        classification = state["classification"]

        if classification == "urgent":
            return "escalation"
        elif classification == "bug":
            return "diagnosis"
        elif classification == "usage_question":
            return "kb_searcher"
        elif classification == "configuration":
            return "kb_searcher"
    else:
        return "error"