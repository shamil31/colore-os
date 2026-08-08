"""The outcome of one dispatched capability call.

`ConnectorGateway.execute()` returns the connector's own return value and lets
exceptions through — that is what the import scripts and `LLMService` want.

`ConnectorGateway.dispatch()` returns one of these instead. It is the path the
decision layer uses, where a messaging failure must be recorded rather than
allowed to take down the request that produced the decision.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

STATUS_OK = "ok"
"""Performed against the live platform, and it succeeded."""

STATUS_DRY_RUN = "dry_run"
"""The connector is not configured. Nothing was sent; the request is recorded."""

STATUS_ERROR = "error"
"""Attempted or rejected, and it did not succeed."""


@dataclass(frozen=True)
class ConnectorResult:
    """Three-valued on purpose.

    A boolean would collapse "sent" and "not sent, because there is no token"
    into the same answer. Those two must never look alike in a trace: the first
    means a human was alerted, the second means nobody was.
    """

    connector: str
    capability: str
    status: str
    request: dict[str, Any] = field(default_factory=dict)
    data: Any = None
    error: str | None = None

    @property
    def ok(self) -> bool:
        return self.status != STATUS_ERROR

    @property
    def delivered(self) -> bool:
        """True only when something actually left the building."""
        return self.status == STATUS_OK

    def to_dict(self) -> dict[str, Any]:
        return {
            "connector": self.connector,
            "capability": self.capability,
            "status": self.status,
            "request": self.request,
            "data": self.data,
            "error": self.error,
        }
