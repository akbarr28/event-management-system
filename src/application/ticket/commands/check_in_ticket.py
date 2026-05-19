from dataclasses import dataclass


@dataclass(frozen=True)
class CheckInTicketCommand:
    """
    Command untuk check-in tiket.
    Digunakan oleh Gate Officer saat peserta masuk venue.
    """
    ticket_code: str
    event_id: str