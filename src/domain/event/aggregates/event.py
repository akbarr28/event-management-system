from dataclasses import dataclass, field
from datetime import datetime
from typing import List

from src.domain.event.domain_events.event_created import EventCreated
from src.domain.event.value_objects.event_id import EventId
from src.domain.event.value_objects.event_status import EventStatus
from src.domain.event.value_objects.organizer_id import OrganizerId
from src.domain.shared.exceptions.domain_exception import DomainException


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

    def pull_domain_events(self) -> List:
        events = list(self._domain_events)
        self._domain_events.clear()
        return events