"""Repository for Ticket database operations.

Encapsulates all direct SQLAlchemy access for Ticket, so endpoints
depend on this abstraction instead of talking to the ORM directly
(Dependency Inversion).
"""

from sqlalchemy.orm import Session

from app.models.ticket import Ticket
from app.schemas.ticket import TicketCreate


class TicketRepository:
    """Handles persistence operations for Ticket entities."""

    def __init__(self, db: Session):
        self.db = db

    def create(self, data: TicketCreate) -> Ticket:
        """Creates and persists a new Ticket from validated input data."""
        ticket = Ticket(original_text=data.original_text)
        self.db.add(ticket)
        self.db.commit()
        self.db.refresh(ticket)
        return ticket

    def get_by_id(self, ticket_id: int) -> Ticket | None:
        """Retrieves a Ticket by its ID, or None if it doesn't exist."""
        return self.db.query(Ticket).filter(Ticket.id == ticket_id).first()

    def get_all(self) -> list[Ticket]:
        """Retrieves all tickets."""
        return self.db.query(Ticket).all()