"""Repository for Approval database operations."""

from sqlalchemy.orm import Session

from app.models.approval import Approval
from app.schemas.approval import ApprovalCreate
from app.repositories.ticket_repository import TicketRepository


class TicketNotFoundError(Exception):
    """Raised when an approval is created for a ticket that doesn't exist."""


class ApprovalRepository:
    """Handles persistence operations for Approval entities."""

    def __init__(self, db: Session):
        self.db = db
        self.ticket_repository = TicketRepository(db)

    def create(self, data: ApprovalCreate) -> Approval:
        """Creates and persists a new approval request, defaulting to pending.

        Raises:
            TicketNotFoundError: if data.ticket_id doesn't match any ticket.
        """
        ticket = self.ticket_repository.get_by_id(data.ticket_id)
        if ticket is None:
            raise TicketNotFoundError(f"Ticket {data.ticket_id} does not exist")

        approval = Approval(**data.model_dump())
        self.db.add(approval)
        self.db.commit()
        self.db.refresh(approval)
        return approval

    def get_by_id(self, approval_id: int) -> Approval | None:
        """Retrieves an approval by its ID, or None if it doesn't exist."""
        return self.db.query(Approval).filter(Approval.id == approval_id).first()

    def get_all(self) -> list[Approval]:
        """Retrieves all approvals."""
        return self.db.query(Approval).all()