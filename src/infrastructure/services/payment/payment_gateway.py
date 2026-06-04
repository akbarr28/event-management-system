import logging
from decimal import Decimal

from src.application.shared.interfaces.i_payment_gateway import (
    IPaymentGateway,
    PaymentResult,
)

logger = logging.getLogger(__name__)


class ConsolePaymentGateway(IPaymentGateway):
    """
    Implementasi stub IPaymentGateway menggunakan console log.
    Pada production, ganti dengan integrasi payment gateway aktual
    seperti Midtrans atau Xendit.
    """

    async def process_payment(
        self,
        booking_reference: str,
        amount: Decimal,
        currency: str,
    ) -> PaymentResult:
        logger.info(
            "[PaymentGateway] Processing payment | ref=%s | amount=%s %s",
            booking_reference,
            amount,
            currency,
        )
        return PaymentResult(
            success=True,
            reference=f"PAY-{booking_reference[:8].upper()}",
            message="Payment processed successfully.",
        )