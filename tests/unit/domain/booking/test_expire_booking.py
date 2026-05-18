"""
Unit Tests — User Story 11: Expire Booking

Business Rules yang diuji:
- BR-B11-01: Hanya booking PendingPayment yang bisa di-expire
- BR-B11-02: Booking Paid tidak bisa di-expire
- BR-B11-03: Booking bisa di-expire hanya setelah payment deadline lewat
- BR-B11-04: Status berubah menjadi Expired
- BR-B11-05: Domain event BookingExpired di-raise
"""

import pytest
from datetime import datetime, timedelta
from decimal import Decimal

from src.domain.booking.aggregates.booking import Booking, PAYMENT_DEADLINE_MINUTES
from src.domain.booking.domain_events.booking_expired import BookingExpired
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


@pytest.fixture
def after_deadline(pending_booking):
    return pending_booking.payment_deadline + timedelta(seconds=1)



class TestExpireBookingSuccess:

    def test_booking_status_changes_to_expired(self, pending_booking, after_deadline):
        """BR-B11-04: Status booking berubah menjadi Expired."""
        pending_booking.expire(now=after_deadline)

        assert pending_booking.status == BookingStatus.EXPIRED

    def test_expired_booking_retains_original_data(self, pending_booking, after_deadline):
        """Data booking tidak berubah setelah di-expire."""
        original_quantity = pending_booking.quantity
        original_total = pending_booking.total_price

        pending_booking.expire(now=after_deadline)

        assert pending_booking.quantity == original_quantity
        assert pending_booking.total_price == original_total



class TestPaidBookingCannotExpire:

    def test_paid_booking_cannot_be_expired(self, pending_booking, now, after_deadline):
        """BR-B11-02: Paid booking tidak bisa di-expire."""
        pending_booking.pay(
            payment_amount=pending_booking.total_price,
            now=now,
        )

        with pytest.raises(DomainException):
            pending_booking.expire(now=after_deadline)

    def test_error_message_for_paid_booking_expiry(self, pending_booking, now, after_deadline):
        """BR-B11-02: Pesan error harus jelas untuk paid booking."""
        pending_booking.pay(
            payment_amount=pending_booking.total_price,
            now=now,
        )

        with pytest.raises(DomainException) as exc_info:
            pending_booking.expire(now=after_deadline)

        assert "paid" in str(exc_info.value).lower()



class TestOnlyPendingPaymentCanExpire:

    def test_already_expired_booking_cannot_be_expired_again(
        self, pending_booking, after_deadline
    ):
        """BR-B11-01: Booking yang sudah Expired tidak bisa di-expire lagi."""
        pending_booking.expire(now=after_deadline)

        with pytest.raises(DomainException):
            pending_booking.expire(now=after_deadline)

    def test_refunded_booking_cannot_be_expired(self, unit_price, now, after_deadline):
        """BR-B11-01: Booking Refunded tidak bisa di-expire."""
        booking = Booking.create(
            customer_id=CustomerId.generate(),
            event_id=EventId.generate(),
            ticket_category_id=TicketCategoryId.generate(),
            quantity=1,
            unit_price=unit_price,
            now=now,
        )
        booking.status = BookingStatus.REFUNDED

        with pytest.raises(DomainException):
            booking.expire(now=after_deadline)



class TestExpireBookingDeadline:

    def test_booking_cannot_be_expired_before_deadline(self, pending_booking, now):
        """BR-B11-03: Booking tidak bisa di-expire sebelum deadline lewat."""
        before_deadline = pending_booking.payment_deadline - timedelta(seconds=1)

        with pytest.raises(DomainException):
            pending_booking.expire(now=before_deadline)

    def test_booking_cannot_be_expired_exactly_at_deadline(self, pending_booking):
        """BR-B11-03: Booking tidak bisa di-expire tepat di deadline."""
        exactly_at_deadline = pending_booking.payment_deadline

        with pytest.raises(DomainException):
            pending_booking.expire(now=exactly_at_deadline)

    def test_booking_can_be_expired_after_deadline(self, pending_booking, after_deadline):
        """BR-B11-03: Booking bisa di-expire setelah deadline lewat."""
        pending_booking.expire(now=after_deadline)

        assert pending_booking.status == BookingStatus.EXPIRED



class TestBookingExpiredDomainEvent:

    def test_booking_expired_event_is_raised(self, pending_booking, after_deadline):
        """BR-B11-05: Domain event BookingExpired harus di-raise."""
        pending_booking.pull_domain_events()  # bersihkan event dari create

        pending_booking.expire(now=after_deadline)
        events = pending_booking.pull_domain_events()

        assert len(events) == 1
        assert isinstance(events[0], BookingExpired)

    def test_booking_expired_event_contains_correct_data(
        self, pending_booking, after_deadline
    ):
        """BR-B11-05: Data dalam BookingExpired harus sesuai dengan booking."""
        pending_booking.pull_domain_events()

        pending_booking.expire(now=after_deadline)
        events = pending_booking.pull_domain_events()
        event = events[0]

        assert event.booking_id == pending_booking.id
        assert event.customer_id == pending_booking.customer_id
        assert event.event_id == pending_booking.event_id
        assert event.ticket_category_id == pending_booking.ticket_category_id
        assert event.quantity == pending_booking.quantity