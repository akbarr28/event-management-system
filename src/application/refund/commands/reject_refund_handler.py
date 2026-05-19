from datetime import datetime

from src.application.refund.commands.reject_refund import RejectRefundCommand
from src.application.shared.dtos.refund_dto import RefundDTO
from src.application.shared.interfaces.i_notification_service import INotificationService
from src.domain.refund.repositories.i_refund_repository import IRefundRepository
from src.domain.refund.value_objects.refund_id import RefundId
from src.domain.shared.exceptions.domain_exception import DomainException


class RejectRefundHandler:
    """
    Command Handler untuk US-17: Reject Refund.
    Menolak refund request dengan alasan yang wajib diisi.
    Booking tetap PAID, tiket tetap ACTIVE.
    """

    def __init__(
        self,
        refund_repository: IRefundRepository,
        notification_service: INotificationService,
    ):
        self._refund_repository = refund_repository
        self._notification_service = notification_service

    async def handle(self, command: RejectRefundCommand) -> RefundDTO:
        now = datetime.utcnow()

        # Ambil refund
        refund_id = RefundId.from_string(command.refund_id)
        refund = await self._refund_repository.find_by_id(refund_id)
        if refund is None:
            raise DomainException("Refund not found.")

        # Reject refund di domain
        refund.reject(rejection_reason=command.rejection_reason)

        # Simpan refund
        await self._refund_repository.save(refund)

        # Kirim notifikasi ke customer
        await self._notification_service.send_refund_status(
            customer_email=str(refund.customer_id),
            refund_reference=str(refund.id),
            status="Rejected",
            reason=command.rejection_reason,
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