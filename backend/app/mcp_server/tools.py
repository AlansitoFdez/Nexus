"""Placeholder MCP tools for Nexus.

Fase 1.4: estas tools devuelven datos de prueba fijos, sin tocar la
base de datos real todavía. El objetivo de esta fase es verificar que
el servidor MCP responde correctamente al protocolo, no la lógica de
negocio real (eso llega en la Fase 3).
"""

from app.mcp_server.instance import mcp
from app.database import SessionLocal
from app.mcp_server.instance import mcp
from app.repositories.knowledge_base_repository import KnowledgeBaseRepository
from app.repositories.ticket_repository import TicketRepository
from app.repositories.external_ticket_repository import ExternalTicketRepository
import logging
from app.repositories.notification_repository import NotificationRepository
from typing import Annotated, Literal
from pydantic import Field

logger = logging.getLogger("nexus.notifications")


@mcp.tool
def search_knowledge_base(query: str, limit: Annotated[int, Field(ge=1, le=20)] = 5,) -> list[dict]:
    """Searches the knowledge base for entries relevant to a support query.

    Use this when the ticket describes a problem that might already have
    a documented solution (how-to questions, known configuration issues).

    Args:
        query: The text to search for, typically the ticket's content.
        limit: Maximum number of results to return.

    Returns:
        A list of matching entries ranked by relevance_score.
    """
    db = SessionLocal()
    try:
        repo = KnowledgeBaseRepository(db)
        return repo.search(query, limit=limit)
    finally:
        db.close()


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


@mcp.tool
def create_external_ticket(ticket_id: int, summary: str) -> dict:
    """Creates a ticket in the external ticketing system used by the support team.

    Use this only when a ticket must be escalated to a human because the
    system could not resolve it automatically. Idempotent: calling this
    again for a ticket_id that already has an external ticket returns
    the existing one instead of creating a duplicate.

    Args:
        ticket_id: The internal Nexus ticket ID being escalated.
        summary: A short diagnostic summary for the human who receives it.

    Returns:
        A dict with the external system's ticket ID and its status.
    """
    db = SessionLocal()
    try:
        repo = ExternalTicketRepository(db)
        external_ticket = repo.create(ticket_id, summary)
        return {
            "external_ticket_id": f"EXT-{external_ticket.id:04d}",
            "status": external_ticket.status,
        }
    finally:
        db.close()


@mcp.tool
def notify_team(message: str, urgency: Literal["low", "normal", "high"] = "normal") -> dict:
    """Sends a notification to the human support team.

    Use this alongside create_external_ticket when escalating, or on its
    own for lower-impact alerts that don't require a full ticket.

    Args:
        message: The notification content.
        urgency: One of "low", "normal", "high". Defaults to "normal".

    Returns:
        A dict confirming whether the notification was sent and via
        which channel.
    """
    logger.info("Notification [%s]: %s", urgency, message)

    db = SessionLocal()
    try:
        repo = NotificationRepository(db)
        repo.create(message=message, urgency=urgency, channel="log")
        return {"notified": True, "channel": "log"}
    finally:
        db.close()