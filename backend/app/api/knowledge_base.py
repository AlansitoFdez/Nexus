"""REST endpoints for knowledge base entry creation and retrieval."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.repositories.knowledge_base_repository import KnowledgeBaseRepository
from app.schemas.knowledge_base import KnowledgeBaseEntryCreate, KnowledgeBaseEntryResponse

router = APIRouter(prefix="/knowledge-base", tags=["knowledge-base"])


@router.post("/", response_model=KnowledgeBaseEntryResponse, status_code=201)
def create_entry(data: KnowledgeBaseEntryCreate, db: Session = Depends(get_db)):
    """Creates a new knowledge base entry."""
    repo = KnowledgeBaseRepository(db)
    return repo.create(data)


@router.get("/{entry_id}", response_model=KnowledgeBaseEntryResponse)
def get_entry(entry_id: int, db: Session = Depends(get_db)):
    """Retrieves a single entry by its ID, or 404 if it doesn't exist."""
    repo = KnowledgeBaseRepository(db)
    entry = repo.get_by_id(entry_id)

    if entry is None:
        raise HTTPException(status_code=404, detail="Knowledge base entry not found")

    return entry


@router.get("/", response_model=list[KnowledgeBaseEntryResponse])
def list_entries(db: Session = Depends(get_db)):
    """Retrieves all knowledge base entries."""
    repo = KnowledgeBaseRepository(db)
    return repo.get_all()