from __future__ import annotations

from app.core.config import settings
from app.integrations.connectors.openai_connector import OpenAIConnector
from app.integrations.gateway.connector_gateway import ConnectorGateway
from app.integrations.gateway.n8n_adapter import N8nAdapter

_gateway_singleton: ConnectorGateway | None = None


def get_connector_gateway() -> ConnectorGateway:
    global _gateway_singleton

    if _gateway_singleton is None:
        _gateway_singleton = ConnectorGateway()

        if settings.OPENAI_API_KEY:
            _gateway_singleton.register(OpenAIConnector(api_key=settings.OPENAI_API_KEY))

        if settings.N8N_WEBHOOK_URL:
            adapter = N8nAdapter(
                webhook_url=settings.N8N_WEBHOOK_URL,
                timeout=settings.N8N_TIMEOUT,
            )
            adapter.attach(_gateway_singleton.event_bus)

    return _gateway_singleton


def reset_connector_gateway_for_tests() -> None:
    global _gateway_singleton
    _gateway_singleton = None
