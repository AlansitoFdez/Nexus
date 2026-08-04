"""Shared test-database engine and session factory (Fase 5.3 review).

TEST_DATABASE_URL/engine/TestSessionLocal used to be redefined
identically in ~10 files across the suite — this is the one place that
changes now if the test database's connection details ever do.

Also fixes a smaller inefficiency: engine (and the connection pool it
owns) is created once here, at import time, and reused by every test —
not rebuilt per test the way the old db_session fixture in conftest.py
used to (a fresh create_engine() call on every single test).
Base.metadata.create_all()/drop_all() still run per test for isolation;
only the engine itself is shared.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

TEST_DATABASE_URL = "postgresql://user:password@localhost:5434/nexus_test"

engine = create_engine(TEST_DATABASE_URL)
TestSessionLocal = sessionmaker(bind=engine)
