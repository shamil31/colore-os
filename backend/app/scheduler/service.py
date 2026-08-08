"""Registry and execution.

One failing job never stops another: each runs in its own try, its own session
scope, and its own recorded row. That is the property the whole thing exists
for — a broken integration should degrade to "that one is failing", not to
"nothing is running".
"""

from __future__ import annotations

import json
import logging
import time
from datetime import datetime, timedelta
from typing import Any, Callable, Iterable

from app.models.scheduler_run import SchedulerRun
from app.scheduler.job import (
    MODE_DRY_RUN,
    MODE_INTERVAL,
    STATUS_FAILED,
    STATUS_SKIPPED,
    STATUS_SUCCESS,
    IntegrationJob,
    JobContext,
    JobResult,
)

logger = logging.getLogger("colore.scheduler")


class JobRegistry:
    def __init__(self) -> None:
        self._jobs: dict[str, IntegrationJob] = {}

    def register(self, job: IntegrationJob) -> None:
        if not job.name:
            raise ValueError("a job must have a name")
        if job.name in self._jobs:
            raise ValueError(f"job '{job.name}' is already registered")
        self._jobs[job.name] = job

    def get(self, name: str) -> IntegrationJob:
        job = self._jobs.get(name)
        if job is None:
            raise KeyError(f"job '{name}' is not registered")
        return job

    def all(self) -> list[IntegrationJob]:
        return [self._jobs[name] for name in sorted(self._jobs)]

    def names(self) -> list[str]:
        return sorted(self._jobs)


class SchedulerService:
    def __init__(
        self,
        registry: JobRegistry,
        session_factory: Callable[[], Any],
        *,
        clock: Callable[[], datetime] | None = None,
    ) -> None:
        self.registry = registry
        self.session_factory = session_factory
        self._clock = clock or datetime.utcnow

    # ------------------------------------------------------------------ query

    def last_run(self, session, job_name: str, *, status: str | None = None) -> SchedulerRun | None:
        query = session.query(SchedulerRun).filter(SchedulerRun.job_name == job_name)
        if status is not None:
            query = query.filter(SchedulerRun.status == status)
        return query.order_by(SchedulerRun.id.desc()).first()

    def next_run_at(self, session, job: IntegrationJob) -> datetime:
        """Due immediately when it has never run — a fresh deploy should not
        wait a full interval before doing anything."""
        # Manual, dry and test runs do not reset the interval: asking a
        # question must not delay the scheduled work.
        last = (
            session.query(SchedulerRun)
            .filter(
                SchedulerRun.job_name == job.name,
                SchedulerRun.mode == MODE_INTERVAL,
            )
            .order_by(SchedulerRun.id.desc())
            .first()
        )
        if last is None:
            return self._clock()
        return last.started_at + timedelta(seconds=job.interval_seconds)

    def due_jobs(self, session, *, now: datetime | None = None) -> list[IntegrationJob]:
        now = now or self._clock()
        return [job for job in self.registry.all() if self.next_run_at(session, job) <= now]

    # ---------------------------------------------------------------- execute

    def run_job(self, job_name: str, *, mode: str = MODE_INTERVAL) -> JobResult:
        job = self.registry.get(job_name)
        session = self.session_factory()
        started = self._clock()
        clock_start = time.monotonic()

        available, reason = job.is_available()
        if not available:
            result = JobResult.skipped(reason or "not available")
        else:
            try:
                result = job.run(JobContext(session=session, mode=mode, now=started))
            except Exception as exc:  # noqa: BLE001 — one job must not stop the rest
                logger.exception("job %s failed", job_name)
                try:
                    session.rollback()
                except Exception:  # noqa: BLE001
                    pass
                result = JobResult.failed(f"{type(exc).__name__}: {exc}")

        duration_ms = int((time.monotonic() - clock_start) * 1000)

        try:
            self._record(session, job_name, mode, result, started, duration_ms)
        except Exception:  # noqa: BLE001
            logger.exception("could not record the run of %s", job_name)
        finally:
            session.close()

        return result

    def run_due(self, *, now: datetime | None = None) -> dict[str, JobResult]:
        session = self.session_factory()
        try:
            due = self.due_jobs(session, now=now)
        finally:
            session.close()

        results: dict[str, JobResult] = {}
        for job in due:
            results[job.name] = self.run_job(job.name, mode=MODE_INTERVAL)
        return results

    def _record(
        self,
        session,
        job_name: str,
        mode: str,
        result: JobResult,
        started: datetime,
        duration_ms: int,
    ) -> None:
        # A dry run is a question, not work. Recording it would move the
        # interval and hide when real work last happened.
        if mode == MODE_DRY_RUN:
            return

        session.add(
            SchedulerRun(
                job_name=job_name,
                mode=mode,
                status=result.status,
                message=result.message[:2000],
                summary=json.dumps(result.summary, ensure_ascii=False, default=str)[:4000],
                error=result.error[:2000],
                started_at=started,
                finished_at=self._clock(),
                duration_ms=duration_ms,
            )
        )
        session.commit()

    # ----------------------------------------------------------------- status

    def status(self) -> dict[str, Any]:
        session = self.session_factory()
        try:
            jobs = []
            failing = []
            for job in self.registry.all():
                last = self.last_run(session, job.name)
                last_success = self.last_run(session, job.name, status=STATUS_SUCCESS)
                last_failure = self.last_run(session, job.name, status=STATUS_FAILED)

                entry = job.describe()
                entry.update(
                    {
                        "last_run_at": last.started_at.isoformat() if last else None,
                        "last_status": last.status if last else None,
                        "last_message": last.message if last else "",
                        "last_success_at": (
                            last_success.started_at.isoformat() if last_success else None
                        ),
                        "last_error": last_failure.error if last_failure else "",
                        "last_error_at": (
                            last_failure.started_at.isoformat() if last_failure else None
                        ),
                        "next_run_at": self.next_run_at(session, job).isoformat(),
                    }
                )
                jobs.append(entry)

                if last is not None and last.status == STATUS_FAILED:
                    failing.append(job.name)

            return {
                "jobs": jobs,
                "job_count": len(jobs),
                "failing": failing,
                "generated_at": self._clock().isoformat(),
            }
        finally:
            session.close()


def _iter(value: Iterable[Any]) -> list[Any]:
    return list(value)
