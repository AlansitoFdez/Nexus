"""Database engine, session factory and declarative base for SQLAlchemy models.

All models in app/models/ must inherit from Base so they get registered
in its metadata, which Alembic and the test suite rely on to create
and drop tables.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

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

# Imported here, not at the top: app/models/*.py import Base from this
# very module, so importing them before Base exists (line 17) would
# fail with a circular import. This is also the real registration
# point for every model on Base.metadata — verified directly (Fase 5.3
# review): alembic/env.py and main.py used to also import these model
# classes by name, but neither needed to, since importing Base from
# here already triggers this exact line and registers everything.
from app.models import analysis_request, approval, finding  # noqa: E402,F401
