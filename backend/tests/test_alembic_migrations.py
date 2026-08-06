"""Tests that Alembic's migrations apply and revert cleanly from
scratch (Fase 5.4).

The rest of the suite never runs Alembic at all — db_session
(conftest.py) builds its schema directly from the SQLAlchemy models via
Base.metadata.create_all()/drop_all(), a deliberate project convention
(see docs/nexus.md's testing section) that never touches Alembic's own
alembic_version tracking table. CI's own "alembic upgrade head" step is
only a smoke test that today's migrations apply from wherever the CI
database happens to be — it doesn't prove downgrade() works, or that
upgrade() works against a database that's genuinely empty. This is the
one place either gets exercised.
"""

from pathlib import Path
from unittest.mock import patch

from alembic.config import Config
from sqlalchemy import text

from alembic import command
from app.config import settings
from app.database import Base
from tests.db import TEST_DATABASE_URL, engine

BACKEND_DIR = Path(__file__).resolve().parent.parent


def _alembic_config() -> Config:
    return Config(str(BACKEND_DIR / "alembic.ini"))


def test_migrations_upgrade_and_downgrade_cleanly():
    """upgrade(head) from a guaranteed-empty database, then
    downgrade(base), then upgrade(head) again — asserting each step
    completes without raising.

    Starts by force-dropping everything via the models directly rather
    than trusting whatever alembic_version state nexus_test happens to
    be in: every other test builds schema through
    Base.metadata.create_all(), never through Alembic, so there's no
    real guarantee this database was ever at a known Alembic revision
    to begin with.

    alembic_version itself is dropped too, explicitly, via raw SQL:
    it isn't part of Base.metadata (it's Alembic's own bookkeeping
    table, not one of the app's models), so Base.metadata.drop_all()
    never touches it. Skipping this step is exactly what broke this
    test the first time around — with alembic_version left claiming
    "already at head" from a previous run while tests/api/'s own
    create_all()/drop_all() fixture had just dropped every real table,
    upgrade("head") silently no-opped (Alembic saw nothing to do) and
    the following downgrade("base") then tried to run real DDL against
    tables that were never actually recreated.

    Safe to share nexus_test with the rest of the suite: pytest runs
    serially, and the finally block always attempts to leave the
    database back at head when this is done, matching the steady state
    every other test's Base.metadata.create_all() already expects
    (a no-op against tables that already exist).

    settings.DATABASE_URL is patched for the duration of every Alembic
    call: alembic/env.py always reads it directly, unconditionally
    overwriting alembic.ini's own placeholder value — verified directly
    against a read-only command (Fase 5.4 review) before ever writing
    this test, since getting this wrong would point a real
    downgrade(base) at the real dev database instead.
    """
    config = _alembic_config()

    with patch.object(settings, "DATABASE_URL", TEST_DATABASE_URL):
        Base.metadata.drop_all(bind=engine)
        with engine.begin() as connection:
            connection.execute(text("DROP TABLE IF EXISTS alembic_version"))
        try:
            command.upgrade(config, "head")
            command.downgrade(config, "base")
            command.upgrade(config, "head")
        finally:
            try:
                command.upgrade(config, "head")
            except Exception:
                pass  # best-effort recovery — the real failure above is what matters
