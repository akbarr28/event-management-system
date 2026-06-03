"""US-03: create bookings table

Revision ID: 002
Revises: 001
Create Date: 2025-01-01 00:01:00
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "002"
down_revision = "001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        "CREATE TYPE booking_status AS ENUM "
        "('PENDING_PAYMENT', 'PAID', 'EXPIRED', 'REFUNDED')"
    )

    op.create_table(
        "bookings",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("event_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("ticket_category_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("customer_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("unit_amount", sa.Numeric(19, 4), nullable=False),
        sa.Column("unit_currency", sa.String(10), nullable=False, server_default="IDR"),
        sa.Column("quantity", sa.Integer, nullable=False),
        sa.Column("total_amount", sa.Numeric(19, 4), nullable=False),
        sa.Column("total_currency", sa.String(10), nullable=False, server_default="IDR"),
        sa.Column("payment_deadline", sa.DateTime(timezone=True), nullable=False),
        sa.Column(
            "status",
            sa.Enum(
                "PENDING_PAYMENT", "PAID", "EXPIRED", "REFUNDED",
                name="booking_status",
                create_type=False,
            ),
            nullable=False,
            server_default="PENDING_PAYMENT",
        ),
        sa.Column("payment_reference", sa.String(255), nullable=True),
    )


def downgrade() -> None:
    op.drop_table("bookings")
    op.execute("DROP TYPE booking_status")