from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class GetEventDetailQuery:
    """
    Query untuk mengambil detail event beserta ticket categories.
    Digunakan oleh Customer untuk melihat informasi lengkap event.
    """
    event_id: str
    now: datetime