"""add pr_comment_url to analysis_requests

Revision ID: 1bbd0755a983
Revises: a1c4e9f27b3d
Create Date: 2026-08-02 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '1bbd0755a983'
down_revision: Union[str, Sequence[str], None] = 'a1c4e9f27b3d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema.

    Closes a conscious deferral noted in post_comment_node's docstring
    (Fase 3.3): whether the PR comment actually got posted, and its URL,
    was only ever surfaced transiently over WebSocket, never persisted —
    which meant "PRs comentados" had no real data to be computed from
    for the Fase 4 metrics view. Nullable and with no default: rows
    where post_to_pr was never true, or where posting failed, correctly
    have no URL to show.
    """
    op.add_column('analysis_requests', sa.Column('pr_comment_url', sa.String(length=500), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('analysis_requests', 'pr_comment_url')
