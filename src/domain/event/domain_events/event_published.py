from dataclasses import dataclass, field
from datetime import datetime

from src.domain.event.value_objects.event_id import EventId


@dataclass(frozen=True)
class EventPublished:
    event_id: EventId
    occurred_at: datetime = field(default_factory=datetime.utcnow)