from datetime import datetime

from sqlalchemy import JSON, Boolean, DateTime, Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class RevenueClient(Base):
    __tablename__ = "revenue_clients"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    altegio_client_id: Mapped[int] = mapped_column(Integer, unique=True, index=True, nullable=False)
    company_id: Mapped[int] = mapped_column(Integer, index=True, nullable=False)

    full_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(50), nullable=True, index=True)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    birthday: Mapped[str | None] = mapped_column(String(50), nullable=True)
    last_visit_date: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    first_visit_date: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    master_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    last_service_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    total_visits: Mapped[int | None] = mapped_column(Integer, nullable=True)
    total_spent: Mapped[float | None] = mapped_column(Float, nullable=True)
    raw_data: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    visit_history_synced_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    last_visit_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    last_service_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    visit_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )
