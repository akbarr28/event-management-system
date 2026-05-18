import pytest
from datetime import datetime

from src.domain.booking.value_objects.booking_id import BookingId
from src.domain.booking.value_objects.customer_id import CustomerId
from src.domain.event.value_objects.event_id import EventId
from src.domain.event.value_objects.event_status import EventStatus
from src.domain.event.value_objects.ticket_category_id import TicketCategoryId
from src.domain.ticket.domain_events.ticket_checked_in import TicketCheckedIn
from src.domain.ticket.entities.ticket import Ticket
from src.domain.ticket.value_objects.ticket_status import TicketStatus
from src.domain.shared.exceptions.domain_exception import DomainException


# ── Fixtures ──────────────────────────────────────────────────────────────────

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


# ── Happy Path ────────────────────────────────────────────────────────────────

def test_check_in_ticket_success(active_ticket, event_id, check_in_time):
    active_ticket.check_in(
        event_id=event_id,
        event_status=EventStatus.PUBLISHED,
        check_in_time=check_in_time,
    )
    assert active_ticket.status == TicketStatus.CHECKED_IN


def test_check_in_ticket_raises_domain_event(active_ticket, event_id, check_in_time):
    active_ticket.check_in(
        event_id=event_id,
        event_status=EventStatus.PUBLISHED,
        check_in_time=check_in_time,
    )
    domain_events = active_ticket.pull_domain_events()

    assert len(domain_events) == 1
    assert isinstance(domain_events[0], TicketCheckedIn)
    assert domain_events[0].ticket_id == active_ticket.id
    assert domain_events[0].event_id == event_id


def test_pull_domain_events_clears_after_pull(active_ticket, event_id, check_in_time):
    active_ticket.check_in(
        event_id=event_id,
        event_status=EventStatus.PUBLISHED,
        check_in_time=check_in_time,
    )
    active_ticket.pull_domain_events()
    assert len(active_ticket.pull_domain_events()) == 0


# ── Unhappy Path ──────────────────────────────────────────────────────────────

def test_check_in_fails_when_already_checked_in(active_ticket, event_id, check_in_time):
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


def test_check_in_fails_when_cancelled(event_id, check_in_time):
    ticket = Ticket.create(
        booking_id=BookingId.generate(),
        customer_id=CustomerId.generate(),
        event_id=event_id,
        ticket_category_id=TicketCategoryId.generate(),
    )
    ticket.cancel()
    with pytest.raises(DomainException) as exc_info:
        ticket.check_in(
            event_id=event_id,
            event_status=EventStatus.PUBLISHED,
            check_in_time=check_in_time,
        )
    assert "cancelled" in str(exc_info.value).lower()


def test_check_in_fails_when_event_id_mismatch(active_ticket, check_in_time):
    with pytest.raises(DomainException) as exc_info:
        active_ticket.check_in(
            event_id=EventId.generate(),
            event_status=EventStatus.PUBLISHED,
            check_in_time=check_in_time,
        )
    assert "does not match" in str(exc_info.value).lower()


def test_check_in_status_unchanged_when_failed(active_ticket, check_in_time):
    with pytest.raises(DomainException):
        active_ticket.check_in(
            event_id=EventId.generate(),
            event_status=EventStatus.PUBLISHED,
            check_in_time=check_in_time,
        )
    assert active_ticket.status == TicketStatus.ACTIVE