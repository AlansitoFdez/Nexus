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