"""Meta attribution as a scheduler job — the first of them, not a special case.

The job does four things in order: build the queue from confirmed outcomes,
drop what is past Meta's window, send what is eligible, and report what
happened. Everything vendor-specific lives here; the scheduler stays generic.
"""

from __future__ import annotations

import logging

from app.core.config import settings
from app.growth import meta_sync
from app.growth.meta_sync import eligible_rows, expire_stale
from app.integrations.connectors.meta_connector import MetaConnector
from app.integrations.gateway.factory import get_connector_gateway
from app.scheduler.job import IntegrationJob, JobContext, JobResult

logger = logging.getLogger("colore.meta_job")

JOB_NAME = "meta_conversions"


class MetaConversionsJob(IntegrationJob):
    name = JOB_NAME
    description = "Send confirmed business outcomes to the Meta Conversions API"

    def __init__(self, *, interval_seconds: int | None = None, days: int | None = None) -> None:
        self.interval_seconds = interval_seconds or settings.META_SYNC_INTERVAL_SECONDS
        self.days = days or settings.META_SYNC_DAYS

    def _connector(self) -> MetaConnector | None:
        try:
            connector = get_connector_gateway().integration_registry.get("meta")
        except KeyError:
            return None
        return connector if isinstance(connector, MetaConnector) else None

    def is_available(self) -> tuple[bool, str]:
        connector = self._connector()
        if connector is None:
            return False, "Meta connector is not registered"
        if not connector.can_send_conversions:
            missing = ", ".join(connector.missing_conversion_settings())
            return False, f"not configured: {missing}"
        return True, ""

    def run(self, context: JobContext) -> JobResult:
        session = context.session

        built, build_errors = meta_sync.build_queue(session, days=self.days)

        if context.dry_run:
            # Nothing is expired and nothing is sent: a dry run answers "what
            # would happen" without moving a single row.
            eligible = eligible_rows(session)
            return JobResult(
                message=f"dry run: {len(eligible)} event(s) would be sent",
                summary={
                    "mode": context.mode,
                    "built": built,
                    "would_send": len(eligible),
                    "event_ids": [row.event_id for row in eligible][:20],
                    "errors": build_errors,
                },
            )

        expired = expire_stale(session)

        test_code = None
        if context.test:
            test_code = settings.META_TEST_EVENT_CODE
            if not test_code:
                return JobResult.failed(
                    "test mode needs META_TEST_EVENT_CODE — refusing to send real "
                    "traffic while pretending it is a test",
                    built=built,
                    expired=expired,
                )

        result = meta_sync.send_pending(session, test_event_code=test_code)

        summary = {
            "mode": context.mode,
            "built": built,
            "expired": expired,
            "sent": result.sent,
            "retry": result.retry,
            "permanent_failure": result.permanent_failure,
            "errors": build_errors + result.errors,
        }

        if result.errors and result.sent == 0 and result.retry:
            # Everything bounced but nothing was lost — that is not a healthy
            # run, and it should be visible as a failure in the doctor.
            return JobResult.failed(
                f"nothing delivered; {result.retry} event(s) queued for retry",
                **summary,
            )

        parts = []
        if built:
            parts.append(f"{built} built")
        if expired:
            parts.append(f"{expired} expired")
        if result.sent:
            parts.append(f"{result.sent} sent")
        if result.retry:
            parts.append(f"{result.retry} retrying")
        if result.permanent_failure:
            parts.append(f"{result.permanent_failure} permanently failed")

        if not parts:
            return JobResult.skipped("nothing to do", **summary)

        return JobResult(message=", ".join(parts), summary=summary)


