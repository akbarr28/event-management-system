from datetime import datetime

from src.application.ticket.commands.check_in_ticket import CheckInTicketCommand
from src.domain.event.repositories.i_event_repository import IEventRepository
from src.domain.event.value_objects.event_id import EventId
from src.domain.event.value_objects.event_status import EventStatus
from src.domain.shared.exceptions.domain_exception import DomainException
from src.domain.ticket.repositories.i_ticket_repository import ITicketRepository
from src.domain.ticket.value_objects.ticket_code import TicketCode
from src.domain.ticket.value_objects.ticket_status import TicketStatus


class CheckInTicketHandler:
    """
    Command Handler untuk US-13 & US-14: Check In Ticket.
    Memvalidasi tiket dan melakukan check-in peserta.
    """

    def __init__(
        self,
        ticket_repository: ITicketRepository,
        event_repository: IEventRepository,
    ):
        self._ticket_repository = ticket_repository
        self._event_repository = event_repository

    async def handle(self, command: CheckInTicketCommand) -> None:
        # Ambil tiket berdasarkan ticket code
        ticket_code = TicketCode(value=command.ticket_code)
        ticket = await self._ticket_repository.find_by_code(ticket_code)

        # US-14: ticket code tidak ditemukan
        if ticket is None:
            raise DomainException("Ticket is invalid.")

        # Ambil event
        event_id = EventId.from_string(command.event_id)
        event = await self._event_repository.find_by_id(event_id)
        if event is None:
            raise DomainException("Event not found.")

        # US-14: event sudah dibatalkan
        if event.status == EventStatus.CANCELLED:
            raise DomainException("This event has been cancelled.")

        # US-14: tiket bukan untuk event ini
        if ticket.event_id != event_id:
            raise DomainException("Ticket does not match this event.")

        # US-14: tiket sudah pernah check-in
        if ticket.status == TicketStatus.CHECKED_IN:
            raise DomainException("Ticket has already been used.")

        # US-13: tiket harus berstatus Active
        if ticket.status != TicketStatus.ACTIVE:
            raise DomainException("Ticket is not active.")

        # Check-in hanya boleh di hari event
        now = datetime.utcnow()
        if now.date() < event.start_date.date() or now.date() > event.end_date.date():
            raise DomainException(
                "Check-in is only allowed on the event day."
            )

        ticket.check_in()

        await self._ticket_repository.save(ticket)