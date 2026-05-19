from abc import ABC, abstractmethod
from typing import List, Optional

from src.domain.booking.aggregates.booking import Booking
from src.domain.booking.value_objects.booking_id import BookingId
from src.domain.booking.value_objects.booking_status import BookingStatus
from src.domain.booking.value_objects.customer_id import CustomerId
from src.domain.event.value_objects.event_id import EventId


class IBookingRepository(ABC):

    @abstractmethod
    async def save(self, booking: Booking) -> None:
        raise NotImplementedError

    @abstractmethod
    async def find_by_id(self, booking_id: BookingId) -> Optional[Booking]:
        raise NotImplementedError

    @abstractmethod
    async def find_active_booking_by_customer_and_event(
        self,
        customer_id: CustomerId,
        event_id: EventId,
    ) -> Optional[Booking]:
        raise NotImplementedError

    @abstractmethod
    async def find_by_customer_id(self, customer_id: CustomerId) -> List[Booking]:
        raise NotImplementedError
    
    @abstractmethod
    async def find_by_event_id(self, event_id: EventId) -> List[Booking]:
        raise NotImplementedError