"""Meta as a scheduler job, configurable currency, and test events."""

import json
from datetime import datetime, timezone

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.db.base import Base
from app.growth import attribution, meta_sync
from app.growth.meta_job import JOB_NAME, MetaConversionsJob, build_registry
from app.integrations.connectors.meta_connector import MetaConnector
from app.models.meta_conversion import (
    OUTCOME_ARRIVED,
    STATUS_QUEUED,
    STATUS_SENT,
    MetaConversion,
)
from app.scheduler.job import (
    MODE_DRY_RUN,
    MODE_MANUAL,
    MODE_TEST,
    STATUS_FAILED,
    STATUS_SKIPPED,
    JobContext,
)


@pytest.fixture
def session():
    engine = create_engine("sqlite://")
    Base.metadata.create_all(bind=engine, tables=[MetaConversion.__table__])
    s = sessionmaker(bind=engine)()
    yield s
    s.close()


def queue(session, n=2):
    rows = []
    for i in range(n):
        row = MetaConversion(
            outcome=OUTCOME_ARRIVED,
            event_name="Purchase",
            event_id=f"arrived-{i}",
            event_time=int(datetime.now(timezone.utc).timestamp()) - 3600,
            action_source="physical_store",
            source_system="altegio",
            user_data=json.dumps({"ph": ["a" * 64]}),
            status=STATUS_QUEUED,
        )
        session.add(row)
        rows.append(row)
    session.commit()
    return rows


class Sender:
    can_send_conversions = True
    verify_token = "v"
    app_secret = "s"

    def __init__(self):
        self.calls = []

    def missing_conversion_settings(self):
        return ()

    def send_conversions(self, events, *, test_event_code=None):
        self.calls.append({"count": len(events), "test_event_code": test_event_code})
        return {"events_received": len(events)}


@pytest.fixture
def no_build(monkeypatch):
    monkeypatch.setattr(meta_sync, "build_queue", lambda session, **kw: (0, []))


# ------------------------------------------------------------------ registry


def test_meta_is_registered_as_a_job():
    registry = build_registry()

    assert JOB_NAME in registry.names()
    assert registry.get(JOB_NAME).description


def test_the_job_is_unavailable_when_meta_is_not_configured(monkeypatch):
    connector = MetaConnector(verify_token="v")
    monkeypatch.setattr(MetaConversionsJob, "_connector", lambda self: connector)

    available, reason = MetaConversionsJob().is_available()

    assert available is False
    assert "META_DATASET_ID" in reason


# ------------------------------------------------------------------- dry run


def test_a_dry_run_sends_nothing_and_changes_nothing(session, monkeypatch, no_build):
    rows = queue(session, 3)
    sender = Sender()
    monkeypatch.setattr(MetaConversionsJob, "_connector", lambda self: sender)
    monkeypatch.setattr(meta_sync, "_meta_connector", lambda: sender)

    result = MetaConversionsJob().run(JobContext(session=session, mode=MODE_DRY_RUN))

    assert sender.calls == [], "a dry run must not call the vendor"
    assert result.summary["would_send"] == 3
    for row in rows:
        session.refresh(row)
        assert row.status == STATUS_QUEUED, "no row may move during a dry run"


def test_a_dry_run_reports_exactly_what_a_real_run_would_touch(session, monkeypatch, no_build):
    rows = queue(session, 2)
    sender = Sender()
    monkeypatch.setattr(MetaConversionsJob, "_connector", lambda self: sender)
    monkeypatch.setattr(meta_sync, "_meta_connector", lambda: sender)

    result = MetaConversionsJob().run(JobContext(session=session, mode=MODE_DRY_RUN))

    assert result.summary["event_ids"] == [r.event_id for r in rows]


# ---------------------------------------------------------------- test mode


def test_test_mode_passes_the_test_event_code(session, monkeypatch, no_build):
    queue(session, 2)
    sender = Sender()
    monkeypatch.setattr(MetaConversionsJob, "_connector", lambda self: sender)
    monkeypatch.setattr(meta_sync, "_meta_connector", lambda: sender)
    monkeypatch.setattr(settings, "META_TEST_EVENT_CODE", "TEST12345")

    MetaConversionsJob().run(JobContext(session=session, mode=MODE_TEST))

    assert sender.calls[0]["test_event_code"] == "TEST12345"


def test_test_mode_refuses_to_run_without_a_test_code(session, monkeypatch, no_build):
    """Otherwise "test" would quietly mean "production"."""
    queue(session, 1)
    sender = Sender()
    monkeypatch.setattr(MetaConversionsJob, "_connector", lambda self: sender)
    monkeypatch.setattr(meta_sync, "_meta_connector", lambda: sender)
    monkeypatch.setattr(settings, "META_TEST_EVENT_CODE", "")

    result = MetaConversionsJob().run(JobContext(session=session, mode=MODE_TEST))

    assert result.status == STATUS_FAILED
    assert sender.calls == []
    assert "META_TEST_EVENT_CODE" in result.error


def test_a_normal_run_sends_no_test_code(session, monkeypatch, no_build):
    queue(session, 1)
    sender = Sender()
    monkeypatch.setattr(MetaConversionsJob, "_connector", lambda self: sender)
    monkeypatch.setattr(meta_sync, "_meta_connector", lambda: sender)
    monkeypatch.setattr(settings, "META_TEST_EVENT_CODE", "TEST12345")

    MetaConversionsJob().run(JobContext(session=session, mode=MODE_MANUAL))

    assert sender.calls[0]["test_event_code"] is None


# ------------------------------------------------------------------ sending


def test_a_manual_run_sends_and_reports(session, monkeypatch, no_build):
    rows = queue(session, 3)
    sender = Sender()
    monkeypatch.setattr(MetaConversionsJob, "_connector", lambda self: sender)
    monkeypatch.setattr(meta_sync, "_meta_connector", lambda: sender)

    result = MetaConversionsJob().run(JobContext(session=session, mode=MODE_MANUAL))

    assert result.summary["sent"] == 3
    assert "3 sent" in result.message
    for row in rows:
        session.refresh(row)
        assert row.status == STATUS_SENT


def test_an_empty_queue_is_skipped_not_failed(session, monkeypatch, no_build):
    sender = Sender()
    monkeypatch.setattr(MetaConversionsJob, "_connector", lambda self: sender)
    monkeypatch.setattr(meta_sync, "_meta_connector", lambda: sender)

    result = MetaConversionsJob().run(JobContext(session=session, mode=MODE_MANUAL))

    assert result.status == STATUS_SKIPPED


# ----------------------------------------------------------------- currency


def test_currency_comes_from_configuration(monkeypatch):
    monkeypatch.setattr(settings, "BUSINESS_CURRENCY", "eur")

    value = attribution._value_of({"services": [{"cost_to_pay": 150}]})

    assert value == {"value": 150.0, "currency": "EUR"}


def test_no_configured_currency_means_no_value_rather_than_a_guess(monkeypatch):
    """A wrong currency misstates every visit by roughly a hundredfold."""
    monkeypatch.setattr(settings, "BUSINESS_CURRENCY", "")

    assert attribution._value_of({"services": [{"cost_to_pay": 22000}]}) == {}


def test_currency_is_never_hardcoded_in_the_source():
    from pathlib import Path

    source = Path(attribution.__file__).read_text(encoding="utf-8")

    assert '"RSD"' not in source
    assert "'RSD'" not in source
