"""meta conversion delivery states

Revision ID: c3d4e5f6a7b8
Revises: b2c3d4e5f6a7
Create Date: 2026-08-08

P0-001. The queue previously had one failure state, `rejected`, and it was
terminal — so a network blip or a single over-age event destroyed every event
in the batch with no way back. This introduces the delivery states and the
`next_attempt_at` column that make a failed send recoverable.

Existing rows are remapped, not dropped:

    pending  -> queued
    accepted -> sent
    rejected -> retry   (they were never given a fair attempt)
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "c3d4e5f6a7b8"
down_revision: Union[str, Sequence[str], None] = "b2c3d4e5f6a7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "meta_conversions",
        sa.Column("next_attempt_at", sa.DateTime(), nullable=True),
    )
    op.create_index(
        op.f("ix_meta_conversions_next_attempt_at"),
        "meta_conversions",
        ["next_attempt_at"],
    )

    op.alter_column(
        "meta_conversions",
        "status",
        server_default="queued",
        existing_type=sa.String(length=20),
        existing_nullable=False,
    )

    # Anything previously marked rejected returns to the queue: under the old
    # code it may have been condemned for a transient failure.
    op.execute("UPDATE meta_conversions SET status = 'queued' WHERE status = 'pending'")
    op.execute("UPDATE meta_conversions SET status = 'sent' WHERE status = 'accepted'")
    op.execute("UPDATE meta_conversions SET status = 'retry' WHERE status = 'rejected'")


def downgrade() -> None:
    op.execute("UPDATE meta_conversions SET status = 'pending' WHERE status IN ('queued', 'sending')")
    op.execute("UPDATE meta_conversions SET status = 'accepted' WHERE status = 'sent'")
    op.execute(
        "UPDATE meta_conversions SET status = 'rejected' "
        "WHERE status IN ('retry', 'permanent_failure')"
    )

    op.alter_column(
        "meta_conversions",
        "status",
        server_default="pending",
        existing_type=sa.String(length=20),
        existing_nullable=False,
    )
    op.drop_index(op.f("ix_meta_conversions_next_attempt_at"), table_name="meta_conversions")
    op.drop_column("meta_conversions", "next_attempt_at")
