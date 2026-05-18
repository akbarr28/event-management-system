"""
Unit Tests — User Story 09: Calculate Booking Total Price

Business Rules yang diuji:
- BR-B09-01: Total price = unit price x quantity
- BR-B09-02: Jika ada service fee, ditambahkan ke total
- BR-B09-03: Total price tidak boleh negatif
- BR-B09-04: Total price direpresentasikan dengan value object Money
"""

import pytest
from datetime import datetime
from decimal import Decimal

from src.domain.booking.aggregates.booking import Booking
from src.domain.booking.value_objects.customer_id import CustomerId
from src.domain.event.value_objects.event_id import EventId
from src.domain.event.value_objects.ticket_category_id import TicketCategoryId
from src.domain.shared.value_objects.money import Money


@pytest.fixture
def now():
    return datetime.utcnow()


def make_booking(quantity, unit_price_amount, now):
    return Booking.create(
        customer_id=CustomerId.generate(),
        event_id=EventId.generate(),
        ticket_category_id=TicketCategoryId.generate(),
        quantity=quantity,
        unit_price=Money(amount=Decimal(str(unit_price_amount)), currency="IDR"),
        now=now,
    )


class TestCalculateTotalPriceWithoutServiceFee:

    def test_total_price_is_unit_price_times_quantity(self, now):
        """BR-B09-01: 100000 x 3 = 300000."""
        booking = make_booking(quantity=3, unit_price_amount=100000, now=now)

        total = booking.calculate_total_price()

        assert total == Money(amount=Decimal("300000"), currency="IDR")

    def test_total_price_for_quantity_one(self, now):
        """BR-B09-01: Quantity 1, total sama dengan unit price."""
        booking = make_booking(quantity=1, unit_price_amount=150000, now=now)

        total = booking.calculate_total_price()

        assert total == Money(amount=Decimal("150000"), currency="IDR")

    def test_total_price_for_free_ticket(self, now):
        """BR-B09-01: Free ticket (harga 0), total tetap 0."""
        booking = make_booking(quantity=5, unit_price_amount=0, now=now)

        total = booking.calculate_total_price()

        assert total == Money(amount=Decimal("0"), currency="IDR")

    def test_total_price_returns_money_value_object(self, now):
        """BR-B09-04: Return type harus Money."""
        booking = make_booking(quantity=2, unit_price_amount=100000, now=now)

        total = booking.calculate_total_price()

        assert isinstance(total, Money)


class TestCalculateTotalPriceWithServiceFee:

    def test_service_fee_is_added_to_total(self, now):
        """BR-B09-02: Total = (unit price x quantity) + service fee."""
        booking = make_booking(quantity=2, unit_price_amount=100000, now=now)
        service_fee = Money(amount=Decimal("10000"), currency="IDR")

        total = booking.calculate_total_price(service_fee=service_fee)

        assert total == Money(amount=Decimal("210000"), currency="IDR")

    def test_service_fee_zero_does_not_change_total(self, now):
        """BR-B09-02: Service fee 0 tidak mengubah total."""
        booking = make_booking(quantity=2, unit_price_amount=100000, now=now)
        service_fee = Money(amount=Decimal("0"), currency="IDR")

        total = booking.calculate_total_price(service_fee=service_fee)

        assert total == Money(amount=Decimal("200000"), currency="IDR")

    def test_without_service_fee_returns_base_total(self, now):
        """BR-B09-02: Tanpa service fee, total sama dengan unit price x quantity."""
        booking = make_booking(quantity=2, unit_price_amount=100000, now=now)

        total = booking.calculate_total_price()

        assert total == Money(amount=Decimal("200000"), currency="IDR")

    def test_service_fee_with_quantity_one(self, now):
        """BR-B09-02: Service fee ditambahkan meski quantity 1."""
        booking = make_booking(quantity=1, unit_price_amount=100000, now=now)
        service_fee = Money(amount=Decimal("5000"), currency="IDR")

        total = booking.calculate_total_price(service_fee=service_fee)

        assert total == Money(amount=Decimal("105000"), currency="IDR")


class TestTotalPriceCannotBeNegative:

    def test_total_price_is_never_negative_for_valid_inputs(self, now):
        """BR-B09-03: Total price valid tidak boleh negatif."""
        booking = make_booking(quantity=1, unit_price_amount=100000, now=now)

        total = booking.calculate_total_price()

        assert total.amount >= Decimal("0")

    def test_total_price_zero_is_valid(self, now):
        """BR-B09-03: Total price 0 diperbolehkan untuk free event."""
        booking = make_booking(quantity=1, unit_price_amount=0, now=now)

        total = booking.calculate_total_price()

        assert total.amount == Decimal("0")