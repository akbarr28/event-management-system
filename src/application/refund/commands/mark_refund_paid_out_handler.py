from datetime import datetime

from src.application.refund.commands.mark_refund_paid_out import MarkRefundPaidOutCommand
from src.application.shared.dtos.refund_dto import RefundDTO
from src.application.shared.interfaces.i_refund_payment_service import IRefundPaymentService
from src.domain.refund.repositories.i_refund_repository import IRefundRepository
from src.domain.refund.value_objects.refund_id import RefundId
from src.domain.shared.exceptions.domain_exception import DomainException


class MarkRefundPaidOutHandler:
    """
    Command Handler untuk US-18: Mark Refund as Paid Out.
    Menandai refund sebagai sudah dibayarkan ke customer.
    """

    def __init__(
        self,
        refund_repository: IRefundRepository,
        refund_payment_service: IRefundPaymentService,
    ):
        self._refund_repository = refund_repository
        self._refund_payment_service = refund_payment_service

    async def handle(self, command: MarkRefundPaidOutCommand) -> RefundDTO:
        now = datetime.utcnow()

        # Ambil refund
        refund_id = RefundId.from_string(command.refund_id)
        refund = await self._refund_repository.find_by_id(refund_id)
        if refund is None:
            raise DomainException("Refund not found.")

        # Proses pencairan lewat bank service
        result = await self._refund_payment_service.process_refund(
            customer_bank_account=str(refund.customer_id),
            amount=refund.amount.amount,
            currency=refund.amount.currency,
            refund_reference=command.payment_reference,
        )
        if not result.success:
            raise DomainException(
                f"Refund payment failed: {result.message}"
            )

        # Mark paid out di domain
        refund.mark_paid_out(payment_reference=command.payment_reference)

        # Simpan refund
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