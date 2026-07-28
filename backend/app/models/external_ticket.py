"""SQLAlchemy model for the simulated external ticketing system.

Fase 3.3: no existe un sistema externo real todavía, así que esta tabla
juega ese rol. Una integración real sustituiría el `create()` del
repository por una llamada HTTP, sin que ningún otro código que hable
con este repository tuviera que cambiar.
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.sql import func
import sqlalchemy as sa
from app.database import Base


class ExternalTicket(Base):
    """A ticket record in the simulated external support system."""

    __tablename__ = "external_tickets"

    id = Column(Integer, primary_key=True, autoincrement=True)
    ticket_id = Column(Integer, ForeignKey("tickets.id"), nullable=False, unique=True, index=True)
    summary = Column(Text, nullable=False)
    status = Column(String(20), server_default=sa.text("'created'"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)