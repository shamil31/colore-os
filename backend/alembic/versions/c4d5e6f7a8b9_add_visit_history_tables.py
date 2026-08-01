"""Add visit history tables

Revision ID: c4d5e6f7a8b9
Revises: 9e7a2b3c4d5e
Create Date: 2026-08-01 13:40:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "c4d5e6f7a8b9"
down_revision: Union[str, Sequence[str], None] = "9e7a2b3c4d5e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("revenue_clients") as batch_op:
        batch_op.add_column(sa.Column("visit_history_synced_at", sa.DateTime(), nullable=True))

    op.create_table(
        "revenue_client_visits",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("revenue_client_id", sa.Integer(), nullable=False),
        sa.Column("altegio_record_id", sa.Integer(), nullable=False),
        sa.Column("last_visit_date", sa.DateTime(), nullable=True),
        sa.Column("previous_visit_date", sa.DateTime(), nullable=True),
        sa.Column("services", sa.JSON(), nullable=True),
        sa.Column("master", sa.String(length=255), nullable=True),
        sa.Column("amount", sa.Float(), nullable=True),
        sa.Column("visit_status", sa.String(length=100), nullable=True),
        sa.Column("raw_data", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["revenue_client_id"], ["revenue_clients.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("altegio_record_id"),
    )
    op.create_index("ix_revenue_client_visits_revenue_client_id", "revenue_client_visits", ["revenue_client_id"], unique=False)
    op.create_index("ix_revenue_client_visits_altegio_record_id", "revenue_client_visits", ["altegio_record_id"], unique=True)


def downgrade() -> None:
    op.drop_index("ix_revenue_client_visits_altegio_record_id", table_name="revenue_client_visits")
    op.drop_index("ix_revenue_client_visits_revenue_client_id", table_name="revenue_client_visits")
    op.drop_table("revenue_client_visits")

    with op.batch_alter_table("revenue_clients") as batch_op:
        batch_op.drop_column("visit_history_synced_at")
