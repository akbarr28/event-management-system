from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional

from src.domain.booking.value_objects.booking_id import BookingId
from src.domain.booking.value_objects.booking_status import BookingStatus
from src.domain.booking.value_objects.customer_id import CustomerId
from src.domain.event.value_objects.event_status import EventStatus
from src.domain.refund.domain_events.refund_approved import RefundApproved
from src.domain.refund.domain_events.refund_requested import RefundRequested
from src.domain.refund.value_objects.refund_id import RefundId
from src.domain.refund.value_objects.refund_status import RefundStatus
from src.domain.shared.exceptions.domain_exception import DomainException
from src.domain.shared.value_objects.money import Money


@dataclass
class Refund:
    id: RefundId
    booking_id: BookingId
    customer_id: CustomerId
    amount: Money
    status: RefundStatus
    rejection_reason: Optional[str] = field(default=None)
    payment_reference: Optional[str] = field(default=None)
    _domain_events: List = field(default_factory=list, init=False, repr=False)

    # User Story - 15

    @staticmethod
    def request(
        booking_id: BookingId,
        customer_id: CustomerId,
        amount: Money,
        booking_status: BookingStatus,
        event_status: EventStatus,
        has_checked_in_tickets: bool,
        refund_deadline: datetime,
        now: datetime,
    ) -> "Refund":
        """
        BR-R01: Mengajukan permintaan refund.
        - Booking harus berstatus PAID
        - Tidak ada tiket yang sudah CHECKED_IN
        - Masih dalam refund deadline
        - Jika event CANCELLED, refund otomatis diizinkan
        """
        # BR-R01: booking harus berstatus PAID
        if booking_status != BookingStatus.PAID:
            raise DomainException(
                "Refund can only be requested for a paid booking."
            )

        # BR-R01: jika event CANCELLED, langsung boleh tanpa cek deadline
        # dan checked-in tickets
        if event_status != EventStatus.CANCELLED:
            # BR-R01: tidak ada tiket yang sudah CHECKED_IN
            if has_checked_in_tickets:
                raise DomainException(
                    "Refund cannot be requested because one or more tickets "
                    "have already been checked in."
                )

            # BR-R01: harus sebelum refund deadline
            if now > refund_deadline:
                raise DomainException(
                    "Refund deadline has passed."
                )

        refund = Refund(
            id=RefundId.generate(),
            booking_id=booking_id,
            customer_id=customer_id,
            amount=amount,
            status=RefundStatus.REQUESTED,
        )

        refund._domain_events.append(
            RefundRequested(
                refund_id=refund.id,
                booking_id=booking_id,
                customer_id=customer_id,
            )
        )

        return refund
    
    # User Story - 16

    def approve(self) -> None:
        """
        BR-R02: Menyetujui permintaan refund.
        - Refund harus berstatus REQUESTED
        - Status berubah menjadi APPROVED
        - Application layer yang akan cancel tiket & mark booking refunded
        """
        if self.status != RefundStatus.REQUESTED:
            raise DomainException(
                "Refund can only be approved if its status is Requested."
            )

        self.status = RefundStatus.APPROVED

        self._domain_events.append(
            RefundApproved(
                refund_id=self.id,
                booking_id=self.booking_id,
            )
        )

    def pull_domain_events(self) -> List:
        events = list(self._domain_events)
        self._domain_events.clear()
        return events