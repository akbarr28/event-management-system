import pytest
from datetime import datetime, timedelta
from decimal import Decimal

from src.domain.event.aggregates.event import Event
from src.domain.event.domain_events.event_published import EventPublished
from src.domain.event.value_objects.event_status import EventStatus
from src.domain.event.value_objects.organizer_id import OrganizerId
from src.domain.shared.exceptions.domain_exception import DomainException
from src.domain.shared.value_objects.money import Money


# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture
def draft_event():
    """Event DRAFT tanpa ticket category."""
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
    event.pull_domain_events()
    return event


@pytest.fixture
def draft_event_with_active_category(draft_event):
    """Event DRAFT dengan satu ticket category ACTIVE."""
    now = datetime.utcnow()
    draft_event.add_ticket_category(
        name="Regular",
        price=Money(Decimal("150000"), "IDR"),
        quota=100,
        sales_start_date=now + timedelta(days=1),
        sales_end_date=now + timedelta(days=25),
    )
    draft_event.pull_domain_events()
    return draft_event


# ── Happy Path ────────────────────────────────────────────────────────────────

def test_publish_event_success(draft_event_with_active_category):
    """Event berhasil dipublish jika memiliki minimal satu active ticket category."""
    draft_event_with_active_category.publish()

    assert draft_event_with_active_category.status == EventStatus.PUBLISHED


def test_publish_event_raises_domain_event(draft_event_with_active_category):
    """Sistem harus raise domain event EventPublished."""
    draft_event_with_active_category.publish()
    domain_events = draft_event_with_active_category.pull_domain_events()

    assert len(domain_events) == 1
    assert isinstance(domain_events[0], EventPublished)
    assert domain_events[0].event_id == draft_event_with_active_category.id


def test_publish_event_with_multiple_active_categories(draft_event):
    """Event dengan beberapa active ticket category bisa dipublish."""
    now = datetime.utcnow()
    sales_start = now + timedelta(days=1)
    sales_end = now + timedelta(days=25)

    draft_event.add_ticket_category(
        name="Regular",
        price=Money(Decimal("150000"), "IDR"),
        quota=200,
        sales_start_date=sales_start,
        sales_end_date=sales_end,
    )
    draft_event.add_ticket_category(
        name="VIP",
        price=Money(Decimal("500000"), "IDR"),
        quota=100,
        sales_start_date=sales_start,
        sales_end_date=sales_end,
    )
    draft_event.pull_domain_events()

    draft_event.publish()

    assert draft_event.status == EventStatus.PUBLISHED


def test_publish_event_with_one_active_one_inactive_category(draft_event):
    """Event bisa dipublish selama minimal satu category masih ACTIVE."""
    now = datetime.utcnow()
    sales_start = now + timedelta(days=1)
    sales_end = now + timedelta(days=25)

    draft_event.add_ticket_category(
        name="Regular",
        price=Money(Decimal("150000"), "IDR"),
        quota=100,
        sales_start_date=sales_start,
        sales_end_date=sales_end,
    )
    draft_event.add_ticket_category(
        name="VIP",
        price=Money(Decimal("500000"), "IDR"),
        quota=50,
        sales_start_date=sales_start,
        sales_end_date=sales_end,
    )

    # Nonaktifkan VIP
    vip_id = draft_event.ticket_categories[1].id
    draft_event.disable_ticket_category(vip_id)
    draft_event.pull_domain_events()

    # Regular masih ACTIVE → publish harus berhasil
    draft_event.publish()

    assert draft_event.status == EventStatus.PUBLISHED


# ── Unhappy Path ──────────────────────────────────────────────────────────────

def test_publish_event_fails_without_ticket_category(draft_event):
    """Event tidak bisa dipublish jika tidak punya ticket category sama sekali."""
    with pytest.raises(DomainException) as exc_info:
        draft_event.publish()

    assert "active ticket category" in str(exc_info.value).lower()


def test_publish_event_fails_when_all_categories_inactive(draft_event):
    """Event tidak bisa dipublish jika semua ticket category INACTIVE."""
    now = datetime.utcnow()
    draft_event.add_ticket_category(
        name="Regular",
        price=Money(Decimal("150000"), "IDR"),
        quota=100,
        sales_start_date=now + timedelta(days=1),
        sales_end_date=now + timedelta(days=25),
    )

    # Nonaktifkan satu-satunya category
    category_id = draft_event.ticket_categories[0].id
    draft_event.disable_ticket_category(category_id)
    draft_event.pull_domain_events()

    with pytest.raises(DomainException) as exc_info:
        draft_event.publish()

    assert "active ticket category" in str(exc_info.value).lower()


def test_publish_event_fails_when_already_published(draft_event_with_active_category):
    """Event yang sudah Published tidak bisa dipublish lagi."""
    draft_event_with_active_category.publish()
    draft_event_with_active_category.pull_domain_events()

    with pytest.raises(DomainException) as exc_info:
        draft_event_with_active_category.publish()

    assert "already published" in str(exc_info.value).lower()


def test_publish_event_fails_when_cancelled(draft_event_with_active_category):
    """Event berstatus CANCELLED tidak bisa dipublish."""
    draft_event_with_active_category.status = EventStatus.CANCELLED

    with pytest.raises(DomainException) as exc_info:
        draft_event_with_active_category.publish()

    assert "cancelled" in str(exc_info.value).lower()


def test_publish_event_fails_when_completed(draft_event_with_active_category):
    """Event berstatus COMPLETED tidak bisa dipublish."""
    draft_event_with_active_category.status = EventStatus.COMPLETED

    with pytest.raises(DomainException) as exc_info:
        draft_event_with_active_category.publish()

    assert "completed" in str(exc_info.value).lower()