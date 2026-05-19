from src.application.event.commands.create_ticket_category import CreateTicketCategoryCommand
from src.domain.event.repositories.i_event_repository import IEventRepository
from src.domain.event.value_objects.event_id import EventId
from src.domain.event.value_objects.organizer_id import OrganizerId
from src.domain.shared.exceptions.domain_exception import DomainException
from src.domain.shared.value_objects.money import Money


class CreateTicketCategoryHandler:
    """
    Command Handler untuk US-04: Create Ticket Category.
    Menambahkan ticket category baru ke event.
    """

    def __init__(
        self,
        event_repository: IEventRepository,
    ):
        self._event_repository = event_repository

    async def handle(self, command: CreateTicketCategoryCommand) -> None:
        event_id = EventId.from_string(command.event_id)
        event = await self._event_repository.find_by_id(event_id)
        if event is None:
            raise DomainException("Event not found.")

        organizer_id = OrganizerId.from_string(command.organizer_id)
        if event.organizer_id != organizer_id:
            raise DomainException(
                "Only the event organizer can add ticket categories."
            )

        price = Money(amount=command.price, currency=command.currency)
        event.add_ticket_category(
            name=command.name,
            price=price,
            quota=command.quota,
            sales_start_date=command.sales_start_date,
            sales_end_date=command.sales_end_date,
        )

        await self._event_repository.save(event)

        event.pull_domain_events()