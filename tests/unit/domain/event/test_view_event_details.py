import pytest
from datetime import datetime, timedelta
from decimal import Decimal

from src.domain.event.aggregates.event import Event
from src.domain.event.value_objects.organizer_id import OrganizerId
from src.domain.event.value_objects.ticket_category_display_status import TicketCategoryDisplayStatus
from src.domain.shared.value_objects.money import Money


@pytest.fixture
def organizer_id():
    return OrganizerId.generate()


@pytest.fixture
def now():
    return datetime.utcnow()


@pytest.fixture
def published_event(organizer_id, now):
    event = Event.create(
        name="ITS Tech Fest 2025",
        description="Annual tech festival.",
        start_date=now + timedelta(days=10),
        end_date=now + timedelta(days=11),
        location="Surabaya, ITS Campus",
        maximum_capacity=500,
        organizer_id=organizer_id,
    )
    return event


def add_category(event, name, price, quota, sales_start, sales_end):
    event.add_ticket_category(
        name=name,
        price=Money(amount=Decimal(str(price)), currency="IDR"),
        quota=quota,
        sales_start_date=sales_start,
        sales_end_date=sales_end,
    )
    return event.ticket_categories[-1]

class TestActiveTicketCategoriesForDisplay:

    def test_returns_only_active_categories(self, published_event, now):
        """BR-E07-01: Inactive category tidak masuk ke list display."""
        sales_start = now - timedelta(days=2)
        sales_end = now + timedelta(days=5)

        add_category(published_event, "Regular", 100000, 200, sales_start, sales_end)
        add_category(published_event, "VIP", 300000, 100, sales_start, sales_end)
        published_event.publish()

        # Disable VIP
        vip = published_event.ticket_categories[1]
        published_event.disable_ticket_category(vip.id)

        result = published_event.get_active_ticket_categories_for_display()

        assert len(result) == 1
        assert result[0].name == "Regular"

    def test_returns_empty_when_all_categories_inactive(self, published_event, now):
        """BR-E07-01: Jika semua category inactive, list kosong."""
        sales_start = now - timedelta(days=2)
        sales_end = now + timedelta(days=5)

        add_category(published_event, "Regular", 100000, 100, sales_start, sales_end)
        published_event.publish()

        regular = published_event.ticket_categories[0]
        published_event.disable_ticket_category(regular.id)

        result = published_event.get_active_ticket_categories_for_display()

        assert result == []

    def test_returns_all_when_all_active(self, published_event, now):
        """BR-E07-01: Semua category active semuanya masuk."""
        sales_start = now - timedelta(days=2)
        sales_end = now + timedelta(days=5)

        add_category(published_event, "Regular", 100000, 200, sales_start, sales_end)
        add_category(published_event, "VIP", 300000, 100, sales_start, sales_end)
        add_category(published_event, "Early Bird", 75000, 50, sales_start, sales_end)
        published_event.publish()

        result = published_event.get_active_ticket_categories_for_display()

        assert len(result) == 3


class TestDisplayStatusComingSoon:

    def test_display_status_is_coming_soon_when_sales_not_started(self, published_event, now):
        """BR-E07-02: Sales period belum mulai → COMING_SOON."""
        sales_start = now + timedelta(days=3)
        sales_end = now + timedelta(days=7)

        category = add_category(published_event, "Early Bird", 75000, 100, sales_start, sales_end)

        assert category.get_display_status(now) == TicketCategoryDisplayStatus.COMING_SOON

    def test_display_status_is_not_coming_soon_when_sales_started(self, published_event, now):
        """BR-E07-02: Jika sales sudah mulai, bukan COMING_SOON."""
        sales_start = now - timedelta(days=1)
        sales_end = now + timedelta(days=5)

        category = add_category(published_event, "Regular", 100000, 100, sales_start, sales_end)

        assert category.get_display_status(now) != TicketCategoryDisplayStatus.COMING_SOON


class TestDisplayStatusSalesClosed:

    def test_display_status_is_sales_closed_when_sales_period_ended(self, published_event, now):
        """BR-E07-03: Sales period sudah berakhir → SALES_CLOSED."""
        sales_start = now - timedelta(days=5)
        sales_end = now - timedelta(days=1)

        category = add_category(published_event, "Regular", 100000, 100, sales_start, sales_end)

        assert category.get_display_status(now) == TicketCategoryDisplayStatus.SALES_CLOSED

    def test_display_status_is_not_sales_closed_when_sales_still_open(self, published_event, now):
        """BR-E07-03: Jika sales masih buka, bukan SALES_CLOSED."""
        sales_start = now - timedelta(days=1)
        sales_end = now + timedelta(days=5)

        category = add_category(published_event, "Regular", 100000, 100, sales_start, sales_end)

        assert category.get_display_status(now) != TicketCategoryDisplayStatus.SALES_CLOSED



class TestDisplayStatusSoldOut:

    def test_display_status_is_sold_out_when_no_remaining_quota(self, published_event, now):
        """BR-E07-04: Quota habis → SOLD_OUT, meski masih dalam sales period."""
        sales_start = now - timedelta(days=1)
        sales_end = now + timedelta(days=5)

        category = add_category(published_event, "Regular", 100000, 1, sales_start, sales_end)

        # Simulasi quota habis
        category.remaining_quota = 0

        assert category.get_display_status(now) == TicketCategoryDisplayStatus.SOLD_OUT

    def test_sold_out_takes_priority_over_coming_soon(self, published_event, now):
        """BR-E07-04: SOLD_OUT prioritas lebih tinggi dari COMING_SOON."""
        sales_start = now + timedelta(days=3)
        sales_end = now + timedelta(days=7)

        category = add_category(published_event, "Early Bird", 75000, 1, sales_start, sales_end)
        category.remaining_quota = 0

        assert category.get_display_status(now) == TicketCategoryDisplayStatus.SOLD_OUT

    def test_sold_out_takes_priority_over_sales_closed(self, published_event, now):
        """BR-E07-04: SOLD_OUT prioritas lebih tinggi dari SALES_CLOSED."""
        sales_start = now - timedelta(days=5)
        sales_end = now - timedelta(days=1)

        category = add_category(published_event, "Regular", 100000, 1, sales_start, sales_end)
        category.remaining_quota = 0

        assert category.get_display_status(now) == TicketCategoryDisplayStatus.SOLD_OUT


class TestDisplayStatusAvailable:

    def test_display_status_is_available_when_in_sales_period_with_quota(self, published_event, now):
        """BR-E07-05: Dalam sales period dan ada quota → AVAILABLE."""
        sales_start = now - timedelta(days=1)
        sales_end = now + timedelta(days=5)

        category = add_category(published_event, "Regular", 100000, 100, sales_start, sales_end)

        assert category.get_display_status(now) == TicketCategoryDisplayStatus.AVAILABLE

    def test_display_status_available_on_exact_sales_start(self, published_event, now):
        """BR-E07-05: Tepat di sales_start_date → AVAILABLE."""
        sales_start = now
        sales_end = now + timedelta(days=5)

        category = add_category(published_event, "Regular", 100000, 100, sales_start, sales_end)

        assert category.get_display_status(now) == TicketCategoryDisplayStatus.AVAILABLE

    def test_display_status_available_on_exact_sales_end(self, published_event, now):
        """BR-E07-05: Tepat di sales_end_date → AVAILABLE."""
        sales_start = now - timedelta(days=5)
        sales_end = now

        category = add_category(published_event, "Regular", 100000, 100, sales_start, sales_end)

        assert category.get_display_status(now) == TicketCategoryDisplayStatus.AVAILABLE