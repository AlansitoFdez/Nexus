"""Human-in-the-loop node: pauses the graph for approval of high-impact
pending_actions before they execute.

Uses LangGraph's interrupt() to freeze execution here, with the full
graph state checkpointed to Redis (via the AsyncRedisSaver configured
when the graph is compiled in Fase 2.10). The graph resumes later via
Command(resume=...), invoked with the same thread_id (the ticket_id),
from whichever endpoint handles the human's decision.
"""

from langgraph.types import interrupt

from app.agents.state import TicketState


async def human_approval_node(state: TicketState) -> dict:
    """Pauses the graph and waits for a human decision on pending_actions.

    The value passed to interrupt() is what the caller sees while the
    graph is paused (e.g. surfaced to the dashboard). The value returned
    by interrupt() is whatever the human's decision turns out to be,
    once the graph is resumed with Command(resume=...).
    """
    decision = interrupt(
        {
            "cleaned_text": state["cleaned_text"],
            "classification": state["classification"],
            "urgency": state["urgency"],
            "diagnosis": state["diagnosis"],
            "diagnosis_confidence": state["diagnosis_confidence"],
            "pending_actions": state["pending_actions"],
        }
    )

    if decision == "approved":
        return {"node_history": ["human_approval"]}
    else:
        return {
            "escalated": True,
            "node_history": ["human_approval"],
        }