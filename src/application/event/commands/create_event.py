from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class CreateEventCommand:
    """
    Command untuk membuat event baru.
    Digunakan oleh Event Organizer.
    """
    name: str
    description: str
    start_date: datetime
    end_date: datetime
    location: str
    maximum_capacity: int
    organizer_id: str