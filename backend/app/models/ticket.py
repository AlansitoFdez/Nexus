from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, JSON
from sqlalchemy.sql import func
from app.database import Base

class Ticket(Base):
    __tablename__ = "tickets"

    id = Column(Integer, primary_key=True, autoincrement=True)
    ticket_original = Column(Text, nullable=False)
    ticket_limpio = Column(Text, nullable=True)
    clasificacion = Column(String(50), nullable=True)
    diagnostico = Column(Text, nullable=True)
    respuesta_propuesta = Column(Text, nullable=True)
    escalado = Column(Boolean, default=False)
    historial_nodos = Column(JSON, default=list)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())