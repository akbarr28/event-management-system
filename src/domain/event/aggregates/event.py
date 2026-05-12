from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional

from src.domain.event.domain_events.event_created import EventCreated
from src.domain.event.value_objects.event_id import EventId
from src.domain.event.value_objects.event_status import EventStatus
from src.domain.event.value_objects.organizer_id import OrganizerId
from src.domain.shared.exceptions.domain_exception import DomainException
from src.domain.event.domain_events.ticket_category_created import TicketCategoryCreated
from src.domain.event.entities.ticket_category import TicketCategory
from src.domain.shared.value_objects.money import Money
from src.domain.event.domain_events.ticket_category_disabled import TicketCategoryDisabled
from src.domain.event.value_objects.ticket_category_id import TicketCategoryId




@dataclass
class Event:
    id: EventId
    name: str
    description: str
    start_date: datetime
    end_date: datetime
    location: str
    maximum_capacity: int
    organizer_id: OrganizerId
    status: EventStatus = field(default=EventStatus.DRAFT)
    ticket_categories: List[TicketCategory] = field(default_factory=list)
    _domain_events: List = field(default_factory=list, init=False, repr=False)

    @staticmethod
    def create(
        name: str,
        description: str,
        start_date: datetime,
        end_date: datetime,
        location: str,
        maximum_capacity: int,
        organizer_id: OrganizerId,
    ) -> "Event":
        # BR-E01: end_date tidak boleh lebih awal dari start_date
        if end_date < start_date:
            raise DomainException(
                "Event end date cannot be earlier than start date."
            )

        # BR-E01: maximum_capacity harus lebih dari nol
        if maximum_capacity <= 0:
            raise DomainException(
                "Event maximum capacity must be greater than zero."
            )

        event = Event(
            id=EventId.generate(),
            name=name,
            description=description,
            start_date=start_date,
            end_date=end_date,
            location=location,
            maximum_capacity=maximum_capacity,
            organizer_id=organizer_id,
            status=EventStatus.DRAFT,
        )

        # Raise domain event EventCreated
        event._domain_events.append(
            EventCreated(
                event_id=event.id,
                organizer_id=organizer_id,
                event_name=name,
            )
        )

        return event
    
    def add_ticket_category(
        self,
        name: str,
        price: Money,
        quota: int,
        sales_start_date: datetime,
        sales_end_date: datetime,
    ) -> TicketCategory:
        # BR-TC01: total quota semua category tidak boleh melebihi maximum_capacity
        total_existing_quota = sum(tc.quota for tc in self.ticket_categories)
        if total_existing_quota + quota > self.maximum_capacity:
            raise DomainException(
                "Total ticket category quota exceeds event maximum capacity."
            )

        ticket_category = TicketCategory.create(
            event_id=self.id,
            name=name,
            price=price,
            quota=quota,
            sales_start_date=sales_start_date,
            sales_end_date=sales_end_date,
            event_start_date=self.start_date,
        )

        self.ticket_categories.append(ticket_category)

        # Raise domain event TicketCategoryCreated
        self._domain_events.append(
            TicketCategoryCreated(
                ticket_category_id=ticket_category.id,
                event_id=self.id,
                category_name=name,
            )
        )

        return ticket_category
    
    def disable_ticket_category(
        self,
        ticket_category_id: TicketCategoryId,
    ) -> None:
        # BR-TC02: event tidak boleh berstatus COMPLETED
        if self.status == EventStatus.COMPLETED:
            raise DomainException(
                "Cannot disable ticket category of a completed event."
            )

        # Cari ticket category berdasarkan ID
        category = self._find_ticket_category(ticket_category_id)
        if category is None:
            raise DomainException("Ticket category not found.")

        # Delegate ke entity untuk ubah statusnya
        category.disable()

        self._domain_events.append(
            TicketCategoryDisabled(
                ticket_category_id=ticket_category_id,
                event_id=self.id,
            )
        )

    def _find_ticket_category(
        self,
        ticket_category_id: TicketCategoryId,
    ) -> Optional[TicketCategory]:
        for tc in self.ticket_categories:
            if tc.id == ticket_category_id:
                return tc
        return None

    def pull_domain_events(self) -> List:
        events = list(self._domain_events)
        self._domain_events.clear()
        return events