"""Ensures all models are imported together so SQLAlchemy can resolve
relationships defined by class name (e.g. relationship("Approval")).
"""

from app.models.ticket import Ticket
from app.models.knowledge_base import KnowledgeBaseEntry
from app.models.approval import Approval
from app.models.external_ticket import ExternalTicket
from app.models.notification import Notification