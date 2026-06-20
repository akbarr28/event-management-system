from decimal import Decimal
from typing import List, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.event.aggregates.event import Event
from src.domain.event.entities.ticket_category import TicketCategory
from src.domain.event.repositories.i_event_repository import IEventRepository
from src.domain.event.value_objects.event_id import EventId
from src.domain.event.value_objects.event_status import EventStatus
from src.domain.event.value_objects.organizer_id import OrganizerId
from src.domain.event.value_objects.ticket_category_id import TicketCategoryId
from src.domain.event.value_objects.ticket_category_status import TicketCategoryStatus
from src.domain.shared.value_objects.money import Money
from src.infrastructure.database.models.event_model import EventModel, TicketCategoryModel


class EventRepository(IEventRepository):

    def __init__(self, session: AsyncSession):
        self._session = session


    async def save(self, event: Event) -> None:
        existing = await self._session.get(EventModel, event.id.value)

        if existing is None:
            model = self._to_model(event)
            self._session.add(model)
        else:
            self._update_model(existing, event)
            existing_tc_ids = {tc.id for tc in existing.ticket_categories}
            domain_tc_ids = {tc.id.value for tc in event.ticket_categories}

            for tc_model in list(existing.ticket_categories):
                if tc_model.id not in domain_tc_ids:
                    await self._session.delete(tc_model)

            for tc in event.ticket_categories:
                if tc.id.value not in existing_tc_ids:
                    self._session.add(self._tc_to_model(tc))
                else:
                    for tc_model in existing.ticket_categories:
                        if tc_model.id == tc.id.value:
                            self._update_tc_model(tc_model, tc)

        await self._session.flush()


    async def find_by_id(self, event_id: EventId) -> Optional[Event]:
        result = await self._session.get(EventModel, event_id.value)
        if result is None:
            return None
        return self._to_domain(result)


    async def find_published(self) -> List[Event]:
        stmt = select(EventModel).where(EventModel.status == "PUBLISHED")
        result = await self._session.execute(stmt)
        rows = result.scalars().all()
        return [self._to_domain(row) for row in rows]


    def _to_model(self, event: Event) -> EventModel:
        model = EventModel(
            id=event.id.value,
            name=event.name,
            description=event.description,
            start_date=event.start_date,
            end_date=event.end_date,
            location=event.location,
            maximum_capacity=event.maximum_capacity,
            organizer_id=event.organizer_id.value,
            status=event.status.value,
            ticket_categories=[self._tc_to_model(tc) for tc in event.ticket_categories],
        )
        return model

    def _update_model(self, model: EventModel, event: Event) -> None:
        model.name = event.name
        model.description = event.description
        model.start_date = event.start_date
        model.end_date = event.end_date
        model.location = event.location
        model.maximum_capacity = event.maximum_capacity
        model.organizer_id = event.organizer_id.value
        model.status = event.status.value

    def _tc_to_model(self, tc: TicketCategory) -> TicketCategoryModel:
        return TicketCategoryModel(
            id=tc.id.value,
            event_id=tc.event_id.value,
            name=tc.name,
            price_amount=tc.price.amount,
            price_currency=tc.price.currency,
            quota=tc.quota,
            remaining_quota=tc.remaining_quota,
            sales_start_date=tc.sales_start_date,
            sales_end_date=tc.sales_end_date,
            status=tc.status.value,
        )

    def _update_tc_model(self, model: TicketCategoryModel, tc: TicketCategory) -> None:
        model.name = tc.name
        model.price_amount = tc.price.amount
        model.price_currency = tc.price.currency
        model.quota = tc.quota
        model.remaining_quota = tc.remaining_quota
        model.sales_start_date = tc.sales_start_date
        model.sales_end_date = tc.sales_end_date
        model.status = tc.status.value

    def _to_domain(self, model: EventModel) -> Event:
        ticket_categories = [self._tc_to_domain(tc) for tc in model.ticket_categories]
        return Event(
            id=EventId(value=model.id),
            name=model.name,
            description=model.description,
            start_date=model.start_date,
            end_date=model.end_date,
            location=model.location,
            maximum_capacity=model.maximum_capacity,
            organizer_id=OrganizerId(value=model.organizer_id),
            status=EventStatus(model.status),
            ticket_categories=ticket_categories,
        )

    def _tc_to_domain(self, model: TicketCategoryModel) -> TicketCategory:
        return TicketCategory(
            id=TicketCategoryId(value=model.id),
            event_id=EventId(value=model.event_id),
            name=model.name,
            price=Money(amount=Decimal(str(model.price_amount)), currency=model.price_currency),
            quota=model.quota,
            remaining_quota=model.remaining_quota,
            sales_start_date=model.sales_start_date,
            sales_end_date=model.sales_end_date,
            status=TicketCategoryStatus(model.status),
        )