"""Add RevenueClient import fields

Revision ID: 9e7a2b3c4d5e
Revises: e3b1c2d3f4a5
Create Date: 2026-08-01 12:35:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "9e7a2b3c4d5e"
down_revision: Union[str, Sequence[str], None] = "e3b1c2d3f4a5"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("revenue_clients") as batch_op:
        batch_op.add_column(sa.Column("email", sa.String(length=255), nullable=True))
        batch_op.add_column(sa.Column("birthday", sa.String(length=50), nullable=True))
        batch_op.add_column(sa.Column("last_visit_date", sa.DateTime(), nullable=True))
        batch_op.add_column(sa.Column("first_visit_date", sa.DateTime(), nullable=True))
        batch_op.add_column(sa.Column("master_id", sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column("last_service_id", sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column("total_visits", sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column("total_spent", sa.Float(), nullable=True))
        batch_op.add_column(sa.Column("raw_data", sa.JSON(), nullable=True))


def downgrade() -> None:
    with op.batch_alter_table("revenue_clients") as batch_op:
        batch_op.drop_column("raw_data")
        batch_op.drop_column("total_spent")
        batch_op.drop_column("total_visits")
        batch_op.drop_column("last_service_id")
        batch_op.drop_column("master_id")
        batch_op.drop_column("first_visit_date")
        batch_op.drop_column("last_visit_date")
        batch_op.drop_column("birthday")
        batch_op.drop_column("email")
