import pytest
from datetime import datetime, timedelta
from decimal import Decimal

from src.domain.event.aggregates.event import Event
from src.domain.event.domain_events.event_cancelled import EventCancelled
from src.domain.event.value_objects.event_status import EventStatus
from src.domain.event.value_objects.organizer_id import OrganizerId
from src.domain.event.value_objects.ticket_category_status import TicketCategoryStatus
from src.domain.shared.exceptions.domain_exception import DomainException
from src.domain.shared.value_objects.money import Money


# Fixtures 
@pytest.fixture
def now():
    return datetime.utcnow()


@pytest.fixture
def published_event(now):
    """Event yang sudah berstatus PUBLISHED dengan satu active ticket category."""
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
    event.add_ticket_category(
        name="VIP",
        price=Money(Decimal("500000"), "IDR"),
        quota=50,
        sales_start_date=now + timedelta(days=1),
        sales_end_date=now + timedelta(days=25),
    )
    event.publish()
    event.pull_domain_events()
    return event


@pytest.fixture
def draft_event(now):
    """Event yang masih berstatus DRAFT."""
    event = Event.create(
        name="ITS Tech Festival 2025",
        description="Annual tech festival.",
        start_date=now + timedelta(days=30),
        end_date=now + timedelta(days=31),
        location="Surabaya",
        maximum_capacity=500,
        organizer_id=OrganizerId.generate(),
    )
    event.pull_domain_events()
    return event


# Happy Path 

def test_cancel_event_success(published_event):
    """Event berstatus PUBLISHED berhasil dibatalkan."""
    published_event.cancel()

    assert published_event.status == EventStatus.CANCELLED


def test_cancel_event_raises_domain_event(published_event):
    """Sistem harus raise domain event EventCancelled."""
    published_event.cancel()
    domain_events = published_event.pull_domain_events()

    assert len(domain_events) == 1
    assert isinstance(domain_events[0], EventCancelled)
    assert domain_events[0].event_id == published_event.id


def test_cancel_event_disables_all_active_ticket_categories(published_event):
    """Semua ticket category ACTIVE harus dinonaktifkan ketika event dibatalkan."""
    # Sebelum cancel — semua ACTIVE
    assert all(
        tc.status == TicketCategoryStatus.ACTIVE
        for tc in published_event.ticket_categories
    )

    published_event.cancel()

    # Setelah cancel — semua INACTIVE
    assert all(
        tc.status == TicketCategoryStatus.INACTIVE
        for tc in published_event.ticket_categories
    )


def test_cancel_event_with_mixed_category_status(now):
    """Hanya ticket category ACTIVE yang dinonaktifkan, yang sudah INACTIVE dibiarkan."""
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
    event.add_ticket_category(
        name="VIP",
        price=Money(Decimal("500000"), "IDR"),
        quota=50,
        sales_start_date=now + timedelta(days=1),
        sales_end_date=now + timedelta(days=25),
    )

    # Nonaktifkan VIP sebelum publish
    vip_id = event.ticket_categories[1].id
    event.disable_ticket_category(vip_id)
    event.publish()
    event.pull_domain_events()

    event.cancel()

    # Regular (tadinya ACTIVE) → harus INACTIVE
    assert event.ticket_categories[0].status == TicketCategoryStatus.INACTIVE
    # VIP (sudah INACTIVE sejak awal) → tetap INACTIVE
    assert event.ticket_categories[1].status == TicketCategoryStatus.INACTIVE


def test_cancel_event_all_categories_not_purchasable_after_cancel(published_event):
    """Setelah cancel, semua ticket category tidak bisa dibeli."""
    published_event.cancel()

    for tc in published_event.ticket_categories:
        assert tc.is_available() is False


# Unhappy Path 

def test_cancel_event_fails_when_draft(draft_event):
    """Event berstatus DRAFT tidak bisa dibatalkan."""
    with pytest.raises(DomainException) as exc_info:
        draft_event.cancel()

    assert "draft" in str(exc_info.value).lower()


def test_cancel_event_fails_when_completed(published_event):
    """Event berstatus COMPLETED tidak bisa dibatalkan."""
    published_event.status = EventStatus.COMPLETED

    with pytest.raises(DomainException) as exc_info:
        published_event.cancel()

    assert "completed" in str(exc_info.value).lower()


def test_cancel_event_fails_when_already_cancelled(published_event):
    """Event yang sudah CANCELLED tidak bisa dibatalkan lagi."""
    published_event.cancel()
    published_event.pull_domain_events()

    with pytest.raises(DomainException) as exc_info:
        published_event.cancel()

    assert "already cancelled" in str(exc_info.value).lower()