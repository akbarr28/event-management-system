from abc import ABC, abstractmethod
from decimal import Decimal


class RefundPaymentResult:
    def __init__(self, success: bool, reference: str, message: str = ""):
        self.success = success
        self.reference = reference
        self.message = message


class IRefundPaymentService(ABC):
    """
    Interface untuk memproses pencairan refund ke rekening
    customer melalui bank service eksternal.
    Implementasinya ada di infrastructure layer.
    """

    @abstractmethod
    async def process_refund(
        self,
        customer_bank_account: str,
        amount: Decimal,
        currency: str,
        refund_reference: str,
    ) -> RefundPaymentResult:
        raise NotImplementedError