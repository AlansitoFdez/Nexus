"""redesign approvals to reference analysis_request instead of ticket, drop tickets table

Revision ID: f9bab08a7d00
Revises: f744bdb8f237
Create Date: 2026-08-01 18:07:02.876048

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = 'f9bab08a7d00'
down_revision: Union[str, Sequence[str], None] = 'f744bdb8f237'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Approvals del dominio de tickets no tienen equivalente en
    # analysis_request_id — se retiran junto con el dominio, no son
    # datos que necesitemos preservar.
    op.execute("DELETE FROM approvals")

    op.drop_constraint(op.f('approvals_ticket_id_fkey'), 'approvals', type_='foreignkey')
    op.drop_index(op.f('ix_approvals_ticket_id'), table_name='approvals')
    op.drop_column('approvals', 'ticket_id')

    op.add_column('approvals', sa.Column('analysis_request_id', sa.Integer(), nullable=False))
    op.create_index(op.f('ix_approvals_analysis_request_id'), 'approvals', ['analysis_request_id'], unique=False)
    op.create_foreign_key(
        'approvals_analysis_request_id_fkey', 'approvals', 'analysis_requests', ['analysis_request_id'], ['id']
    )

    # Ahora que nada depende ya de tickets, es seguro borrarla.
    op.drop_table('tickets')


def downgrade() -> None:
    """Downgrade schema."""
    # Aviso: los approvals creados bajo el esquema nuevo (analysis_request_id)
    # no tienen ticket_id válido al que volver — se pierden al revertir,
    # igual que las filas de tickets se perdieron al aplicar.
    op.execute("DELETE FROM approvals")

    op.create_table('tickets',
        sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
        sa.Column('original_text', sa.TEXT(), autoincrement=False, nullable=False),
        sa.Column('cleaned_text', sa.TEXT(), autoincrement=False, nullable=True),
        sa.Column('classification', sa.VARCHAR(length=50), autoincrement=False, nullable=True),
        sa.Column('diagnosis', sa.TEXT(), autoincrement=False, nullable=True),
        sa.Column('proposed_response', sa.TEXT(), autoincrement=False, nullable=True),
        sa.Column('escalated', sa.BOOLEAN(), server_default=sa.text('false'), autoincrement=False, nullable=False),
        sa.Column('node_history', postgresql.JSONB(astext_type=sa.Text()), server_default=sa.text("'[]'::jsonb"), autoincrement=False, nullable=False),
        sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), autoincrement=False, nullable=False),
        sa.Column('updated_at', postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=True),
        sa.PrimaryKeyConstraint('id', name=op.f('tickets_pkey'))
    )

    op.drop_constraint('approvals_analysis_request_id_fkey', 'approvals', type_='foreignkey')
    op.drop_index(op.f('ix_approvals_analysis_request_id'), table_name='approvals')
    op.drop_column('approvals', 'analysis_request_id')

    op.add_column('approvals', sa.Column('ticket_id', sa.INTEGER(), autoincrement=False, nullable=False))
    op.create_index(op.f('ix_approvals_ticket_id'), 'approvals', ['ticket_id'], unique=False)
    op.create_foreign_key(op.f('approvals_ticket_id_fkey'), 'approvals', 'tickets', ['ticket_id'], ['id'])