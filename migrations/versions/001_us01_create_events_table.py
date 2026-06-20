"""US-01: create events and ticket_categories table

Revision ID: 001
Revises:
Create Date: 2025-01-01 00:00:00
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "events",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text, nullable=False),
        sa.Column("start_date", sa.DateTime(timezone=True), nullable=False),
        sa.Column("end_date", sa.DateTime(timezone=True), nullable=False),
        sa.Column("location", sa.String(255), nullable=False),
        sa.Column("maximum_capacity", sa.Integer, nullable=False),
        sa.Column("organizer_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "status",
            sa.Enum("DRAFT", "PUBLISHED", "CANCELLED", "COMPLETED", name="event_status"),
            nullable=False,
            server_default="DRAFT",
        ),
    )
    op.create_table(
        "ticket_categories",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("event_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("events.id"), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("price_amount", sa.Numeric(19, 4), nullable=False),
        sa.Column("price_currency", sa.String(10), nullable=False, server_default="IDR"),
        sa.Column("quota", sa.Integer, nullable=False),
        sa.Column("remaining_quota", sa.Integer, nullable=False),
        sa.Column("sales_start_date", sa.DateTime(timezone=True), nullable=False),
        sa.Column("sales_end_date", sa.DateTime(timezone=True), nullable=False),
        sa.Column(
            "status",
            sa.Enum("ACTIVE", "INACTIVE", name="ticket_category_status"),
            nullable=False,
            server_default="ACTIVE",
        ),
    )


def downgrade() -> None:
    op.drop_table("ticket_categories")
    op.drop_table("events")
    op.execute("DROP TYPE IF EXISTS event_status")
    op.execute("DROP TYPE IF EXISTS ticket_category_status")