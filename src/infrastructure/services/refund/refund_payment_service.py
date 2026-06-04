import logging
from decimal import Decimal

from src.application.shared.interfaces.i_refund_payment_service import (
    IRefundPaymentService,
    RefundPaymentResult,
)

logger = logging.getLogger(__name__)


class ConsoleRefundPaymentService(IRefundPaymentService):
    """
    Implementasi stub IRefundPaymentService menggunakan console log.
    Pada production, ganti dengan integrasi bank transfer aktual.
    """

    async def process_refund(
        self,
        customer_bank_account: str,
        amount: Decimal,
        currency: str,
        refund_reference: str,
    ) -> RefundPaymentResult:
        logger.info(
            "[RefundPaymentService] Processing refund | account=%s | amount=%s %s | ref=%s",
            customer_bank_account,
            amount,
            currency,
            refund_reference,
        )
        return RefundPaymentResult(
            success=True,
            reference=f"RFD-{refund_reference[:8].upper()}",
            message="Refund processed successfully.",
        )