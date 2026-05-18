"""
Unit Tests — User Story 12: View Purchased Tickets

Business Rules yang diuji:
- BR-T12-01: Ticket hanya bisa dilihat dari booking yang Paid
- BR-T12-02: Setiap ticket memiliki unique ticket code
- BR-T12-03: Status awal ticket adalah Active
- BR-T12-04: Jumlah ticket yang diterbitkan sesuai dengan quantity booking
- BR-T12-05: Ticket dari event cancelled berstatus Cancelled
"""

import pytest
from datetime import datetime
from decimal import Decimal

from src.domain.booking.aggregates.booking import Booking
from src.domain.booking.value_objects.booking_status import BookingStatus
from src.domain.booking.value_objects.customer_id import CustomerId
from src.domain.event.value_objects.event_id import EventId
from src.domain.event.value_objects.ticket_category_id import TicketCategoryId
from src.domain.shared.exceptions.domain_exception import DomainException
from src.domain.shared.value_objects.money import Money
from src.domain.ticket.entities.ticket import Ticket
from src.domain.ticket.value_objects.ticket_status import TicketStatus



@pytest.fixture
def now():
    return datetime.utcnow()


@pytest.fixture
def unit_price():
    return Money(amount=Decimal("100000"), currency="IDR")


@pytest.fixture
def paid_booking(unit_price, now):
    booking = Booking.create(
        customer_id=CustomerId.generate(),
        event_id=EventId.generate(),
        ticket_category_id=TicketCategoryId.generate(),
        quantity=2,
        unit_price=unit_price,
        now=now,
    )
    booking.pay(payment_amount=booking.total_price, now=now)
    return booking


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


class TestTicketInitialStatus:

    def test_newly_issued_ticket_has_active_status(self, paid_booking):
        """BR-T12-03: Ticket baru harus berstatus Active."""
        tickets = paid_booking.issue_tickets()

        for ticket in tickets:
            assert ticket.status == TicketStatus.ACTIVE



class TestTicketUniqueCode:

    def test_each_ticket_has_a_ticket_code(self, paid_booking):
        """BR-T12-02: Setiap ticket harus punya ticket code."""
        tickets = paid_booking.issue_tickets()

        for ticket in tickets:
            assert ticket.ticket_code is not None
            assert str(ticket.ticket_code) != ""

    def test_ticket_codes_are_unique(self, paid_booking):
        """BR-T12-02: Semua ticket code harus berbeda."""
        tickets = paid_booking.issue_tickets()
        codes = [str(t.ticket_code) for t in tickets]

        assert len(codes) == len(set(codes))

    def test_tickets_from_different_bookings_have_different_codes(
        self, unit_price, now
    ):
        """BR-T12-02: Ticket dari booking berbeda juga harus punya code unik."""
        booking1 = Booking.create(
            customer_id=CustomerId.generate(),
            event_id=EventId.generate(),
            ticket_category_id=TicketCategoryId.generate(),
            quantity=1,
            unit_price=unit_price,
            now=now,
        )
        booking1.pay(payment_amount=booking1.total_price, now=now)

        booking2 = Booking.create(
            customer_id=CustomerId.generate(),
            event_id=EventId.generate(),
            ticket_category_id=TicketCategoryId.generate(),
            quantity=1,
            unit_price=unit_price,
            now=now,
        )
        booking2.pay(payment_amount=booking2.total_price, now=now)

        tickets1 = booking1.issue_tickets()
        tickets2 = booking2.issue_tickets()

        code1 = str(tickets1[0].ticket_code)
        code2 = str(tickets2[0].ticket_code)

        assert code1 != code2



class TestTicketQuantity:

    def test_number_of_tickets_matches_booking_quantity(self, paid_booking):
        """BR-T12-04: Jumlah ticket harus sama dengan quantity booking."""
        tickets = paid_booking.issue_tickets()

        assert len(tickets) == paid_booking.quantity

    def test_single_ticket_for_quantity_one(self, unit_price, now):
        """BR-T12-04: Quantity 1 menghasilkan 1 ticket."""
        booking = Booking.create(
            customer_id=CustomerId.generate(),
            event_id=EventId.generate(),
            ticket_category_id=TicketCategoryId.generate(),
            quantity=1,
            unit_price=unit_price,
            now=now,
        )
        booking.pay(payment_amount=booking.total_price, now=now)

        tickets = booking.issue_tickets()

        assert len(tickets) == 1


class TestOnlyPaidBookingCanIssueTickets:

    def test_pending_booking_cannot_issue_tickets(self, pending_booking):
        """BR-T12-01: Booking PendingPayment tidak bisa issue tickets."""
        with pytest.raises(DomainException):
            pending_booking.issue_tickets()

    def test_expired_booking_cannot_issue_tickets(self, unit_price, now):
        """BR-T12-01: Booking Expired tidak bisa issue tickets."""
        from datetime import timedelta
        booking = Booking.create(
            customer_id=CustomerId.generate(),
            event_id=EventId.generate(),
            ticket_category_id=TicketCategoryId.generate(),
            quantity=1,
            unit_price=unit_price,
            now=now,
        )
        after_deadline = booking.payment_deadline + timedelta(seconds=1)
        booking.expire(now=after_deadline)

        with pytest.raises(DomainException):
            booking.issue_tickets()


class TestTicketCancelledStatus:

    def test_ticket_can_be_cancelled(self, paid_booking):
        """BR-T12-05: Ticket bisa di-cancel, misalnya saat event dibatalkan."""
        tickets = paid_booking.issue_tickets()
        ticket = tickets[0]

        ticket.cancel()

        assert ticket.status == TicketStatus.CANCELLED

    def test_checked_in_ticket_cannot_be_cancelled(self, paid_booking):
        """BR-T12-05: Ticket yang sudah CheckedIn tidak bisa di-cancel."""
        tickets = paid_booking.issue_tickets()
        ticket = tickets[0]
        ticket.status = TicketStatus.CHECKED_IN

        with pytest.raises(DomainException):
            ticket.cancel()