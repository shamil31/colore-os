from __future__ import annotations


class CapabilityRegistry:
    def __init__(self) -> None:
        self._capabilities: dict[str, set[str]] = {}

    def register(self, integration_name: str, capability: str) -> None:
        self._capabilities.setdefault(capability, set()).add(integration_name)

    def get_integrations(self, capability: str) -> list[str]:
        names = self._capabilities.get(capability, set())
        return sorted(names)

    def supports(self, integration_name: str, capability: str) -> bool:
        return integration_name in self._capabilities.get(capability, set())
