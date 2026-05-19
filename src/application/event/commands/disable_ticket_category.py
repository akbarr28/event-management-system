from dataclasses import dataclass


@dataclass(frozen=True)
class DisableTicketCategoryCommand:
    """
    Command untuk menonaktifkan ticket category.
    Digunakan oleh Event Organizer.
    """
    event_id: str
    organizer_id: str
    ticket_category_id: str