from dataclasses import dataclass


@dataclass(frozen=True)
class CancelEventCommand:
    """
    Command untuk membatalkan event.
    Digunakan oleh Event Organizer.
    """
    event_id: str
    organizer_id: str