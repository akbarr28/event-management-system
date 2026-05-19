from src.application.event.commands.disable_ticket_category import DisableTicketCategoryCommand
from src.domain.event.repositories.i_event_repository import IEventRepository
from src.domain.event.value_objects.event_id import EventId
from src.domain.event.value_objects.organizer_id import OrganizerId
from src.domain.event.value_objects.ticket_category_id import TicketCategoryId
from src.domain.shared.exceptions.domain_exception import DomainException


class DisableTicketCategoryHandler:
    """
    Command Handler untuk US-05: Disable Ticket Category.
    Menonaktifkan ticket category sehingga tidak bisa dibeli customer.
    """

    def __init__(
        self,
        event_repository: IEventRepository,
    ):
        self._event_repository = event_repository

    async def handle(self, command: DisableTicketCategoryCommand) -> None:  
        event_id = EventId.from_string(command.event_id)
        event = await self._event_repository.find_by_id(event_id)
        if event is None:
            raise DomainException("Event not found.")


        organizer_id = OrganizerId.from_string(command.organizer_id)
        if event.organizer_id != organizer_id:
            raise DomainException(
                "Only the event organizer can disable ticket categories."
            )
        
        ticket_category_id = TicketCategoryId.from_string(command.ticket_category_id)
        event.disable_ticket_category(ticket_category_id)

        await self._event_repository.save(event)

        event.pull_domain_events()