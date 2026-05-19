from datetime import datetime

from src.application.booking.commands.expire_booking import ExpireBookingCommand
from src.domain.booking.repositories.i_booking_repository import IBookingRepository
from src.domain.booking.value_objects.booking_id import BookingId
from src.domain.event.repositories.i_event_repository import IEventRepository
from src.domain.shared.exceptions.domain_exception import DomainException


class ExpireBookingHandler:
    """
    Command Handler untuk US-11: Expire Booking.
    Menandai booking sebagai Expired dan melepas quota tiket yang direservasi.
    """

    def __init__(
        self,
        booking_repository: IBookingRepository,
        event_repository: IEventRepository,
    ):
        self._booking_repository = booking_repository
        self._event_repository = event_repository

    async def handle(self, command: ExpireBookingCommand) -> None:
  
        booking_id = BookingId.from_string(command.booking_id)
        booking = await self._booking_repository.find_by_id(booking_id)
        if booking is None:
            raise DomainException("Booking not found.")

        now = datetime.utcnow()
        booking.expire(now=now)

        await self._booking_repository.save(booking)

        event = await self._event_repository.find_by_id(booking.event_id)
        if event is not None:
            ticket_category = next(
                (tc for tc in event.ticket_categories
                 if tc.id == booking.ticket_category_id),
                None,
            )
            if ticket_category is not None:
                ticket_category.release_quota(booking.quantity)
                await self._event_repository.save(event)

        booking.pull_domain_events()