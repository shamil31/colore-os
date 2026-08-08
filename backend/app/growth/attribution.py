"""Turn confirmed business outcomes into Conversions API events.

The rule this module exists to enforce: **an event is only ever built from a
fact that already happened and is recorded somewhere authoritative.** There is
no path from a guess, a projection, or a ratio to a row in `meta_conversions`.

Concretely:

- Appointment states come from Altegio's `attendance` field. Altegio is the
  system of record for appointments, so its answer is the fact.
- `lead_created` comes from a persisted `growth_events` row — an inbound
  message that actually arrived and was processed.

Nothing is inferred in between. A booking is not assumed from a lead, and a
visit is not assumed from a booking: Altegio says whether the client arrived,
and until it does, no arrival event exists.

Field contracts verified 2026-08-08 against Meta's Conversions API
documentation; quoted in `docs/research/META_ATTRIBUTION_FLOW.md`.
"""

from __future__ import annotations

import hashlib
import json
import logging
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from app.growth.business_data import (
    ATTENDANCE_ARRIVED,
    ATTENDANCE_NO_SHOW,
    BusinessSnapshot,
)
from app.models.meta_conversion import (
    OUTCOME_ARRIVED,
    OUTCOME_BOOKED,
    OUTCOME_CANCELLED,
    OUTCOME_LEAD,
    OUTCOME_NO_SHOW,
)

logger = logging.getLogger("colore.attribution")

# Meta standard event names where one fits the outcome, custom names where none
# does. Custom event names are permitted by the Conversions API.
EVENT_NAMES = {
    OUTCOME_LEAD: "Lead",
    OUTCOME_BOOKED: "Schedule",
    OUTCOME_CANCELLED: "AppointmentCancelled",
    OUTCOME_ARRIVED: "Purchase",
    OUTCOME_NO_SHOW: "NoShow",
}

# action_source allowed values are fixed by Meta: email, website, app,
# phone_call, chat, physical_store, system_generated, business_messaging, other.
ACTION_SOURCES = {
    OUTCOME_LEAD: "business_messaging",
    OUTCOME_BOOKED: "business_messaging",
    OUTCOME_CANCELLED: "business_messaging",
    # The client physically came to the salon. That is the whole point of
    # reporting it: Meta cannot observe it any other way.
    OUTCOME_ARRIVED: "physical_store",
    OUTCOME_NO_SHOW: "physical_store",
}


@dataclass
class ConversionEvent:
    outcome: str
    event_id: str
    event_time: int
    user_data: dict[str, Any] = field(default_factory=dict)
    custom_data: dict[str, Any] = field(default_factory=dict)
    source_system: str = ""
    source_ref: str = ""

    @property
    def event_name(self) -> str:
        return EVENT_NAMES[self.outcome]

    @property
    def action_source(self) -> str:
        return ACTION_SOURCES[self.outcome]

    def payload(self) -> dict[str, Any]:
        """The exact object sent to Meta."""
        body: dict[str, Any] = {
            "event_name": self.event_name,
            "event_time": self.event_time,
            "event_id": self.event_id,
            "action_source": self.action_source,
            "user_data": self.user_data,
        }
        if self.custom_data:
            body["custom_data"] = self.custom_data
        return body


# ------------------------------------------------------------------ hashing


def _sha256(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def hash_phone(value: Any) -> str:
    """`ph`: "Remove symbols, letters, and any leading zeros… Always include the country code"."""
    digits = re.sub(r"\D", "", str(value or ""))
    digits = digits.lstrip("0")
    if len(digits) < 8:
        return ""
    return _sha256(digits)


def hash_email(value: Any) -> str:
    """`em`: "Trim any leading and trailing spaces. Convert all characters to lowercase"."""
    text = str(value or "").strip().lower()
    if "@" not in text:
        return ""
    return _sha256(text)


def hash_name(value: Any) -> str:
    """`fn`/`ln`: "Lowercase only with no punctuation"."""
    text = re.sub(r"[^\w\s]", "", str(value or ""), flags=re.UNICODE).strip().lower()
    if not text:
        return ""
    return _sha256(text)


def build_user_data(*, phone: Any = None, email: Any = None, first: Any = None, last: Any = None,
                    external_id: Any = None) -> dict[str, list[str]]:
    """Matching fields, hashed. Raw PII never leaves this function.

    Meta expects each customer parameter as a list, and every one of these is on
    the "must be hashed" list. `client_ip_address`, `client_user_agent`, `fbc`
    and `fbp` would be sent unhashed — we have none of them, because these
    outcomes happen in a salon rather than in a browser.
    """
    data: dict[str, list[str]] = {}

    for key, value in (
        ("ph", hash_phone(phone)),
        ("em", hash_email(email)),
        ("fn", hash_name(first)),
        ("ln", hash_name(last)),
    ):
        if value:
            data[key] = [value]

    if external_id:
        data["external_id"] = [_sha256(str(external_id))]

    return data


# ------------------------------------------------------------- time helpers


def _unix(value: Any) -> int | None:
    """Meta: "A Unix timestamp in seconds indicating when the actual event occurred"."""
    if isinstance(value, datetime):
        moment = value if value.tzinfo else value.replace(tzinfo=timezone.utc)
        return int(moment.timestamp())

    if not isinstance(value, str) or not value.strip():
        return None

    text = value.strip().replace("Z", "+00:00")
    # Altegio returns both "2026-08-06 09:00:00" and "2026-07-18T11:46:48+0200".
    if len(text) >= 5 and (text[-5] in "+-") and ":" not in text[-5:]:
        text = f"{text[:-2]}:{text[-2:]}"
    try:
        parsed = datetime.fromisoformat(text)
    except ValueError:
        return None

    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return int(parsed.timestamp())


# ------------------------------------------------------------------ builders


def event_from_record(record: dict[str, Any]) -> list[ConversionEvent]:
    """Everything Altegio confirms about one appointment.

    A booked appointment always yields `appointment_booked`. Its outcome yields
    at most one more event, and only when Altegio has actually recorded one:
    `attendance` 1 is arrival, -1 is a no-show, and 0 (pending) yields nothing,
    because nothing has happened yet.
    """
    record_id = record.get("id")
    if record_id is None:
        return []

    client = record.get("client") or {}
    user_data = build_user_data(
        phone=client.get("phone"),
        email=client.get("email"),
        first=client.get("name"),
        last=client.get("surname"),
        external_id=client.get("id"),
    )

    if not _has_strong_identifier(user_data):
        # A name is not an identifier. Meta can only attribute an offline event
        # to a person through a strong key — phone or email — and `external_id`
        # is meaningless here because nothing sends the matching id from the ad
        # side. An event with only `fn`/`ln` would be unattributable noise.
        return []

    events: list[ConversionEvent] = []

    booked_at = _unix(record.get("create_date"))
    if booked_at is not None:
        events.append(
            ConversionEvent(
                outcome=OUTCOME_BOOKED,
                event_id=f"booked-{record_id}",
                event_time=booked_at,
                user_data=user_data,
                source_system="altegio",
                source_ref=str(record_id),
            )
        )

    if record.get("deleted"):
        cancelled_at = _unix(record.get("last_change_date")) or booked_at
        if cancelled_at is not None:
            events.append(
                ConversionEvent(
                    outcome=OUTCOME_CANCELLED,
                    event_id=f"cancelled-{record_id}",
                    event_time=cancelled_at,
                    user_data=user_data,
                    source_system="altegio",
                    source_ref=str(record_id),
                )
            )
        return events

    visit_at = _unix(record.get("date"))
    attendance = record.get("attendance")

    if attendance == ATTENDANCE_ARRIVED and visit_at is not None:
        events.append(
            ConversionEvent(
                outcome=OUTCOME_ARRIVED,
                event_id=f"arrived-{record_id}",
                event_time=visit_at,
                user_data=user_data,
                custom_data=_value_of(record),
                source_system="altegio",
                source_ref=str(record_id),
            )
        )
    elif attendance == ATTENDANCE_NO_SHOW and visit_at is not None:
        events.append(
            ConversionEvent(
                outcome=OUTCOME_NO_SHOW,
                event_id=f"noshow-{record_id}",
                event_time=visit_at,
                user_data=user_data,
                source_system="altegio",
                source_ref=str(record_id),
            )
        )

    return events


def _has_strong_identifier(user_data: dict[str, list[str]]) -> bool:
    return bool(user_data.get("ph") or user_data.get("em"))


def _value_of(record: dict[str, Any]) -> dict[str, Any]:
    """Money actually recorded against the visit, or nothing at all.

    The currency comes from configuration and is never assumed. Meta treats
    `value` as the number it optimises the budget against, and this salon
    prices in one currency while its ad account bills in another — a wrong
    guess would misstate every visit by roughly a hundredfold. With no
    configured currency the event is sent without a value, which is valid and
    honest, rather than with a number nobody verified.
    """
    from app.core.config import settings

    currency = (settings.BUSINESS_CURRENCY or "").strip().upper()
    if not currency:
        return {}

    total = 0.0
    for service in record.get("services") or []:
        cost = service.get("cost_to_pay", service.get("cost"))
        if isinstance(cost, (int, float)):
            total += float(cost)

    if total <= 0:
        return {}

    return {"value": round(total, 2), "currency": currency}


def event_from_lead(event: Any) -> list[ConversionEvent]:
    """A real inbound message that Growth AI processed.

    Confirmed by our own record of the conversation rather than by Altegio —
    Altegio has no concept of a lead. The event is only built for a persisted
    row, never for a message in flight.
    """
    if getattr(event, "id", None) is None:
        return []

    user_data = build_user_data(phone=getattr(event, "sender_ref", ""))
    if not user_data:
        # Instagram IGSID is app-scoped and is not a phone. No matching field,
        # no event — rather than an event Meta cannot attribute to anyone.
        return []

    when = _unix(getattr(event, "received_at", None))
    if when is None:
        return []

    return [
        ConversionEvent(
            outcome=OUTCOME_LEAD,
            event_id=f"lead-{event.id}",
            event_time=when,
            user_data=user_data,
            source_system="colore",
            source_ref=str(event.id),
        )
    ]


def build_events(snapshot: BusinessSnapshot, leads: list[Any]) -> list[ConversionEvent]:
    events: list[ConversionEvent] = []
    for record in snapshot.records:
        events.extend(event_from_record(record))
    for record in snapshot.cancelled_records:
        events.extend(event_from_record(record))
    for lead in leads:
        events.extend(event_from_lead(lead))
    return events


def dumps(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True)
