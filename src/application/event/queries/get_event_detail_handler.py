from src.application.event.queries.get_event_detail import GetEventDetailQuery
from src.application.shared.dtos.event_dto import EventDetailDTO, TicketCategoryDTO
from src.domain.event.repositories.i_event_repository import IEventRepository
from src.domain.event.value_objects.event_id import EventId
from src.domain.event.value_objects.ticket_category_status import TicketCategoryStatus
from src.domain.shared.exceptions.domain_exception import DomainException


class GetEventDetailHandler:
    """
    Query Handler untuk US-07: View Event Details.
    Mengambil detail event beserta status display tiap ticket category.
    """

    def __init__(self, event_repository: IEventRepository):
        self._event_repository = event_repository

    async def handle(self, query: GetEventDetailQuery) -> EventDetailDTO:
        event_id = EventId.from_string(query.event_id)
        event = await self._event_repository.find_by_id(event_id)

        if event is None:
            raise DomainException("Event not found.")

        ticket_categories = []
        for tc in event.ticket_categories:
            # Tentukan display_status sesuai acceptance criteria US-07
            display_status = self._resolve_display_status(tc, query.now)

            ticket_categories.append(TicketCategoryDTO(
                id=str(tc.id),
                name=tc.name,
                price=tc.price.amount,
                currency=tc.price.currency,
                quota=tc.quota,
                remaining_quota=tc.remaining_quota,
                sales_start_date=tc.sales_start_date,
                sales_end_date=tc.sales_end_date,
                status=tc.status.value,
                display_status=display_status,
            ))

        return EventDetailDTO(
            id=str(event.id),
            name=event.name,
            description=event.description,
            start_date=event.start_date,
            end_date=event.end_date,
            location=event.location,
            organizer_id=str(event.organizer_id),
            status=event.status.value,
            maximum_capacity=event.maximum_capacity,
            ticket_categories=ticket_categories,
        )

    def _resolve_display_status(self, ticket_category, now) -> str:
        """
        US-07: Tentukan display status ticket category:
        - INACTIVE           → tidak ditampilkan (filter di luar)
        - Sales belum mulai  → Coming Soon
        - Sales sudah habis  → Sales Closed
        - Quota habis        → Sold Out
        - Lainnya            → Available
        """
        if ticket_category.status == TicketCategoryStatus.INACTIVE:
            return "Inactive"

        if now < ticket_category.sales_start_date:
            return "Coming Soon"

        if now > ticket_category.sales_end_date:
            return "Sales Closed"

        if ticket_category.remaining_quota <= 0:
            return "Sold Out"

        return "Available"