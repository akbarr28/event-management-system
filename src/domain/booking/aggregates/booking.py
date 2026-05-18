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
from src.domain.booking.domain_events.booking_paid import BookingPaid
from src.domain.booking.domain_events.booking_expired import BookingExpired
from typing import List

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
    
    # User Story - 10

    def pay(self, payment_amount: Money, now: datetime) -> None:
        """
        BR-B10: Memproses pembayaran booking.
        - Booking harus berstatus PendingPayment
        - Pembayaran tidak boleh melewati payment deadline
        - Jumlah pembayaran harus sama dengan total price
        """
        # BR-B10-01: hanya PendingPayment yang bisa dibayar
        if self.status != BookingStatus.PENDING_PAYMENT:
            raise DomainException(
                "Only bookings with status PendingPayment can be paid."
            )

        # BR-B10-02: tidak boleh melewati payment deadline
        if now > self.payment_deadline:
            raise DomainException(
                "Payment deadline has passed. Booking cannot be paid."
            )

        # BR-B10-03: jumlah pembayaran harus sama dengan total price
        if payment_amount != self.total_price:
            raise DomainException(
                "Payment amount does not match the total booking price."
            )

        self.status = BookingStatus.PAID

        self._domain_events.append(
            BookingPaid(
                booking_id=self.id,
                customer_id=self.customer_id,
                event_id=self.event_id,
                amount_paid=payment_amount,
            )
        )

        # User Story - 11

    def expire(self, now: datetime) -> None:
        """
        BR-B11: Menandai booking sebagai Expired.
        - Hanya booking PendingPayment yang bisa di-expire
        - Booking Paid tidak bisa di-expire
        - Payment deadline harus sudah lewat
        """
        # BR-B11-01: hanya PendingPayment yang bisa di-expire
        if self.status == BookingStatus.PAID:
            raise DomainException(
                "Paid booking cannot be expired."
            )

        if self.status != BookingStatus.PENDING_PAYMENT:
            raise DomainException(
                "Only bookings with status PendingPayment can be expired."
            )

        # BR-B11-02: payment deadline harus sudah lewat
        if now <= self.payment_deadline:
            raise DomainException(
                "Booking cannot be expired before payment deadline has passed."
            )

        self.status = BookingStatus.EXPIRED

        self._domain_events.append(
            BookingExpired(
                booking_id=self.id,
                customer_id=self.customer_id,
                event_id=self.event_id,
                ticket_category_id=self.ticket_category_id,
                quantity=self.quantity,
            )
        )

        # User Story - 12

    def issue_tickets(self) -> list:
        """
        BR-T12: Menerbitkan tickets setelah booking dibayar.
        - Hanya booking Paid yang bisa menerbitkan tickets
        - Jumlah ticket = quantity booking
        - Setiap ticket memiliki unique ticket code
        """
        from src.domain.ticket.entities.ticket import Ticket

        if self.status != BookingStatus.PAID:
            raise DomainException(
                "Tickets can only be issued for paid bookings."
            )

        tickets = []
        for _ in range(self.quantity):
            ticket = Ticket.create(
                booking_id=self.id,
                customer_id=self.customer_id,
                event_id=self.event_id,
                ticket_category_id=self.ticket_category_id,
            )
            tickets.append(ticket)

        return tickets