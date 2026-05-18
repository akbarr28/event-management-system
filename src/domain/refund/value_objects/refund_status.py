from enum import Enum


class RefundStatus(Enum):
    REQUESTED = "REQUESTED"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    PAID_OUT = "PAID_OUT"