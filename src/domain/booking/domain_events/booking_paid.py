from dataclasses import dataclass, field
from datetime import datetime

from src.domain.booking.value_objects.booking_id import BookingId
from src.domain.booking.value_objects.customer_id import CustomerId
from src.domain.event.value_objects.event_id import EventId


@dataclass(frozen=True)
class BookingPaid:
    booking_id: BookingId
    customer_id: CustomerId
    event_id: EventId
    amount_paid: object  # Money
    occurred_at: datetime = field(default_factory=datetime.utcnow)