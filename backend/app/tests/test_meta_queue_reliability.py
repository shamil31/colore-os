"""P0-001: a failed send must never destroy a confirmed business outcome.

These run against a real SQLite session rather than a fake, because the whole
defect was about which rows end up in which state — exactly what a fake would
have hidden.

The old behaviour: one failure marked every event in the batch `rejected`,
terminally. A five-second network blip, a rotated token, or one over-age event
permanently destroyed up to a hundred confirmed outcomes.
"""

import json
from datetime import datetime, timedelta, timezone

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.base import Base
from app.growth import meta_delivery, meta_sync
from app.growth.meta_delivery import PERMANENT, TEMPORARY, classify
from app.integrations.connectors.meta_connector import MetaSendError
from app.models.meta_conversion import (
    OUTCOME_ARRIVED,
    STATUS_PERMANENT_FAILURE,
    STATUS_QUEUED,
    STATUS_RETRY,
    STATUS_SENT,
    MetaConversion,
)


@pytest.fixture
def session():
    engine = create_engine("sqlite://")
    Base.metadata.create_all(bind=engine, tables=[MetaConversion.__table__])
    maker = sessionmaker(bind=engine)
    s = maker()
    yield s
    s.close()


def now_ts() -> int:
    return int(datetime.now(timezone.utc).timestamp())


def queue(session, n=1, *, age_days=1, start=1):
    rows = []
    for i in range(n):
        row = MetaConversion(
            outcome=OUTCOME_ARRIVED,
            event_name="Purchase",
            event_id=f"arrived-{start + i}",
            event_time=now_ts() - int(age_days * 86400),
            action_source="physical_store",
            source_system="altegio",
            source_ref=str(start + i),
            user_data=json.dumps({"ph": ["a" * 64]}),
            status=STATUS_QUEUED,
        )
        session.add(row)
        rows.append(row)
    session.commit()
    return rows


class Connector:
    """A Meta connector whose behaviour per-batch is scripted."""

    can_send_conversions = True
    verify_token = "v"
    app_secret = "s"

    def __init__(self, *, fail_with=None, bad_event_ids=()):
        self.fail_with = fail_with
        self.bad_event_ids = set(bad_event_ids)
        self.batches = []
        self.test_event_codes = []

    def missing_conversion_settings(self):
        return ()

    def send_conversions(self, events, *, test_event_code=None):
        self.batches.append([e["event_id"] for e in events])
        self.test_event_codes.append(test_event_code)

        if self.fail_with is not None:
            raise self.fail_with

        if self.bad_event_ids:
            hit = [e["event_id"] for e in events if e["event_id"] in self.bad_event_ids]
            if hit:
                raise MetaSendError(
                    "Meta rejected the events: HTTP 400 invalid parameter",
                    status_code=400,
                    error_code=100,
                )

        return {"events_received": len(events)}


def use(monkeypatch, connector):
    monkeypatch.setattr(meta_sync, "_meta_connector", lambda: connector)


# ------------------------------------------------------------ classification


@pytest.mark.parametrize(
    "error",
    [
        MetaSendError("connection reset", network=True),
        MetaSendError("boom", status_code=500),
        MetaSendError("boom", status_code=503),
        MetaSendError("slow down", status_code=429),
        MetaSendError("rate limit", error_code=613),
        MetaSendError("app limit", error_code=4),
        MetaSendError("temporary", is_transient=True),
    ],
)
def test_infrastructure_failures_are_temporary(error):
    kind, _ = classify(error)
    assert kind == TEMPORARY


@pytest.mark.parametrize(
    "error",
    [
        MetaSendError("event_time is more than 7 days in the past", status_code=400),
        MetaSendError("Invalid parameter", status_code=400, error_code=100),
        MetaSendError("duplicate event", status_code=400),
    ],
)
def test_payload_failures_are_permanent(error):
    kind, _ = classify(error)
    assert kind == PERMANENT


@pytest.mark.parametrize("code", [190, 200, 803])
def test_configuration_failures_are_temporary_not_permanent(code):
    """A bad token or dataset id is not the event's fault.

    Marking these permanent would recreate the exact bug this change removes:
    one wrong setting destroying the whole queue.
    """
    kind, reason = classify(MetaSendError("nope", status_code=400, error_code=code))

    assert kind == TEMPORARY
    assert "configuration" in reason


def test_an_unknown_error_is_retried_rather_than_discarded():
    kind, _ = classify(RuntimeError("something nobody predicted"))
    assert kind == TEMPORARY


def test_backoff_grows_and_is_capped():
    assert meta_delivery.backoff_for(1) < meta_delivery.backoff_for(3)
    assert meta_delivery.backoff_for(99) == meta_delivery.MAX_BACKOFF


# ------------------------------------------------------------- no event lost


def test_a_network_failure_returns_every_event_to_the_queue(session, monkeypatch):
    rows = queue(session, 10)
    use(monkeypatch, Connector(fail_with=MetaSendError("connection reset", network=True)))

    result = meta_sync.send_pending(session)

    assert result.retry == 10
    assert result.permanent_failure == 0
    for row in rows:
        session.refresh(row)
        assert row.status == STATUS_RETRY
        assert row.next_attempt_at is not None, "a retry must be scheduled"
        assert row.attempts == 1


def test_a_5xx_does_not_permanently_fail_anything(session, monkeypatch):
    rows = queue(session, 5)
    use(monkeypatch, Connector(fail_with=MetaSendError("bad gateway", status_code=502)))

    meta_sync.send_pending(session)

    assert all(session.refresh(r) or r.status == STATUS_RETRY for r in rows)


def test_an_expired_token_does_not_destroy_the_queue(session, monkeypatch):
    """The scenario that would have burned 235 events."""
    rows = queue(session, 20)
    use(monkeypatch, Connector(fail_with=MetaSendError("token expired", status_code=400, error_code=190)))

    meta_sync.send_pending(session)

    for row in rows:
        session.refresh(row)
        assert row.status == STATUS_RETRY
        assert row.status != STATUS_PERMANENT_FAILURE


def test_retry_rows_are_picked_up_again_once_due(session, monkeypatch):
    rows = queue(session, 3)
    use(monkeypatch, Connector(fail_with=MetaSendError("blip", network=True)))
    meta_sync.send_pending(session)

    # Time passes.
    for row in rows:
        row.next_attempt_at = datetime.utcnow() - timedelta(seconds=1)
    session.commit()

    use(monkeypatch, Connector())
    result = meta_sync.send_pending(session)

    assert result.sent == 3
    for row in rows:
        session.refresh(row)
        assert row.status == STATUS_SENT


def test_a_retry_is_not_attempted_before_its_backoff_expires(session, monkeypatch):
    queue(session, 3)
    use(monkeypatch, Connector(fail_with=MetaSendError("blip", network=True)))
    meta_sync.send_pending(session)

    connector = Connector()
    use(monkeypatch, connector)
    result = meta_sync.send_pending(session)

    assert result.sent == 0
    assert connector.batches == [], "nothing should have been sent yet"


# ------------------------------------------------- one bad event, batch lives


def test_one_bad_event_does_not_take_the_batch_with_it(session, monkeypatch):
    """The core requirement: isolate the offender, deliver the rest."""
    rows = queue(session, 8)
    bad = rows[3].event_id
    connector = Connector(bad_event_ids=[bad])
    use(monkeypatch, connector)

    result = meta_sync.send_pending(session)

    session.expire_all()
    states = {r.event_id: r.status for r in session.query(MetaConversion).all()}

    assert states[bad] == STATUS_PERMANENT_FAILURE
    delivered = [eid for eid, st in states.items() if st == STATUS_SENT]
    assert len(delivered) == 7, "the seven good events must still be delivered"
    assert result.sent == 7
    assert result.permanent_failure == 1


def test_isolation_narrows_by_halving_rather_than_condemning_everyone(session, monkeypatch):
    rows = queue(session, 8)
    connector = Connector(bad_event_ids=[rows[0].event_id])
    use(monkeypatch, connector)

    meta_sync.send_pending(session)

    # First the whole batch, then halves, down to the single offender.
    assert len(connector.batches[0]) == 8
    assert any(len(b) == 1 for b in connector.batches)


def test_two_bad_events_are_both_isolated(session, monkeypatch):
    rows = queue(session, 8)
    bad = {rows[1].event_id, rows[6].event_id}
    use(monkeypatch, Connector(bad_event_ids=bad))

    meta_sync.send_pending(session)

    session.expire_all()
    states = {r.event_id: r.status for r in session.query(MetaConversion).all()}

    assert {e for e, s in states.items() if s == STATUS_PERMANENT_FAILURE} == bad
    assert sum(1 for s in states.values() if s == STATUS_SENT) == 6


# ---------------------------------------------------------- the 7-day window


def test_events_past_the_seven_day_window_are_removed_before_batching(session, monkeypatch):
    """229 of 235 real events were in this state. One of them poisons a batch."""
    fresh = queue(session, 3, age_days=1, start=100)
    stale = queue(session, 5, age_days=30, start=200)
    connector = Connector()
    use(monkeypatch, connector)

    result = meta_sync.send_pending(session)

    assert result.expired == 5
    for row in stale:
        session.refresh(row)
        assert row.status == STATUS_PERMANENT_FAILURE
        assert "7 days" in row.error

    assert result.sent == 3
    assert connector.batches == [[r.event_id for r in fresh]], "only fresh events were sent"


def test_a_stale_event_never_reaches_meta(session, monkeypatch):
    queue(session, 4, age_days=90)
    connector = Connector()
    use(monkeypatch, connector)

    meta_sync.send_pending(session)

    assert connector.batches == [], "no request should be made at all"


# ---------------------------------------------------------------- happy path


def test_a_successful_send_marks_events_sent(session, monkeypatch):
    rows = queue(session, 4)
    use(monkeypatch, Connector())

    result = meta_sync.send_pending(session)

    assert result.sent == 4
    for row in rows:
        session.refresh(row)
        assert row.status == STATUS_SENT
        assert row.sent_at is not None
        assert row.error == ""


def test_status_counts_retry_as_still_waiting_not_as_lost(session, monkeypatch):
    queue(session, 6)
    use(monkeypatch, Connector(fail_with=MetaSendError("blip", network=True)))
    meta_sync.send_pending(session)

    status = meta_sync.read_status(session, build=False)

    assert status.retry == 6
    assert status.permanent_failure == 0
    assert status.waiting == 6, "a retry is still in the queue"
