import pytest

import app.models  # noqa: F401  (registers all models on Base.metadata)
from app.core.config import settings
from app.db.base import Base
from app.integrations.gateway import reset_connector_gateway_for_tests
from app.tests.testdb import engine_test

# Settings that let a connector reach a real platform. The test suite must not
# be able to send a live message, start a real workflow, or call a partner API,
# whatever happens to be in the developer's .env.
#
# This is not hypothetical: once Telegram credentials were added to backend/.env
# so the host-side bot could run, a dry-run test began sending real messages to
# the salon owner. Blanking them here makes "unconfigured" the default and
# forces any test that wants a live-looking connector to say so explicitly.
OUTBOUND_CREDENTIALS = (
    "TELEGRAM_BOT_TOKEN",
    "TELEGRAM_OPERATOR_CHAT_ID",
    "TELEGRAM_OWNER_ID",
    "META_APP_SECRET",
    "META_VERIFY_TOKEN",
    "N8N_WORKFLOW_URL",
    "N8N_WORKFLOW_TOKEN",
    "N8N_WEBHOOK_URL",
    "ALTEGIO_PARTNER_TOKEN",
    "ALTEGIO_LOGIN",
    "ALTEGIO_PASSWORD",
)


@pytest.fixture(autouse=True)
def no_live_channels(monkeypatch):
    """Every test starts with no channel able to reach the outside world."""
    for name in OUTBOUND_CREDENTIALS:
        monkeypatch.setattr(settings, name, "", raising=False)
    reset_connector_gateway_for_tests()
    yield
    reset_connector_gateway_for_tests()


@pytest.fixture(scope="session")
def setup_test_db():
    Base.metadata.create_all(bind=engine_test)
    yield
    Base.metadata.drop_all(bind=engine_test)
