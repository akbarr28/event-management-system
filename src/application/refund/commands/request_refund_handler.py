from datetime import datetime, timedelta

from src.application.refund.commands.request_refund import RequestRefundCommand
from src.application.shared.dtos.refund_dto import RefundDTO
from src.domain.booking.repositories.i_booking_repository import IBookingRepository
from src.domain.booking.value_objects.booking_id import BookingId
from src.domain.booking.value_objects.customer_id import CustomerId
from src.domain.event.repositories.i_event_repository import IEventRepository
from src.domain.refund.aggregates.refund import Refund
from src.domain.refund.domain_services.refund_domain_service import RefundDomainService
from src.domain.refund.repositories.i_refund_repository import IRefundRepository
from src.domain.shared.exceptions.domain_exception import DomainException
from src.domain.ticket.repositories.i_ticket_repository import ITicketRepository

REFUND_DEADLINE_DAYS = 7


class RequestRefundHandler:
    """
    Command Handler untuk US-15: Request Refund.
    Memvalidasi booking, tiket, dan deadline sebelum membuat refund request.
    """

    def __init__(
        self,
        booking_repository: IBookingRepository,
        event_repository: IEventRepository,
        ticket_repository: ITicketRepository,
        refund_repository: IRefundRepository,
    ):
        self._booking_repository = booking_repository
        self._event_repository = event_repository
        self._ticket_repository = ticket_repository
        self._refund_repository = refund_repository

    async def handle(self, command: RequestRefundCommand) -> RefundDTO:
        now = datetime.utcnow()

        # Ambil booking
        booking_id = BookingId.from_string(command.booking_id)
        booking = await self._booking_repository.find_by_id(booking_id)
        if booking is None:
            raise DomainException("Booking not found.")

        # Pastikan customer adalah pemilik booking
        customer_id = CustomerId.from_string(command.customer_id)
        if booking.customer_id != customer_id:
            raise DomainException(
                "Only the booking owner can request a refund."
            )

        # Ambil event untuk cek status
        event = await self._event_repository.find_by_id(booking.event_id)
        if event is None:
            raise DomainException("Event not found.")

        # Ambil semua tiket terkait booking
        tickets = await self._ticket_repository.find_by_booking_id(booking_id)

        # Cek apakah ada tiket yang sudah checked-in
        has_checked_in = RefundDomainService.has_checked_in_tickets(tickets)

        # Hitung refund deadline dari payment deadline booking
        refund_deadline = booking.payment_deadline + timedelta(
            days=REFUND_DEADLINE_DAYS
        )

        # Buat refund request lewat domain
        refund = Refund.request(
            booking_id=booking_id,
            customer_id=customer_id,
            amount=booking.total_price,
            booking_status=booking.status,
            event_status=event.status,
            has_checked_in_tickets=has_checked_in,
            refund_deadline=refund_deadline,
            now=now,
        )

        await self._refund_repository.save(refund)

        refund.pull_domain_events()

        return RefundDTO(
            id=str(refund.id),
            booking_id=str(refund.booking_id),
            customer_id=str(refund.customer_id),
            amount=refund.amount.amount,
            currency=refund.amount.currency,
            status=refund.status.value,
            rejection_reason=refund.rejection_reason,
            payment_reference=refund.payment_reference,
            occurred_at=now,
        )