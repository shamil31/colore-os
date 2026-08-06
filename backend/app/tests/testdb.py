"""Test database wiring.

Tests must never touch the working database. The engine here uses
TEST_DATABASE_URL, and falls back to a temporary SQLite file when it is
not set.
"""

import os
import tempfile

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.db.database import get_db
from app.main import app

if settings.TEST_DATABASE_URL:
    TEST_DATABASE_URL = settings.TEST_DATABASE_URL
    CONNECT_ARGS = {}
else:
    _fd, _path = tempfile.mkstemp(prefix="colore_test_", suffix=".db")
    os.close(_fd)
    TEST_DATABASE_URL = f"sqlite:///{_path}"
    CONNECT_ARGS = {"check_same_thread": False}

if TEST_DATABASE_URL == settings.DATABASE_URL:
    raise RuntimeError(
        "TEST_DATABASE_URL must not point at the working database "
        "(DATABASE_URL). Tests drop tables on teardown."
    )

engine_test = create_engine(TEST_DATABASE_URL, connect_args=CONNECT_ARGS)
TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine_test,
)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)
