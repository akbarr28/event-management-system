from datetime import datetime

from src.application.booking.commands.pay_booking import PayBookingCommand
from src.application.shared.interfaces.i_notification_service import INotificationService
from src.application.shared.interfaces.i_payment_gateway import (
    IPaymentGateway,
    PaymentResult,
)
from src.domain.booking.repositories.i_booking_repository import IBookingRepository
from src.domain.booking.value_objects.booking_id import BookingId
from src.domain.booking.value_objects.customer_id import CustomerId
from src.domain.event.repositories.i_event_repository import IEventRepository
from src.domain.shared.exceptions.domain_exception import DomainException
from src.domain.shared.value_objects.money import Money
from src.domain.ticket.repositories.i_ticket_repository import ITicketRepository


class PayBookingHandler:
    """
    Command Handler untuk US-10: Pay Booking.
    Memproses pembayaran booking dan menerbitkan tiket setelah berhasil.
    """

    def __init__(
        self,
        booking_repository: IBookingRepository,
        event_repository: IEventRepository,
        ticket_repository: ITicketRepository,
        payment_gateway: IPaymentGateway,
        notification_service: INotificationService,
    ):
        self._booking_repository = booking_repository
        self._event_repository = event_repository
        self._ticket_repository = ticket_repository
        self._payment_gateway = payment_gateway
        self._notification_service = notification_service

    async def handle(self, command: PayBookingCommand) -> None:
        booking_id = BookingId.from_string(command.booking_id)
        booking = await self._booking_repository.find_by_id(booking_id)

        if booking is None:
            raise DomainException("Booking not found.")

        customer_id = CustomerId.from_string(command.customer_id)

        if booking.customer_id != customer_id:
            raise DomainException("You are not authorized to pay this booking.")

        payment_amount = Money(
            amount=command.payment_amount,
            currency=command.currency,
        )

        result = await self._payment_gateway.process_payment(
            booking_reference=str(booking.id),
            amount=command.payment_amount,
            currency=command.currency,
        )

        if not result.success:
            raise DomainException(f"Payment failed: {result.message}")

        now = datetime.utcnow()

        booking.pay(
            payment_amount=payment_amount,
            now=now,
        )

        await self._booking_repository.save(booking)

        event = await self._event_repository.find_by_id(booking.event_id)

        tickets = booking.issue_tickets()
        await self._ticket_repository.save_all(tickets)

        ticket_codes = [str(t.ticket_code) for t in tickets]

        await self._notification_service.send_ticket_issued(
            customer_email=str(booking.customer_id),
            ticket_codes=ticket_codes,
            event_name=event.name if event else "",
        )

        booking.pull_domain_events()