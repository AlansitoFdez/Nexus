"""add full-text search to knowledge base

Revision ID: d7bf4d3eadfd
Revises: 12d52a65ec7c
Create Date: 2026-07-28 19:26:04.208031

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import TSVECTOR


revision: str = 'a1c47e9f2b06'
down_revision: Union[str, Sequence[str], None] = '12d52a65ec7c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        'knowledge_base',
        sa.Column(
            'search_vector',
            TSVECTOR,
            sa.Computed(
                "to_tsvector('spanish', coalesce(title, '') || ' ' || coalesce(content, ''))",
                persisted=True,
            ),
        ),
    )
    op.create_index(
        'ix_knowledge_base_search_vector',
        'knowledge_base',
        ['search_vector'],
        postgresql_using='gin',
    )


def downgrade() -> None:
    op.drop_index('ix_knowledge_base_search_vector', table_name='knowledge_base')
    op.drop_column('knowledge_base', 'search_vector')