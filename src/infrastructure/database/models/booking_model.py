from datetime import datetime
from uuid import UUID

from sqlalchemy import DateTime, Enum, Integer, Numeric, String
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from src.infrastructure.database.connection import Base


class BookingModel(Base):
    __tablename__ = "bookings"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True)
    event_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    ticket_category_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    customer_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    unit_amount: Mapped[float] = mapped_column(Numeric(19, 4), nullable=False)
    unit_currency: Mapped[str] = mapped_column(String(10), nullable=False, default="IDR")
    total_amount: Mapped[float] = mapped_column(Numeric(19, 4), nullable=False)
    total_currency: Mapped[str] = mapped_column(String(10), nullable=False, default="IDR")
    payment_deadline: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    status: Mapped[str] = mapped_column(
        Enum(
            "PENDING_PAYMENT", "PAID", "EXPIRED", "REFUNDED",
            name="booking_status",
        ),
        nullable=False,
        default="PENDING_PAYMENT",
    )
    payment_reference: Mapped[str] = mapped_column(String(255), nullable=True)