from typing import List

from src.domain.booking.aggregates.booking import Booking
from src.domain.booking.value_objects.booking_status import BookingStatus
from src.domain.booking.value_objects.customer_id import CustomerId
from src.domain.event.value_objects.event_id import EventId
from src.domain.shared.exceptions.domain_exception import DomainException


class BookingDomainService:
    """
    Domain service untuk logika Booking yang melibatkan
    lebih dari satu Booking aggregate sekaligus.
    """

    @staticmethod
    def validate_no_active_booking_exists(
        customer_id: CustomerId,
        event_id: EventId,
        existing_bookings: List[Booking],
    ) -> None:
        """
        BR-B08: Satu customer hanya boleh memiliki satu booking
        aktif untuk event yang sama.

        Active booking = PENDING_PAYMENT atau PAID.
        EXPIRED dan REFUNDED tidak dihitung aktif.
        """
        active_statuses = {BookingStatus.PENDING_PAYMENT, BookingStatus.PAID}

        for booking in existing_bookings:
            if (
                booking.customer_id == customer_id
                and booking.event_id == event_id
                and booking.status in active_statuses
            ):
                raise DomainException(
                    "Customer already has an active booking for this event."
                )