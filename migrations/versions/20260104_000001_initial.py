"""initial

Revision ID: 20260104_000001
Revises:
Create Date: 2026-01-04

"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = "20260104_000001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    invoicestatus = postgresql.ENUM(
        "ISSUED",
        "PAID",
        "CANCELLED",
        name="invoicestatus",
        create_type=False,
    )
    invoicestatus.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "invoices",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("invoice_number", sa.String(), nullable=False, unique=True),
        sa.Column("partner_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("company_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("comment", sa.Text(), nullable=True),
        sa.Column("issue_date", sa.DateTime(), nullable=False),
        sa.Column("due_date", sa.DateTime(), nullable=False),
        sa.Column("status", invoicestatus, nullable=False),
        sa.Column("subtotal", sa.Numeric(10, 2), nullable=False),
        sa.Column("tax_total", sa.Numeric(10, 2), nullable=False),
        sa.Column("total", sa.Numeric(10, 2), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )

    op.create_table(
        "invoice_lines",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("invoice_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("invoices.id"), nullable=False),
        sa.Column("product_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("amount", sa.Integer(), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("invoice_lines")
    op.drop_table("invoices")
    op.execute("DROP TYPE IF EXISTS invoicestatus")


