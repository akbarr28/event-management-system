from dataclasses import dataclass, field
from datetime import datetime

from src.domain.event.value_objects.event_id import EventId
from src.domain.ticket.value_objects.ticket_id import TicketId


@dataclass(frozen=True)
class TicketCheckedIn:
    ticket_id: TicketId
    event_id: EventId
    occurred_at: datetime = field(default_factory=datetime.utcnow)