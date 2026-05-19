from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass(frozen=True)
class GetAvailableEventsQuery:
    """
    Query untuk mengambil daftar event yang tersedia.
    Digunakan oleh Customer untuk browse event.
    Filter by date atau location bersifat opsional.
    """
    filter_date: Optional[datetime] = None
    filter_location: Optional[str] = None