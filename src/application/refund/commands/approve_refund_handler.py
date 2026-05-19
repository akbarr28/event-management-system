from src.application.refund.commands.approve_refund import ApproveRefundCommand
from src.application.shared.dtos.refund_dto import RefundDTO
from src.application.shared.interfaces.i_notification_service import INotificationService
from src.domain.booking.repositories.i_booking_repository import IBookingRepository
from src.domain.refund.repositories.i_refund_repository import IRefundRepository
from src.domain.refund.value_objects.refund_id import RefundId
from src.domain.shared.exceptions.domain_exception import DomainException
from src.domain.ticket.repositories.i_ticket_repository import ITicketRepository
from datetime import datetime


class ApproveRefundHandler:
    """
    Command Handler untuk US-16: Approve Refund.
    Menyetujui refund, cancel tiket terkait, dan mark booking sebagai refunded.
    """

    def __init__(
        self,
        refund_repository: IRefundRepository,
        booking_repository: IBookingRepository,
        ticket_repository: ITicketRepository,
        notification_service: INotificationService,
    ):
        self._refund_repository = refund_repository
        self._booking_repository = booking_repository
        self._ticket_repository = ticket_repository
        self._notification_service = notification_service

    async def handle(self, command: ApproveRefundCommand) -> RefundDTO:
        now = datetime.utcnow()

        # Ambil refund
        refund_id = RefundId.from_string(command.refund_id)
        refund = await self._refund_repository.find_by_id(refund_id)
        if refund is None:
            raise DomainException("Refund not found.")

        # Approve refund di domain
        refund.approve()

        # Ambil booking terkait dan mark sebagai refunded
        booking = await self._booking_repository.find_by_id(refund.booking_id)
        if booking is None:
            raise DomainException("Booking not found.")
        booking.mark_refunded()

        # Cancel semua tiket terkait booking
        tickets = await self._ticket_repository.find_by_booking_id(refund.booking_id)
        for ticket in tickets:
            ticket.cancel()
            await self._ticket_repository.save(ticket)

        # Simpan refund dan booking
        await self._refund_repository.save(refund)
        await self._booking_repository.save(booking)

        # Kirim notifikasi ke customer
        await self._notification_service.send_refund_status(
            customer_email=str(refund.customer_id),
            refund_reference=str(refund.id),
            status="Approved",
        )

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