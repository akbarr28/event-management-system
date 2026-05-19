from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal


@dataclass(frozen=True)
class BookingDTO:
    """DTO untuk detail booking — US-08, US-10, US-11."""
    id: str
    customer_id: str
    event_id: str
    ticket_category_id: str
    quantity: int
    unit_price: Decimal
    total_price: Decimal
    currency: str
    status: str
    payment_deadline: datetime