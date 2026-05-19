from dataclasses import dataclass, field
from datetime import datetime

from src.domain.booking.value_objects.booking_id import BookingId
from src.domain.refund.value_objects.refund_id import RefundId


@dataclass(frozen=True)
class RefundPaidOut:
    refund_id: RefundId
    booking_id: BookingId
    payment_reference: str
    occurred_at: datetime = field(default_factory=datetime.utcnow)