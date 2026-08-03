"""add claimed_at to approvals

Revision ID: 17221b0f4fe7
Revises: 1bbd0755a983
Create Date: 2026-08-03 21:23:23.002588

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '17221b0f4fe7'
down_revision: Union[str, Sequence[str], None] = '1bbd0755a983'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema.

    Closes a real race in POST /approvals/{id}/decision: reading
    status="pending" and then acting on it were separated by however
    long it takes to schedule resume_analysis, wide enough for two
    concurrent requests against the same approval_id to both pass the
    check before either had written anything. claimed_at lets the
    endpoint claim the approval atomically (a single UPDATE ... WHERE
    status='pending' AND claimed_at IS NULL) without touching status
    itself — that column keeps meaning only the human's actual
    decision, still written exclusively by human_approval_node once the
    graph wakes up and resumes.
    """
    op.add_column('approvals', sa.Column('claimed_at', sa.DateTime(timezone=True), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('approvals', 'claimed_at')
