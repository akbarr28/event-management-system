from dataclasses import dataclass


@dataclass(frozen=True)
class MarkRefundPaidOutCommand:
    """
    Command untuk menandai refund sebagai sudah dibayarkan.
    Digunakan oleh System Admin.
    """
    refund_id: str
    payment_reference: str