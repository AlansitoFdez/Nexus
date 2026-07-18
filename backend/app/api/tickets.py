"""REST endpoints for ticket creation and retrieval."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.repositories.ticket_repository import TicketRepository
from app.schemas.ticket import TicketCreate, TicketResponse, TicketUpdate

router = APIRouter(prefix="/tickets", tags=["tickets"])


@router.post("/", response_model=TicketResponse, status_code=status.HTTP_201_CREATED)
def create_ticket(data: TicketCreate, db: Session = Depends(get_db)):
    """Creates a new ticket from the user's original text."""
    repo = TicketRepository(db)
    return repo.create(data)


@router.get("/{ticket_id}", response_model=TicketResponse)
def get_ticket(ticket_id: int, db: Session = Depends(get_db)):
    """Retrieves a single ticket by its ID, or 404 if it doesn't exist."""
    repo = TicketRepository(db)
    ticket = repo.get_by_id(ticket_id)

    if ticket is None:
        raise HTTPException(status_code=404, detail="Ticket not found")

    return ticket


@router.get("/", response_model=list[TicketResponse])
def list_tickets(db: Session = Depends(get_db)):
    """Retrieves all tickets."""
    repo = TicketRepository(db)
    return repo.get_all()

@router.patch("/{ticket_id}", response_model=TicketResponse)
def update_ticket(ticket_id: int, data: TicketUpdate, db: Session = Depends(get_db)):
    """Partially updates an existing ticket."""
    repo = TicketRepository(db)
    ticket = repo.update(ticket_id, data)

    if ticket is None:
        raise HTTPException(status_code=404, detail="Ticket not found")

    return ticket