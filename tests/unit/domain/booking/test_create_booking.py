"""
Unit Tests — User Story 08: Create Ticket Booking

Business Rules yang diuji:
- BR-B08-01: Quantity harus lebih dari nol
- BR-B08-02: Status awal booking adalah PendingPayment
- BR-B08-03: Payment deadline adalah 15 menit setelah booking dibuat
- BR-B08-04: Total price = unit price x quantity
- BR-B08-05: Domain event TicketReserved di-raise setelah booking dibuat
"""

import pytest
from datetime import datetime, timedelta
from decimal import Decimal

from src.domain.booking.aggregates.booking import Booking, PAYMENT_DEADLINE_MINUTES
from src.domain.booking.value_objects.booking_status import BookingStatus
from src.domain.booking.domain_events.ticket_reserved import TicketReserved
from src.domain.booking.value_objects.customer_id import CustomerId
from src.domain.event.value_objects.event_id import EventId
from src.domain.event.value_objects.ticket_category_id import TicketCategoryId
from src.domain.shared.value_objects.money import Money


@pytest.fixture
def customer_id():
    return CustomerId.generate()


@pytest.fixture
def event_id():
    return EventId.generate()


@pytest.fixture
def ticket_category_id():
    return TicketCategoryId.generate()


@pytest.fixture
def unit_price():
    return Money(amount=Decimal("100000"), currency="IDR")


@pytest.fixture
def now():
    return datetime.utcnow()


class TestBookingInitialStatus:

    def test_newly_created_booking_has_pending_payment_status(
        self, customer_id, event_id, ticket_category_id, unit_price, now
    ):
        """BR-B08-02: Booking baru harus berstatus PendingPayment."""
        booking = Booking.create(
            customer_id=customer_id,
            event_id=event_id,
            ticket_category_id=ticket_category_id,
            quantity=2,
            unit_price=unit_price,
            now=now,
        )

        assert booking.status == BookingStatus.PENDING_PAYMENT


class TestPaymentDeadline:

    def test_payment_deadline_is_15_minutes_after_creation(
        self, customer_id, event_id, ticket_category_id, unit_price, now
    ):
        """BR-B08-03: Payment deadline harus 15 menit setelah booking dibuat."""
        booking = Booking.create(
            customer_id=customer_id,
            event_id=event_id,
            ticket_category_id=ticket_category_id,
            quantity=1,
            unit_price=unit_price,
            now=now,
        )

        expected_deadline = now + timedelta(minutes=PAYMENT_DEADLINE_MINUTES)
        assert booking.payment_deadline == expected_deadline

    def test_payment_deadline_is_in_the_future(
        self, customer_id, event_id, ticket_category_id, unit_price, now
    ):
        """BR-B08-03: Payment deadline harus di masa depan."""
        booking = Booking.create(
            customer_id=customer_id,
            event_id=event_id,
            ticket_category_id=ticket_category_id,
            quantity=1,
            unit_price=unit_price,
            now=now,
        )

        assert booking.payment_deadline > now


class TestTotalPrice:

    def test_total_price_equals_unit_price_times_quantity(
        self, customer_id, event_id, ticket_category_id, unit_price, now
    ):
        """BR-B08-04: Total price = unit price x quantity."""
        booking = Booking.create(
            customer_id=customer_id,
            event_id=event_id,
            ticket_category_id=ticket_category_id,
            quantity=3,
            unit_price=unit_price,
            now=now,
        )

        expected_total = Money(amount=Decimal("300000"), currency="IDR")
        assert booking.total_price == expected_total

    def test_total_price_for_quantity_one(
        self, customer_id, event_id, ticket_category_id, unit_price, now
    ):
        """BR-B08-04: Total price untuk quantity 1 sama dengan unit price."""
        booking = Booking.create(
            customer_id=customer_id,
            event_id=event_id,
            ticket_category_id=ticket_category_id,
            quantity=1,
            unit_price=unit_price,
            now=now,
        )

        assert booking.total_price == unit_price

    def test_total_price_for_free_event(
        self, customer_id, event_id, ticket_category_id, now
    ):
        """BR-B08-04: Total price untuk free event (harga 0) adalah 0."""
        free_price = Money(amount=Decimal("0"), currency="IDR")
        booking = Booking.create(
            customer_id=customer_id,
            event_id=event_id,
            ticket_category_id=ticket_category_id,
            quantity=5,
            unit_price=free_price,
            now=now,
        )

        assert booking.total_price == Money(amount=Decimal("0"), currency="IDR")


class TestBookingQuantityValidation:

    def test_booking_cannot_be_created_with_zero_quantity(
        self, customer_id, event_id, ticket_category_id, unit_price, now
    ):
        """BR-B08-01: Quantity nol harus ditolak."""
        from src.domain.shared.exceptions.domain_exception import DomainException

        with pytest.raises(DomainException):
            Booking.create(
                customer_id=customer_id,
                event_id=event_id,
                ticket_category_id=ticket_category_id,
                quantity=0,
                unit_price=unit_price,
                now=now,
            )

    def test_booking_cannot_be_created_with_negative_quantity(
        self, customer_id, event_id, ticket_category_id, unit_price, now
    ):
        """BR-B08-01: Quantity negatif harus ditolak."""
        from src.domain.shared.exceptions.domain_exception import DomainException

        with pytest.raises(DomainException):
            Booking.create(
                customer_id=customer_id,
                event_id=event_id,
                ticket_category_id=ticket_category_id,
                quantity=-1,
                unit_price=unit_price,
                now=now,
            )

    def test_booking_can_be_created_with_quantity_one(
        self, customer_id, event_id, ticket_category_id, unit_price, now
    ):
        """BR-B08-01: Quantity 1 adalah minimum yang valid."""
        booking = Booking.create(
            customer_id=customer_id,
            event_id=event_id,
            ticket_category_id=ticket_category_id,
            quantity=1,
            unit_price=unit_price,
            now=now,
        )

        assert booking.quantity == 1


class TestTicketReservedDomainEvent:

    def test_ticket_reserved_event_is_raised_after_booking_created(
        self, customer_id, event_id, ticket_category_id, unit_price, now
    ):
        """BR-B08-05: Domain event TicketReserved harus di-raise."""
        booking = Booking.create(
            customer_id=customer_id,
            event_id=event_id,
            ticket_category_id=ticket_category_id,
            quantity=2,
            unit_price=unit_price,
            now=now,
        )

        events = booking.pull_domain_events()

        assert len(events) == 1
        assert isinstance(events[0], TicketReserved)

    def test_ticket_reserved_event_contains_correct_data(
        self, customer_id, event_id, ticket_category_id, unit_price, now
    ):
        """BR-B08-05: Data dalam TicketReserved harus sesuai dengan booking."""
        booking = Booking.create(
            customer_id=customer_id,
            event_id=event_id,
            ticket_category_id=ticket_category_id,
            quantity=2,
            unit_price=unit_price,
            now=now,
        )

        events = booking.pull_domain_events()
        event = events[0]

        assert event.booking_id == booking.id
        assert event.customer_id == customer_id
        assert event.event_id == event_id
        assert event.ticket_category_id == ticket_category_id
        assert event.quantity == 2

    def test_pull_domain_events_clears_events(
        self, customer_id, event_id, ticket_category_id, unit_price, now
    ):
        """Domain events dikosongkan setelah di-pull."""
        booking = Booking.create(
            customer_id=customer_id,
            event_id=event_id,
            ticket_category_id=ticket_category_id,
            quantity=1,
            unit_price=unit_price,
            now=now,
        )

        booking.pull_domain_events()
        assert booking.pull_domain_events() == []