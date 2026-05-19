import pytest

from src.domain.booking.value_objects.booking_id import BookingId
from src.domain.booking.value_objects.customer_id import CustomerId
from src.domain.event.value_objects.event_id import EventId
from src.domain.event.value_objects.ticket_category_id import TicketCategoryId
from src.domain.refund.domain_services.refund_domain_service import RefundDomainService
from src.domain.shared.exceptions.domain_exception import DomainException
from src.domain.ticket.entities.ticket import Ticket
from src.domain.ticket.value_objects.ticket_status import TicketStatus


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
def checked_in_ticket(event_id):
    from src.domain.event.value_objects.event_status import EventStatus
    from datetime import datetime

    ticket = Ticket.create(
        booking_id=BookingId.generate(),
        customer_id=CustomerId.generate(),
        event_id=event_id,
        ticket_category_id=TicketCategoryId.generate(),
    )
    ticket.check_in(
        event_id=event_id,
        event_status=EventStatus.PUBLISHED,
        check_in_time=datetime.utcnow(),
    )
    return ticket


@pytest.fixture
def cancelled_ticket(event_id):
    ticket = Ticket.create(
        booking_id=BookingId.generate(),
        customer_id=CustomerId.generate(),
        event_id=event_id,
        ticket_category_id=TicketCategoryId.generate(),
    )
    ticket.cancel()
    return ticket


# has_checked_in_tickets 

def test_returns_false_when_no_tickets():
    """Tidak ada tiket → tidak ada yang checked-in."""
    result = RefundDomainService.has_checked_in_tickets([])

    assert result is False


def test_returns_false_when_all_tickets_active(active_ticket):
    """Semua tiket ACTIVE → tidak ada yang checked-in."""
    result = RefundDomainService.has_checked_in_tickets([active_ticket])

    assert result is False


def test_returns_false_when_all_tickets_cancelled(cancelled_ticket):
    """Semua tiket CANCELLED → tidak ada yang checked-in."""
    result = RefundDomainService.has_checked_in_tickets([cancelled_ticket])

    assert result is False


def test_returns_true_when_one_ticket_checked_in(
    active_ticket, checked_in_ticket
):
    """Ada satu tiket CHECKED_IN → return True."""
    result = RefundDomainService.has_checked_in_tickets(
        [active_ticket, checked_in_ticket]
    )

    assert result is True


def test_returns_true_when_all_tickets_checked_in(checked_in_ticket):
    """Semua tiket CHECKED_IN → return True."""
    result = RefundDomainService.has_checked_in_tickets([checked_in_ticket])

    assert result is True


# validate_no_checked_in_tickets 

def test_validate_passes_when_no_checked_in_tickets(active_ticket):
    """Validasi lolos jika tidak ada tiket CHECKED_IN."""
    RefundDomainService.validate_no_checked_in_tickets([active_ticket])


def test_validate_passes_with_empty_list():
    """Validasi lolos jika list tiket kosong."""
    RefundDomainService.validate_no_checked_in_tickets([])


def test_validate_fails_when_checked_in_ticket_exists(
    active_ticket, checked_in_ticket
):
    """Validasi gagal jika ada tiket CHECKED_IN."""
    with pytest.raises(DomainException) as exc_info:
        RefundDomainService.validate_no_checked_in_tickets(
            [active_ticket, checked_in_ticket]
        )

    assert "checked in" in str(exc_info.value).lower()