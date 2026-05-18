from dataclasses import dataclass, field
from datetime import datetime

from src.domain.booking.value_objects.booking_id import BookingId
from src.domain.booking.value_objects.customer_id import CustomerId
from src.domain.refund.value_objects.refund_id import RefundId


@dataclass(frozen=True)
class RefundRequested:
    refund_id: RefundId
    booking_id: BookingId
    customer_id: CustomerId
    occurred_at: datetime = field(default_factory=datetime.utcnow)