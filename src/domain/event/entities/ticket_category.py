from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal

from src.domain.event.value_objects.event_id import EventId
from src.domain.event.value_objects.ticket_category_id import TicketCategoryId
from src.domain.event.value_objects.ticket_category_status import TicketCategoryStatus
from src.domain.shared.exceptions.domain_exception import DomainException
from src.domain.shared.value_objects.money import Money


@dataclass
class TicketCategory:
    id: TicketCategoryId
    event_id: EventId
    name: str
    price: Money
    quota: int
    remaining_quota: int
    sales_start_date: datetime
    sales_end_date: datetime
    status: TicketCategoryStatus = TicketCategoryStatus.ACTIVE

    @staticmethod
    def create(
        event_id: EventId,
        name: str,
        price: Money,
        quota: int,
        sales_start_date: datetime,
        sales_end_date: datetime,
        event_start_date: datetime,
    ) -> "TicketCategory":
        # BR-TC01: harga tidak boleh negatif (sudah dicek di Money, tapi eksplisit di sini)
        if price.amount < Decimal("0"):
            raise DomainException("Ticket price cannot be negative.")

        # BR-TC01: quota harus lebih dari nol
        if quota <= 0:
            raise DomainException("Ticket quota must be greater than zero.")

        # BR-TC01: sales_end_date harus sebelum atau sama dengan event start_date
        if sales_end_date > event_start_date:
            raise DomainException(
                "Ticket sales end date must be before or on the event start date."
            )

        # BR-TC01: sales_start_date tidak boleh setelah sales_end_date
        if sales_start_date > sales_end_date:
            raise DomainException(
                "Ticket sales start date cannot be after sales end date."
            )

        return TicketCategory(
            id=TicketCategoryId.generate(),
            event_id=event_id,
            name=name,
            price=price,
            quota=quota,
            remaining_quota=quota,  # awalnya remaining = quota penuh
            sales_start_date=sales_start_date,
            sales_end_date=sales_end_date,
            status=TicketCategoryStatus.ACTIVE,
        )

    def disable(self) -> None:
        # BR-TC02: set status menjadi INACTIVE
        self.status = TicketCategoryStatus.INACTIVE

    def reserve_quota(self, quantity: int) -> None:
        if quantity <= 0:
            raise DomainException("Quantity must be greater than zero.")
        if self.remaining_quota < quantity:
            raise DomainException("Insufficient ticket quota.")
        self.remaining_quota -= quantity

    def release_quota(self, quantity: int) -> None:
        if quantity <= 0:
            raise DomainException("Quantity must be greater than zero.")
        self.remaining_quota += quantity

    def is_on_sale(self, at: datetime) -> bool:
        return self.sales_start_date <= at <= self.sales_end_date

    def is_available(self) -> bool:
        return (
            self.status == TicketCategoryStatus.ACTIVE
            and self.remaining_quota > 0
        )