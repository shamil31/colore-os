from __future__ import annotations

from app.integrations.gateway.base_connector import BaseConnector


class IntegrationRegistry:
    def __init__(self) -> None:
        self._connectors: dict[str, BaseConnector] = {}

    def register(self, connector: BaseConnector) -> None:
        if connector.integration_name in self._connectors:
            raise ValueError(f"Connector '{connector.integration_name}' is already registered")
        self._connectors[connector.integration_name] = connector

    def get(self, integration_name: str) -> BaseConnector:
        connector = self._connectors.get(integration_name)
        if connector is None:
            raise KeyError(f"Connector '{integration_name}' is not registered")
        return connector

    def list_names(self) -> list[str]:
        return sorted(self._connectors.keys())
