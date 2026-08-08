from __future__ import annotations

from inspect import isawaitable
from typing import Any

from app.integrations.gateway.base_connector import BaseConnector
from app.integrations.gateway.capability_registry import CapabilityRegistry
from app.integrations.gateway.event_bus import EventBus, IntegrationEvent
from app.integrations.gateway.integration_registry import IntegrationRegistry


class ConnectorGateway:
    def __init__(
        self,
        *,
        integration_registry: IntegrationRegistry | None = None,
        capability_registry: CapabilityRegistry | None = None,
        event_bus: EventBus | None = None,
    ) -> None:
        self.integration_registry = integration_registry or IntegrationRegistry()
        self.capability_registry = capability_registry or CapabilityRegistry()
        self.event_bus = event_bus or EventBus()

    def register(self, connector: BaseConnector) -> None:
        self.integration_registry.register(connector)

        for capability in connector.capabilities:
            self.capability_registry.register(connector.integration_name, capability)

        self.event_bus.publish(
            IntegrationEvent(
                name="integration.registered",
                source=connector.integration_name,
                payload={"capabilities": sorted(connector.capabilities)},
            )
        )

    def execute(
        self,
        integration_name: str,
        capability: str,
        *,
        payload: dict[str, Any] | None = None,
    ) -> Any:
        connector = self._resolve_connector(integration_name=integration_name, capability=capability)

        self.event_bus.publish(
            IntegrationEvent(
                name="integration.request",
                source=integration_name,
                payload={"capability": capability},
            )
        )

        try:
            result = connector.execute(capability, payload=payload)
        except Exception as exc:  # noqa: BLE001
            self.event_bus.publish(
                IntegrationEvent(
                    name="integration.request_failed",
                    source=integration_name,
                    payload={"capability": capability, "error": str(exc)},
                )
            )
            raise

        self.event_bus.publish(
            IntegrationEvent(
                name="integration.request_succeeded",
                source=integration_name,
                payload={"capability": capability},
            )
        )
        return result

    async def execute_async(
        self,
        integration_name: str,
        capability: str,
        *,
        payload: dict[str, Any] | None = None,
    ) -> Any:
        result = self.execute(integration_name, capability, payload=payload)
        if isawaitable(result):
            return await result
        return result

    def _resolve_connector(self, *, integration_name: str, capability: str) -> BaseConnector:
        if not self.capability_registry.supports(integration_name, capability):
            supported = self.capability_registry.get_integrations(capability)
            raise ValueError(
                f"Capability '{capability}' is not supported by '{integration_name}'. "
                f"Supported integrations: {supported}"
            )
        return self.integration_registry.get(integration_name)
