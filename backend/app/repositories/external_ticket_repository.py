"""Repository for ExternalTicket database operations (simulated external system)."""

from sqlalchemy.orm import Session

from app.models.external_ticket import ExternalTicket


class ExternalTicketRepository:
    """Handles persistence for the simulated external ticketing system.

    create() is idempotent: calling it twice for the same ticket_id
    returns the existing record instead of creating a duplicate — a
    real external ticketing API would behave the same way.
    """

    def __init__(self, db: Session):
        self.db = db

    def create(self, ticket_id: int, summary: str) -> ExternalTicket:
        existing = self.get_by_ticket_id(ticket_id)
        if existing is not None:
            return existing

        external_ticket = ExternalTicket(ticket_id=ticket_id, summary=summary)
        self.db.add(external_ticket)
        self.db.commit()
        self.db.refresh(external_ticket)
        return external_ticket

    def get_by_ticket_id(self, ticket_id: int) -> ExternalTicket | None:
        return self.db.query(ExternalTicket).filter(ExternalTicket.ticket_id == ticket_id).first()