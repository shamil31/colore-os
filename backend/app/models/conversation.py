from datetime import datetime

from sqlalchemy import DateTime, Integer, String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Conversation(Base):
    __tablename__ = "conversations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    customer_id: Mapped[int] = mapped_column(Integer, ForeignKey("clients.id"), nullable=False)
    primary_channel: Mapped[str] = mapped_column(String(50), nullable=False)
    current_channel: Mapped[str] = mapped_column(String(50), nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )


class Message(Base):
    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    conversation_id: Mapped[int] = mapped_column(Integer, ForeignKey("conversations.id"), nullable=False)
    channel: Mapped[str] = mapped_column(String(50), nullable=False)
    direction: Mapped[str] = mapped_column(String(50), nullable=False)
    content: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
    )
