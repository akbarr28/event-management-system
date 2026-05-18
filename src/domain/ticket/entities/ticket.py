from dataclasses import dataclass
from datetime import datetime

from src.domain.booking.value_objects.booking_id import BookingId
from src.domain.booking.value_objects.customer_id import CustomerId
from src.domain.event.value_objects.event_id import EventId
from src.domain.event.value_objects.ticket_category_id import TicketCategoryId
from src.domain.shared.exceptions.domain_exception import DomainException
from src.domain.ticket.value_objects.ticket_code import TicketCode
from src.domain.ticket.value_objects.ticket_id import TicketId
from src.domain.ticket.value_objects.ticket_status import TicketStatus


@dataclass
class Ticket:
    id: TicketId
    booking_id: BookingId
    customer_id: CustomerId
    event_id: EventId
    ticket_category_id: TicketCategoryId
    ticket_code: TicketCode
    status: TicketStatus

    # User Story - 12

    @staticmethod
    def create(
        booking_id: BookingId,
        customer_id: CustomerId,
        event_id: EventId,
        ticket_category_id: TicketCategoryId,
    ) -> "Ticket":
        """
        BR-T12: Membuat ticket baru setelah booking dibayar.
        - Ticket memiliki unique ticket code
        - Status awal adalah Active
        """
        return Ticket(
            id=TicketId.generate(),
            booking_id=booking_id,
            customer_id=customer_id,
            event_id=event_id,
            ticket_category_id=ticket_category_id,
            ticket_code=TicketCode.generate(),
            status=TicketStatus.ACTIVE,
        )

    def is_viewable_by_customer(self) -> bool:
        """
        BR-T12: Ticket hanya bisa dilihat customer jika booking statusnya Paid.
        Ticket dengan status apapun bisa dilihat selama booking-nya Paid.
        """
        return True  # filter by booking status dilakukan di repository/query

    def cancel(self) -> None:
        """BR-T12: Membatalkan ticket, misalnya saat event dibatalkan."""
        if self.status == TicketStatus.CHECKED_IN:
            raise DomainException("Checked-in ticket cannot be cancelled.")
        self.status = TicketStatus.CANCELLED