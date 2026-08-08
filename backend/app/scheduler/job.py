"""What a scheduled integration job is.

The scheduler knows nothing about Meta, Altegio, or any vendor. It knows how to
run something on an interval, record what happened, and keep one failure from
stopping the rest. A job supplies the behaviour; adding an integration is
registering a job, not editing the scheduler.

Four execution modes, because "run it" is not one question:

- `interval` — the scheduler decided it was due
- `manual`   — a human asked for it now, ignoring the interval
- `dry_run`  — work out what would happen and change nothing
- `test`     — really call the vendor, but in whatever sandbox it offers

`dry_run` and `test` are different on purpose. A dry run never leaves the
building; a test run does, and that distinction is the difference between
"I think this works" and "the vendor confirmed it".
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

MODE_INTERVAL = "interval"
MODE_MANUAL = "manual"
MODE_DRY_RUN = "dry_run"
MODE_TEST = "test"

ALL_MODES = (MODE_INTERVAL, MODE_MANUAL, MODE_DRY_RUN, MODE_TEST)

STATUS_SUCCESS = "success"
STATUS_FAILED = "failed"
STATUS_SKIPPED = "skipped"
"""The job ran and correctly decided there was nothing to do, or that it could
not act — not configured, for instance. Distinct from failure: a skipped job is
healthy."""


@dataclass
class JobContext:
    session: Any
    mode: str = MODE_INTERVAL
    now: datetime | None = None

    @property
    def dry_run(self) -> bool:
        return self.mode == MODE_DRY_RUN

    @property
    def test(self) -> bool:
        return self.mode == MODE_TEST

    @property
    def writes_allowed(self) -> bool:
        return self.mode != MODE_DRY_RUN


@dataclass
class JobResult:
    status: str = STATUS_SUCCESS
    message: str = ""
    summary: dict[str, Any] = field(default_factory=dict)
    error: str = ""

    @property
    def ok(self) -> bool:
        return self.status != STATUS_FAILED

    @classmethod
    def skipped(cls, message: str, **summary: Any) -> "JobResult":
        return cls(status=STATUS_SKIPPED, message=message, summary=summary)

    @classmethod
    def failed(cls, error: str, **summary: Any) -> "JobResult":
        return cls(status=STATUS_FAILED, error=error, message=error, summary=summary)


class IntegrationJob(ABC):
    name: str = ""
    description: str = ""

    interval_seconds: int = 3600
    """How often the scheduler should run this when nobody asks."""

    @abstractmethod
    def run(self, context: JobContext) -> JobResult:
        """Do the work. May raise — the scheduler converts that to a failure."""

    def is_available(self) -> tuple[bool, str]:
        """Whether the job can act at all right now.

        Returning False produces a `skipped` run rather than a failure, so an
        unconfigured integration does not read as a broken one.
        """
        return True, ""

    def describe(self) -> dict[str, Any]:
        available, reason = self.is_available()
        return {
            "name": self.name,
            "description": self.description,
            "interval_seconds": self.interval_seconds,
            "available": available,
            "unavailable_reason": reason,
        }
