"""Tests for ExternalTicketRepository database operations."""

from app.repositories.external_ticket_repository import ExternalTicketRepository
from app.repositories.ticket_repository import TicketRepository
from app.schemas.ticket import TicketCreate


def test_create_persists_a_new_external_ticket(db_session):
    """create() should save a new external ticket for a given ticket_id."""
    ticket = TicketRepository(db_session).create(TicketCreate(original_text="fallo crítico"))
    repo = ExternalTicketRepository(db_session)

    external = repo.create(ticket.id, "Resumen del diagnóstico")

    assert external.id is not None
    assert external.status == "created"


def test_create_is_idempotent_for_the_same_ticket(db_session):
    """Calling create() twice for the same ticket_id should not duplicate the row."""
    ticket = TicketRepository(db_session).create(TicketCreate(original_text="fallo crítico"))
    repo = ExternalTicketRepository(db_session)

    first = repo.create(ticket.id, "Resumen inicial")
    second = repo.create(ticket.id, "Resumen distinto, no debería importar")

    assert first.id == second.id
    assert second.summary == "Resumen inicial"


def test_get_by_ticket_id_returns_none_when_not_found(db_session):
    """get_by_ticket_id() should return None when no external ticket exists yet."""
    repo = ExternalTicketRepository(db_session)

    assert repo.get_by_ticket_id(999) is None