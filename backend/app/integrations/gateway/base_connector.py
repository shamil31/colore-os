from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class BaseConnector(ABC):
    integration_name: str

    min_interval_seconds: float = 0.0
    """Smallest gap between two calls sharing a rate-limit bucket.

    Taken from the platform's published limit, not chosen. 0 means unlimited.
    Enforced by `ConnectorGateway.dispatch()`.
    """

    @property
    @abstractmethod
    def capabilities(self) -> set[str]:
        """Return capability names supported by this connector."""

    def supports(self, capability: str) -> bool:
        return capability in self.capabilities

    @abstractmethod
    def execute(self, capability: str, *, payload: dict[str, Any] | None = None) -> Any:
        """Execute capability and return either value or awaitable."""

    def is_configured(self) -> bool:
        """True when this connector holds everything it needs to act.

        Defaults to True so connectors that are only constructed when their
        credentials exist keep their current behaviour. Channel connectors,
        which are registered unconditionally so the system runs with no
        credentials at all, override this. See ADR-002 decision 7.
        """
        return True

    def missing_configuration(self) -> tuple[str, ...]:
        """Names of the absent settings. Never their values."""
        return ()

    def rate_limit_key(self, capability: str, payload: dict[str, Any] | None) -> str:
        """Bucket this call shares a limit with.

        One bucket per connector by default. Telegram overrides it because its
        published limit is per chat, not per bot.
        """
        return self.integration_name

    def describe(self) -> dict[str, Any]:
        return {
            "name": self.integration_name,
            "configured": self.is_configured(),
            "capabilities": sorted(self.capabilities),
            "missing_configuration": list(self.missing_configuration()),
        }
