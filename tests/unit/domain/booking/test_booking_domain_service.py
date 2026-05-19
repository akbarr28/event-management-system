import pytest
from datetime import datetime, timedelta
from decimal import Decimal

from src.domain.booking.aggregates.booking import Booking
from src.domain.booking.domain_services.booking_domain_service import BookingDomainService
from src.domain.booking.value_objects.booking_status import BookingStatus
from src.domain.booking.value_objects.customer_id import CustomerId
from src.domain.event.value_objects.event_id import EventId
from src.domain.event.value_objects.ticket_category_id import TicketCategoryId
from src.domain.shared.exceptions.domain_exception import DomainException
from src.domain.shared.value_objects.money import Money


# Fixtures 

@pytest.fixture
def now():
    return datetime.utcnow()


@pytest.fixture
def customer_id():
    return CustomerId.generate()


@pytest.fixture
def event_id():
    return EventId.generate()


@pytest.fixture
def pending_booking(customer_id, event_id, now):
    """Booking berstatus PENDING_PAYMENT."""
    return Booking.create(
        customer_id=customer_id,
        event_id=event_id,
        ticket_category_id=TicketCategoryId.generate(),
        quantity=1,
        unit_price=Money(Decimal("150000"), "IDR"),
        now=now,
    )


@pytest.fixture
def paid_booking(customer_id, event_id, now):
    """Booking berstatus PAID."""
    booking = Booking.create(
        customer_id=customer_id,
        event_id=event_id,
        ticket_category_id=TicketCategoryId.generate(),
        quantity=1,
        unit_price=Money(Decimal("150000"), "IDR"),
        now=now,
    )
    booking.pay(
        payment_amount=Money(Decimal("150000"), "IDR"),
        now=now,
    )
    return booking


# Happy Path 

def test_no_active_booking_passes_with_empty_list(customer_id, event_id):
    """Validasi lolos jika belum ada booking sama sekali."""
    BookingDomainService.validate_no_active_booking_exists(
        customer_id=customer_id,
        event_id=event_id,
        existing_bookings=[],
    )


def test_no_active_booking_passes_with_expired_booking(
    customer_id, event_id, now
):
    """Booking EXPIRED tidak dianggap aktif — validasi lolos."""
    booking = Booking.create(
        customer_id=customer_id,
        event_id=event_id,
        ticket_category_id=TicketCategoryId.generate(),
        quantity=1,
        unit_price=Money(Decimal("150000"), "IDR"),
        now=now,
    )
    # Expire booking
    expired_time = now + timedelta(minutes=20)
    booking.expire(now=expired_time)

    BookingDomainService.validate_no_active_booking_exists(
        customer_id=customer_id,
        event_id=event_id,
        existing_bookings=[booking],
    )


def test_no_active_booking_passes_for_different_event(
    customer_id, event_id, pending_booking
):
    """Booking aktif di event lain tidak menghalangi booking baru."""
    different_event_id = EventId.generate()

    BookingDomainService.validate_no_active_booking_exists(
        customer_id=customer_id,
        event_id=different_event_id,
        existing_bookings=[pending_booking],
    )


def test_no_active_booking_passes_for_different_customer(
    customer_id, event_id, pending_booking
):
    """Booking aktif milik customer lain tidak menghalangi."""
    different_customer_id = CustomerId.generate()

    BookingDomainService.validate_no_active_booking_exists(
        customer_id=different_customer_id,
        event_id=event_id,
        existing_bookings=[pending_booking],
    )


# Unhappy Path 

def test_fails_when_pending_payment_booking_exists(
    customer_id, event_id, pending_booking
):
    """Booking PENDING_PAYMENT dianggap aktif — validasi gagal."""
    with pytest.raises(DomainException) as exc_info:
        BookingDomainService.validate_no_active_booking_exists(
            customer_id=customer_id,
            event_id=event_id,
            existing_bookings=[pending_booking],
        )

    assert "active booking" in str(exc_info.value).lower()


def test_fails_when_paid_booking_exists(customer_id, event_id, paid_booking):
    """Booking PAID dianggap aktif — validasi gagal."""
    with pytest.raises(DomainException) as exc_info:
        BookingDomainService.validate_no_active_booking_exists(
            customer_id=customer_id,
            event_id=event_id,
            existing_bookings=[paid_booking],
        )

    assert "active booking" in str(exc_info.value).lower()