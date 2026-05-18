"""
Unit Tests — User Story 10: Pay Booking

Business Rules yang diuji:
- BR-B10-01: Booking harus berstatus PendingPayment untuk bisa dibayar
- BR-B10-02: Booking tidak bisa dibayar jika payment deadline sudah lewat
- BR-B10-03: Jumlah pembayaran harus sama dengan total price
- BR-B10-04: Setelah bayar, status berubah menjadi Paid
- BR-B10-05: Domain event BookingPaid di-raise setelah pembayaran berhasil
"""

import pytest
from datetime import datetime, timedelta
from decimal import Decimal

from src.domain.booking.aggregates.booking import Booking, PAYMENT_DEADLINE_MINUTES
from src.domain.booking.domain_events.booking_paid import BookingPaid
from src.domain.booking.value_objects.booking_status import BookingStatus
from src.domain.booking.value_objects.customer_id import CustomerId
from src.domain.event.value_objects.event_id import EventId
from src.domain.event.value_objects.ticket_category_id import TicketCategoryId
from src.domain.shared.exceptions.domain_exception import DomainException
from src.domain.shared.value_objects.money import Money



@pytest.fixture
def now():
    return datetime.utcnow()


@pytest.fixture
def unit_price():
    return Money(amount=Decimal("100000"), currency="IDR")


@pytest.fixture
def pending_booking(unit_price, now):
    return Booking.create(
        customer_id=CustomerId.generate(),
        event_id=EventId.generate(),
        ticket_category_id=TicketCategoryId.generate(),
        quantity=2,
        unit_price=unit_price,
        now=now,
    )


class TestPayBookingSuccess:

    def test_booking_status_changes_to_paid(self, pending_booking, now):
        """BR-B10-04: Status booking berubah menjadi Paid setelah bayar."""
        payment = pending_booking.total_price

        pending_booking.pay(payment_amount=payment, now=now)

        assert pending_booking.status == BookingStatus.PAID

    def test_booking_data_unchanged_after_payment(self, pending_booking, now):
        """Quantity dan total price tidak berubah setelah pembayaran."""
        original_quantity = pending_booking.quantity
        original_total = pending_booking.total_price
        payment = pending_booking.total_price

        pending_booking.pay(payment_amount=payment, now=now)

        assert pending_booking.quantity == original_quantity
        assert pending_booking.total_price == original_total

class TestPayBookingStatusValidation:

    def test_paid_booking_cannot_be_paid_again(self, pending_booking, now):
        """BR-B10-01: Booking yang sudah Paid tidak bisa dibayar lagi."""
        payment = pending_booking.total_price
        pending_booking.pay(payment_amount=payment, now=now)

        with pytest.raises(DomainException):
            pending_booking.pay(payment_amount=payment, now=now)

    def test_expired_booking_cannot_be_paid(self, unit_price, now):
        """BR-B10-01: Booking yang sudah Expired tidak bisa dibayar."""
        booking = Booking.create(
            customer_id=CustomerId.generate(),
            event_id=EventId.generate(),
            ticket_category_id=TicketCategoryId.generate(),
            quantity=1,
            unit_price=unit_price,
            now=now,
        )
        # Simulasi expired
        booking.status = BookingStatus.EXPIRED

        with pytest.raises(DomainException):
            booking.pay(payment_amount=booking.total_price, now=now)



class TestPayBookingDeadline:

    def test_booking_cannot_be_paid_after_deadline(self, pending_booking):
        """BR-B10-02: Pembayaran setelah deadline harus ditolak."""
        after_deadline = pending_booking.payment_deadline + timedelta(seconds=1)

        with pytest.raises(DomainException):
            pending_booking.pay(
                payment_amount=pending_booking.total_price,
                now=after_deadline,
            )

    def test_booking_can_be_paid_before_deadline(self, pending_booking, now):
        """BR-B10-02: Pembayaran sebelum deadline harus berhasil."""
        before_deadline = pending_booking.payment_deadline - timedelta(seconds=1)

        pending_booking.pay(
            payment_amount=pending_booking.total_price,
            now=before_deadline,
        )

        assert pending_booking.status == BookingStatus.PAID

    def test_booking_can_be_paid_exactly_at_deadline(self, pending_booking):
        """BR-B10-02: Pembayaran tepat di deadline harus berhasil."""
        exactly_at_deadline = pending_booking.payment_deadline

        pending_booking.pay(
            payment_amount=pending_booking.total_price,
            now=exactly_at_deadline,
        )

        assert pending_booking.status == BookingStatus.PAID



class TestPayBookingAmount:

    def test_payment_less_than_total_is_rejected(self, pending_booking, now):
        """BR-B10-03: Pembayaran kurang dari total harus ditolak."""
        less_than_total = Money(
            amount=pending_booking.total_price.amount - Decimal("1"),
            currency="IDR",
        )

        with pytest.raises(DomainException):
            pending_booking.pay(payment_amount=less_than_total, now=now)

    def test_payment_more_than_total_is_rejected(self, pending_booking, now):
        """BR-B10-03: Pembayaran lebih dari total harus ditolak."""
        more_than_total = Money(
            amount=pending_booking.total_price.amount + Decimal("1"),
            currency="IDR",
        )

        with pytest.raises(DomainException):
            pending_booking.pay(payment_amount=more_than_total, now=now)

    def test_payment_exactly_equal_to_total_is_accepted(self, pending_booking, now):
        """BR-B10-03: Pembayaran tepat sama dengan total harus diterima."""
        pending_booking.pay(
            payment_amount=pending_booking.total_price,
            now=now,
        )

        assert pending_booking.status == BookingStatus.PAID


class TestBookingPaidDomainEvent:

    def test_booking_paid_event_is_raised(self, pending_booking, now):
        """BR-B10-05: Domain event BookingPaid harus di-raise."""
        pending_booking.pull_domain_events()  # bersihkan event dari create
        payment = pending_booking.total_price

        pending_booking.pay(payment_amount=payment, now=now)
        events = pending_booking.pull_domain_events()

        assert len(events) == 1
        assert isinstance(events[0], BookingPaid)

    def test_booking_paid_event_contains_correct_data(self, pending_booking, now):
        """BR-B10-05: Data dalam BookingPaid harus sesuai dengan booking."""
        pending_booking.pull_domain_events()
        payment = pending_booking.total_price

        pending_booking.pay(payment_amount=payment, now=now)
        events = pending_booking.pull_domain_events()
        event = events[0]

        assert event.booking_id == pending_booking.id
        assert event.customer_id == pending_booking.customer_id
        assert event.event_id == pending_booking.event_id
        assert event.amount_paid == payment