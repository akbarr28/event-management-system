from uuid import UUID
from typing import Optional

from sqlalchemy import Enum, ForeignKey, Numeric, String
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from src.infrastructure.database.connection import Base


class RefundModel(Base):
    __tablename__ = "refunds"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True)
    booking_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("bookings.id"),
        nullable=False,
    )
    customer_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    amount: Mapped[float] = mapped_column(Numeric(19, 4), nullable=False)
    currency: Mapped[str] = mapped_column(String(10), nullable=False, default="IDR")
    status: Mapped[str] = mapped_column(
        Enum("REQUESTED", "APPROVED", "REJECTED", "PAID_OUT", name="refund_status"),
        nullable=False,
        default="REQUESTED",
    )
    rejection_reason: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    payment_reference: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)