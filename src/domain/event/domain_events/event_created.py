from dataclasses import dataclass, field
from datetime import datetime

from src.domain.event.value_objects.event_id import EventId
from src.domain.event.value_objects.organizer_id import OrganizerId


@dataclass(frozen=True)
class EventCreated:
    event_id: EventId
    organizer_id: OrganizerId
    event_name: str
    occurred_at: datetime = field(default_factory=datetime.utcnow)