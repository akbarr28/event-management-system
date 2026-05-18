from enum import Enum


class BookingStatus(Enum):
    PENDING_PAYMENT = "PENDING_PAYMENT"
    PAID = "PAID"
    EXPIRED = "EXPIRED"
    REFUNDED = "REFUNDED"