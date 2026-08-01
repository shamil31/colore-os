from datetime import datetime

from sqlalchemy import JSON, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class RevenueClientVisit(Base):
    __tablename__ = "revenue_client_visits"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    revenue_client_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("revenue_clients.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )

    altegio_record_id: Mapped[int] = mapped_column(Integer, unique=True, index=True, nullable=False)

    last_visit_date: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    previous_visit_date: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    services: Mapped[list | dict | None] = mapped_column(JSON, nullable=True)
    master: Mapped[str | None] = mapped_column(String(255), nullable=True)
    amount: Mapped[float | None] = mapped_column(Float, nullable=True)
    visit_status: Mapped[str | None] = mapped_column(String(100), nullable=True)

    raw_data: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )
