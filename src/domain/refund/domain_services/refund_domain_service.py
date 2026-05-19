from typing import List

from src.domain.shared.exceptions.domain_exception import DomainException
from src.domain.ticket.entities.ticket import Ticket
from src.domain.ticket.value_objects.ticket_status import TicketStatus


class RefundDomainService:
    """
    Domain service untuk logika Refund yang melibatkan
    data dari aggregate lain (Ticket).
    """

    @staticmethod
    def has_checked_in_tickets(tickets: List[Ticket]) -> bool:
        """
        BR-R01: Mengecek apakah ada tiket dari booking
        yang sudah berstatus CHECKED_IN.
        """
        return any(
            ticket.status == TicketStatus.CHECKED_IN
            for ticket in tickets
        )

    @staticmethod
    def validate_no_checked_in_tickets(tickets: List[Ticket]) -> None:
        """
        BR-R01: Raise DomainException jika ada tiket
        yang sudah CHECKED_IN — shortcut untuk validasi langsung.
        """
        if RefundDomainService.has_checked_in_tickets(tickets):
            raise DomainException(
                "Refund cannot be requested because one or more "
                "tickets have already been checked in."
            )