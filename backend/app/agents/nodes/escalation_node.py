"""Escalation node: hands off a ticket to the human support team when
the system can't resolve it automatically (low confidence, unknown
issue, or high urgency).

Reuses state["diagnosis"] as the summary sent to the external system
rather than generating a new one via LLM — it already captures the
probable cause and proposed solution, so a second LLM call would just
be paying for a summary of a summary.
"""

from app.agents.state import TicketState
from app.config import settings
from fastmcp import Client


async def escalation_node(state: TicketState) -> dict:
    """Creates an external ticket and notifies the team, given the ticket's diagnosis so far."""
    try:
        async with Client(settings.MCP_SERVER_URL, auth=settings.MCP_API_KEY) as client:
            await client.call_tool(
                "create_external_ticket",
                {"ticket_id": state["ticket_id"], "summary": state["diagnosis"]},
            )
            await client.call_tool(
                "notify_team",
                {"message": state["diagnosis"], "urgency": state["urgency"]},
            )

    except Exception as e:
        return {
            "error": f"Escalation node failed: {e}",
            "node_history": ["escalation"],
        }

    return {
        "escalated": True,
        "node_history": ["escalation"],
    }