"""Database engine, session factory and declarative base for SQLAlchemy models.

All models in app/models/ must inherit from Base so they get registered
in its metadata, which Alembic and the test suite rely on to create
and drop tables.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.config import settings

engine = create_engine(settings.DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    """Yields a database session and ensures it's closed afterwards.

    Used as a FastAPI dependency via Depends(get_db), so each request
    gets its own session without endpoints managing its lifecycle
    directly (Dependency Inversion).
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

from app.models import ticket, knowledge_base, approval