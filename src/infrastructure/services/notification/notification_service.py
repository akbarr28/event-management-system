import logging
from typing import List

from src.application.shared.interfaces.i_notification_service import INotificationService

logger = logging.getLogger(__name__)


class ConsoleNotificationService(INotificationService):
    """
    Implementasi sederhana INotificationService menggunakan console log.
    Pada production, ganti dengan integrasi email/WhatsApp aktual.
    """

    async def send_booking_confirmation(
        self,
        customer_email: str,
        booking_reference: str,
        event_name: str,
    ) -> None:
        logger.info(
            "[Notification] Booking confirmation sent to %s | ref=%s | event=%s",
            customer_email,
            booking_reference,
            event_name,
        )

    async def send_ticket_issued(
        self,
        customer_email: str,
        ticket_codes: List[str],
        event_name: str,
    ) -> None:
        logger.info(
            "[Notification] Tickets issued to %s | codes=%s | event=%s",
            customer_email,
            ticket_codes,
            event_name,
        )

    async def send_refund_status(
        self,
        customer_email: str,
        refund_reference: str,
        status: str,
        reason: str = "",
    ) -> None:
        logger.info(
            "[Notification] Refund status '%s' sent to %s | ref=%s | reason=%s",
            status,
            customer_email,
            refund_reference,
            reason,
        )

    async def send_event_cancelled(
        self,
        customer_email: str,
        event_name: str,
    ) -> None:
        logger.info(
            "[Notification] Event cancelled notification sent to %s | event=%s",
            customer_email,
            event_name,
        )

    async def notify_event_published(self, event) -> None:
        logger.info(
            "[Notification] Event published: %s (id=%s)",
            event.name,
            str(event.id),
        )