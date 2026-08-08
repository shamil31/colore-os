"""The scheduler: generic, extensible, and unable to let one job stop another.

Meta is deliberately absent from most of this file. If these tests needed to
know about Meta, the scheduler would not be generic.
"""

from datetime import datetime, timedelta

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.base import Base
from app.models.scheduler_run import SchedulerRun
from app.scheduler.job import (
    MODE_DRY_RUN,
    MODE_INTERVAL,
    MODE_MANUAL,
    MODE_TEST,
    STATUS_FAILED,
    STATUS_SKIPPED,
    STATUS_SUCCESS,
    IntegrationJob,
    JobContext,
    JobResult,
)
from app.scheduler.service import JobRegistry, SchedulerService

NOW = datetime(2026, 8, 8, 12, 0, 0)


@pytest.fixture
def session_factory():
    engine = create_engine("sqlite://")
    Base.metadata.create_all(bind=engine, tables=[SchedulerRun.__table__])
    return sessionmaker(bind=engine)


class Recorder(IntegrationJob):
    name = "recorder"
    interval_seconds = 600

    def __init__(self, name="recorder", *, raises=None, result=None, available=(True, "")):
        self.name = name
        self.raises = raises
        self.result = result
        self.available = available
        self.calls: list[str] = []

    def is_available(self):
        return self.available

    def run(self, context: JobContext) -> JobResult:
        self.calls.append(context.mode)
        if self.raises:
            raise self.raises
        return self.result or JobResult(message="done")


def service_for(session_factory, *jobs, clock=lambda: NOW):
    registry = JobRegistry()
    for job in jobs:
        registry.register(job)
    return SchedulerService(registry, session_factory, clock=clock)


# ------------------------------------------------------------------ registry


def test_a_job_can_be_registered_and_found(session_factory):
    job = Recorder()
    service = service_for(session_factory, job)

    assert service.registry.names() == ["recorder"]
    assert service.registry.get("recorder") is job


def test_registering_the_same_name_twice_is_rejected():
    registry = JobRegistry()
    registry.register(Recorder())

    with pytest.raises(ValueError):
        registry.register(Recorder())


def test_an_unknown_job_raises():
    with pytest.raises(KeyError):
        JobRegistry().get("nope")


def test_the_scheduler_holds_many_jobs_without_knowing_what_they_are(session_factory):
    service = service_for(session_factory, Recorder("alpha"), Recorder("beta"), Recorder("gamma"))

    assert service.registry.names() == ["alpha", "beta", "gamma"]


# -------------------------------------------------------------------- modes


@pytest.mark.parametrize("mode", [MODE_INTERVAL, MODE_MANUAL, MODE_TEST])
def test_each_mode_reaches_the_job(session_factory, mode):
    job = Recorder()
    service = service_for(session_factory, job)

    service.run_job("recorder", mode=mode)

    assert job.calls == [mode]


def test_dry_run_reaches_the_job_but_is_not_recorded(session_factory):
    """A question must not look like work, or it would move the interval."""
    job = Recorder()
    service = service_for(session_factory, job)

    service.run_job("recorder", mode=MODE_DRY_RUN)

    assert job.calls == [MODE_DRY_RUN]
    session = session_factory()
    assert session.query(SchedulerRun).count() == 0


def test_a_job_can_tell_a_dry_run_from_a_real_one(session_factory):
    seen = {}

    class Checking(Recorder):
        def run(self, context):
            seen["dry"] = context.dry_run
            seen["test"] = context.test
            seen["writes"] = context.writes_allowed
            return JobResult(message="ok")

    service = service_for(session_factory, Checking())
    service.run_job("recorder", mode=MODE_DRY_RUN)

    assert seen == {"dry": True, "test": False, "writes": False}


# ------------------------------------------------------------------ recording


def test_a_successful_run_is_recorded(session_factory):
    service = service_for(session_factory, Recorder())

    service.run_job("recorder", mode=MODE_MANUAL)

    session = session_factory()
    row = session.query(SchedulerRun).one()
    assert row.job_name == "recorder"
    assert row.mode == MODE_MANUAL
    assert row.status == STATUS_SUCCESS
    assert row.finished_at is not None


def test_an_exception_becomes_a_failed_run_not_a_crash(session_factory):
    service = service_for(session_factory, Recorder(raises=RuntimeError("kaboom")))

    result = service.run_job("recorder")

    assert result.status == STATUS_FAILED
    assert "kaboom" in result.error

    session = session_factory()
    assert session.query(SchedulerRun).one().status == STATUS_FAILED


def test_an_unavailable_job_is_skipped_not_failed(session_factory):
    """An unconfigured integration is not a broken one."""
    job = Recorder(available=(False, "no credentials"))
    service = service_for(session_factory, job)

    result = service.run_job("recorder")

    assert result.status == STATUS_SKIPPED
    assert "no credentials" in result.message
    assert job.calls == [], "an unavailable job must not be executed"


def test_one_failing_job_does_not_stop_the_others(session_factory):
    """The property the whole scheduler exists for."""
    bad = Recorder("bad", raises=RuntimeError("down"))
    good_a = Recorder("aaa")
    good_b = Recorder("zzz")
    service = service_for(session_factory, bad, good_a, good_b)

    results = service.run_due()

    assert results["bad"].status == STATUS_FAILED
    assert results["aaa"].status == STATUS_SUCCESS
    assert results["zzz"].status == STATUS_SUCCESS
    assert good_a.calls and good_b.calls


# ----------------------------------------------------------------- intervals


def test_a_job_that_never_ran_is_due_immediately(session_factory):
    service = service_for(session_factory, Recorder())
    session = session_factory()

    assert [j.name for j in service.due_jobs(session)] == ["recorder"]


def test_a_job_is_not_due_again_before_its_interval(session_factory):
    service = service_for(session_factory, Recorder())
    service.run_job("recorder", mode=MODE_INTERVAL)

    session = session_factory()
    assert service.due_jobs(session, now=NOW + timedelta(seconds=100)) == []


def test_a_job_becomes_due_once_the_interval_passes(session_factory):
    service = service_for(session_factory, Recorder())
    service.run_job("recorder", mode=MODE_INTERVAL)

    session = session_factory()
    due = service.due_jobs(session, now=NOW + timedelta(seconds=601))

    assert [j.name for j in due] == ["recorder"]


def test_a_manual_run_does_not_delay_the_scheduled_one(session_factory):
    """Asking a question must not postpone the work."""
    service = service_for(session_factory, Recorder())
    service.run_job("recorder", mode=MODE_MANUAL)

    session = session_factory()
    assert [j.name for j in service.due_jobs(session)] == ["recorder"]


# -------------------------------------------------------------------- status


def test_status_reports_everything_the_doctor_needs(session_factory):
    service = service_for(session_factory, Recorder())
    service.run_job("recorder", mode=MODE_INTERVAL)

    status = service.status()
    job = status["jobs"][0]

    assert status["job_count"] == 1
    assert job["name"] == "recorder"
    assert job["last_run_at"] is not None
    assert job["last_status"] == STATUS_SUCCESS
    assert job["next_run_at"] is not None
    assert job["last_success_at"] is not None
    assert status["failing"] == []


def test_status_lists_a_failing_job(session_factory):
    service = service_for(session_factory, Recorder(raises=RuntimeError("nope")))
    service.run_job("recorder")

    status = service.status()

    assert status["failing"] == ["recorder"]
    assert "nope" in status["jobs"][0]["last_error"]


def test_status_keeps_the_last_success_after_a_later_failure(session_factory):
    job = Recorder()
    service = service_for(session_factory, job)
    service.run_job("recorder")

    job.raises = RuntimeError("later problem")
    service.run_job("recorder")

    job_status = service.status()["jobs"][0]

    assert job_status["last_status"] == STATUS_FAILED
    assert job_status["last_success_at"] is not None, "the earlier success is still recorded"
    assert "later problem" in job_status["last_error"]
