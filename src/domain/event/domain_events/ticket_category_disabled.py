from dataclasses import dataclass, field
from datetime import datetime

from src.domain.event.value_objects.event_id import EventId
from src.domain.event.value_objects.ticket_category_id import TicketCategoryId


@dataclass(frozen=True)
class TicketCategoryDisabled:
    ticket_category_id: TicketCategoryId
    event_id: EventId
    occurred_at: datetime = field(default_factory=datetime.utcnow)