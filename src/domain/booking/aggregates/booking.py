from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import List

from src.domain.booking.domain_events.ticket_reserved import TicketReserved
from src.domain.booking.value_objects.booking_id import BookingId
from src.domain.booking.value_objects.booking_status import BookingStatus
from src.domain.booking.value_objects.customer_id import CustomerId
from src.domain.event.value_objects.event_id import EventId
from src.domain.event.value_objects.ticket_category_id import TicketCategoryId
from src.domain.shared.exceptions.domain_exception import DomainException
from src.domain.shared.value_objects.money import Money

PAYMENT_DEADLINE_MINUTES = 15


@dataclass
class Booking:
    id: BookingId
    customer_id: CustomerId
    event_id: EventId
    ticket_category_id: TicketCategoryId
    quantity: int
    unit_price: Money
    total_price: Money
    status: BookingStatus
    payment_deadline: datetime
    _domain_events: List = field(default_factory=list, init=False, repr=False)

    # User Story - 08

    @staticmethod
    def create(
        customer_id: CustomerId,
        event_id: EventId,
        ticket_category_id: TicketCategoryId,
        quantity: int,
        unit_price: Money,
        now: datetime,
    ) -> "Booking":
        # BR-B08: quantity harus lebih dari nol
        if quantity <= 0:
            raise DomainException("Ticket quantity must be greater than zero.")

       
        total_price = unit_price.multiply(quantity)

       
        payment_deadline = now + timedelta(minutes=PAYMENT_DEADLINE_MINUTES)

        booking = Booking(
            id=BookingId.generate(),
            customer_id=customer_id,
            event_id=event_id,
            ticket_category_id=ticket_category_id,
            quantity=quantity,
            unit_price=unit_price,
            total_price=total_price,
            status=BookingStatus.PENDING_PAYMENT,
            payment_deadline=payment_deadline,
        )

        booking._domain_events.append(
            TicketReserved(
                booking_id=booking.id,
                customer_id=customer_id,
                event_id=event_id,
                ticket_category_id=ticket_category_id,
                quantity=quantity,
            )
        )

        return booking

    def pull_domain_events(self) -> List:
        events = list(self._domain_events)
        self._domain_events.clear()
        return events
    
    # User Story - 09

    def calculate_total_price(self, service_fee: Money = None) -> Money:
        """
        BR-B09: Menghitung total price booking.
        - Total = unit price x quantity
        - Jika ada service fee, ditambahkan ke total
        - Total tidak boleh negatif
        """
        total = self.unit_price.multiply(self.quantity)

        if service_fee is not None:
            total = total.add(service_fee)

        if total.amount < 0:
            raise DomainException("Total price cannot be negative.")

        return total