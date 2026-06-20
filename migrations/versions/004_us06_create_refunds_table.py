"""us06 create refunds table

Revision ID: 004
Revises: 003
Create Date: 2025-01-01 00:00:00.000000
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "004"
down_revision: Union[str, None] = "003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "refunds",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "booking_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("bookings.id"),
            nullable=False,
        ),
        sa.Column("customer_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("amount", sa.Numeric(19, 4), nullable=False),
        sa.Column("currency", sa.String(10), nullable=False, server_default="IDR"),
        sa.Column(
            "status",
            sa.Enum(
                "REQUESTED", "APPROVED", "REJECTED", "PAID_OUT",
                name="refund_status",
            ),
            nullable=False,
            server_default="REQUESTED",
        ),
        sa.Column("rejection_reason", sa.String, nullable=True),
        sa.Column("payment_reference", sa.String(255), nullable=True),
    )
    op.create_index("ix_refunds_booking_id", "refunds", ["booking_id"])
    op.create_index("ix_refunds_customer_id", "refunds", ["customer_id"])


def downgrade() -> None:
    op.drop_index("ix_refunds_customer_id", "refunds")
    op.drop_index("ix_refunds_booking_id", "refunds")
    op.drop_table("refunds")
    op.execute("DROP TYPE IF EXISTS refund_status")