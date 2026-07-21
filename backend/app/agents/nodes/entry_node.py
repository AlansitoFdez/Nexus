"""Entry node: first stop for every ticket entering the graph.

Deterministic, no LLM involved. Cleans the raw text, persists the
result to the ticket row that already exists (created by the
POST /tickets/ endpoint before the graph even starts), and notifies
the dashboard over WebSocket that processing has begun.
"""

from app.agents.state import TicketState
from app.database import SessionLocal
from app.repositories.ticket_repository import TicketRepository
from app.schemas.ticket import TicketUpdate
from app.api.websocket import manager


async def entry_node(state: TicketState) -> dict:
    cleaned_text = state["original_text"].strip()

    db = SessionLocal()
    try:
        repo = TicketRepository(db)
        updated_ticket = repo.update(state["ticket_id"], TicketUpdate(cleaned_text=cleaned_text))
    finally:
        db.close()

    if updated_ticket is None:
        return {
            "error": f"Ticket {state['ticket_id']} not found during entry_node",
            "node_history": ["entry"],
        }

    await manager.send_to_ticket(state["ticket_id"], "Procesando ticket...")

    return {
        "cleaned_text": cleaned_text,
        "node_history": ["entry"],
    }