"""Ensures all models are imported together so SQLAlchemy can resolve
relationships defined by class name (e.g. relationship("Approval")).
"""

from app.models.approval import Approval
from app.models.analysis_request import AnalysisRequest
from app.models.finding import Finding