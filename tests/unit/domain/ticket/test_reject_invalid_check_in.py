import pytest
from datetime import datetime

from src.domain.booking.value_objects.booking_id import BookingId
from src.domain.booking.value_objects.customer_id import CustomerId
from src.domain.event.value_objects.event_id import EventId
from src.domain.event.value_objects.event_status import EventStatus
from src.domain.event.value_objects.ticket_category_id import TicketCategoryId
from src.domain.ticket.entities.ticket import Ticket
from src.domain.ticket.value_objects.ticket_status import TicketStatus
from src.domain.shared.exceptions.domain_exception import DomainException


# Fixtures 

@pytest.fixture
def event_id():
    return EventId.generate()


@pytest.fixture
def active_ticket(event_id):
    return Ticket.create(
        booking_id=BookingId.generate(),
        customer_id=CustomerId.generate(),
        event_id=event_id,
        ticket_category_id=TicketCategoryId.generate(),
    )


@pytest.fixture
def check_in_time():
    return datetime.utcnow()


# US-14: Rejection Scenarios 

def test_reject_when_ticket_code_not_found():
    """BR-T14: Kode tiket tidak ditemukan → tiket tidak valid."""
    with pytest.raises(DomainException) as exc_info:
        Ticket.validate_code_exists(None)

    assert "not found" in str(exc_info.value).lower()


def test_reject_when_ticket_code_found_returns_ticket(active_ticket):
    """validate_code_exists() mengembalikan tiket jika ditemukan."""
    result = Ticket.validate_code_exists(active_ticket)

    assert result == active_ticket


def test_reject_when_ticket_already_checked_in(active_ticket, event_id, check_in_time):
    """BR-T14: Tiket sudah di-check-in → tiket sudah digunakan."""
    active_ticket.check_in(
        event_id=event_id,
        event_status=EventStatus.PUBLISHED,
        check_in_time=check_in_time,
    )

    with pytest.raises(DomainException) as exc_info:
        active_ticket.check_in(
            event_id=event_id,
            event_status=EventStatus.PUBLISHED,
            check_in_time=check_in_time,
        )

    assert "already been checked in" in str(exc_info.value).lower()


def test_reject_when_ticket_belongs_to_different_event(active_ticket, check_in_time):
    """BR-T14: Tiket milik event lain → tiket tidak sesuai event."""
    different_event_id = EventId.generate()

    with pytest.raises(DomainException) as exc_info:
        active_ticket.check_in(
            event_id=different_event_id,
            event_status=EventStatus.PUBLISHED,
            check_in_time=check_in_time,
        )

    assert "does not match" in str(exc_info.value).lower()


def test_reject_when_event_is_cancelled(active_ticket, event_id, check_in_time):
    """BR-T14: Event sudah dibatalkan → event telah dibatalkan."""
    with pytest.raises(DomainException) as exc_info:
        active_ticket.check_in(
            event_id=event_id,
            event_status=EventStatus.CANCELLED,
            check_in_time=check_in_time,
        )

    assert "cancelled" in str(exc_info.value).lower()


def test_reject_does_not_change_ticket_status(active_ticket, check_in_time):
    """BR-T14: Status tiket tidak boleh berubah jika check-in gagal."""
    original_status = active_ticket.status

    # Gagal karena event cancelled
    with pytest.raises(DomainException):
        active_ticket.check_in(
            event_id=active_ticket.event_id,
            event_status=EventStatus.CANCELLED,
            check_in_time=check_in_time,
        )

    assert active_ticket.status == original_status


def test_reject_does_not_change_status_on_event_mismatch(active_ticket, check_in_time):
    """BR-T14: Status tiket tidak berubah jika event tidak sesuai."""
    with pytest.raises(DomainException):
        active_ticket.check_in(
            event_id=EventId.generate(),
            event_status=EventStatus.PUBLISHED,
            check_in_time=check_in_time,
        )

    assert active_ticket.status == TicketStatus.ACTIVE