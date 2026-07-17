"""Tests for TicketRepository database operations."""

from app.repositories.ticket_repository import TicketRepository
from app.schemas.ticket import TicketCreate


def test_create_persists_a_new_ticket(db_session):
    """create() should save a new ticket with the given original_text."""
    repo = TicketRepository(db_session)

    ticket = repo.create(TicketCreate(original_text="no puedo iniciar sesión"))

    assert ticket.id is not None
    assert ticket.original_text == "no puedo iniciar sesión"


def test_get_by_id_returns_existing_ticket(db_session):
    """get_by_id() should return the matching ticket when it exists."""
    repo = TicketRepository(db_session)
    created = repo.create(TicketCreate(original_text="error 500 al guardar"))

    found = repo.get_by_id(created.id)

    assert found is not None
    assert found.id == created.id


def test_get_by_id_returns_none_when_ticket_does_not_exist(db_session):
    """get_by_id() should return None when no ticket matches the given ID."""
    repo = TicketRepository(db_session)

    found = repo.get_by_id(999)

    assert found is None  


def test_get_all_returns_every_ticket(db_session):
    """get_all() should return all persisted tickets."""
    repo = TicketRepository(db_session)
    repo.create(TicketCreate(original_text="ticket uno"))
    repo.create(TicketCreate(original_text="ticket dos"))

    tickets = repo.get_all()

    assert len(tickets) == 2