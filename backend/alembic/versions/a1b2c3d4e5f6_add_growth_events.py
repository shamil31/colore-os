"""add growth events and actions

Revision ID: a1b2c3d4e5f6
Revises: f5a8b9c0d1e2
Create Date: 2026-08-08

The trace for the Growth AI flow. Deduplication lives in the unique constraint
on (source, external_id): Meta retries a failed delivery over 36 hours and
states that deduplication is the receiver's job, so this has to survive a
restart rather than live in memory.
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "a1b2c3d4e5f6"
down_revision: Union[str, Sequence[str], None] = "f5a8b9c0d1e2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "growth_events",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("source", sa.String(length=50), nullable=False),
        sa.Column("external_id", sa.String(length=255), nullable=False),
        sa.Column("sender_ref", sa.String(length=255), nullable=False, server_default=""),
        sa.Column("sender_name", sa.String(length=255), nullable=False, server_default=""),
        sa.Column("channel_ref", sa.String(length=255), nullable=False, server_default=""),
        sa.Column("text", sa.Text(), nullable=False, server_default=""),
        sa.Column("status", sa.String(length=50), nullable=False, server_default="received"),
        sa.Column("skip_reason", sa.String(length=100), nullable=False, server_default=""),
        sa.Column("intent", sa.String(length=50), nullable=False, server_default=""),
        sa.Column("priority", sa.String(length=20), nullable=False, server_default=""),
        sa.Column("decision_reason", sa.Text(), nullable=False, server_default=""),
        sa.Column("raw", sa.Text(), nullable=False, server_default=""),
        sa.Column("received_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("source", "external_id", name="uq_growth_events_source_external_id"),
    )
    op.create_index(op.f("ix_growth_events_id"), "growth_events", ["id"])
    op.create_index(op.f("ix_growth_events_source"), "growth_events", ["source"])
    op.create_index(op.f("ix_growth_events_received_at"), "growth_events", ["received_at"])

    op.create_table(
        "growth_actions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("event_id", sa.Integer(), nullable=False),
        sa.Column("connector", sa.String(length=50), nullable=False),
        sa.Column("capability", sa.String(length=100), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("request", sa.Text(), nullable=False, server_default=""),
        sa.Column("response", sa.Text(), nullable=False, server_default=""),
        sa.Column("error", sa.Text(), nullable=False, server_default=""),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["event_id"], ["growth_events.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_growth_actions_id"), "growth_actions", ["id"])
    op.create_index(op.f("ix_growth_actions_event_id"), "growth_actions", ["event_id"])


def downgrade() -> None:
    op.drop_index(op.f("ix_growth_actions_event_id"), table_name="growth_actions")
    op.drop_index(op.f("ix_growth_actions_id"), table_name="growth_actions")
    op.drop_table("growth_actions")
    op.drop_index(op.f("ix_growth_events_received_at"), table_name="growth_events")
    op.drop_index(op.f("ix_growth_events_source"), table_name="growth_events")
    op.drop_index(op.f("ix_growth_events_id"), table_name="growth_events")
    op.drop_table("growth_events")
