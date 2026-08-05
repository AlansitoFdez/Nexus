"""Ensures all models are imported together so SQLAlchemy can resolve
relationships defined by class name (e.g. relationship("Approval")).
"""

from app.models.analysis_request import AnalysisRequest  # noqa: F401
from app.models.approval import Approval  # noqa: F401
from app.models.finding import Finding  # noqa: F401
