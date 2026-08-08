from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base

# Event lifecycle.
STATUS_RECEIVED = "received"
STATUS_PROCESSED = "processed"
STATUS_SKIPPED = "skipped"
STATUS_FAILED = "failed"


class GrowthEvent(Base):
    """One inbound platform event, and what Growth AI decided about it.

    Persisted rather than held in memory because deduplication has to survive a
    restart: Meta retries a failed delivery "over the next 36 hours", and
    explicitly states that "your server should handle deduplication in these
    cases". An in-memory set would forget every retry window on deploy.
    """

    __tablename__ = "growth_events"
    __table_args__ = (
        # The dedup key. A platform message id is unique per platform, so the
        # pair is what makes a retry a no-op.
        UniqueConstraint("source", "external_id", name="uq_growth_events_source_external_id"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    source: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    external_id: Mapped[str] = mapped_column(String(255), nullable=False)
    sender_ref: Mapped[str] = mapped_column(String(255), nullable=False, default="")
    sender_name: Mapped[str] = mapped_column(String(255), nullable=False, default="")
    channel_ref: Mapped[str] = mapped_column(String(255), nullable=False, default="")
    text: Mapped[str] = mapped_column(Text, nullable=False, default="")

    status: Mapped[str] = mapped_column(String(50), nullable=False, default=STATUS_RECEIVED)
    skip_reason: Mapped[str] = mapped_column(String(100), nullable=False, default="")

    intent: Mapped[str] = mapped_column(String(50), nullable=False, default="")
    priority: Mapped[str] = mapped_column(String(20), nullable=False, default="")
    decision_reason: Mapped[str] = mapped_column(Text, nullable=False, default="")

    raw: Mapped[str] = mapped_column(Text, nullable=False, default="")

    received_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)


class GrowthAction(Base):
    """One connector call made because of an event. The other half of the trace."""

    __tablename__ = "growth_actions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    event_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("growth_events.id"), nullable=False, index=True
    )

    connector: Mapped[str] = mapped_column(String(50), nullable=False)
    capability: Mapped[str] = mapped_column(String(100), nullable=False)
    # ok | dry_run | error — never a boolean. "Sent" and "not sent, there is no
    # token" must not look alike here.
    status: Mapped[str] = mapped_column(String(20), nullable=False)

    request: Mapped[str] = mapped_column(Text, nullable=False, default="")
    response: Mapped[str] = mapped_column(Text, nullable=False, default="")
    error: Mapped[str] = mapped_column(Text, nullable=False, default="")

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
