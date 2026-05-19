from typing import List

from src.application.shared.dtos.ticket_dto import TicketDTO
from src.application.ticket.queries.get_purchased_tickets import GetPurchasedTicketsQuery
from src.domain.booking.repositories.i_booking_repository import IBookingRepository
from src.domain.booking.value_objects.booking_status import BookingStatus
from src.domain.booking.value_objects.customer_id import CustomerId
from src.domain.ticket.repositories.i_ticket_repository import ITicketRepository


class GetPurchasedTicketsHandler:
    """
    Query Handler untuk US-12: View Purchased Tickets.
    Mengambil semua tiket dari booking Paid milik customer.
    """

    def __init__(
        self,
        booking_repository: IBookingRepository,
        ticket_repository: ITicketRepository,
    ):
        self._booking_repository = booking_repository
        self._ticket_repository = ticket_repository

    async def handle(self, query: GetPurchasedTicketsQuery) -> List[TicketDTO]:
        customer_id = CustomerId.from_string(query.customer_id)
        bookings = await self._booking_repository.find_by_customer_id(customer_id)
        paid_bookings = [
            b for b in bookings
            if b.status == BookingStatus.PAID
        ]

        tickets = []
        for booking in paid_bookings:
            booking_tickets = await self._ticket_repository.find_by_booking_id(
                booking.id
            )
            for ticket in booking_tickets:
                tickets.append(TicketDTO(
                    ticket_id=str(ticket.id),
                    ticket_code=str(ticket.ticket_code),
                    booking_id=str(ticket.booking_id),
                    event_id=str(ticket.event_id),
                    ticket_category_id=str(ticket.ticket_category_id),
                    status=ticket.status.value,
                ))

        return tickets