from src.application.event.commands.create_event import CreateEventCommand
from src.application.shared.dtos.event_dto import EventSummaryDTO
from src.domain.event.aggregates.event import Event
from src.domain.event.repositories.i_event_repository import IEventRepository
from src.domain.event.value_objects.organizer_id import OrganizerId


class CreateEventHandler:
    """
    Command Handler untuk US-01: Create Event.
    Membuat event baru dan menyimpannya ke repository.
    """

    def __init__(
        self,
        event_repository: IEventRepository,
    ):
        self._event_repository = event_repository

    async def handle(self, command: CreateEventCommand) -> EventSummaryDTO:
        organizer_id = OrganizerId.from_string(command.organizer_id)

        event = Event.create(
            name=command.name,
            description=command.description,
            start_date=command.start_date,
            end_date=command.end_date,
            location=command.location,
            maximum_capacity=command.maximum_capacity,
            organizer_id=organizer_id,
        )

        await self._event_repository.save(event)

        event.pull_domain_events()

        return EventSummaryDTO(
            id=str(event.id),
            name=event.name,
            description=event.description,
            start_date=event.start_date,
            end_date=event.end_date,
            location=event.location,
            organizer_id=str(event.organizer_id),
            status=event.status.value,
            lowest_price=None,
            lowest_price_currency="IDR",
        )