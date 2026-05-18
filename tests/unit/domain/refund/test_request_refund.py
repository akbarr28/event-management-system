import pytest
from datetime import datetime, timedelta
from decimal import Decimal

from src.domain.booking.value_objects.booking_id import BookingId
from src.domain.booking.value_objects.booking_status import BookingStatus
from src.domain.booking.value_objects.customer_id import CustomerId
from src.domain.event.value_objects.event_status import EventStatus
from src.domain.refund.aggregates.refund import Refund
from src.domain.refund.domain_events.refund_requested import RefundRequested
from src.domain.refund.value_objects.refund_status import RefundStatus
from src.domain.shared.exceptions.domain_exception import DomainException
from src.domain.shared.value_objects.money import Money


# Fixtures 

@pytest.fixture
def now():
    return datetime.utcnow()


@pytest.fixture
def refund_deadline(now):
    return now + timedelta(days=7)


@pytest.fixture
def valid_refund_data(now, refund_deadline):
    return {
        "booking_id": BookingId.generate(),
        "customer_id": CustomerId.generate(),
        "amount": Money(Decimal("150000"), "IDR"),
        "booking_status": BookingStatus.PAID,
        "event_status": EventStatus.PUBLISHED,
        "has_checked_in_tickets": False,
        "refund_deadline": refund_deadline,
        "now": now,
    }


# Happy Path 

def test_request_refund_success(valid_refund_data):
    """Refund berhasil diajukan dengan data yang valid."""
    refund = Refund.request(**valid_refund_data)

    assert refund.status == RefundStatus.REQUESTED
    assert refund.booking_id == valid_refund_data["booking_id"]
    assert refund.customer_id == valid_refund_data["customer_id"]
    assert refund.amount == valid_refund_data["amount"]


def test_request_refund_initial_status_is_requested(valid_refund_data):
    """Status awal refund harus REQUESTED."""
    refund = Refund.request(**valid_refund_data)

    assert refund.status == RefundStatus.REQUESTED


def test_request_refund_raises_domain_event(valid_refund_data):
    """Sistem harus raise domain event RefundRequested."""
    refund = Refund.request(**valid_refund_data)
    domain_events = refund.pull_domain_events()

    assert len(domain_events) == 1
    assert isinstance(domain_events[0], RefundRequested)
    assert domain_events[0].refund_id == refund.id
    assert domain_events[0].booking_id == valid_refund_data["booking_id"]


def test_request_refund_generates_unique_id(valid_refund_data):
    """Setiap refund harus punya ID unik."""
    refund_1 = Refund.request(**valid_refund_data)
    refund_2 = Refund.request(**valid_refund_data)

    assert refund_1.id != refund_2.id


def test_request_refund_no_rejection_reason_initially(valid_refund_data):
    """Refund yang baru dibuat tidak punya rejection reason."""
    refund = Refund.request(**valid_refund_data)

    assert refund.rejection_reason is None
    assert refund.payment_reference is None


def test_request_refund_allowed_when_event_cancelled(valid_refund_data, now):
    """Refund otomatis diizinkan jika event dibatalkan meski deadline lewat."""
    valid_refund_data["event_status"] = EventStatus.CANCELLED
    valid_refund_data["has_checked_in_tickets"] = True  # tidak dicek
    valid_refund_data["refund_deadline"] = now - timedelta(days=1)  # sudah lewat

    refund = Refund.request(**valid_refund_data)

    assert refund.status == RefundStatus.REQUESTED


def test_request_refund_before_deadline(valid_refund_data, now):
    """Refund berhasil jika masih dalam refund deadline."""
    valid_refund_data["refund_deadline"] = now + timedelta(hours=1)

    refund = Refund.request(**valid_refund_data)

    assert refund.status == RefundStatus.REQUESTED


# Unhappy Path 

def test_request_refund_fails_when_booking_not_paid(valid_refund_data):
    """Refund hanya bisa diminta untuk booking berstatus PAID."""
    for status in [BookingStatus.PENDING_PAYMENT,
                   BookingStatus.EXPIRED,
                   BookingStatus.REFUNDED]:
        valid_refund_data["booking_status"] = status

        with pytest.raises(DomainException) as exc_info:
            Refund.request(**valid_refund_data)

        assert "paid booking" in str(exc_info.value).lower()


def test_request_refund_fails_when_ticket_checked_in(valid_refund_data):
    """Refund tidak bisa diminta jika ada tiket yang sudah CHECKED_IN."""
    valid_refund_data["has_checked_in_tickets"] = True

    with pytest.raises(DomainException) as exc_info:
        Refund.request(**valid_refund_data)

    assert "checked in" in str(exc_info.value).lower()


def test_request_refund_fails_when_deadline_passed(valid_refund_data, now):
    """Refund tidak bisa diminta jika refund deadline sudah lewat."""
    valid_refund_data["refund_deadline"] = now - timedelta(days=1)

    with pytest.raises(DomainException) as exc_info:
        Refund.request(**valid_refund_data)

    assert "deadline" in str(exc_info.value).lower()


def test_request_refund_checked_in_not_checked_when_event_cancelled(
    valid_refund_data, now
):
    """Jika event CANCELLED, checked-in tickets tidak menghalangi refund."""
    valid_refund_data["event_status"] = EventStatus.CANCELLED
    valid_refund_data["has_checked_in_tickets"] = True

    refund = Refund.request(**valid_refund_data)

    assert refund.status == RefundStatus.REQUESTED