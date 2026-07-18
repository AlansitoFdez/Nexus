"""Tests for ApprovalRepository database operations."""

import pytest

from app.repositories.approval_repository import ApprovalRepository, TicketNotFoundError
from app.repositories.ticket_repository import TicketRepository
from app.schemas.approval import ApprovalCreate
from app.schemas.ticket import TicketCreate


class FakeTicketRepositoryReturningNone:
    """A fake TicketRepository whose get_by_id always returns None."""

    def get_by_id(self, ticket_id: int) -> None:
        return None


def test_create_persists_a_new_approval_for_an_existing_ticket(db_session):
    """create() should save a new approval when the ticket exists."""
    ticket_repo = TicketRepository(db_session)
    ticket = ticket_repo.create(TicketCreate(original_text="fallo de conexión"))

    approval_repo = ApprovalRepository(db_session, ticket_repo)
    approval = approval_repo.create(ApprovalCreate(ticket_id=ticket.id, proposed_action="reiniciar servicio"))

    assert approval.id is not None
    assert approval.status == "pending"


def test_create_raises_error_when_ticket_does_not_exist(db_session):
    """create() should raise TicketNotFoundError when ticket_id doesn't exist."""
    fake_ticket_repo = FakeTicketRepositoryReturningNone()
    approval_repo = ApprovalRepository(db_session, fake_ticket_repo)

    with pytest.raises(TicketNotFoundError):
        approval_repo.create(ApprovalCreate(ticket_id=999, proposed_action="reiniciar servicio"))


def test_get_by_id_returns_none_when_approval_does_not_exist(db_session):
    """get_by_id() should return None when no approval matches the given ID."""
    approval_repo = ApprovalRepository(db_session, TicketRepository(db_session))

    result = approval_repo.get_by_id(999)

    assert result is None