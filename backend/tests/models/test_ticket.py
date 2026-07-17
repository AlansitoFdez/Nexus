# backend/tests/models/test_ticket.py
"""Tests for the Ticket model and its relationship with Approval."""

from app.models.ticket import Ticket
from app.models.approval import Approval


def test_ticket_approvals_relationship_returns_related_approvals(db_session):
    """ticket.approvals should return all Approval rows linked to that ticket."""
    ticket = Ticket(original_text="el sistema no guarda cambios")
    db_session.add(ticket)
    db_session.commit()

    approval = Approval(ticket_id=ticket.id, proposed_action="reiniciar el servicio")
    db_session.add(approval)
    db_session.commit()

    db_session.refresh(ticket)

    assert len(ticket.approvals) == 1
    assert ticket.approvals[0].proposed_action == "reiniciar el servicio"
    assert ticket.approvals[0].ticket.id == ticket.id


def test_node_history_can_be_updated_and_persisted(db_session):
    """Appending node names to node_history should persist correctly."""
    ticket = Ticket(original_text="fallo al iniciar sesión")
    db_session.add(ticket)
    db_session.commit()

    ticket.node_history = ticket.node_history + ["entry", "classifier"]
    db_session.commit()
    db_session.refresh(ticket)

    assert ticket.node_history == ["entry", "classifier"]