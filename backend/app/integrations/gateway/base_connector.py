from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class BaseConnector(ABC):
    integration_name: str

    @property
    @abstractmethod
    def capabilities(self) -> set[str]:
        """Return capability names supported by this connector."""

    def supports(self, capability: str) -> bool:
        return capability in self.capabilities

    @abstractmethod
    def execute(self, capability: str, *, payload: dict[str, Any] | None = None) -> Any:
        """Execute capability and return either value or awaitable."""
