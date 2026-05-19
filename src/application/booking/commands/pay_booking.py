from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class PayBookingCommand:
    """
    Command untuk membayar booking.
    Digunakan oleh Customer.
    """
    booking_id: str
    customer_id: str
    payment_amount: Decimal
    currency: str