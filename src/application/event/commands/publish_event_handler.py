from src.application.event.commands.publish_event import PublishEventCommand
from src.application.shared.interfaces.i_notification_service import INotificationService
from src.domain.event.repositories.i_event_repository import IEventRepository
from src.domain.event.value_objects.event_id import EventId
from src.domain.event.value_objects.organizer_id import OrganizerId
from src.domain.shared.exceptions.domain_exception import DomainException


class PublishEventHandler:
    """
    Command Handler untuk US-02: Publish Event.
    Memvalidasi dan mempublish event yang berstatus Draft.
    """

    def __init__(
        self,
        event_repository: IEventRepository,
        notification_service: INotificationService,
    ):
        self._event_repository = event_repository
        self._notification_service = notification_service

    async def handle(self, command: PublishEventCommand) -> None:
        event_id = EventId.from_string(command.event_id)
        event = await self._event_repository.find_by_id(event_id)
        if event is None:
            raise DomainException("Event not found.")

        organizer_id = OrganizerId.from_string(command.organizer_id)
        if event.organizer_id != organizer_id:
            raise DomainException("Only the event organizer can publish this event.")

        event.publish()

        await self._event_repository.save(event)

        domain_events = event.pull_domain_events()
        for domain_event in domain_events:
            await self._notification_service.notify_event_published(event)