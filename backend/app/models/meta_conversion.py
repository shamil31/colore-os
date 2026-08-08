from datetime import datetime

from sqlalchemy import DateTime, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base

# Delivery states.
STATUS_QUEUED = "queued"
"""Built from a confirmed outcome, waiting for its first attempt."""

STATUS_SENDING = "sending"
"""Claimed by an in-flight batch. A crash mid-send leaves rows here, and they
are recovered on the next run rather than being lost or double-sent."""

STATUS_SENT = "sent"
"""Meta accepted it."""

STATUS_RETRY = "retry"
"""The attempt failed for a reason that may not repeat — network, timeout,
5xx, rate limit, or a configuration fault that is not the event's own. The
event is intact and will be attempted again after `next_attempt_at`."""

STATUS_PERMANENT_FAILURE = "permanent_failure"
"""Re-sending this exact event can never succeed: the payload is invalid, it
is a duplicate, or it is older than Meta's limit and only gets older. This is
the only state that gives up on an event, and it is reached per event, never
per batch."""

RETRYABLE_STATUSES = (STATUS_QUEUED, STATUS_RETRY, STATUS_SENDING)

# Names used before P0-001. Kept so the migration and any operator query can
# still refer to them.
LEGACY_STATUS_PENDING = "pending"
LEGACY_STATUS_ACCEPTED = "accepted"
LEGACY_STATUS_REJECTED = "rejected"

# The five business outcomes this project reports. Nothing else is ever sent.
OUTCOME_LEAD = "lead_created"
OUTCOME_BOOKED = "appointment_booked"
OUTCOME_CANCELLED = "appointment_cancelled"
OUTCOME_ARRIVED = "client_arrived"
OUTCOME_NO_SHOW = "no_show"


class MetaConversion(Base):
    """One business outcome, queued for the Conversions API.

    A row exists only when the outcome already happened and is recorded in a
    system of record — an appointment state in Altegio, or a real inbound
    message persisted in `growth_events`. There is no code path that creates a
    row from an estimate, a projection, or an inference.

    `event_id` is derived from the source record's identity, so rebuilding the
    queue over the same data produces the same row. That is what makes the
    build idempotent locally, and it is the same value Meta deduplicates on.
    """

    __tablename__ = "meta_conversions"
    __table_args__ = (
        UniqueConstraint("event_id", name="uq_meta_conversions_event_id"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    # What happened, in our vocabulary, and what Meta is told it is called.
    outcome: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    event_name: Mapped[str] = mapped_column(String(50), nullable=False)

    # Deduplication key. Meta: "the event_id and event_name parameters are used
    # to deduplicate events".
    event_id: Mapped[str] = mapped_column(String(120), nullable=False)
    event_time: Mapped[int] = mapped_column(Integer, nullable=False)
    action_source: Mapped[str] = mapped_column(String(30), nullable=False)

    # Where the fact came from, so any row can be traced back to its evidence.
    source_system: Mapped[str] = mapped_column(String(20), nullable=False)
    source_ref: Mapped[str] = mapped_column(String(80), nullable=False, default="")

    # Already SHA256-hashed, per Meta's customer information parameters. Raw
    # phone numbers and emails are never written to this table.
    user_data: Mapped[str] = mapped_column(Text, nullable=False, default="")
    custom_data: Mapped[str] = mapped_column(Text, nullable=False, default="")

    status: Mapped[str] = mapped_column(String(20), nullable=False, default=STATUS_QUEUED, index=True)
    attempts: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    error: Mapped[str] = mapped_column(Text, nullable=False, default="")
    response: Mapped[str] = mapped_column(Text, nullable=False, default="")

    next_attempt_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True, index=True)
    """When a `retry` row becomes eligible again. Null means immediately."""

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    sent_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
