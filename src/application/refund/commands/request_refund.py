from dataclasses import dataclass


@dataclass(frozen=True)
class RequestRefundCommand:
    """
    Command untuk mengajukan permintaan refund.
    Digunakan oleh Customer.
    """
    booking_id: str
    customer_id: str