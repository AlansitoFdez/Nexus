"""Tests for TicketRepository database operations."""

from app.repositories.ticket_repository import TicketRepository, TicketUpdate
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


def test_update_only_modifies_provided_fields(db_session):
    """update() should not overwrite fields that weren't included in the payload."""
    repo = TicketRepository(db_session)
    ticket = repo.create(TicketCreate(original_text="no carga el dashboard"))

    repo.update(ticket.id, TicketUpdate(diagnosis="problema de caché del navegador"))
    updated = repo.update(ticket.id, TicketUpdate(classification="bug"))

    assert updated.classification == "bug"
    assert updated.diagnosis == "problema de caché del navegador"


def test_update_returns_none_when_ticket_does_not_exist(db_session):
    """update() should return None when no ticket matches the given ID."""
    repo = TicketRepository(db_session)

    result = repo.update(999, TicketUpdate(classification="bug"))

    assert result is None


def test_get_similar_resolved_returns_only_non_escalated_tickets_with_response(db_session):
    """get_similar_resolved() should exclude escalated tickets and unresolved ones."""
    repo = TicketRepository(db_session)

    resolved = repo.create(TicketCreate(original_text="no puedo iniciar sesión"))
    repo.update(resolved.id, TicketUpdate(classification="bug", proposed_response="Reinicia el servicio"))

    escalated = repo.create(TicketCreate(original_text="fuga de datos crítica"))
    repo.update(escalated.id, TicketUpdate(classification="bug", escalated=True))

    unresolved = repo.create(TicketCreate(original_text="error intermitente"))
    repo.update(unresolved.id, TicketUpdate(classification="bug"))

    results = repo.get_similar_resolved("bug")

    assert len(results) == 1
    assert results[0].id == resolved.id


def test_get_similar_resolved_filters_by_category(db_session):
    """get_similar_resolved() should only return tickets matching the given category."""
    repo = TicketRepository(db_session)

    bug_ticket = repo.create(TicketCreate(original_text="fallo al guardar"))
    repo.update(bug_ticket.id, TicketUpdate(classification="bug", proposed_response="Solución aplicada"))

    config_ticket = repo.create(TicketCreate(original_text="no encuentro el ajuste"))
    repo.update(config_ticket.id, TicketUpdate(classification="configuration", proposed_response="Ir a ajustes > cuenta"))

    results = repo.get_similar_resolved("bug")

    assert len(results) == 1
    assert results[0].id == bug_ticket.id


def test_get_similar_resolved_respects_limit(db_session):
    """get_similar_resolved() should not return more than `limit` tickets."""
    repo = TicketRepository(db_session)

    for i in range(3):
        t = repo.create(TicketCreate(original_text=f"ticket {i}"))
        repo.update(t.id, TicketUpdate(classification="bug", proposed_response="Resuelto"))

    results = repo.get_similar_resolved("bug", limit=2)

    assert len(results) == 2