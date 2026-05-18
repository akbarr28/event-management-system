from abc import ABC, abstractmethod
from typing import List, Optional

from src.domain.booking.value_objects.booking_id import BookingId
from src.domain.booking.value_objects.customer_id import CustomerId
from src.domain.ticket.entities.ticket import Ticket
from src.domain.ticket.value_objects.ticket_id import TicketId
from src.domain.ticket.value_objects.ticket_code import TicketCode


class ITicketRepository(ABC):

    @abstractmethod
    async def save(self, ticket: Ticket) -> None:
        raise NotImplementedError

    @abstractmethod
    async def save_all(self, tickets: List[Ticket]) -> None:
        raise NotImplementedError

    @abstractmethod
    async def find_by_id(self, ticket_id: TicketId) -> Optional[Ticket]:
        raise NotImplementedError

    @abstractmethod
    async def find_by_code(self, ticket_code: TicketCode) -> Optional[Ticket]:
        raise NotImplementedError

    @abstractmethod
    async def find_by_booking_id(self, booking_id: BookingId) -> List[Ticket]:
        raise NotImplementedError

    @abstractmethod
    async def find_paid_tickets_by_customer(
        self, customer_id: CustomerId
    ) -> List[Ticket]:
        raise NotImplementedError