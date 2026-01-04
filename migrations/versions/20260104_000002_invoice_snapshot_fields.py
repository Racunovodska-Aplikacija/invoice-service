"""invoice snapshot fields; remove subtotal/tax_total

Revision ID: 20260104_000002
Revises: 20260104_000001
Create Date: 2026-01-04

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "20260104_000002"
down_revision = "20260104_000001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # invoices: add snapshot names
    op.add_column(
        "invoices",
        sa.Column("partner_name", sa.String(), nullable=False, server_default=""),
    )
    op.add_column(
        "invoices",
        sa.Column("company_name", sa.String(), nullable=False, server_default=""),
    )

    # invoice_lines: store snapshot line info so we don't call product-service
    op.add_column(
        "invoice_lines",
        sa.Column("description", sa.String(), nullable=False, server_default=""),
    )
    op.add_column(
        "invoice_lines",
        sa.Column("unit_price", sa.Numeric(10, 2), nullable=False, server_default="0"),
    )

    # invoices: drop derived totals
    op.drop_column("invoices", "subtotal")
    op.drop_column("invoices", "tax_total")


def downgrade() -> None:
    # invoices: restore derived totals
    op.add_column(
        "invoices",
        sa.Column("subtotal", sa.Numeric(10, 2), nullable=False, server_default="0"),
    )
    op.add_column(
        "invoices",
        sa.Column("tax_total", sa.Numeric(10, 2), nullable=False, server_default="0"),
    )

    # invoice_lines: remove snapshot info
    op.drop_column("invoice_lines", "unit_price")
    op.drop_column("invoice_lines", "description")

    # invoices: remove snapshot names
    op.drop_column("invoices", "company_name")
    op.drop_column("invoices", "partner_name")


