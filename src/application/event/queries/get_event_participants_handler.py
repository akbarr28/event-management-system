from typing import List

from src.application.event.queries.get_event_participants import GetEventParticipantsQuery
from src.application.shared.dtos.participant_dto import ParticipantDTO
from src.domain.booking.repositories.i_booking_repository import IBookingRepository
from src.domain.booking.value_objects.booking_status import BookingStatus
from src.domain.event.repositories.i_event_repository import IEventRepository
from src.domain.event.value_objects.event_id import EventId
from src.domain.shared.exceptions.domain_exception import DomainException
from src.domain.ticket.repositories.i_ticket_repository import ITicketRepository
from src.domain.ticket.value_objects.ticket_status import TicketStatus


class GetEventParticipantsHandler:
    """
    Query Handler untuk US-20: View Event Participants.
    Mengambil daftar peserta dari booking Paid yang belum di-refund.
    """

    def __init__(
        self,
        event_repository: IEventRepository,
        booking_repository: IBookingRepository,
        ticket_repository: ITicketRepository,
    ):
        self._event_repository = event_repository
        self._booking_repository = booking_repository
        self._ticket_repository = ticket_repository

    async def handle(self, query: GetEventParticipantsQuery) -> List[ParticipantDTO]:
        event_id = EventId.from_string(query.event_id)
        event = await self._event_repository.find_by_id(event_id)
        if event is None:
            raise DomainException("Event not found.")

    
        bookings = await self._booking_repository.find_by_event_id(event_id)
        paid_bookings = [
            b for b in bookings
            if b.status == BookingStatus.PAID
        ]

     
        category_map = {
            str(tc.id): tc.name
            for tc in event.ticket_categories
        }

        participants = []
        for booking in paid_bookings:
            tickets = await self._ticket_repository.find_by_booking_id(booking.id)
            for ticket in tickets:
                if ticket.status == TicketStatus.CANCELLED:
                    continue

                participants.append(ParticipantDTO(
                    customer_name=str(booking.customer_id),
                    ticket_category_name=category_map.get(
                        str(booking.ticket_category_id), "Unknown"
                    ),
                    ticket_code=str(ticket.ticket_code),
                    is_checked_in=ticket.status == TicketStatus.CHECKED_IN,
                ))

        return participants