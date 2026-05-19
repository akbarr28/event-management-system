from dataclasses import dataclass


@dataclass(frozen=True)
class PublishEventCommand:
    """
    Command untuk mempublish event.
    Digunakan oleh Event Organizer.
    """
    event_id: str
    organizer_id: str