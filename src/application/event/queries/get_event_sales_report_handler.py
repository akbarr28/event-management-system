from decimal import Decimal

from src.application.event.queries.get_event_sales_report import GetEventSalesReportQuery
from src.application.shared.dtos.sales_report_dto import SalesReportDTO, TicketCategorySalesDTO
from src.domain.booking.repositories.i_booking_repository import IBookingRepository
from src.domain.booking.value_objects.booking_status import BookingStatus
from src.domain.event.repositories.i_event_repository import IEventRepository
from src.domain.event.value_objects.event_id import EventId
from src.domain.shared.exceptions.domain_exception import DomainException


class GetEventSalesReportHandler:
    """
    Query Handler untuk US-19: View Event Sales Report.
    Mengambil data event dan semua bookingnya, lalu menyusun laporan penjualan.
    """

    def __init__(
        self,
        event_repository: IEventRepository,
        booking_repository: IBookingRepository,
    ):
        self._event_repository = event_repository
        self._booking_repository = booking_repository

    async def handle(self, query: GetEventSalesReportQuery) -> SalesReportDTO:
        # Ambil event
        event_id = EventId.from_string(query.event_id)
        event = await self._event_repository.find_by_id(event_id)
        if event is None:
            raise DomainException("Event not found.")

        # Ambil semua booking untuk event ini
        bookings = await self._booking_repository.find_by_event_id(event_id)

        # Siapkan counter per category
        category_sales = {}
        for tc in event.ticket_categories:
            category_sales[str(tc.id)] = {
                "name": tc.name,
                "sold": 0,
            }

        total_pending = 0
        total_paid = 0
        total_expired = 0
        total_refunded = 0
        total_revenue = Decimal("0")
        revenue_currency = "IDR"

        for booking in bookings:
            if booking.status == BookingStatus.PENDING_PAYMENT:
                total_pending += 1
            elif booking.status == BookingStatus.PAID:
                total_paid += 1
                total_revenue += booking.total_price.amount
                revenue_currency = booking.total_price.currency
                cat_id = str(booking.ticket_category_id)
                if cat_id in category_sales:
                    category_sales[cat_id]["sold"] += booking.quantity
            elif booking.status == BookingStatus.EXPIRED:
                total_expired += 1
            elif booking.status == BookingStatus.REFUNDED:
                total_refunded += 1

        tickets_sold_per_category = [
            TicketCategorySalesDTO(
                category_name=data["name"],
                tickets_sold=data["sold"],
            )
            for data in category_sales.values()
        ]

        return SalesReportDTO(
            event_id=str(event.id),
            event_name=event.name,
            tickets_sold_per_category=tickets_sold_per_category,
            total_pending_payment=total_pending,
            total_paid=total_paid,
            total_expired=total_expired,
            total_refunded=total_refunded,
            total_revenue_amount=total_revenue,
            total_revenue_currency=revenue_currency,
        )