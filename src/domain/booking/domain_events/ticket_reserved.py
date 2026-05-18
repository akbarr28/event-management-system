from dataclasses import dataclass, field
from datetime import datetime

from src.domain.booking.value_objects.booking_id import BookingId
from src.domain.booking.value_objects.customer_id import CustomerId
from src.domain.event.value_objects.event_id import EventId
from src.domain.event.value_objects.ticket_category_id import TicketCategoryId


@dataclass(frozen=True)
class TicketReserved:
    booking_id: BookingId
    customer_id: CustomerId
    event_id: EventId
    ticket_category_id: TicketCategoryId
    quantity: int
    occurred_at: datetime = field(default_factory=datetime.utcnow)