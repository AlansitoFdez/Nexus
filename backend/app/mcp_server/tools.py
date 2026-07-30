"""MCP tools for Nexus.

Nota post-pivote: solo query_tickets_db sigue viva por ahora porque
depende de TicketRepository, que se mantiene mientras Approval siga
con su FK a tickets.id. search_knowledge_base, create_external_ticket
y notify_team se eliminan por completo: no tienen equivalente en el
dominio de code review, ni por adaptación ni por sustitución directa.
"""

from app.mcp_server.instance import mcp
from app.database import SessionLocal
from app.repositories.ticket_repository import TicketRepository
from typing import Annotated, Literal
from pydantic import Field


@mcp.tool
def query_tickets_db(category: Literal["bug", "usage_question", "configuration", "urgent"], limit: Annotated[int, Field(ge=1, le=20)] = 5,) -> list[dict]:
    """Retrieves previously resolved tickets similar to the current one.

    Use this to check how similar problems were diagnosed and solved in
    the past, before generating a new diagnosis from scratch.

    Args:
        category: The classification category to filter by (e.g. "bug",
            "configuration", "usage_question").
        limit: Maximum number of past tickets to return.

    Returns:
        A list of resolved tickets with their id, classification and
        the solution that was applied.
    """
    db = SessionLocal()
    try:
        repo = TicketRepository(db)
        tickets = repo.get_similar_resolved(category, limit=limit)
        return [
            {"id": t.id, "classification": t.classification, "solution": t.proposed_response}
            for t in tickets
        ]
    finally:
        db.close()