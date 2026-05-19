from dataclasses import dataclass


@dataclass(frozen=True)
class RejectRefundCommand:
    """
    Command untuk menolak permintaan refund.
    Digunakan oleh Event Organizer.
    """
    refund_id: str
    organizer_id: str
    rejection_reason: str