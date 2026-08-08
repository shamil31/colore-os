"""add scheduler runs

Revision ID: d4e5f6a7b8c9
Revises: c3d4e5f6a7b8
Create Date: 2026-08-08

P0-003. Job executions are persisted because the interval calculation, the
doctor and the Telegram report all need to know when a job last ran, and a log
line cannot answer that across a restart.
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "d4e5f6a7b8c9"
down_revision: Union[str, Sequence[str], None] = "c3d4e5f6a7b8"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "scheduler_runs",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("job_name", sa.String(length=60), nullable=False),
        sa.Column("mode", sa.String(length=20), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("message", sa.Text(), nullable=False, server_default=""),
        sa.Column("summary", sa.Text(), nullable=False, server_default=""),
        sa.Column("error", sa.Text(), nullable=False, server_default=""),
        sa.Column("started_at", sa.DateTime(), nullable=True),
        sa.Column("finished_at", sa.DateTime(), nullable=True),
        sa.Column("duration_ms", sa.Integer(), nullable=False, server_default="0"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_scheduler_runs_id"), "scheduler_runs", ["id"])
    op.create_index(op.f("ix_scheduler_runs_job_name"), "scheduler_runs", ["job_name"])
    op.create_index(op.f("ix_scheduler_runs_status"), "scheduler_runs", ["status"])
    op.create_index(op.f("ix_scheduler_runs_started_at"), "scheduler_runs", ["started_at"])


def downgrade() -> None:
    op.drop_index(op.f("ix_scheduler_runs_started_at"), table_name="scheduler_runs")
    op.drop_index(op.f("ix_scheduler_runs_status"), table_name="scheduler_runs")
    op.drop_index(op.f("ix_scheduler_runs_job_name"), table_name="scheduler_runs")
    op.drop_index(op.f("ix_scheduler_runs_id"), table_name="scheduler_runs")
    op.drop_table("scheduler_runs")
