"""add check constraints for status and severity domains

Revision ID: 3d7394b8ba6d
Revises: 17221b0f4fe7
Create Date: 2026-08-04 16:19:27.616040

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3d7394b8ba6d'
down_revision: Union[str, Sequence[str], None] = '17221b0f4fe7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema.

    --autogenerate produced an empty migration for all three of these —
    Alembic's diff doesn't pick up new CheckConstraints by default, only
    columns/indexes/FKs — so these three are written by hand, same
    principle as always reviewing the generated file before applying it.

    status/severity are the truly fixed domains (Fase 4.2 review, see
    FindingCreate's docstring for why Finding.specialist deliberately
    isn't guaranteed here too).
    """
    op.create_check_constraint(
        "ck_analysis_requests_valid_status",
        "analysis_requests",
        "status IN ('pending', 'running', 'completed', 'completed_with_errors', 'failed')",
    )
    op.create_check_constraint(
        "ck_approvals_valid_status",
        "approvals",
        "status IN ('pending', 'approved', 'rejected')",
    )
    op.create_check_constraint(
        "ck_findings_valid_severity",
        "findings",
        "severity IN ('critical', 'high', 'medium', 'low')",
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint("ck_findings_valid_severity", "findings", type_="check")
    op.drop_constraint("ck_approvals_valid_status", "approvals", type_="check")
    op.drop_constraint("ck_analysis_requests_valid_status", "analysis_requests", type_="check")
