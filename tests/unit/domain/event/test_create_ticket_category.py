import pytest
from datetime import datetime, timedelta
from decimal import Decimal

from src.domain.event.aggregates.event import Event
from src.domain.event.domain_events.ticket_category_created import TicketCategoryCreated
from src.domain.event.value_objects.organizer_id import OrganizerId
from src.domain.event.value_objects.ticket_category_status import TicketCategoryStatus
from src.domain.shared.exceptions.domain_exception import DomainException
from src.domain.shared.value_objects.money import Money


# Fixtures 
@pytest.fixture
def base_event():
    now = datetime.utcnow()
    return Event.create(
        name="ITS Tech Festival 2025",
        description="Annual tech festival.",
        start_date=now + timedelta(days=30),
        end_date=now + timedelta(days=31),
        location="Surabaya",
        maximum_capacity=500,
        organizer_id=OrganizerId.generate(),
    )


@pytest.fixture
def valid_category_data(base_event):
    now = datetime.utcnow()
    return {
        "name": "Regular",
        "price": Money(Decimal("150000"), "IDR"),
        "quota": 100,
        "sales_start_date": now + timedelta(days=1),
        "sales_end_date": now + timedelta(days=25),   # sebelum event start
    }


# Happy Path 

def test_add_ticket_category_success(base_event, valid_category_data):
    """Ticket category berhasil ditambahkan ke event."""
    category = base_event.add_ticket_category(**valid_category_data)

    assert category.name == valid_category_data["name"]
    assert category.price == valid_category_data["price"]
    assert category.quota == valid_category_data["quota"]
    assert category.remaining_quota == valid_category_data["quota"]
    assert category.status == TicketCategoryStatus.ACTIVE
    assert len(base_event.ticket_categories) == 1


def test_add_ticket_category_raises_domain_event(base_event, valid_category_data):
    """Sistem harus raise domain event TicketCategoryCreated."""
    # Bersihkan EventCreated dari create()
    base_event.pull_domain_events()

    base_event.add_ticket_category(**valid_category_data)
    domain_events = base_event.pull_domain_events()

    assert len(domain_events) == 1
    assert isinstance(domain_events[0], TicketCategoryCreated)
    assert domain_events[0].event_id == base_event.id


def test_add_multiple_ticket_categories(base_event):
    """Bisa menambahkan lebih dari satu ticket category."""
    now = datetime.utcnow()
    sales_start = now + timedelta(days=1)
    sales_end = now + timedelta(days=25)

    base_event.add_ticket_category(
        name="Regular",
        price=Money(Decimal("150000"), "IDR"),
        quota=200,
        sales_start_date=sales_start,
        sales_end_date=sales_end,
    )
    base_event.add_ticket_category(
        name="VIP",
        price=Money(Decimal("500000"), "IDR"),
        quota=100,
        sales_start_date=sales_start,
        sales_end_date=sales_end,
    )

    assert len(base_event.ticket_categories) == 2


def test_ticket_category_initial_remaining_quota_equals_quota(base_event, valid_category_data):
    """remaining_quota awal harus sama dengan quota."""
    category = base_event.add_ticket_category(**valid_category_data)

    assert category.remaining_quota == category.quota


def test_add_ticket_category_with_zero_price_is_allowed(base_event, valid_category_data):
    """Harga tiket boleh nol (free event)."""
    valid_category_data["price"] = Money(Decimal("0"), "IDR")
    category = base_event.add_ticket_category(**valid_category_data)

    assert category.price.amount == Decimal("0")


# Unhappy Path 

def test_add_ticket_category_fails_when_quota_is_zero(base_event, valid_category_data):
    """Ticket category tidak bisa dibuat jika quota = 0."""
    valid_category_data["quota"] = 0

    with pytest.raises(DomainException) as exc_info:
        base_event.add_ticket_category(**valid_category_data)

    assert "quota" in str(exc_info.value).lower()


def test_add_ticket_category_fails_when_quota_is_negative(base_event, valid_category_data):
    """Ticket category tidak bisa dibuat jika quota negatif."""
    valid_category_data["quota"] = -50

    with pytest.raises(DomainException) as exc_info:
        base_event.add_ticket_category(**valid_category_data)

    assert "quota" in str(exc_info.value).lower()


def test_add_ticket_category_fails_when_price_is_negative(base_event, valid_category_data):
    """Ticket category tidak bisa dibuat jika harga negatif."""
    with pytest.raises(ValueError):
        valid_category_data["price"] = Money(Decimal("-1"), "IDR")
        base_event.add_ticket_category(**valid_category_data)


def test_add_ticket_category_fails_when_sales_end_after_event_start(base_event, valid_category_data):
    """Sales end date tidak boleh melewati event start date."""
    valid_category_data["sales_end_date"] = base_event.start_date + timedelta(days=1)

    with pytest.raises(DomainException) as exc_info:
        base_event.add_ticket_category(**valid_category_data)

    assert "sales end date" in str(exc_info.value).lower()


def test_add_ticket_category_fails_when_sales_start_after_sales_end(base_event, valid_category_data):
    """Sales start date tidak boleh setelah sales end date."""
    now = datetime.utcnow()
    valid_category_data["sales_start_date"] = now + timedelta(days=20)
    valid_category_data["sales_end_date"] = now + timedelta(days=10)

    with pytest.raises(DomainException) as exc_info:
        base_event.add_ticket_category(**valid_category_data)

    assert "sales start date" in str(exc_info.value).lower()


def test_add_ticket_category_fails_when_total_quota_exceeds_capacity(base_event):
    """Total quota semua category tidak boleh melebihi maximum_capacity event (500)."""
    now = datetime.utcnow()
    sales_start = now + timedelta(days=1)
    sales_end = now + timedelta(days=25)

    # Tambah category pertama quota 400
    base_event.add_ticket_category(
        name="Regular",
        price=Money(Decimal("150000"), "IDR"),
        quota=400,
        sales_start_date=sales_start,
        sales_end_date=sales_end,
    )

    # Tambah category kedua quota 200 → total 600 > 500 (maximum_capacity)
    with pytest.raises(DomainException) as exc_info:
        base_event.add_ticket_category(
            name="VIP",
            price=Money(Decimal("500000"), "IDR"),
            quota=200,
            sales_start_date=sales_start,
            sales_end_date=sales_end,
        )

    assert "capacity" in str(exc_info.value).lower()