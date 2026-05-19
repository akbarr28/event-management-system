from src.application.event.commands.cancel_event import CancelEventCommand
from src.application.shared.interfaces.i_notification_service import INotificationService
from src.domain.booking.repositories.i_booking_repository import IBookingRepository
from src.domain.booking.value_objects.booking_status import BookingStatus
from src.domain.event.repositories.i_event_repository import IEventRepository
from src.domain.event.value_objects.event_id import EventId
from src.domain.event.value_objects.organizer_id import OrganizerId
from src.domain.shared.exceptions.domain_exception import DomainException


class CancelEventHandler:
    """
    Command Handler untuk US-03: Cancel Event.
    Membatalkan event dan menandai semua booking Paid agar di-refund.
    """

    def __init__(
        self,
        event_repository: IEventRepository,
        booking_repository: IBookingRepository,
        notification_service: INotificationService,
    ):
        self._event_repository = event_repository
        self._booking_repository = booking_repository
        self._notification_service = notification_service

    async def handle(self, command: CancelEventCommand) -> None:
        event_id = EventId.from_string(command.event_id)
        event = await self._event_repository.find_by_id(event_id)
        if event is None:
            raise DomainException("Event not found.")

       
        organizer_id = OrganizerId.from_string(command.organizer_id)
        if event.organizer_id != organizer_id:
            raise DomainException("Only the event organizer can cancel this event.")

    
        event.cancel()

      
        await self._event_repository.save(event)

        bookings = await self._booking_repository.find_by_event_id(event_id)
        for booking in bookings:
            if booking.status == BookingStatus.PAID:
                booking.mark_refunded()
                await self._booking_repository.save(booking)

            
                await self._notification_service.send_event_cancelled(
                    customer_email=str(booking.customer_id),
                    event_name=event.name,
                )

        event.pull_domain_events()