from datetime import datetime
from uuid import UUID

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, Numeric, String
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.infrastructure.database.connection import Base


class EventModel(Base):
    __tablename__ = "events"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=False)
    start_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    end_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    location: Mapped[str] = mapped_column(String(255), nullable=False)
    maximum_capacity: Mapped[int] = mapped_column(Integer, nullable=False)
    organizer_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    status: Mapped[str] = mapped_column(
        Enum("DRAFT", "PUBLISHED", "CANCELLED", "COMPLETED", name="event_status"),
        nullable=False,
        default="DRAFT",
    )

    ticket_categories: Mapped[list["TicketCategoryModel"]] = relationship(
        "TicketCategoryModel",
        back_populates="event",
        cascade="all, delete-orphan",
        lazy="selectin",
    )


class TicketCategoryModel(Base):
    __tablename__ = "ticket_categories"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True)
    event_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("events.id"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    price_amount: Mapped[float] = mapped_column(Numeric(19, 4), nullable=False)
    price_currency: Mapped[str] = mapped_column(String(10), nullable=False, default="IDR")
    quota: Mapped[int] = mapped_column(Integer, nullable=False)
    remaining_quota: Mapped[int] = mapped_column(Integer, nullable=False)
    sales_start_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    sales_end_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    status: Mapped[str] = mapped_column(
        Enum("ACTIVE", "INACTIVE", name="ticket_category_status"),
        nullable=False,
        default="ACTIVE",
    )

    event: Mapped["EventModel"] = relationship("EventModel", back_populates="ticket_categories")