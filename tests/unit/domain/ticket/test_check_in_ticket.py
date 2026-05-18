import pytest
from datetime import datetime, timedelta

from src.domain.booking.value_objects.booking_id import BookingId
from src.domain.booking.value_objects.customer_id import CustomerId
from src.domain.event.value_objects.event_id import EventId
from src.domain.event.value_objects.ticket_category_id import TicketCategoryId
from src.domain.ticket.domain_events.ticket_checked_in import TicketCheckedIn
from src.domain.ticket.entities.ticket import Ticket
from src.domain.ticket.value_objects.ticket_status import TicketStatus
from src.domain.shared.exceptions.domain_exception import DomainException


# Fixtures 

@pytest.fixture
def event_id():
    return EventId.generate()


@pytest.fixture
def active_ticket(event_id):
    """Ticket dengan status ACTIVE yang siap untuk check-in."""
    return Ticket.create(
        booking_id=BookingId.generate(),
        customer_id=CustomerId.generate(),
        event_id=event_id,
        ticket_category_id=TicketCategoryId.generate(),
    )


@pytest.fixture
def check_in_time():
    """Waktu check-in yang valid yaitu hari ini."""
    return datetime.utcnow()


# Happy Path 

def test_check_in_ticket_success(active_ticket, event_id, check_in_time):
    """Tiket berhasil di-check-in dengan data yang valid."""
    active_ticket.check_in(event_id=event_id, check_in_time=check_in_time)

    assert active_ticket.status == TicketStatus.CHECKED_IN


def test_check_in_ticket_raises_domain_event(active_ticket, event_id, check_in_time):
    """Sistem harus raise domain event TicketCheckedIn setelah check-in berhasil."""
    active_ticket.check_in(event_id=event_id, check_in_time=check_in_time)
    domain_events = active_ticket.pull_domain_events()

    assert len(domain_events) == 1
    assert isinstance(domain_events[0], TicketCheckedIn)
    assert domain_events[0].ticket_id == active_ticket.id
    assert domain_events[0].event_id == event_id


def test_pull_domain_events_clears_after_pull(active_ticket, event_id, check_in_time):
    """Domain events harus terhapus setelah di-pull."""
    active_ticket.check_in(event_id=event_id, check_in_time=check_in_time)
    active_ticket.pull_domain_events()

    remaining = active_ticket.pull_domain_events()
    assert len(remaining) == 0


# Unhappy Path 

def test_check_in_fails_when_ticket_already_checked_in(active_ticket, event_id, check_in_time):
    """Tiket yang sudah CHECKED_IN tidak bisa di-check-in lagi."""
    active_ticket.check_in(event_id=event_id, check_in_time=check_in_time)
    active_ticket.pull_domain_events()

    with pytest.raises(DomainException) as exc_info:
        active_ticket.check_in(event_id=event_id, check_in_time=check_in_time)

    assert "already been checked in" in str(exc_info.value).lower()


def test_check_in_fails_when_ticket_is_cancelled(event_id, check_in_time):
    """Tiket berstatus CANCELLED tidak bisa di-check-in."""
    ticket = Ticket.create(
        booking_id=BookingId.generate(),
        customer_id=CustomerId.generate(),
        event_id=event_id,
        ticket_category_id=TicketCategoryId.generate(),
    )
    ticket.cancel()

    with pytest.raises(DomainException) as exc_info:
        ticket.check_in(event_id=event_id, check_in_time=check_in_time)

    assert "cancelled" in str(exc_info.value).lower()


def test_check_in_fails_when_event_id_does_not_match(active_ticket, check_in_time):
    """Tiket tidak bisa di-check-in jika event_id tidak sesuai."""
    different_event_id = EventId.generate()

    with pytest.raises(DomainException) as exc_info:
        active_ticket.check_in(
            event_id=different_event_id,
            check_in_time=check_in_time,
        )

    assert "does not match" in str(exc_info.value).lower()


def test_check_in_status_unchanged_when_failed(active_ticket, check_in_time):
    """Status tiket tidak boleh berubah jika check-in gagal."""
    different_event_id = EventId.generate()

    with pytest.raises(DomainException):
        active_ticket.check_in(
            event_id=different_event_id,
            check_in_time=check_in_time,
        )

    assert active_ticket.status == TicketStatus.ACTIVE