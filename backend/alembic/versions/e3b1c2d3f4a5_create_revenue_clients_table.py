"""Create revenue_clients table

Revision ID: e3b1c2d3f4a5
Revises: d7b60b912b5a
Create Date: 2026-08-01 13:05:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "e3b1c2d3f4a5"
down_revision: Union[str, Sequence[str], None] = "d7b60b912b5a"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "revenue_clients",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("altegio_client_id", sa.Integer(), nullable=False),
        sa.Column("company_id", sa.Integer(), nullable=False),
        sa.Column("full_name", sa.String(length=255), nullable=True),
        sa.Column("phone", sa.String(length=50), nullable=True),
        sa.Column("last_visit_at", sa.DateTime(), nullable=True),
        sa.Column("last_service_name", sa.String(length=255), nullable=True),
        sa.Column("visit_count", sa.Integer(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("altegio_client_id"),
    )
    op.create_index("ix_revenue_clients_altegio_client_id", "revenue_clients", ["altegio_client_id"], unique=True)
    op.create_index("ix_revenue_clients_company_id", "revenue_clients", ["company_id"], unique=False)
    op.create_index("ix_revenue_clients_phone", "revenue_clients", ["phone"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_revenue_clients_phone", table_name="revenue_clients")
    op.drop_index("ix_revenue_clients_company_id", table_name="revenue_clients")
    op.drop_index("ix_revenue_clients_altegio_client_id", table_name="revenue_clients")
    op.drop_table("revenue_clients")
