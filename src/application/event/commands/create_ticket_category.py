from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal


@dataclass(frozen=True)
class CreateTicketCategoryCommand:
    """
    Command untuk membuat ticket category baru.
    Digunakan oleh Event Organizer.
    """
    event_id: str
    organizer_id: str
    name: str
    price: Decimal
    currency: str
    quota: int
    sales_start_date: datetime
    sales_end_date: datetime