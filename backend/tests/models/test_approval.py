"""Tests for the Approval model's default status behavior."""

from app.models.ticket import Ticket
from app.models.approval import Approval


def test_approval_defaults_to_pending_status(db_session):
    """A newly created Approval should default to status='pending', not None."""
    ticket = Ticket(original_text="acceso denegado al panel")
    db_session.add(ticket)
    db_session.commit()

    approval = Approval(ticket_id=ticket.id, proposed_action="restablecer permisos")
    db_session.add(approval)
    db_session.commit()
    db_session.refresh(approval)

    assert approval.status == "pending"
    assert approval.decided_at is None