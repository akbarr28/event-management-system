from dataclasses import dataclass


@dataclass(frozen=True)
class CreateBookingCommand:
    """
    Command untuk membuat booking tiket baru.
    Digunakan oleh Customer.
    """
    customer_id: str
    event_id: str
    ticket_category_id: str
    quantity: int