from decimal import Decimal
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.booking.aggregates.booking import Booking
from src.domain.booking.repositories.i_booking_repository import IBookingRepository
from src.domain.booking.value_objects.booking_id import BookingId
from src.domain.booking.value_objects.booking_status import BookingStatus
from src.domain.booking.value_objects.customer_id import CustomerId
from src.domain.event.value_objects.event_id import EventId
from src.domain.event.value_objects.ticket_category_id import TicketCategoryId
from src.domain.shared.value_objects.money import Money
from src.infrastructure.database.models.booking_model import BookingModel


class BookingRepository(IBookingRepository):

    def __init__(self, session: AsyncSession):
        self._session = session

    async def save(self, booking: Booking) -> None:
        existing = await self._session.get(BookingModel, booking.id.value)
        if existing is None:
            self._session.add(self._to_model(booking))
        else:
            self._update_model(existing, booking)
        await self._session.flush()

    async def find_by_id(self, booking_id: BookingId) -> Optional[Booking]:
        result = await self._session.get(BookingModel, booking_id.value)
        if result is None:
            return None
        return self._to_domain(result)

    async def find_active_booking_by_customer_and_event(
        self,
        customer_id: CustomerId,
        event_id: EventId,
    ) -> Optional[Booking]:
        stmt = (
            select(BookingModel)
            .where(BookingModel.customer_id == customer_id.value)
            .where(BookingModel.event_id == event_id.value)
            .where(
                BookingModel.status.in_([
                BookingStatus.PENDING_PAYMENT.value,
                BookingStatus.PAID.value,
                ])
            )
        )
        result = await self._session.execute(stmt)
        row = result.scalar_one_or_none()
        return self._to_domain(row) if row else None

    async def find_by_customer_id(self, customer_id: CustomerId) -> List[Booking]:
        stmt = select(BookingModel).where(BookingModel.customer_id == customer_id.value)
        result = await self._session.execute(stmt)
        return [self._to_domain(row) for row in result.scalars().all()]

    async def find_by_event_id(self, event_id: EventId) -> List[Booking]:
        stmt = select(BookingModel).where(BookingModel.event_id == event_id.value)
        result = await self._session.execute(stmt)
        return [self._to_domain(row) for row in result.scalars().all()]

    # ---------- mapping ----------

    def _to_model(self, booking: Booking) -> BookingModel:
        return BookingModel(
            id=booking.id.value,
            event_id=booking.event_id.value,
            ticket_category_id=booking.ticket_category_id.value,
            customer_id=booking.customer_id.value,
            quantity=booking.quantity,
            unit_amount=booking.unit_price.amount,
            unit_currency=booking.unit_price.currency,
            total_amount=booking.total_price.amount,
            total_currency=booking.total_price.currency,
            payment_deadline=booking.payment_deadline,
            status=booking.status.value,
        )

    def _update_model(self, model: BookingModel, booking: Booking) -> None:
        model.status = booking.status.value
        model.total_amount = booking.total_price.amount
        model.total_currency = booking.total_price.currency
        model.unit_amount = booking.unit_price.amount
        model.unit_currency = booking.unit_price.currency

    def _to_domain(self, model: BookingModel) -> Booking:
        unit_price = Money(amount=Decimal(str(model.unit_amount)), currency=model.unit_currency)
        total_price = Money(amount=Decimal(str(model.total_amount)), currency=model.total_currency)
        return Booking(
            id=BookingId(value=model.id),
            customer_id=CustomerId(value=model.customer_id),
            event_id=EventId(value=model.event_id),
            ticket_category_id=TicketCategoryId(value=model.ticket_category_id),
            quantity=model.quantity,
            unit_price=unit_price,
            total_price=total_price,
            status=BookingStatus(model.status),
            payment_deadline=model.payment_deadline,
        )