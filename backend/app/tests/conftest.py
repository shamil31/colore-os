import pytest

import app.models  # noqa: F401  (registers all models on Base.metadata)
from app.db.base import Base
from app.tests.testdb import engine_test


@pytest.fixture(scope="session")
def setup_test_db():
    Base.metadata.create_all(bind=engine_test)
    yield
    Base.metadata.drop_all(bind=engine_test)
