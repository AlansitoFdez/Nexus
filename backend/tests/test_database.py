"""Tests for the database engine and session configuration."""

from app.models.ticket import Ticket


def test_can_create_and_query_a_ticket(db_session):
    """A Ticket created through the session should be retrievable afterwards."""
    ticket = Ticket(original_text="mi impresora no imprime")
    db_session.add(ticket)
    db_session.commit()

    result = db_session.query(Ticket).filter(Ticket.original_text == "mi impresora no imprime").first()

    assert result is not None
    assert result.id is not None
    assert result.escalated is False
    assert result.node_history == []