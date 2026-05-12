import pytest
from datetime import datetime, timedelta
from decimal import Decimal

from src.domain.event.aggregates.event import Event
from src.domain.event.value_objects.event_status import EventStatus
from src.domain.event.value_objects.organizer_id import OrganizerId
from src.domain.shared.value_objects.money import Money


@pytest.fixture
def organizer_id():
    return OrganizerId.generate()


@pytest.fixture
def future_dates():
    now = datetime.utcnow()
    return {
        "start_date": now + timedelta(days=10),
        "end_date": now + timedelta(days=11),
    }


@pytest.fixture
def draft_event(organizer_id, future_dates):
    return Event.create(
        name="Draft Event",
        description="Belum dipublish.",
        start_date=future_dates["start_date"],
        end_date=future_dates["end_date"],
        location="Surabaya",
        maximum_capacity=100,
        organizer_id=organizer_id,
    )


@pytest.fixture
def published_event(organizer_id, future_dates):
    event = Event.create(
        name="ITS Tech Fest 2025",
        description="Annual tech festival.",
        start_date=future_dates["start_date"],
        end_date=future_dates["end_date"],
        location="Surabaya, ITS Campus",
        maximum_capacity=500,
        organizer_id=organizer_id,
    )
    sales_start = future_dates["start_date"] - timedelta(days=7)
    sales_end = future_dates["start_date"] - timedelta(days=1)
    event.add_ticket_category(
        name="Regular",
        price=Money(amount=Decimal("100000"), currency="IDR"),
        quota=200,
        sales_start_date=sales_start,
        sales_end_date=sales_end,
    )
    event.add_ticket_category(
        name="VIP",
        price=Money(amount=Decimal("300000"), currency="IDR"),
        quota=100,
        sales_start_date=sales_start,
        sales_end_date=sales_end,
    )
    event.publish()
    event.pull_domain_events()
    return event


@pytest.fixture
def cancelled_event(organizer_id, future_dates):
    event = Event.create(
        name="Cancelled Event",
        description="Event ini dibatalkan.",
        start_date=future_dates["start_date"],
        end_date=future_dates["end_date"],
        location="Jakarta",
        maximum_capacity=100,
        organizer_id=organizer_id,
    )
    sales_start = future_dates["start_date"] - timedelta(days=7)
    sales_end = future_dates["start_date"] - timedelta(days=1)
    event.add_ticket_category(
        name="Regular",
        price=Money(amount=Decimal("50000"), currency="IDR"),
        quota=100,
        sales_start_date=sales_start,
        sales_end_date=sales_end,
    )
    event.publish()
    event.cancel()
    event.pull_domain_events()
    return event

class TestEventAvailabilityForBrowsing:

    def test_published_event_is_available_for_browsing(self, published_event):
        """BR-E06-01: Event PUBLISHED harus tersedia untuk dilihat customer."""
        assert published_event.is_available_for_browsing() is True

    def test_draft_event_is_not_available_for_browsing(self, draft_event):
        """BR-E06-03: Event DRAFT tidak boleh ditampilkan ke customer."""
        assert draft_event.is_available_for_browsing() is False

    def test_cancelled_event_is_not_available_for_browsing(self, cancelled_event):
        """BR-E06-02: Event CANCELLED tidak boleh ditampilkan ke customer."""
        assert cancelled_event.is_available_for_browsing() is False

    def test_browsing_filter_returns_only_published(self, draft_event, published_event, cancelled_event):
        """Simulasi filter list — hanya PUBLISHED yang lolos."""
        all_events = [draft_event, published_event, cancelled_event]
        available = [e for e in all_events if e.is_available_for_browsing()]

        assert len(available) == 1
        assert available[0].status == EventStatus.PUBLISHED
        assert available[0].name == "ITS Tech Fest 2025"


class TestLowestTicketPrice:

    def test_lowest_price_returns_cheapest_active_category(self, published_event):
        """BR-E06-04: Harga terendah adalah harga ticket category termurah."""
        lowest = published_event.get_lowest_ticket_price()

        assert lowest is not None
        assert lowest.amount == Decimal("100000")
        assert lowest.currency == "IDR"

    def test_lowest_price_ignores_inactive_category(self, organizer_id, future_dates):
        """BR-E06-04: Category yang di-disable tidak ikut dihitung."""
        event = Event.create(
            name="Test Event",
            description="Test.",
            start_date=future_dates["start_date"],
            end_date=future_dates["end_date"],
            location="Surabaya",
            maximum_capacity=500,
            organizer_id=organizer_id,
        )
        sales_start = future_dates["start_date"] - timedelta(days=7)
        sales_end = future_dates["start_date"] - timedelta(days=1)
        event.add_ticket_category(
            name="Regular",
            price=Money(amount=Decimal("100000"), currency="IDR"),
            quota=200,
            sales_start_date=sales_start,
            sales_end_date=sales_end,
        )
        event.add_ticket_category(
            name="VIP",
            price=Money(amount=Decimal("300000"), currency="IDR"),
            quota=100,
            sales_start_date=sales_start,
            sales_end_date=sales_end,
        )
        event.publish()
        regular_category = event.ticket_categories[0]
        event.disable_ticket_category(regular_category.id)

        lowest = event.get_lowest_ticket_price()

        assert lowest is not None
        assert lowest.amount == Decimal("300000")

    def test_lowest_price_returns_none_when_no_active_category(self, organizer_id, future_dates):
        """BR-E06-05: None jika tidak ada active ticket category."""
        event = Event.create(
            name="Empty Event",
            description="No categories.",
            start_date=future_dates["start_date"],
            end_date=future_dates["end_date"],
            location="Surabaya",
            maximum_capacity=100,
            organizer_id=organizer_id,
        )
        assert event.get_lowest_ticket_price() is None

    def test_lowest_price_single_category(self, organizer_id, future_dates):
        """BR-E06-04: Jika hanya satu category, harga itu yang dikembalikan."""
        event = Event.create(
            name="Single Cat Event",
            description="One category only.",
            start_date=future_dates["start_date"],
            end_date=future_dates["end_date"],
            location="Surabaya",
            maximum_capacity=100,
            organizer_id=organizer_id,
        )
        sales_start = future_dates["start_date"] - timedelta(days=7)
        sales_end = future_dates["start_date"] - timedelta(days=1)
        event.add_ticket_category(
            name="Early Bird",
            price=Money(amount=Decimal("75000"), currency="IDR"),
            quota=100,
            sales_start_date=sales_start,
            sales_end_date=sales_end,
        )
        event.publish()

        assert event.get_lowest_ticket_price().amount == Decimal("75000")


class TestDateFilter:

    def test_matches_date_filter_when_date_is_on_start_date(self, published_event, future_dates):
        """BR-E06-06: Cocok jika filter_date == start_date."""
        assert published_event.matches_date_filter(future_dates["start_date"]) is True

    def test_matches_date_filter_when_date_is_on_end_date(self, published_event, future_dates):
        """BR-E06-06: Cocok jika filter_date == end_date."""
        assert published_event.matches_date_filter(future_dates["end_date"]) is True

    def test_matches_date_filter_when_date_is_between_start_and_end(self, organizer_id):
        """BR-E06-06: Cocok jika filter_date di antara start dan end."""
        now = datetime.utcnow()
        event = Event.create(
            name="Multi-day Event",
            description="3 hari.",
            start_date=now + timedelta(days=10),
            end_date=now + timedelta(days=13),
            location="Surabaya",
            maximum_capacity=100,
            organizer_id=organizer_id,
        )
        assert event.matches_date_filter(now + timedelta(days=11)) is True

    def test_does_not_match_date_filter_when_date_is_before_start(self, published_event, future_dates):
        """BR-E06-06: Tidak cocok jika filter_date sebelum start_date."""
        assert published_event.matches_date_filter(future_dates["start_date"] - timedelta(days=1)) is False

    def test_does_not_match_date_filter_when_date_is_after_end(self, published_event, future_dates):
        """BR-E06-06: Tidak cocok jika filter_date setelah end_date."""
        assert published_event.matches_date_filter(future_dates["end_date"] + timedelta(days=1)) is False


class TestLocationFilter:

    def test_matches_location_filter_exact(self, published_event):
        """BR-E06-07: Cocok dengan keyword yang sama persis."""
        assert published_event.matches_location_filter("Surabaya") is True

    def test_matches_location_filter_case_insensitive(self, published_event):
        """BR-E06-07: Case-insensitive."""
        assert published_event.matches_location_filter("surabaya") is True
        assert published_event.matches_location_filter("SURABAYA") is True

    def test_matches_location_filter_partial_keyword(self, published_event):
        """BR-E06-07: Partial keyword (substring) tetap cocok."""
        assert published_event.matches_location_filter("ITS") is True
        assert published_event.matches_location_filter("Campus") is True

    def test_does_not_match_location_filter_wrong_city(self, published_event):
        """BR-E06-07: Keyword kota berbeda tidak cocok."""
        assert published_event.matches_location_filter("Jakarta") is False

    def test_matches_location_filter_trims_whitespace(self, published_event):
        """BR-E06-07: Spasi di awal/akhir keyword diabaikan."""
        assert published_event.matches_location_filter("  Surabaya  ") is True