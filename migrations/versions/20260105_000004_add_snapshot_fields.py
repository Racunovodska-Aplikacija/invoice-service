"""add snapshot fields

Revision ID: 20260105_000004
Revises: 20260105_000003
Create Date: 2026-01-05

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '20260105_000004'
down_revision = '20260105_000003'
branch_labels = None
depends_on = None


def upgrade():
    # Add snapshot fields for efficient list display
    op.add_column('invoices', sa.Column('company_name', sa.String(), nullable=True))
    op.add_column('invoices', sa.Column('partner_name', sa.String(), nullable=True))
    op.add_column('invoices', sa.Column('total', sa.Numeric(10, 2), nullable=True))


def downgrade():
    op.drop_column('invoices', 'total')
    op.drop_column('invoices', 'partner_name')
    op.drop_column('invoices', 'company_name')
