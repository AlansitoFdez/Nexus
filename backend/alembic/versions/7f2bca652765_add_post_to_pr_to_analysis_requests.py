"""add post_to_pr to analysis_requests

Revision ID: 7f2bca652765
Revises: fc10589eb440
Create Date: 2026-07-30 23:11:56.266212

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '7f2bca652765'
down_revision: Union[str, Sequence[str], None] = 'fc10589eb440'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('analysis_requests', sa.Column('post_to_pr', sa.Boolean(), server_default=sa.text('false'), nullable=False))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('analysis_requests', 'post_to_pr')