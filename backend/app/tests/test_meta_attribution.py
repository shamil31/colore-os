"""The attribution loop: only confirmed outcomes, never a fabricated conversion.

The rule under test is narrow and absolute — an event exists only when the
outcome already happened and is recorded in a system of record. A booking is
never assumed from a lead, and a visit is never assumed from a booking.
"""

import json
from datetime import datetime

import pytest

from app.growth import attribution, meta_sync
from app.growth.business_data import BusinessSnapshot
from app.growth.meta_renderer import MetaRenderer
from app.growth.meta_sync import MetaStatus
from app.integrations.connectors.meta_connector import MetaConnector, MetaVerificationError
from app.models.growth import STATUS_PROCESSED, GrowthEvent
from app.models.meta_conversion import (
    OUTCOME_ARRIVED,
    OUTCOME_BOOKED,
    OUTCOME_CANCELLED,
    OUTCOME_LEAD,
    OUTCOME_NO_SHOW,
)

PHONE = "381641234567"


def record(record_id=1, attendance=1, deleted=False, phone=PHONE, **extra):
    data = {
        "id": record_id,
        "attendance": attendance,
        "deleted": deleted,
        "create_date": extra.get("create_date", "2026-07-18T11:46:48+0200"),
        "date": extra.get("date", "2026-08-06 09:00:00"),
        "last_change_date": extra.get("last_change_date", "2026-08-01T10:00:00+0200"),
        "client": {"id": 42, "phone": phone, "name": "Ана", "surname": "Петровић", "email": ""},
        "services": extra.get("services", [{"cost_to_pay": 22000}]),
    }
    return data


def lead_event(event_id=7, sender_ref=PHONE, source="whatsapp"):
    event = GrowthEvent(
        source=source,
        external_id="wamid.X",
        sender_ref=sender_ref,
        status=STATUS_PROCESSED,
    )
    event.id = event_id
    event.received_at = datetime(2026, 8, 3, 12, 0, 0)
    return event


# ---------------------------------------------------------------- hashing


def test_customer_data_is_hashed_and_never_sent_raw():
    data = attribution.build_user_data(
        phone=PHONE, email="Ana@Example.COM ", first="Ана", last="Петровић", external_id=42
    )

    blob = json.dumps(data)
    assert PHONE not in blob
    assert "ana@example.com" not in blob.lower()
    assert "Ана" not in blob
    assert set(data) == {"ph", "em", "fn", "ln", "external_id"}
    assert all(len(v[0]) == 64 for v in data.values()), "SHA256 is 64 hex chars"


def test_phone_normalisation_matches_metas_rules():
    """"Remove symbols, letters, and any leading zeros… Always include the country code"."""
    assert attribution.hash_phone("+381 64 123-45-67") == attribution.hash_phone("381641234567")
    assert attribution.hash_phone("00381641234567") == attribution.hash_phone("381641234567")


def test_email_is_lowercased_and_trimmed_before_hashing():
    assert attribution.hash_email("  Ana@Example.COM ") == attribution.hash_email("ana@example.com")


def test_a_non_phone_produces_no_matching_field():
    assert attribution.hash_phone("IGSID_ANA") == ""
    assert attribution.build_user_data(phone="IGSID_ANA") == {}


# ------------------------------------------------------- confirmed outcomes


def test_a_booking_yields_a_schedule_event():
    events = attribution.event_from_record(record(attendance=0))

    assert [e.outcome for e in events] == [OUTCOME_BOOKED]
    assert events[0].event_name == "Schedule"
    assert events[0].action_source == "business_messaging"
    assert events[0].event_id == "booked-1"


def test_an_arrival_yields_a_purchase_from_the_physical_store():
    events = attribution.event_from_record(record(attendance=1))

    outcomes = {e.outcome: e for e in events}
    assert OUTCOME_ARRIVED in outcomes
    arrival = outcomes[OUTCOME_ARRIVED]
    assert arrival.event_name == "Purchase"
    assert arrival.action_source == "physical_store"
    assert arrival.custom_data == {"value": 22000.0, "currency": "RSD"}


def test_a_no_show_is_reported_as_such_not_as_a_visit():
    events = attribution.event_from_record(record(attendance=-1))

    outcomes = [e.outcome for e in events]
    assert OUTCOME_NO_SHOW in outcomes
    assert OUTCOME_ARRIVED not in outcomes


def test_a_pending_appointment_produces_no_outcome_event():
    """Nothing has happened yet, so nothing is claimed."""
    events = attribution.event_from_record(record(attendance=0))

    outcomes = [e.outcome for e in events]
    assert outcomes == [OUTCOME_BOOKED]
    assert OUTCOME_ARRIVED not in outcomes
    assert OUTCOME_NO_SHOW not in outcomes


def test_a_cancelled_appointment_yields_a_cancellation():
    events = attribution.event_from_record(record(deleted=True, attendance=1))

    outcomes = [e.outcome for e in events]
    assert OUTCOME_CANCELLED in outcomes
    assert OUTCOME_ARRIVED not in outcomes, "a cancelled appointment was not attended"


def test_a_lead_is_built_only_from_a_persisted_event():
    assert attribution.event_from_lead(GrowthEvent(source="whatsapp")) == []

    events = attribution.event_from_lead(lead_event())
    assert [e.outcome for e in events] == [OUTCOME_LEAD]
    assert events[0].event_id == "lead-7"
    assert events[0].event_name == "Lead"


def test_an_instagram_lead_yields_no_event_because_it_cannot_be_matched():
    assert attribution.event_from_lead(lead_event(sender_ref="IGSID_A", source="instagram")) == []


def test_a_record_with_only_a_name_is_skipped():
    """A name is not an identifier — Meta cannot attribute an event to "Ана"."""
    assert attribution.event_from_record(record(phone="")) == []


def test_an_email_alone_is_enough_to_attribute():
    data = record(phone="")
    data["client"]["email"] = "ana@example.com"

    events = attribution.event_from_record(data)

    assert events, "email is a strong identifier"
    assert "em" in events[0].user_data


# -------------------------------------------------------------- no invention


def test_a_lead_never_produces_a_booking_event():
    """The whole point: a conversation is not a conversion."""
    events = attribution.build_events(BusinessSnapshot(company_id=1), [lead_event()])

    assert [e.outcome for e in events] == [OUTCOME_LEAD]


def test_a_booking_never_produces_an_arrival_event():
    """Attendance is Altegio's to confirm; until it does, nobody arrived."""
    snapshot = BusinessSnapshot(company_id=1, records=[record(attendance=0)])

    events = attribution.build_events(snapshot, [])

    assert [e.outcome for e in events] == [OUTCOME_BOOKED]


# ------------------------------------------------------------------ payload


def test_every_event_carries_the_four_required_fields():
    snapshot = BusinessSnapshot(
        company_id=1,
        records=[record(record_id=2, attendance=1)],
        cancelled_records=[record(record_id=3, deleted=True)],
    )

    for event in attribution.build_events(snapshot, [lead_event()]):
        payload = event.payload()
        assert payload["event_name"]
        assert isinstance(payload["event_time"], int) and payload["event_time"] > 0
        assert payload["event_id"]
        assert payload["action_source"] in {
            "email", "website", "app", "phone_call", "chat",
            "physical_store", "system_generated", "business_messaging", "other",
        }
        assert payload["user_data"], "an event with no matching field cannot be attributed"


def test_event_ids_are_unique_and_stable_across_rebuilds():
    snapshot = BusinessSnapshot(
        company_id=1,
        records=[record(record_id=1, attendance=1), record(record_id=2, attendance=-1)],
    )

    first = [e.event_id for e in attribution.build_events(snapshot, [lead_event()])]
    second = [e.event_id for e in attribution.build_events(snapshot, [lead_event()])]

    assert first == second, "the same facts must produce the same event ids"
    assert len(first) == len(set(first)), "event ids must be unique"


def test_altegio_datetime_formats_both_parse():
    assert attribution._unix("2026-08-06 09:00:00") is not None
    assert attribution._unix("2026-07-18T11:46:48+0200") is not None
    assert attribution._unix("not a date") is None


# --------------------------------------------------------------- connector


class FakeResponse:
    def __init__(self, payload, status_code=200):
        self._payload = payload
        self.status_code = status_code

    def json(self):
        return self._payload


class FakeSession:
    def __init__(self, response):
        self.response = response
        self.calls = []

    def post(self, url, json=None, timeout=None):
        self.calls.append({"url": url, "json": json})
        return self.response


def test_connector_refuses_to_send_when_not_configured():
    connector = MetaConnector(verify_token="v")

    assert connector.can_send_conversions is False
    assert connector.missing_conversion_settings() == ("META_ACCESS_TOKEN", "META_DATASET_ID")

    with pytest.raises(MetaVerificationError) as exc:
        connector.send_conversions([{"event_name": "Lead"}])

    assert "META_ACCESS_TOKEN" in str(exc.value)


def test_connector_posts_to_the_dataset_events_endpoint():
    session = FakeSession(FakeResponse({"events_received": 1}))
    connector = MetaConnector(
        verify_token="v", access_token="tok", dataset_id="DS1", session=session
    )

    result = connector.send_conversions([{"event_name": "Lead"}])

    assert result == {"events_received": 1}
    assert session.calls[0]["url"].endswith("/v23.0/DS1/events")
    assert session.calls[0]["json"]["data"] == [{"event_name": "Lead"}]


def test_connector_treats_a_meta_error_body_as_a_rejection():
    session = FakeSession(
        FakeResponse({"error": {"type": "OAuthException", "message": "Invalid token"}}, 400)
    )
    connector = MetaConnector(
        verify_token="v", access_token="tok", dataset_id="DS1", session=session
    )

    with pytest.raises(MetaVerificationError) as exc:
        connector.send_conversions([{"event_name": "Lead"}])

    assert "Invalid token" in str(exc.value)


# ------------------------------------------------------------------ command


def test_meta_command_routes():
    from app.growth import commands

    assert commands.route("Meta") == commands.CMD_META
    assert commands.route("мета") == commands.CMD_META
    assert commands.route("/meta") == commands.CMD_META


def test_meta_status_reports_the_required_fields():
    status = MetaStatus(
        connected=True,
        waiting=3,
        sent=25,
        accepted=25,
        rejected=0,
        last_sync=datetime(2026, 8, 8, 14, 35),
    )

    answer = MetaRenderer().render(status, limit=4096, now=datetime(2026, 8, 8, 15, 0))

    assert "Connected" in answer and "YES" in answer
    assert "Events waiting" in answer and "3" in answer
    assert "Events sent" in answer and "25" in answer
    assert "Accepted" in answer
    assert "Rejected" in answer
    assert "Today 14:35" in answer


def test_meta_status_explains_exactly_what_is_missing_without_secrets():
    status = MetaStatus(
        connected=False,
        missing=["META_ACCESS_TOKEN", "META_DATASET_ID"],
        waiting=12,
        by_outcome={OUTCOME_ARRIVED: 9, OUTCOME_LEAD: 3},
    )

    answer = MetaRenderer().render(status, limit=4096)

    assert "NO" in answer
    assert "META_ACCESS_TOKEN" in answer
    assert "META_DATASET_ID" in answer
    assert "Events are queued, not lost." in answer
    assert "Client arrived: 9" in answer


def test_never_synchronised_says_never():
    answer = MetaRenderer().render(MetaStatus(), limit=4096)

    assert "never" in answer


# ---------------------------------------------------------------- sending


class FakeQuery:
    def __init__(self, rows):
        self._rows = rows

    def filter(self, *args):
        return self

    def order_by(self, *args):
        return self

    def limit(self, n):
        return self

    def all(self):
        return self._rows


class FakeSessionDB:
    def __init__(self, rows):
        self.rows = rows
        self.committed = 0

    def query(self, *models):
        return FakeQuery(self.rows)

    def commit(self):
        self.committed += 1


def test_send_pending_marks_everything_rejected_when_meta_refuses(monkeypatch):
    from app.models.meta_conversion import STATUS_PENDING, MetaConversion

    row = MetaConversion(
        outcome=OUTCOME_LEAD,
        event_name="Lead",
        event_id="lead-1",
        event_time=1,
        action_source="business_messaging",
        source_system="colore",
        user_data='{"ph": ["abc"]}',
        status=STATUS_PENDING,
        attempts=0,
    )

    connector = MetaConnector(verify_token="v", access_token="t", dataset_id="d")
    monkeypatch.setattr(meta_sync, "_meta_connector", lambda: connector)
    monkeypatch.setattr(
        connector,
        "send_conversions",
        lambda events: (_ for _ in ()).throw(MetaVerificationError("Invalid token")),
    )

    session = FakeSessionDB([row])
    result = meta_sync.send_pending(session)

    assert result.rejected == 1
    assert result.accepted == 0
    assert row.status == "rejected"
    assert "Invalid token" in row.error


def test_send_pending_refuses_when_not_configured(monkeypatch):
    connector = MetaConnector(verify_token="v")
    monkeypatch.setattr(meta_sync, "_meta_connector", lambda: connector)

    result = meta_sync.send_pending(FakeSessionDB([]))

    assert result.sent == 0
    assert any("META_ACCESS_TOKEN" in error for error in result.errors)
