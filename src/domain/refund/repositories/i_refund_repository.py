from abc import ABC, abstractmethod
from typing import Optional

from src.domain.booking.value_objects.booking_id import BookingId
from src.domain.refund.aggregates.refund import Refund
from src.domain.refund.value_objects.refund_id import RefundId


class IRefundRepository(ABC):

    @abstractmethod
    async def save(self, refund: Refund) -> None:
        raise NotImplementedError

    @abstractmethod
    async def find_by_id(self, refund_id: RefundId) -> Optional[Refund]:
        raise NotImplementedError

    @abstractmethod
    async def find_by_booking_id(self, booking_id: BookingId) -> Optional[Refund]:
        raise NotImplementedError