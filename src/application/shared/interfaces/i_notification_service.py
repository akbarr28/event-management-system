from abc import ABC, abstractmethod
from typing import List


class INotificationService(ABC):
    """
    Interface untuk mengirim notifikasi email atau WhatsApp
    ke customer dan organizer.
    Implementasinya ada di infrastructure layer.
    """

    @abstractmethod
    async def send_booking_confirmation(
        self,
        customer_email: str,
        booking_reference: str,
        event_name: str,
    ) -> None:
        raise NotImplementedError

    @abstractmethod
    async def send_ticket_issued(
        self,
        customer_email: str,
        ticket_codes: List[str],
        event_name: str,
    ) -> None:
        raise NotImplementedError

    @abstractmethod
    async def send_refund_status(
        self,
        customer_email: str,
        refund_reference: str,
        status: str,
        reason: str = "",
    ) -> None:
        raise NotImplementedError

    @abstractmethod
    async def send_event_cancelled(
        self,
        customer_email: str,
        event_name: str,
    ) -> None:
        raise NotImplementedError