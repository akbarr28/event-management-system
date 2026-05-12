import pytest
from datetime import datetime, timedelta

from src.domain.event.aggregates.event import Event
from src.domain.event.domain_events.event_created import EventCreated
from src.domain.event.value_objects.event_status import EventStatus
from src.domain.event.value_objects.organizer_id import OrganizerId
from src.domain.shared.exceptions.domain_exception import DomainException


# Fixtures 

@pytest.fixture
def valid_organizer_id():
    return OrganizerId.generate()


@pytest.fixture
def valid_event_data():
    now = datetime.utcnow()
    return {
        "name": "ITS Tech Festival 2025",
        "description": "Annual technology festival at ITS.",
        "start_date": now + timedelta(days=10),
        "end_date": now + timedelta(days=11),
        "location": "Surabaya, ITS Campus",
        "maximum_capacity": 500,
    }


# Happy Path 

def test_create_event_success(valid_event_data, valid_organizer_id):
    """Event berhasil dibuat dengan data yang valid."""
    event = Event.create(**valid_event_data, organizer_id=valid_organizer_id)

    assert event.name == valid_event_data["name"]
    assert event.description == valid_event_data["description"]
    assert event.location == valid_event_data["location"]
    assert event.maximum_capacity == valid_event_data["maximum_capacity"]
    assert event.organizer_id == valid_organizer_id


def test_create_event_initial_status_is_draft(valid_event_data, valid_organizer_id):
    """Event yang baru dibuat harus berstatus DRAFT."""
    event = Event.create(**valid_event_data, organizer_id=valid_organizer_id)

    assert event.status == EventStatus.DRAFT


def test_create_event_raises_event_created_domain_event(valid_event_data, valid_organizer_id):
    """Sistem harus raise domain event EventCreated setelah event dibuat."""
    event = Event.create(**valid_event_data, organizer_id=valid_organizer_id)
    domain_events = event.pull_domain_events()

    assert len(domain_events) == 1
    assert isinstance(domain_events[0], EventCreated)
    assert domain_events[0].event_id == event.id
    assert domain_events[0].organizer_id == valid_organizer_id


def test_create_event_generates_unique_id(valid_event_data, valid_organizer_id):
    """Setiap event yang dibuat harus memiliki ID yang unik."""
    event_1 = Event.create(**valid_event_data, organizer_id=valid_organizer_id)
    event_2 = Event.create(**valid_event_data, organizer_id=valid_organizer_id)

    assert event_1.id != event_2.id


def test_pull_domain_events_clears_after_pull(valid_event_data, valid_organizer_id):
    """Domain events harus terhapus setelah di-pull."""
    event = Event.create(**valid_event_data, organizer_id=valid_organizer_id)
    event.pull_domain_events()
    remaining = event.pull_domain_events()

    assert len(remaining) == 0


# Unhappy Path

def test_create_event_fails_when_end_date_before_start_date(valid_event_data, valid_organizer_id):
    """Event tidak bisa dibuat jika end_date lebih awal dari start_date."""
    now = datetime.utcnow()
    valid_event_data["start_date"] = now + timedelta(days=10)
    valid_event_data["end_date"] = now + timedelta(days=5)  # lebih awal

    with pytest.raises(DomainException) as exc_info:
        Event.create(**valid_event_data, organizer_id=valid_organizer_id)

    assert "end date" in str(exc_info.value).lower()


def test_create_event_fails_when_end_date_equals_start_date_is_allowed(valid_event_data, valid_organizer_id):
    """Event boleh dibuat jika end_date sama dengan start_date (one-day event)."""
    same_day = datetime.utcnow() + timedelta(days=10)
    valid_event_data["start_date"] = same_day
    valid_event_data["end_date"] = same_day

    event = Event.create(**valid_event_data, organizer_id=valid_organizer_id)
    assert event is not None


def test_create_event_fails_when_capacity_is_zero(valid_event_data, valid_organizer_id):
    """Event tidak bisa dibuat jika maximum_capacity = 0."""
    valid_event_data["maximum_capacity"] = 0

    with pytest.raises(DomainException) as exc_info:
        Event.create(**valid_event_data, organizer_id=valid_organizer_id)

    assert "capacity" in str(exc_info.value).lower()


def test_create_event_fails_when_capacity_is_negative(valid_event_data, valid_organizer_id):
    """Event tidak bisa dibuat jika maximum_capacity negatif."""
    valid_event_data["maximum_capacity"] = -100

    with pytest.raises(DomainException) as exc_info:
        Event.create(**valid_event_data, organizer_id=valid_organizer_id)

    assert "capacity" in str(exc_info.value).lower()