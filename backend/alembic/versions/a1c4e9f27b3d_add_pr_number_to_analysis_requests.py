"""add pr_number to analysis_requests

Revision ID: a1c4e9f27b3d
Revises: f9bab08a7d00
Create Date: 2026-08-02 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'a1c4e9f27b3d'
down_revision: Union[str, Sequence[str], None] = 'f9bab08a7d00'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('analysis_requests', sa.Column('pr_number', sa.Integer(), nullable=True))
    op.create_check_constraint(
        'ck_analysis_requests_post_to_pr_requires_pr_number',
        'analysis_requests',
        "post_to_pr = false OR (post_to_pr = true AND source_type = 'github_repo' AND pr_number IS NOT NULL)",
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint('ck_analysis_requests_post_to_pr_requires_pr_number', 'analysis_requests', type_='check')
    op.drop_column('analysis_requests', 'pr_number')
