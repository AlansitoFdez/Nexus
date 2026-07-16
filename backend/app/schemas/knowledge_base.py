from datetime import datetime
from pydantic import BaseModel, ConfigDict

class KnowledgeBaseEntryCreate(BaseModel):
    title: str
    content: str
    category: str | None = None


class KnowledgeBaseEntryResponse(BaseModel):
    id: int
    title: str
    content: str
    category: str | None
    created_at: datetime
    updated_at: datetime | None

    model_config = ConfigDict(from_attributes=True)