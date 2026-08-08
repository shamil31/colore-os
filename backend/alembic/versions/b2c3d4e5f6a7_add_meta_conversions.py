"""add meta conversions queue

Revision ID: b2c3d4e5f6a7
Revises: a1b2c3d4e5f6
Create Date: 2026-08-08

The attribution queue. Every row is a business outcome that already happened
and is recorded in a system of record. `event_id` is unique because it is
derived from the source record's identity: rebuilding the queue over the same
data cannot duplicate a row, and Meta deduplicates on the same value.
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "b2c3d4e5f6a7"
down_revision: Union[str, Sequence[str], None] = "a1b2c3d4e5f6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "meta_conversions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("outcome", sa.String(length=50), nullable=False),
        sa.Column("event_name", sa.String(length=50), nullable=False),
        sa.Column("event_id", sa.String(length=120), nullable=False),
        sa.Column("event_time", sa.Integer(), nullable=False),
        sa.Column("action_source", sa.String(length=30), nullable=False),
        sa.Column("source_system", sa.String(length=20), nullable=False),
        sa.Column("source_ref", sa.String(length=80), nullable=False, server_default=""),
        sa.Column("user_data", sa.Text(), nullable=False, server_default=""),
        sa.Column("custom_data", sa.Text(), nullable=False, server_default=""),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="pending"),
        sa.Column("attempts", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("error", sa.Text(), nullable=False, server_default=""),
        sa.Column("response", sa.Text(), nullable=False, server_default=""),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("sent_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("event_id", name="uq_meta_conversions_event_id"),
    )
    op.create_index(op.f("ix_meta_conversions_id"), "meta_conversions", ["id"])
    op.create_index(op.f("ix_meta_conversions_outcome"), "meta_conversions", ["outcome"])
    op.create_index(op.f("ix_meta_conversions_status"), "meta_conversions", ["status"])


def downgrade() -> None:
    op.drop_index(op.f("ix_meta_conversions_status"), table_name="meta_conversions")
    op.drop_index(op.f("ix_meta_conversions_outcome"), table_name="meta_conversions")
    op.drop_index(op.f("ix_meta_conversions_id"), table_name="meta_conversions")
    op.drop_table("meta_conversions")
