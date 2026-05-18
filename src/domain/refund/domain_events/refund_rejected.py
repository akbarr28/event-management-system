from dataclasses import dataclass, field
from datetime import datetime

from src.domain.booking.value_objects.booking_id import BookingId
from src.domain.refund.value_objects.refund_id import RefundId


@dataclass(frozen=True)
class RefundRejected:
    refund_id: RefundId
    booking_id: BookingId
    rejection_reason: str
    occurred_at: datetime = field(default_factory=datetime.utcnow)