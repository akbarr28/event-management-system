from decimal import Decimal
from typing import List, Optional

from src.application.event.queries.get_available_events import GetAvailableEventsQuery
from src.application.shared.dtos.event_dto import EventSummaryDTO
from src.domain.event.repositories.i_event_repository import IEventRepository
from src.domain.event.value_objects.ticket_category_status import TicketCategoryStatus


class GetAvailableEventsHandler:
    """
    Query Handler untuk US-06: View Available Events.
    Mengambil semua event Published dan mengembalikan summary-nya.
    """

    def __init__(self, event_repository: IEventRepository):
        self._event_repository = event_repository

    async def handle(self, query: GetAvailableEventsQuery) -> List[EventSummaryDTO]:
        events = await self._event_repository.find_published()

        # Filter by date jika ada
        if query.filter_date:
            events = [
                e for e in events
                if e.start_date.date() == query.filter_date.date()
            ]

        # Filter by location jika ada
        if query.filter_location:
            events = [
                e for e in events
                if query.filter_location.lower() in e.location.lower()
            ]

        result = []
        for event in events:
            lowest_price = self._get_lowest_price(event)
            result.append(EventSummaryDTO(
                id=str(event.id),
                name=event.name,
                description=event.description,
                start_date=event.start_date,
                end_date=event.end_date,
                location=event.location,
                organizer_id=str(event.organizer_id),
                status=event.status.value,
                lowest_price=lowest_price,
                lowest_price_currency="IDR",
            ))

        return result

    def _get_lowest_price(self, event) -> Optional[Decimal]:
        active_prices = [
            tc.price.amount
            for tc in event.ticket_categories
            if tc.status == TicketCategoryStatus.ACTIVE
        ]
        return min(active_prices) if active_prices else None