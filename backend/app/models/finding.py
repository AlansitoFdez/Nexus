"""SQLAlchemy model for a single finding produced by a specialist agent.

A Finding always belongs to exactly one AnalysisRequest and records
which specialist produced it, so the synthesizer node can group and
prioritize findings by source when building the final report.
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class Finding(Base):
    """A single issue detected by one specialist agent.

    Attributes:
        specialist: Which specialist produced this finding (e.g.
            "security", "performance").
        file_path: The file this finding applies to, or None for a
            finding about the codebase as a whole rather than one file.
        analysis_request: The AnalysisRequest this finding belongs to.
    """

    __tablename__ = "findings"

    id = Column(Integer, primary_key=True, autoincrement=True)
    analysis_request_id = Column(Integer, ForeignKey("analysis_requests.id"), nullable=False, index=True)
    specialist = Column(String(50), nullable=False)
    severity = Column(String(20), nullable=False)
    file_path = Column(String(500), nullable=True)
    description = Column(Text, nullable=False)
    suggestion = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    analysis_request = relationship("AnalysisRequest", back_populates="findings")