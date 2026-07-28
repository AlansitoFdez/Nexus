"""add notifications table

Revision ID: 3f2af789409e
Revises: dad342fb6d9b
Create Date: 2026-07-28 21:52:18.889445

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3f2af789409e'
down_revision: Union[str, Sequence[str], None] = 'dad342fb6d9b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table('notifications',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('message', sa.Text(), nullable=False),
    sa.Column('urgency', sa.String(length=20), nullable=False),
    sa.Column('channel', sa.String(length=20), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('notifications')