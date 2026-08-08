from __future__ import annotations

import logging
from inspect import isawaitable
from typing import Any

from app.integrations.gateway.base_connector import BaseConnector
from app.integrations.gateway.capability_registry import CapabilityRegistry
from app.integrations.gateway.event_bus import EventBus, IntegrationEvent
from app.integrations.gateway.integration_registry import IntegrationRegistry
from app.integrations.gateway.rate_limit import RateLimiter, RateLimitExceeded
from app.integrations.gateway.results import (
    STATUS_DRY_RUN,
    STATUS_ERROR,
    STATUS_OK,
    ConnectorResult,
)

logger = logging.getLogger("colore.gateway")


class ConnectorGateway:
    """Single entry point for every outbound integration call.

    Two ways in, for two kinds of caller:

    `execute()` returns the connector's own value and lets exceptions through.
    Import scripts and `LLMService` use it: they name one platform on purpose
    and want the typed result.

    `dispatch()` takes a vendor-neutral capability, resolves a provider,
    enforces the platform's rate limit, and always returns a `ConnectorResult`.
    The decision layer uses it. It never raises, because a failure to notify
    must not take down the request that decided to notify.
    """

    def __init__(
        self,
        *,
        integration_registry: IntegrationRegistry | None = None,
        capability_registry: CapabilityRegistry | None = None,
        event_bus: EventBus | None = None,
        rate_limiter: RateLimiter | None = None,
    ) -> None:
        self.integration_registry = integration_registry or IntegrationRegistry()
        self.capability_registry = capability_registry or CapabilityRegistry()
        self.event_bus = event_bus or EventBus()
        self.rate_limiter = rate_limiter or RateLimiter()

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

    # ------------------------------------------------------------------ direct

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

    # -------------------------------------------------------------- capability

    def providers_for(self, capability: str) -> list[BaseConnector]:
        """Every registered connector offering this capability."""
        return [
            self.integration_registry.get(name)
            for name in self.capability_registry.get_integrations(capability)
        ]

    def resolve(self, capability: str, *, prefer: str | None = None) -> BaseConnector | None:
        """Pick the connector that should serve this capability.

        A configured provider always wins over an unconfigured one. When none
        is configured the first provider is still returned, so the call becomes
        a recorded dry run rather than a missing-integration error.
        """
        providers = self.providers_for(capability)
        if not providers:
            return None

        if prefer is not None:
            for connector in providers:
                if connector.integration_name == prefer:
                    return connector
            return None

        for connector in providers:
            if connector.is_configured():
                return connector

        return providers[0]

    def dispatch(
        self,
        capability: str,
        payload: dict[str, Any] | None = None,
        *,
        prefer: str | None = None,
    ) -> ConnectorResult:
        """Guarded capability call. Never raises."""
        request = payload or {}

        connector = self.resolve(capability, prefer=prefer)
        if connector is None:
            known = self.capability_registry.get_integrations(capability)
            detail = (
                f"'{prefer}' does not provide it (providers: {known or 'none'})"
                if prefer is not None
                else "no connector provides it"
            )
            return ConnectorResult(
                connector=prefer or "-",
                capability=capability,
                status=STATUS_ERROR,
                request=request,
                error=f"capability '{capability}': {detail}",
            )

        if not connector.is_configured():
            missing = ", ".join(connector.missing_configuration()) or "credentials"
            logger.info(
                "gateway: dry run %s via %s (missing: %s)",
                capability,
                connector.integration_name,
                missing,
            )
            return self._publish(
                ConnectorResult(
                    connector=connector.integration_name,
                    capability=capability,
                    status=STATUS_DRY_RUN,
                    request=request,
                    data={"reason": f"not configured: {missing}"},
                )
            )

        try:
            self.rate_limiter.acquire(
                connector.rate_limit_key(capability, request),
                connector.min_interval_seconds,
            )
        except RateLimitExceeded as exc:
            return self._publish(
                ConnectorResult(
                    connector=connector.integration_name,
                    capability=capability,
                    status=STATUS_ERROR,
                    request=request,
                    error=f"rate limited: {exc}",
                )
            )

        try:
            data = connector.execute(capability, payload=request)
        except Exception as exc:  # noqa: BLE001 — the point is that nothing escapes
            logger.exception("gateway: %s failed on %s", connector.integration_name, capability)
            return self._publish(
                ConnectorResult(
                    connector=connector.integration_name,
                    capability=capability,
                    status=STATUS_ERROR,
                    request=request,
                    error=f"{type(exc).__name__}: {exc}",
                )
            )

        if isawaitable(data):
            # Nothing on the decision path is async today. Rather than leak an
            # un-awaited coroutine into a trace, say so.
            data.close()
            return self._publish(
                ConnectorResult(
                    connector=connector.integration_name,
                    capability=capability,
                    status=STATUS_ERROR,
                    request=request,
                    error=(
                        f"{connector.integration_name}.{capability} is asynchronous — "
                        "call execute_async(), not dispatch()"
                    ),
                )
            )

        return self._publish(
            ConnectorResult(
                connector=connector.integration_name,
                capability=capability,
                status=STATUS_OK,
                request=request,
                data=data,
            )
        )

    # ------------------------------------------------------------------ status

    def status(self) -> dict[str, Any]:
        """What is registered, what is configured, and who serves what.

        Read by the `/growth/integrations` endpoint and by the operator when a
        channel silently stops delivering.
        """
        integrations = [
            self.integration_registry.get(name).describe()
            for name in self.integration_registry.list_names()
        ]

        capabilities: dict[str, Any] = {}
        for capability in self.capability_registry.list_capabilities():
            providers = self.providers_for(capability)
            capabilities[capability] = {
                "providers": [c.integration_name for c in providers],
                "configured_providers": [
                    c.integration_name for c in providers if c.is_configured()
                ],
            }

        return {"integrations": integrations, "capabilities": capabilities}

    # ----------------------------------------------------------------- private

    def _publish(self, result: ConnectorResult) -> ConnectorResult:
        self.event_bus.publish(
            IntegrationEvent(
                name=f"integration.dispatch_{result.status}",
                source=result.connector,
                payload={"capability": result.capability, "error": result.error},
            )
        )
        return result

    def _resolve_connector(self, *, integration_name: str, capability: str) -> BaseConnector:
        if not self.capability_registry.supports(integration_name, capability):
            supported = self.capability_registry.get_integrations(capability)
            raise ValueError(
                f"Capability '{capability}' is not supported by '{integration_name}'. "
                f"Supported integrations: {supported}"
            )
        return self.integration_registry.get(integration_name)
