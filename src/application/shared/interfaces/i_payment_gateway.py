from abc import ABC, abstractmethod
from decimal import Decimal


class PaymentResult:
    def __init__(self, success: bool, reference: str, message: str = ""):
        self.success = success
        self.reference = reference
        self.message = message


class IPaymentGateway(ABC):
    """
    Interface untuk memproses pembayaran booking
    melalui payment gateway eksternal.
    Implementasinya ada di infrastructure layer.
    """

    @abstractmethod
    async def process_payment(
        self,
        booking_reference: str,
        amount: Decimal,
        currency: str,
    ) -> PaymentResult:
        raise NotImplementedError