from dataclasses import dataclass


@dataclass(frozen=True)
class TicketDTO:
    """DTO untuk tiket yang sudah dibeli — US-12, US-13."""
    id: str
    booking_id: str
    event_id: str
    ticket_category_id: str
    customer_id: str
    ticket_code: str
    status: str