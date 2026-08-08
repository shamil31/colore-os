from __future__ import annotations

from typing import Any

import requests

from app.integrations.gateway.event_bus import EventBus, IntegrationEvent


class N8nAdapter:
    def __init__(self, webhook_url: str, *, timeout: int = 5) -> None:
        self.webhook_url = webhook_url.strip()
        self.timeout = timeout
        self._session = requests.Session()

    def attach(self, event_bus: EventBus) -> None:
        event_bus.subscribe("*", self._forward_event)

    def _forward_event(self, event: IntegrationEvent) -> None:
        if not self.webhook_url:
            return

        payload: dict[str, Any] = {
            "event": event.name,
            "source": event.source,
            "payload": event.payload,
            "occurred_at": event.occurred_at.isoformat(),
        }

        # Keep automation telemetry best-effort: integration flow must not fail on webhook outages.
        try:
            self._session.post(self.webhook_url, json=payload, timeout=self.timeout)
        except requests.RequestException:
            return
