from datetime import datetime

from src.application.booking.commands.create_booking import CreateBookingCommand
from src.application.shared.dtos.booking_dto import BookingDTO
from src.domain.booking.aggregates.booking import Booking
from src.domain.booking.domain_services.booking_domain_service import BookingDomainService
from src.domain.booking.repositories.i_booking_repository import IBookingRepository
from src.domain.booking.value_objects.customer_id import CustomerId
from src.domain.event.repositories.i_event_repository import IEventRepository
from src.domain.event.value_objects.event_id import EventId
from src.domain.event.value_objects.event_status import EventStatus
from src.domain.event.value_objects.ticket_category_id import TicketCategoryId
from src.domain.event.value_objects.ticket_category_status import TicketCategoryStatus
from src.domain.shared.exceptions.domain_exception import DomainException


class CreateBookingHandler:
    """
    Command Handler untuk US-08: Create Ticket Booking.
    Memvalidasi event, ticket category, dan quota sebelum membuat booking.
    """

    def __init__(
        self,
        event_repository: IEventRepository,
        booking_repository: IBookingRepository,
    ):
        self._event_repository = event_repository
        self._booking_repository = booking_repository

    async def handle(self, command: CreateBookingCommand) -> BookingDTO:
        now = datetime.utcnow()

        # Ambil event
        event_id = EventId.from_string(command.event_id)
        event = await self._event_repository.find_by_id(event_id)
        if event is None:
            raise DomainException("Event not found.")

        # BR-B08: event harus berstatus PUBLISHED
        if event.status != EventStatus.PUBLISHED:
            raise DomainException(
                "Booking can only be created for a published event."
            )

        # Cari ticket category yang dipilih
        ticket_category_id = TicketCategoryId.from_string(
            command.ticket_category_id
        )
        ticket_category = next(
            (tc for tc in event.ticket_categories
             if tc.id == ticket_category_id),
            None,
        )
        if ticket_category is None:
            raise DomainException("Ticket category not found.")

        # BR-B08: ticket category harus ACTIVE
        if ticket_category.status != TicketCategoryStatus.ACTIVE:
            raise DomainException(
                "Booking can only be created for an active ticket category."
            )

        # BR-B08: harus dalam sales period
        if not ticket_category.is_on_sale(now):
            raise DomainException(
                "Booking can only be created within the ticket sales period."
            )

        # BR-B08: quantity tidak boleh melebihi remaining quota
        if command.quantity > ticket_category.remaining_quota:
            raise DomainException(
                "Ticket quantity exceeds remaining quota."
            )

        # BR-B08: customer tidak boleh punya active booking untuk event ini
        customer_id = CustomerId.from_string(command.customer_id)
        existing_bookings = await self._booking_repository.find_by_customer_id(
            customer_id
        )
        BookingDomainService.validate_no_active_booking_exists(
            customer_id=customer_id,
            event_id=event_id,
            existing_bookings=existing_bookings,
        )

        # Buat booking
        booking = Booking.create(
            customer_id=customer_id,
            event_id=event_id,
            ticket_category_id=ticket_category_id,
            quantity=command.quantity,
            unit_price=ticket_category.price,
            now=now,
        )

        # Kurangi remaining quota di ticket category
        ticket_category.reserve_quota(command.quantity)

        # Simpan booking dan event (karena quota berubah)
        await self._booking_repository.save(booking)
        await self._event_repository.save(event)

        booking.pull_domain_events()

        return BookingDTO(
            id=str(booking.id),
            customer_id=str(booking.customer_id),
            event_id=str(booking.event_id),
            ticket_category_id=str(booking.ticket_category_id),
            quantity=booking.quantity,
            unit_price=booking.unit_price.amount,
            total_price=booking.total_price.amount,
            currency=booking.total_price.currency,
            status=booking.status.value,
            payment_deadline=booking.payment_deadline,
        )