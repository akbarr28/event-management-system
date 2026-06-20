"""us05 create tickets table

Revision ID: 003
Revises: 002
Create Date: 2025-01-01 00:00:00.000000
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "003"
down_revision: Union[str, None] = "002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "tickets",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "booking_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("bookings.id"),
            nullable=False,
        ),
        sa.Column("customer_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("event_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("ticket_category_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("ticket_code", sa.String(50), nullable=False, unique=True),
        sa.Column(
            "status",
            sa.Enum("ACTIVE", "CHECKED_IN", "CANCELLED", name="ticket_status"),
            nullable=False,
            server_default="ACTIVE",
        ),
    )
    op.create_index("ix_tickets_booking_id", "tickets", ["booking_id"])
    op.create_index("ix_tickets_event_id", "tickets", ["event_id"])
    op.create_index("ix_tickets_customer_id", "tickets", ["customer_id"])


def downgrade() -> None:
    op.drop_index("ix_tickets_customer_id", "tickets")
    op.drop_index("ix_tickets_event_id", "tickets")
    op.drop_index("ix_tickets_booking_id", "tickets")
    op.drop_table("tickets")
    op.execute("DROP TYPE IF EXISTS ticket_status")