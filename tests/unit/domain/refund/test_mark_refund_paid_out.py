import pytest
from datetime import datetime, timedelta
from decimal import Decimal

from src.domain.booking.value_objects.booking_id import BookingId
from src.domain.booking.value_objects.booking_status import BookingStatus
from src.domain.booking.value_objects.customer_id import CustomerId
from src.domain.event.value_objects.event_status import EventStatus
from src.domain.refund.aggregates.refund import Refund
from src.domain.refund.domain_events.refund_paid_out import RefundPaidOut
from src.domain.refund.value_objects.refund_status import RefundStatus
from src.domain.shared.exceptions.domain_exception import DomainException
from src.domain.shared.value_objects.money import Money


#─ Fixtures 

@pytest.fixture
def now():
    return datetime.utcnow()


@pytest.fixture
def approved_refund(now):
    """Refund yang sudah berstatus APPROVED."""
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
    refund.approve()
    refund.pull_domain_events()
    return refund


# Happy Path

def test_mark_paid_out_success(approved_refund):
    """Refund berhasil ditandai sebagai PAID_OUT."""
    approved_refund.mark_paid_out("TRX-20250101-ABC123")

    assert approved_refund.status == RefundStatus.PAID_OUT


def test_mark_paid_out_stores_payment_reference(approved_refund):
    """Payment reference tersimpan di aggregate."""
    reference = "TRX-20250101-ABC123"
    approved_refund.mark_paid_out(reference)

    assert approved_refund.payment_reference == reference


def test_mark_paid_out_raises_domain_event(approved_refund):
    """Sistem harus raise domain event RefundPaidOut."""
    reference = "TRX-20250101-ABC123"
    approved_refund.mark_paid_out(reference)
    domain_events = approved_refund.pull_domain_events()

    assert len(domain_events) == 1
    assert isinstance(domain_events[0], RefundPaidOut)
    assert domain_events[0].refund_id == approved_refund.id
    assert domain_events[0].booking_id == approved_refund.booking_id
    assert domain_events[0].payment_reference == reference


def test_mark_paid_out_does_not_change_amount(approved_refund):
    """Amount refund tidak berubah setelah paid out."""
    original_amount = approved_refund.amount
    approved_refund.mark_paid_out("TRX-20250101-ABC123")

    assert approved_refund.amount == original_amount


def test_mark_paid_out_rejection_reason_remains_none(approved_refund):
    """Paid out tidak mengisi rejection reason."""
    approved_refund.mark_paid_out("TRX-20250101-ABC123")

    assert approved_refund.rejection_reason is None


# Unhappy Path 

def test_mark_paid_out_fails_when_requested(now):
    """Refund berstatus REQUESTED tidak bisa di-paid out."""
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

    with pytest.raises(DomainException) as exc_info:
        refund.mark_paid_out("TRX-20250101-ABC123")

    assert "approved" in str(exc_info.value).lower()


def test_mark_paid_out_fails_when_rejected(approved_refund):
    """Refund berstatus REJECTED tidak bisa di-paid out."""
    approved_refund.status = RefundStatus.REJECTED

    with pytest.raises(DomainException) as exc_info:
        approved_refund.mark_paid_out("TRX-20250101-ABC123")

    assert "approved" in str(exc_info.value).lower()


def test_mark_paid_out_fails_when_already_paid_out(approved_refund):
    """Refund yang sudah PAID_OUT tidak bisa di-paid out lagi."""
    approved_refund.mark_paid_out("TRX-PERTAMA-001")
    approved_refund.pull_domain_events()

    with pytest.raises(DomainException) as exc_info:
        approved_refund.mark_paid_out("TRX-KEDUA-002")

    assert "approved" in str(exc_info.value).lower()


def test_mark_paid_out_fails_when_reference_is_empty(approved_refund):
    """Payment reference tidak boleh kosong."""
    with pytest.raises(DomainException) as exc_info:
        approved_refund.mark_paid_out("")

    assert "payment reference" in str(exc_info.value).lower()


def test_mark_paid_out_fails_when_reference_is_whitespace(approved_refund):
    """Payment reference tidak boleh hanya spasi."""
    with pytest.raises(DomainException) as exc_info:
        approved_refund.mark_paid_out("   ")

    assert "payment reference" in str(exc_info.value).lower()


def test_paid_out_cannot_be_approved_again(approved_refund):
    """Refund yang sudah PAID_OUT tidak bisa di-approve lagi."""
    approved_refund.mark_paid_out("TRX-20250101-ABC123")

    with pytest.raises(DomainException) as exc_info:
        approved_refund.approve()

    assert "requested" in str(exc_info.value).lower()


def test_paid_out_cannot_be_rejected(approved_refund):
    """Refund yang sudah PAID_OUT tidak bisa di-reject."""
    approved_refund.mark_paid_out("TRX-20250101-ABC123")

    with pytest.raises(DomainException) as exc_info:
        approved_refund.reject("Alasan penolakan.")

    assert "requested" in str(exc_info.value).lower()