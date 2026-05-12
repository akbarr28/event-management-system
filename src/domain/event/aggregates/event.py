from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional

from src.domain.event.domain_events.event_cancelled import EventCancelled
from src.domain.event.domain_events.event_created import EventCreated
from src.domain.event.domain_events.event_published import EventPublished
from src.domain.event.domain_events.ticket_category_created import TicketCategoryCreated
from src.domain.event.domain_events.ticket_category_disabled import TicketCategoryDisabled
from src.domain.event.entities.ticket_category import TicketCategory
from src.domain.event.value_objects.event_id import EventId
from src.domain.event.value_objects.event_status import EventStatus
from src.domain.event.value_objects.organizer_id import OrganizerId
from src.domain.event.value_objects.ticket_category_id import TicketCategoryId
from src.domain.event.value_objects.ticket_category_status import TicketCategoryStatus
from src.domain.shared.exceptions.domain_exception import DomainException
from src.domain.shared.value_objects.money import Money


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

    # User Story - 01

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
    
    # User Story - 02

    def publish(self) -> None:
        # BR-E02: hanya event DRAFT yang bisa dipublish
        if self.status == EventStatus.CANCELLED:
            raise DomainException(
                "Cancelled event cannot be published."
            )
        if self.status == EventStatus.PUBLISHED:
            raise DomainException(
                "Event is already published."
            )
        if self.status == EventStatus.COMPLETED:
            raise DomainException(
                "Completed event cannot be published."
            )

        # BR-E02: harus ada minimal satu ticket category ACTIVE
        active_categories = [
            tc for tc in self.ticket_categories
            if tc.status == TicketCategoryStatus.ACTIVE
        ]
        if not active_categories:
            raise DomainException(
                "Event must have at least one active ticket category before publishing."
            )

        # BR-E02: total quota tidak boleh melebihi maximum_capacity
        total_quota = sum(tc.quota for tc in active_categories)
        if total_quota > self.maximum_capacity:
            raise DomainException(
                "Total ticket quota exceeds event maximum capacity."
            )

        self.status = EventStatus.PUBLISHED

        self._domain_events.append(
            EventPublished(event_id=self.id)
        )


    # User Story - 03

    def cancel(self) -> None:
        # BR-E03: hanya event PUBLISHED yang bisa dibatalkan
        if self.status == EventStatus.DRAFT:
            raise DomainException(
                "Draft event cannot be cancelled. Only published events can be cancelled."
            )
        if self.status == EventStatus.COMPLETED:
            raise DomainException(
                "Completed event cannot be cancelled."
            )
        if self.status == EventStatus.CANCELLED:
            raise DomainException(
                "Event is already cancelled."
            )

        # BR-E03: nonaktifkan semua ticket category agar tidak bisa dibeli
        for tc in self.ticket_categories:
            if tc.status == TicketCategoryStatus.ACTIVE:
                tc.disable()

        self.status = EventStatus.CANCELLED

        # Raise EventCancelled — application layer akan handle marking refund
        # untuk semua booking PAID terkait event ini
        self._domain_events.append(
            EventCancelled(event_id=self.id)
        )


    # User Story - 04
    
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
    

    # User Story - 05
    
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

    
    # User Story - 06

    def is_available_for_browsing(self) -> bool:
        """BR-E06: Event hanya bisa dilihat customer jika statusnya PUBLISHED."""
        return self.status == EventStatus.PUBLISHED

    def get_lowest_ticket_price(self) -> Optional["Money"]:
        """
        BR-E06: Mengembalikan harga ticket terendah dari semua active ticket category.
        Digunakan untuk menampilkan informasi harga ke customer.
        Returns None jika tidak ada active ticket category.
        """
        active_prices = [
            tc.price
            for tc in self.ticket_categories
            if tc.status == TicketCategoryStatus.ACTIVE
        ]
        if not active_prices:
            return None
        return min(active_prices, key=lambda m: m.amount)

    def matches_date_filter(self, filter_date: datetime) -> bool:
        """
        BR-E06: Event cocok dengan date filter jika filter_date berada
        di antara start_date dan end_date (inklusif).
        """
        return self.start_date.date() <= filter_date.date() <= self.end_date.date()

    def matches_location_filter(self, location_keyword: str) -> bool:
        """
        BR-E06: Event cocok dengan location filter jika keyword terdapat
        di dalam location string (case-insensitive).
        """
        return location_keyword.strip().lower() in self.location.lower()
    
    # User Story - 07

    def get_active_ticket_categories_for_display(self) -> list:
        """
        BR-E07: Mengembalikan list ticket category yang aktif untuk ditampilkan
        ke customer. Ticket category inactive tidak ditampilkan sama sekali.
        """
        return [
            tc for tc in self.ticket_categories
            if tc.status == TicketCategoryStatus.ACTIVE
        ]