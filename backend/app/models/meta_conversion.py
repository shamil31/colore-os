from datetime import datetime

from sqlalchemy import DateTime, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base

# Queue lifecycle.
STATUS_PENDING = "pending"
"""Built from a confirmed outcome, not yet sent."""

STATUS_SENT = "sent"
"""Handed to Meta; the response has not been classified yet."""

STATUS_ACCEPTED = "accepted"
"""Meta acknowledged the event."""

STATUS_REJECTED = "rejected"
"""Meta refused it. `error` holds the reason verbatim."""

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

    status: Mapped[str] = mapped_column(String(20), nullable=False, default=STATUS_PENDING, index=True)
    attempts: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    error: Mapped[str] = mapped_column(Text, nullable=False, default="")
    response: Mapped[str] = mapped_column(Text, nullable=False, default="")

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    sent_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
