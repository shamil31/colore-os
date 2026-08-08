"""Process-wide gateway assembly.

Channel connectors are registered **unconditionally**, whether or not their
credentials exist. A connector without settings reports itself unconfigured and
turns calls into recorded dry runs, which is what lets the system start, test
and deploy with no channel credentials at all (ADR-002 decision 7).

OpenAI is the exception: it is registered only when a key is present, because
`LLMService` and the `/ai` endpoints already gate on that key and return 503,
and changing it here would move that behaviour without reason.
"""

from __future__ import annotations

from app.core.config import settings
from app.integrations.gateway.connector_gateway import ConnectorGateway
from app.integrations.gateway.n8n_adapter import N8nAdapter

_gateway_singleton: ConnectorGateway | None = None


def build_connector_gateway() -> ConnectorGateway:
    """Assemble a gateway from current settings. No global state.

    Connectors are imported here rather than at module scope: they import
    `gateway.base_connector`, which imports this package, which imports this
    module. As the composition root, this is the right place to break that
    cycle — at call time, when every module is fully initialised.
    """
    from app.integrations.connectors.altegio_connector import AltegioConnector
    from app.integrations.connectors.meta_connector import MetaConnector
    from app.integrations.connectors.n8n_connector import N8nConnector
    from app.integrations.connectors.openai_connector import OpenAIConnector
    from app.integrations.connectors.telegram_connector import TelegramConnector

    gateway = ConnectorGateway()

    if settings.OPENAI_API_KEY:
        gateway.register(OpenAIConnector(api_key=settings.OPENAI_API_KEY))

    gateway.register(
        TelegramConnector(
            bot_token=settings.TELEGRAM_BOT_TOKEN,
            default_chat_id=settings.TELEGRAM_OPERATOR_CHAT_ID,
        )
    )

    gateway.register(
        MetaConnector(
            app_secret=settings.META_APP_SECRET,
            verify_token=settings.META_VERIFY_TOKEN,
            api_version=settings.META_API_VERSION,
            access_token=settings.META_ACCESS_TOKEN,
            dataset_id=settings.META_DATASET_ID,
        )
    )

    gateway.register(
        N8nConnector(
            workflow_url=settings.N8N_WORKFLOW_URL,
            auth_header=settings.N8N_WORKFLOW_HEADER,
            auth_token=settings.N8N_WORKFLOW_TOKEN,
        )
    )

    gateway.register(
        AltegioConnector(
            base_url=settings.ALTEGIO_BASE_URL,
            partner_token=settings.ALTEGIO_PARTNER_TOKEN,
            login=settings.ALTEGIO_LOGIN,
            password=settings.ALTEGIO_PASSWORD,
            timeout=settings.ALTEGIO_TIMEOUT,
        )
    )

    if settings.N8N_WEBHOOK_URL:
        adapter = N8nAdapter(
            webhook_url=settings.N8N_WEBHOOK_URL,
            timeout=settings.N8N_TIMEOUT,
        )
        adapter.attach(gateway.event_bus)

    return gateway


def get_connector_gateway() -> ConnectorGateway:
    global _gateway_singleton

    if _gateway_singleton is None:
        _gateway_singleton = build_connector_gateway()

    return _gateway_singleton


def reset_connector_gateway_for_tests() -> None:
    global _gateway_singleton
    _gateway_singleton = None
