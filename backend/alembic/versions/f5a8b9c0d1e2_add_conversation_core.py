"""Add conversation core tables

Revision ID: f5a8b9c0d1e2
Revises: c4d5e6f7a8b9
Create Date: 2026-08-06 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f5a8b9c0d1e2'
down_revision: Union[str, Sequence[str], None] = 'c4d5e6f7a8b9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create conversations table
    op.create_table(
        'conversations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('customer_id', sa.Integer(), nullable=False),
        sa.Column('primary_channel', sa.String(length=50), nullable=False),
        sa.Column('current_channel', sa.String(length=50), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['customer_id'], ['clients.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_conversations_id'), 'conversations', ['id'], unique=False)

    # Create messages table
    op.create_table(
        'messages',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('conversation_id', sa.Integer(), nullable=False),
        sa.Column('channel', sa.String(length=50), nullable=False),
        sa.Column('direction', sa.String(length=50), nullable=False),
        sa.Column('content', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['conversation_id'], ['conversations.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_messages_id'), 'messages', ['id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_messages_id'), table_name='messages')
    op.drop_table('messages')
    op.drop_index(op.f('ix_conversations_id'), table_name='conversations')
    op.drop_table('conversations')
