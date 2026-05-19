from dataclasses import dataclass


@dataclass(frozen=True)
class GetEventParticipantsQuery:
    """
    Query untuk mengambil daftar peserta event.
    Digunakan oleh Event Organizer untuk melihat siapa saja yang akan hadir.
    """
    event_id: str