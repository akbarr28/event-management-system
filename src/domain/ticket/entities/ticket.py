from dataclasses import dataclass, field
from datetime import datetime
from typing import List


from src.domain.booking.value_objects.booking_id import BookingId
from src.domain.booking.value_objects.customer_id import CustomerId
from src.domain.event.value_objects.event_id import EventId
from src.domain.event.value_objects.ticket_category_id import TicketCategoryId
from src.domain.shared.exceptions.domain_exception import DomainException
from src.domain.ticket.domain_events.ticket_checked_in import TicketCheckedIn
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
    _domain_events: List = field(default_factory=list, init=False, repr=False)

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

    # User Story - 13
    def check_in(self, event_id: EventId, check_in_time: datetime) -> None:
        """
        BR-T13: Check-in tiket saat peserta memasuki venue event.
        - Tiket harus berstatus ACTIVE
        - Tiket harus milik event yang sesuai
        - Check-in hanya boleh dilakukan pada hari event
        """
        # BR-T13: tiket harus berstatus ACTIVE
        if self.status == TicketStatus.CHECKED_IN:
            raise DomainException(
                "Ticket has already been checked in."
            )
        if self.status == TicketStatus.CANCELLED:
            raise DomainException(
                "Cancelled ticket cannot be checked in."
            )

        # BR-T13: tiket harus milik event yang sesuai
        if self.event_id != event_id:
            raise DomainException(
                "Ticket does not match the event."
            )

        self.status = TicketStatus.CHECKED_IN

        self._domain_events.append(
            TicketCheckedIn(
                ticket_id=self.id,
                event_id=self.event_id,
            )
        )

    def pull_domain_events(self) -> List:
        events = list(self._domain_events)
        self._domain_events.clear()
        return events