import pytest
from datetime import datetime, timedelta
from decimal import Decimal

from src.domain.booking.value_objects.booking_id import BookingId
from src.domain.booking.value_objects.booking_status import BookingStatus
from src.domain.booking.value_objects.customer_id import CustomerId
from src.domain.event.value_objects.event_status import EventStatus
from src.domain.refund.aggregates.refund import Refund
from src.domain.refund.domain_events.refund_rejected import RefundRejected
from src.domain.refund.value_objects.refund_status import RefundStatus
from src.domain.shared.exceptions.domain_exception import DomainException
from src.domain.shared.value_objects.money import Money


# Fixtures 

@pytest.fixture
def now():
    return datetime.utcnow()


@pytest.fixture
def requested_refund(now):
    """Refund yang sudah berstatus REQUESTED."""
    refund = Refund.request(
        booking_id=BookingId.generate(),
        customer_id=CustomerId.generate(),
        amount=Money(Decimal("150000"), "IDR"),
        booking_status=BookingStatus.PAID,
        event_status=EventStatus.PUBLISHED,
        has_checked_in_tickets=False,
        refund_deadline=now + timedelta(days=7),
        now=now,
    )
    refund.pull_domain_events()
    return refund


# Happy Path 

def test_reject_refund_success(requested_refund):
    """Refund berhasil ditolak dengan alasan yang valid."""
    requested_refund.reject("Tiket sudah digunakan sebelum event dibatalkan.")

    assert requested_refund.status == RefundStatus.REJECTED


def test_reject_refund_stores_rejection_reason(requested_refund):
    """Alasan penolakan tersimpan di aggregate."""
    reason = "Refund tidak sesuai kebijakan pengembalian."
    requested_refund.reject(reason)

    assert requested_refund.rejection_reason == reason


def test_reject_refund_raises_domain_event(requested_refund):
    """Sistem harus raise domain event RefundRejected."""
    reason = "Permintaan refund tidak valid."
    requested_refund.reject(reason)
    domain_events = requested_refund.pull_domain_events()

    assert len(domain_events) == 1
    assert isinstance(domain_events[0], RefundRejected)
    assert domain_events[0].refund_id == requested_refund.id
    assert domain_events[0].booking_id == requested_refund.booking_id
    assert domain_events[0].rejection_reason == reason


def test_reject_refund_does_not_change_amount(requested_refund):
    """Amount refund tidak berubah setelah ditolak."""
    original_amount = requested_refund.amount
    requested_refund.reject("Alasan penolakan.")

    assert requested_refund.amount == original_amount


def test_reject_refund_payment_reference_remains_none(requested_refund):
    """Reject tidak mengisi payment reference."""
    requested_refund.reject("Alasan penolakan.")

    assert requested_refund.payment_reference is None


# Unhappy Path 

def test_reject_refund_fails_when_already_rejected(requested_refund):
    """Refund yang sudah REJECTED tidak bisa ditolak lagi."""
    requested_refund.reject("Alasan pertama.")
    requested_refund.pull_domain_events()

    with pytest.raises(DomainException) as exc_info:
        requested_refund.reject("Alasan kedua.")

    assert "requested" in str(exc_info.value).lower()


def test_reject_refund_fails_when_approved(requested_refund):
    """Refund yang sudah APPROVED tidak bisa ditolak."""
    requested_refund.status = RefundStatus.APPROVED

    with pytest.raises(DomainException) as exc_info:
        requested_refund.reject("Alasan penolakan.")

    assert "requested" in str(exc_info.value).lower()


def test_reject_refund_fails_when_paid_out(requested_refund):
    """Refund yang sudah PAID_OUT tidak bisa ditolak."""
    requested_refund.status = RefundStatus.PAID_OUT

    with pytest.raises(DomainException) as exc_info:
        requested_refund.reject("Alasan penolakan.")

    assert "requested" in str(exc_info.value).lower()


def test_reject_refund_fails_when_reason_is_empty(requested_refund):
    """Alasan penolakan tidak boleh kosong."""
    with pytest.raises(DomainException) as exc_info:
        requested_refund.reject("")

    assert "rejection reason" in str(exc_info.value).lower()


def test_reject_refund_fails_when_reason_is_whitespace(requested_refund):
    """Alasan penolakan tidak boleh hanya spasi."""
    with pytest.raises(DomainException) as exc_info:
        requested_refund.reject("   ")

    assert "rejection reason" in str(exc_info.value).lower()