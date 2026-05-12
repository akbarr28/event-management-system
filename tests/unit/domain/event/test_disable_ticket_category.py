import pytest
from datetime import datetime, timedelta
from decimal import Decimal

from src.domain.event.aggregates.event import Event
from src.domain.event.domain_events.ticket_category_disabled import TicketCategoryDisabled
from src.domain.event.value_objects.event_status import EventStatus
from src.domain.event.value_objects.organizer_id import OrganizerId
from src.domain.event.value_objects.ticket_category_id import TicketCategoryId
from src.domain.event.value_objects.ticket_category_status import TicketCategoryStatus
from src.domain.shared.exceptions.domain_exception import DomainException
from src.domain.shared.value_objects.money import Money


# Fixtures 
@pytest.fixture
def event_with_category():
    """Event DRAFT dengan satu ticket category aktif."""
    now = datetime.utcnow()
    event = Event.create(
        name="ITS Tech Festival 2025",
        description="Annual tech festival.",
        start_date=now + timedelta(days=30),
        end_date=now + timedelta(days=31),
        location="Surabaya",
        maximum_capacity=500,
        organizer_id=OrganizerId.generate(),
    )
    event.add_ticket_category(
        name="Regular",
        price=Money(Decimal("150000"), "IDR"),
        quota=100,
        sales_start_date=now + timedelta(days=1),
        sales_end_date=now + timedelta(days=25),
    )
    # Bersihkan domain events dari create() dan add_ticket_category()
    event.pull_domain_events()
    return event


@pytest.fixture
def category_id(event_with_category):
    """Ambil ID ticket category pertama dari event."""
    return event_with_category.ticket_categories[0].id


# Happy Path

def test_disable_ticket_category_success(event_with_category, category_id):
    """Ticket category berhasil dinonaktifkan."""
    event_with_category.disable_ticket_category(category_id)

    category = event_with_category.ticket_categories[0]
    assert category.status == TicketCategoryStatus.INACTIVE


def test_disable_ticket_category_raises_domain_event(event_with_category, category_id):
    """Sistem harus raise domain event TicketCategoryDisabled."""
    event_with_category.disable_ticket_category(category_id)
    domain_events = event_with_category.pull_domain_events()

    assert len(domain_events) == 1
    assert isinstance(domain_events[0], TicketCategoryDisabled)
    assert domain_events[0].ticket_category_id == category_id
    assert domain_events[0].event_id == event_with_category.id


def test_disable_ticket_category_still_stored(event_with_category, category_id):
    """Ticket category yang dinonaktifkan tetap tersimpan untuk histori."""
    event_with_category.disable_ticket_category(category_id)

    assert len(event_with_category.ticket_categories) == 1
    assert event_with_category.ticket_categories[0].id == category_id


def test_disable_ticket_category_on_published_event(event_with_category, category_id):
    """Ticket category boleh dinonaktifkan meski event sudah Published."""
    # Paksa status Published tanpa lewat publish() karena US-02 belum diimplementasi
    event_with_category.status = EventStatus.PUBLISHED

    event_with_category.disable_ticket_category(category_id)

    assert event_with_category.ticket_categories[0].status == TicketCategoryStatus.INACTIVE


def test_disable_ticket_category_on_cancelled_event(event_with_category, category_id):
    """Ticket category boleh dinonaktifkan meski event Cancelled (bukan Completed)."""
    event_with_category.status = EventStatus.CANCELLED

    event_with_category.disable_ticket_category(category_id)

    assert event_with_category.ticket_categories[0].status == TicketCategoryStatus.INACTIVE


def test_inactive_category_is_not_available(event_with_category, category_id):
    """Ticket category yang sudah INACTIVE tidak available untuk dibeli."""
    event_with_category.disable_ticket_category(category_id)

    category = event_with_category.ticket_categories[0]
    assert category.is_available() is False


# Unhappy Path 

def test_disable_ticket_category_fails_when_event_completed(event_with_category, category_id):
    """Ticket category tidak bisa dinonaktifkan jika event sudah COMPLETED."""
    event_with_category.status = EventStatus.COMPLETED

    with pytest.raises(DomainException) as exc_info:
        event_with_category.disable_ticket_category(category_id)

    assert "completed" in str(exc_info.value).lower()


def test_disable_ticket_category_fails_when_category_not_found(event_with_category):
    """Harus error jika ticket category ID tidak ditemukan."""
    fake_id = TicketCategoryId.generate()

    with pytest.raises(DomainException) as exc_info:
        event_with_category.disable_ticket_category(fake_id)

    assert "not found" in str(exc_info.value).lower()


def test_disable_already_inactive_category(event_with_category, category_id):
    """Menonaktifkan category yang sudah INACTIVE tetap bisa dilakukan."""
    event_with_category.disable_ticket_category(category_id)
    # Disable kedua kali — tidak raise error, status tetap INACTIVE
    event_with_category.disable_ticket_category(category_id)

    assert event_with_category.ticket_categories[0].status == TicketCategoryStatus.INACTIVE