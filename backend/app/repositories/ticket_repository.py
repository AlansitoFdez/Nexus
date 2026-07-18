"""Repository for Ticket database operations.

Encapsulates all direct SQLAlchemy access for Ticket, so endpoints
depend on this abstraction instead of talking to the ORM directly
(Dependency Inversion).
"""

from sqlalchemy.orm import Session

from app.models.ticket import Ticket
from app.schemas.ticket import TicketCreate
from app.schemas.ticket import TicketUpdate


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

    def update(self, ticket_id: int, data: TicketUpdate) -> Ticket | None:
        """Applies a partial update to an existing ticket.

        Only fields explicitly provided in `data` are modified; omitted
        fields are left untouched.
        """
        ticket = self.get_by_id(ticket_id)
        if ticket is None:
            return None

        update_fields = data.model_dump(exclude_unset=True)
        for field, value in update_fields.items():
            setattr(ticket, field, value)

        self.db.commit()
        self.db.refresh(ticket)
        return ticket