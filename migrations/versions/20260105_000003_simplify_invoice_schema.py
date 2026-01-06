"""simplify invoice schema - remove snapshots and totals, add service_date

Revision ID: 20260105_000003
Revises: 20260104_000002
Create Date: 2026-01-05

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "20260105_000003"
down_revision = "20260104_000002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # invoices: drop snapshot fields, total, and created_at
    op.drop_column("invoices", "partner_name")
    op.drop_column("invoices", "company_name")
    op.drop_column("invoices", "total")
    op.drop_column("invoices", "created_at")
    
    # invoices: rename comment to notes
    op.alter_column("invoices", "comment", new_column_name="notes")
    
    # invoices: add service_date
    op.add_column(
        "invoices",
        sa.Column("service_date", sa.DateTime(), nullable=False, server_default=sa.text("NOW()")),
    )
    
    # invoice_lines: drop snapshot fields
    op.drop_column("invoice_lines", "description")
    op.drop_column("invoice_lines", "unit_price")


def downgrade() -> None:
    # invoice_lines: restore snapshot fields
    op.add_column(
        "invoice_lines",
        sa.Column("description", sa.String(), nullable=False, server_default=""),
    )
    op.add_column(
        "invoice_lines",
        sa.Column("unit_price", sa.Numeric(10, 2), nullable=False, server_default="0"),
    )
    
    # invoices: drop service_date
    op.drop_column("invoices", "service_date")
    
    # invoices: rename notes back to comment
    op.alter_column("invoices", "notes", new_column_name="comment")
    
    # invoices: restore snapshot fields, total, and created_at
    op.add_column(
        "invoices",
        sa.Column("partner_name", sa.String(), nullable=False, server_default=""),
    )
    op.add_column(
        "invoices",
        sa.Column("company_name", sa.String(), nullable=False, server_default=""),
    )
    op.add_column(
        "invoices",
        sa.Column("total", sa.Numeric(10, 2), nullable=False, server_default="0"),
    )
    op.add_column(
        "invoices",
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("NOW()")),
    )
