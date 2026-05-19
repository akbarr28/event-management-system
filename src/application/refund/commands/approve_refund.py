from dataclasses import dataclass


@dataclass(frozen=True)
class ApproveRefundCommand:
    """
    Command untuk menyetujui permintaan refund.
    Digunakan oleh Event Organizer.
    """
    refund_id: str
    organizer_id: str