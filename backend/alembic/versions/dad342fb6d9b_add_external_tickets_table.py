"""add external_tickets table

Revision ID: dad342fb6d9b
Revises: a1c47e9f2b06
Create Date: 2026-07-28 20:38:14.226651

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'dad342fb6d9b'
down_revision: Union[str, Sequence[str], None] = 'a1c47e9f2b06'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table('external_tickets',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('ticket_id', sa.Integer(), nullable=False),
    sa.Column('summary', sa.Text(), nullable=False),
    sa.Column('status', sa.String(length=20), server_default=sa.text("'created'"), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['ticket_id'], ['tickets.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_external_tickets_ticket_id'), 'external_tickets', ['ticket_id'], unique=True)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_external_tickets_ticket_id'), table_name='external_tickets')
    op.drop_table('external_tickets')