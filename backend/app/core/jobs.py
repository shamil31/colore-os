"""Which integration jobs this deployment runs.

The composition root for the scheduler. It exists so the scheduler package
never names a vendor: `app/scheduler/` knows how to run jobs, this module knows
which jobs there are, and adding an integration is one line here.
"""

from __future__ import annotations

from app.scheduler.service import JobRegistry


def build_registry() -> JobRegistry:
    # Imported here rather than at module scope: jobs import the scheduler,
    # which would otherwise import this module back.
    from app.growth.meta_job import MetaConversionsJob

    registry = JobRegistry()
    registry.register(MetaConversionsJob())
    return registry
