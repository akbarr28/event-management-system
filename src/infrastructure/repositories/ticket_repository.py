from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.booking.value_objects.booking_id import BookingId
from src.domain.booking.value_objects.customer_id import CustomerId
from src.domain.event.value_objects.event_id import EventId
from src.domain.ticket.entities.ticket import Ticket
from src.domain.ticket.repositories.i_ticket_repository import ITicketRepository
from src.domain.ticket.value_objects.ticket_code import TicketCode
from src.domain.ticket.value_objects.ticket_id import TicketId
from src.domain.ticket.value_objects.ticket_status import TicketStatus
from src.domain.event.value_objects.ticket_category_id import TicketCategoryId
from src.infrastructure.database.models.ticket_model import TicketModel


class TicketRepository(ITicketRepository):

    def __init__(self, session: AsyncSession):
        self._session = session

    # ---------- save ----------

    async def save(self, ticket: Ticket) -> None:
        existing = await self._session.get(TicketModel, ticket.id.value)
        if existing is None:
            self._session.add(self._to_model(ticket))
        else:
            self._update_model(existing, ticket)
        await self._session.flush()

    # ---------- save_all ----------

    async def save_all(self, tickets: List[Ticket]) -> None:
        for ticket in tickets:
            await self.save(ticket)

    # ---------- find_by_id ----------

    async def find_by_id(self, ticket_id: TicketId) -> Optional[Ticket]:
        result = await self._session.get(TicketModel, ticket_id.value)
        if result is None:
            return None
        return self._to_domain(result)

    # ---------- find_by_code ----------

    async def find_by_code(self, ticket_code: TicketCode) -> Optional[Ticket]:
        stmt = select(TicketModel).where(
            TicketModel.ticket_code == ticket_code.value
        )
        result = await self._session.execute(stmt)
        row = result.scalar_one_or_none()
        return self._to_domain(row) if row else None

    # ---------- find_by_booking_id ----------

    async def find_by_booking_id(self, booking_id: BookingId) -> List[Ticket]:
        stmt = select(TicketModel).where(
            TicketModel.booking_id == booking_id.value
        )
        result = await self._session.execute(stmt)
        return [self._to_domain(row) for row in result.scalars().all()]

    # ---------- find_paid_tickets_by_customer ----------

    async def find_paid_tickets_by_customer(
        self, customer_id: CustomerId
    ) -> List[Ticket]:
        stmt = select(TicketModel).where(
            TicketModel.customer_id == customer_id.value
        )
        result = await self._session.execute(stmt)
        return [self._to_domain(row) for row in result.scalars().all()]

    # ---------- find_paid_tickets_by_event ----------

    async def find_paid_tickets_by_event(
        self, event_id: EventId
    ) -> List[Ticket]:
        stmt = select(TicketModel).where(
            TicketModel.event_id == event_id.value
        )
        result = await self._session.execute(stmt)
        return [self._to_domain(row) for row in result.scalars().all()]

    # ---------- mapping helpers ----------

    def _to_model(self, ticket: Ticket) -> TicketModel:
        return TicketModel(
            id=ticket.id.value,
            booking_id=ticket.booking_id.value,
            customer_id=ticket.customer_id.value,
            event_id=ticket.event_id.value,
            ticket_category_id=ticket.ticket_category_id.value,
            ticket_code=str(ticket.ticket_code),
            status=ticket.status.value,
        )

    def _update_model(self, model: TicketModel, ticket: Ticket) -> None:
        model.status = ticket.status.value

    def _to_domain(self, model: TicketModel) -> Ticket:
        return Ticket(
            id=TicketId(value=model.id),
            booking_id=BookingId(value=model.booking_id),
            customer_id=CustomerId(value=model.customer_id),
            event_id=EventId(value=model.event_id),
            ticket_category_id=TicketCategoryId(value=model.ticket_category_id),
            ticket_code=TicketCode(value=model.ticket_code),
            status=TicketStatus(model.status),
        )